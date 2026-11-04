---
title: "Incremental Refresh in Power BI: Setup and Gotchas"
description: "Incremental refresh splits a fact table into history and a hot window. How partitions are created, and the limits that change the design."
pubDate: 2026-10-11
updatedDate: 2026-11-04
category: data-modeling
tags: ["refresh", "performance"]
difficulty: Advanced
author: Mireia
featured: false
draft: false
---

## What Incremental Refresh Actually Does

Incremental refresh splits a large fact table into two logical halves: the part that never changes (historical partitions) and the part that can change (the current, hot window). When a scheduled refresh runs, Power BI re-reads and reloads only the recent window and leaves the frozen partitions alone. Partitions are the unit of parallel loading inside Power BI, so partitioning a 400-million-row sales table by month means a refresh touches a single month partition instead of the whole table.

The upside is measurable. Full refreshes scale linearly with total data volume. Incremental refreshes scale with window size, so a table with six years of history and a rolling ten-day refresh window reloads roughly the same amount of data every night whether there are ten million rows or ten billion.

Three things make this work: a `RangeStart` and `RangeEnd` filter in Power Query, a stored policy defining how far back to keep and refresh, and a source table that supports efficient filtering by date. Miss any one and the refresh either fails or silently reloads everything, which is the most common complaint about the feature.

Incremental refresh is only available in Power BI Premium, Premium Per User, Fabric capacities, and Power BI Embedded. On shared (Pro) capacity the policy UI stays visible but publishing drops the partition definitions and you get a single full partition. That licensing jump is the real cost of the feature — the [licence calculator](/tools/license-calculator/) shows what it adds for your team size.

## Step 1: Prepare the Source Table

The date column you filter on must be a real `datetime` or `date` type in the source, indexed, and monotonic with load order. The last condition matters: incremental refresh assumes new rows arrive with ever-increasing dates. If late-arriving facts can appear with old dates outside the refresh window, those rows will never load.

Best practice is to use a dedicated column rather than the business date. A common pattern is an audit timestamp set by the ETL process, or a surrogate load date. Using `OrderDate` for the range filter means a backdated order correction in March will be invisible to a refresh that only covers the current period.

For SQL Server and Azure SQL, an index on the range column turns the generated predicate into a seek instead of a scan. Without it, the gateway query runs against a full table scan every night and the performance gain disappears.

## Step 2: Add RangeStart and RangeEnd Parameters

In Power Query, open the editor and create two parameters named exactly `RangeStart` and `RangeEnd` (case sensitive). Type them as Date/Time. Leave their "Current Value" at any date; the service replaces these values at refresh time.

```powerquery
// Parameter definitions (in the Advanced Editor of the parameters query)
RangeStart = #datetime(2024, 1, 1, 0, 0, 0) meta [
    IsParameterQuery = true,
    Type = "DateTime",
    IsParameterQueryRequired = true
],
RangeEnd = #datetime(2024, 1, 11, 0, 0, 0) meta [
    IsParameterQuery = true,
    Type = "DateTime",
    IsParameterQueryRequired = true
]
```

Next, apply a filter on the fact table using both boundaries. The `>= RangeStart` and `< RangeEnd` pair is mandatory; a filter on only one parameter disables partitioning.

```powerquery
let
    Source = Sql.Database("server", "warehouse"),
    Sales = Source{[Schema = "dbo", Item = "FactSales"]}[Data],
    Filtered = Table.SelectRows(Sales, each
        [LoadDateTime] >= RangeStart and [LoadDateTime] < RangeEnd)
in
    Filtered
```

If the filter is written as a relative comparison against `DateTime.LocalNow()` or a hardcoded literal, the engine cannot infer the partition boundaries. It must reference the two parameters directly in a `Table.SelectRows` predicate.

## Step 3: Define the Policy in Desktop

Right-click the table in the Fields pane, choose **Incremental refresh**, and set two numbers:

- **Store rows in the last N periods** - total history kept in the model.
- **Refresh rows in the last M periods** - the mutable window reloaded each time.

A table with 5 years stored and 10 days refreshed yields 6 partitions including the "before" partition holding anything older than the stored range and the "after" partition holding future-dated rows. Only the refresh-window partitions are reprocessed; the others are skipped.

The date picker at the top chooses day, month, quarter, or year granularity. Monthly granularity on a daily-loading fact table means a full month reloads every night, which is fine for small monthly slices but wasteful for high-volume daily data.

There is also a "Detect data changes" option that uses a separate column and query to decide whether a partition needs reprocessing at all. It works well when the source has a reliable `LastModified` column, but it adds a probe query per partition and can slow refresh startup on tables with hundreds of partitions.

Publish the model. The partitioning only materialises once the dataset lands in a workspace backed by the required capacity.

## Step 4: Verify Partitions After Publish

Open the workspace, find the dataset, and use SQL Server Management Studio connected to the XMLA endpoint (`powerbi://api.powerbi.com/v1.0/myorg/<WorkspaceName>`) to list partitions. You should see partitions named `FactSales-2024-01`, `FactSales-2024-02`, and so on, plus `FactSales-before` and `FactSales-after`.

