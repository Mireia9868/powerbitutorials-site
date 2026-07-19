---
title: "Calculated Tables and What-If Parameters in Power BI: Dynamic Modeling Tools"
description: "Calculated tables let you build tables with DAX instead of loading them from a source. What-if parameters turn static assumptions into interactive slicers. This guide covers both features, the syntax, and five practical patterns — from date tables to scenario analysis."
pubDate: 2026-07-16
category: "data-modeling"
difficulty: "Intermediate"
tags: ["data-modeling", "calculated-tables", "what-if-parameters", "dax", "scenario-analysis"]
author: "Power BI Tutorials Team"
featured: false
---

Some tables in a Power BI model don't need to come from a data source. Date tables, scenario tables, and parameter tables can all be generated with DAX — giving you full control over their structure and letting them respond to model changes automatically. This guide covers calculated tables and what-if parameters, the two DAX-generated table types every analyst should know.

## Calculated tables: the basics

A calculated table is created with a DAX expression that returns a table. In Power BI Desktop: **Modeling → New Table**.

```dax
Date = 
ADDCOLUMNS(
    CALENDAR(DATE(2020, 1, 1), DATE(2026, 12, 31)),
    "Year", YEAR([Date]),
    "Month", FORMAT([Date], "MMMM"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "Weekday", FORMAT([Date], "dddd"),
    "IsWeekend", WEEKDAY([Date], 2) > 5
)
```

The result is a table that lives in your model like any other. It refreshes when the dataset refreshes, and it can participate in relationships, be used in visuals, and serve as a filter.

## When to use calculated tables

### Pattern 1: Date tables

The most common calculated table. A DAX-generated date table guarantees a complete, gap-free date range and the columns you need for time intelligence.

```dax
Date = 
VAR _Start = DATE(YEAR(MIN(Sales[OrderDate])) - 1, 1, 1)
VAR _End = DATE(YEAR(MAX(Sales[OrderDate])) + 1, 12, 31)
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

**Tip:** use `MIN` and `MAX` of your fact table's date column to make the date table span exactly the range you need — plus a buffer year on each end for time intelligence functions.

### Pattern 2: Disconnected tables for filtering

Sometimes you want a table that provides filter values without being connected to your fact table via a relationship. A classic example: a "rolling period" selector.

```dax
Period Selector = 
DATATABLE(
    "Label", STRING,
    "Value", INTEGER,
    {
        {"Last 7 days", 7},
        {"Last 30 days", 30},
        {"Last 90 days", 90},
        {"Last 12 months", 365}
    }
)
```

This table is disconnected (no relationship). A measure reads the selected value with `SELECTEDVALUE` and applies the filter:

```dax
Rolling Revenue =
VAR Days = SELECTEDVALUE('Period Selector'[Value], 30)
RETURN
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(Date[Date], MAX(Date[Date]), -Days, DAY)
)
```

### Pattern 3: Role-playing dimensions

If you need `OrderDate` and `ShipDate` from the same date table, create a calculated table for the second role:

```dax
ShipDate = 'Date'
```

This creates a copy of the date table. Relate it to `Sales[ShipDate]` and use `USERELATIONSHIP` in DAX to activate it when needed.

### Pattern 4: Aggregated summary tables

For reports that need pre-aggregated data (e.g., monthly summary for performance), a calculated table can summarize the fact table:

```dax
MonthlySummary = 
SUMMARIZECOLUMNS(
    Date[YearMonth],
    "Revenue", [Total Revenue],
    "Orders", [Order Count],
    "AvgOrderValue", DIVIDE([Total Revenue], [Order Count], 0)
)
```

**Caution:** aggregated tables don't update dynamically with slicer selections — they're computed at refresh time. Use them for static summaries, not interactive reporting.

## What-if parameters

A what-if parameter is a calculated table with a slicer that lets users explore scenarios. **Modeling → What-If → New Parameter**.

When you create one, Power BI generates:
1. A calculated table with a range of values (e.g., 0% to 50% discount in 1% increments)
2. A slicer on the page
3. A DAX measure that reads the selected value

```dax
DiscountRate = GENERATESERIES(0, 0.5, 0.01)
DiscountRate Value = SELECTEDVALUE('DiscountRate'[DiscountRate], 0)
```

### Pattern: Scenario analysis

You want users to see how revenue changes with different discount rates.

```dax
Projected Revenue =
VAR Rate = [DiscountRate Value]
RETURN
    SUMX(
        Sales,
        Sales[Revenue] * (1 - Rate)
    )
```

Drop the `Projected Revenue` measure into a card visual. As users move the slicer, the card updates instantly.

### Pattern: Sensitivity analysis

What-if parameters can drive multi-scenario comparisons. Create two parameters — `OptimisticGrowth` and `PessimisticGrowth` — and a measure that shows the range:

```dax
Revenue Range =
VAR Current = [Total Revenue]
VAR Optimistic = Current * (1 + [OptimisticGrowth Value])
VAR Pessimistic = Current * (1 - [PessimisticGrowth Value])
RETURN
"Range: " & FORMAT(Pessimistic, "$#,##0") & " - " & FORMAT(Optimistic, "$#,##0")
```

## Common mistakes

**Mistake 1: Calculated tables that should be Power Query tables.** If the table comes from a source or requires complex transformations, build it in Power Query. Calculated tables are for DAX-generated structures — date tables, parameter tables, disconnected tables.

**Mistake 2: Calculated tables that don't refresh.** A calculated table with hardcoded date ranges won't extend when new data arrives. Use `MIN`/`MAX` of fact columns to make the range dynamic.

**Mistake 3: Overusing what-if parameters.** They're powerful for scenario analysis but add slicer clutter. Use them when interactivity adds genuine value — not for values that could be hardcoded.

## Performance note

Calculated tables are computed at refresh time, not at query time. This means:

- They don't slow down report interactions (the computation happens once).
- They do increase refresh time and model size.
- For large tables (millions of rows), prefer Power Query — it's more efficient for bulk data operations.

## Summary

Calculated tables are DAX-generated structures that live in your model. Use them for date tables, disconnected filter tables, role-playing dimensions, and pre-aggregated summaries. What-if parameters are a specialized calculated table that drives scenario analysis via slicers. Both refresh when the dataset refreshes — keep their ranges dynamic with `MIN`/`MAX` to avoid stale data.
