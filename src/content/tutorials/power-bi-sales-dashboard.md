---
title: "Build a Sales Dashboard in Power BI (Step by Step)"
description: "A sales dashboard is the most common first project in Power BI, and it is also the one most people get wrong."
pubDate: 2026-10-05
category: visualization
tags: ["dashboard", "sales"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

A sales dashboard is the most common first project in Power BI, and it is also the one most people get wrong. The usual failure mode is not a broken chart: it is a report with twenty visuals where nobody can tell whether revenue is up or down. This tutorial walks through building a compact, decision-ready sales dashboard from a flat order table. You will shape the data, build a small star schema, write a handful of measures, and lay out the finished page.

The whole build takes about an hour if you follow along in order. Everything here works on Power BI Desktop with no premium capacity.

## Prerequisites and sample data

Assume you have a single CSV export named `Sales.csv` with these columns:

| Column | Type | Example |
|---|---|---|
| OrderDate | Date | 2024-03-14 |
| OrderID | Text | SO-10231 |
| Customer | Text | Northwind Traders |
| Region | Text | West |
| Product | Text | Standing Desk |
| Category | Text | Furniture |
| Quantity | Whole number | 4 |
| UnitPrice | Decimal | 450.00 |
| UnitCost | Decimal | 290.00 |

Real exports are rarely this clean, which is exactly why step one is about cleanup.

## Step 1: Clean the data in Power Query

Load the CSV with **Get Data > Text/CSV**, then click **Transform Data** so you land in the Power Query Editor. Three things usually need fixing on a sales extract: dates arriving as text, missing cost values, and a concatenated key you do not want in the model.

```powerquery
let
    Source = Csv.Document(File.Contents("C:\Data\Sales.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"OrderDate", type date},
        {"OrderID", type text},
        {"Customer", type text},
        {"Region", type text},
        {"Product", type text},
        {"Category", type text},
        {"Quantity", Int64.Type},
        {"UnitPrice", type number},
        {"UnitCost", type number}
    }),
    RemovedBlankRows = Table.SelectRows(TypedColumns, each [OrderID] <> null and [OrderDate] <> null),
    FilledCost = Table.ReplaceValue(RemovedBlankRows, null, 0, Replacer.ReplaceValue, {"UnitCost"})
in
    FilledCost
```

`Table.TransformColumnTypes` fixes the date problem at the source, which matters because a text date breaks every time intelligence calculation later. `Int64.Type` on Quantity prevents accidental decimals. If your source has separate customer and product files, you will want to combine them rather than cram everything into one table; the trade-offs are covered in [Merge vs Append Queries](/tutorials/merge-vs-append-queries/).

Click **Close & Apply** when the preview looks right.

## Step 2: Build a minimal star schema

One wide table works, but it makes filtering unpredictable and slow. Split the order table into a fact and three dimensions. In Power BI Desktop, use **Enter Data** or reference the query to create `DimDate`, `DimCustomer`, and `DimProduct`. At minimum you need a proper date table.

```dax
DimDate =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2023, 1, 1 ), DATE ( 2025, 12, 31 ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "mmm" ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Year Month", FORMAT ( [Date], "yyyy-mm" )
)
```

Then mark it as a date table: select `DimDate`, go to **Table tools > Mark as date table**, and pick the `Date` column. Relationships go one-to-many from each dimension to the fact table, single direction. If you have not built a star schema before, [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/) covers why the shape matters more than the number of tables.

## Step 3: Write the core measures

Create a dedicated measure table (a blank table named `_Measures`) so your measures do not clutter the fact table. Start with revenue and margin.

```dax
Total Sales = SUMX ( Sales, Sales[Quantity] * Sales[UnitPrice] )

Total Cost = SUMX ( Sales, Sales[Quantity] * Sales[UnitCost] )

Gross Margin = [Total Sales] - [Total Cost]

Gross Margin % =
DIVIDE ( [Gross Margin], [Total Sales] )

Sales LY =
CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DimDate[Date] ) )

Sales YoY % =
VAR CurrentSales = [Total Sales]
VAR PriorSales = [Sales LY]
RETURN
    DIVIDE ( CurrentSales - PriorSales, PriorSales )
```

Note that `Gross Margin %` uses `DIVIDE` rather than the `/` operator. When the denominator is zero or blank, `DIVIDE` returns blank instead of an error, which keeps your visual from showing infinity. The `VAR` pattern in `Sales YoY %` is not decoration: it guarantees both branches of the calculation see the same filter context, and it is the recommended habit described in [DAX Variables Best Practices](/tutorials/dax-variables-best-practices/).

If you want to understand the engine underneath `CALCULATE`, start with [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/). `SUMX` iterates row by row, `CALCULATE` rewrites the filter context, and almost every sales measure is some combination of those two ideas.

## Step 4: Lay out the report page

Design the page before you drag a single field onto the canvas. A workable beginner layout:

| Zone | Visual | Fields |
|---|---|---|
| Top strip | Card visuals (4 across) | Total Sales, Gross Margin %, Sales YoY %, Orders |
| Left column | Line chart | Year Month on axis, Total Sales and Sales LY as values |
| Center | Clustered bar chart | Product on axis, Total Sales, top 10 by value |
| Right | Matrix | Region rows, Category columns, Gross Margin % values |
| Bottom left | Slicer | Region, Product Category |

Keep the line chart as the hero. Comparison against last year is the fastest way for a reader to answer "are we doing better?" without doing arithmetic. Format the line chart so the current year is a solid line and last year is dashed and muted; you set this per-series in the **Format** pane under **Lines**.

Three formatting rules that separate a professional page from a cluttered one:

1. Left-align all text, including card titles.
2. Use one accent color for the current period and gray for comparison series.
3. Turn off unnecessary axis labels when a data label already shows the value.

Sort the product bar chart explicitly with **Sort axis > Total Sales > descending**. Alphabetical product order hides your best sellers.

For color logic that reacts to the data itself, [Conditional Formatting Charts in Power BI](/tutorials/conditional-formatting-charts-power-bi/) explains how to drive colors from a measure rather than a static palette. That is worth doing on the margin matrix so weak regions stand out immediately.

## Step 5: Add interactivity

Two features raise the value of the dashboard far above a static chart dump.

**Drill-through**: create a second page called `Customer Detail`, add `Customer[Customer]` to the drill-through well, then right-click any data point on page one and pick **Drill through**. The full setup, including passing multiple fields, is in [Power BI Drill-Through](/tutorials/power-bi-drill-through/).

**Bookmarks**: if you want to switch the center visual between "by Product" and "by Customer", field parameters are the cleaner option, but bookmarks plus buttons work fine for beginners. See [Bookmarks and Navigation in Power BI](/tutorials/bookmarks-navigation-power-bi/) for the numbering trick that makes page navigation behave.

## Step 6: Check performance and publish

Before publishing, open **View > Performance Analyzer**, click **Start recording**, and refresh every visual on the page. Any visual taking more than roughly two seconds deserves investigation. A card visual that reads from a high-cardinality column, or a table with no aggregation, is the usual culprit.

Common beginner problems and their causes:

| Symptom | Likely cause |
|---|---|
| YoY % shows blank everywhere | Date table not marked, or relationship missing |
| Slicer filters some visuals but not others | Multiple fact tables without shared dimensions |
| Totals do not match row sums | Using `SUM` on a column with blanks instead of `SUMX` |
| Report is slow on open | Too many visuals per page, or DirectQuery instead of Import |

## FAQ

### Q: Do I need a separate date table to build a sales dashboard?

For year-over-year, YTD, or MTD comparisons, yes. `SAMEPERIODLASTYEAR` and its relatives require a contiguous date column marked as a date table and related to your fact table. Without it, the functions either error or return results that look plausible but are wrong.

### Q: Should I use SUM or SUMX for revenue?

If your source has a single `ExtendedAmount` column, `SUM` is enough. When revenue is quantity multiplied by price, use `SUMX` because there is no stored column to sum. `SUMX` on a large fact table is slower than summing a materialized column, so if performance becomes a problem, add the calculated line amount in Power Query instead.

### Q: How many visuals should one dashboard page have?

Aim for six to nine. Every visual is a question the reader has to process. Cards for the headline numbers, one trend chart, one comparison chart, one breakdown table, and slicers is a complete page for most audiences.

### Q: Why does my YoY percentage show infinity?

You used the `/` operator with a zero or blank prior-year value. Replace it with `DIVIDE`, which returns blank for invalid divisions. Blanks render as empty cells rather than error text.

### Q: Can I build this dashboard without writing DAX?

You can produce a basic version using implicit measures, but you lose year-over-year comparison and margin percentages. Learning ten DAX measures covers the vast majority of sales reporting requirements, and [DAX Basics](/tutorials/dax-basics/) is the fastest starting point.

## Related Reading

- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/)
- [DAX Basics](/tutorials/dax-basics/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX Time Intelligence: YTD, QTD, MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [Power BI MoM and YoY DAX Template](/tutorials/power-bi-mom-yoy-dax-template/)
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
- [Conditional Formatting Charts in Power BI](/tutorials/conditional-formatting-charts-power-bi/)
- [Power BI Drill-Through](/tutorials/power-bi-drill-through/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
