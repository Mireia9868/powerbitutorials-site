---
title: "DAX Troubleshooting Guide: Fix the 15 Most Common Errors"
description: "DAX errors are notoriously unhelpful. This guide covers the 15 most common DAX errors — from blank results to wrong totals to circular dependencies — with exact before-and-after fixes you can copy-paste."
pubDate: 2026-07-20
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "troubleshooting", "errors", "debugging", "best-practices"]
author: "Power BI Tutorials Team"
featured: true
---

DAX is unforgiving. A single misstep with context transition, a misplaced `FILTER`, or a missing date table can produce results that look plausible in development and catastrophically wrong in production. This guide covers the 15 most common DAX errors, with exact fixes you can apply immediately.

## Errors that return BLANK

### 1. Measure returns BLANK in every visual

**Cause:** The most common cause is a data type mismatch — a column that should be numeric is stored as text.

**Fix:** Go to Power Query and verify data types. `SUM` on a text column returns BLANK because text can't be aggregated.

```dax
// If Sales[Revenue] is text type, this returns BLANK
Total Revenue = SUM(Sales[Revenue])

// Fix: change the column type to Decimal Number in Power Query
```

### 2. Time intelligence returns BLANK

**Cause:** Your date table isn't marked as a date table, or the relationship between the date table and fact table is missing.

**Fix:**
1. Go to Model View
2. Select your date table
3. Click "Mark as date table" in the ribbon
4. Choose the date column
5. Verify a relationship exists between `Date[Date]` and `Sales[OrderDate]`

```dax
// Without a marked date table, this returns BLANK:
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Date[Date]))
```

### 3. BLANK vs. 0 confusion

**Cause:** `BLANK` and `0` are different values. `BLANK` means "no data"; `0` means "the value is zero." Treating them interchangeably causes issues.

**Fix:** Use `COALESCE` when you need to display 0 instead of BLANK:

```dax
// Shows BLANK for missing months
Total Revenue = SUM(Sales[Revenue])

// Shows 0 for missing months
Total Revenue Display = COALESCE([Total Revenue], 0)
```

**Warning:** don't use `COALESCE` in the denominator of a ratio — `DIVIDE` handles BLANK correctly, but `0` causes divide-by-zero errors.

## Errors with wrong totals

### 4. Row values are correct but grand total is wrong

**Cause:** Context transition issue. The total row doesn't have the same filter context as the detail rows.

**Fix:** Use `SUMX` over the grouping column:

```dax
// Wrong totals — the grand total doesn't match the sum of rows
Margin % = DIVIDE([Revenue], [Cost])

// Correct — iterates over the grouping column
Correct Margin % =
DIVIDE(
    SUMX(VALUES(Product[Category]), [Revenue]),
    SUMX(VALUES(Product[Category]), [Cost])
)
```

### 5. Percentage always shows 100%

**Cause:** Both numerator and denominator evaluate in the same filter context, so they return the same number.

**Fix:** Use `CALCULATE` with `REMOVEFILTERS` on the denominator:

```dax
// Bug — both sides are identical
% of Total = DIVIDE([Total Revenue], [Total Revenue])

// Fix — denominator ignores the category filter
% of Total =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], REMOVEFILTERS(Product[Category]))
)
```

### 6. Measure returns the same value in every row

**Cause:** You're referencing a measure inside an iterator without triggering context transition, or you're using `ALL` incorrectly.

**Fix:** Wrap the measure reference in `CALCULATE` to trigger context transition:

```dax
// Bug — [Total Revenue] evaluates in the outer context, same for every row
Wrong = ADDCOLUMNS(VALUES(Product[Category]), "Rev", [Total Revenue])

// This actually works because ADDCOLUMNS triggers context transition automatically
// But if you're inside SUMX:
Wrong Sum = SUMX(VALUES(Product[Category]), [Total Revenue])

// If you need per-row evaluation with explicit context:
Right = SUMX(VALUES(Product[Category]), CALCULATE([Total Revenue]))
```

## Errors with filters

### 7. Slicer doesn't filter the visual

**Cause:** The relationship between the dimension and fact table is missing, has the wrong direction, or uses mismatched data types.

**Fix:**
1. Open Model View
2. Check that a relationship exists between the slicer's table and the fact table
3. Verify cardinality is `1:*` (dimension → fact)
4. Verify filter direction is single (dimension → fact)
5. Check that the join columns have the same data type in both tables

### 8. "A table of multiple values was supplied where a single value was expected"

**Cause:** Using `VALUES` where a scalar is expected. `VALUES` returns a table, not a single value.

**Fix:** Use `SELECTEDVALUE` instead:

```dax
// Error when multiple values are visible
Selected Category = VALUES(Product[Category])

// Returns the selected value, or BLANK if multiple are visible
Selected Category = SELECTEDVALUE(Product[Category])

// With a default value
Selected Category = SELECTEDVALUE(Product[Category], "All")
```

### 9. FILTER is slow on large tables

**Cause:** `FILTER(ALL(Sales), ...)` scans every row in the Sales table.

**Fix:** Use boolean filters for simple column conditions:

```dax
// Slow — scans every row
CALCULATE([Total Revenue], FILTER(ALL(Sales), Sales[Status] = "Paid"))

// Fast — uses column dictionary
CALCULATE([Total Revenue], Sales[Status] = "Paid")
```

