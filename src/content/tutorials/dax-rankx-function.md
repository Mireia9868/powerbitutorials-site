---
title: "DAX RANKX: Rank Data in Power BI with Complete Control"
description: "RANKX is the DAX function for ranking rows by any measure or expression. This guide covers the syntax, the four ranking patterns every analyst needs, ties handling, and the common mistakes that produce wrong results."
pubDate: 2026-07-23
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "rankx", "ranking", "topn", "best-practices"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

RANKX is the DAX function for ranking rows by any measure or expression. This guide covers the syntax, the four ranking patterns every analyst needs, ties handling, and the common mistakes that produce wrong results.

Ranking is one of the most common requests in business reporting — top 10 customers, best-selling products, worst-performing regions. RANKX gives you full control over how ranking works, but its syntax has enough moving parts that small mistakes produce silently wrong results. This guide covers the function end to end, with copy-paste patterns for the four scenarios you'll encounter.

## RANKX syntax

```dax
RANKX(
    <table>,              -- The table to iterate over
    <expression>,         -- What to rank by (evaluated per row)
    [<value>],            -- Optional: the value to find the rank for
    [<order>],            -- ASC (ascending) or DESC (descending)
    [<ties>]              -- Skip or Dense
)
```

The function iterates over `<table>`, evaluates `<expression>` for each row to build an internal ranked list, then returns the rank of `<value>` within that list. If `<value>` is omitted, it defaults to `<expression>` — which is what you want in most cases.

**Key detail:** the `<table>` argument determines *what gets ranked*, and the filter context at the time of evaluation determines *what's visible*. This is where most ranking bugs originate.

## Pattern 1: Simple ranking within filter context

The most common use case — rank products by revenue within the current filter context:

```dax
Product Rank by Revenue =
RANKX(
    ALLSELECTED(Product[Product Name]),
    [Total Revenue],
    ,
    DESC,
    SKIP
)
```

**How this works:**