If you see only one partition, the cause is almost always one of these:

1. The workspace is on shared capacity.
2. The RangeStart/RangeEnd filter is missing from the table's applied steps.
3. A downstream step (merge, append, custom column) discards the filter and reconstructs the full table.

Point 3 catches a lot of people. A `Table.Combine` or a merge with a lookup table returns a new table, and if you inserted that step after the range filter, the partitioning hint is gone. Put the range filter as late as possible in the query, ideally as the final step applied to the fact table.

## Gotchas That Break Refreshes

**Timezone drift.** The service evaluates partition boundaries in UTC. If your `LoadDateTime` is stored in local time, a ten-day window can miss the newest day or double-process the oldest. Normalise the range column to UTC or set the source connection to UTC.

**Gateway credentials.** Incremental refresh needs the data source credentials refreshed on the gateway, and the gateway account needs read access to the same objects throughout the stored period. Switching to a service principal later can break partitions that were created under a personal account.

**Partition count explosion.** Monthly partitions over 20 years is 240 partitions per table. Add several fact tables and refresh planning time grows. Keep the stored window no longer than the business needs, and switch to yearly granularity for anything older than a couple of years.

**Schema changes.** Changing a column type or renaming a field in a query forces a metadata refresh. Existing partitions keep the old schema until they are reprocessed, and the model can end up with mismatched partition definitions. After any structural change, do a full refresh once.

**DirectQuery and live connections.** Incremental refresh works on Import and Dual-mode tables. A table set to DirectQuery is not partitioned, so the option has no effect.

**Dates in measures.** Time intelligence functions that use `DATESYTD` or `DATEADD` operate on the model's date table, not the source range filter. Keep the date table fully loaded and mark it as a date table so these functions stay correct even though the fact table is truncated.

```dax
-- Rolling 30-day revenue that stays valid across partition boundaries
Rolling 30 Day Revenue =
VAR MaxDate = MAX ( 'Date'[Date] )
VAR StartDate = MaxDate - 29
RETURN
    CALCULATE (
        [Total Revenue],
        'Date'[Date] >= StartDate && 'Date'[Date] <= MaxDate
    )
```

Because this measure filters the date table rather than the fact table, it works no matter how many partitions exist or which ones were refreshed last night. Partition pruning happens at the storage engine level, so the query touches only the needed partitions.

A final note for troubleshooting: refreshing a single partition from SSMS with `Process Data` isolates whether a failure is policy-related or data-related. If manual processing succeeds and scheduled refresh fails, the problem is almost always credentials or a boundary calculation, not the query.

### Q: Why is my incremental refresh reloading the entire table?

Check four things in order: the workspace capacity, the presence of both `RangeStart` and `RangeEnd` in a `Table.SelectRows` step on the fact table, the position of that step (it must not be bypassed by a merge or append), and whether the table is set to Import or Dual mode. Query folding also matters: if the source does not fold the range filter, the engine still partitions the model but reads the full source each time, which defeats the performance gain.

### Q: Can I use incremental refresh with a dataflow or a SharePoint list?

Dataflows Gen1 and Gen2 both support incremental refresh as a first-class feature, and the same parameter rules apply. SharePoint lists are a poor fit because they lack an indexed date column and the connector often fails to fold the range predicate, so every refresh downloads the full list before filtering. If you must use SharePoint, stage the data into a SQL table first.

### Q: What happens to old rows outside the stored window?

They are dropped from the model. The `before` partition is emptied on the next operation, so a report filtered to three years ago returns blanks. If you need unlimited history for audit or compliance, keep the stored window wide enough or archive the raw data outside Power BI and query it separately. There is no automatic rollup or summarisation of evicted rows.

### Q: How does incremental refresh interact with DirectQuery?

It does not. Partitioning is an Import-mode concept. A table in DirectQuery mode stores no data and issues SQL at query time, so partition definitions are ignored and the policy UI has no effect. Dual mode tables are partitioned because they hold an Import copy that the engine can slice.

### Q: Do I need to refresh the whole model after changing the policy?

Yes, run one full refresh per affected table after editing the stored or refresh window. Changing the window rewrites the partition boundaries, and Power BI does not backfill newly covered partitions automatically. The first refresh after a policy change is typically much longer than subsequent ones.

Behaviour described here follows [Microsoft's Incremental refresh documentation](https://learn.microsoft.com/en-us/power-bi/connect-data/incremental-refresh-overview).

## Related Reading

- [Star Schema Data Modeling](/tutorials/data-modeling-star-schema/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Power BI Date Table](/tutorials/power-bi-date-table/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
- [DAX Time Intelligence: YTD, QTD, MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)

- [VertiPaq Analyzer: Optimize Your Power BI Data Model](/tutorials/vertipaq-optimizer-power-bi/)
- [Power BI Licensing: Free vs Pro vs PPU vs Fabric](/tutorials/power-bi-licensing-explained/)
- [Scheduled Refresh Failed: Seven Causes and the Fix](/tutorials/scheduled-refresh-failed-gateway/)
