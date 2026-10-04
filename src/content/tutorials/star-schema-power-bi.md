---
title: "Star Schema Design in Power BI: A Practical Guide"
description: "A star schema organizes your data model around a single fact table at the center, surrounded by dimension tables that describe the who, what, when, and where of each transaction."
pubDate: 2026-10-04
category: data-modeling
tags: ["data modeling", "star schema"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What a Star Schema Actually Is

A star schema organizes your data model around a single fact table at the center, surrounded by dimension tables that describe the "who, what, when, and where" of each transaction. The fact table stores numeric, additive measures and foreign keys. Dimension tables store descriptive attributes used for slicing and filtering. The shape looks like a star because each dimension connects directly to the fact table with a one-to-many relationship, and dimensions do not connect to each other.

In Power BI, this shape matters more than it does in most relational databases. The VertiPaq engine and the DAX formula engine are built to exploit it. Filter propagation flows from the "one" side of a relationship (a dimension) to the "many" side (the fact), so a single slicer selection filters the fact table efficiently without scanning unrelated relationships. When your model deviates from this shape, DAX measures that look simple start returning wrong numbers, and performance degrades because the engine has to evaluate ambiguous filter paths.

This guide walks through building a star schema from a flat table, verifying it, and fixing the three most common mistakes that break it.

## Fact Table vs. Dimension Table: The Decision Rules

Before writing any DAX, classify each column in your source.

| Question | Fact table | Dimension table |
|---|---|---|
| Does it contain numbers you aggregate (SUM, AVERAGE)? | Yes | Rarely |
| Does it contain text you group by? | No | Yes |
| Does it have a grain like "one row per order line"? | Yes | No |
| Is it narrow and tall (millions of rows)? | Yes | No |
| Is it wide and short (dozens to thousands of rows)? | No | Yes |

A table that mixes both is a flat denormalized table, common in Excel exports. Splitting it is the core task of star schema design.

## Step 1: Identify the Grain of the Fact Table

Grain means what one row represents. Write it down in a sentence: "one row per sales order line item." If two rows could describe the same event, the grain is wrong or you need a compound key. Getting the grain right prevents double-counting later, because every measure in DAX implicitly assumes the fact table's grain matches the level of detail being summed.

If a source table has multiple grains bundled together, split it into two fact tables. For example, an invoice header table and an invoice line table should not be merged.

## Step 2: Extract Dimensions with Power Query

Start from a flat Sales table and pull out a Product dimension using a reference query so the source is not re-evaluated twice.

```powerquery
// Query name: DimProduct
let
    Source = Sales,
    KeepColumns = Table.SelectColumns(
        Source,
        {"ProductID", "ProductName", "Category", "Subcategory"}
    ),
    RemoveDuplicates = Table.Distinct(KeepColumns, {"ProductID"}),
    TrimText = Table.TransformColumns(
        RemoveDuplicates,
        {{"ProductName", Text.Trim, type text},
         {"Category", Text.Trim, type text}}
    ),
    TypedColumns = Table.TransformColumnTypes(
        TrimText,
        {{"ProductID", Int64.Type},
         {"ProductName", type text},
         {"Category", type text},
         {"Subcategory", type text}}
    )
in
    TypedColumns
```

Repeat the pattern for Customer, Date, and any other descriptive grouping. The key step is `Table.Distinct` on the surrogate key, which guarantees one row per dimension member and keeps the relationship valid.

## Step 3: Reduce the Fact Table to Keys and Measures

After the dimensions are extracted, the fact table should hold only foreign keys and numeric measures.

```powerquery
// Query name: FactSales
let
    Source = Sales,
    KeepColumns = Table.SelectColumns(
        Source,
        {"OrderLineID", "ProductID", "CustomerID", "OrderDate",
         "Quantity", "UnitPrice", "DiscountAmount"}
    ),
    AddLineAmount = Table.AddColumn(
        KeepColumns,
        "LineAmount",
        each [Quantity] * [UnitPrice] - [DiscountAmount],
        type number
    ),
    TypedColumns = Table.TransformColumnTypes(
        AddLineAmount,
        {{"OrderLineID", Int64.Type},
         {"ProductID", Int64.Type},
         {"CustomerID", Int64.Type},
         {"OrderDate", type date},
         {"Quantity", Int64.Type},
         {"UnitPrice", type number},
         {"DiscountAmount", type number}}
    )
in
    TypedColumns
```

Note that `LineAmount` is materialized in Power Query rather than left as a DAX calculated column. At this stage in the design, pushing simple row-level arithmetic upstream reduces the model size and the memory VertiPaq must allocate during compression.

## Step 4: Build a Dedicated Date Dimension

Never use the automatic date hierarchy Power BI creates from a datetime column. It hides a table behind the scenes, prevents time intelligence from behaving predictably, and gives you no control over fiscal calendars. Create a proper Date table and mark it as a date table in the model view.

```dax
DimDate =
VAR MinDate = DATE ( 2021, 1, 1 )
VAR MaxDate = DATE ( 2025, 12, 31 )
RETURN
ADDCOLUMNS (
    CALENDAR ( MinDate, MaxDate ),
    "Year", YEAR ( [Date] ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Month Number", MONTH ( [Date] ),
    "Month Name", FORMAT ( [Date], "MMMM" ),
    "Year Month", FORMAT ( [Date], "YYYY-MM" ),
    "Day of Week", FORMAT ( [Date], "dddd" )
)
```

A calculated table works well for a fixed range. For a range driven by your data, replace the hardcoded dates with `MIN` and `MAX` from the fact table.

## Step 5: Create Relationships Correctly

In Model view, drag the dimension key to the fact key. Power BI will usually detect a one-to-many relationship. Verify the following for each relationship:

- Cardinality is one-to-many, with the dimension on the one side.
- Cross-filter direction is single, from dimension to fact.
- The relationship is active. If you need an inactive relationship for a secondary date role, use `USERELATIONSHIP` inside a `CALCULATE` expression.
- Data types on both sides match exactly. An Int64 key joined to a text key silently fails.

Avoid bidirectional filter direction unless you have a specific reason. Bidirectional filters create ambiguous filter paths in a star schema and can produce inflated totals. There is almost always a cleaner modeling fix.

## Step 6: Validate with a Simple Measure

After relationships are in place, test with a basic measure.

```dax
Total Sales = SUM ( FactSales[LineAmount] )

Sales by Category =
CALCULATE (
    [Total Sales],
    ALL ( DimProduct ),
    VALUES ( DimProduct[Category] )
)
```

If the model is a true star schema, filtering by any dimension attribute propagates correctly and produces no duplicates. If totals do not match a known reference, the grain of the fact table is likely wrong.

## Three Mistakes That Break the Star

**Snowflaking a dimension.** Splitting Product into Product and Subcategory tables adds a relationship and a filter hop. Unless Subcategory is reused across multiple unrelated dimensions, keep it as a column inside DimProduct. Snowflakes cost performance with no analytical gain in Power BI.

**Many-to-many relationships without a bridge.** If two fact tables share a dimension, route the relationship through a bridge table rather than setting many-to-many. Bridge tables preserve a clean one-to-many path.

**Calculated columns that should be measures.** A calculated column is evaluated at refresh and stored in memory. In a properly modeled star schema, most aggregation logic lives in measures that respond to filter context. Reserve calculated columns for row-level attributes like a discounted unit price or a sort key.

## Optimizing After the Model Is Built

Once the star schema is stable, run Performance Analyzer to see which visuals are slow. Most improvements come from reducing the cardinality of dimension columns, removing unused columns from the fact table, and avoiding calculated columns on high-cardinality text fields. A star schema gives the engine a clean filter graph; from there, measure optimization is the next lever.

## FAQ

### Q: Can I have more than one fact table in a star schema?

Yes, a model with multiple fact tables sharing conformed dimensions is called a galaxy schema or a fact constellation. Each fact table keeps its own grain and its own set of measures. Shared dimensions connect to all of them via one-to-many relationships. This is common in models that combine sales and inventory or sales and budget data.

### Q: What is the difference between a star schema and a snowflake schema?

A star schema has dimensions directly attached to the fact table with no further normalization. A snowflake schema normalizes dimensions into additional tables, creating chains of relationships. Power BI prefers stars because fewer relationship hops mean simpler filter propagation and faster queries. Snowflakes only make sense when a dimension attribute set is genuinely shared across multiple unrelated dimensions.

### Q: Do I need a separate date table, or can I use the date column in the fact table?

Use a separate date table. Time intelligence functions such as `TOTALYTD`, `SAMEPERIODLASTYEAR`, and `DATEADD` expect a continuous date column with no gaps, which a fact table date column often does not provide. A dedicated date table also lets you add fiscal columns, sort order columns, and year-to-date flags without touching the fact table.

### Q: How many columns should a dimension table have?

Only the attributes you actually use in slicers, axis labels, or filter conditions. Every extra column increases memory footprint and refresh time. A common rule is to keep the visible attribute list under twenty and to remove technical keys from the report view.

### Q: Why is bidirectional filtering discouraged in a star schema?

Bidirectional filtering allows a filter to flow from the fact table back to a dimension, which creates ambiguous paths when two dimensions both filter the same fact. The engine then has to guess which path wins, and the resulting totals are often inflated. Keep filters flowing one way, from dimensions to facts, and use measures with `CALCULATE` when you need a specific cross-filtering effect.

## Related Reading

- [Star Schema Data Modeling](/tutorials/data-modeling-star-schema/)
- [Bidirectional Filtering Guide](/tutorials/bidirectional-filtering-guide/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [CALCULATE Function](/tutorials/calculate-function/)
- [DAX Basics](/tutorials/dax-basics/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Power BI Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer-guide/)
