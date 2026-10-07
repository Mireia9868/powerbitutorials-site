---
title: "Import and Transform Excel Data with Power Query"
description: "Excel remains the most common starting point for Power BI projects."
pubDate: 2026-10-07
category: power-query
tags: ["excel", "power query"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Excel remains the most common starting point for Power BI projects. Most analysts have data sitting in `.xlsx` files on a network share, in a SharePoint library, or attached to an email, and the first real task in any report is getting that data into a clean shape. Power Query is the engine that does this work, and it is the same engine whether you are using Power BI Desktop, Excel's own Get & Transform, or a Dataflow in the Power BI Service.

This tutorial walks through the full path: connecting to a workbook, choosing the right container object, cleaning columns with the standard transformations, and writing a query that survives the next time someone saves over the source file. It stays at beginner level, but the details matter, so the steps are explicit.

## Why Power Query beats copying and pasting

When you paste a range of cells into Power BI, you get a static snapshot. If the source changes, your report does not. Power Query builds a repeatable recipe instead: it records each step as a named transformation, and every time the data refreshes, Power BI replays the recipe against the current file.

Three practical consequences:

- **Repeatability.** The same transforms run on every refresh. No drifting formatting.
- **Auditability.** The Applied Steps pane lists exactly what happened to the data, in order.
- **Reusability.** Once a query is clean, you can duplicate it, parameterise it, or promote it to a Dataflow that other reports consume.

The trade-off is that Power Query operates on a load step, not on live cells. It reads a snapshot of the file at refresh time, so you cannot have a measure that reacts to an unsaved edit in Excel.

## Connecting to a workbook

In Power BI Desktop, go to **Home > Get data > Excel workbook**, or use **Data > Get data > Excel workbook** on the ribbon if the Home tab is collapsed. Pick the file, then choose the object to load.

### Table vs Worksheet vs Named Range

The Navigator dialog shows the internal objects of the workbook. The distinction matters more than most beginners expect.

| Object | What Power Query returns | When to use |
|---|---|---|
| Table | A named Excel table (`ListObject`) with headers | Preferred. Structure is stable, blanks at the top are rare |
| Worksheet | The used range of the sheet, with the first row promoted as headers | When the source is a flat grid with no table object |
| Named Range | The cells behind a defined name | Reporting templates where a name points at a fixed block |
| Workbook | All of the above as a folder-like container | Rarely; leads to accidental duplicate loads |

Always prefer a Table. A worksheet's used range can shift if someone adds a note two rows below the data, and Power Query will happily include it as a new row of values mixed into your numeric column.

Select the object, then click **Transform Data** rather than **Load**. Transform Data opens the Power Query Editor, where you shape the query before anything lands in the model.

## A worked example

Assume a workbook called `SalesData.xlsx` with a table named `tblSales` containing columns: `OrderID`, `OrderDate`, `Region`, `Product`, `Units`, `UnitPrice`. Some regions are typed inconsistently (`north`, `North `, `NORTH`), and `UnitPrice` sometimes arrives as text because of a stray currency symbol.

The generated query after connecting will look close to this:

```powerquery
let
    Source = Excel.Workbook(File.Contents("C:\Data\SalesData.xlsx"), null, true),
    tblSales_Table = Source{[Item="tblSales",Kind="Table"]}[Data],
    ChangedTypes = Table.TransformColumnTypes(tblSales_Table, {
        {"OrderID", Int64.Type},
        {"OrderDate", type date},
        {"Region", type text},
        {"Product", type text},
        {"Units", Int64.Type},
        {"UnitPrice", type number}
    }),
    CleanedRegion = Table.TransformColumns(ChangedTypes, {
        {"Region", each Text.Proper(Text.Trim(_)), type text}
    }),
    RemovedBlankRows = Table.SelectRows(CleanedRegion, each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null})))
in
    RemovedBlankRows
```

A few notes on the code above, since the shape is what causes most beginner friction.

`Excel.Workbook` is the raw function behind the connector. It returns a navigation table with one row per object in the file, which is why the second step drills into the row where `Item` equals `tblSales` and `Kind` equals `Table`. If you rename the table in Excel, this step breaks and the query fails with a `"tblSales" wasn't found` style error. That is a feature, not a bug: it tells you the source changed shape.

`Table.TransformColumnTypes` sets the type for each column in one pass. Setting types early, before you add custom columns, avoids the situation where a downstream step works on the wrong type and silently drops values.

`Text.Proper(Text.Trim(_))` normalises the region. Note the underscore: inside `Table.TransformColumns`, `_` is the current value of the column being processed. Without `Text.Trim`, `" north "` becomes `" North "`.

`Table.SelectRows` with `Record.FieldValues(_)` is a compact way to drop rows where every field is empty. If your table has a key column that is never blank, a simpler `each [OrderID] <> null` is easier to read and faster.

## Common transformations you will actually use

The Applied Steps pane records everything, so you can always delete a step and reapply. The transformations below cover the large majority of Excel cleanup work.

**Promote headers.** When a worksheet arrives with the first row as data, right-click the first row and choose *Use First Row as Headers*. If the headers are on the second or third row, use **Home > Remove Rows > Remove Top Rows** until they align.

**Remove empty rows and columns.** **Home > Remove Rows > Remove Empty Rows** handles rows that contain nothing. For columns, right-click a column header and choose *Remove Empty* only if you are sure the column is genuinely unused; it checks whether every value is null, not whether every value is blank text.

**Unpivot columns.** Excel reports often arrive in a wide layout with months or years as column headers. Select the columns that identify a row (say `Product`), then **Transform > Unpivot Other Columns**. You get a tidy long table with an `Attribute` column and a `Value` column, which is what a star schema wants downstairs.

**Split a column.** **Transform > Split Column > By Delimiter** is useful when a field like `"North|Q1"` needs decomposing. Use *Each occurrence of the delimiter* when a value may contain the delimiter more than once, and *Left-most delimiter* when you only want the first piece.

**Merge queries instead of using VLOOKUP.** Bring the lookup table in as its own query and use **Home > Merge Queries**. The result is a real join that refreshes with the model, rather than a formula that needs to be dragged down. The related article on merge vs append covers the distinction between joins (`merge`) and stacking (`append`).

**Group and aggregate.** **Transform > Group By** can do sums, counts, and even `All Rows` for a nested table. For a beginner, summing `Units` by `Region` here is often cleaner than doing it in DAX later, but be careful: pre-aggregating removes the detail needed for slicing by date or product.

## Parameters and refresh safety

Hard-coding a file path in `File.Contents` is fine for a personal report and terrible for anything shared. Convert the path into a parameter: **Home > Manage Parameters > New Parameter**, name it `SourceFile`, type Text, and give it the full path. Then edit the first step of the query and replace the literal string with `SourceFile`.

For a folder of identically shaped workbooks, use **Get data > Folder** and let Power Query combine the files. The generated `Transform File from <folder>` function handles the iteration; you point it at a folder and it reads every `.xlsx` inside. The parameters dialog is the right place to define the folder path.

Two settings worth checking before you publish:

- **Privacy levels.** If a query combines Excel with a web source, Power BI may refuse to combine data unless privacy levels are set correctly. **File > Options > Current File > Privacy** controls this. The safe default for local files is *Combine data according to your Privacy Level settings for each source* with levels set to *Organizational* or *Private*.
- **Data source credentials.** After publishing to the Service, open **Settings** on the dataset and supply credentials for the Excel file, especially if it lives on SharePoint or OneDrive. Without them, scheduled refreshes fail with an authentication error.

## Load settings and closing the loop

When you click **Close & Apply**, Power Query asks how the query should behave in the model. The default is *Load*, which writes the data into the in-memory model. Some queries should not be loaded: staging queries you only use as a source for a merge, lookup tables that never appear in a visual, and debug queries. In those cases choose **Close & Apply > Connection only** from the dropdown next to Close & Apply.

Type detection and column quality settings affect what you see in the editor but not what loads. The **Column Quality**, **Column Distribution**, and **Column Profile** toggles show, in the status bar, how many distinct and unique values exist and how many errors are present. Turn on **Column Profile** for the whole dataset under the View tab, not just the first 1,000 rows, when you are investigating a type conversion problem.

If your model is going to be large, consider whether the Excel source should be a one-off import or whether the report should read directly via DirectQuery. DirectQuery against Excel is not supported, so the choice is really import vs reading the workbook through a gateway. Import mode is almost always the right call for Excel sources; the DirectQuery vs import mode article explains when that changes.

## Frequently asked questions

### Q: Why does the file path in Power Query break after I move the workbook?

`File.Contents` stores an absolute path. Move or rename the file and the query points at nothing. The fix is to use a parameter, or store the workbook in a SharePoint or OneDrive library and connect via the SharePoint Folder connector, which uses a stable URL. Excel Online files refreshed through the Service can also use `Web.Contents` against the workbook URL with the correct permissions.

### Q: Can I edit the original Excel file while Power BI is open?

Yes, but the change is only picked up on refresh. Power Query reads the file at refresh time; it does not watch the file on disk. If the workbook is open in Excel with an unsaved buffer, Power Query may still read the last saved version. Save before refreshing.

### Q: What happens if a column name changes in the source workbook?

The step that references the old name fails, and the query shows an error step with a message naming the missing column. In the Applied Steps pane you can click the failing step, fix the reference in the formula bar, and continue. If the data is being refreshed automatically, consider adding a step that renames columns to stable names early, so downstream steps do not care what the source header said.

### Q: How do I combine several worksheets in one workbook that all have the same layout?

Connect to the Workbook container once, filter the navigation table to the sheets you want (for example by a naming prefix), remove the other columns, and then expand the `Data` column. Power Query will combine them into a single table. Keep the `Name` column from the navigation table if you want to know which sheet each row came from, and rename it to `SourceSheet`.

### Q: Is Power Query in Excel the same as in Power BI?

The engine is the same M language, and the transformation steps behave identically. The differences are in the output: Excel loads into a worksheet table or the Data Model, while Power BI loads into the model behind the report. Query code you write in Excel can be copied into Power BI's Advanced Editor and will usually run without changes.

## Related Reading

- [Power BI Excel Integration: A Practical Guide](/tutorials/power-bi-excel-integration/)
- [Merge vs Append Queries in Power Query](/tutorials/merge-vs-append-queries/)
- [DirectQuery vs Import Mode: Choosing the Right Storage Mode](/tutorials/directquery-vs-import-mode/)
- [Designing a Star Schema for Power BI](/tutorials/data-modeling-star-schema/)
- [Common Power BI Mistakes Beginners Make](/tutorials/power-bi-common-mistakes-beginners/)
- [DAX Basics: A Beginner's Guide](/tutorials/dax-basics/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX EARLIER Function: When and Why It Exists](/tutorials/dax-earlier-function/)
