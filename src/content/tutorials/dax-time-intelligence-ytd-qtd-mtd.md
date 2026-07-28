---
title: "DAX Time Intelligence: YTD, QTD, and MTD Complete Guide"
description: "Time intelligence is one of the most common — and most error-prone — areas of DAX. This guide covers TOTALYTD, TOTALQTD, TOTALMTD, DATEADD, and SAMEPERIODLASTYEAR, the calendar table requirements that make them work, and the five mistakes that produce wrong year-to-date numbers."
pubDate: 2026-07-28
category: "time-intelligence"
difficulty: "Intermediate"
tags: ["time-intelligence", "dax", "ytd", "dateadd", "calendar"]
author: "Power BI Tutorials Team"
---

# DAX Time Intelligence: YTD, QTD, and MTD Complete Guide

Year-to-date, quarter-to-date, month-to-date, and year-over-year comparisons are the bread and butter of business reporting. Yet they're also among the most frequently broken DAX calculations — not because the functions are complex, but because the prerequisites (a proper Date table) are often missing or misconfigured.

This guide covers the five core time intelligence functions, the Date table requirements, and the mistakes that produce silently wrong numbers.

## The Prerequisite: A Proper Date Table

Every time intelligence function in DAX has one non-negotiable requirement: **a marked Date table with a contiguous range of dates**. If this is missing, your YTD calculations will return blank, wrong, or inconsistent results.

### What "Marked" Means

In Power BI Desktop: select your Date table → Table Tools → Mark as Date Table → select the date column. This tells the engine that the column is a proper date column and enables time intelligence functions.

### What a Proper Date Table Looks Like

```dax
Date =
VAR StartDate = DATE(2020, 1, 1)
VAR EndDate = DATE(2026, 12, 31)
RETURN
    ADDCOLUMNS(
        CALENDAR(StartDate, EndDate),
        "Year", YEAR([Date]),
        "YearLabel", "FY" & YEAR([Date]),
        "Quarter", "Q" & FORMAT([Date], "Q"),
        "QuarterNum", FORMAT([Date], "Q"),
        "Month", FORMAT([Date], "MM"),
        "MonthName", FORMAT([Date], "MMMM"),
        "MonthShort", FORMAT([Date], "MMM"),
        "DayOfWeek", FORMAT([Date], "dddd"),
        "DayOfWeekNum", WEEKDAY([Date], 2),
        "IsWorkday", WEEKDAY([Date], 2) <= 5,
        "FiscalYear",
            VAR M = MONTH([Date])
            RETURN IF(M >= 7, YEAR([Date]) + 1, YEAR([Date])),
        "FiscalQuarter",
            VAR M = MONTH([Date])
            RETURN "Q" & FORMAT(IF(M >= 7, M - 6, M + 6), "0")
    )
```

**Critical requirements**:
- The date column must be of type `Date` (not text, not datetime)
- The range must be **contiguous** — no missing dates
- The table must be **marked** as a date table
- The table must have a **relationship** to your fact table(s)

If any of these are missing, time intelligence functions will fail silently — returning blanks or incorrect values without any error message.

## The Five Core Functions

### Function 1: TOTALYTD (Year-to-Date)

**Scenario**: Show cumulative sales from January 1 to the current date.

```dax
Sales YTD =
TOTALYTD(
    [Sales Amount],
    'Date'[Date]
)
```

**How it works**: `TOTALYTD` evaluates `[Sales Amount]` for all dates from the start of the year through the **latest date in the current filter context**. If the visual shows March 2024, `TOTALYTD` returns the sum of January + February + March 2024.

**With a fiscal year** (e.g., July–June):

```dax
Sales Fiscal YTD =
TOTALYTD(
    [Sales Amount],
    'Date'[Date],
    "06-30"  // Fiscal year ends June 30
)
```

The third argument tells `TOTALYTD` that the year ends on June 30, so the YTD calculation resets on July 1.

### Function 2: TOTALQTD (Quarter-to-Date)

```dax
Sales QTD =
TOTALQTD(
    [Sales Amount],
    'Date'[Date]
)
```

Returns cumulative sales from the start of the current quarter through the latest date in the filter context. If the visual shows May 2024, `TOTALQTD` returns April + May 2024.

### Function 3: TOTALMTD (Month-to-Date)

```dax
Sales MTD =
TOTALMTD(
    [Sales Amount],
    'Date'[Date]
)
```

Returns cumulative sales from the first day of the current month through the latest date in the filter context. If the visual shows March 15, 2024, `TOTALMTD` returns March 1–15, 2024.

