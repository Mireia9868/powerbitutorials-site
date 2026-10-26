---
title: "DAX EARLIER Explained: Reference the Previous Row in a Nested Row Context"
description: "EARLIER reaches a parent row context from inside a nested iteration. When you still need it, and the cleaner alternatives to use instead."
pubDate: 2026-09-23
category: "dax"
difficulty: "Advanced"
tags: ["power bi", "dax", "earlier", "nested row context", "rankx"]
author: Mireia
featured: false
draft: false
---

If you have spent more than a week writing DAX, you have hit it: a calculated column that needs the "current" value of a row **and** a value from the same table one level up. That is exactly what `EARLIER` is for — and exactly why most beginners find it confusing. This guide explains what `EARLIER` actually references, shows a worked example, and then shows the patterns that make you not need it at all. Microsoft's [EARLIER reference](https://learn.microsoft.com/en-us/dax/earlier-function-dax) covers the full syntax.

## What EARLIER really does

`EARLIER` returns the value of a column in an **outer** row context — a row context created by a parent iterator, not the innermost one you are currently in.

A row context is created by:
- a calculated column (one per row of the table), and
- iterator functions like `SUMX`, `FILTER`, `RANKX`, `ADDCOLUMNS`, `MAXX`.

When an iterator runs *inside* a calculated column, you get **two** row contexts stacked: the column's own row, and the row the iterator is looping over. `EARLIER` reaches the outer one. `EARLIEST` reaches two levels up.

<!-- TODO: add screenshot: Figure 1: dax earlier function illustration -->

## The classic example: rank within a category

Say you have a `Sales` table and want a column that ranks each row by `Amount` **within its own `Product`**. A naive `RANKX` in a column ranks across the whole table, not per product. `EARLIER` fixes that:

```dax
Rank within Product =
RANKX (
    FILTER (
        Sales,
        Sales[Product] = EARLIER ( Sales[Product] )
    ),
    Sales[Amount],
    ,
    DESC,
    DENSE
)
```

Here is what happens step by step:
1. The calculated column creates a row context for each `Sales` row.
2. `FILTER` iterates `Sales` again, creating a **second** row context.
3. Inside `FILTER`, `EARLIER ( Sales[Product] )` pulls the product of the *outer* (column) row, so the filter keeps only rows of the same product.
4. `RANKX` then ranks only within that subset. Microsoft's [FILTER reference](https://learn.microsoft.com/en-us/dax/filter-function-dax) covers the full syntax.

Without `EARLIER`, the inner `Sales[Product]` would refer to the row `FILTER` is currently scanning — which is always equal to itself, so the filter would never narrow correctly.

## When you should NOT reach for EARLIER

`EARLIER` only works in a **calculated column**, because it depends on a row context. Most real reporting is better done with measures, which have no row context and therefore cannot use `EARLIER` at all. Three modern replacements:

### 1. Use a measure with RANKX and a visual context

If the ranking is for a visual, do it as a measure:

```dax
Rank by Product Measure =
RANKX (
    ALLSELECTED ( Sales[Product] ),
    [Total Amount],
    ,
    DESC,
    DENSE
)
```

This ranks products in the current visual filter, no column, no `EARLIER`.

### 2. Use variables to capture the outer value

When you do need a column, a variable is clearer than `EARLIER` and easier to read:

```dax
Rank within Product (var) =
VAR CurrentProduct = Sales[Product]
RETURN
    RANKX (
        FILTER ( Sales, Sales[Product] = CurrentProduct ),
        Sales[Amount],
        , DESC, DENSE
    )
```

`CurrentProduct` captures the outer row context before the inner `FILTER` shadows it. Same result, no `EARLIER` keyword, far easier to debug.

### 3. Use window functions (Power BI / DirectQuery friendly)

Newer Power BI supports `RANK` and `INDEX` window functions that handle grouping natively:

```dax
Rank within Product (window) =
RANK ( DENSE, Sales, ORDERBY ( Sales[Amount], DESC ), PARTITIONBY ( Sales[Product] ) )
```

This reads top to bottom and avoids both `EARLIER` and manual `FILTER` subsets.

## Performance note

`EARLIER` wrapped in `FILTER ( FullTable, ... )` forces a row-by-row scan of the whole table for **every** row — it is one of the slower patterns in DAX. On a large table, prefer the window function or a pre-grouped summary table. See [power-bi-dax-optimization](/tutorials/power-bi-dax-optimization/) and [power-bi-performance-analyzer-guide](/tutorials/power-bi-performance-analyzer/) for measuring it.

## FAQ

**Q: Is EARLIER deprecated?**
A: No, it still works. But variables and window functions are preferred because they are easier to read and usually faster.

**Q: Why do I get an error "EARLIER has no outer row context"?**
A: You used it where no parent row context exists — typically inside a measure, which has a filter context but no row context. Capture the value with a variable inside `SUMX` instead, or rewrite as a measure.

**Q: EARLIER vs EARLIEST?**
A: `EARLIER` goes one level up; `EARLIEST` goes to the top level regardless of depth. Use `EARLIEST` only when you are three or more iterators deep.

## Related Reading

- [DAX Variables Guide](/tutorials/dax-variables-guide/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX RANKX Function](/tutorials/dax-rankx-function/)
- [Calculated Tables and What-If Parameters](/tutorials/calculated-tables-what-if-parameters/)
- [DAX Basics](/tutorials/dax-basics/)
- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
