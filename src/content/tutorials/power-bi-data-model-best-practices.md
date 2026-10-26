---
title: "Power BI Data Model Best Practices"
description: "Most Power BI reports that feel slow, produce wrong totals, or collapse the moment a new slicer is added share one root cause: a weak data model."
pubDate: 2026-10-15
category: data-modeling
tags: ["data modeling", "best practices"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

Most Power BI reports that feel slow, produce wrong totals, or collapse the moment a new slicer is added share one root cause: a weak data model. Visual formatting and clever DAX get the attention, but the model underneath decides whether a report scales to ten million rows or chokes on a hundred thousand. This guide covers the modelling decisions that matter most for an Intermediate report author: star schema shape, relationship direction, column hygiene, measure design, and the mistakes that quietly cost performance.

## Start With a Star Schema

The single highest-impact decision is the shape of your tables. A star schema has two kinds of tables:

- **Fact tables** hold transactions, events, or measurements at a defined grain (one row per order line, per sensor reading, per invoice). They are tall and narrow, mostly numeric foreign keys and measures.
- **Dimension tables** describe the things you filter and group by: Date, Customer, Product, Geography. They are short and wide, with a unique key and descriptive text columns.

A snowflake schema extends a dimension into two or more tables (for example, Product joined to Product Category joined to Department). Power BI handles snowflakes, but each extra hop adds relationship lookups at query time. Flatten dimensions at the Power Query stage wherever the cardinality stays reasonable — a Product dimension with 50,000 rows and a Subcategory text column is cheap; splitting it into three tables is not free.

The practical test: draw your tables on paper and connect them. If you see relationships forming loops or fact tables joining to other fact tables, the model needs rework.

## Choose Relationship Directions Deliberately

The default one-to-many relationship from a dimension to a fact table, filtering in a single direction, is correct the vast majority of the time. Two rules keep you out of trouble:

1. Keep filter direction single. Bidirectional cross-filtering creates ambiguous filter paths and unpredictable results once multiple fact tables exist.
2. Set the relationship to **inactive** and activate it with `USERELATIONSHIP` when you need a second role for the same dimension — for example, Order Date and Ship Date both pointing at the Date table.

If you genuinely need a dimension to filter another dimension (a common demand with role-playing hierarchies), consider a bridge table rather than turning on bidirectional filtering across the board.

## Cardinality and Data Types

Every column you import carries cost. Import only what the report needs, and set data types explicitly in Power Query rather than letting the engine infer them.

| Situation | Better choice | Why |
|---|---|---|
| Decimal price with 2 places | Fixed decimal number | Avoids floating-point rounding in aggregations |
| ID that is only ever displayed | Text | Prevents accidental arithmetic and sorting artefacts |
| Boolean flags | True/False | Smallest encoding, clean in visuals |
| Long free-text notes | Remove or keep in a separate table | High-cardinality text destroys compression |

A column's cardinality — the count of distinct values — drives how well VertiPaq compresses it. A Date column stored as datetime with a unique value per second is far larger than one stored as a date. Trim datetimes to dates in Power Query before they reach the model.

Also resist the urge to keep calculated columns that merely concatenate or extract text. If you do not need to slice by the value, compute it inside a measure with DAX variables instead.

## Measures vs Calculated Columns

This distinction trips up nearly everyone moving from Excel.

- A **calculated column** is evaluated row by row at refresh, stored in the model, and consumes memory. It has a row context.
- A **measure** is evaluated at query time within whatever filter context the visual provides. It is not stored and adapts to every slicer.

Put numeric logic in measures. A `Total Sales` measure recalculates correctly when the user filters to a single region; a calculated column of the same name does not respond to filter context at all.

```dax
Total Sales :=
SUMX (
    Sales,
    Sales[Quantity] * Sales[Unit Price]
)

Total Sales LY :=
CALCULATE (
    [Total Sales],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)

Sales Growth % :=
VAR CurrentSales = [Total Sales]
VAR PriorSales   = [Total Sales LY]
RETURN
    DIVIDE ( CurrentSales - PriorSales, PriorSales )
```

Note the use of `VAR` to compute each branch once and keep the formula readable. Variables are evaluated before the `RETURN` expression and cannot be referenced outside their measure.

Calculated columns are still appropriate when you need the value in a slicer, a row-level security filter, or a relationship key. Otherwise, push the logic upstream to Power Query or downstream into a measure.

## Build a Dedicated Date Table

Time intelligence depends on a contiguous Date table marked as a date table, with one row per day and no gaps. Link it to every fact table that has a date column. Do not rely on `AUTO DATETIME` — disable it in options, because it silently creates a hidden date table per datetime column and bloats the model.

A compliant Date table looks like this in DAX:

```dax
Date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2020, 1, 1 ), DATE ( 2026, 12, 31 ) ),
    "Year",        YEAR ( [Date] ),
    "Quarter",     "Q" & QUARTER ( [Date] ),
    "Month Name",  FORMAT ( [Date], "MMM" ),
    "Month Number", MONTH ( [Date] ),
    "Year Month",  FORMAT ( [Date], "YYYY-MM" )
)
```

Sort `Month Name` by `Month Number` so charts display months in calendar order, not alphabetical.

## Naming, Hiding, and Formatting

A model is a product other people maintain. Conventions pay off:

- Prefix fact tables with `Fact` and dimensions with `Dim`, or at minimum group them in display folders.
- Use spaces in measure names (`Total Sales`) and no spaces in column names where you write a lot of DAX — pick one convention and apply it everywhere.
- Hide every key column from report view. Users should never drop `CustomerKey` into a visual.
- Set a format string on each measure (`#,##0.00`, `0.0%`) so visuals inherit consistent display.
- Add descriptions to measures explaining their grain and any exclusions.

## Reduce Model Size and Refresh Time

Performance work starts before DAX. A few habits:

- Remove columns you do not use. The fastest column is the one that is not there.
- Disable `Auto Date/Time` at the file level (File > Options > Data Load).
- Prefer `Table.Buffer` sparingly in Power Query — it can help iterative lookups but hurts memory on large tables.
- Use Import mode unless you have a hard freshness requirement; DirectQuery pushes work to the source on every interaction.
- Consider aggregations or a composite model when a fact table passes roughly a hundred million rows.

```powerquery
let
    Source = Sql.Database("server", "warehouse"),
    Sales  = Source{[Schema="dbo", Item="FactSales"]}[Data],
    // Drop columns the report never references
    Kept   = Table.SelectColumns(
                 Sales,
                 {"OrderDate", "CustomerKey", "ProductKey", "Quantity", "UnitPrice"}
             ),
    Typed  = Table.TransformColumnTypes(
                 Kept,
                 {
                     {"OrderDate", type date},
                     {"CustomerKey", Int64.Type},
                     {"ProductKey", Int64.Type},
                     {"Quantity", Int64.Type},
                     {"UnitPrice", type number}
                 }
             )
in
    Typed
```

Selecting columns immediately after the source keeps the query folding engine from pulling unnecessary data.

## Common Data Model Mistakes

- **Two-way relationships everywhere.** They seem convenient and create non-deterministic results.
- **Fact-to-fact relationships.** Usually a sign the grain is wrong; aggregate one side or build a bridge.
- **Calculated columns for aggregation.** Memory cost with no benefit over a measure.
- **Unmarked date table.** Time intelligence functions misbehave or return blanks.
- **Many-to-many without a bridge.** It works, but the semantics are subtle and often hide a modelling error.
- **Blank foreign keys.** Null keys break relationships silently; handle them explicitly in Power Query.

## FAQ

### Q: Can I use a snowflake schema instead of a star?

Yes, Power BI supports it, and sometimes your source system forces it. But flatten dimensions where the row count stays manageable. Each additional relationship adds a lookup during query execution, and the Model view becomes harder to reason about. Reserve snowflaking for genuinely large or reused sub-dimensions.

### Q: When should I use a calculated column instead of a measure?

Use a calculated column only when the value must exist at the row level: as a slicer field, a relationship key, a sort-by column, or a row-level security filter. For anything that gets aggregated in a visual, a measure is smaller, faster, and responds correctly to filter context.

### Q: How many relationships can a single table have?

Technically many, but a fact table with dozens of active relationships is a warning sign. Use inactive relationships plus `USERELATIONSHIP` inside `CALCULATE` for role-playing dimensions, and keep only one active path between any two tables. Ambiguous paths cause Power BI to reject the model or produce unexpected filter propagation.

### Q: Does bidirectional filtering ever make sense?

Occasionally, with a bridge table or a many-to-many dimension used purely for filtering a single fact table. Turn it on per relationship, not globally, and test totals against a known-good query. For most models, single-direction filtering plus a well-built bridge table solves the same problem more predictably.

### Q: What is the fastest way to check my model size?

Open the Model view, then use the external tool DAX Studio to run VertiPaq Analyzer. It reports the size of every table and column, which quickly reveals oversized columns, redundant calculated columns, and dimensions that should be trimmed.

## Related Reading

- [Data Modeling Star Schema](/tutorials/data-modeling-star-schema/)
- [Bidirectional Filtering Guide](/tutorials/bidirectional-filtering-guide/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [Power BI Date Table](/tutorials/power-bi-date-table/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [DAX Variables Best Practices](/tutorials/dax-variables-guide/)

- [Snowflake Schema vs Star Schema in Power BI](/tutorials/snowflake-schema-power-bi/)