### Function 4: DATEADD (Period Comparison)

**Scenario**: Compare current sales to the same period last year.

```dax
Sales Last Year =
CALCULATE(
    [Sales Amount],
    DATEADD('Date'[Date], -1, YEAR)
)
```

`DATEADD` shifts the date filter by a specified number of intervals. `-1, YEAR` means "same period, one year earlier." If the current context is March 2024, this returns March 2023.

**Other intervals**:
```dax
// Same period, previous quarter
Sales Last Quarter =
CALCULATE([Sales Amount], DATEADD('Date'[Date], -1, QUARTER))

// Same period, previous month
Sales Last Month =
CALCULATE([Sales Amount], DATEADD('Date'[Date], -1, MONTH))
```

### Function 5: SAMEPERIODLASTYEAR (Shortcut)

```dax
Sales Same Period Last Year =
CALCULATE(
    [Sales Amount],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

This is equivalent to `DATEADD('Date'[Date], -1, YEAR)` but more readable. Use it when the intent is specifically "same period, one year back."

## Building YoY Growth (The Real-World Pattern)

Combining these functions into a year-over-year growth measure is the most common time intelligence pattern:

```dax
YoY Growth % =
VAR CurrentSales = [Sales Amount]
VAR PriorYearSales =
    CALCULATE(
        [Sales Amount],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    DIVIDE(
        CurrentSales - PriorYearSales,
        PriorYearSales
    )
```

**Why use variables here**: `PriorYearSales` captures the prior-year value before any further filter modifications. `CurrentSales` captures the current value. Both are snapshots — if you tried to inline them in the `DIVIDE`, you'd be recalculating the same expressions multiple times.

## The Five Mistakes That Produce Wrong Numbers

### Mistake 1: No Marked Date Table

**The problem**: You wrote `TOTALYTD([Sales Amount], 'Date'[Date])` and the result is blank or shows the same value as `[Sales Amount]`.

**The cause**: Your Date table isn't marked. The time intelligence functions can't determine the year boundaries without it.

**The fix**: Select the Date table → Table Tools → Mark as Date Table → select the date column. Also verify that File → Options → Data Load → "Auto date/time" is **unchecked** (you don't want auto-generated date tables interfering with your custom one).

### Mistake 2: Non-Contiguous Date Range

**The problem**: Your YTD calculation resets mid-year or returns unexpected values for certain months.

**The cause**: Your Date table has gaps — missing dates where there were no sales. This commonly happens when you use `DISTINCT(Sales[OrderDate])` to build your Date table instead of `CALENDAR()`.

```dax
// WRONG — creates gaps where there are no sales
Date = DISTINCT(Sales[OrderDate])

// RIGHT — contiguous date range
Date = CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31))
```

Time intelligence functions assume every date in the period exists. If May 15 is missing, `TOTALYTD` might stop at May 14.

### Mistake 3: Using DATEADD Without Understanding Granularity

**The problem**: Your `DATEADD` comparison works for months but returns wrong values for days or quarters.

**The cause**: `DATEADD` shifts the **filter context** on the Date column. If your visual is at the month level, `DATEADD(-1, YEAR)` shifts the entire month filter. If your visual is at the day level, it shifts the day filter. The function works at whatever granularity the current filter context provides.

```dax
// If the visual shows March 2024 → returns March 2023 (correct)
// If the visual shows March 15, 2024 → returns March 15, 2023 (correct)
// If the visual shows Q1 2024 → returns Q1 2023 (correct)
Sales Last Year = CALCULATE([Sales Amount], DATEADD('Date'[Date], -1, YEAR))
```

The function is correct at all granularities — but you need to understand that the granularity is determined by the **visual**, not by the DAX code.

### Mistake 4: Forgetting That TOTALYTD Respects the Filter Context

**The problem**: Your YTD measure shows the full year's total instead of the year-to-date total.

**The cause**: `TOTALYTD` calculates from January 1 through the **latest date in the filter context**. If your visual or slicer includes the full year (e.g., Year = 2024 without a month filter), `TOTALYTD` returns the entire year's total.

**The fix**: Ensure your visual or filter context includes the specific date or month you want the YTD for. If the visual shows a specific month, `TOTALYTD` will correctly accumulate through that month.

```dax
// If visual shows March 2024 → YTD = Jan + Feb + Mar 2024 (correct)
// If visual shows 2024 (full year) → YTD = entire 2024 (also "correct," just not what you wanted)
Sales YTD = TOTALYTD([Sales Amount], 'Date'[Date])
```

### Mistake 5: Mixing Calendar Types

**The problem**: Your fiscal YTD resets in January instead of July, or your standard YTD includes fiscal-year boundary dates incorrectly.

**The cause**: You're using standard YTD functions (`TOTALYTD` without the fiscal year-end parameter) when your business uses a fiscal calendar.

```dax
// WRONG — uses calendar year (Jan–Dec) when business uses fiscal year (Jul–Jun)
Sales YTD Wrong = TOTALYTD([Sales Amount], 'Date'[Date])

