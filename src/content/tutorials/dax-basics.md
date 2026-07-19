---
title: "DAX Basics: The Beginner's Guide to Data Analysis Expressions"
description: "Learn what DAX is, how measures differ from calculated columns, and write your first five formulas with confidence. A practical starting point for every Power BI analyst."
pubDate: 2026-06-15
updatedDate: 2026-07-10
category: "dax"
difficulty: "Beginner"
tags: ["dax", "basics", "measures", "calculated-columns"]
author: "DAX Guide Editorial Team"
featured: true
---

If you've built a Power BI report and hit the wall where drag-and-drop visuals aren't enough, you've met the moment where DAX becomes essential. This guide covers the foundations every analyst needs before moving to advanced patterns.

## What is DAX?

DAX (Data Analysis Expressions) is the formula language behind Power BI, Power Pivot for Excel, and Analysis Services Tabular models. It looks similar to Excel formulas, but behaves very differently because it operates over **tables and columns** rather than cells.

The single most important mental shift: **DAX evaluates over a filtered table, not a range of cells.** Every measure you write runs in a *filter context* — the set of rows currently visible based on slicers, visual cross-filtering, and relationships in your data model.

## Measures vs. Calculated Columns

This is the first decision you'll make for every DAX formula, and it trips up most beginners.

| Aspect | Measure | Calculated Column |
|--------|---------|-------------------|
| When it computes | At query time (on the visual) | At data refresh time |
| Storage | Not stored — computed on demand | Stored in the model (uses memory) |
| Filter context | Dynamic, depends on the visual | Row context only (the current row) |
| Typical use | Aggregations: SUM, AVERAGE, COUNT | Row-level attributes: `Price * Qty` |

**Rule of thumb:** if the result depends on the visual's filter context, write a measure. If the result is the same for every row regardless of filtering, write a calculated column.

> Overusing calculated columns is the #1 cause of bloated Power BI models. Default to measures unless you genuinely need the value stored per row.

## Your first five measures

Assume a `Sales` table with columns `Revenue`, `Quantity`, `UnitCost`, and `OrderDate`.

**Total Revenue:**

```dax
Total Revenue = SUM(Sales[Revenue])
```

**Total Quantity:**

```dax
Total Quantity = SUM(Sales[Quantity])
```

**Average Order Value:**

```dax
Avg Order Value = DIVIDE([Total Revenue], [Total Quantity])
```

Notice we use `DIVIDE` instead of `/`. `DIVIDE` handles divide-by-zero errors gracefully and returns BLANK instead of an error — always prefer it.

**Total Cost** (calculated column referenced by a measure):

```dax
Total Cost = SUMX(Sales, Sales[Quantity] * Sales[UnitCost])
```

`SUMX` is an iterator — it walks row by row, computes the expression, then sums the results. Iterators (`SUMX`, `AVERAGEX`, `MINX`, etc.) are essential when a calculation needs row-level arithmetic before aggregation.

**Gross Margin %:**

```dax
Gross Margin % =
DIVIDE(
    [Total Revenue] - [Total Cost],
    [Total Revenue]
)
```

Format this as a percentage in the Modeling ribbon. Now every visual showing margin respects whatever filters are applied — by product, by region, by date.

## Essential functions to learn first

- **Aggregation:** `SUM`, `AVERAGE`, `MIN`, `MAX`, `COUNTROWS`
- **Iterators:** `SUMX`, `AVERAGEX`, `FILTER`
- **Logical:** `IF`, `SWITCH`, `COALESCE`
- **Filter manipulation:** `CALCULATE`, `ALL`, `ALLEXCEPT`
- **Time intelligence:** `TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`

If you learn only one function deeply, make it `CALCULATE` — it's the gateway to every advanced pattern. See our dedicated [CALCULATE guide](/tutorials/calculate-function) for the deep dive.

## Three common beginner mistakes

**1. Referencing a column where a measure is needed.**

```dax
// Wrong — returns the column reference, not a value
Total = Sales[Revenue]

// Right
Total = SUM(Sales[Revenue])
```

**2. Forgetting that filters flow through relationships.**
A slicer on `Products[Category]` filters `Sales` only if the relationship direction allows it. One-to-many relationships filter from the "one" side (dimension) to the "many" side (fact). If your slicer isn't working, check relationship direction first.

**3. Using `IF` when `SWITCH` is clearer.**

```dax
// Hard to read
Bucket = IF(Sales[Qty] < 10, "Small", IF(Sales[Qty] < 100, "Medium", "Large"))

// Better
Bucket =
SWITCH(
    TRUE(),
    Sales[Qty] < 10, "Small",
    Sales[Qty] < 100, "Medium",
    "Large"
)
```

## What's next

You now have the mental model: measures compute in filter context, calculated columns compute in row context, and iterators let you do row-level math before aggregating. The next leap is learning how to *modify* the filter context — which is exactly what `CALCULATE` does.

Continue with [CALCULATE: The Most Important DAX Function](/tutorials/calculate-function) and [Time Intelligence Patterns](/tutorials/time-intelligence) to round out your foundation.
