---
title: "Filter Context vs Row Context in DAX: The Core Mental Model"
description: "Filter context and row context are the two evaluation contexts that govern every DAX formula. Most calculation errors trace back to confusing them. This guide breaks down both, shows how they interact, and gives you the mental model to predict formula behavior before you write it."
pubDate: 2026-07-12
updatedDate: 2026-07-20
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "filter-context", "row-context", "evaluation-context", "calculate"]
author: "Power BI Tutorials Team"
featured: false
---

Every DAX formula you write runs inside an *evaluation context*. Get that context wrong and a measure that looks perfectly typed returns a baffling number — or blank. This guide covers the two contexts every analyst must understand: filter context and row context. Master these, and 80% of DAX bugs become predictable.

If you take only one thing from this guide: **filter context decides which rows are visible; row context decides which row you're on.** Everything else follows from that.

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

The critical insight: filter context propagates through **relationships**. If you filter `Product[Category]`, the filter flows downstream to `Sales` via the one-to-many relationship. It does *not* flow upstream unless you enable bidirectional filtering (which has performance costs and can cause silent double-counting).

### How filter context flows through a model

Imagine a simple star schema: `Sales` (fact) → `Product` (dimension), `Customer` (dimension), `Date` (dimension). When a user selects "Bikes" in a category slicer:

1. `Product[Category] = "Bikes"` filter is set on the Product table
2. The filter flows through the `Product → Sales` relationship (one-to-many)
3. `Sales` is now filtered to only rows where the product is a bike
4. Any measure like `[Total Revenue]` computes over that filtered set
5. The filter does **not** flow to `Customer` or `Date` — those remain unfiltered

This is why a one-to-many relationship is described as "filtering from the one side to the many side." The dimension table filters the fact table, not the other way around.

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

### Row context does NOT equal filter context

This is the most common misunderstanding. Having a row context does **not** mean the table is filtered to that row. Row context just means "I'm currently looking at row N." It doesn't set any filter context.

This matters when you reference columns from related tables inside an iterator:

```dax
// Inside SUMX — row context is on Sales, but Product is NOT filtered
Wrong Total =
SUMX(
    Sales,
    Sales[Quantity] * RELATED(Products[UnitPrice])  // RELATED works because of row context
)
```

`RELATED` works here because it uses the row context to look up the matching row in Products via the relationship. But if you tried to use a measure that relies on filter context, it wouldn't work as expected:

```dax
// This evaluates [Total Revenue] in the OUTER filter context, not per-row
Confusing =
SUMX(
    Sales,
    [Total Revenue]  // Returns the same value for every row!
)
```

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

### When context transition bites you

```dax
// Intent: sum the margin for each row
Total Margin =
SUMX(
    Sales,
    Sales[Revenue] - [Total Cost]  // [Total Cost] is a measure
)
```

If `[Total Cost]` is a measure like `SUMX(Sales, Sales[Quantity] * Sales[UnitCost])`, context transition turns it into a per-row calculation — which may or may not be what you want. The result can be wildly different from summing the row-level costs.

**Rule:** whenever you reference a measure inside an iterator, you're triggering context transition. Be explicit about whether that's your intent. If you want the row-level value, use the raw column expression instead of the measure.

## The four combinations

| Scenario | Filter context? | Row context? | Typical result |
|----------|----------------|--------------|----------------|
| Measure in a visual | Yes (from visual) | No | Aggregation over visible rows |
| Calculated column | No (unless CALCULATE) | Yes | Row-level expression |
| `SUMX(Sales, ...)` | Yes (inherited) | Yes (per row) | Row-by-row calc, then sum |
| `CALCULATE([M], ALL(Sales))` | Overridden | No | Ignores current filters |
| Measure inside iterator | Yes + context transition | Yes | Per-row measure evaluation |

## Common mistakes (and fixes)

### Mistake 1: Forgetting iterators in measures

