---
title: "Append Queries in Power Query: Combine Files Easily"
description: "Appending stacks tables with the same shape: a January table and a February table become one. Column matching and failure modes."
pubDate: 2026-10-12
category: power-query
tags: ["power query", "append"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

## What Appending Actually Does

Appending queries stacks rows on top of each other. If you have a January sales table and a February sales table with the same columns, appending produces one table with both months. The column count stays the same; the row count grows.

This is the essential difference from merging. Merging joins tables side by side by matching a key column and adds new columns. Appending adds new rows and keeps the existing columns. A common beginner mistake is reaching for merge when the task is really "I have twelve monthly exports and I want one table" — that is an append job.

Three situations call for append:

- Monthly, quarterly, or yearly files with identical structure that need to become one fact table.
- Multiple regions, departments, or entities sending the same report layout.
- Historical data plus a current extract that share a schema.

The prerequisite is aligned columns. Power Query matches columns by name, not position. If the January file calls a column `Sales` and the February file calls it `Revenue`, appending creates two separate columns and fills the mismatched rows with nulls. Fix the names before you append.

## Step 1: Load the Source Queries

Start with each source as its own query. Use **Data > Get Data** for each file, folder, or database table.

For two CSV files, the generated queries look like this:

```powerquery
let
    Source = Csv.Document(File.Contents("C:\Data\Sales_Jan.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"Date", type date}, {"Region", type text}, {"Product", type text}, {"Sales", type number}})
in
    ChangedTypes
```

Give each query a clear name in the Queries pane — `Sales_Jan`, `Sales_Feb`, and so on. Do the cleansing per query first: promote headers, set data types, remove junk rows, trim text. Cleaning before appending means you fix a column once instead of in the combined output.

## Step 2: Run the Append

With one query selected, go to **Home > Append Queries**. The dialog offers two modes.

**Two tables** appends the currently selected query with one other query you pick from a dropdown.

**Three or more tables** lets you add any number of queries to the list. Use this for a stack of monthly files — one operation rather than chaining appends.

Click OK. Power Query creates a new query named `Append1` (or similar) whose only step is the append. Rename it to something meaningful like `Sales_Combined`.

The generated M code for appending two queries is:

```powerquery
let
    Source = Table.Combine({Sales_Jan, Sales_Feb})
in
    Source
```

`Table.Combine` is the function underneath the button. If you are appending a dynamic list of queries, you pass a list built at runtime:

```powerquery
let
    Source = Table.Combine({Sales_Jan, Sales_Feb, Sales_Mar, Sales_Apr})
in
    Source
```

The list must be a list of tables, not a list of query names as text. Referencing the query name directly resolves to its table value.

## Step 3: Understand Column Matching

`Table.Combine` aligns columns by name. `Table.Combine` keeps the union of all column names across the inputs. A row from a table that lacks a column gets null in that column. A column that exists in only one input survives with nulls everywhere else.

This matters because a null-filled column usually signals a naming mismatch, not missing data. Before appending, open each query and compare the column headers. Rename to a single convention. A quick check: the combined table's column count should equal the column count of a single source. If it is larger, something did not match.

You can inspect columns without loading by using the formula bar, or by reading the headers in the Queries pane preview.

## Step 4: Handle Type Differences

If January sets `Sales` to `type number` and February sets it to `type text`, the combined column carries the intersection. In practice you want consistent types. Apply the same `Table.TransformColumnTypes` step to every source query, or apply types once on the appended query as the final step. The safer pattern is to type each source, then let the append inherit the common type.

For a column that is `type date` in one source and `type datetime` in another, the append widens to `type datetime`. Convert both to `type date` beforehand if you want a clean date column.

## Step 5: Append Smarter with a Folder

If you have dozens of files, hand-building an append is tedious. Use **Get Data > Folder**, point at the directory, and Power Query produces a `Folder.Files` query, a `Transform Sample File` function, and an `Append` step automatically. The result is a single query that reads every file in the folder and combines them.

The core of that pattern is a custom function applied to each file, then combined:

```powerquery
let
    Source = Folder.Files("C:\Data\Sales"),
    Filtered = Table.SelectRows(Source, each [Extension] = ".csv"),
    AddContent = Table.AddColumn(Filtered, "Data", each Csv.Document([Content], [Delimiter=","])),
    Combined = Table.Combine(AddContent[Data])
in
    Combined
```

For this to work, every file must share the same column layout. One rogue file with a different header produces null columns across the whole result.

## Verifying the Append

Check the row count. If January has 1,000 rows and February has 900, the append should have 1,900. A number that is too low usually means a filter inside a source query is dropping rows unintentionally. A number that is too high usually means duplicate loading — you appended a query that was itself already an append.

Also check for duplicate dates if you re-run the source. Appending a refreshed monthly file to a historical table that already contains that month duplicates rows. Make the source query filter to the new period only, or build a folder-based query that always reads the complete set.

## Common Problems

**Mismatched headers create extra columns.** Rename all sources to match before appending. Use the same case and spacing; Power Query treats `Sales` and `sales` as different names.

**Data types conflict and values turn to error or null.** Set types per source so the combined column has one consistent type.

**New columns appear over time.** If February adds a `Channel` column that January lacks, January rows get null there. That is expected and fine, but document it.

**Appending a lot of queries slows refresh.** The query folding status matters. If the sources are database tables and the append folds to a single SQL `UNION ALL`, it is efficient. If folding breaks early, Power Query materializes each table first. Keep transformations foldable where possible.

**The preview looks right but the loaded table is stale.** Click **Refresh Preview** in the editor, then **Close & Apply** to push changes to the model.

## Append vs Merge, in One Line

Append when the tables are the same shape and you want more rows. Merge when the tables are different shapes and you want more columns. If you are still deciding between them, review the difference carefully before building a relationship in the model, because getting this backwards creates a rectangular mess that no DAX measure can repair cleanly.

Once the combined query loads, relate it to your dimension tables. Appending without a star schema around it gives you a wide table that is hard to slice; appending into a proper fact table that joins to date, product, and region dimensions gives you the model structure you actually want.

### Q: What is the difference between append and merge in Power Query?

Append stacks rows from tables with the same columns, increasing row count. Merge joins columns from two tables by matching a key, increasing column count. Use append for monthly or regional files with identical layouts; use merge to bring a lookup table into a fact table.

### Q: Why did appending create extra columns with null values?

Power Query matches columns by name. If one source uses `Sales` and another uses `Revenue`, the combined table keeps both columns and fills the missing side with nulls. Rename columns to a single convention in each source query before appending.

### Q: Can I append more than two queries at once?

Yes. The Append Queries dialog offers a "Three or more tables" option where you add any number of queries to a list. Under the hood it calls `Table.Combine` with a list of tables, so you can also write that function manually for full control.

### Q: Does appending in Power Query affect query folding?

It can. When sources are database tables and the transformations stay simple, `Table.Combine` folds to a `UNION ALL` and runs server-side. If earlier steps break folding, each table is materialized first and combined locally, which slows refresh on large datasets.

### Q: How do I append files from a folder without naming each one?

Use **Get Data > Folder**. Power Query reads the directory, applies a transformation function to each file, and combines the results. This is the standard pattern for dozens of monthly exports that share the same column structure.

### Q: Why does my appended table have fewer rows than expected?

A filter inside one of the source queries is likely removing rows, or a source failed to load entirely. Compare the row count of each source query with the combined result and check that every expected table is present in the append list.

Behaviour described here follows [Microsoft's Append queries documentation](https://learn.microsoft.com/en-us/power-query/append-queries).

## Related Reading

- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Power Query Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
- [Data Modeling Star Schema](/tutorials/data-modeling-star-schema/)
- [Power BI Excel Integration](/tutorials/power-bi-excel-integration/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX Basics](/tutorials/dax-basics/)

- [Unpivot in Power Query: Turn a Wide Table into a Long Table the Right Way](/tutorials/power-query-unpivot/)
- [Merge Queries in Power Query (VLOOKUP Equivalent)](/tutorials/power-query-merge-queries/)