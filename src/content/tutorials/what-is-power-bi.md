---
title: "What Is Power BI? A Complete Beginner Overview"
description: "What is Power BI? An overview of its three parts - Power Query for data prep, the data model, and report design - with a first report built from a spreadsheet."
pubDate: 2026-10-14
category: visualization
tags: ["fundamentals"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Power BI is Microsoft's business intelligence platform for turning raw data into interactive reports and dashboards. It bundles together three things that used to require separate tools: a data preparation engine (Power Query), an analytical calculation language (DAX), and a visualization layer that runs in the browser, on desktop, and on mobile.

If you have ever stitched together a monthly report by copying figures out of Excel into slides, Power BI is designed to remove that workflow. You connect once, model the data properly, and then refresh on a schedule.

## The Three Core Tools Inside Power BI

Most of the confusion beginners hit comes from not realizing Power BI is really three products sharing one file format.

| Tool | What it does | Language / Interface |
|---|---|---|
| Power Query | Connects to sources, cleans and shapes data | M language, mostly graphical |
| Data Model | Relates tables, defines measures | DAX, relationships view |
| Report View | Builds visuals and pages | Drag-and-drop canvas |

Power BI Desktop is the authoring tool. Power BI Service (app.powerbi.com) is the cloud host where reports get published, shared, and scheduled for refresh. A `.pbix` file holds all three layers.

## Step 1: Get the Data In

Open Power BI Desktop and click **Get data**. You get connectors for Excel, SQL Server, SharePoint, Dataverse, Salesforce, web pages, and hundreds more. The choice that matters most early on is the storage mode:

- **Import mode** copies data into Power BI's in-memory engine (VertiPaq). It is fast and works with the full DAX feature set.
- **DirectQuery** leaves data in the source and queries it live. It suits very large or constantly changing sources but limits some DAX functions.

For a first project, use Import mode. It is faster to build with and easier to reason about.

## Step 2: Transform Data with Power Query

Clicking **Transform Data** opens the Power Query Editor. This is where you remove columns, change types, split text, filter rows, and merge or append queries.

Every click generates M code. You can see it in the formula bar, and you can edit it directly. For example, a simple query that promotes headers, removes a column, and changes a type looks like this:

```powerquery
let
    Source = Excel.Workbook(File.Contents("C:\Reports\Sales.xlsx"), null, true),
    Sales_Sheet = Source{[Item="Sales",Kind="Sheet"]}[Data],
    PromotedHeaders = Table.PromoteHeaders(Sales_Sheet, [PromoteAllScalars=true]),
    RemovedErrors = Table.RemoveRowsWithErrors(PromotedHeaders, {"OrderDate"}),
    ChangedTypes = Table.TransformColumnTypes(RemovedErrors, {
        {"OrderDate", type date},
        {"CustomerID", Int64.Type},
        {"Amount", type number}
    })
in
    ChangedTypes
```

Two habits pay off here. First, always set data types explicitly rather than leaving them as "Any". Second, name your steps meaningfully, because you will read them again six months later. Data cleaning that happens in Power Query does not have to be repeated in DAX, and it does not slow down your report visuals.

## Step 3: Build the Data Model

Close Power Query and you land in the model view. A well-built model is almost always a **star schema**: one or more fact tables (transactions, events, sales lines) surrounded by dimension tables (Date, Customer, Product, Geography).

Relationships connect them, usually one-to-many from dimension to fact. Get this right and DAX measures become short and predictable. Get it wrong and you end up fighting filter behavior in every visual.

Measures are the calculations the report consumes. A basic revenue measure using the `CALCULATE` function to change filter context:

```dax
Total Sales =
SUMX(
    Sales,
    Sales[Quantity] * Sales[UnitPrice]
)

Sales YoY % =
VAR CurrentSales = [Total Sales]
VAR PriorSales =
    CALCULATE(
        [Total Sales],
        SAMEPERIODLASTYEAR('Date'[Date])
    )
RETURN
    DIVIDE(CurrentSales - PriorSales, PriorSales)
```

`CALCULATE` is the function that makes Power BI powerful: it evaluates an expression under a modified filter context, which is how time intelligence, percentages of total, and dynamic comparisons all work.

A quick note on a common beginner misconception: `EARLIER` is often described as "the previous row", but it actually refers to an outer row context and only behaves as expected when there is a nested row context, such as an iterator inside a calculated column.

## Step 4: Design the Report

Switch to report view. The canvas holds visuals: bar charts, line charts, matrices, cards, slicers, maps. You bind them by dragging fields and measures into the field wells.

The layout rules that matter most:

1. **One question per visual.** If a chart tries to answer two questions, split it.
2. **Top-left is prime real estate.** Put the most important KPI or trend there.
3. **Limit slicers to three or four per page.** More than that becomes a control panel nobody uses.
4. **Use consistent formatting.** Same number formats, same color palette, same font sizes across pages.
5. **Design for the smallest screen your audience uses.** Mobile layouts are a separate configuration in Desktop.

Conditional formatting is where a lot of report polish lives. Coloring a bar chart by a measure, or applying rules to a matrix, lets the visual communicate without a legend explaining it.

## Step 5: Publish and Share

Click **Publish** to push the `.pbix` to a workspace in Power BI Service. From there you can:

- Create a **dashboard** that pins visuals from one or more reports.
- Build an **app** to distribute a curated set of reports to a group.
- Set up a **scheduled refresh** against an on-premises data gateway if the source is internal.
- Configure **row-level security** so different users see different slices of the same report.

Licensing splits into two tracks: Power BI Free (authoring and personal use) and Power BI Pro or Premium Per User (sharing, collaboration, app distribution). Fabric capacities sit above both and add shared compute.

## What Power BI Is Not

It is not a spreadsheet replacement for ad-hoc calculations. It is not a database. It is not a place to store your source of truth. The source system stays authoritative; Power BI reads from it, shapes it, and presents it. Treating a `.pbix` file as a data store leads to fragile reports that break the moment someone edits a cell in the underlying Excel file.

It is also not automatic. A model full of many-to-many relationships, no date table, and columns where measures should be will produce slow, wrong reports regardless of how attractive the visuals look.

## A Reasonable First Project

Pick one process you already report on monthly. Load the source into Power Query, clean it, build a star schema with a proper date table, write three or four measures, and build a single-page report with a trend line, a category breakdown, and two KPI cards. Publish it to a workspace and share it with one colleague.

That loop covers every concept you need to understand the rest of the platform. Everything after that is depth: better DAX, better modeling, better visual design.

## FAQ

### Q: Do I need a paid license to learn Power BI?

No. Power BI Desktop is free and includes the full authoring experience: Power Query, the data model, DAX, and report design. You only need Power BI Pro or Premium Per User when you want to share reports with other people through the Service, use apps, or set up scheduled refresh in a shared workspace. For learning, Desktop alone is enough.

### Q: What is the difference between Power BI Desktop and Power BI Service?

Desktop is the authoring tool where you build queries, models, and reports, and it saves everything into a `.pbix` file on your machine. The Service is the cloud platform at app.powerbi.com where you publish those files, create dashboards, manage refresh schedules, control permissions, and let colleagues view reports in a browser. You generally work in Desktop and distribute through the Service.

### Q: Should I use Import mode or DirectQuery?

Start with Import mode unless you have a specific reason not to. It is faster, supports the full DAX function library, and is far easier to debug. DirectQuery makes sense when the source is too large to copy, when data must be real-time, or when security rules live in the source database. Many production models use a mix, with large fact tables in DirectQuery and small dimensions imported.

### Q: Do I need to know DAX to build reports?

You can build simple reports by dragging existing columns into visuals, so technically no. But any calculation beyond a basic sum or count, such as year-over-year growth, running totals, or dynamic ranking, requires a measure. Learning `CALCULATE`, `SUMX`, `DIVIDE`, and `VAR` covers a surprisingly large share of real-world needs.

### Q: How is Power BI different from Excel?

Excel is a grid you compute in; Power BI is a model you query. Excel works well for one-off analysis and small datasets, and its formulas recalculate cell by cell. Power BI separates data preparation (Power Query), calculations (DAX measures evaluated against a filter context), and presentation (visuals). That separation is what lets a Power BI report scale to millions of rows and refresh automatically.

### Q: What is a star schema and why does it matter?

A star schema arranges tables into fact tables (measurable events like sales) and dimension tables (descriptive attributes like customer, product, date). Relationships run one-to-many from dimension to fact. This layout makes DAX measures simpler and faster, avoids ambiguous filter paths, and is the shape the VertiPaq engine is optimized for. Most modeling problems trace back to skipping it.

For the official documentation behind this topic, see [Microsoft Visual types in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-types-for-reports-and-q-and-a).

## Related Reading

- [Power BI Common Mistakes Beginners Make](/tutorials/power-bi-common-mistakes-beginners/)
- [Data Modeling: Star Schema Guide](/tutorials/data-modeling-star-schema/)
- [DAX Basics](/tutorials/dax-basics/)
- [Power Query Getting Started](/tutorials/de-power-query-getting-started/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)

- [Power BI Slicers: Sync, Hierarchy, and Bookmark-Driven Filtering](/tutorials/power-bi-slicers-best-practices/)
- [Tableau vs Power BI: Which Should You Choose in 2026](/tutorials/tableau-vs-power-bi/)