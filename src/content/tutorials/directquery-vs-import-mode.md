---
title: "DirectQuery vs Import Mode: Choosing the Right Power BI Storage Mode"
description: "Import Mode caches data in memory for fast queries, while DirectQuery sends every visual request back to the source database. Learn when to use each, how Dual mode works, and the performance trade-offs that determine your report architecture."
pubDate: 2026-07-26
category: "data-modeling"
difficulty: "Advanced"
tags: ["data-modeling", "directquery", "import-mode", "storage-mode", "performance"]
author: "Power BI Tutorials Team"
---

Every Power BI dataset uses a storage mode that determines how data is retrieved when a user interacts with a report. The choice between Import Mode and DirectQuery — or a hybrid of both — affects query speed, data freshness, source load, and the DAX functions available to you.

This guide covers the three storage modes, the decision criteria for choosing between them, how to configure hybrid models, and the common mistakes that turn a fast report into a slow one.

## The Three Storage Modes

### Import Mode

Import Mode copies data from the source into Power BI's in-memory engine (VertiPaq) at refresh time. All subsequent queries run against the in-memory copy.

**How it works:**
1. You connect to a data source and define which tables to import
2. Power BI loads the data into the VertiPaq columnar database
3. All DAX queries run against the in-memory copy
4. Data updates only when you refresh the dataset (scheduled or manual)

**Pros:**
- Fastest query performance (sub-second for most visuals)
- Full DAX function support
- Works offline (after initial refresh)
- Supports Power BI's full feature set (Q&A, Quick Insights, etc.)
- Aggregations and calculated tables work without limitations

**Cons:**
- Data is stale until the next refresh
- Memory size limited by your Power BI capacity (1 GB for Pro, 100 GB for P1)
- Refresh time grows with data volume
- Large models can be expensive to host

**When to use:** When data volume fits in memory and near-real-time data is not required. This is the right choice for most reporting scenarios.

### DirectQuery Mode

DirectQuery does not store any data. Every time a user interacts with a visual, Power BI generates a SQL query and sends it to the source database in real time.

**How it works:**
1. You connect to a supported data source (SQL Server, Snowflake, etc.)
2. Power BI stores only the table metadata and relationships
3. Each visual interaction generates a native SQL query
4. The source database executes the query and returns results

**Pros:**
- Real-time data (no staleness)
- No data stored in Power BI (useful for compliance/security)
- Handles large datasets that exceed memory limits
- Single source of truth (no sync issues)

**Cons:**
- Query performance depends on the source database
- Limited DAX functions (some time intelligence and statistical functions not supported)
- No calculated tables
- Concurrent users can overload the source database
- Some Power BI features unavailable (Q&A, Quick Insights)

**When to use:** When you need real-time data, when data volume exceeds memory limits, or when security policies prohibit data extraction.

### Dual Mode

Dual Mode stores a table in memory (like Import) but can also fall back to DirectQuery when needed. Tables set to Dual mode act as a bridge between Import and DirectQuery tables in a hybrid model.

**Primary use case:** Dimension tables in a star schema where fact tables use DirectQuery. Setting dimension tables to Dual allows them to participate in both Import and DirectQuery relationships without breaking the model. See our [star schema guide](/tutorials/data-modeling-star-schema/) for dimension/fact table patterns.

## Decision Matrix

| Criterion | Import | DirectQuery | Dual |
|-----------|--------|-------------|------|
| Query speed | ⚡ Fastest | 🐌 Depends on source | ⚡ Fast for bridging |
| Data freshness | Stale until refresh | Real-time | Mixed |
| Max data size | Memory-limited | Source-limited | Memory-limited |
| DAX support | Full | Partial | Full |
| Source DB load | Low (only at refresh) | High (every query) | Medium |
| Setup complexity | Low | Medium | High |
| Best for | Most reports | Real-time / very large | Hybrid models |

## Configuring a Hybrid Model

In many real-world scenarios, you want both: fast performance for historical data and real-time access for recent transactions. Power BI supports this through hybrid models.

**Step 1 — Set fact tables to DirectQuery:**
In Power BI Desktop, open **Model** view → select the fact table → **Properties** → **Advanced** → **Storage mode** → **DirectQuery**.

**Step 2 — Set dimension tables to Dual:**
Select each dimension table → **Storage mode** → **Dual**.

**Step 3 — Configure aggregations (optional but recommended):**
Create aggregation tables that pre-summarize fact data at common grouping levels. Power BI will use the aggregation (Import Mode, fast) when a query matches the aggregation pattern, and fall back to DirectQuery only for queries that need detail-level data.

```dax
-- Aggregation table example: daily sales summary
Daily Sales Agg = 
SUMMARIZE(
    'Sales',
    'Date'[Date],
    'Product'[Category],
    "Total Sales", SUM('Sales'[Amount]),
    "Total Quantity", SUM('Sales'[Qty])
)
```

Set the aggregation table to Import Mode, then use the **Manage aggregations** dialog to map it to the DirectQuery fact table.

