---
title: "Filter Context vs Row Context in DAX: The Core Mental Model"
description: "Filter context and row context are the two evaluation contexts that govern every DAX formula. Most calculation errors trace back to confusing them. This guide breaks down both, shows how they interact, and gives you the mental model to predict formula behavior before you write it."
pubDate: 2026-07-12
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "filter-context", "row-context", "evaluation-context", "calculate"]
author: "Power BI Tutorials Team"
featured: false
---

Every DAX formula you write runs inside an *evaluation context*. Get that context wrong and a measure that looks perfectly typed returns a baffling number — or blank. This guide covers the two contexts every analyst must understand: filter context and row context.

## The short version

- **Filter context** = "which rows are currently visible?" Set by slicers, visual cross-filtering, and `CALCULATE` modifiers.
- **Row context** = "which row am I currently on?" Exists only inside iterators (`SUMX`, `FILTER`, `ADDCOLUMNS`) and calculated columns.

A measure without an iterator has filter context but no row context. A calculated column has row context but no filter context (unless you add one with `CALCULATE`).

## Filter context explained

When you drop `[Total Revenue]` into a matrix visual grouped by `Product[Category]`, the measure doesn't sum all rows — it sums only the rows where `Product[Category]` matches the current cell. That visible set of rows *is* the filter context.

```dax
Total Revenue = SUM(Sales[Revenue])
```

Three things contribute to filter context:

1. **Slicers and filters** on the page.
2. **Visual cross-filtering** — clicking a bar in one chart filters the matrix next to it.
3. **`CALCULATE` modifiers** — `CALCULATE([Measure], Product[Category] = "Bikes")` injects a filter.

The critical insight: filter context propagates through **relationships**. If you filter `Product[Category]`, the filter flows downstream to `Sales` via the one-to-many relationship. It does *not* flow upstream unless you enable bidirectional filtering (which has performance costs).

## Row context explained

Row context exists only in two places:

1. **Calculated columns** — each row is evaluated one at a time.
2. **Iterators** — `SUMX`, `AVERAGEX`, `MINX`, `MAXX`, `FILTER`, `ADDCOLUMNS`, `SELECTCOLUMNS`.

```dax
Line Amount = Sales[Quantity] * Sales[UnitPrice]
```

This calculated column works because each row has its own row context — `Sales[Quantity]` means "the Quantity value in *this* row."

But if you write the same expression as a measure, it fails:

```dax
// This will ERROR — measures have no row context
Line Amount = SUM(Sales[Quantity] * Sales[UnitPrice])
```

The fix is to use an iterator:

```dax
Total Line Amount = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
```

`SUMX` walks every row in the (filtered) `Sales` table, evaluates `Quantity * UnitPrice` for each row in row context, then sums the results.

## Context transition: where it gets tricky

Here's the scenario that trips up most analysts. You're inside an iterator (row context) and you reference a measure. What happens?

```dax
Sales with Margin =
ADDCOLUMNS(
    Sales,
    "MarginPct", [Margin Percentage]
)
```

When `[Margin Percentage]` is called inside `ADDCOLUMNS`, the row context is **automatically transformed** into an equivalent filter context. This is called *context transition*, and it's what `CALCULATE` does implicitly when you reference a measure.

Without context transition, `[Margin Percentage]` would evaluate in the outer filter context and return the same value for every row. With it, each row gets its own margin percentage.

## The four combinations

| Scenario | Filter context? | Row context? | Typical result |
|----------|----------------|--------------|----------------|
| Measure in a visual | Yes (from visual) | No | Aggregation over visible rows |
| Calculated column | No (unless CALCULATE) | Yes | Row-level expression |
| `SUMX(Sales, ...)` | Yes (inherited) | Yes (per row) | Row-by-row calc, then sum |
| `CALCULATE([M], ALL(Sales))` | Overridden | No | Ignores current filters |

## Common mistakes

**Mistake 1: Forgetting iterators in measures.**

```dax
// WRONG — no row context in a measure
Average Order Value = SUM(Sales[Revenue]) / SUM(Sales[Quantity])

// This "works" but calculates total revenue / total quantity,
// not the average of per-order values.
```

If you actually want the average of per-order revenue, use:

```dax
Average Order Value = AVERAGEX(Sales, Sales[Revenue])
```

**Mistake 2: Assuming row context filters.**

Row context does *not* automatically filter. If you're inside `SUMX(Sales, ...)` and reference a column from `Product`, DAX uses `VALUES(Product[Column])` — it doesn't filter `Product` to the current row. To get relationship-based filtering inside an iterator, wrap the reference in `CALCULATE`.

**Mistake 3: Confusing `ALL` with removing row context.**

`ALL(Table)` removes *filter* context, not row context. Inside an iterator, `ALL` doesn't change which row you're on — it changes which rows are visible to the aggregation.

## How to debug evaluation context

When a DAX formula returns unexpected results:

1. **Identify the iterators.** Every `*X` function and `FILTER` creates row context.
2. **Trace the filter context.** What slicers, visual filters, or `CALCULATE` arguments are active?
3. **Check for context transition.** Are you calling a measure inside an iterator? That triggers an implicit `CALCULATE`.
4. **Use DAX Studio.** Run the query with `EVALUATE` and inspect the intermediate table to see exactly which rows are visible.

## Summary

Filter context determines *which rows are visible*. Row context determines *which row you're on*. Measures have filter context; calculated columns and iterators have row context. `CALCULATE` is the bridge — it can modify filter context and trigger context transition. Once you internalize these two contexts, most DAX "bugs" become predictable.
