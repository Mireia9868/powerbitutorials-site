---
title: "Power Query Parameters: Build Dynamic, Reusable Data Sources"
description: "Parameters let you control Power Query behavior without editing the M code — swap environments, change date ranges, or toggle between production and test data with a dropdown. This guide covers creating parameters, using them in queries, and the pattern for environment switching."
pubDate: 2026-07-18
category: "power-query"
difficulty: "Intermediate"
tags: ["power-query", "parameters", "dynamic-sources", "environment-switching", "m"]
author: "Power BI Tutorials Team"
featured: false
---

Hardcoding server names, file paths, and date ranges in Power Query works — until you need to switch from a development database to production, or change a reporting period. Parameters solve this by externalizing values into a manageable dropdown. This guide covers the fundamentals and the three patterns where parameters shine.

## What is a parameter?

A parameter is a named value that lives outside your query. You create it once, reference it in any query, and change it from a single place. In Power BI Desktop, parameters appear under **Home → Manage Parameters**.

Parameters support these data types:
- Text
- Date / DateTime
- Decimal Number / Whole Number
- True/False
- Any (untyped)

## Creating a parameter

In Power Query Editor:

1. **Home → Manage Parameters → New Parameter**
2. Name it (e.g., `ServerName`)
3. Set the type (`Text`)
4. Add suggested values (optional — a list of allowed values for a dropdown)
5. Set the current value
6. Click OK

The parameter now appears in the Queries pane and can be referenced in any query as `ServerName` (no quotes — it's a variable, not a string).

## Pattern 1: Dynamic data source

The classic use case — switch between dev and prod databases without editing M code.

**Step 1:** Create a text parameter `Environment` with allowed values `["DEV", "PROD"]`.

**Step 2:** Create a parameter `ServerName` that derives from `Environment`:

```m
ServerName =
    if Environment = "DEV" then "dev-sql.company.local"
    else if Environment = "PROD" then "prod-sql.company.local"
    else error "Unknown environment"
```

**Step 3:** Use `ServerName` in your source query:

```m
let
    Source = Sql.Database(ServerName, "SalesDB"),
    SalesTable = Source{[Schema="dbo", Item="Sales"]}[Data]
in
    SalesTable
```

Now changing `Environment` from `DEV` to `PROD` redirects every query that uses `ServerName`. No code edits, no risk of forgetting to update one of twenty queries.

## Pattern 2: Date range filtering

Parameters let users control the reporting window without editing queries.

**Step 1:** Create a `StartDate` parameter (type `Date`) and an `EndDate` parameter (type `Date`).

**Step 2:** In your query, filter by the parameter values:

```m
let
    Source = Sql.Database(ServerName, "SalesDB"),
    Sales = Source{[Schema="dbo", Item="Sales"]}[Data],
    Filtered = Table.SelectRows(Sales, each [OrderDate] >= StartDate and [OrderDate] <= EndDate)
in
    Filtered
```

**Tip:** For date parameters, use "Suggested Values" with a query that returns recent dates — this gives users a dropdown of valid options instead of typing.

## Pattern 3: File path parameterization

When reading files from a folder, parameterize the path so different environments can point to different network drives.

```m
let
    // FilePath is a text parameter, e.g., "\\prod-server\reports\"
    Source = Folder.Files(FilePath),
    FilteredCSVs = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv")),
    Result = FilteredCSVs
in
    Result
```

This is especially useful when moving a report from a developer's local machine to a shared server.

## Using parameters in the Power BI Service

Parameters become even more powerful after publishing to the Power BI Service. In a dataset's Settings, you can:

1. **Change parameter values** without opening Power BI Desktop.
2. **Create multiple parameter sets** for different environments (dev / test / prod).
3. **Automate parameter changes** via the Power BI REST API or Power Automate.

This means a single `.pbix` file can serve multiple environments — publish once, configure parameters per workspace.

## Common mistakes

**Mistake 1: Parameterizing values that should be hardcoded.** Don't parameterize table names or column names — these rarely change and parameterizing them makes the query fragile. Parameterize *connection strings*, *file paths*, and *filter thresholds* — values that genuinely vary by environment.

**Mistake 2: Forgetting to update parameters after publishing.** If you change a parameter in Power BI Desktop and republish, the Service retains its previous parameter values by default. Check the dataset settings after republishing.

**Mistake 3: Using parameters for values that change per user.** Parameters are dataset-level — they apply to everyone viewing the report. For per-user filtering (like "show only my region"), use row-level security (RLS) instead.

## Performance note

Parameters are resolved at query refresh time, not at query execution time. This means:

- A parameterized source query refreshes correctly when the parameter changes.
- But a parameterized *filter* (like `StartDate`) filters at the source — good for performance because less data is loaded.
- If you parameterize a filter that could be done in DAX instead, consider whether the parameter is worth the added complexity. DAX filters respond to slicers dynamically; parameter filters require a refresh.

## Summary

Parameters externalize values that vary by environment or reporting period. Use them for server names, file paths, date ranges, and environment switching. Avoid parameterizing table names or per-user values. When published to the Power BI Service, parameters let a single dataset serve multiple environments — a powerful pattern for managing dev/test/prod lifecycles.