**Step 4 — Set up incremental refresh:**
For Import tables in the hybrid model, configure incremental refresh to only load new data rather than full reloads. See our guide on calculated tables and parameters for [what-if parameters and calculated tables](/tutorials/calculated-tables-what-if-parameters/) that can help with refresh configuration.

## Performance Implications

### Import Mode Performance
VertiPaq compresses data at 3:1 to 10:1 ratios. A 1 GB source table typically becomes 100-300 MB in memory. Query performance is driven by:
- Number of columns (more = slower, because VertiPaq is columnar)
- Cardinality of columns (high cardinality = more memory)
- Data model design (fewer, wider tables are better than many narrow ones)

### DirectQuery Performance
Every visual generates SQL. A report with 10 visuals on a page generates 10 simultaneous queries. Performance depends entirely on:
- Source database speed (indexes, partitions, query optimizer)
- Query complexity (DAX is translated to SQL — complex DAX = complex SQL)
- Number of concurrent users
- Network latency between Power BI and the source

**DirectQuery best practices:**
- Add a date/time filter to every page (limits query range)
- Avoid high-cardinality visuals (don't put 1M rows in a table visual)
- Limit visuals per page (5-7 maximum)
- Use the Performance Analyzer to identify slow queries

### Hybrid Model Performance
The key to hybrid performance is the aggregation table. Without it, DirectQuery tables will dominate query time because every query falls through to the source. With properly designed aggregations, 80-90% of queries hit the in-memory aggregation table, and only detailed drill-downs use DirectQuery.

## Common Mistakes

### 1. Using DirectQuery to Avoid Data Modeling
```
❌ Connecting DirectQuery to a raw transactional table with 50 columns and no aggregation
✅ Create an aggregation table in Import Mode, use DirectQuery only for drill-through
```

DirectQuery is not a substitute for proper data modeling. If your report is slow under DirectQuery, the problem is likely in the data model or the source query, not in Power BI.

### 2. Mixing Storage Modes Incorrectly
```
❌ Fact table = Import, Dimension table = DirectQuery
   → This forces DirectQuery for every join, killing performance

✅ Fact table = DirectQuery, Dimension table = Dual
   → Dimension table is in-memory for fast joins, fact table hits source only when needed
```

### 3. Forgetting That Some DAX Functions Don't Work in DirectQuery
DirectQuery does not support all DAX functions. Common unsupported functions include:
- Some time intelligence functions (limited support)
- `PATH()` and parent-child functions
- Certain statistical functions
- Calculated tables (not available at all)

**Check:** The Power BI Desktop will show a warning if you use an unsupported function in a DirectQuery measure. Do not ignore these warnings.

### 4. Not Setting Up Incremental Refresh for Import Tables
```
❌ Full refresh of 5 years of data every hour → 20-minute refresh cycle
✅ Incremental refresh: only load new daily data → 30-second refresh cycle
```

Incremental refresh is configured using parameters named `RangeStart` and `RangeEnd`. See our [Power BI performance optimization](/tutorials/power-bi-performance-optimization/) guide for detailed refresh strategies.

## FAQ

**Q: Can I change a table's storage mode after building the report?**

Yes, but it can break relationships and measures. In Power BI Desktop, go to Model view → select the table → Properties → Advanced → Storage mode. Be aware that changing from Import to DirectQuery will remove all calculated columns and calculated tables on that table.

**Q: How many concurrent users can DirectQuery handle?**

It depends entirely on the source database. SQL Server can handle hundreds of concurrent queries if properly tuned. A small PostgreSQL instance might struggle with 20. Test with realistic concurrent loads before deploying.

**Q: Does DirectQuery work with Excel files or CSV sources?**

No. DirectQuery requires a supported database source (SQL Server, Snowflake, Oracle, PostgreSQL, etc.). File-based sources like Excel, CSV, and SharePoint lists only support Import Mode.

**Q: Can I use Row-Level Security with DirectQuery?**

Yes. RLS works with both Import and DirectQuery. In DirectQuery, RLS filters are pushed down to the source database as WHERE clauses. See our [Row-Level Security guide](/tutorials/power-bi-row-level-security/) for implementation details.

**Q: What is the recommended refresh frequency for Import Mode?**

For most business reports, 8 times per day (every 3 hours) is sufficient. For operational dashboards, hourly refreshes may be needed. Power BI Pro allows 8 scheduled refreshes per day; Premium allows 48. For more frequent updates, consider DirectQuery or Streaming Datasets.

## What's Next

- Build the star schema that works with any storage mode: [Data modeling star schema](/tutorials/data-modeling-star-schema/)
- Understand relationships that cross storage modes: [One-to-many and many-to-many](/tutorials/relationships-one-to-many-many-to-many/)
- Optimize your model for fast queries: [Power BI performance optimization](/tutorials/power-bi-performance-optimization/)
- Secure your model: [Power BI Row-Level Security](/tutorials/power-bi-row-level-security/)
