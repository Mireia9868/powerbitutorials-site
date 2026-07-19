---
title: "Merge vs Append Queries in Power Query: Which One Do You Need?"
description: "Merge and append are the two ways to combine tables in Power Query, and they do completely different things. Merge is a SQL-style join — it adds columns. Append is a union — it stacks rows. This guide covers the difference, the join types, and the performance implications of each."
pubDate: 2026-07-17
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "merge", "append", "join", "combine-queries"]
author: "Power BI Tutorials Team"
featured: false
---

Combining tables is one of the most common Power Query tasks, and it's also one of the most confused. "Merge" and "append" sound similar, but they solve fundamentally different problems. Pick the wrong one and you'll get either duplicate columns or stacked data that makes no sense. This guide makes the distinction clear.

## The one-line summary

- **Merge** = join two tables side by side. Adds **columns** based on matching keys. Think SQL `JOIN`.
- **Append** = stack tables on top of each other. Adds **rows** from one table to another. Think SQL `UNION`.

## When to merge

Use merge when you have two tables with a common key and you want to enrich one with columns from the other.

**Example:** `Sales` has `ProductID`, and `Products` has `ProductID`, `ProductName`, and `Category`. You want `ProductName` and `Category` available in the sales table.

```
Sales:                      Products:
OrderID | ProductID | Revenue    ProductID | ProductName | Category
1       | P100      | 500         P100      | Widget      | Hardware
2       | P200      | 300         P200      | Gadget      | Electronics
3       | P100      | 450         P300      | Gizmo       | Hardware
```

After merging `Sales` with `Products` on `ProductID`:

```
OrderID | ProductID | Revenue | ProductName | Category
1       | P100      | 500     | Widget      | Hardware
2       | P200      | 300     | Gadget      | Electronics
3       | P100      | 450     | Widget      | Hardware
```

## Merge join types

Power Query offers six join types. The first two cover 90% of use cases:

| Join type | What it returns |
|-----------|----------------|
| **Left Outer** | All rows from the left table, with matched columns from the right. Unmatched rows show `null` for right columns. (Most common.) |
| **Right Outer** | All rows from the right table, with matched columns from the left. |
| **Full Outer** | All rows from both tables. Unmatched rows show `null` on the side that doesn't match. |
| **Inner** | Only rows where the key exists in both tables. |
| **Left Anti** | Rows from the left table that have **no match** in the right. Useful for finding orphaned records. |
| **Right Anti** | Rows from the right table that have no match in the left. |

**Which to choose?** Start with Left Outer. It preserves all your existing rows and adds lookups. If you only want matched rows (dropping orphans), use Inner.

## When to append

Use append when you have tables with the same (or similar) structure and you want to stack them into one.

**Example:** You receive monthly sales files — `JanSales`, `FebSales`, `MarSales` — each with the same columns. You want a single `Q1Sales` table.

```
JanSales:             FebSales:             MarSales:
Date | Revenue         Date | Revenue         Date | Revenue
1/1  | 100             2/1  | 200             3/1  | 150
1/15 | 120             2/15 | 180             3/15 | 210
```

After appending:

```
Q1Sales:
Date | Revenue
1/1  | 100
1/15 | 120
2/1  | 200
2/15 | 180
3/1  | 150
3/15 | 210
```

Append matches columns by **name**, not position. If `JanSales` has `Revenue` and `FebSales` has `Revenue`, they stack. If `FebSales` has `Amount` instead, you'll get two separate columns with `null` in the gaps.

## The performance difference

**Append is fast.** It's a simple row concatenation — the engine just stacks the tables. Even millions of rows append in seconds.

**Merge can be slow.** It's a join operation, and performance depends on:

- **Table size** — merging a 10M-row fact table with a 100-row dimension table is fine. Merging two 10M-row tables can take minutes.
- **Join type** — Left Outer is usually fastest. Full Outer can be slower because it scans both tables.
- **Keys** — merging on an integer key is faster than on a text key. If possible, use surrogate keys (integers) for merges.

**Tip:** In the Power BI data model, relationships handle most "merge" scenarios more efficiently than Power Query. If you're merging just to add a lookup column, consider loading both tables separately and creating a relationship instead — it's more flexible and uses less memory.

## Practical example: merging customer lookups

You have `Orders` with `CustomerID` and a `Customers` table. You want `CustomerName` and `Region` available for filtering.

**Option A: Merge in Power Query.**

```m
Merged = Table.NestedJoin(
    Orders,
    {"CustomerID"},
    Customers,
    {"CustomerID"},
    "Customers",
    JoinKind.LeftOuter
)
Expanded = Table.ExpandTableColumn(Merged, "Customers", {"CustomerName", "Region"})
```

This adds the columns directly to `Orders`. Simple, but it duplicates the lookup data in every row.

**Option B: Load both tables and create a relationship.**

Load `Orders` and `Customers` as separate tables. In the Power BI model view, create a one-to-many relationship from `Customers[CustomerID]` to `Orders[CustomerID]`. Now you can filter by `Region` or display `CustomerName` without duplicating data.

**When to use which:**
- Use **Option B (relationship)** for standard star schema designs. It's the recommended approach — less memory, more flexible, and follows best practices.
- Use **Option A (merge)** only when you need the enriched table as a flat export, or when the relationship approach doesn't work (e.g., merging two fact tables with no shared dimension).

## Common mistakes

**Mistake 1: Appending tables with mismatched column names.** `JanSales` has `Revenue`, `FebSales` has `RevenueAmount`. After append, you get both columns with `null` interleaving. Fix: rename columns to match before appending.

**Mistake 2: Merging when a relationship would do.** If you're adding lookup columns from a dimension table, a relationship is almost always better than a merge. Relationships are dynamic (respond to filters) and don't duplicate data.

**Mistake 3: Merging on non-unique keys.** If the right table has duplicate keys, the merge produces duplicate rows in the left table. Always verify that your merge key is unique on at least one side.

## Summary

Merge adds columns (join). Append adds rows (union). Use merge for lookups and enrichment — but prefer relationships in the model when possible. Use append to combine similarly structured tables, like monthly exports or regional files. Match column names before appending, and use integer keys for faster merges.
