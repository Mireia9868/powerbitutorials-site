---
title: "Measure vs Calculated Column in Power BI"
description: "The first real decision you make in a Power BI model is where a calculation belongs."
pubDate: 2026-10-09
category: dax
tags: ["dax", "data modeling"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

The first real decision you make in a Power BI model is where a calculation belongs. Two options look almost identical in the formula bar, but they behave in completely different ways: a **calculated column** and a **measure**.

Choosing wrong leads to bloated models, slow reports, wrong totals, and filters that appear to do nothing. This tutorial explains how each object works, when to use which, and how to convert one into the other without breaking your report.

## The one-sentence difference

A **calculated column** is computed row by row when the model refreshes, then stored in the table like any other column.

A **measure** is computed at query time by the visuals that need it, using whatever filters are currently active.

That single difference drives everything else: memory usage, evaluation context, and where you can use the calculation at all.

## How a calculated column works

A calculated column is created in the Data view (or from the Modelling tab). It evaluates **once per row** of the table, using the values already present in that row. The result is materialized — it physically lives in the model and consumes RAM, the same as an imported column.

```dax
Profit Margin % =
DIVIDE(
    Sales[SalesAmount] - Sales[CostAmount],
    Sales[SalesAmount]
)
```

This works because `SalesAmount` and `CostAmount` exist on every row of `Sales`. The column is filled during refresh. If your refresh takes 40 minutes, some of that time is this column being stored for millions of rows.

The key context here is a **row context**: DAX is standing on one row and can read its columns directly. This is why a calculated column cannot reference another table's columns without `RELATED` or `RELATEDTABLE`.

## How a measure works

A measure is written in the Report view and has no row context of its own. It only knows the **filter context** created by the visual, slicers, and any `CALCULATE` modifiers.

```dax
Total Sales = SUM ( Sales[SalesAmount] )

Profit Margin % :=
DIVIDE (
    [Total Sales] - [Total Cost],
    [Total Sales]
)
```

Nothing is stored. When a card visual shows `Profit Margin %`, Power BI asks the engine "what is the margin for the current filter context?" and gets a number back. Change the slicer, and the answer changes without a refresh.

This is why measures are the correct choice for ratios, percentages and totals. A column storing a per-row ratio cannot be summed — the sum of ratios is not the ratio of the totals.

## Side-by-side comparison

| | Calculated column | Measure |
|---|---|---|
| Evaluated | At refresh, per row | At query time, per filter context |
| Stored in model | Yes, consumes memory | No |
| Context required | Row context | Filter context |
| Usable in slicers / rows / axis | Yes | No |
| Usable in a card / values well | Yes, but usually wrong for aggregation | Yes, this is its purpose |
| Can reference other measures | No | Yes |
| Supports `CALCULATE` | Yes, but context is fixed per row | Yes, this is the core pattern |

The last two rows matter most in practice. A calculated column can call `CALCULATE`, but it resolves against the row it belongs to — it cannot react to a slicer. A measure can do both, and is the only object that understands what the user has filtered.

## Use `RELATED` and `EARLIER` correctly

Two functions trip up beginners because they only work in calculated columns, never in measures.

`RELATED` pulls a value across a many-to-one relationship into the current row:

```dax
Product Category =
RELATED ( Products[Category] )
```

`EARLIER` is more subtle. It does not mean "the previous row" or "the outer loop" in any generic sense. It requires a **nested row context** — two row contexts stacked, with `EARLIER` referring to the outer one. Refer to the [EARLIER reference](https://learn.microsoft.com/en-us/dax/earlier-function-dax) for edge cases.

A classic pattern is ranking customers by sales inside a calculated column:

```dax
Customer Rank =
COUNTROWS (
    FILTER (
        Customers,
        Customers[Total Sales] > EARLIER ( Customers[Total Sales] )
    )
) + 1
```

The outer row context is created by the calculated column itself. The inner row context comes from `FILTER` iterating `Customers`. `EARLIER` reaches back to the outer one. If you paste this into a measure, or into a single row context, it fails or silently returns 1 for every row.

For ranking specifically, `RANKX` is usually cleaner and works in both columns and measures.

## Decision rules you can apply in ten seconds

Ask these questions in order:

1. **Does the value need to respond to a slicer, filter or visual grouping?** If yes, it is a measure. Full stop.
2. **Is it a ratio, percentage, average or any non-additive number?** Use a measure. Aggregating a stored ratio produces wrong totals.
3. **Do you need it in a slicer, on an axis, in a matrix row header, or as a sort key?** Use a calculated column. Measures cannot go in these places.
4. **Is it a fixed attribute of a row that never changes with the report context** — a bucket, a flag, a concatenated key, a category label? A calculated column is fine.
5. **Is the table huge (millions of rows) and the calculation expensive?** Lean towards a measure, or push the logic upstream into Power Query.

A practical example: you want profit margin by product category. The margin itself is a measure. If you also want to sort categories by margin band ("High", "Medium", "Low"), that band is a calculated column, because it must sit on the axis.

## Common mistakes

**Storing a percentage as a column.** `SUM(Sales[Margin %])` gives a number that means nothing. Use a measure.

**Using a measure where a column is required.** Drag a measure to the Rows area of a matrix and Power BI refuses, or wraps it in an implicit aggregation you did not ask for.

**Assuming a calculated column is free.** Every one adds to the VertiPaq footprint and slow down refresh. On a fact table with 50 million rows, a `SWITCH`-heavy column can add hundreds of megabytes.

**Filtering a measure with a slicer set to the same column.** A measure computes after filters; a column is fixed. If a user filters a slicer to "High" but the measure ignores it, the model is behaving correctly — the filter simply has nothing to bind to.

## Converting between the two

From a calculated column to a measure: remove the row-by-row logic and wrap it in an aggregator.

```dax
-- Column (per row)
Revenue Band = IF ( Sales[SalesAmount] > 1000, "High", "Low" )

-- Measure (aggregated over the filter context)
High Value Sales =
CALCULATE (
    [Total Sales],
    FILTER ( Sales, Sales[SalesAmount] > 1000 )
)
```

From a measure to a column: you cannot, unless the calculation is naturally row-scoped. A measure that depends on slicers has no meaning during refresh, because there is no user and no filter context.

## Performance notes

Measures are not automatically faster — a badly written measure with `FILTER` over a fact table can be slower than a stored column. The rule is: columns trade memory for speed and lose flexibility; measures trade CPU for flexibility and cost nothing when unused.

Use Performance Analyzer to see which visuals spend time on storage engine versus formula engine queries. If a measure is causing a large number of formula engine calls, it usually needs rewriting rather than converting to a column.

## FAQ

### Q: Can a measure reference a calculated column?

Yes. Measures can read any column, including calculated ones. The reverse is not true — a calculated column cannot call a measure, because measures need a filter context that does not exist during refresh.

### Q: Why does my total row show a wrong number when I use a calculated column?

Because the column is summed, not recomputed. If the column holds a ratio or an average, the total is the sum of those per-row values, which is arithmetically meaningless. Replace it with a measure that recalculates at the total level.

### Q: Does a calculated column slow down refresh?

Yes. It is evaluated for every row and then stored. On large fact tables this is measurable. If the logic is simple, consider doing it in Power Query instead, where it runs once during load and can be folded into the source query.

### Q: Can I put a measure on a slicer?

No. Slicers need a column to list distinct values. If you need users to filter by something derived from a measure, build a calculated column for the categories and let the measure respond to the slicer selection.

### Q: Is a measure always better than a calculated column?

No. Measures are better for anything context-sensitive, but they cannot appear on axes, in slicers, or as sort keys. Calculated columns remain the right tool for static row-level attributes.

## Related Reading

- [DAX Basics](/tutorials/dax-basics/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [The CALCULATE Function](/tutorials/calculate-function/)
- [DAX EARLIER Function](/tutorials/dax-earlier-function/)
- [DAX Variables Best Practices](/tutorials/dax-variables-guide/)
- [Star Schema Data Modeling](/tutorials/data-modeling-star-schema/)
- [Common Mistakes Beginners Make in Power BI](/tutorials/power-bi-common-mistakes-beginners/)
- [Percentage of Total in Power BI](/tutorials/power-bi-percentage-of-total/)
