---
title: "Rolling Averages and Moving Sums in DAX: Smooth Out the Noise"
description: "Daily data is noisy — a slow Tuesday followed by a spike Wednesday. Rolling averages and moving sums reveal the trend underneath. This guide covers the 7-day rolling average, the 30-day moving sum, and the pattern for any custom rolling window using DAX window functions."
pubDate: 2026-07-19
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["dax", "rolling-average", "moving-sum", "window-functions", "time-intelligence"]
author: "Power BI Tutorials Team"
featured: false
---

Daily metrics fluctuate. A B2B sales team closes no deals on weekends; a retail site spikes on Black Friday. If you plot daily revenue, the noise obscures the trend. Rolling averages smooth it out. This guide covers the three rolling patterns every analyst needs: the moving average, the moving sum, and the cumulative total.

## Prerequisites

All rolling calculations require a proper date table, marked as a date table, with a relationship to your fact table. If you don't have one, stop and set that up first — see our [time intelligence fundamentals guide](/tutorials/time-intelligence) for the setup.

## Pattern 1: The 7-day rolling average

A 7-day rolling average at each date = the average of revenue for that date and the previous 6 days.

```dax
7-Day Rolling Avg Revenue =
CALCULATE(
    AVERAGEX(VALUES(Date[Date]), [Total Revenue]),
    DATESINPERIOD(Date[Date], MAX(Date[Date]), -7, DAY)
)
```

**How it works:**
- `DATESINPERIOD` returns a table of dates: the current date plus the previous 6 (7 days total).
- `CALCULATE` evaluates `[Total Revenue]` over that date range.
- `AVERAGEX(VALUES(Date[Date]), ...)` averages the per-day revenue across the 7 days.

**Important:** `AVERAGEX(VALUES(Date[Date]), [Total Revenue])` computes the average of daily revenues, not the total divided by 7. This matters when some days have no sales — `AVERAGEX` skips blanks, while `DIVIDE(total, 7)` would dilute the average.

## Pattern 2: The 30-day moving sum

A moving sum is the same idea, but summed instead of averaged.

```dax
30-Day Moving Sum =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(Date[Date], MAX(Date[Date]), -30, DAY)
)
```

This returns the total revenue for the last 30 days ending at the current date. Useful for:
- "Last 30 days" KPI cards
- Comparing a rolling 30-day window to the previous 30-day window
- Smoothing daily data for trend lines

## Pattern 3: Cumulative total (running total)

A running total accumulates from the start of the period to the current date.

```dax
YTD Revenue =
CALCULATE(
    [Total Revenue],
    DATESYTD(Date[Date])
)
```

`DATESYTD` returns all dates from the start of the year to the current date. The result is a running total that resets at the start of each year.

**Custom year-end:** if your fiscal year ends in June, pass the year-end date:

```dax
Fiscal YTD Revenue =
CALCULATE(
    [Total Revenue],
    DATESYTD(Date[Date], "06-30")
)
```

## Pattern 4: Custom rolling window with WINDOW

For windows that don't fit the standard patterns (e.g., a 14-day window centered on the current date), use the `WINDOW` function (DAX 2022+).

```dax
Centered 7-Day Avg =
CALCULATE(
    AVERAGEX(VALUES(Date[Date]), [Total Revenue]),
    WINDOW(-3, REL, 3, REL, ALL(Date[Date])
)
```

`WINDOW(-3, REL, 3, REL, ...)` returns a window from 3 rows before to 3 rows after the current row in the `Date` table — a centered 7-day window.

**When to use `WINDOW` vs `DATESINPERIOD`:**
- `DATESINPERIOD` is simpler for "last N days" patterns.
- `WINDOW` handles centered windows, asymmetric windows, and non-date hierarchies (e.g., a rolling 5 products by rank).

## Pattern 5: Rolling average by month (not day)

Sometimes you want a 3-month rolling average — the average of the current month and the previous 2 months.

```dax
3-Month Rolling Avg =
CALCULATE(
    AVERAGEX(VALUES(Date[YearMonth]), [Total Revenue]),
    DATESINPERIOD(Date[Date], MAX(Date[Date]), -3, MONTH)
)
```

The key: `AVERAGEX(VALUES(Date[YearMonth]), ...)` averages over months, not days. `DATESINPERIOD` with `MONTH` as the interval returns a 3-month date range.

## Visualizing rolling calculations

Rolling averages shine in line charts. Plot:
- **Daily revenue** (jagged line)
- **7-day rolling average** (smoothed line)

The contrast makes the trend visible. Use a secondary axis or a small-multiples layout to compare rolling averages across categories.

## Common mistakes

**Mistake 1: Using `CALCULATE` with the wrong date column.** The date column in `DATESINPERIOD` must be from your date table, not the fact table. If you use `Sales[OrderDate]`, the calculation may work but won't respect the date table's relationships.

**Mistake 2: Forgetting that rolling windows at the start of the data are incomplete.** The 7-day rolling average on the first day of your data is just that day's value — there's no previous data. Either:
- Accept this (the average will ramp up over the first 6 days).
- Filter the visual to start 7 days after the data begins.

**Mistake 3: Mixing rolling windows inappropriately.** A 7-day rolling average and a 30-day rolling average tell different stories. Don't put both on the same chart without clear labeling — users will confuse the two.

**Mistake 4: Using `AVERAGE` instead of `AVERAGEX`.** `AVERAGE(Sales[Revenue])` averages the column. `AVERAGEX(VALUES(Date[Date]), [Total Revenue])` averages the daily totals. These are different when some days have multiple transactions or no transactions.

## Performance note

Rolling calculations over large date ranges can be slow because they re-evaluate the measure for each date in the window. To optimize:

- Use `DATESINPERIOD` (optimized) instead of `FILTER` with date comparisons.
- Avoid nested iterators in rolling measures.
- Pre-aggregate daily data in Power Query if the fact table is very large.

## Summary

Rolling averages smooth daily noise; moving sums provide a rolling window total; cumulative totals accumulate from period start. Use `DATESINPERIOD` for "last N days/months" patterns and `WINDOW` for centered or asymmetric windows. Average over `VALUES(Date[Date])` to get the per-day average, not the total divided by N. And always use a proper date table — without one, all time intelligence functions return wrong results silently.