```dax
// WRONG — no row context in a measure, and division is wrong
Average Order Value = SUM(Sales[Revenue]) / SUM(Sales[Quantity])

// This "works" but calculates total revenue / total quantity,
// not the average of per-order values.
```

If you actually want the average of per-order revenue, use:

```dax
Average Order Value = AVERAGEX(Sales, Sales[Revenue])
```

The difference: the first computes a ratio of totals; the second computes the average of per-row values. For most business questions, the second is what you want.

### Mistake 2: Assuming row context filters

Row context does *not* automatically filter. If you're inside `SUMX(Sales, ...)` and reference a column from `Product`, DAX uses `VALUES(Product[Column])` — it doesn't filter `Product` to the current row. To get relationship-based filtering inside an iterator, wrap the reference in `CALCULATE`:

```dax
// Without CALCULATE — Product[UnitPrice] returns all prices, not the matching one
Wrong = SUMX(Sales, Sales[Quantity] * RELATED(Products[UnitPrice]))

// RELATED works here, but if you need a measure to respect the row:
Right = SUMX(Sales, CALCULATE([Total Revenue]))
```

### Mistake 3: Confusing `ALL` with removing row context

`ALL(Table)` removes *filter* context, not row context. Inside an iterator, `ALL` doesn't change which row you're on — it changes which rows are visible to the aggregation.

```dax
// This removes the filter on Sales but keeps iterating row by row
Total All Sales = SUMX(ALL(Sales), Sales[Quantity] * Sales[UnitPrice])
```

### Mistake 4: Wrong totals in a matrix

If your row-level numbers look correct but the grand total is wrong, you're likely hitting a context transition issue. The total row doesn't have the same filter context as the detail rows. The fix is usually to wrap the calculation in a `SUMX` over the grouping column:

```dax
// Instead of a simple ratio that gives wrong totals:
Margin % = DIVIDE([Revenue], [Cost])  // Totals are wrong

// Use a SUMX that respects the visual's grouping:
Correct Margin % =
DIVIDE(
    SUMX(VALUES(Product[Category]), [Revenue]),
    SUMX(VALUES(Product[Category]), [Cost])
)
```

## How to debug evaluation context

When a DAX formula returns unexpected results:

1. **Identify the iterators.** Every `*X` function and `FILTER` creates row context. List them.
2. **Trace the filter context.** What slicers, visual filters, or `CALCULATE` arguments are active?
3. **Check for context transition.** Are you calling a measure inside an iterator? That triggers an implicit `CALCULATE`.
4. **Use DAX Studio.** Run the query with `EVALUATE` and inspect the intermediate table to see exactly which rows are visible:

```dax
EVALUATE
ADDCOLUMNS(
    VALUES(Product[Category]),
    "Revenue", [Total Revenue],
    "AllRevenue", CALCULATE([Total Revenue], ALL(Product[Category]))
)
```

This shows you exactly what `[Total Revenue]` returns per category vs. the grand total — revealing whether your filter context is behaving as expected.

## Real scenario: why my percentage was always 100%

A common support question: "I wrote a percentage measure and every row shows 100%."

```dax
// The bug
% of Total = DIVIDE([Total Revenue], [Total Revenue])
```

Both numerator and denominator evaluate in the same filter context, so they return the same number. The fix: use `CALCULATE` to remove the filter on the denominator:

```dax
% of Total =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], REMOVEFILTERS(Product[Category]))
)
```

Now the denominator ignores the category filter and returns the grand total, giving you the correct percentage. This is the #1 DAX question on the Microsoft Fabric Community forum.

## Summary

Filter context determines *which rows are visible*. Row context determines *which row you're on*. Measures have filter context; calculated columns and iterators have row context. `CALCULATE` is the bridge — it can modify filter context and trigger context transition. Once you internalize these two contexts, most DAX "bugs" become predictable.

For more on `CALCULATE` and filter context manipulation, see our [CALCULATE guide](/tutorials/calculate-function). For common DAX errors and their fixes, see the [DAX troubleshooting guide](/tutorials/dax-troubleshooting-guide).
