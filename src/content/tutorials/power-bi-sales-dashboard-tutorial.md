---
title: "Build a Sales Dashboard in Power BI: End-to-End Tutorial"
description: "Follow a real-world project from raw data to finished dashboard. Learn data import, Power Query cleaning, star schema modeling, DAX measures, and visual design — all in one walkthrough."
pubDate: 2026-07-20
category: "visualization"
difficulty: "Intermediate"
tags: ["project", "sales", "dashboard", "end-to-end", "tutorial"]
author: "Power BI Tutorials Team"
featured: true
---

Most tutorials teach Power BI features in isolation. This guide is different — we'll build a complete sales dashboard from scratch, covering every stage: data import, cleaning, modeling, DAX, and visual design. By the end, you'll have a repeatable workflow you can apply to any business dataset.

## The scenario

You're a data analyst at a retail company. The sales director wants a dashboard to answer:

1. What's our revenue trend over the last 12 months?
2. Which product categories are over/under performing vs. target?
3. Which regions need attention?

You have three data sources:
- **Sales transactions** (CSV, 50,000 rows)
- **Product master** (Excel, 500 products)
- **Sales targets** (Excel, monthly targets by category)

## Step 1: Import and clean data

### Import the sales CSV

In Power BI Desktop: **Get Data → Text/CSV → select sales.csv → Transform Data** (not Load).

Common issues in raw sales data:
- Dates as text (`2026-01-15` instead of a date type)
- Revenue with currency symbols (`$1,200.00`)
- Inconsistent category labels ("Electronics" vs "Electronic")
- Duplicate rows from system exports

### Clean in Power Query

Apply these transformations:

1. **Set data types:**
   - `OrderDate` → Date
   - `Revenue` → Currency (remove `$` and `,` first if needed)
   - `Quantity` → Whole Number
   - `ProductKey` → Whole Number
   - `Region` → Text

2. **Remove duplicates:**
   - Select all columns → Right-click → Remove duplicates

3. **Filter out test data:**
   - Filter `Revenue > 0` (remove nulls and test orders)

4. **Remove unused columns:**
   - Keep only: `OrderDate`, `ProductKey`, `Region`, `Quantity`, `Revenue`, `Cost`

### Import product master

**Get Data → Excel → products.xlsx → Transform Data:**

1. Set `ProductKey` to Whole Number
2. Remove columns you don't need (keep: `ProductKey`, `ProductName`, `Category`, `Subcategory`, `Brand`)
3. Standardize category labels (Replace Values: "Electronic" → "Electronics")

### Import sales targets

**Get Data → Excel → targets.xlsx → Transform Data:**

The targets file likely has months as columns (wide format). Unpivot:

1. Select `Category` column
2. Transform → Unpivot Other Columns
3. Rename: `Attribute` → `Month`, `Value` → `TargetRevenue`
4. Set `TargetRevenue` to Currency
5. Convert `Month` text ("Jan 2026") to a date that matches your date table

## Step 2: Build the star schema

