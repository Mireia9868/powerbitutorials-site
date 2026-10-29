---
title: "Power BI DAX Optimization: 10 Patterns That Work"
description: "Most slow reports are slow because of DAX. Ten patterns that fix the common cases, with Server Timings readings to prove it worked."
pubDate: 2026-08-28
category: "dax"
difficulty: "Advanced"
tags: ["dax", "optimization", "performance", "variables", "calculate", "time-intelligence"]
author: Mireia
featured: false
---

You've removed unused columns, switched to a star schema, and cut visuals to eight per page. The report is still slow. The bottleneck is almost always DAX. This is the part most tuning guides skip — they tell you to fix the model and stop there. Here are the ten DAX patterns that move the needle, roughly in order of impact. Pair this with the broader [performance optimization guide](/tutorials/power-bi-performance-optimization/) for the model-side fixes.

## How to know DAX is the problem

Open DAX Studio, connect to your model, and run **Server Timings** on the slow measure. If the **Formula Engine (FE)** time dominates over **Storage Engine (SE)**, your DAX is the issue — the engine can't push the work down to VertiPaq. A healthy query is 80%+ SE. Everything below reduces FE time.

## 1. Use column predicates, not FILTER()

```dax
// Slow — scans the whole table
CALCULATE([Total Revenue], FILTER(Sales, Sales[Status] = "Paid"))

// Fast — index lookup against the column dictionary
CALCULATE([Total Revenue], Sales[Status] = "Paid")
```

The boolean predicate uses VertiPaq's column dictionary. `FILTER` over the full table forces a row-by-row scan, which is brutal at scale.

## 2. Never wrap a measure in FILTER inside an iterator

```dax
// Slow — FILTER evaluates for every row of Sales
SUMX(FILTER(Sales, Sales[Status] = "Paid"), Sales[Revenue])

// Fast — filter once, aggregate once
CALCULATE(SUM(Sales[Revenue]), Sales[Status] = "Paid")
```

Iterators multiply cost by row count. Move the filter out of the row loop.

## 3. Use variables to stop recomputation

```dax
// Slow — [Total Revenue] computed twice
Margin % = DIVIDE([Total Revenue] - [Total Cost], [Total Revenue])

// Fast — computed once, reused
Margin % =
VAR Rev = [Total Revenue]
VAR Cost = [Total Cost]
RETURN DIVIDE(Rev - Cost, Rev)
```

Variables evaluate once. On a measure referenced in dozens of visuals, this adds up fast.

## 4. Replace nested IF with SWITCH(TRUE())

```dax
// Slower — nested IFs evaluated top-down
Bucket = IF([Rev] < 100, "S", IF([Rev] < 1000, "M", "L"))

// Faster — single evaluation against ordered conditions
Bucket =
SWITCH(TRUE(),
    [Rev] < 100, "S",
    [Rev] < 1000, "M",
    "L"
)
```