// RIGHT — specifies fiscal year-end of June 30
Sales YTD Fiscal = TOTALYTD([Sales Amount], 'Date'[Date], "06-30")
```

The third parameter of `TOTALYTD` accepts a string in `"MM-DD"` format representing the last day of the fiscal year. Common values:
- `"12-31"` — Calendar year (default)
- `"06-30"` — July–June fiscal year
- `"03-31"` — April–March fiscal year (UK/Japan)
- `"09-30"` — October–September fiscal year (US federal government)

## Decision Framework: Which Function to Use

| Need | Function | Example |
|------|----------|---------|
| Cumulative from start of year | `TOTALYTD` | YTD sales through current month |
| Cumulative from start of quarter | `TOTALQTD` | QTD sales through current month |
| Cumulative from start of month | `TOTALMTD` | MTD sales through current day |
| Compare to previous period (any interval) | `DATEADD` | Same month last year, same quarter last year |
| Compare to same period last year (shortcut) | `SAMEPERIODLASTYEAR` | Same month/quarter/year last year |
| Compare to a specific shifted period | `DATEADD` with custom offset | 3 months ago, 2 quarters ago |
| Rolling 12 months | Custom pattern with `DATESINPERIOD` | Trailing 12-month total |

### Rolling 12 Months (Advanced Pattern)

```dax
Rolling 12 Months =
CALCULATE(
    [Sales Amount],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
)
```

`DATESINPERIOD` returns a table of dates going back 12 months from the latest date in the current filter context. This is useful for moving averages and trailing comparisons.

## Frequently Asked Questions

**Q: Do I need to disable Auto Date/Time?**

Yes. Auto Date/Time creates hidden date tables for every date column in your model, which adds model size and conflicts with your custom Date table. Go to File → Options → Data Load → uncheck "Auto date/time" for the current file.

**Q: What happens if my fact table has dates outside the Date table range?**

Those rows will not be included in time intelligence calculations. The relationship between the fact table and Date table only includes dates that exist in the Date table. Extend your Date table to cover the full range of your fact data.

**Q: Can I use time intelligence with DirectQuery?**

Yes, but performance may be significantly slower. Time intelligence functions generate complex SQL queries behind the scenes. For DirectQuery models, consider pre-calculating YTD/QTD/MTD values in your data source (SQL view or stored procedure) and importing them as columns.

**Q: What's the difference between DATESYTD and TOTALYTD?**

`TOTALYTD` is a shortcut that combines `CALCULATE` + `DATESYTD`. These two measures are equivalent:

```dax
// Using TOTALYTD (recommended — cleaner)
Sales YTD = TOTALYTD([Sales Amount], 'Date'[Date])

// Using CALCULATE + DATESYTD (explicit)
Sales YTD = CALCULATE([Sales Amount], DATESYTD('Date'[Date]))
```

Use `TOTALYTD` for readability. Use `DATESYTD` when you need the date table itself (e.g., inside a more complex `CALCULATE` with additional filters).

**Q: How do I handle 4-4-5 fiscal calendars?**

Standard time intelligence functions assume calendar months. For 4-4-5 fiscal calendars (used in retail), you need custom DAX patterns. Create a custom `FiscalPeriod` column in your Date table and write measures that calculate cumulative totals based on the fiscal period number rather than calendar dates.

## What's Next

Time intelligence pairs naturally with these advanced topics:

- [DAX CALCULATE: The Function That Controls Everything](/tutorials/dax-calculate-function/) — Every time intelligence function uses `CALCULATE` internally
- [DAX Variables: Write Cleaner and Faster Measures](/tutorials/dax-variables-guide/) — Variables make time intelligence measures like YoY Growth readable
- [Power BI Star Schema: The Data Model That Scales](/tutorials/power-bi-star-schema/) — A proper Date table is the centerpiece of a star schema
- [DAX SWITCH: Cleaner Conditional Logic](/tutorials/dax-switch-function/) — Build dynamic measure selectors for YTD/QTD/MTD switching
