---
title: "Month-over-Month and Year-over-Year DAX: A Copy-Paste Template"
description: "Stop rewriting time comparisons. Use this copy-paste DAX template for MoM, YoY, MoM %, and YoY % that works with any marked Date table."
pubDate: 2026-09-23
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["power bi", "time intelligence", "month over month", "year over year", "dax template"]
author: Mireia
featured: false
draft: false
---

Time comparisons — month-over-month (MoM) and year-over-year (YoY) — are in nearly every report, yet everyone rewrites them from scratch. Here is a template you can paste, rename, and reuse. It assumes a **marked Date table** with a single active relationship to your fact.

## The base measure

Every pattern below builds on one base measure. Name it to match your fact:

```dax
Total Sales = SUM ( Fact[SalesAmount] )
```

## MoM (previous month)

```dax
Sales PM =
CALCULATE (
    [Total Sales],
    DATEADD ( 'Date'[Date], -1, MONTH )
)
```

## MoM % change

```dax
Sales MoM % =
VAR Current = [Total Sales]
VAR Previous = [Sales PM]
RETURN
    DIVIDE ( Current - Previous, Previous )
```

`DIVIDE` returns blank instead of an error when `Previous` is zero — use it, do not use `/`.

## YoY (same period last year)

```dax
Sales PY =
CALCULATE (
    [Total Sales],
    SAMEPERIODLASTYEAR ( 'Date'[Date] )
)
```

## YoY % change

```dax
Sales YoY % =
VAR Current = [Total Sales]
VAR Previous = [Sales PY]
RETURN
    DIVIDE ( Current - Previous, Previous )
```

## YTD and the rolling versions

If you also need year-to-date and a rolling 12-month, see [dax-time-intelligence-ytd-qtd-mtd](/tutorials/dax-time-intelligence-ytd-qtd-mtd/) and [rolling-averages-moving-sums-dax](/tutorials/rolling-averages-moving-sums-dax/).

## Why DATEADD not PREVIOUSMONTH

`PREVIOUSMONTH` is fine, but `DATEADD` is more flexible — change `MONTH` to `QUARTER` or `YEAR` and you get the quarter/annual comparison for free. One function, three comparisons.

## Gotcha: no marked date table

If `'Date'[Date]` is not marked as a date table, time intelligence can return wrong totals on the grand total row. Right-click the table → **Mark as Date Table**.

<!-- TODO: add screenshot: Figure 1: power bi mom yoy dax template illustration -->

## FAQ

**Q: My YoY shows blank for the first year — is that wrong?**
A: No. There is no previous year, so `SAMEPERIODLASTYEAR` returns blank, and `DIVIDE` keeps it blank instead of dividing by nothing.

**Q: MoM works but YoY doesn't — why?**
A: Usually the date table doesn't span a full extra year, or the relationship is inactive. Confirm the Date table covers at least last year's full range.

**Q: Can I compare to a custom fiscal year?**
A: Yes — use `DATESYTD` with a `FiscalYearEndDate` argument, or build a fiscal date table. Standard `SAMEPERIODLASTYEAR` follows the calendar.

## Related Reading

- [SamePeriodLastYear Comparison Patterns](/tutorials/sameperiodlastyear-comparison-patterns/)
- [DAX Time Intelligence YTD/QTD/MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [Rolling Averages and Moving Sums](/tutorials/rolling-averages-moving-sums-dax/)
- [Time Intelligence Overview](/tutorials/time-intelligence/)
- [DAX CALCULATE Function](/tutorials/dax-calculate-function/)
- [Data Modeling Star Schema](/tutorials/data-modeling-star-schema/)
