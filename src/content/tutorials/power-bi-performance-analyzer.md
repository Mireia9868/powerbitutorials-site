---
title: "Using Performance Analyzer to Find Slow Visuals in Power BI"
description: "Performance Analyzer is a pane inside Power BI Desktop that records what happens when a report page or a single visual renders."
pubDate: 2026-10-03
category: visualization
tags: ["performance", "optimization"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What Performance Analyzer Actually Measures

Performance Analyzer is a pane inside Power BI Desktop that records what happens when a report page or a single visual renders. It answers a narrow but important question: where is the time going, and is it the visual, the DAX query, or the rendering engine that is slow?

It does not measure refresh performance for your dataset, and it does not measure gateway latency for DirectQuery in any detailed way. Those are separate tools (Tabular Editor, DAX Studio, SQL Profiler, and the Fabric Capacity Metrics app). Performance Analyzer is a *report-authoring* profiler, and it should be your first stop when a page feels sluggish.

The pane produces a table of rows, one per visual per action, with three durations:

| Column | Meaning |
|---|---|
| DAX query | Time for the storage engine and formula engine to answer the query from that visual |
| Visual display | Time for the visual's rendering code to draw the result |
| Other | Time spent in the host, waiting on the query, or in queries not tied to a single visual (like page-level filters) |

A slow report is almost always dominated by one of three causes: an expensive DAX query, too many visuals on a page, or a poorly filtered visual that scans more data than it needs. The tool separates these so you stop guessing.

## Running a Capture

1. Open the report in Power BI Desktop, go to the **View** tab, and click **Performance Analyzer**. The pane docks on the right.
2. Click **Start recording**. Nothing is captured until you do.
3. Interact with the report. Click a slicer, drill into a chart, change a page. Each user action produces a new "record" block.
4. Click **Stop** when finished. You can also **Clear** to reset, or expand individual rows.

For a fair baseline, capture a page in three scenarios:

- Cold: right after a **Refresh** and a fresh Desktop start.
- Warm: the second time you navigate to the page.
- Interaction: after changing a slicer value.

Cold vs warm matters because cold includes storage engine warmup. If warm is fast and cold is slow, your bottleneck is data scan or cardinality, not the visual.

## Reading the Numbers

Expand the top-level page row to see one child row per visual. Sort by DAX query descending. Look for the top three rows only — those usually account for most of the time.

A few patterns and what they mean:

- **DAX query > 500 ms, Visual display < 30 ms.** The data model or the measure is the problem. Open DAX Studio and profile the query.
- **DAX query < 100 ms, Visual display > 200 ms.** Too many visuals, or a visual with a high-cardinality axis (e.g. a table with 5,000 rows, or a scatter chart with thousands of points).
- **Other dominates.** Typically DirectQuery, live connections, or a page with a slow filter/slicer.
- **Every visual is 300 ms+.** Something upstream: a calculated column evaluated per row, a bidirectional relationship creating cross-filter fanout, or a fact table with millions of rows and no aggregation table.

A common culprit is a measure that scans a fact table with a nested iteration. Consider a "top N customers by revenue" calculation:

```dax
Top Customers Revenue =
VAR CustomerRevenue =
    ADDCOLUMNS (
        VALUES ( Customer[CustomerKey] ),
        "@Revenue", [Total Revenue]
    )
VAR TopN =
    TOPN ( 10, CustomerRevenue, [@Revenue], DESC )
RETURN
    SUMX ( TopN, [@Revenue] )
```

`VALUES(Customer[CustomerKey])` can produce hundreds of thousands of rows, and `ADDCOLUMNS` evaluates `[Total Revenue]` once per customer. Rewriting with variables, or pushing the top-N logic into a visual-level filter, often cuts the query time by an order of magnitude. The Performance Analyzer will show this as a single visual with a very high DAX query time and near-zero display time.

## Copying the Query to DAX Studio

Performance Analyzer gives you a **Copy query** option on each visual row. Use it. Paste the copied DAX into DAX Studio's editor, connect to the same model (File > Connect > PBI / XMLA endpoint), and look at the **Server Timings** tab.

Server Timings splits the query into:

- **FE (Formula Engine):** single-threaded, does `SUMX`, `FILTER`, `ADDCOLUMNS` and similar row-by-row work.
- **SE (Storage Engine):** multi-threaded, scans the compressed column store.
- **Scan count:** how many storage engine scans the FE requested. High scan count with low SE time is the classic "FE-bound" signal, meaning your measure iterates too much.

This is the point where Performance Analyzer hands off to better tools. It told you *which* visual is slow. DAX Studio tells you *why*.

## Practical Fixes That Move the Needle

Before you optimize DAX, check the cheap wins:

- Remove visuals you don't need. Each visual is a separate query. Ten visuals on a page mean ten queries fired in parallel; the page waits for the slowest.
- Replace high-cardinality slicers. A slicer on `Customer[Customer Name]` (200k values) is fine to *display* but terrible to query against because it materializes the whole column. Use a hierarchy: region, then city, then name.
- Move calculated columns out of the fact table. Calculated columns cannot be compressed by the storage engine and are recomputed on refresh. If they are returned by a visual, they are just columns — but if a measure references them in a filter, you double the work.
- Consider aggregations or a pre-aggregated import table when a DirectQuery visual is slow. DirectQuery queries hit the source every time; Performance Analyzer's "Other" column will balloon.
- Use cardinality reduction. A `DateTime` column with second-level granularity has 86,400 values per day. Split into date and time, or round to the nearest minute (or hour), and compress the whole column.

For DAX-side fixes, the two rules that consistently pay off are: (1) prevent context transitions by never iterating a measure inside `SUMX`/`FILTER` on a large table, and (2) use variables to compute a scalar once and reference it, instead of letting Power BI re-evaluate a subexpression across a row context.

## A Worked Example

You open a sales dashboard and the total render time is 3.8 seconds. Performance Analyzer shows:

| Visual | DAX query | Visual display | Other |
|---|---|---|---|
| Revenue by month (line) | 210 ms | 45 ms | 12 ms |
| Top 10 products (table) | 2,410 ms | 80 ms | 15 ms |
| Slicer: country | 620 ms | 20 ms | 8 ms |
| Card: total revenue | 180 ms | 10 ms | 5 ms |

The Top 10 products table is the obvious target. Copy its query into DAX Studio. Server Timings shows FE 2,200 ms, SE 210 ms, scan count 14. That is a row-context problem, not a data-volume problem. The measure likely uses `FILTER` over the product table with a nested measure. Rewrite using `TOPN` with variables, or move the top-N filter to the visual's Top N filter (which is optimized to use the storage engine). The query drops to 300 ms. The slicer is next: 620 ms to display 200 country values is fine, but you can drop to 40 ms by replacing it with a dropdown or list (both use less layout work than a tile slicer with 200 values).

Total render time after fixes: about 900 ms. The improvements came from measurement, not intuition.

## FAQ

### Q: Does Performance Analyzer work against a Power BI Service dataset?

Only in Power BI Desktop, connected to the model. You cannot run Performance Analyzer in the browser. For service-side investigation, use the Fabric Capacity Metrics app and DAX Studio via the XMLA endpoint. If you publish first and see slowness only in the Service, the issue is likely gateway, capacity, or a different dataset version — not the visual.

### Q: Why is DAX query time different each time I run it?

Power BI's storage engine caches column data in memory after a query. The first run reads from disk or the source; the second reads from the in-memory store. Always compare like-for-like: cold vs cold, warm vs warm. If you see variance of more than 2x on the same visual with the same filters, you are probably looking at cold/warm mixing.

### Q: Can I record a specific interaction without capturing the whole page load?

Yes. Start recording, then interact with the report. Performance Analyzer only records actions you trigger. It also keeps records stacked, so you can compare a slow interaction to a fast one in the same session. Use **Clear** between captures if the list gets long.

### Q: Is `Visual display` time the same as perceived render time?

Not exactly. It measures the visual's own drawing time, not the time until the user sees the result. Browser paint, network transport (in Service), and layout of surrounding visuals all add latency. Treat it as directionally useful: if display time is high, the visual itself is the cost; if it is near zero and DAX is high, the query is.

### Q: What is a reasonable DAX query time?

Under 200 ms for a warm cache is comfortable. 200–500 ms usually indicates room to improve. Above 500 ms is when users start to notice, and above 1 second you should treat it as a bug regardless of how many visuals are on the page.

<!-- PERF-CLUSTER-NAV -->
## More performance optimization guides

- [Power BI Performance Optimization: A Complete Guide](/tutorials/power-bi-performance-optimization/)
- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Power Query Query Folding](/tutorials/power-query-query-folding/)
## Related Reading

- [Performance Analyzer guide](/tutorials/power-bi-performance-analyzer-guide/)
- [Power BI performance optimization](/tutorials/power-bi-performance-optimization/)
- [DAX optimization techniques](/tutorials/dax-optimization-techniques/)
- [DAX variables best practices](/tutorials/dax-variables-best-practices/)
- [Filter context and row context explained](/tutorials/filter-context-row-context-explained/)
- [DirectQuery vs Import mode](/tutorials/directquery-vs-import-mode/)
- [Star schema data modeling](/tutorials/data-modeling-star-schema/)
- [DAX Studio getting started](/tutorials/dax-studio-getting-started/)
