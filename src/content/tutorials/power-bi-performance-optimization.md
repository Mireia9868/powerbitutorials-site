---
title: "Power BI Performance Optimization: Reports and DAX"
description: "Find the bottleneck before optimising: Performance Analyzer, then DAX, then the model. A diagnosis order that saves hours of guessing."
pubDate: 2026-07-20
category: "data-modeling"
difficulty: "Advanced"
tags: ["performance", "optimization", "dax", "data-modeling", "vertipaq", "performance-analyzer"]
author: Mireia
featured: true
---

A Power BI report that takes 20 seconds to load isn't just annoying — it kills adoption. Users abandon slow reports and go back to Excel. This guide covers the systematic approach to diagnosing and fixing performance issues, from the easiest wins to advanced model tuning and DAX optimization.

## The performance diagnosis workflow

Before optimizing anything, measure. Power BI has a built-in tool that tells you exactly what's slow.

### Step 1: Use Performance Analyzer

In Power BI Desktop, go to **View → Performance Analyzer → Start recording**. Then interact with your report (click slicers, switch pages, hover over visuals). The tool records how long each visual takes to render, broken down into:

- **DAX query** — time spent running your measures
- **Visual display** — time spent rendering the chart
- **Network** — time fetching data from the source

If the DAX query time dominates, optimize your measures or model. If visual display dominates, reduce the number of visuals or simplify them. If network dominates, check your data source connection. For a step-by-step walkthrough, see our [Performance Analyzer guide](/tutorials/power-bi-performance-analyzer/).

### Step 2: Check model size

In Power BI Desktop, check the file size. If your `.pbix` file is over 500MB, you're likely loading too much data. Every column consumes memory in the VertiPaq engine.

### Step 3: Use DAX Studio for deep analysis

Download DAX Studio (free, open-source). Connect to your Power BI model and run the **Server Timings** feature on a slow query. It breaks DAX execution into:

- **Storage Engine (SE)** — fetching data from VertiPaq (fast, should dominate)
- **Formula Engine (FE)** — complex calculations (slower, indicates DAX needs optimization)

A healthy query is 80%+ SE. If FE dominates, your DAX is doing work the engine can't push down to storage.

## Quick wins (do these first)

### 1. Remove unused columns and rows

This is the #1 performance fix. Every column in your model consumes memory. If you loaded 50 columns but only use 10 in reports, remove the other 40 in Power Query.

**Impact:** 40-60% model size reduction is common. Refresh time drops proportionally.

### 2. Reduce visuals per page

Each visual on a page runs a separate DAX query. A page with 20 visuals runs 20 queries on every interaction.

**Guideline:** maximum 8-10 visuals per page. Use bookmarks, drill-throughs, or tab navigation to split content across multiple pages.

### 3. Replace calculated columns with measures

Calculated columns are stored in the model and consume memory. Measures compute on demand and take zero storage.

```dax
// Bad — stored for every row, bloats the model
Margin = Sales[Revenue] - Sales[Cost]

// Good — computed on demand, no storage
Margin = SUM(Sales[Revenue]) - SUM(Sales[Cost])
```

**Impact:** removing calculated columns from a 50M-row fact table can save hundreds of megabytes.

### 4. Disable cross-filtering where unneeded

By default, every visual cross-filters every other visual on the page. If you have a bar chart and a pie chart showing the same data, they don't need to filter each other.

Select a visual → Format pane → "Edit interactions" → turn off cross-filtering for visuals that don't need it.

## DAX optimization patterns

Most slow reports are slow because of DAX, not the model. These patterns fix the majority of DAX performance problems. For a dedicated deep dive, see our [DAX optimization guide](/tutorials/power-bi-dax-optimization/).

### Use column filters, not FILTER()

```dax
// Slow — scans every row
CALCULATE([Total Revenue], FILTER(Sales, Sales[Status] = "Paid"))

// Fast — uses column dictionary
CALCULATE([Total Revenue], Sales[Status] = "Paid")
```

The boolean filter uses the VertiPaq column dictionary — it's an index lookup, not a row scan. `FILTER(ALL(Sales), ...)` scans every row in the fact table, which is fatal on large models. See the [FILTER reference](https://learn.microsoft.com/en-us/dax/filter-function-dax) for the complete rules.

### Avoid FILTER inside iterators

```dax
// Slow — FILTER runs for every row of Sales
SUMX(FILTER(Sales, Sales[Status] = "Paid"), Sales[Revenue])

// Fast — filter once, then sum
CALCULATE(SUM(Sales[Revenue]), Sales[Status] = "Paid")
```

### Use variables to avoid recomputation

```dax
// Slow — [Total Revenue] computed twice
Margin % =
DIVIDE(
    [Total Revenue] - [Total Cost],
    [Total Revenue]
)

// Fast — computed once
Margin % =
VAR Rev = [Total Revenue]
VAR Cost = [Total Cost]
RETURN DIVIDE(Rev - Cost, Rev)
```

Variables are evaluated once and reused. For measures called in many visuals, this saves significant computation.

### Replace IF with SWITCH for multi-way logic

```dax
// Slower — nested IFs
Bucket = IF([Rev] < 100, "S", IF([Rev] < 1000, "M", IF([Rev] < 10000, "L", "XL")))

// Faster — single SWITCH evaluation
Bucket =
SWITCH(
    TRUE(),
    [Rev] < 100, "S",
    [Rev] < 1000, "M",
    [Rev] < 10000, "L",
    "XL"
)
```

