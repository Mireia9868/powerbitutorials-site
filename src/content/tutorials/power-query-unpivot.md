---
title: "Unpivot in Power Query: Turn a Wide Table into a Long Table the Right Way"
description: "Unpivot Columns in Power Query converts month-by-column reports into a tidy long format Power BI can model. Learn the exact steps, the pitfalls, and how to keep one column fixed."
pubDate: 2026-09-23
category: "power-query"
difficulty: "Beginner"
tags: ["power bi", "power query", "unpivot", "wide to long", "data shaping"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

A report that looks fine in Excel — months across the top, one row per product — is usually the wrong shape for Power BI. To chart, filter, or time-intelligence it, you want one row per (product, month, value). That transformation is called **unpivot**, and Power Query does it in two clicks. This guide shows the steps and the mistakes that break refreshes later.

## The problem with wide data

Imagine this source:

| Product | Jan | Feb | Mar |
|---|---|---|---|
| A | 100 | 120 | 90 |
| B | 80 | 95 | 110 |

You cannot put "Jan/Feb/Mar" on an axis because they are columns, not values. After unpivot you get:

| Product | Attribute | Value |
|---|---|---|
| A | Jan | 100 |
| A | Feb | 120 |
| A | Mar | 90 |
| B | Jan | 80 |
| … | … | … |

Now `Attribute` is a column you can slice and `Value` is a real measure.

## Step-by-step

1. Open **Power Query Editor** → select the column(s) you want to keep as-is (here, `Product`).
2. Right-click that column → **Unpivot Other Columns**.
   - Power Query keeps the selected column fixed and unpivots everything else.
3. Rename the two new columns: `Attribute` → `Month`, `Value` → `Amount`.
4. Set the `Month` column data type to text (or to a real date if it was `1/1/2026` style).
5. Close & Apply.

<!-- TODO: add screenshot: Figure 1: power query unpivot illustration -->

```powerquery
let
    Source = Excel.CurrentWorkbook(){[Name="Sales"]}[Content],
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Product", type text}}),
    #"Unpivoted Other Columns" = Table.UnpivotOtherColumns(
        #"Changed Type",
        {"Product"},
        "Month",
        "Amount"
    ),
    #"Changed Type1" = Table.TransformColumnTypes(#"Unpivoted Other Columns",{{"Amount", Int64.Type}})
in
    #"Unpivoted Other Columns"
```

## Unpivot Columns vs Unpivot Only Selected

There are two buttons:
- **Unpivot Columns** (with columns selected): unpivots *only* the selected ones.
- **Unpivot Other Columns** (with columns selected): keeps the selected ones fixed, unpivots the rest.

Prefer **Unpivot Other Columns**. If your source later adds a `Region` column, "unpivot other columns" adapts automatically; a hardcoded "unpivot Jan/Feb/Mar" breaks because those columns no longer exist.

## Pitfall: mixed data types in the value column

If `Jan` is text in one row and number in another, the unpivoted `Value` becomes `any`. Set the type **after** unpivot, and consider `Table.FillDown` or a clean step first. See [power-query-common-transformations](/tutorials/power-query-common-transformations/) for the type-cleaning patterns.

## Pitfall: the new column name collides with an existing one

If your source already has a column called `Attribute`, Power Query appends `1`. Rename explicitly so your model and any downstream DAX stay stable.

## When NOT to unpivot

If the wide layout is already your final visual (a printed-style matrix), leave it. But for almost any analytical model — especially time intelligence — long format is required. Read [time-intelligence](/tutorials/time-intelligence/) to see why a single `Date` column matters.

## FAQ

**Q: Can I unpivot in DAX instead?**
A: No clean way. Reshape in Power Query; DAX is for aggregation, not row rotation.

**Q: My months came in as text "Jan", how do I sort correctly?**
A: Add a sort column (1,2,3) or convert to a real date with `Date.FromText`, then sort by it. Text months sort alphabetically (Apr before Feb).

**Q: Unpivot makes my table huge — is that bad?**
A: Long format is how columnar engines (VertiPaq) compress best. It is usually smaller on disk than it looks.

## Related Reading

- [Power Query Getting Started](/tutorials/power-query-getting-started/)
- [Power Query Common Transformations](/tutorials/power-query-common-transformations/)
- [Power Query Group By](/tutorials/power-query-group-by/)
- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Power Query M Language Basics](/tutorials/power-query-m-language-basics/)
- [Time Intelligence Overview](/tutorials/time-intelligence/)
