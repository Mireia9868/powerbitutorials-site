---
title: "Time Intelligence in DAX: YTD, YoY, and Rolling Patterns That Work"
description: "Time intelligence is 80% of business reporting. Learn the calendar table setup, YTD/QTD/MTD functions, year-over-year comparison, and the rolling-average pattern every analyst needs."
pubDate: 2026-07-06
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["dax", "time-intelligence", "ytd", "yoy", "calendar-table"]
author: "DAX Guide Editorial Team"
featured: false
---

"How are we doing versus last year?" is the question behind most Power BI reports. Time intelligence in DAX answers it — but only if your data model is set up correctly. This guide covers the setup and the five patterns that cover 95% of date-based reporting.

## The non-negotiable: a proper calendar table

Time intelligence functions will silently return wrong results — or blank — if you don't have a dedicated date table. The requirements:

1. **One row per day**, no gaps, covering the full date range of your fact data (and ideally a buffer on both ends).
2. **A `Date` column** of type `Date` (not `DateTime`, not text).
3. **Marked as a date table** — in Power BI Desktop, select the table → Table Tools → Mark as Date Table → choose the Date column.
4. **A relationship** from `Date[Date]` to your fact table's date column (one-to-many, single direction).

You can generate this table in Power Query or DAX. The DAX approach is fastest to prototype:

```dax
Date = 
VAR _Start = DATE(2020, 1, 1)
VAR _End = DATE(2026, 12, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(_Start, _End),
    "Year", YEAR([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "YearQuarter", FORMAT([Date], "YYYY") & " Q" & FORMAT([Date], "Q"),
    "Month", FORMAT([Date], "MMMM"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "MonthKey", YEAR([Date]) * 100 + MONTH([Date]),
    "Weekday", FORMAT([Date], "dddd"),
    "IsWeekend", WEEKDAY([Date], 2) > 5
)
```

> If your fiscal year doesn't start January 1, add a `FiscalYear` and `FiscalQuarter` column. Most time intelligence functions accept a fiscal year-end date as the optional third argument.

## Pattern 1: Year-to-date (YTD)

```dax
Revenue YTD =
TOTALYTD(
    [Total Revenue],
    Date[Date]
)
```

`TOTALYTD` accumulates from January 1 of the current year through the latest date in the current filter context. Pair it with a month-level visual and you'll see the running total reset each January.

Quarter-to-date and month-to-date work identically:

```dax
Revenue QTD = TOTALQTD([Total Revenue], Date[Date])
Revenue MTD = TOTALMTD([Total Revenue], Date[Date])
```

## Pattern 2: Year-over-year (YoY)

Two equivalent approaches — pick whichever reads clearer to you:

```dax
// Approach 1: SAMEPERIODLASTYEAR
Revenue LY =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(Date[Date])
)

// Approach 2: DATEADD
Revenue LY =
CALCULATE(
    [Total Revenue],
    DATEADD(Date[Date], -1, YEAR)
)
```

Then compute the growth rate:

```dax
YoY Growth % =
VAR _Current = [Total Revenue]
VAR _Prior = [Revenue LY]
RETURN
DIVIDE(_Current - _Prior, _Prior)
```

Using variables (`VAR`) makes the formula readable and is slightly faster — the engine evaluates each variable once.

## Pattern 3: Rolling 12-month average

```dax
Revenue Rolling 12M =
CALCULATE(
    AVERAGEX(
        DATESINPERIOD(
            Date[Date],
            MAX(Date[Date]),
            -12,
            MONTH
        ),
        [Total Revenue]
    )
)
```

Breaking this down:
- `MAX(Date[Date])` gets the last date visible in the current filter context.
- `DATESINPERIOD` returns a 12-month window ending at that date.
- `AVERAGEX` iterates over each day in that window and averages the revenue.

> A common mistake is using `DATESINPERIOD` inside `CALCULATE` directly without the iterator. That returns the **sum**, not the average — because `CALCULATE` applies the date range as a filter to the existing measure.

## Pattern 4: Same period last year, year-to-date

Combine the two — show last year's YTD figure next to this year's, so February 2026 compares to February 2025's YTD (not the full year 2025):

```dax
Revenue YTD LY =
CALCULATE(
    [Revenue YTD],
    SAMEPERIODLASTYEAR(Date[Date])
)
```

This is the pattern executives actually want. "How does our YTD through March compare to the same period last year?" — answered by one formula.

## Pattern 5: Moving annual total (MAT)

The sum of the trailing 12 months, used to smooth out seasonality:

```dax
Revenue MAT =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(
        Date[Date],
        MAX(Date[Date]),
        -1,
        YEAR
    )
)
```

Distinct from the rolling 12-month *average* — MAT sums; rolling 12M averages. Choose based on the question you're answering.

## The five most common time intelligence mistakes

1. **Forgetting to mark the date table.** Time intelligence functions return blank or wrong numbers silently. Always verify the table is marked.
2. **Using `Date[Date]` from the fact table instead of the calendar table.** Time intelligence requires the *calendar* table's date column.
3. **Mixing `TOTALYTD` with manual date filters.** `TOTALYTD` respects the current filter context, so a slicer on `Date[Month] = "February"` returns only February YTD — which is just February. Use `ALL(Date)` as the third argument if you want YTD to ignore the month slicer.
4. **Comparing partial periods to full periods.** "Revenue LY" for November 2025 returns November 2024 — correct. But "Revenue LY YTD" through November 2025 should return Jan–Nov 2024, not all of 2024. Pattern 4 above handles this.
5. **Assuming `SAMEPERIODLASTYEAR` works without a calendar table.** It needs a contiguous date range. Gaps in the calendar produce blank rows.

## Reference: time intelligence function cheat sheet

| Function | Returns | Typical use |
|----------|---------|-------------|
| `TOTALYTD` | Cumulative YTD value | Annual running totals |
| `SAMEPERIODLASTYEAR` | Date shifted -1 year | YoY comparison |
| `DATEADD` | Date shifted by N intervals | Flexible period shifts (quarters, months) |
| `DATESINPERIOD` | Rolling window | Rolling averages, MAT |
| `PARALLELPERIOD` | Equivalent prior period | QoQ, MoM comparisons |
| `DATESMTD` / `DATESQTD` / `DATESYTD` | Date table for MTD/QTD/YTD | Custom time calcs |

## What's next

With these five patterns you can answer nearly every "vs. last year" question. The remaining 5% — fiscal calendars, 4-4-5 retail calendars, week-based time intelligence — requires custom date tables and the `DATEADD` approach rather than built-in functions. We'll cover those in the advanced guide.

Pair these time intelligence measures with a well-designed star schema (see [Star Schema Data Modeling](/tutorials/data-modeling-star-schema)) and your reports will be both fast and easy to maintain.