The [SWITCH documentation](https://learn.microsoft.com/en-us/dax/switch-function-dax) has the full specification.

### Use DIVIDE instead of /

`DIVIDE` is not just safer — the engine optimizes it differently than the `/` operator, and it handles BLANK denominators without error-handling overhead.

### Watch out for context transition in iterators

`SUMX` and `FILTER` over a table force context transition when they hit a measure. If your iterator wraps a measure that itself is expensive, the cost multiplies by row count. Push the filter outside the iterator and let CALCULATE handle it, like the FILTER examples above.

### Time intelligence: mark your date table

Unmarked date tables force Power BI to scan the entire date column for every time-intelligence calculation. Mark a proper date table (Modeling → Mark as Date Table) so the engine uses the date index. Pair it with a clean [star schema](/tutorials/data-modeling-star-schema) and your YTD/QTD calculations stop materializing the whole fact table.

### Limit window functions on big tables

`OFFSET`, `INDEX`, and `WINDOW` are powerful but memory-hungry on large fact tables because they materialize partitions. Use them on aggregated or summarized tables, not on 100M-row fact tables directly. When possible, pre-aggregate with a summary table first.

## Model optimization

### Star schema (non-negotiable)

If your model isn't a star schema, nothing else in this guide will help. See our [star schema guide](/tutorials/data-modeling-star-schema). A flat table defeats every VertiPaq optimization.

### Avoid bidirectional filters

Bidirectional relationships force the engine to propagate filters in both directions across every relationship. On models with many tables, this creates exponential filter propagation paths.

**Fix:** keep all relationships single-direction. If you need a fact to filter a dimension, write a measure with `CALCULATETABLE` instead.

### Use aggregation tables for large fact tables

If your fact table has 100M+ rows, create an aggregation table that pre-summarizes by common dimensions (Month, Region, Category). Power BI can use the aggregation for queries that don't need row-level detail.

```dax
// Aggregation table structure
// Sales_Agg: one row per (MonthKey, Region, Category) with SUM(Revenue), SUM(Quantity)
```

Configure in Model View → manage aggregations → map the aggregation columns to the fact table.

### Split fact tables by grain

If you have transactions at different grains (orders vs. daily summaries), don't force them into one fact table. Use separate fact tables connected to conformed dimensions.

## Monitoring ongoing performance

### Set up usage metrics

In Power BI Service, enable usage metrics for your reports. This shows:
- Who's using the report
- When peak usage occurs
- Which pages are most viewed

High-traffic reports should be prioritized for optimization.

### Use the Power BI usage analyzer

The built-in analyzer in Power BI Desktop (View → Performance Analyzer) gives you per-visual timing. Run it after every model change to catch regressions early.

### Watch for refresh failures

Slow refreshes often indicate model issues. If refresh time grows over time, check:
- Are you loading more data than needed?
- Has query folding broken?
- Are calculated columns multiplying?

## Common performance killers (checklist)

- [ ] Flat table instead of star schema
- [ ] More than 10 visuals on a page
- [ ] Calculated columns that could be measures
- [ ] `FILTER(ALL(Table), ...)` inside CALCULATE
- [ ] Bidirectional relationships enabled
- [ ] Unused columns loaded into the model
- [ ] No marked date table (time intelligence scans instead of using indexes)
- [ ] Complex DAX in card visuals (cards compute on every interaction)
- [ ] Window functions running against the raw fact table

## FAQ

**How big is too big for a Power BI model?**
Pro license: 1GB per dataset. Premium: up to 100GB. But "big" isn't just about size — a 500MB model with a star schema can outperform a 100MB flat table. Focus on structure, not just size.

**Should I use Import or DirectQuery?**
Import for anything under 1GB — it's 10-100x faster. DirectQuery only when data must be real-time or exceeds memory limits. DirectQuery pushes every visual interaction to the source database, which is slow.

**Why is my report fast in Desktop but slow in Service?**
Check your capacity. Shared capacity has resource limits. Also, the Service may have different data freshness — if Desktop has cached data and Service is querying live, timing differs.

**My DAX runs fine on 1M rows but dies at 50M — what changed?**
Volume exposes bad patterns. `FILTER(ALL(...))`, nested iterators, and unmarked date tables all scale linearly or worse. The same measure that costs 50ms on 1M rows can cost several seconds at 50M. Apply the DAX optimization patterns above before adding hardware.

## What's next

Performance optimization is iterative. Start with the quick wins (remove columns, reduce visuals), then tackle DAX patterns, then model structure. For a focused DAX tuning reference, see our [DAX optimization guide](/tutorials/power-bi-dax-optimization/). To find what's actually slow in your report, start with the [Performance Analyzer guide](/tutorials/power-bi-performance-analyzer/). For model design, revisit the [star schema guide](/tutorials/data-modeling-star-schema).
<!-- PERF-CLUSTER-NAV -->
## More performance optimization guides

- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Power Query Query Folding](/tutorials/power-query-query-folding/)
- [Using Performance Analyzer in Power BI](/tutorials/power-bi-performance-analyzer/)

## Related Reading

- [Power BI Dataflows Explained (vs Datasets)](/tutorials/power-bi-dataflows/)

- [Power BI Data Model Best Practices](/tutorials/power-bi-data-model-best-practices/)