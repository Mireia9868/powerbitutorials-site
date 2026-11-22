---
title: "Convert Power Query to Power BI: Load, Transform, Refresh"
description: "Convert Power Query to Power BI: move M code, load queries into the model, set refresh, and avoid the errors that break a query after migration."
pubDate: 2026-11-23
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "migration", "excel", "data-loading"]
author: Mireia
featured: false
draft: false
---

The best way to convert Power Query to Power BI depends on where your queries live today. If they are in an Excel workbook, you can either load the workbook as a source or copy the M code into Power BI Desktop. If they already run in Power BI but point at the wrong source, you only need to change the source step. This guide covers all three cases, then the refresh setup that keeps the result working after you close the file.

## Case 1: Queries in an Excel workbook

You have a workbook with queries built in **Data → Get & Transform**. You want the same tables in a Power BI report.

**Option A — load the workbook directly.** In Power BI Desktop choose **Get Data → Excel workbook** and select the file. The Navigator shows the sheets, tables, and named ranges. If your queries loaded to worksheet tables, select those tables. This is the fastest path, but the transformation steps stay in Excel: Power BI only sees the output table.

**Option B — move the query code.** Open the Advanced Editor in Excel (Power Query Editor → View → Advanced Editor), copy the entire M expression, then in Power BI Desktop open **Get Data → Blank Query** and paste it into the Advanced Editor. The steps come across exactly, including types, merges, and custom columns. Rename the query and click **Close & Apply**. This is the real conversion: the M code itself is identical in both products because the engine is the same.

Two things to check after pasting:

1. **Source paths.** An Excel query that reads `C:\Users\me\data\sales.xlsx` will look for that file on your machine. In Power BI Desktop it works locally, but it will fail in the Service. Use a parameter for the folder path, or move the file to OneDrive / SharePoint and reconnect with the SharePoint Folder connector.
2. **Credentials.** Power BI asks for credentials at the source step even if Excel remembered them. Re-enter them once in **Data source settings**.

## Case 2: Queries already in Power BI, wrong source

If a query was built against a local file and needs to move to a database (or from development to production), do not rebuild the steps. Change only the source line in the Advanced Editor.

For example, replace:

```m
Source = Excel.Workbook(File.Contents("C:\Data\sales.xlsx"), null, true)
```

with a SQL Server source:

```m
Source = Sql.Database(ServerName, DatabaseName)
```

Everything downstream that references `Source` keeps working as long as the column names match. If they differ, add one **Renamed Columns** step immediately after the source so the rest of the query does not need to change. Microsoft documents the available source functions in the [Power Query connectors reference](https://learn.microsoft.com/en-us/power-query/connectors/).

## Case 3: Excel data model to Power BI semantic model

If your workbook uses Power Pivot with a Data Model, the tables and relationships can be imported. In Power BI Desktop, **Get Data → Import from Excel workbook** gives you the option to import the entire data model. Measures written in DAX come across as measures. This path is useful for a one-time migration, but you should still rebuild the model using a star schema if the workbook grew organically — a flat model with ten lookup tables will refresh slowly in the Service.

## Set refresh after the conversion

Loading the queries is only half the migration. A report that refreshes on your laptop but not in the Service is not finished.

1. Publish the report to a workspace.
2. Open **Semantic model → Refresh**. If the source is a local file, refresh will fail: the Service has no access to your disk. Move the file to SharePoint, OneDrive for Business, or a gateway-connected database.
3. Configure **Scheduled refresh** with the right credentials. Personal gateways are required for on-premises sources; cloud sources such as SharePoint and SQL Azure do not need one.
4. Run a manual refresh in the Service and check that row counts match Desktop.

Microsoft's guide to [refreshing data in the Power BI Service](https://learn.microsoft.com/en-us/power-bi/connect-data/refresh-data) covers the gateway and credential setup in detail.

## Common conversion errors

- **"The file is in use"** — close the workbook in Excel before refreshing from Power BI Desktop.
- **"Column X not found"** — the source column was renamed. Fix the step that first references the old name.
- **"Query contains a reference to a local path"** — replace the absolute path with a parameter or a web connector.
- **Refresh works in Desktop, fails in Service** — almost always credentials or an unreachable local source. Check **Data source settings** and the gateway.

## FAQ

### Q: Is Power Query in Excel the same as Power Query in Power BI?

The engine and the M language are the same, so query steps behave identically. The output differs: Excel loads to a worksheet table or the Data Model, while Power BI loads to the model behind a report. Code copied from Excel's Advanced Editor normally runs unchanged in Power BI.

### Q: Can I just copy the M code from Excel into Power BI?

Yes. Open the Advanced Editor in both products, copy the full expression, paste it into a **Blank Query** in Power BI Desktop, and rename it. The only parts that usually need editing are the source path and credentials.

### Q: What is the best way to convert Power Query to Power BI for a workbook with twenty queries?

Copy each query's M code into a Blank Query, or use **Get Data → Excel workbook** if the queries only load to tables. For twenty queries, keep them in one group and define a folder-path parameter first, so you only change one value when the source moves.

### Q: Will my refresh keep working after I publish?

Only if the source is reachable from the Power BI Service. Local file paths break after publishing. Use SharePoint, OneDrive for Business, or an on-premises data gateway for local databases.

### Q: Do I need to install Power Query separately?

No. It is built into Power BI Desktop and Excel 2016 or later. The [Power Query documentation](https://learn.microsoft.com/en-us/power-query/) covers both.

## Related reading

- [Import and Transform Excel Data with Power Query](/tutorials/power-query-from-excel/)
- [Power BI Data Source Parameters: Setup in Power Query](/tutorials/power-query-parameters-dynamic-sources/)
- [Getting Started with Power Query in Power BI](/tutorials/power-query-getting-started/)
