---
title: "SUMMARIZE vs SUMMARIZECOLUMNS vs GROUPBY"
description: "Three DAX functions that all group rows, and only one is right for a given job. Where each one belongs, and the SUMMARIZE pattern that quietly misbehaves."
pubDate: 2026-11-04
category: dax
tags: ["dax", "summarize", "performance", "calculated-tables"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

Three DAX functions return a grouped table, and they are not interchangeable. Pick the wrong one and you get a result that is either slower than it should be, or subtly incorrect in a way that survives every visual check.

The short version:

| Use | Function |
|---|---|
| A calculated table | `SUMMARIZECOLUMNS` |
| Grouping inside a measure | `SUMMARIZE` or `GROUPBY` |
| Adding columns to the grouping | `SUMMARIZECOLUMNS` or `ADDCOLUMNS` — **not** `SUMMARIZE` |

If you remember nothing else: **do not add extension columns to `SUMMARIZE`.** That is the one habit worth breaking today, and the rest of this article explains why.

## SUMMARIZE: the original, and the trap

`SUMMARIZE` groups a table by one or more columns:

```dax
Product Summary =
SUMMARIZE ( Sales, 'Product'[Category], 'Product'[Subcategory] )
```

That returns a two-column table of distinct pairs. Correct, fast, no surprises.

The trouble starts when you add a third argument:

```dax
-- This is the pattern to avoid
Product Summary =
SUMMARIZE (
    Sales,
    'Product'[Category],
    "Revenue", SUM ( Sales[Amount] )
)
```

This *works*, which is exactly the problem. What DAX actually does here is:

1. group by `Category`,
2. for each group, run `SUM ( Sales[Amount] )` in a context that has been implicitly transitioned from row context to filter context,
3. and do that on top of the grouping, not before it.

On a large fact table the extra context transition is expensive. On a model with ambiguous relationships or inactive relationships it can also return the wrong number — the sum is computed against the group rather than the filter that produced the group.

The same calculation written safely:

```dax
Product Summary =
ADDCOLUMNS (
    SUMMARIZE ( Sales, 'Product'[Category] ),
    "Revenue", CALCULATE ( SUM ( Sales[Amount] ) )
)
```

`CALCULATE` makes the context transition explicit, so you can see what is being evaluated and reason about it. This is the pattern Microsoft's own
[SUMMARIZE reference](https://learn.microsoft.com/en-us/dax/summarize-function-dax)
now recommends in place of the extension-column form.

## SUMMARIZECOLUMNS: the one for calculated tables

`SUMMARIZECOLUMNS` was built for exactly this job:

```dax
Product Summary =
SUMMARIZECOLUMNS (
    'Product'[Category],
    "Revenue", SUM ( Sales[Amount] ),
    "Orders", COUNTROWS ( Sales )
)
```

Cleaner than the `ADDCOLUMNS` version, and faster, because the engine can push the aggregation down instead of iterating.

Three limits worth knowing:

**It cannot be used inside a measure.** `SUMMARIZECOLUMNS` needs a query context and returns a table; a measure must return a scalar. If you try it, the error is immediate and unambiguous.

**It cannot be used in `ADDCOLUMNS` or `FILTER` as a table expression in the same way `SUMMARIZE` can**, because of how it handles filter context. In practice you use it at the top level of a calculated table, or inside `CALCULATETABLE`, rather than nested deep in an iterator.

**Its filter behaviour differs from `SUMMARIZE`.** `SUMMARIZECOLUMNS` respects filter context from the outside but treats its own arguments as grouping columns with automatic non-empty handling. That is usually what you want for a calculated table, and occasionally exactly what you don't — for instance when you need groups that have zero rows.

## GROUPBY: the one that needs an iterator

`GROUPBY` looks like `SUMMARIZE` but behaves differently:

```dax
Category Counts =
GROUPBY ( Sales, 'Product'[Category], "Rows", COUNTX ( CURRENTGROUP (), 1 ) )
```

The catch is `CURRENTGROUP()`. `GROUPBY` produces a table where each row carries an implicit group reference, and you can only read it with `CURRENTGROUP()` — which means `GROUPBY` is only usable **inside an iterator** like `SUMX`, `MAXX` or `COUNTX`.

That makes it useful in a narrow place: when you want to group inside a measure, and then iterate over the groups.

```dax
Categories above target =
SUMX (
    GROUPBY ( Sales, 'Product'[Category] ),
    IF ( CALCULATE ( SUM ( Sales[Amount] ) ) > 100000, 1, 0 )
)
```

For most grouping jobs `SUMMARIZE` does the same thing with less ceremony. `GROUPBY` earns its place when the grouping is an intermediate step in a longer computation, not the final output.

## How to choose, in practice

**You are writing a calculated table.** Use `SUMMARIZECOLUMNS`. It is purpose-built, faster, and the syntax puts the grouping columns and the aggregations in a readable order.

**You are inside a measure and need a grouped table.** Use `SUMMARIZE` with `CALCULATE` for the aggregation, or `ADDCOLUMNS` around it. Never the extension-column form.

**You are iterating over groups inside a measure.** `GROUPBY` with `CURRENTGROUP()` is available, but reach for it only if `SUMMARIZE` genuinely does not fit — in most models it does.

**You are filtering a table by a grouped result.** Wrap whichever function you chose in `CALCULATETABLE`, and check the filter behaviour. This is where `SUMMARIZECOLUMNS` and `SUMMARIZE` differ most, and where a measure that "worked" in one model fails in the next.

## The performance difference, honestly

`SUMMARIZECOLUMNS` is typically the fastest of the three for calculated tables, but the gap is not always dramatic. On a 50-million-row fact table with five grouping columns, expect a visible difference. On a 200,000-row table, all three will finish before the visual renders.

The reason to prefer `SUMMARIZECOLUMNS` is not only speed — it is that its behaviour is easier to predict. The reason to avoid the `SUMMARIZE` extension-column form is not only speed — it is that the context transition happens where you cannot see it.

Write for the model you will have in eighteen months, not the one you have today.

## FAQ

### Q: Can I use SUMMARIZE inside a measure at all?

Yes. `SUMMARIZE` returns a table, and a measure can hold a table variable:

```dax
Distinct categories =
COUNTROWS ( SUMMARIZE ( Sales, 'Product'[Category] ) )
```

That is legal and common. What you cannot do is return the table itself from a measure.

### Q: Why does SUMMARIZECOLUMNS fail inside FILTER?

Because it manages its own filter context for non-empty group elimination, and nesting it inside another filter changes which groups survive. If you need the grouped table as a filter argument, materialise it into a variable first:

```dax
VAR Grouped = SUMMARIZECOLUMNS ( 'Product'[Category] )
RETURN CALCULATE ( [Total Sales], Grouped )
```

### Q: Is GROUPBY ever clearly better than SUMMARIZE?

For grouping alone, no. It becomes the better choice when you need to iterate over groups and the grouping columns are the only thing you need to carry — the syntax makes the intent explicit. Otherwise it is extra ceremony for the same result.

### Q: Does any of this change with DirectQuery?

Yes, at the margins. `SUMMARIZECOLUMNS` can sometimes be pushed to the source as a GROUP BY, while `SUMMARIZE` with an extension column usually cannot and gets computed in the formula engine. In a DirectQuery model the performance gap between the two widens considerably.

## Related Reading

- [The CALCULATE Function in DAX](/tutorials/calculate-function/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX Optimization: 10 Patterns That Work](/tutorials/power-bi-dax-optimization/)
- [DAX Variables: Cleaner Measures](/tutorials/dax-variables-guide/)
- [SUMX vs SUM: When Iterators Matter](/tutorials/sumx-vs-sum-iterators/)
- [Calculated Tables and What-If Parameters](/tutorials/calculated-tables-what-if-parameters/)
- [DAX Basics: What It Is and How It Works](/tutorials/dax-basics/)
