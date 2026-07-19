---
title: "SUMX vs SUM in DAX: When Iterators Matter and When They Don't"
description: "SUM is simple and fast. SUMX is flexible and powerful. Choosing the wrong one leads to incorrect totals or bloated models. This guide covers the difference, when each is appropriate, and the three patterns where SUMX is the only correct choice."
pubDate: 2026-07-14
category: "dax"
difficulty: "Beginner"
tags: ["dax", "sumx", "sum", "iterators", "aggregation"]
author: "Power BI Tutorials Team"
featured: false
---

`SUM` and `SUMX` look almost identical, but they solve different problems. Pick the wrong one and your totals will be wrong — silently wrong, with no error message. This guide covers when to use each and the three scenarios where only an iterator works.

## The one-sentence difference

- **`SUM(Column)`** adds up all the values in a single column.
- **`SUMX(Table, Expression)`** evaluates an expression *row by row*, then sums the results.

`SUM` can't do row-by-row math. `SUMX` can.

## When SUM is enough

If your calculation is "add up this column," use `SUM`. It's faster, simpler, and the intent is obvious.

```dax
Total Revenue = SUM(Sales[Revenue])
Total Quantity = SUM(Sales[Quantity])
```

No row context needed. The column already exists with the value you want. `SUM` is the right tool.

## When you need SUMX

Three scenarios require an iterator:

### 1. Row-level multiplication

You have `Quantity` and `UnitPrice` columns. You want total revenue, but there's no pre-calculated `Revenue` column in the table.

```dax
// This fails — measures have no row context
Total Revenue = SUM(Sales[Quantity] * Sales[UnitPrice])

// This works — SUMX evaluates the multiplication per row
Total Revenue = SUMX(Sales, Sales[Quantity] * Sales[UnitPrice])
```

`SUMX` walks every row in the (filtered) `Sales` table, computes `Quantity * UnitPrice` for that row, stores it in memory, then sums all the stored values.

### 2. Conditional aggregation

You want to sum values, but only for rows that meet a condition.

```dax
High Value Revenue =
SUMX(
    FILTER(Sales, Sales[Revenue] > 1000),
    Sales[Revenue]
)
```

Here `FILTER` returns a subset of `Sales`, and `SUMX` sums `Revenue` over just those rows. (You could also use `CALCULATE(SUM(Sales[Revenue]), Sales[Revenue] > 1000)` — both work, and the `CALCULATE` version is often faster for simple conditions.)

### 3. Multi-table expressions

When the expression involves columns from related tables, you need row context to evaluate the relationship per row.

```dax
Weighted Discount =
SUMX(
    Sales,
    Sales[Revenue] * RELATED(Discounts[Rate])
)
```

`RELATED` pulls a value from the parent table for each row in `Sales`. Without the iterator, there's no row context for `RELATED` to work in.

## The performance question

A common worry: "Is `SUMX` slower than `SUM`?"

**Usually no**, because the Power BI engine is optimized for columnar iteration. But there are cases where `SUMX` hurts:

- **Iterating a huge table with a complex expression** — if the expression calls another measure that itself uses iterators, you can get O(n²) behavior.
- **Using `SUMX` when `SUM` would do** — unnecessary complexity for no benefit.

```dax
// Unnecessary SUMX — SUM is simpler and identical
Total Revenue = SUMX(Sales, Sales[Revenue])  // works but pointless
Total Revenue = SUM(Sales[Revenue])           // preferred
```

**Rule of thumb:** use `SUM` by default. Switch to `SUMX` only when the expression can't be precomputed into a column.

## The iterator family

`SUMX` is one of many iterators. They all share the same row-by-row pattern:

| Function | Returns |
|----------|---------|
| `SUMX` | Sum of the expression |
| `AVERAGEX` | Average of the expression |
| `MINX` / `MAXX` | Min / max of the expression |
| `COUNTX` | Count of non-blank values |
| `COUNTAX` | Count of non-blank values (including text) |
| `RANKX` | Rank of each row |
| `TOPN` | Top N rows (returns a table) |

If you understand `SUMX`, you understand the whole family.

## A practical example

You have a `Sales` table with `Quantity`, `UnitPrice`, and `DiscountPct`. You want net revenue after discount.

```dax
Net Revenue =
SUMX(
    Sales,
    Sales[Quantity] * Sales[UnitPrice] * (1 - Sales[DiscountPct])
)
```

Try to do this with `SUM` alone — you can't. The discount applies per row, so you need row context.

**Alternative:** add a calculated column `NetAmount = Quantity * UnitPrice * (1 - DiscountPct)`, then `SUM(Sales[NetAmount])`. This works but stores the column in memory — fine for small models, problematic for large ones. The `SUMX` approach computes on demand without storage.

## Common mistakes

**Mistake 1: Nesting iterators unnecessarily.**

```dax
// Slow — nested SUMX
Total =
SUMX(
    Sales,
    Sales[Revenue] * SUMX(RELATEDTABLE(Returns), Returns[Amount])
)
```

If the inner `SUMX` doesn't depend on the outer row, pull it out into a separate measure.

**Mistake 2: Using `SUMX` when `CALCULATE` is clearer.**

```dax
// Works but verbose
Bike Revenue = SUMX(FILTER(Sales, RELATED(Product[Category]) = "Bikes"), Sales[Revenue])

// Cleaner and often faster
Bike Revenue = CALCULATE(SUM(Sales[Revenue]), Product[Category] = "Bikes")
```

Both are correct. The `CALCULATE` version is easier to read and lets the engine optimize the filter.

## Summary

Use `SUM` for simple column totals. Use `SUMX` when you need row-by-row math, conditional aggregation, or multi-table expressions. Don't use `SUMX` as a default — it adds complexity without benefit when `SUM` suffices. When in doubt, start with `SUM` and switch to `SUMX` only if the expression requires row context.
