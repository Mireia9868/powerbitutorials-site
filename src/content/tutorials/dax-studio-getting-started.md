---
title: "DAX Studio: Connect to Power BI, Trace & Tune Queries"
description: "A hands-on DAX Studio tutorial: download it, connect to an open PBIX, run EVALUATE queries, read query plans and Server Timings, and find the slow measures."
pubDate: 2026-09-23
category: "dax"
difficulty: "Intermediate"
tags: ["power bi", "dax studio", "query plan", "performance", "vertipaq"]
author: Mireia
featured: false
draft: false
---

DAX Studio is a free, open-source client for the tabular model behind Power BI. It lets you write DAX queries against a live model, capture the **query plan**, and see how much time the Storage Engine and the Formula Engine each spent. This guide gets you connected, runs a first query, and then walks through the workflow I use when a report visual is slow: copy the query out of Power BI, measure it, read the plan, and rewrite the measure.

## What DAX Studio is for

Power BI Desktop can already tell you *which* visual is slow. Open **View → Performance Analyzer**, start recording, refresh the visuals, and you get a duration per visual split into DAX query, visual display, and other. That is enough to find the problem, but not to explain it.

DAX Studio answers the next question: why did that DAX query take that long? It shows the actual query text Power BI generated, the logical and physical plans, the individual Storage Engine queries, and the SE/FE time split. It also gives you a scratch pad to test a rewritten measure without touching the model or the report.

That makes it the natural second step after [Performance Analyzer](/tutorials/power-bi-performance-analyzer/), not a replacement for it.

## Install and connect

