---
title: "VertiPaq Analyzer: Optimize Your Power BI Data Model"
description: "Every Power BI Import model is stored in the VertiPaq engine, a columnar, in-memory database."
pubDate: 2026-10-03
category: data-modeling
tags: ["performance", "data model"]
difficulty: Advanced
author: Mireia
featured: false
draft: false
---

## What VertiPaq Analyzer Actually Measures

Every Power BI Import model is stored in the VertiPaq engine, a columnar, in-memory database. When a report feels slow, the bottleneck is rarely DAX syntax alone. It is usually how much data VertiPaq has to scan, how well that data compresses, and how many distinct values each column contains. VertiPaq Analyzer is a free external tool (distributed as a Power BI template plus a Tabular Editor script) that reads the model's metadata and exposes those numbers as tables you can sort and filter.

The tool answers three questions:

1. How many bytes does each table, column, and relationship cost in memory?
2. How efficiently does each column compress (bits per value, dictionary size)?
3. Which columns are the heaviest, and would they be better as integer keys, removed entirely, or moved to a different storage mode?

This article walks through installing it, reading its output, and acting on the four highest-impact findings: oversized dictionaries, high-cardinality text columns, expensive relationships, and redundant columns.

## Getting the Analyzer Into Your Model

VertiPaq Analyzer is published as a `.pbit` template by SQLBI. The workflow:

1. Open your report in Power BI Desktop.
2. Install **Tabular Editor 2** (free, external). It can attach to the running Desktop instance.
3. In Tabular Editor, run the **VertiPaq Analyzer** C# script from the Advanced Scripting pane. It computes statistics directly against the in-memory model and writes them to a model table called `VertiPaqAnalyzer`.
4. Save the model back to Desktop, then create a blank report page and bind a table visual to the `Columns`, `Tables`, and `Relationships` tables the script created.
5. Exclude the analyzer tables from your final published model, or keep them in a separate `.pbix` copy.

An alternative that needs no external tooling: **DAX Studio** includes a built-in VertiPaq Analyzer pane under the Advanced tab. Connect DAX Studio to the Desktop instance, then open that pane. For most tuning work the DAX Studio route is faster because you never modify the model.

## Reading the Columns Table

The `Columns` table is where optimization decisions originate. The important columns:

| Column | Meaning | What "good" looks like |
|---|---|---|
| `Cardinality` | Distinct values | Low for keys, moderate for dimensions |
| `Data Size` | Compressed bytes for the data | Proportional to cardinality × row count |
| `Dictionary Size` | Bytes for the value dictionary | Small for numeric surrogate keys |
| `Hierarchy Size` | Bytes for internal tree structures | Near zero on non-key columns |
| `Encoding` | Hash or Value | Value for sorted/compressed, Hash for unsortable |

A classic symptom: a `Customer Name` text column with 900,000 rows and 850,000 distinct values. Its dictionary is enormous because every value is nearly unique. Text with high cardinality is the single most expensive thing you can store in VertiPaq.

### Fix 1: Replace high-cardinality text with surrogate integers

If you only slice by `Customer Name` in a slicer, you can often keep the name but drop the relationship key. Build the relationship on an integer `CustomerKey` instead:

```powerquery
// In the fact table query, keep the integer foreign key
let
    Source = Sql.Database("server", "dw"),
    Sales = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Typed = Table.TransformColumnTypes(Sales, {
        {"CustomerKey", Int64.Type},
        {"ProductKey", Int64.Type},
        {"OrderDate", type date},
        {"SalesAmount", type number}
    })
in
    Typed
```

Related dimensions then hold the readable name:

```powerquery
let
    Source = Sql.Database("server", "dw"),
    DimCustomer = Source{[Schema="dbo", Item="DimCustomer"]}[Data],
    Kept = Table.SelectColumns(DimCustomer, {"CustomerKey", "CustomerName", "Segment"}),
    Typed = Table.TransformColumnTypes(Kept, {
        {"CustomerKey", Int64.Type},
        {"CustomerName", type text},
        {"Segment", type text}
    })
in
    Typed
```

VertiPaq compresses a contiguous `Int64` key far better than a text name. Dictionary size collapses from hundreds of megabytes to kilobytes.

### Fix 2: Drop columns you never reference

Sort the `Columns` table by `Data Size` descending. The top entries are frequently columns that no visual, measure, relationship, or RLS rule uses. Deleting them is free performance. To find unused columns, use DAX Studio's **VertiPaq Analyzer → Columns** view, then cross-reference with the **Model → Dependencies** view, or run a simple metadata query:

