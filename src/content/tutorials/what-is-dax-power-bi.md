---
title: "What Is DAX in Power BI? (Plain-English Explanation)"
description: "DAX stands for Data Analysis Expressions. It is the formula language you use inside Power BI to create calculated columns, measures, and calculated tables."
pubDate: 2026-10-06
category: dax
tags: ["dax", "fundamentals"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

DAX stands for Data Analysis Expressions. It is the formula language you use inside Power BI to create calculated columns, measures, and calculated tables. If Power Query is the tool that shapes and loads your data, DAX is the language that answers questions about that data once it is loaded: totals, ratios, year-over-year growth, rankings, running balances, and anything else that needs to react to what a user clicks on a report.

This guide is a plain-English introduction. You do not need a programming background. You need a mental model of how DAX thinks, and a few working examples you can paste into Power BI Desktop and watch behave.

## Why DAX exists at all

When you drag a numeric column into a visual, Power BI sums it. That implicit aggregation is enough for simple reports, but it breaks down quickly. Revenue divided by order count, margin only for a specific region, this month compared to the same month last year, top 10 products within the currently selected category: none of these are a single column. They are calculations that must respond to filters.

That responsiveness is the whole point. A DAX measure does not store a value. It stores a recipe. When a user selects a slicer value, Power BI re-evaluates the recipe against the new filter context and returns a fresh number. One measure can produce different results in every cell of a matrix.

## The three things you can create with DAX

There are three objects you can build, and they behave very differently.

| Object | What it is | When it is calculated | Typical use |
|---|---|---|---|
| Calculated column | A new column added to a table | Once, during data refresh, row by row | A row-level attribute like a price band or a concatenated label |
| Measure | A dynamic value stored in the model | On every visual interaction | Aggregations, ratios, time intelligence |
| Calculated table | A whole new table produced by a query | Once, during data refresh | Date tables, parameter tables, disconnected lookup tables |

Beginners usually overuse calculated columns and underuse measures. Columns consume memory and are computed for every row, even if no visual shows them. Measures are computed only when needed and are what make a report interactive.

## The two contexts that explain almost everything

Two terms appear constantly in DAX documentation. Getting them straight removes most of the confusion.

**Filter context** is the set of filters active when a value is calculated. It comes from slicers, the row and column headers of a visual, page-level filters, and any filters a DAX function adds itself. If a matrix cell sits at the intersection of Region = "West" and Year = 2024, that cell's filter context includes both of those filters.

**Row context** is the "current row" a formula is evaluating. It exists inside calculated columns, inside iterators like SUMX and FILTER, and inside calculated tables. A calculated column formula always has a row context. A measure, by itself, does not.

The two interact through functions like CALCULATE (which modifies filter context) and through relationship propagation. If you only take one thing from this article, take this: a calculated column cannot see the whole table, and a measure cannot see individual rows unless you explicitly give it one with an iterator.

## Your first measures

Open Power BI Desktop, load any table with numeric values, right-click the table in the Fields pane, and choose New measure. The formula bar appears. Here is a small starter set using a conventional Sales table.

```dax
Total Sales = SUM ( Sales[SalesAmount] )

Order Count = COUNTROWS ( Sales )

Average Order Value = DIVIDE ( [Total Sales], [Order Count] )

Sales vs Target % = DIVIDE ( [Total Sales], SUM ( Targets[TargetAmount] ) )
```

Three details matter here.

First, measures reference other measures by name inside square brackets. `[Total Sales]` is a measure; `SUM ( Sales[SalesAmount] )` is a column being aggregated. Mixing the two up is a common beginner error.

Second, use DIVIDE instead of the `/` operator. DIVIDE handles division by zero by returning BLANK (or a value you specify) rather than an error, and it is typically faster.

Third, note the table name qualifier. `Sales[SalesAmount]` means the SalesAmount column of the Sales table. Fully qualifying column references keeps formulas readable and avoids ambiguity when two tables share a column name.

## A calculated column, and why it is different

Suppose you want to classify each order by size. That is a row-level decision, so a calculated column fits.

```dax
Order Size =
SWITCH (
    TRUE (),
    Sales[SalesAmount] >= 1000, "Large",
    Sales[SalesAmount] >= 250, "Medium",
    "Small"
)
```

This evaluates once per row at refresh time and stores the text. It has a row context, so referring to `Sales[SalesAmount]` returns the value on the current row. Try the same formula as a measure and it fails, because a measure has no current row to look at.

SWITCH with `TRUE ()` is the idiomatic DAX way to write a chain of conditions. The first condition that evaluates to TRUE wins, so order your thresholds from highest to lowest.

## Changing the filter context with CALCULATE

CALCULATE is the most important function in the language. It takes an expression and evaluates it under a modified filter context.

```dax
West Sales =
CALCULATE ( [Total Sales], Sales[Region] = "West" )
```

Whatever slicers or visual headers are active, this measure computes Total Sales as if Region were "West". It does not replace the existing filters; it overrides the filter on the Region column specifically, while leaving filters on other columns intact. That distinction is why CALCULATE composes so well.

A more realistic pattern combines CALCULATE with time intelligence:

```dax
Sales LY =
CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )

YoY Growth % =
DIVIDE ( [Total Sales] - [Sales LY], [Sales LY] )
```

Both measures depend on a marked Date table with a continuous, unbroken range of dates and a one-to-many relationship to Sales. Without that, time intelligence functions return wrong or blank results. This is the single most common source of "my DAX is broken" complaints.

## Where DAX fits in the workflow

A reasonable order of operations for a new report:

1. Get the data into Power Query and clean it there. Splitting columns, unpivoting, trimming text, and fixing types belong in Power Query, not in DAX.
2. Build a star schema. Fact tables at the centre, dimension tables around them, one-to-many relationships flowing from dimensions to facts.
3. Create a dedicated Date table and mark it as a date table.
4. Write base measures first: sums, counts, distinct counts. Name them with a consistent prefix or suffix so they sort together in the Fields pane.
5. Build derived measures on top of the base measures. Ratios, variances, and time comparisons should reference existing measures rather than re-aggregating columns.
6. Only add calculated columns when the value is genuinely row-level and cannot be done in Power Query.

That last point is worth restating. If a transformation can be done in Power Query, do it there. It compresses better, refreshes faster, and keeps the model smaller. DAX columns are for logic that depends on relationships between tables or on values that only make sense in the model.

## Syntax rules that trip people up

A short list of things that cause most beginner error messages:

- Column references need a table qualifier: `Sales[Amount]`, not `[Amount]`, when the column is not in the current table context.
- Measure references do not: `[Total Sales]`.
- String literals use double quotes. Single quotes wrap table names that contain spaces: `'Date'[Date]`.
- Comparison uses `=` for equality inside DAX expressions, unlike Excel's `=` convention confusion. `==` is not valid.
- DAX is case-insensitive for function and identifier names but conventionally written in UPPERCASE for functions.
- Blank and zero are different. `BLANK ()` is the DAX null. Use `ISBLANK` to test for it.
- Comments use `//` for a single line or `/* ... */` for a block.

If a measure returns an unexpected number, the fastest diagnosis is usually to drop the underlying columns into a table visual and check which filter context is actually active. A blank result almost always means the filter context eliminated every row.

## Hands-on exercise

Load the built-in financial sample or any sales dataset, then work through this sequence without looking anything up:

1. Create `[Total Sales]` as a SUM over the amount column.
2. Create `[Order Count]` with COUNTROWS.
3. Create `[Average Order Value]` with DIVIDE.
4. Put all three in a card visual, then add a Region slicer and click through the regions. Watch every card change together.
5. Add `[West Sales]` using CALCULATE and observe that it stays fixed while the others move.

That fifth step is the moment DAX usually clicks. You will see one measure that ignores a slicer and three that obey it, and the difference is entirely a matter of filter context.

## FAQ

### Q: Is DAX the same as Excel formulas?

No, although they share a family resemblance. Excel formulas operate on cells and ranges on a worksheet. DAX operates on tables and columns inside a data model, and it has a filter context that Excel does not. Functions like SUM and IF exist in both, but CALCULATE, FILTER, and the time intelligence family have no direct Excel equivalent. People who are strong in Excel pick up the syntax quickly and then get stuck on context, which is the genuinely new concept.

### Q: Should I write a calculated column or a measure?

Ask whether the answer depends on what the user has selected. If it does, it is a measure. If the value is a fixed property of the row, such as a category label or a price tier, a calculated column is fine. When in doubt, prefer a measure: it uses less memory and keeps the model smaller.

### Q: Does DAX work with DirectQuery models?

Yes. Measures work in DirectQuery, but performance depends on how much work you push back to the source database. Functions that require scanning an entire table, such as iterators over large fact tables, can be slow because every visual refresh generates SQL against the source. Calculated columns and calculated tables are more restricted and, in some DirectQuery configurations, unavailable. Test with realistic data volumes before committing.

### Q: What is the difference between CALCULATE and FILTER?

CALCULATE modifies the filter context using simple boolean conditions or filter tables, and it does so efficiently because the engine understands the shape of the filter. FILTER returns a table of rows and is evaluated as an iterator, which is more flexible but usually slower. Use CALCULATE with a direct condition whenever that expresses the intent. Reach for FILTER when the condition needs a measure or a complex expression that a simple column comparison cannot express.

### Q: Why does my time intelligence measure return blank?

The most common causes are a missing or unmarked Date table, a broken date relationship, or gaps in the date range. Time intelligence functions rely on a contiguous date column and a relationship to the fact table. Create a dedicated Date table with CALENDAR or CALENDARAUTO, mark it as a date table, and relate it to your fact table before writing any year-over-year logic.

### Q: How do I learn DAX faster?

Write measures, break them, and inspect the results. Use variables to split a complex formula into named steps so you can return the intermediate value and see what it holds. Read other people's measures and try to predict what they will do before you run them. The context model is the hard part, not the function list, so spend your practice time on filter context experiments rather than memorising syntax.

## Related Reading

- [DAX Basics](/tutorials/dax-basics/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [The CALCULATE Function](/tutorials/calculate-function/)
- [DAX CALCULATE Function](/tutorials/dax-calculate-function/)
- [DAX Variables Guide](/tutorials/dax-variables-guide/)
- [DAX Time Intelligence: YTD, QTD, MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [Star Schema Data Modeling](/tutorials/data-modeling-star-schema/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [DAX Troubleshooting Guide](/tutorials/dax-troubleshooting-guide/)
