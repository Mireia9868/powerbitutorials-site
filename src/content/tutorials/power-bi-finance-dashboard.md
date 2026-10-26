---
title: "Build a Finance Dashboard in Power BI"
description: "Finance reporting has a shape that generic dashboards ignore."
pubDate: 2026-10-05
category: visualization
tags: ["dashboard", "finance"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What a Finance Dashboard Actually Needs

Finance reporting has a shape that generic dashboards ignore. The audience wants four things at once: how much came in, how much went out, what is left, and whether that result is on track versus a plan. Every finance page you build is a variation on that theme, sliced by period, cost center, department, or legal entity.

This tutorial builds a working finance dashboard in Power BI from a star-schema model. You get a P&L summary card set, a revenue versus budget variance chart, a monthly trend with a forecast, a cost breakdown, and drill-through to transaction detail. The DAX uses time intelligence and budget measures that behave correctly under filter context.

You should already be comfortable with basic measures and relationships. Everything else is built step by step.

## Step 1: Model the Data Correctly

Before any visual, get the model right. A finance dashboard fails fast if the grain is wrong or the budget table is joined incorrectly.

Use this structure:

| Table | Grain | Role |
|---|---|---|
| FactGL | One row per journal line | Actuals |
| FactBudget | One row per account/period | Budget |
| DimAccount | One row per GL account | Account hierarchy |
| DimDate | One row per calendar day | Marked date table |
| DimCostCenter | One row per cost center | Slicer dimension |

Two rules matter here:

- Do not merge actuals and budget into one table with a "Scenario" column unless you also carry distinct amount columns. Keeping them separate keeps measures simpler and lets each table use a single-direction relationship to `DimDate`.
- Never relate `FactBudget` to `DimCostCenter` on a many-to-many basis. Add a bridge table or keep budget at the cost-center grain it is genuinely stored at.

Mark `DimDate` as the date table (Table tools > Mark as date table) and create standard relationships to both fact tables. Filter direction stays single from dimensions to facts.

## Step 2: Base Measures with DIVIDE and Variables

Start with the primitives every other measure references.

```dax
Total Revenue =
CALCULATE(
    [Total Amount],
    DimAccount[AccountType] = "Revenue"
)

Total Cost =
CALCULATE(
    [Total Amount],
    DimAccount[AccountType] IN { "COGS", "OpEx" }
)

Gross Margin =
VAR Revenue = [Total Revenue]
VAR Cost = [Total Cost]
RETURN
    DIVIDE(Revenue - Cost, Revenue)
```

`DIVIDE` handles the zero-revenue month without throwing an error. Variables compute Revenue and Cost once, which matters when the same expression appears more than once. The `IN` operator reads better than chained `OR` conditions and optimizes the same way.

Note the sign convention. If your GL stores expenses as positive numbers, `Gross Margin` as written gives the right answer. If expenses are stored negative, drop the subtraction and use `Revenue + Cost`. Decide the convention once and document it, because every measure downstream depends on it.

## Step 3: Budget vs Actual Variance

Budgets live in their own fact table, so you need a measure that reads it without inheriting the actuals filter.

```dax
Total Budget =
SUM( FactBudget[BudgetAmount] )

Variance vs Budget =
[Total Revenue] - [Total Budget]

Variance % =
DIVIDE( [Variance vs Budget], [Total Budget] )

Budget Status =
VAR VarPct = [Variance %]
RETURN
    SWITCH(
        TRUE(),
        VarPct >= 0,    "On Track",
        VarPct > -0.05, "Watch",
        "Off Track"
    )
```

`Budget Status` returns text, so it works in a card, a table column, or as the input to conditional formatting rules. A `SWITCH(TRUE(), ...)` pattern evaluates top to bottom and stops at the first true condition, so order the thresholds from best to worst.

## Step 4: Add Time Intelligence

The trend visuals need YTD and prior-year comparisons. These require a marked date table and a contiguous date column.

```dax
Revenue YTD =
TOTALYTD( [Total Revenue], DimDate[Date] )

Revenue PY =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR( DimDate[Date] )
)

Revenue YoY % =
DIVIDE(
    [Total Revenue] - [Revenue PY],
    [Revenue PY]
)
```

If `Revenue YTD` returns a value only for the last day of the period, your date table is not marked or the relationship is missing. Time intelligence functions do not work against a date column in the fact table.

Budget comparisons usually want YTD too. Use `TOTALYTD([Total Budget], DimDate[Date])` with the same pattern. If your fiscal year does not start in January, add a fiscal year and fiscal period column to `DimDate` during Power Query and pass the fiscal year-end date as the third argument to `TOTALYTD`.

## Step 5: Lay Out the Page

Build the page in this order, top to bottom.

**Row 1: KPI strip.** Four or five cards: Total Revenue, Total Cost, Gross Margin %, Revenue YTD, Variance vs Budget. Keep them on one line so the eye reads them as a single status bar.

**Row 2: Trend and variance.** A line chart of Revenue versus Budget by month, and a column chart of Variance % by month. Color the variance columns by sign using a rule so negative months read red immediately.

**Row 3: Composition.** A bar chart of Cost by AccountType or by CostCenter, sorted descending. Add a treemap if you want the account hierarchy visible without drilling.

**Row 4: Detail table.** A matrix with Account rows, months as columns, and conditional formatting on the variance.

Use slicers for Fiscal Year and Cost Center in a left or top panel. Sync them across every page from the View menu so navigation does not reset the context.

## Step 6: Conditional Formatting for Finance Signals

Finance readers scan for exceptions. Formatting should encode one meaning only.

For the variance column chart, set a data color rule where values below zero are red and values at or above zero are green. On the matrix, apply background color formatting driven by a measure so that rows meaningfully under budget are highlighted.

Do not color every metric. Pick the two or three where a threshold genuinely changes a decision: variance to budget, margin percentage, and maybe days sales outstanding. Coloring everything makes nothing stand out.

## Step 7: Drill-Through to Transactions

Executives will ask "why is marketing overspent in March." Give them the answer in two clicks.

Create a drill-through page with `DimAccount[AccountName]` and `DimDate[Month]` as drill fields. Put a table of `FactGL` rows on it: date, vendor, description, amount. Add a card showing the filtered total so the reader can confirm the number matches what they clicked.

On the drill-through page, add a back button from Insert > Buttons so navigation does not depend on right-click.

## Step 8: Performance and Refresh

Three habits keep a finance report responsive:

1. Use variables in any measure that references another measure more than once. The engine caches the variable result within the evaluation.
2. Avoid `FILTER` over large fact tables when a simple column predicate in `CALCULATE` will do.
3. In Import mode, drop unused columns during Power Query. A GL table with thirty columns where you need eight wastes memory and slows refresh.

If you build against a live warehouse, weigh the trade-off between DirectQuery freshness and Import speed before you commit to either.

## FAQ

### Q: Why does my YTD measure return a blank for most dates?

`TOTALYTD` accumulates to the end of the period you are evaluating. If you place it next to `DimDate[Date]` at day grain, only the last day of each period shows a full value. Put the measure in a visual grouped by month or year, or use it in a card where the filter context is the whole period. Also confirm `DimDate` is marked as a date table, because time intelligence silently fails without it.

### Q: Should actuals and budget live in one table or two?

Two tables are easier to reason about because each measure reads one fact table and the relationships stay simple. A single table with a Scenario column works when the grain, dimensions, and amount columns are identical, but it forces every measure to filter on Scenario, and it makes sign conventions harder to check. Start with two tables unless you have a strong reason to combine.

### Q: How do I handle a fiscal year that starts in July?

Add `FiscalYear` and `FiscalPeriod` columns in Power Query on `DimDate`, then pass the fiscal year-end date to the time intelligence function, for example `TOTALYTD([Total Revenue], DimDate[Date], "06/30")`. For grouped visuals, sort by the fiscal period number rather than the calendar month name so the axis runs July to June.

### Q: My variance percentage looks wrong when budget is zero.

It is not wrong, it is undefined. `DIVIDE` returns blank when the denominator is zero, which is the correct behavior. If you want a visible label, wrap the measure in `IF([Total Budget] = 0, BLANK(), ...)` and handle display formatting in the visual. Do not substitute a zero, because a zero variance implies you hit a target that does not exist.

### Q: How many visuals belong on one finance page?

Roughly ten to twelve, with the KPI strip counting as one band. The constraint is cognitive, not technical. If a reader has to scroll to compare last month's revenue to this month's, the layout is doing the wrong job. Move supporting detail to drill-through or a secondary page.

## Related Reading

- [Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
- [Build a Star Schema](/tutorials/data-modeling-star-schema/)
- [YTD, QTD and MTD in DAX](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [The CALCULATE Function](/tutorials/calculate-function/)
- [MoM and YoY DAX Template](/tutorials/power-bi-mom-yoy-dax-template/)
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)
- [Drill-Through in Power BI](/tutorials/power-bi-drill-through/)
- [DAX Variables Best Practices](/tutorials/dax-variables-guide/)