1. Download DAX Studio from [daxstudio.org](https://daxstudio.org/) and install it. A portable build is also available if you cannot install software on a managed machine. It is free and open source — there is no licence tier or trial limit.
2. Open Power BI Desktop with the .pbix you want to investigate. The model must be loaded in memory; a file that is merely open on disk is not enough.
3. In DAX Studio, click **Connect** and choose **Power BI / SSDT Model**. DAX Studio enumerates the local Analysis Services instances started by Power BI Desktop, so your open report appears by name. Select it and click Connect.

<!-- TODO: add screenshot: Figure 1: dax studio getting started illustration -->

The connection reads the live model in memory — no export, no copy of the data, no publishing. The metadata tree on the left lists the tables, columns, measures and hierarchies exactly as the model exposes them.

Three other connection modes matter later:

- **Analysis Services / XMLA** — useful for a published dataset. For the Power BI Service you need an XMLA endpoint on Premium, Premium Per User, or a Fabric capacity, plus sufficient workspace permissions. The server name uses the `powerbi://api.powerbi.com/v1.0/myorg/<workspace>` form rather than `localhost`.
- **PowerPivot / Excel** — connects to a Power Pivot model inside an Excel workbook, which is handy when the slow logic lives in a spreadsheet rather than a .pbix.
- **Tabular Editor / other clients** — anything that can speak XMLA to the same model can share the same tracing workflow.

**If the connect dialog shows no model:** confirm Power BI Desktop is actually open with a report (not just the start screen), close and reopen DAX Studio after Desktop has finished loading, and check that no firewall rule is blocking the local instance. On managed machines, a pending Power BI Desktop update is a common cause — restart Desktop once the update has applied. Advanced users can also select **Analysis Services** and paste the `localhost:<port>` instance name directly; DAX Studio displays the port it detected in the connection dialog.

## A five-minute first run

Type this into the editor and press **Run**:

```dax
EVALUATE
SUMMARIZECOLUMNS (
    'Product'[Category],
    "Total Sales", [Total Sales]
)
```

`EVALUATE` is the DAX query keyword — every query you run in DAX Studio starts with it. `SUMMARIZECOLUMNS` groups by the columns you list and evaluates the expressions you name. If your model has no `Product` table, drag any column from the metadata pane into the editor instead; DAX Studio writes the fully qualified name for you, which is the fastest way to learn the exact table and column spelling a model expects.

Before you trust any timing, use **Clear Cache then Run** (in the Run dropdown) rather than a plain Run. The Storage Engine caches results, so a second identical run can look dramatically faster than the first one without your DAX having changed at all. Clearing the cache first makes comparisons between two versions of a measure meaningful. This single habit separates usable measurements from misleading ones.

The result appears in a grid by default. You can copy rows out of the grid, or change the output target to a file before running a query that returns too many rows to display.

## Write and run DAX freely

A query can define local measures and variables in a `DEFINE` block, which lets you test a rewrite without creating anything in the model:

```dax
DEFINE
    MEASURE Sales[Fast Total] =
        SUMX ( Sales, Sales[Quantity] * Sales[Unit Price] )
EVALUATE
SUMMARIZECOLUMNS (
    'Date'[Year],
    "Original", [Total Sales],
    "Rewritten", [Fast Total]
)
```

Put both versions side by side, run once with the timers on, and you have a direct comparison. Nothing here is persisted: close the window and the model is unchanged. That is why DAX Studio is a safe place to experiment with `CALCULATE` rewrites, iterator changes, and filter arguments before committing them to a report — see [CALCULATE in Power BI](/tutorials/calculate-function/) for the patterns worth testing.

Other useful editor habits:

- The metadata pane is searchable; typing a fragment of a column name is faster than remembering the exact table prefix.
- IntelliSense lists measures and functions with their arguments, which catches misspelled measure names immediately.
- `TOPN`, `ORDER BY` and `SUMMARIZECOLUMNS` let you build the exact shape of a visual's result set, so you can reproduce a slow visual outside the report.
- Save queries as `.dax` files. A small library of diagnostic queries is more useful over time than one-off investigations.

## Copy a slow query out of Performance Analyzer

This is the workflow that pays for the install, and it is the one most people skip:

1. In Power BI Desktop, open **View → Performance Analyzer** and click **Start recording**.
2. Click **Refresh visuals**, or interact with the report the way a user does.
3. Expand the slow visual and click **Copy query**. Power BI puts the full DAX query it generated — including implicit filters from slicers and the visual — on the clipboard.
4. Paste it into DAX Studio. Switch on **Query Plan** and **Server Timings** in the Traces area, then run with **Clear Cache then Run**.
5. Read the timers first, then the plan. Rewrite the measure, paste the new query, and run again under the same conditions.

The pasted query is often long and full of generated aliases. Do not try to clean it up before measuring — the point is to measure exactly what the report sent. Once you know the expensive part, you can write a smaller reproduction query by hand.

## Read the query plan

With **Query Plan** enabled, a run produces two trees:

- **Logical Plan** — what the DAX engine intends to compute, expressed as logical operators.
- **Physical Plan** — what the Storage Engine actually did, with the scans, joins and row counts for each step.

Look at the Physical Plan first. A healthy measure shows a small number of `Scan_Vertipaq` operations returning only the rows the result needs. Two things are worth investigating: a scan that returns far more rows than the final result, and a large materialisation — an intermediate table the Formula Engine has to hold in memory before it can produce the answer. Row counts on each node make both visible.

The Logical Plan is where you spot the shape of the calculation: nested iterators, a `FILTER` over a whole fact table, or a context transition you did not intend. If you are unsure why a filter behaves the way it does, [filter context vs row context](/tutorials/filter-context-row-context-explained/) is the prerequisite reading.

## Read Server Timings

The **Server Timings** tab splits a query into:

- **Total** — wall-clock duration for the query.
- **SE** — time in the Storage Engine, which scans and aggregates compressed columns in parallel.
- **FE** — time in the Formula Engine, which is single-threaded and handles the logic the SE cannot express.
- **SE Queries** — how many separate scans the SE had to run, and how much was served from the SE cache.

The golden rule is to push work into the SE. A fast measure usually has high SE time, low FE time, and a small number of SE queries. When FE dominates, the engine is doing row-by-row work that often belongs in a variable, a pre-aggregated column, or a simpler filter expression.

Click an individual SE query to see its **xmSQL** — the pseudo-SQL the VertiPaq engine generated. It is readable enough to tell you which columns were scanned, which predicates were pushed down, and whether a filter was applied natively or left for the FE.

Be careful with comparisons: run both versions with the cache cleared, on the same slicer state, and repeat each at least twice. A single run is not a benchmark.

## Three patterns worth recognising

**`CallbackDataID` in the plan or xmSQL.** The SE had to call back into the FE for every row because an expression could not be evaluated natively — commonly a complex `IF`, a measure reference inside an iterator, or a string operation. The fix is usually to restructure the expression so the SE can evaluate it, or to precompute the value as a column.

**FE time much larger than SE time.** Look for iterators over large tables (`SUMX`, `FILTER`, `ADDCOLUMNS`) and for measures that reference other measures inside a row context, causing repeated context transitions. Hoist repeated expressions into `VAR` and check whether an aggregation can be pushed into a single `SUMMARIZECOLUMNS`.

**A huge materialisation before a small result.** Often caused by `FILTER ( AllRows, ... )` where a narrower filter or `KEEPFILTERS` would do, or by a `CROSSJOIN` that generates combinations the visual never displays. Reducing the number of rows the FE must hold is usually a bigger win than micro-optimising arithmetic.

For a wider set of fixes, see [DAX optimization techniques](/tutorials/dax-optimization-techniques/) and the [DAX troubleshooting guide](/tutorials/dax-troubleshooting-guide/).

## Beyond a single query

Two features are easy to miss on a first pass:

- **VertiPaq Analyzer** (Advanced → View Metrics) reports table and column sizes, cardinality, dictionary size, and compression ratios. When a model is slow because it is simply too large or a high-cardinality column is expensive to scan, this tells you where the bytes are. It is also the quickest way to confirm that a data-type change actually reduced a column's footprint.
- **All Queries** traces the queries sent by other clients — including Power BI Desktop itself — rather than only the queries you run inside DAX Studio. Turn it on, interact with the report, and you can see which visual fires how many queries, which is useful for reports where the delay comes from dozens of small queries rather than one slow one.

Both are read-only. Neither requires publishing or changing the model.

## When to reach for it

- A visual is slow and you need the *why*, not just the duration.
- You want to compare two versions of a measure without editing the model.
- You are learning why `EARLIER` or `FILTER ( FullTable )` is expensive.
- You need to know how much a high-cardinality column is costing you before changing the model.
- A report feels slow but Performance Analyzer shows no single slow visual — a sign that many small queries are the problem.

## FAQ

**Is DAX Studio really free?**
Yes. It is free and open source, with no paid tier. Its documentation lives at [daxstudio.org](https://daxstudio.org/).

**Does it change my model?**
No. Queries are read-only against the connected model. Measures defined with `DEFINE` exist only inside that query window. You can experiment freely.

**Can I use it with the Power BI Service?**
Yes, over an XMLA endpoint on a supported capacity with the right workspace permissions. The Desktop connection is the easier place to start.

**What is the difference from Performance Analyzer?**
Performance Analyzer lives inside Power BI and times whole visuals. DAX Studio times individual queries and exposes the SE/FE split, the query plans, and the Storage Engine queries. Use the first to locate the visual, the second to explain it.

**Why does the timing change between two identical runs?**
Usually the Storage Engine cache. Use **Clear Cache then Run** for every comparison, and keep the slicer state constant.

**The connect dialog is empty — what now?**
Make sure Power BI Desktop has a report open and has finished loading, restart DAX Studio, and check for a pending Desktop update. As a fallback, choose the Analysis Services connection type and enter the `localhost:<port>` instance shown in the dialog.

## Related Reading

- [DAX Basics](/tutorials/dax-basics/)
- [CALCULATE in Power BI](/tutorials/calculate-function/)
- [Filter Context vs Row Context](/tutorials/filter-context-row-context-explained/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer/)
- [DAX Troubleshooting Guide](/tutorials/dax-troubleshooting-guide/)
