---
title: "Getting Started with Power Query: Clean and Shape Data in Power BI"
description: "Power Query is the ETL engine behind Power BI. Learn to connect, transform, and shape data with a no-code interface plus a peek at the M language underneath."
pubDate: 2026-06-29
updatedDate: 2026-07-15
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "etl", "m-language", "data-prep"]
author: "DAX Guide Editorial Team"
featured: true
---

Every Power BI model starts with data, and data is rarely clean. Power Query is the built-in ETL (extract, transform, load) tool that lets you shape source data into a model-ready form — without writing code, if you prefer. This guide walks through the essentials.

## What is Power Query?

Power Query is a data preparation engine available in Power BI Desktop, Excel, and Dataflows. It provides:

- A **graphical interface** (the Power Query Editor) for common transformations
- A **formula language** called **M** for anything the UI can't do
- A **refreshable pipeline** — every step is recorded and re-run on each data refresh

The key insight: Power Query records your transformations as a script. When the source data changes, you click **Refresh** and the same steps run again. No more copy-pasting in Excel.

## Connecting to data

In Power BI Desktop, click **Get Data** and choose your source. Common options:

| Source | Use case |
|--------|----------|
| Excel workbook | Prototyping, small reference tables |
| SQL Server / PostgreSQL | Production data warehouses |
| SharePoint folder | Combining multiple files dropped in a shared folder |
| Web | Scraping HTML tables or calling REST APIs |
| Folder | Combining all CSV/Excel files in a local folder |

After connecting, Power BI shows a preview window. Click **Transform Data** to open the Power Query Editor — not Load, unless the data is already model-ready (rarely the case).

## Core transformations

The Power Query Editor ribbon has dozens of transformations. The 80/20 — the ones you'll use daily:

**1. Remove columns.** Right-click a column header → Remove. Or select several and choose Remove Columns. Models bloat fast; keep only what the report needs.

**2. Change data types.** Click the icon next to a column name. Power Query auto-detects types on import but always verify — `Decimal Number` vs `Whole Number` vs `Text` matters for DAX later.

**3. Filter rows.** Use the dropdown on any column header, identical to Excel's autofilter. To remove blanks: dropdown → (null) → uncheck.

**4. Split columns.** Right-click → Split Column → By Delimiter. Split `"Smith, John"` into two columns on the comma.

**5. Unpivot.** Select columns → Transform tab → Unpivot Columns. Converts wide tables (Jan, Feb, Mar as separate columns) into tall tables (one Date column, one Value column) — the format Power BI prefers.

**6. Merge queries.** Home tab → Merge Queries. The Power BI equivalent of SQL JOIN — combine two tables on a matching key.

**7. Append queries.** Stack tables vertically — useful for combining monthly files with identical structure.

## The M language (peek under the hood)

Every click in the Power Query Editor generates **M** code. Click **Advanced Editor** on the Home tab to see it. Here's a complete query that reads a CSV, promotes headers, sets types, and filters:

```text
let
    Source = Csv.Document(File.Contents("C:\Data\sales.csv"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"OrderDate", type date},
        {"Product", type text},
        {"Revenue", Currency.Type},
        {"Quantity", Int64.Type}
    }),
    Filtered = Table.SelectRows(Typed, each [Revenue] <> null and [Revenue] > 0)
in
    Filtered
```

M is a **functional language** — every step is a function call chained together with `let ... in`. You don't need to write M by hand for 90% of tasks, but reading it helps you debug and customize.

> When the Power Query UI can't do something, M can. Common scenarios: dynamic file paths, conditional logic across columns, custom API pagination.

## The single biggest performance mistake

Power Query applies transformations **in the order shown in the Applied Steps pane**. Reordering steps can dramatically change performance:

```text
// Slow: filter last, after expensive join
Source = ...,
Joined = Table.NestedJoin(Source, ...),
Filtered = Table.SelectRows(Joined, each [Region] = "EMEA")

// Fast: filter first, then join (fewer rows to join)
Source = ...,
Filtered = Table.SelectRows(Source, each [Region] = "EMEA"),
Joined = Table.NestedJoin(Filtered, ...)
```

Power Query's query folding can sometimes push filters down to the source, but never assume. When in doubt, filter early.

## Refresh strategy

Once your query is loaded into the Power BI model:

1. **Manual refresh** — Click Refresh in Power BI Desktop or the Power BI Service.
2. **Scheduled refresh** — In the Power BI Service, configure a refresh schedule (up to 8x/day with Pro, 48x/day with Premium).
3. **Incremental refresh** — For large tables, define a date-based partition so only new data is loaded on each refresh. Configure via Power Query parameters `RangeStart` and `RangeEnd`.

## What's next

Power Query handles the "shape your data" phase. Once data lands in the model, the next step is designing relationships and the star schema — see [Star Schema Data Modeling](/tutorials/data-modeling-star-schema) for the deep dive. Pair a clean Power Query pipeline with a well-designed model and DAX becomes dramatically easier to write.
