---
title: "Star Schema Data Modeling: The Foundation of Fast Power BI Reports"
description: "A well-designed star schema makes DAX easier and reports faster. Learn fact vs. dimension tables, relationship cardinality, and why bidirectional filters are usually a mistake."
pubDate: 2026-07-13
category: "data-modeling"
difficulty: "Intermediate"
tags: ["data-modeling", "star-schema", "relationships", "performance"]
author: "DAX Guide Editorial Team"
featured: false
---

If your Power BI report is slow, your DAX is convoluted, or your filters aren't working as expected — the problem is almost always the data model, not the formula. The star schema is the single most important design decision you'll make.

## Fact tables vs. dimension tables

A well-modeled Power BI dataset has two types of tables:

**Fact tables** record events. Each row is a transaction, an order, a click, a measurement. They're narrow (few columns) and long (many rows), and they consist mostly of:

- **Foreign keys** — pointers to dimension tables (`ProductKey`, `CustomerKey`, `DateKey`)
- **Measures** — numeric values you aggregate (`Revenue`, `Quantity`, `Cost`)

**Dimension tables** describe the entities involved. Each row is a unique entity, and the table is wide (many descriptive columns):

- `Product` — ProductKey, Name, Category, Brand, Color, ListPrice
- `Customer` — CustomerKey, Name, Segment, Country, City
- `Date` — Date, Year, Quarter, Month, Weekday

The fact table holds "what happened," the dimension tables hold "who, what, when, where."

## The star schema

In a star schema, one fact table sits at the center, with dimension tables radiating out — each connected by a one-to-many relationship. The shape looks like a star.

```
        Product
           |
    Date — Sales — Customer
           |
        Store
```

**Why this matters:**

1. **Filter direction is unambiguous.** Filters flow from dimensions (one side) to the fact (many side). One direction, predictable, fast.
2. **DAX becomes simple.** "Total revenue by category" is just `SUM(Sales[Revenue])` in a matrix with `Product[Category]` — the model does the work.
3. **Performance is optimal.** The Vertipaq engine compresses dimension tables heavily (few rows, many columns) and joins them efficiently to the fact.
4. **Maintenance is easier.** New attributes go in the relevant dimension. New measures go in the fact. Adding a `Brand` column to `Product` doesn't touch the fact table.

## Star vs. snowflake

A **snowflake schema** normalizes dimensions further — `Product → ProductSubcategory → ProductCategory`. Each level is its own table, chained by relationships.

| Aspect | Star | Snowflake |
|--------|------|-----------|
| Query simplicity | Simpler — one hop from dim to fact | More joins, more relationships |
| Storage | Slightly more (denormalized) | Less (normalized) |
| Performance | Faster (fewer joins) | Slower for complex queries |
| Maintenance | Easier — fewer tables | Harder — more tables to keep in sync |

**Recommendation:** default to star. Snowflake only when a dimension is genuinely huge and normalization saves meaningful storage — rare in Power BI where Vertipaq compression is excellent.

## Relationship cardinality

Power BI supports four relationship cardinalities. In order of preference:

**1. Many-to-one (the default).** Dimension (one side) → Fact (many side). Filter flows from the "one" to the "many." This is what you want 95% of the time.

**2. One-to-one.** Two tables with matching keys. Usually a sign you should merge them in Power Query instead.

**3. Many-to-many.** Both sides have duplicate keys. Power BI supports this but it's a performance and clarity red flag. Usually fixable by introducing a bridge dimension table.

**4. Many-to-many (with a bridge table).** The correct pattern for true many-to-many relationships (e.g., a customer can belong to multiple segments). Use a bridge table connecting both dimensions.

## Bidirectional relationships: handle with care

By default, relationships filter in one direction (dimension → fact). Power BI lets you enable **bidirectional** filtering, where the fact also filters the dimension.

**When it's useful:** rare. Scenarios like "show only the products that have sales in the current filter context."

**When it's dangerous:** almost always. Bidirectional filters:

- **Cause performance issues** — the engine must propagate filters in both directions across every relationship.
- **Create ambiguity** — when multiple paths exist between tables, Power BI picks one (often the wrong one) and results become unpredictable.
- **Make DAX harder to reason about** — you can no longer predict filter flow by looking at the model.

> Rule of thumb: never enable bidirectional filtering unless you can articulate exactly why single-direction won't work. If you're enabling it to make a measure return non-blank results, the measure is wrong — fix the DAX, not the relationship.

## A practical example

A sales report with these tables:

- `Sales` (fact) — `SalesKey`, `DateKey`, `ProductKey`, `CustomerKey`, `StoreKey`, `Quantity`, `UnitPrice`, `Revenue`
- `Date` (dim) — `Date`, `Year`, `Quarter`, `Month`, `MonthKey`
- `Product` (dim) — `ProductKey`, `Name`, `Category`, `Subcategory`, `Brand`
- `Customer` (dim) — `CustomerKey`, `Name`, `Segment`, `Country`
- `Store` (dim) — `StoreKey`, `Name`, `City`, `State`, `Region`

Relationships — all many-to-one, single-direction:

```
Date[Date]      → Sales[DateKey]
Product[ProductKey] → Sales[ProductKey]
Customer[CustomerKey] → Sales[CustomerKey]
Store[StoreKey]  → Sales[StoreKey]
```

With this model, every common question becomes a one-line measure:

```dax
Revenue by Category = SUM(Sales[Revenue])
// Drop Product[Category] on rows, the measure on values. Done.

Revenue by Country = SUM(Sales[Revenue])
// Drop Customer[Country] on rows. Done.

Revenue by Quarter = SUM(Sales[Revenue])
// Drop Date[YearQuarter] on rows. Done.
```

No `CALCULATE` gymnastics. No `FILTER` over multiple tables. The model does the work.

## Common modeling mistakes

**1. Using a single flat table.** Loading one giant Excel sheet with every column. It works for a 50-row prototype, but filters become slow, DAX becomes impossible, and refresh takes forever. Split into fact + dimensions.

**2. Storing attributes in the fact table.** `Sales[ProductName]`, `Sales[Category]` — these belong in `Product`, not `Sales`. Storing them in the fact table bloats it (millions of repeated strings) and breaks when a product changes category.

**3. Connecting date columns directly.** `Sales[OrderDate]` should not be both a column you filter and a column you join on. Always have a dedicated `Date` table and join through it.

**4. Multiple fact tables sharing no conformed dimension.** If `Sales` and `Inventory` both have a `ProductKey` but no shared `Product` dimension, you can't analyze them together. Build conformed dimensions — shared dimension tables that multiple facts reference.

## What's next

A clean star schema makes everything downstream easier: DAX, time intelligence, performance tuning, even security (row-level security is much simpler on dimension tables). Once your model is solid, revisit [DAX Basics](/tutorials/dax-basics) and [CALCULATE](/tutorials/calculate-function) — the formulas will feel dramatically more natural.

For large models (10M+ fact rows), the next step is aggregation tables and incremental refresh — topics we'll cover in the performance tuning guide.
