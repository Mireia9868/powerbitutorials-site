---
title: "SAMEPERIODLASTYEAR and Date Comparison Patterns in DAX"
description: "Year-over-year comparison is the most common business question in reporting. SAMEPERIODLASTYEAR is the simplest function for it, but it's just the start. This guide covers YoY, MoM, QoQ, and the custom comparison patterns for fiscal calendars and non-standard periods."
pubDate: 2026-07-20
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["dax", "sameperiodlastyear", "yoy", "mom", "date-comparison", "time-intelligence"]
author: "Power BI Tutorials Team"
featured: false
---

"How are we doing versus last year?" is the question behind most Power BI reports. DAX has a family of time intelligence functions for date comparison, but they're easy to get wrong — especially around fiscal calendars, partial periods, and custom comparisons. This guide covers the core patterns and the edge cases that trip up most analysts.

## Prerequisites

Same as all time intelligence: a proper date table, marked as a date table, with a relationship to your fact table. No exceptions.

## Pattern 1: Year-over-year (YoY)

The simplest comparison — this period vs. the same period last year.

```dax
Revenue YoY =
VAR Current = [Total Revenue]
VAR PriorYear =
    CALCULATE(
        [Total Revenue],
        SAMEPERIODLASTYEAR(Date[Date])
    )
RETURN
    DIVIDE(Current - PriorYear, PriorYear, 0)
```

`SAMEPERIODLASTYEAR` shifts the current filter context back one year. If the current context is "January 2026," it returns "January 2025."

**Variant: absolute difference instead of percentage.**

```dax
Revenue YoY Δ = [Total Revenue] - CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(Date[Date]))
```

## Pattern 2: Month-over-month (MoM)

Compare the current month to the previous month.

```dax
Revenue MoM % =
VAR Current = [Total Revenue]
VAR PriorMonth =
    CALCULATE(
        [Total Revenue],
        DATEADD(Date[Date], -1, MONTH)
    )
RETURN
    DIVIDE(Current - PriorMonth, PriorMonth, 0)
```

`DATEADD` is the general-purpose date shifter. `DATEADD(Date[Date], -1, MONTH)` shifts back one month; `DATEADD(Date[Date], -1, YEAR)` shifts back one year (equivalent to `SAMEPERIODLASTYEAR`).

**Why use `DATEADD` over `SAMEPERIODLASTYEAR`:** `DATEADD` supports any interval (day, month, quarter, year) and any offset. `SAMEPERIODLASTYEAR` is specifically for one year back. Use `DATEADD` when you need flexibility.

## Pattern 3: Quarter-over-quarter (QoQ)

```dax
Revenue QoQ % =
VAR Current = [Total Revenue]
VAR PriorQuarter =
    CALCULATE(
        [Total Revenue],
        DATEADD(Date[Date], -1, QUARTER)
    )
RETURN
    DIVIDE(Current - PriorQuarter, PriorQuarter, 0)
```

Same pattern, different interval. The structure is identical — only the `DATEADD` parameter changes.

## Pattern 4: Year-to-date vs. prior year-to-date

Compare the running total for this year to the running total for the same period last year.

```dax
YTD vs Prior YTD % =
VAR CurrentYTD =
    CALCULATE([Total Revenue], DATESYTD(Date[Date]))
VAR PriorYTD =
    CALCULATE(
        [Total Revenue],
        DATESYTD(Date[Date]),
        SAMEPERIODLASTYEAR(Date[Date])
    )
RETURN
    DIVIDE(CurrentYTD - PriorYTD, PriorYTD, 0)
```

**How it works:**
- `DATESYTD(Date[Date])` filters to the current year up to the current date.
- `SAMEPERIODLASTYEAR` shifts that range back one year.
- The combination gives "the same YTD range, but last year."

This is the pattern for "are we tracking ahead of last year?" reporting.

## Pattern 5: Fiscal calendar comparisons

If your fiscal year doesn't match the calendar year (e.g., fiscal year starts in July), use `DATESYTD` with a year-end parameter:

