---
title: "Power Query Query Folding: How and Why It Matters"
description: "Query folding is the process where Power Query translates the steps you build in the editor into a single query statement that the source system executes on its own engine."
pubDate: 2026-10-02
category: power-query
tags: ["performance", "query folding"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What Query Folding Actually Is

Query folding is the process where Power Query translates the steps you build in the editor into a single query statement that the source system executes on its own engine. Instead of downloading a million rows into your machine and then filtering them, Power Query sends a `SELECT ... WHERE ... GROUP BY` to SQL Server, and SQL Server returns only the result.

The practical effect is enormous. A folded query pushes the heavy lifting to the source, which has indexes, statistics, a query optimizer, and often far more CPU than your laptop. A non-folded query drags raw data across the network and does the work locally in the Power Query engine (the same engine that runs inside the Power BI service and the on-premises data gateway).

Every transformation step in the Applied Steps pane has a folding state:

| State | Meaning |
|---|---|
| Folded | The step is included in the query sent to the source |
| Not folded | The step runs locally after data is retrieved |
| Possibly folded | Power Query cannot determine folding until runtime |
| Folding stopped | A step broke the chain; every step after it runs locally |

Once folding stops at step *N*, no step after *N* can fold. This is the single most important rule to remember. A single badly placed step near the top of your query can force the entire downstream pipeline to materialize locally.

## Why It Matters More Than You Think

The most common symptom of a non-folding query is not an error message. It is a refresh that works fine on 50,000 rows in development and then times out in production on 8 million rows. Two things happen when folding stops:

1. **Volume.** The source returns everything up to the break point. If you filtered late, that could be the entire table.
2. **Location.** All remaining work runs in the Power Query engine. In the Power BI service, that engine has memory limits and a per-refresh timeout. In DirectQuery mode the folding question becomes even more critical, because DirectQuery *only* sends folded operations to the source. Steps that do not fold are not allowed in some DirectQuery scenarios at all.

This is also why two queries that look identical in the editor can behave completely differently: one is a thin wrapper over a server-side aggregate, the other is a local computation over a full table scan.

## How to Check Whether Your Query Folds

Right-click any step in the Applied Steps pane. If the context menu shows **View Native Query**, that step folds. Clicking it reveals the exact SQL or OData statement Power Query generated.

If the option is greyed out, either that step does not fold, or an earlier step broke the chain.

You can also read the fold state from the status bar at the bottom of the Power Query editor while a step is selected, or right-click the step and inspect the folding indicator icon.

For a bulk check across many queries, the diagnostic route is better. Open **Tools > Diagnostics** in Power Query Desktop, or run a refresh in Power BI Desktop while tracing with a tool like SQL Server Profiler or Extended Events if your source is SQL Server. You will see either one aggregate query or a flood of `SELECT *` statements followed by client-side work.

## The Transformations That Fold and the Ones That Break It

Folding depends on the connector. SQL Server, Azure SQL, Synapse, Oracle, PostgreSQL, Snowflake, and OData fold a rich set of operations. Excel workbooks, CSV files, and most web sources fold almost nothing, because there is no query engine on the other side to fold *into*. A CSV on a network share will always download in full.

For relational sources, these generally fold:

- Filtering rows (`Table.SelectRows`)
- Selecting and removing columns (`Table.SelectColumns`, `Table.RemoveColumns`)
- Renaming columns (`Table.RenameColumns`)
- Sorting (`Table.Sort`)
- Grouping and aggregating (`Table.Group` with foldable aggregate functions such as `List.Sum`, `List.Count`, `List.Min`, `List.Max`)
- Joins and merges (`Table.NestedJoin`) when keys and join kind are foldable
- Appending when both branches are folded from the same source
- Basic type changes (`Table.TransformColumnTypes`)

These usually do **not** fold, or fold only in limited cases:

- `Table.AddIndexColumn` — no equivalent server-side concept for arbitrary ordering
- `Table.AddColumn` with custom M or DAX-style logic, unless Power Query can express it in the source language
- `Table.Pivot` and `Table.Unpivot` — folding support varies by connector
- `Table.Buffer` — explicitly forces materialization
- `Table.Distinct` on many connectors — historically a break point, though some connectors now fold it
- Any step involving an external function call, a lookup into another M query, or a data type the source cannot represent

The pattern is that row-and-column shaping folds; per-row computation and order-dependent logic generally do not.

## A Concrete Example

Suppose you have a `Sales` table in SQL Server with 12 million rows and you want the total by region for the last two years. Written as a single folded chain:

```powerquery
let
    Source = Sql.Database("myserver.database.windows.net", "SalesDW"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Folds: becomes WHERE OrderDate >= ...
    FilterRecent = Table.SelectRows(Sales, each [OrderDate] >= #date(2023, 1, 1)),

    // Folds: becomes SELECT Region, Amount
    KeepColumns = Table.SelectColumns(FilterRecent, {"Region", "Amount"}),

    // Folds: becomes GROUP BY Region
    Grouped = Table.Group(KeepColumns, {"Region"},
        {{"TotalSales", each List.Sum([Amount]), type number}})
in
    Grouped
```

Power Query sends one statement roughly like this to SQL Server, and only a handful of rows come back:

```sql
SELECT [Region], SUM([Amount]) AS [TotalSales]
FROM [dbo].[Sales]
WHERE [OrderDate] >= '2023-01-01'
GROUP BY [Region]
```

Now move a single non-folding step to the top. Add an index column before the filter:

```powerquery
let
    Source = Sql.Database("myserver.database.windows.net", "SalesDW"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],

    // Does not fold: forces the full table to download
    AddIndex = Table.AddIndexColumn(Sales, "RowNum", 1, 1),

    // Now runs locally on 12M rows
    FilterRecent = Table.SelectRows(AddIndex, each [OrderDate] >= #date(2023, 1, 1)),
    KeepColumns = Table.SelectColumns(FilterRecent, {"Region", "Amount"}),
    Grouped = Table.Group(KeepColumns, {"Region"},
        {{"TotalSales", each List.Sum([Amount]), type number}})
in
    Grouped
```

The result set is identical. The refresh goes from seconds to minutes, or times out entirely. The fix is trivial: move `AddIndex` to the end of the chain, after the aggregation, where only a few rows are involved.

## Practical Habits That Preserve Folding

**Filter and remove columns first.** Push the cheapest narrowing steps as early as possible, while the context is still being sent to the source.

**Reorder before you rewrite.** The single biggest performance win in most Power Query queries is drag-and-drop. Move non-folding steps to the bottom of the Applied Steps list.

**Declare types after filtering, not before.** A type change usually folds for simple cases, but converting a column to a type the source cannot express forces local materialization. Apply types to the narrow result, not the wide input.

**Avoid `Table.Buffer` in `Import` queries.** It forces the data into memory locally and breaks folding at that point. It is useful in a few narrow scenarios, mostly inside merge operations where you know the table is small, but it is not a performance tool for large tables.

**Check connectors before assuming.** A `Group By` on SQL Server folds. The same `Group By` on a `SharePoint List` or a `.csv` file does not, because there is no server-side engine to delegate to. The folding map is published per connector in Microsoft's Power Query documentation, and it changes with updates.

**Watch merges across sources.** Merging a folded SQL Server table with a non-folded Excel sheet forces the SQL side to be partially materialized. If possible, load both into your own database or your Power BI dataflow and fold there.

## When Folding Is Not Possible

Some sources genuinely cannot fold: CSV files, Excel files, JSON from a web API, and most flat-file exports. In those cases, the relevant tool is **staging through a foldable target**. Load the raw file into your data warehouse, an Azure SQL Database, or a Power BI dataflow backed by a foldable engine, then build your transform chain against that. The pattern is to get data into something with a query engine, and then fold against it.

The same logic applies to DirectQuery models used for real-time reporting: if your report needs DirectQuery and your source does not fold well, redesign the source rather than fighting the connector.

## Diagnosing Production Issues

When a report refreshes slowly, the sequence to check is:

1. Open the query in Power Query, walk the Applied Steps, and find the **first greyed-out View Native Query**. That is your fold break.
2. Look at the step above and below it. Can the non-folding step be moved below the fold break?
3. If the answer is no, ask whether the shaping can happen after the fold (e.g., aggregate first, then add the index, then compute).
4. If neither works, consider staging the intermediate result in a foldable target, so downstream queries start from a folded source.

For DirectQuery models, the diagnostic is stricter: every step that does not fold becomes a warning in the Power Query editor, and in some configurations the query will not run at all until the step is removed.

## FAQ

### Q: Does Power Query folding work with CSV and Excel files?

No, folding requires a source that has its own query engine. CSV, Excel, and most web sources do not, so Power Query downloads the file in full and transforms it locally. If you need folding against flat files, load them into a foldable target such as SQL Server, Azure Synapse, Fabric Warehouse, or a Power BI dataflow first, and then build the query against that target.

### Q: Can I force folding on a step Power Query says is not foldable?

Not reliably. You can sometimes rewrite the step using equivalent M functions that the connector supports, but the transformation must have an expressible form in the source language. Things like `Table.AddIndexColumn` have no SQL equivalent for arbitrary ordering, so there is nothing to force. The realistic alternatives are moving the step to the end of the chain, or staging the intermediate result in a foldable source.

### Q: What is the difference between "View Native Query" being greyed out and folding being stopped?

"View Native Query" greyed out usually means the current step does not fold. If the step before it did fold, then folding is stopped at this step and every step after runs locally. If the step before also did not fold, you are looking at two consecutive non-folded steps, and the break is earlier in the chain. Inspect upward until you find a step whose native query is viewable.

### Q: Does folding affect DirectQuery differently from Import mode?

Yes, significantly. In Import mode, a non-folding step means local processing with more memory and more time. In DirectQuery mode, folding is not optional: only folded operations can be sent, and non-folding steps are either flagged as unsupported or handled with a slower fallback that often degrades performance. If your model is DirectQuery, treat folding as a hard requirement rather than an optimization.

### Q: Does `Table.Buffer` help or hurt performance?

It hurts folding, because it forces the table into local memory and cuts the query chain. It occasionally helps a narrow class of merge operations where the same small table is read repeatedly in a nested context, but for large tables in Import queries it is usually a mistake. Remove it and re-measure before assuming it helps.

<!-- PERF-CLUSTER-NAV -->
## More performance optimization guides

- [Power BI Performance Optimization: A Complete Guide](/tutorials/power-bi-performance-optimization/)
- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Using Performance Analyzer in Power BI](/tutorials/power-bi-performance-analyzer/)
## Related Reading

- [DirectQuery vs Import Mode in Power BI](/tutorials/directquery-vs-import-mode/)
- [Merge vs Append in Power Query](/tutorials/merge-vs-append-queries/)
- [Power BI Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer-guide/)
- [Power BI Performance Optimization](/tutorials/power-bi-performance-optimization/)
- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
- [Calculated Tables and What-If Parameters](/tutorials/calculated-tables-what-if-parameters/)
- [Star Schema Data Modeling](/tutorials/data-modeling-star-schema/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
