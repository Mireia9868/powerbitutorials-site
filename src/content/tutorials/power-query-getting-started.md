---
title: "Getting Started with Power Query: Clean and Shape Data in Power BI"
description: "Power Query is the ETL engine behind Power BI. Learn to connect, transform, and shape data with a no-code interface plus a peek at the M language underneath."
pubDate: 2026-06-29
updatedDate: 2026-07-20
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "etl", "m-language", "data-prep"]
author: "Power BI Tutorials Team"
featured: true
---

Every Power BI model starts with data, and data is rarely clean. Dates come in as text. Numbers have thousand separators embedded. Column names change between exports. Power Query is the built-in ETL (extract, transform, load) tool that lets you shape source data into a model-ready form — without writing code, if you prefer. This guide walks through the essentials, including the mistakes that cause 80% of downstream DAX problems.

## What is Power Query?

Power Query is a data preparation engine available in Power BI Desktop, Excel, and Dataflows. It provides:

- A **graphical interface** (the Power Query Editor) for common transformations
- A **formula language** called **M** for anything the UI can't do
- A **refreshable pipeline** — every step is recorded and re-run on each data refresh

The key insight: Power Query records your transformations as a script. When the source data changes, you click **Refresh** and the same steps run again. No more copy-pasting in Excel.

> **Why Power Query matters for DAX:** 80% of "DAX problems" are actually data model problems. If your data types are wrong, your relationships are misconfigured, or your table structure doesn't match the star schema pattern, no amount of DAX will produce correct results. Power Query is where you prevent these issues.

## Connecting to data

In Power BI Desktop, click **Get Data** and choose your source. Common options:

| Source | Use case | Watch out for |
|--------|----------|---------------|
| Excel workbook | Prototyping, small reference tables | Merged cells, multiple sheets, hidden columns |
| SQL Server / PostgreSQL | Production data warehouses | Write a SQL query instead of loading raw tables — faster and more maintainable |
| SharePoint folder | Combining multiple files dropped in a shared folder | File naming conventions matter for sorting |
| Web | Scraping HTML tables or calling REST APIs | API authentication and pagination need M code |
| Folder | Combining all CSV/Excel files in a local folder | Use "Combine Files" button — handles schema changes automatically |

After connecting, Power BI shows a preview window. Click **Transform Data** to open the Power Query Editor — not Load, unless the data is already model-ready (rarely the case).

## Core transformations

The Power Query Editor ribbon has dozens of transformations. The 80/20 — the ones you'll use daily:

**1. Remove columns.** Right-click a column header → Remove. Or select several and choose Remove Columns. Models bloat fast; keep only what the report needs. Every column you load consumes memory in the VertiPaq engine — removing unused columns is the easiest performance win.

**2. Change data types.** Click the icon next to a column name. Power Query auto-detects types on import but **always verify** — `Decimal Number` vs `Whole Number` vs `Text` matters for DAX later. A common bug: revenue stored as text because the source had a currency symbol, causing `SUM` to return BLANK.

**3. Filter rows.** Use the dropdown on any column header, identical to Excel's autofilter. To remove blanks: dropdown → (null) → uncheck. Filter early to reduce the data loaded into the model.

**4. Split columns.** Right-click → Split Column → By Delimiter. Split `"Smith, John"` into two columns on the comma. Also useful for extracting IDs from composite keys.

**5. Unpivot.** Select columns → Transform tab → Unpivot Columns. Converts wide tables (Jan, Feb, Mar as separate columns) into tall tables (one Date column, one Value column) — the format Power BI prefers. This is essential for time-series data that arrives in Excel's cross-tab format.

**6. Merge queries.** Home tab → Merge Queries. The Power BI equivalent of SQL JOIN — combine two tables on a matching key. Choose the join kind carefully (Left Outer, Inner, Full Outer, etc.).

**7. Append queries.** Stack tables vertically — useful for combining monthly files with identical structure. The "Append Queries as New" option creates a new table that combines multiple sources.

**8. Replace values.** Right-click a column → Replace Values. Useful for standardizing inconsistent labels ("USA", "U.S.", "United States" → "United States").

## Real scenario: cleaning a messy sales export

Let's walk through a realistic data cleaning pipeline. You receive a monthly sales Excel file that looks like this:

| Region | Product | Jan | Feb | Mar | Salesperson |
|--------|---------|-----|-----|-----|-------------|
| EMEA | Widget A | $1,200 | $1,500 | $1,800 | Smith, John |
| APAC | Widget B | $900 | (null) | $1,100 | Lee, Maria |

Problems to fix in Power Query:

1. **Revenue columns are text** (because of the `$` symbol) → Change type to Currency
2. **Months are in columns** (wide format) → Select Jan/Feb/Mar columns → Unpivot → creates `Attribute` (month) and `Value` (revenue) columns
3. **Null values** in Feb → Replace with 0 or leave as null (depends on business logic)
4. **Salesperson name format** → Split on comma → creates Last Name and First Name columns
5. **Rename columns** → `Attribute` → `Month`, `Value` → `Revenue`