```dax
Fiscal YTD Revenue =
CALCULATE(
    [Total Revenue],
    DATESYTD(Date[Date], "06-30")
)
```

For fiscal YoY:

```dax
Fiscal YoY % =
VAR Current = [Total Revenue]
VAR PriorFiscalYear =
    CALCULATE(
        [Total Revenue],
        DATEADD(Date[Date], -1, YEAR)
    )
RETURN
    DIVIDE(Current - PriorFiscalYear, PriorFiscalYear, 0)
```

`DATEADD` with `-1, YEAR` works regardless of fiscal calendar — it shifts the date back 365 days, which aligns with the same fiscal period last year.

**Tip:** add a `FiscalYear` column to your date table (e.g., "FY2026" for dates from July 2025 to June 2026) so users can filter by fiscal year directly.

## Pattern 6: Custom period comparison

For comparisons that don't fit standard intervals (e.g., "compare this 45-day promotion to the 45 days before it"), use explicit date filters:

```dax
Promotion vs Pre-Promotion % =
VAR PromoStart = DATE(2026, 3, 1)
VAR PromoEnd = DATE(2026, 4, 14)
VAR PrePromoStart = DATE(2026, 1, 15)
VAR PrePromoEnd = DATE(2026, 2, 28)
VAR PromoRevenue =
    CALCULATE(
        [Total Revenue],
        Date[Date] >= PromoStart && Date[Date] <= PromoEnd
    )
VAR PrePromoRevenue =
    CALCULATE(
        [Total Revenue],
        Date[Date] >= PrePromoStart && Date[Date] <= PrePromoEnd
    )
RETURN
    DIVIDE(PromoRevenue - PrePromoRevenue, PrePromoRevenue, 0)
```

This pattern is verbose but handles any custom date range — useful for A/B tests, promotions, and event comparisons.

## Handling partial periods

A common issue: comparing January 2026 (partial month, 15 days in) to January 2025 (full month). The comparison is unfair because the current period is incomplete.

**Solution:** filter the prior period to the same number of days:

```dax
YoY Comparable =
VAR LastDateInData = MAX(Sales[OrderDate])
VAR DaysIntoMonth = DATEDIFF(DATE(YEAR(LastDateInData), MONTH(LastDateInData), 1), LastDateInData, DAY) + 1
VAR Current =
    CALCULATE(
        [Total Revenue],
        DATESMTD(Date[Date])
    )
VAR PriorYearComparable =
    CALCULATE(
        [Total Revenue],
        DATEADD(Date[Date], -1, YEAR),
        FILTER(
            ALL(Date[Date]),
            DAY(Date[Date]) <= DaysIntoMonth
        )
    )
RETURN
    DIVIDE(Current - PriorYearComparable, PriorYearComparable, 0)
```

This ensures both periods have the same number of days, making the comparison fair.

## Common mistakes

**Mistake 1: Dividing by zero.** If the prior period had no revenue (new product, new region), `DIVIDE` without a fallback returns infinity. Always use `DIVIDE(numerator, denominator, 0)` to return 0 instead.

**Mistake 2: Comparing different period lengths.** February vs. January compares 28 days to 31. Either compare full months (accept the difference) or use daily averages.

**Mistake 3: Forgetting that `SAMEPERIODLASTYEAR` respects the current filter context.** If a slicer filters to Q1 2026, `SAMEPERIODLASTYEAR` returns Q1 2025 — not the full year. This is usually what you want, but be aware.

**Mistake 4: Using date functions on non-date tables.** Time intelligence functions only work with the date table marked as a date table. Using `Sales[OrderDate]` directly may produce errors or wrong results.

## Summary

`SAMEPERIODLASTYEAR` is the simplest YoY function; `DATEADD` is the flexible general-purpose shifter. Use `DATESYTD` with a year-end parameter for fiscal calendars. For custom comparisons, use explicit date filters with variables. Handle partial periods by filtering the prior period to the same number of days. And always guard against division by zero with `DIVIDE(numerator, denominator, 0)`.