Create a date table (if you don't have one):

```dax
Date = CALENDAR(DATE(2025, 1, 1), DATE(2026, 12, 31))
```

Add columns:

```dax
Year = YEAR('Date'[Date])
Quarter = "Q" & QUARTER('Date'[Date])
Month = FORMAT('Date'[Date], "MMM yyyy")
MonthKey = FORMAT('Date'[Date], "YYYYMM")
```

Mark as date table: Model View → select Date table → Mark as date table → choose `Date` column.

### Set up relationships

In Model View, create these relationships (all many-to-one, single-direction):

```
Date[Date]           → Sales[OrderDate]
Product[ProductKey]  → Sales[ProductKey]
Date[Date]           → Targets[Month]  (may need a MonthKey relationship)
```

Your model should look like a star: `Sales` at the center, with `Date`, `Product`, and `Targets` as dimensions radiating out.

## Step 3: Write DAX measures

### Basic measures

```dax
Total Revenue = SUM(Sales[Revenue])
Total Quantity = SUM(Sales[Quantity])
Total Cost = SUMX(Sales, Sales[Quantity] * Sales[UnitCost])
Gross Margin = [Total Revenue] - [Total Cost]
Gross Margin % = DIVIDE([Gross Margin], [Total Revenue])
```

### Target comparison

```dax
Target Revenue = SUM(Targets[TargetRevenue])

Revenue vs Target = [Total Revenue] - [Target Revenue]
Revenue vs Target % = DIVIDE([Revenue vs Target], [Target Revenue])
```

### Time intelligence

```dax
Revenue LY = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
Revenue YoY = [Total Revenue] - [Revenue LY]
Revenue YoY % = DIVIDE([Revenue YoY], [Revenue LY])

Revenue YTD = TOTALYTD([Total Revenue], 'Date'[Date])
```

### Rolling 12-month

```dax
Revenue Rolling 12M =
CALCULATE(
    [Total Revenue],
    DATESINPERIOD(
        'Date'[Date],
        MAX('Date'[Date]),
        -12,
        MONTH
    )
)
```

## Step 4: Build the dashboard

### Page 1: Executive summary

**Purpose:** Answer "are we on track?"

Layout (top to bottom):
1. **KPI cards** (row of 4): Revenue YTD | Target | Variance % | YoY Growth %
2. **Revenue trend** (line chart): Date[Month] on x-axis, [Total Revenue] and [Target Revenue] on y-axis
3. **Category performance** (bar chart): Product[Category] on y-axis, [Revenue vs Target %] on x-axis
4. **Region breakdown** (matrix): Region on rows, [Total Revenue] and [Revenue vs Target %] on values

### Page 2: Category deep-dive

**Purpose:** Answer "which categories need attention?"

1. **Slicer:** Product[Category]
2. **Revenue by subcategory** (bar chart)
3. **Margin % by product** (bar chart, sorted descending)
4. **Revenue vs target by month** (clustered column chart)

### Page 3: Regional analysis

**Purpose:** Answer "which regions need attention?"

1. **Slicer:** Region
2. **Revenue by region** (map visual)
3. **Top 10 products by region** (table with conditional formatting)
4. **Monthly trend by region** (line chart with small multiples)

### Apply design principles

- **Color:** one accent color (blue) for current period, gray for comparison
- **Conditional formatting:** red for negative variance, green for positive
- **Labels:** clear KPI titles, axis labels with units
- **Tooltips:** customize to show Revenue, Target, Variance, and LY comparison

See our [dashboard design principles](/tutorials/power-bi-dashboard-design-principles) for the full guide.

## Step 5: Add interactivity

### Slicers

Add a date range slicer and a category slicer to the top of each page. Sync slicers across pages using the View → Sync Slicers pane.

### Drill-through

Enable drill-through from the regional matrix on Page 1 to Page 3:

1. On Page 3, drag `Region` to the "Drill-through" field well
2. On Page 1, right-click a region in the matrix → Drill through → Regional analysis

### Bookmarks

Create bookmarks for different views:
- "All regions" view
- "Underperforming regions" view (filtered to negative variance)
- "Growth opportunities" view (filtered to high YoY growth)

See our [bookmarks guide](/tutorials/bookmarks-navigation-power-bi) for setup.

## Step 6: Optimize and test

### Performance check

Run Performance Analyzer (View → Performance Analyzer):
- Each visual should load in under 2 seconds
- DAX query time should dominate (not visual display)
- If slow, check for `FILTER(ALL(...))` patterns and unused columns

See our [performance guide](/tutorials/power-bi-performance-optimization) for optimization techniques.

### User testing

Before publishing, watch someone use the dashboard:
- Can they answer the three business questions?
- Do they know where to click?
- Are the numbers formatted clearly?

## Step 7: Publish and share

1. **Publish to Power BI Service:** File → Publish → select workspace
2. **Set up scheduled refresh:** Workspace → Datasets → Settings → Scheduled refresh
3. **Share with stakeholders:** Workspace → Reports → Share

For row-level security (each regional manager sees only their region), see Microsoft's RLS documentation.

## What you built

A three-page sales dashboard that:
- Tracks revenue vs. target with variance analysis
- Shows YoY growth and rolling 12-month trends
- Drills from executive summary to category and regional detail
- Updates automatically with scheduled refresh

The same workflow — import, clean, model, DAX, design, test, publish — applies to any business dashboard you'll build.

## FAQ

**How long should this take to build?**
For a beginner: 4-8 hours. For an experienced analyst: 1-2 hours. The first build is always slowest — once you have the pattern, subsequent dashboards go faster.

**Can I use this as a portfolio project?**
Yes. Use the sample data from Microsoft's Contoso dataset (free download) and build this dashboard. It demonstrates data cleaning, modeling, DAX, and visual design — all the skills employers look for.

**What if my data sources are different?**
The workflow is the same. The specific transformations change, but the structure (clean in Power Query → star schema → DAX measures → designed pages) applies universally.

## What's next

- Learn [DAX basics](/tutorials/dax-basics) to write better measures
- Master [star schema modeling](/tutorials/data-modeling-star-schema) for clean models
- Study [dashboard design principles](/tutorials/power-bi-dashboard-design-principles) for better visuals
- Check the [performance guide](/tutorials/power-bi-performance-optimization) when reports slow down