After these steps, your table looks like this:

| Region | Product | Month | Revenue | Last Name | First Name |
|--------|---------|-------|---------|-----------|------------|
| EMEA | Widget A | Jan | 1200 | Smith | John |
| EMEA | Widget A | Feb | 1500 | Smith | John |
| EMEA | Widget A | Mar | 1800 | Smith | John |
| APAC | Widget B | Jan | 900 | Lee | Maria |
| APAC | Widget B | Mar | 1100 | Lee | Maria |

This tall format is what Power BI wants. Now you can build a date table, create relationships, and write time intelligence measures without fighting the data structure.

## The M language (peek under the hood)

Every click in the Power Query Editor generates **M** code. Click **Advanced Editor** on the Home tab to see it. Here's the complete query for the scenario above:

```text
let
    Source = Excel.Workbook(File.Contents("C:\Data\sales_monthly.xlsx"), null, true),
    Sheet = Source{[Item="Sheet1",Kind="Sheet"]}[Data],
    Typed = Table.TransformColumnTypes(Sheet, {
        {"Jan", Currency.Type},
        {"Feb", Currency.Type},
        {"Mar", Currency.Type}
    }),
    Unpivoted = Table.UnpivotOtherColumns(Typed, {"Region", "Product", "Salesperson"}, "Month", "Revenue"),
    SplitName = Table.SplitColumn(Unpivoted, "Salesperson", Splitter.SplitTextByDelimiter(", ", QuoteStyle.None), {"Last Name", "First Name"}),
    ReplacedNulls = Table.ReplaceValue(SplitName, null, 0, Replacer.ReplaceValue, {"Revenue"}),
    Renamed = Table.RenameColumns(ReplacedNulls, {{"Month", "Month"}})
in
    Renamed
```

M is a **functional language** — every step is a function call chained together with `let ... in`. You don't need to write M by hand for 90% of tasks, but reading it helps you debug and customize.

> When the Power Query UI can't do something, M can. Common scenarios: dynamic file paths, conditional logic across columns, custom API pagination, complex string parsing.

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

Power Query's **query folding** can sometimes push filters down to the source (so the SQL database does the filtering before sending data), but never assume. When in doubt, filter early.

### How to check if query folding is working

Right-click any step in the Applied Steps pane → "View Native Query." If you see a SQL statement, query folding is working for that step. If the option is grayed out, folding broke at that step — common causes are:
- Adding a calculated column
- Using certain M functions (like `Table.Buffer`)
- Merging queries from different sources

When folding breaks, Power BI loads the entire source table into memory before filtering. For large databases, this can turn a 5-second refresh into a 5-minute refresh.

## Common mistakes that break DAX later

| Power Query mistake | What breaks in DAX | Fix |
|---------------------|--------------------|----|
| Not setting data types | `SUM` returns BLANK because text can't sum | Set types explicitly in Power Query, never rely on auto-detection |
| Loading unnecessary columns | Model bloats, refresh slows, relationships confuse | Remove columns you don't need for reporting |
| Keeping wide tables (months as columns) | Time intelligence measures fail | Unpivot to tall format |
| Not removing duplicate rows | Measures double-count | Use `Table.Distinct` or identify the true grain |
| Inconsistent labels ("USA" vs "United States") | Slicers show both, splitting the filter | Use `Table.ReplaceValue` to standardize |

## Refresh strategy

Once your query is loaded into the Power BI model:

1. **Manual refresh** — Click Refresh in Power BI Desktop or the Power BI Service.
2. **Scheduled refresh** — In the Power BI Service, configure a refresh schedule (up to 8x/day with Pro, 48x/day with Premium).
3. **Incremental refresh** — For large tables, define a date-based partition so only new data is loaded on each refresh. Configure via Power Query parameters `RangeStart` and `RangeEnd`.

For incremental refresh setup, see our [Power Query parameters guide](/tutorials/power-query-parameters-dynamic-sources).

## FAQ

**Should I transform in Power Query or DAX?**
Power Query for row-level transformations (cleaning, splitting, type conversion). DAX for aggregations and context-dependent calculations. If a value is the same regardless of filter context, do it in Power Query. If it changes based on what the user selects, use DAX.

**Does Power Query slow down my report?**
Power Query runs at refresh time, not query time. A complex Power Query pipeline slows your refresh but doesn't affect report interactivity. If your refresh is slow, check query folding and step ordering.

**Can I use Python or R in Power Query?**
Yes — both are supported as transformations. Use them for statistical analysis or ML scoring that M can't handle. Be aware that Python/R transformations break query folding.

## What's next

Power Query handles the "shape your data" phase. Once data lands in the model, the next step is designing relationships and the star schema — see [Star Schema Data Modeling](/tutorials/data-modeling-star-schema) for the deep dive. Pair a clean Power Query pipeline with a well-designed model and DAX becomes dramatically easier to write. For more advanced transformations, see our [Power Query common transformations guide](/tutorials/power-query-common-transformations).
