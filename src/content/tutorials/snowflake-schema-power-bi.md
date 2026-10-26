---
title: "Snowflake Schema vs Star Schema in Power BI"
description: "Dimensional modeling is the backbone of a fast, maintainable Power BI dataset."
pubDate: 2026-10-04
category: data-modeling
tags: ["data modeling", "schema"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

Dimensional modeling is the backbone of a fast, maintainable Power BI dataset. Two shapes dominate the conversation: the star schema and the snowflake schema. Both organize data into facts and dimensions, but they differ in how far they normalize those dimensions. Choosing correctly affects DAX complexity, refresh time, and how easily users find their way around the model.

This tutorial explains the difference, shows when snowflaking helps and when it hurts in Power BI, and walks through normalizing and re-flattening a dimension in Power Query.

## The Core Difference

A **star schema** has one central fact table connected to dimension tables that are *denormalized*: all attributes of a dimension live in a single table. Product category, subcategory, and product name all sit in one `DimProduct` table.

A **snowflake schema** normalizes those dimensions into multiple related tables. `DimProduct` links to `DimSubcategory`, which links to `DimCategory`. The fact table is still at the center, but the dimension branches out like a snowflake.

| Aspect | Star schema | Snowflake schema |
|---|---|---|
| Dimension structure | Flat, one table per dimension | Normalized, multiple related tables |
| Number of relationships | Fewer, mostly one hop | More, chained hops |
| Storage size | Larger (repeated values) | Smaller (values stored once) |
| DAX complexity | Lower | Higher across chained tables |
| Query/refresh speed in Power BI | Generally faster | Generally slower |
| ETL from normalized sources | Requires flattening | Can map source tables directly |

The storage argument for snowflaking is real in a relational warehouse, but Power BI is a columnar engine. It compresses repeated low-cardinality text extremely well, so the storage savings from normalization are usually negligible. What you *do* pay for is extra relationships and longer filter paths.

## Why Power BI Prefers Stars

The VertiPaq engine and the DAX formula engine both reward simplicity. When a filter travels from a fact table through a chain of dimension tables, each relationship is a hop the engine must traverse. Filter propagation across a snowflake is a common cause of slow visuals, and it becomes harder to reason about when bidirectional filters are involved.

Beyond performance, flat dimensions give report authors a single place to find attributes. A user dragging "Category" expects it in the product table, not buried two relationships away. Star schemas also keep relationship cardinality and direction simple, which matters if you later use `/tutorials/bidirectional-filtering-guide/` patterns.

## When Snowflaking Is Acceptable

Snowflaking is not a sin. There are practical cases where keeping a normalized dimension pays off:

- **Reused shared dimensions.** A `DimGeography` referenced by several facts is cleaner as one conformed table.
- **Very large dimensions with heavy attribute churn.** Splitting slowly changing pieces limits how often you process a huge table.
- **DirectQuery over a live warehouse.** You may not want to duplicate a complex source join at the model layer.
- **Role-playing dimensions.** A single date or employee table reused across multiple fact columns benefits from one canonical dimension.

The rule of thumb: snowflake at the *source* or in the warehouse, but flatten toward a star in the *import* model that feeds your reports.

## Building a Star in Power Query

Suppose your source delivers a normalized product hierarchy: `Products`, `Subcategories`, and `Categories`. You can merge them into one flat dimension table.

```powerquery
let
    // Start from the most granular table
    Source = Products,

    // Bring in subcategory name
    MergeSub = Table.NestedJoin(
        Source, {"SubcategoryKey"},
        Subcategories, {"SubcategoryKey"},
        "Sub", JoinKind.LeftOuter
    ),
    ExpandSub = Table.ExpandTableColumn(
        MergeSub, "Sub", {"SubcategoryName", "CategoryKey"}, {"SubcategoryName", "CategoryKey"}
    ),

    // Bring in category name
    MergeCat = Table.NestedJoin(
        ExpandSub, {"CategoryKey"},
        Categories, {"CategoryKey"},
        "Cat", JoinKind.LeftOuter
    ),
    ExpandCat = Table.ExpandTableColumn(
        MergeCat, "Cat", {"CategoryName"}, {"CategoryName"}
    ),

    // Drop the surrogate keys you no longer need for the model
    Result = Table.RemoveColumns(ExpandCat, {"SubcategoryKey", "CategoryKey"})
in
    Result
```

This pattern (join, expand, drop keys) is the same logic covered in `/tutorials/merge-vs-append-queries/`. Once expanded, you have a single `DimProduct` table with `ProductName`, `SubcategoryName`, and `CategoryName`, and the fact table needs only one relationship to it.

## Querying a Snowflake: DAX Implications

If you *do* keep a snowflake, your measures still work because filter context propagates through relationships, but cross-table references get verbose. Consider a chain Fact -> Product -> Subcategory -> Category.

```dax
Total Sales by Category =
CALCULATE(
    SUM ( FactSales[SalesAmount] ),
    USERELATIONSHIP ( DimProduct[CategoryKey], DimCategory[CategoryKey] )
)
```

If `DimProduct` already carried `CategoryName`, the same result is a plain visual-level filter with no measure needed. That is the trade: snowflaking pushes complexity into DAX and relationships; flattening pushes it into Power Query, once, at load time. The `CALCULATE` mechanics that make propagation work are worth reviewing in `/tutorials/calculate-function/` and `/tutorials/filter-context-row-context-explained/`.

A subtle accuracy point: relationship chains require *unbroken* many-to-one, single-direction paths from fact to the farthest dimension. If any hop is bidirectional or many-to-many, filter propagation can produce unexpected results, and you may need to rethink the model rather than patch it with DAX.

## Performance and Maintenance Trade-offs

Flattening increases the width of dimension tables and can inflate the model if you repeat long text strings. In practice, VertiPaq compresses those strings well, and the memory difference is small compared to the query-time savings. Larger models also refresh more slowly, so test both shapes with `/tutorials/power-bi-performance-analyzer/` before committing.

Maintenance is the stronger argument. A star schema is easier for teammates to navigate, easier to document, and less likely to break when someone adds a relationship. Snowflakes invite relationship sprawl and are harder to audit.

## Recommendation

For import-mode models in Power BI, default to a star schema. Flatten your conformed dimensions in Power Query, keep relationships one-hop, and reserve snowflaking for shared dimensions, DirectQuery scenarios, or genuinely huge, churny dimensions. When in doubt, model the star first and only break it apart when a concrete performance or source-integrity problem forces you to.

If you are still comparing storage and query engines, `/tutorials/directquery-vs-import-mode/` explains how mode changes these trade-offs. And if you are setting up your first dimensional model, start with `/tutorials/data-modeling-star-schema/` to get the base shape right.

## FAQ

### Q: Can I mix star and snowflake tables in one Power BI model?

Yes. Many production models are hybrids. You might keep a flat `DimProduct` while leaving `DimGeography` snowflaked into region and country, or keep a shared `DimDate` referenced by several facts. Mixing is fine as long as each path stays many-to-one and single-direction, and you document which dimensions are intentionally branched. Just avoid chains you cannot justify, since every extra hop adds filter-propagation cost and cognitive load.

### Q: Does snowflaking make my model smaller and therefore faster?

Rarely in Power BI. VertiPaq compresses repeated low-cardinality text very efficiently, so storing a category name in every product row costs little. The storage you save by normalizing is usually outweighed by extra relationships and longer filter paths at query time. Measure both shapes with Performance Analyzer before assuming a smaller model is a faster one.

### Q: Will flattening a dimension break my existing DAX measures?

It depends on what the measures reference. Measures that sum a fact column keep working, because the fact-to-dimension relationship is unchanged. Measures that reference a specific dimension table name or column will break if that table no longer exists, so you must retarget them to the flattened column. Adopt a consistent naming convention and use variables (`/tutorials/dax-variables-guide/`) so refactors touch fewer formulas.

### Q: When is snowflaking actually the right call in Power BI?

When a dimension is genuinely shared across multiple facts, when you are in DirectQuery over a live normalized warehouse, or when one dimension is so large and volatile that reprocessing it as a single flat table is impractical. These are real constraints. For typical import models built from a handful of source tables, flatten and stay flat.

## Related Reading

- /tutorials/data-modeling-star-schema/
- /tutorials/bidirectional-filtering-guide/
- /tutorials/filter-context-row-context-explained/
- /tutorials/merge-vs-append-queries/
- /tutorials/directquery-vs-import-mode/
- /tutorials/dax-optimization-techniques/
- /tutorials/calculate-function/
- /tutorials/power-bi-performance-analyzer/