1. `ALLSELECTED(Product[Product Name])` returns the products currently visible in the visual (respects slicers but ignores the visual's own grouping)
2. `[Total Revenue]` is evaluated for each product to build the ranking
3. `DESC` ranks highest revenue first
4. `SKIP` means tied products get the same rank, and the next rank is skipped (1, 1, 3, 4...)

**Why ALLSELECTED and not ALL?**

`ALL(Product[Product Name])` removes all filters from the product column — including slicers. If a user filters to a specific category, the ranking would still consider all products from all categories. `ALLSELECTED` preserves the slicer context.

```dax
// WRONG — ignores category slicer, ranks across everything
Product Rank = RANKX(ALL(Product[Product Name]), [Total Revenue])

// RIGHT — respects slicer, ranks within visible products
Product Rank = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue])
```

## Pattern 2: Ranking within a category

Ranking products within each category requires modifying the filter context so that the ranking re-evaluates per category. Use `ALLSELECTED` on the product column while keeping the category filter intact:

```dax
Rank Within Category =
RANKX(
    ALLSELECTED(Product[Product Name]),
    CALCULATE([Total Revenue], ALLSELECTED(Product[Product Name])),
    ,
    DESC,
    SKIP
)
```

In a matrix with Category on rows and Product Name on rows beneath it, this measure ranks each product within its parent category. The `ALLSELECTED(Product[Product Name])` removes the per-product filter but keeps the category filter from the matrix row.

**Alternative with VALUES:**

If you don't need slicer sensitivity and want to rank within the current category no matter what:

```dax
Rank Within Category =
RANKX(
    VALUES(Product[Product Name]),
    [Total Revenue],
    ,
    DESC,
    SKIP
)
```

`VALUES` returns the products in the current filter context. When the category filter is active (from the matrix row), only products in that category are returned.

## Pattern 3: SKIP vs DENSE tie handling

The `<ties>` parameter controls how ranks are assigned when two rows have the same value:

- **SKIP** (default): Tied rows get the same rank, and the next rank is skipped. Ranks: 1, 1, 3, 4, 5
- **DENSE**: Tied rows get the same rank, and the next rank is not skipped. Ranks: 1, 1, 2, 3, 4

```dax
// SKIP: if two products tie for rank 1, the next product is rank 3
Rank Skip = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue], , DESC, SKIP)

// DENSE: if two products tie for rank 1, the next product is rank 2
Rank Dense = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue], , DESC, DENSE)
```

**When to use which:**

- **SKIP** is standard for competitive rankings and "top N" filters (a top 3 filter with SKIP correctly excludes the 4th item when there's a tie at rank 1)
- **DENSE** is better when you want to know "how many distinct performance levels are above me" — useful in percentile calculations

## Pattern 4: Top N filter with RANKX

RANKX combined with a visual-level filter creates dynamic top N reports. Create the ranking measure, then filter the visual to show only ranks 1 through N:

```dax
Top 10 Rank =
RANKX(
    ALLSELECTED(Product[Product Name]),
    [Total Revenue],
    ,
    DESC,
    SKIP
)
```

Then in the visual's Filter pane:
1. Add the `Top 10 Rank` measure to the visual-level filters
2. Set the filter type to "Less than or equal to"
3. Set the value to 10

This is dynamic — when slicers change, the ranking recalculates and the top 10 updates automatically.

**Warning:** Don't use the built-in "Top N" filter type on visuals if you need the ranking to respect multiple slicers. The built-in filter sometimes doesn't handle complex filter contexts correctly. The RANKX + visual filter approach is more predictable.

## Common mistakes

### 1. Ranking over the wrong table

```dax
// WRONG — ranks over the entire Sales fact table (millions of rows)
Rank = RANKX(ALL(Sales), [Total Revenue])

// RIGHT — ranks over the dimension column you're displaying
Rank = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue])
```

Ranking over a fact table is the most expensive mistake in RANKX. It forces the engine to evaluate the expression for every row in the fact table. Always rank over a dimension column.

### 2. Forgetting DESC

```dax
// Default is ASC — ranks lowest revenue as #1
Rank = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue])

// Add DESC for "highest = #1"
Rank = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue], , DESC)
```

The default order is ascending. If you want the highest value ranked #1 (which is almost always the case), you must specify `DESC`.

### 3. Rank shows 1 for every row

This happens when the `<table>` argument returns only one row in the current filter context. The measure evaluates `RANKX` over a single-row table, and the single row is always rank 1.

**Cause:** You used `VALUES(Product[Product Name])` in a visual where only one product is visible per row (e.g., Product Name on rows). The filter context for each row contains only that one product.

**Fix:** Use `ALLSELECTED` or `ALL` to expand the table beyond the current row:

```dax
// Shows 1 for every row — VALUES returns only the current product
Wrong Rank = RANKX(VALUES(Product[Product Name]), [Total Revenue])

// Correct — ALLSELECTED returns all visible products
Correct Rank = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue])
```

### 4. Blank values in ranking

If some products have no sales, `[Total Revenue]` returns BLANK. RANKX ranks BLANK as the lowest value, which means:

- With `DESC`: BLANK products get the worst rank
- With `ASC` (default): BLANK products get rank 1

**Fix:** Filter out blanks before ranking:

```dax
Rank Excluding Blanks =
VAR ProductsWithSales =
    FILTER(
        ALLSELECTED(Product[Product Name]),
        [Total Revenue] > 0
    )
RETURN
    RANKX(ProductsWithSales, [Total Revenue], , DESC, SKIP)
```

## RANKX vs RANK function

Power BI also has a `RANK` function (introduced in 2023) that uses window function syntax:

```dax
// RANKX — the classic approach
Rank Classic = RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue], , DESC, SKIP)

// RANK — the window function approach
Rank New =
    RANK(
        DENSE,
        ALLSELECTED(Product[Product Name]),
        ORDERBY([Total Revenue], DESC)
    )
```

**Key differences:**

| Feature | RANKX | RANK |
|---------|-------|------|
| Ties parameter | SKIP / DENSE as 5th argument | DENSE / SKIP as 1st argument |
| Order specification | ASC / DESC as 4th argument | ORDERBY clause |
| Relation support | No | Yes (can partition by category) |
| Performance | Optimized for simple ranking | Better for partitioned ranking |

Use `RANKX` for simple ranking and `RANK` when you need partitioned ranking (rank within category without modifying filter context).

## Debugging ranking with DAX Studio

When a ranking measure returns unexpected results, inspect the intermediate values:

```dax
EVALUATE
ADDCOLUMNS(
    ALLSELECTED(Product[Product Name]),
    "Revenue", [Total Revenue],
    "Rank", RANKX(ALLSELECTED(Product[Product Name]), [Total Revenue], , DESC, SKIP)
)
ORDER BY [Revenue] DESC
```

This shows every product, its revenue, and its rank — making it obvious where the logic breaks.

## FAQ

**Does RANKX work with calculated columns?**
Yes, but the behavior is different. In a calculated column, RANKX operates in row context. You need to use `ALL(Table)` or `ALL(Column)` to break out of the single-row context. Measures are generally preferred for ranking because they respond to filter context dynamically.

**How do I rank by multiple criteria?**
Combine the criteria into a single expression. For example, rank by revenue, then by quantity as a tiebreaker:

```dax
Multi-Criteria Rank =
RANKX(
    ALLSELECTED(Product[Product Name]),
    [Total Revenue] + [Total Quantity] * 0.0001,
    ,
    DESC,
    SKIP
)
```

The multiplier ensures quantity only matters as a tiebreaker — it's too small to change the revenue-based ranking but enough to break ties.

**Why is my RANKX measure slow?**
Three common causes: (1) ranking over a fact table instead of a dimension, (2) the `<expression>` is a complex measure that recalculates per row, (3) the table argument returns too many rows. Use DAX Studio's Performance Analyzer to identify which part is slow.

## What's next

- Learn [filter context vs. row context](/tutorials/filter-context-row-context-explained) to understand why ALLSELECTED is necessary for correct ranking
- Read the [CALCULATE guide](/tutorials/calculate-function) to master filter modification, which controls what RANKX sees
- See the [DAX variables guide](/tutorials/dax-variables-best-practices) for cleaner ranking measures using VAR
- Check the [performance optimization guide](/tutorials/power-bi-performance-optimization) if your ranking measures are slow