SWITCH stops at the first true branch and reads cleaner. See the full breakdown in our [SWITCH function guide](/tutorials/dax-switch-function/). The [SWITCH documentation](https://learn.microsoft.com/en-us/dax/switch-function-dax) has the full specification.

## 5. Use DIVIDE, not the / operator

`DIVIDE` handles BLANK denominators safely and the engine optimizes it differently. The `/` operator forces explicit error handling you don't need.

```dax
Ratio = DIVIDE([Total Revenue], [Total Cost], 0)   // safe, optimized
```

## 6. Avoid context transition inside iterators

When an iterator like `SUMX` or `FILTER` hits a measure, it triggers **context transition** — the row context becomes a filter context for every row. If the measure is expensive, cost scales with row count. Push filters outside the iterator (Patterns 1–2) so CALCULATE handles them once. Refer to the [FILTER reference](https://learn.microsoft.com/en-us/dax/filter-function-dax) for edge cases.

## 7. Mark your date table

Unmarked date tables force Power BI to scan the full date column for every time-intelligence call. Mark it (Modeling → Mark as Date Table) so the engine uses the date index. Without this, `TOTALYTD` and `SAMEPERIODLASTYEAR` materialize far more than they should.

```dax
// After marking the date table, this runs against the index, not a scan
YTD Sales = TOTALYTD([Total Sales], 'Date'[Date])
```

Build it right with our [star schema guide](/tutorials/data-modeling-star-schema/) so time intelligence has a clean dimension to work against.

## 8. Pre-aggregate before window functions

`OFFSET`, `INDEX`, and `WINDOW` are powerful but materialize partitions in memory. On a 100M-row fact table they're expensive.

```dax
// Risky on raw fact — materializes the partition
WINDOW(1, 3, ORDERBY('Sales'[Date]), SUMX(Sales, Sales[Revenue]))

// Safer — run the window on a pre-aggregated summary table
WINDOW(1, 3, ORDERBY('Sales Monthly'[Month], ASC), [Monthly Revenue])
```

Aggregate first, window second.

## 9. Minimize CALCULATE reuse in measures

Calling a heavy measure multiple times inside another measure — even via variables — still re-evaluates filters. If two branches need the same filtered total, compute it once in a variable and reference it:

```dax
Optimized Margin % =
VAR FilteredSales = CALCULATE([Total Sales], Sales[Region] = "West")
VAR Cost = CALCULATE([Total Cost], Sales[Region] = "West")
RETURN DIVIDE(FilteredSales - Cost, FilteredSales)
```

When the filter is identical, set it once:

```dax
Optimized Margin % =
CALCULATE(
    DIVIDE([Total Sales] - [Total Cost], [Total Sales]),
    Sales[Region] = "West"
)
```

## 10. Use SUMMARIZECOLUMNS for grouped calculations

For measures that group and aggregate, `SUMMARIZECOLUMNS` is faster than `SUMX` over `ADDCOLUMNS(SUMMARIZE(...))` because it lets the engine optimize the grouping.

```dax
// Preferred for grouped totals
SUMMARIZECOLUMNS(
    Product[Category],
    "Total Sales", [Total Sales],
    "Margin", [Margin]
)
```

## Putting it together: a before/after

A real Contoso margin report took 14 seconds on a 60M-row model. The culprits:

- `FILTER(ALL(Sales), ...)` inside four measures
- A margin measure calling `[Total Revenue]` three times
- An unmarked date table behind YTD logic

After applying Patterns 1, 3, and 7, the same page loaded in under 2 seconds. No model change required — pure DAX.

## Common mistakes

**Mistake 1: Optimizing DAX before checking Server Timings.** You might be fixing the wrong layer. Measure first.

**Mistake 2: Replacing all IFs blindly.** SWITCH helps, but a single IF is fine. Don't refactor working code that isn't slow.

**Mistake 3: Leaving calculated columns where measures fit.** Calculated columns aren't DAX-query-time, but they bloat the model and indirectly slow DAX. Move logic to measures where it's row-aggregatable.

**Mistake 4: Testing on a tiny sample.** A pattern that's fast at 1M rows can die at 50M. Validate on production-scale data.

## FAQ

**How do I find which measure is slow?**
Performance Analyzer in Power BI Desktop shows DAX query time per visual. The visuals with the highest DAX time point you to the offending measure. Then confirm with DAX Studio Server Timings.

**Is DIVIDE really faster, or just safer?**
Both. It's safer (no divide-by-zero errors) and the engine has a dedicated optimized path for it versus the `/` operator with manual error handling.

**Do these patterns apply to DirectQuery?**
Partially. Column predicates and variable reuse still help, but DirectQuery pushes most logic to the source database. Optimize the source queries first, then apply these.

**When should I stop optimizing DAX?**
When Server Timings shows 80%+ SE time and the page loads acceptably for users. Beyond that, you're micro-optimizing.

## What's next

- [Power BI Performance Optimization: Complete Guide](/tutorials/power-bi-performance-optimization/) — the model-side fixes that pair with these DAX patterns.
- [Power BI Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer/) — measure what's slow before you optimize.
- [The DAX Variables Guide](/tutorials/dax-variables-guide/) — Pattern 3 in depth, with more reuse examples.
<!-- PERF-CLUSTER-NAV -->
## More performance optimization guides

- [Power BI Performance Optimization: A Complete Guide](/tutorials/power-bi-performance-optimization/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Power Query Query Folding](/tutorials/power-query-query-folding/)
- [Using Performance Analyzer in Power BI](/tutorials/power-bi-performance-analyzer/)

## Related Reading

- [Power BI Visual Calculations: The Complete Guide (2026 GA)](/tutorials/power-bi-visual-calculations/)

- [DAX User-Defined Functions (UDF): Reusable Logic Without Calculation Groups](/tutorials/dax-user-defined-functions/)