Reserve `FILTER` for complex conditions that can't be expressed as a single column predicate.

### 10. Bidirectional filter causes double-counting

**Cause:** Enabling bidirectional filtering on a relationship allows filters to propagate in both directions, which can fan out across multiple paths.

**Fix:** Keep relationships single-direction. If you need a fact to filter a dimension, write a measure:

```dax
// Instead of enabling bidirectional filtering:
Products with Sales =
CALCULATETABLE(
    VALUES(Product[ProductKey]),
    FILTER(Sales, [Total Revenue] > 0)
)
```

## Errors with relationships

### 11. RELATED returns BLANK

**Cause:** There's no relationship between the tables, or the row context isn't set up correctly.

**Fix:**
1. Verify a relationship exists in Model View
2. Ensure you're inside a row context (calculated column or iterator)
3. Check that the join columns have matching values

```dax
// In a calculated column — works if relationship exists
Product Name = RELATED(Product[Name])

// In a measure — fails because there's no row context
// Fix: use SELECTEDVALUE or VALUES instead
Product Name = SELECTEDVALUE(Product[Name])
```

### 12. LOOKUPVALUE is slow

**Cause:** `LOOKUPVALUE` performs an unoptimized scan of the lookup table.

**Fix:** Use `RELATED` if a relationship exists (it uses the VertiPaq relationship index):

```dax
// Slow — scans the lookup table
Product Name = LOOKUPVALUE(Product[Name], Product[ProductKey], Sales[ProductKey])

// Fast — uses relationship index
Product Name = RELATED(Product[Name])
```

Use `LOOKUPVALUE` only when no relationship exists and you can't create one.

## Errors with calculations

### 13. Circular dependency detected

**Cause:** Column A references Column B, and Column B references Column A.

**Fix:** Merge the logic into one column, or compute in Power Query:

```dax
// Circular dependency:
ColA = [ColB] * 2
ColB = [ColA] / 2

// Fix: compute both in one expression, or do it in Power Query
ColA = Sales[BaseValue] * 2
ColB = Sales[BaseValue]
```

Power Query runs before the DAX engine and is immune to circular dependencies.

### 14. "Function X has been used in a True/False expression that is used as a table filter expression"

**Cause:** Using a measure inside `FILTER` without proper context.

**Fix:** Wrap the filter in `CALCULATETABLE` or restructure:

```dax
// Error
CALCULATE([Rev], FILTER(Sales, [Total Revenue] > 100))

// Fix — use VALUES to iterate over the column, not the fact table
CALCULATE([Rev], FILTER(VALUES(Product[Category]), [Total Revenue] > 100))
```

### 15. Wrong results from context transition inside iterators

**Cause:** Calling a measure inside `SUMX` or `FILTER` triggers implicit context transition, which may not be what you want.

**Fix:** Be explicit about whether you want context transition:

```dax
// Context transition happens — [Total Cost] evaluates per row
Margin = SUMX(Sales, Sales[Revenue] - [Total Cost])

// No context transition — uses the row-level column directly
Margin = SUMX(Sales, Sales[Revenue] - Sales[Quantity] * Sales[UnitCost])
```

If you're inside an iterator and referencing a measure, context transition is happening whether you want it or not. Be intentional.

## Debugging workflow

When a DAX formula returns unexpected results:

1. **Check data types** — 90% of "BLANK result" bugs are type mismatches
2. **Identify iterators** — every `*X` function creates row context
3. **Trace filter context** — what slicers, visual filters, or CALCULATE arguments are active?
4. **Check for context transition** — are you calling a measure inside an iterator?
5. **Use DAX Studio** — run `EVALUATE` queries to inspect intermediate results:

```dax
EVALUATE
ADDCOLUMNS(
    VALUES(Product[Category]),
    "Revenue", [Total Revenue],
    "AllRevenue", CALCULATE([Total Revenue], ALL(Product[Category])),
    "Pct", DIVIDE([Total Revenue], CALCULATE([Total Revenue], ALL(Product[Category])))
)
```

This shows you exactly what each measure returns per category, revealing where the logic breaks.

## FAQ

**Why does DAX give such unhelpful error messages?**
DAX errors point to where the error manifests, not where it originates. A data type issue in Power Query can surface as a BLANK result in a visual, with no error message at all. The debugging workflow above helps you trace back to the root cause.

**Should I use DAX Studio or Tabular Editor?**
Both. DAX Studio for query analysis and performance profiling. Tabular Editor for model structure, calculation groups, and batch measure editing. Both are free and essential for serious Power BI development.

**How do I know if my DAX is "good"?**
Three indicators: (1) it returns correct results in all filter contexts, (2) it's readable enough that another developer can understand it, (3) it runs fast enough that users don't complain. If any of these fail, the DAX needs work.

## What's next

- Learn [filter context vs. row context](/tutorials/filter-context-row-context-explained) to prevent most of these errors
- Read the [CALCULATE guide](/tutorials/calculate-function) to understand filter modification
- See the [performance optimization guide](/tutorials/power-bi-performance-optimization) for DAX that's not just correct, but fast
- Check the [10 common beginner mistakes](/tutorials/power-bi-common-mistakes-beginners) to avoid these errors in the first place