```dax
EVALUATE
SELECTCOLUMNS(
    INFO.COLUMNS(),
    "Table", [TableID],
    "Column", [ExplicitName],
    "Data Type", [ExplicitDataType]
)
ORDER BY [Table], [Column]
```

`INFO.COLUMNS()` returns one row per column in the model; comparing it to your report's field usage reveals dead weight.

### Fix 3: Reduce dictionary size with calculated columns done right

Calculated columns live in the model and cost memory. A calculated column that concatenates text is expensive; a calculated column that yields an integer flag is cheap. Watch out for `EARLIER`, which needs a nested row context to make sense. It works inside a calculated column only against an outer row context, not as a general aggregation function:

```dax
-- Cheap: integer flag, low cardinality
Sales[IsReturned] =
IF( Sales[ReturnQuantity] > 0, 1, 0 )

-- Expensive: unique text per row, huge dictionary
Sales[RowLabel] =
Sales[OrderID] & " - " & Sales[ProductName]
```

Move the `RowLabel` logic into a measure or a visual-level tooltip instead. Anything that produces a near-unique string per row belongs outside the model.

## Reading the Relationships Table

Cross-filtering direction and key cardinality affect query plans. Two rules guide most optimizations:

- **One-to-many on integer keys, single direction.** Bidirectional filters invite ambiguous paths and expand the VertiPaq operation graph.
- **Avoid many-to-many where a bridge table can serve.** Many-to-many relationships force VertiPaq to hash two large dictionaries at query time.

Sort the `Relationships` table by `Used Size`. If a relationship's key column has a large `Dictionary Size`, the relationship itself is the cost driver, not the visual.

## Reading the Tables Table

The `Tables` table aggregates column sizes. Look for:

- Tables over 100 MB in a Desktop-only model.
- Tables whose `Cardinality` (row count) is far smaller than their `Data Size`, indicating poor compression.
- Calculated tables that duplicate imported data.

If a table is large only because of a few text columns, the fix is upstream: reshape in Power Query or in the source warehouse before import. VertiPaq cannot compress what you give it; it can only compress it well or badly.

## Acting on the Results: A Checklist

Run through this after every analyzer pass:

1. Sort `Columns` by `Data Size`. Remove or replace the top three offenders.
2. Sort by `Dictionary Size`. Replace text keys with integers or convert to a star schema.
3. Sort `Relationships` by `Used Size`. Flatten bidirectional filters to single direction where possible.
4. Check `Hierarchy Size`. If a single column dominates, you likely have a degenerate attribute table where a proper dimension belongs.
5. Re-run the analyzer after each change. Memory savings compound.

## When to Change Storage Mode

If the analyzer shows a table is large but rarely queried at detail grain, consider a **DirectQuery** or **dual** storage mode for that table. DirectQuery pushes the scan to the source and avoids importing bytes VertiPaq must compress. The trade-off is query latency and source load. For fact tables queried at the day or month grain most of the time, dual mode with a pre-aggregation table is often the right compromise.

## Common Mistakes

- **Treating the analyzer as a DAX profiler.** It measures storage, not query execution. Use Performance Analyzer for query timing.
- **Chasing total size instead of hot columns.** A 500 MB model with a well-designed star schema often outperforms a 200 MB model riddled with high-cardinality text.
- **Optimizing before measuring.** Change the model only after the analyzer shows a specific column or relationship is expensive.

## FAQ

### Q: Is VertiPaq Analyzer free?

Yes. The original SQLBI tool is free, and DAX Studio bundles an equivalent VertiPaq Analyzer pane at no cost. Both read model metadata without altering it, except the Tabular Editor script version, which writes a temporary table you can remove.

### Q: Does it work on DirectQuery models?

Partially. DirectQuery tables have no compressed storage in VertiPaq, so their byte-level stats are not meaningful. You can still use the tool to inspect cardinality and relationship metadata, and to compare against imported tables in a composite model.

### Q: How often should I run it?

Every time you add a new table or column, and before promoting a model from Desktop to the Service. A 30-second pass prevents a 300 MB regression from reaching production.

### Q: Can high cardinality ever be acceptable?

Yes, on key columns that are already integers or on columns used for fine-grained slicing where the business genuinely needs every value. The problem is high-cardinality *text*, not high cardinality itself.

## Related Reading

- /tutorials/data-modeling-star-schema/
- /tutorials/dax-optimization-techniques/
- /tutorials/power-bi-performance-analyzer-guide/
- /tutorials/power-bi-performance-optimization/
- /tutorials/directquery-vs-import-mode/
- /tutorials/bidirectional-filtering-guide/
- /tutorials/filter-context-row-context-explained/
- /tutorials/dax-earlier-function/
