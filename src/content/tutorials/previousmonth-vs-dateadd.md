---
title: "PREVIOUSMONTH vs DATEADD in DAX: Why They Disagree on the 31st"
description: "Both look like 'last month' but return different date sets on the 31st. When each is correct, and how to check which one your model needs."
pubDate: 2026-10-26
category: time-intelligence
tags: ["time-intelligence", "dax", "dateadd", "previousmonth", "month-over-month"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

On the 31st of any month, `PREVIOUSMONTH` and `DATEADD ( 'Date'[Date], -1, MONTH )`
return different numbers. Both read like "last month". Both are usually described
that way in tutorials. One of them is wrong for whatever you are building, and
nothing in the model tells you which.

The difference is not a rounding quirk or a leap-year edge case. It is a
difference in what the functions return: one gives you a month, the other shifts
your date set.

## What each function actually returns

`PREVIOUSMONTH` returns every date in the previous calendar month, regardless of
which day is currently in filter context.

`DATEADD` shifts whatever dates are in filter context by the given interval. One
day in, one day out. On 31 March, it returns 28 February — because there is no 29,
30 or 31 in that month.

```dax
-- Filtered to 31 March 2026

-- All 28 days of February
CALCULATE ( [Total Sales], PREVIOUSMONTH ( 'Date'[Date] ) )

-- 28 February only
CALCULATE ( [Total Sales], DATEADD ( 'Date'[Date], -1, MONTH ) )
```

On the 15th of the month, the two agree. On the 30th or 31st, they diverge by
however many days the previous month is short. In March that is three days out of
thirty-one — the number is about 10% too high.

That is the whole bug. It is not subtle once you see it; it is invisible when you
don't.

## A comparison that holds up

| Situation | `PREVIOUSMONTH` | `DATEADD ( -1, MONTH )` |
|---|---|---|
| Filtered to 15 March | 1–28 February | 15 February |
| Filtered to 31 March | 1–28 February | 28 February |
| Filtered to 31 May | 1–30 April | 30 April |
| Filtered to whole month of March | 1–28 February | 1–28 February |
| Filtered to a year | Previous year's same months | Previous year, shifted |

The last two rows are why this stays hidden. When the visual is filtered to a whole
month, both functions return the same thing and the measures look fine. The bug only
appears when a single date is in context — a card showing "today", a daily snapshot,
a drill-through target page.

Microsoft documents the behaviour on the
[PREVIOUSMONTH reference](https://learn.microsoft.com/en-us/dax/previousmonth-function-dax)
and the [DATEADD reference](https://learn.microsoft.com/en-us/dax/dateadd-function-dax);
neither page frames them as interchangeable, but most tutorials do.

## Choosing between them

Work backwards from what the consumer of the number expects.

**Month-over-month totals → `PREVIOUSMONTH`.** A monthly total compares month to
month. February is twenty-eight days; that is the comparison the business asked
for. Using `DATEADD` here means March is compared against three weeks of February,
which flatters March every year.

**"Same day last month" → `DATEADD`.** If the card says "revenue on the 31st vs the
same day last month", the reader expects a single day, not a month. `DATEADD`
gives that.

**Rolling windows → neither, use `DATESINPERIOD`.** A 30-day rolling sum should not
care where month boundaries fall. Reaching for month functions to build a rolling
window is a different bug that produces plausible-looking charts.

**Fiscal months → `PREVIOUSMONTH` will not help you.** It is calendar-based. If
your periods don't align to the calendar month, build the window explicitly with
`FILTER` and `DATESBETWEEN`, or use a period table. This is the same class of
problem as the `TOTALYTD` fiscal-year trap: the function name promises something
more general than what it does.

## Check your own model in thirty seconds

Before trusting any month-over-month measure, find out how far apart the two
functions are on your data:

```dax
MoM Drift =
VAR PriorMonthAll =
    CALCULATE ( [Total Sales], PREVIOUSMONTH ( 'Date'[Date] ) )
VAR PriorDayShift =
    CALCULATE ( [Total Sales], DATEADD ( 'Date'[Date], -1, MONTH ) )
RETURN
    PriorMonthAll - PriorDayShift
```

Put it in a card and filter to 31 March.

- **Zero** means your fact table only holds month-end rows, so the two are
  equivalent. This is common with monthly snapshots — and it is why the bug
  survives in some models for years. Nothing is broken; the check simply cannot
  see it.
- **Non-zero** means the number on screen is exactly how much your existing
  month-over-month measure is off, if it uses the wrong one.

Run it once, and either fix the measure or note that your data makes it moot. Both
are acceptable answers. Continuing not to know is the one that isn't.

## Common mistakes beyond the 31st

**Assuming `DATEADD` needs a row context.** It does not. It operates on the date
column in filter context, which is why it works inside `CALCULATE` without any
iteration.

**Using `PREVIOUSMONTH` inside a measure that filters a specific date.** If the
visual has one date selected, `PREVIOUSMONTH` returns the whole previous month and
the measure silently inflates. This is the exact mechanism of the bug above.

**Confusing "previous month" with "month to date last month".** The second one is
`CALCULATE ( [Total Sales], DATESMTD ( PREVIOUSMONTH ( 'Date'[Date] ) ) )` — a
different question with a different answer.

## FAQ

### Q: Does DATEADD handle months of different lengths correctly?

Yes, in the sense that it clamps rather than errors. 31 March shifted back one month
becomes 28 February (or 29 in a leap year). It never returns a date that doesn't
exist. Whether that is what you want depends on the question — see the table above.

### Q: Which one should I use for a year-over-year comparison?

Neither. Year-over-year usually means `SAMEPERIODLASTYEAR`, which is a date-set
shift of exactly one year and handles 29 February by returning blank. If you need
"same period last year plus a custom offset", `DATEADD ( -1, YEAR )` is the
explicit version.

### Q: Why does PREVIOUSMONTH return blank in January?

It shouldn't, as long as your date table starts before the earliest fact. A blank in
January almost always means the date table does not have the previous December. This
is the same root cause as missing time intelligence across the board — the calendar
table is too short or not marked.

### Q: Can I use these with a fiscal calendar?

Not reliably. Both are calendar-based. For a July-to-June fiscal year, build the
comparison window explicitly against your date table's fiscal columns rather than
relying on the function name.

## Related Reading

- [Time Intelligence: The Complete Setup](/tutorials/time-intelligence/)
- [The Date Table Every Model Needs](/tutorials/power-bi-date-table/)
- [TIME INTELLIGENCE: YTD, QTD and MTD with TOTALYTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [SAMEPERIODLASTYEAR: Comparison Patterns](/tutorials/sameperiodlastyear-comparison-patterns/)
- [Rolling Averages and Moving Sums in DAX](/tutorials/rolling-averages-moving-sums-dax/)
- [MoM and YoY DAX Template](/tutorials/power-bi-mom-yoy-dax-template/)
- [CALCULATE: The Function Everything Runs Through](/tutorials/calculate-function/)
