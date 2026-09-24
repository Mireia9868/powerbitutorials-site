---
title: "Percentage of Total in Power BI: Three DAX Patterns and When to Use Each"
description: "Calculate % of total in Power BI with ALL, ALLEXCEPT, and a ratio measure. Learn which pattern respects slicers and which ignores them, with copy-paste DAX."
pubDate: 2026-09-23
category: "dax"
difficulty: "Beginner"
tags: ["power bi", "percentage of total", "dax all", "allexcept", "share"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

"Show me each product's share of total sales" is a top-5 request, and there are three DAX patterns that give different answers depending on whether you want the share to respect the current slicers. This guide shows all three with the exact behavior of each.

## Pattern 1: ALL — share of the grand total (ignores slicers)

```dax
% of Total (ALL) =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALL ( 'Product' ) )
)
```

`ALL ( 'Product' )` removes the product filter, so the denominator is the grand total across **all** products, even if a slicer hides some. Use this for "share of everything".

## Pattern 2: ALLEXCEPT — share within the current group (respects slicers)

```dax
% of Total (ALLEXCEPT) =
DIVIDE (
    [Total Sales],
    CALCULATE (
        [Total Sales],
        ALLEXCEPT ( Sales, Sales[Region] )
    )
)
```

This keeps the `Region` filter but removes the `Product` filter, so you get each product's share **within its region**. This is the pattern most business users actually mean by "% of total".

## Pattern 3: ratio over a category (cleaner ALLEXCEPT alternative)

If you only ever need share within one category, filter just that column:

```dax
% of Region Total =
DIVIDE (
    [Total Sales],
    CALCULATE ( [Total Sales], ALL ( Sales[Product] ) )
)
```

Here `ALL ( Sales[Product] )` removes only the product filter, leaving region (and any other filter) active. Same result as Pattern 2, easier to read.

## Which one to use

| You want… | Use |
|---|---|
| Share of grand total, ignore slicers | Pattern 1 (ALL) |
| Share within a group (region/category) | Pattern 2 or 3 (ALLEXCEPT / ALL on the lower column) |
| A single fixed denominator | CALCULATE with the specific filter removed |

## Gotcha: totals row shows 100%

On the grand total row, the numerator equals the denominator, so the measure shows 100%. That is correct. If you want the total row blank, wrap with `IF ( HASONEVALUE ( Product[Product] ), … )`.

## FAQ

**Q: Why does my % of total not add to 100%?**
A: You used `ALL` but a slicer is filtering the numerator only. Switch to `ALLEXCEPT` for a scoped share.

**Q: ALL vs REMOVEFILTERS?**
A: `REMOVEFILTERS` is the modern, clearer way to remove filters and is preferred inside `CALCULATE`; `ALL` also returns a table and is fine here. Either works for a denominator.

**Q: Can I show % of total on a matrix subtotal?**
A: Yes — the pattern flows through matrix groups; each level computes against its own `ALLEXCEPT` scope if you remove only the leaf column.

## Related Reading

- [DAX CALCULATE Function](/tutorials/dax-calculate-function/)
- [SUMX vs SUM Iterators](/tutorials/sumx-vs-sum-iterators/)
- [Filter Context vs Row Context](/tutorials/filter-context-row-context-explained/)
- [DAX RANKX Function](/tutorials/dax-rankx-function/)
- [Sales Dashboard Tutorial](/tutorials/power-bi-sales-dashboard-tutorial/)
- [Data Modeling Star Schema](/tutorials/data-modeling-star-schema/)
