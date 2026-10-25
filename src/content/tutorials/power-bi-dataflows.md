---
title: "Power BI Dataflows Explained (vs Datasets)"
description: "Dataflows and datasets are both storage layers for Power BI data, but they sit at different points in the architecture and solve different problems."
pubDate: 2026-10-14
category: data-modeling
tags: ["dataflows", "etl"]
difficulty: Advanced
author: Mireia
featured: false
draft: false
---

Dataflows and datasets are both storage layers for Power BI data, but they sit at different points in the architecture and solve different problems. Confusing the two leads to duplicated transformation logic, refresh bottlenecks, and models that quietly drift apart. This article breaks down what a dataflow actually is, how it relates to datasets, and when to choose one over the other.

## What a Dataflow Is

A dataflow is a self-service ETL layer that stores tables in the Power BI service. You build it with Power Query, either in Power BI Desktop or in the browser, and you publish it to a workspace as a first-class artifact. The result is one or more tables that live in Azure Data Lake Storage Gen2 (behind the scenes, in the CDM folder format).

The key architectural point: a dataflow produces **tables**, not a model. There are no relationships, no measures, no hierarchies, no calculated columns. It is a cleaned, reusable set of entities that any number of downstream artifacts can consume.

A typical flow looks like this:

1. Source systems (SQL, SharePoint, CSV, API) get queried by Power Query M inside the dataflow.
2. The dataflow runs those queries and writes the result to the service's managed lake.
3. Downstream, Power BI Desktop connects to the dataflow and gets those tables as sources.
4. The resulting dataset adds relationships, measures, and the rest of the semantic model.

That middle layer is what makes dataflows valuable. Instead of every report author re-implementing the same joins and cleanup against the source database, one dataflow does it once.

## What a Dataset Is

A dataset (in newer terminology, a *semantic model*) is the analytical layer itself. It holds:

- Tables loaded from sources, dataflows, or DirectQuery connections
- Relationships and cardinality
- Measures written in DAX
- Hierarchies, calculated columns, calculated tables, RLS roles
- The refresh schedule that keeps cached data current

When a report is bound to a dataset, the report is a thin visual layer. The dataset is where all business logic lives. This is why you can have one dataset serving twenty reports, and why changing a measure in the dataset immediately affects every report that consumes it.

## The Head-to-Head Comparison

| Aspect | Dataflow | Dataset |
| --- | --- | --- |
| Language | Power Query M | DAX for logic, M for ingestion |
| Contains measures | No | Yes |
| Contains relationships | No | Yes |
| Storage | ADLS Gen2 (CDM folders) | VertiPaq in-memory or DirectQuery backend |
| Consumed by | Datasets, other dataflows | Reports, dashboards, paginated reports |
| Refresh | Own schedule | Own schedule |
| Row-level security | No (at the artifact level) | Yes |
| Reusability scope | ETL / transformation logic | Business logic and metrics |
| Direct connection from Desktop | Yes, via "Power BI dataflows" connector | Live connection / DirectQuery |

The single most important row is reuse. Dataflows reuse *preparation*. Datasets reuse *semantics*. Mixing the two roles causes pain.

## Step-by-Step: Building a Dataflow

Start in Power BI Desktop or the service. The service approach is more common for dataflow-first workflows.

1. In a Premium or PPU workspace, click **New > Dataflow**.
2. Choose **Define new entities** and select your source connector.
3. Power Query opens in the browser. Apply your transformations: filtering, type changes, merges, custom columns. This is ordinary M, but you cannot reference another entity with a calculated column here the way you might in a Desktop model.
4. Name the entity (for example, `Sales` or `Customers`). Keep entity names stable; downstream datasets reference them by name.
5. Optionally add **computed entities** (M queries that reference other entities inside the same dataflow) for further shaping.
6. Save and publish. The first refresh materialises the tables into the lake.
7. Set a refresh schedule under the dataflow's settings.

A minimal M expression to clean a sales table might look like this:

```powerquery
let
    Source = Sql.Database("srv-sales", "Warehouse"),
    Sales = Source{[Schema="dbo", Item="FactSales"]}[Data],
    Typed = Table.TransformColumnTypes(Sales, {
        {"OrderDate", type date},
        {"Amount", type number},
        {"CustomerKey", Int64.Type}
    }),
    Filtered = Table.SelectRows(Typed, each [Amount] <> null and [Amount] > 0)
in
    Filtered
```

Publish that as an entity named `Sales`, and any dataset in the workspace can ingest it.

## Consuming a Dataflow from a Dataset

In Power BI Desktop:

1. Get Data > **Power BI dataflows**.
2. Sign in and pick the workspace holding the dataflow.
3. Select the entities you need. Each entity becomes a table in the model.
4. Build relationships, add measures, and publish the dataset.

Now here's the payoff. If the dataflow changes its cleaning logic—say, a new source column needs filtering—you update the dataflow once and refresh the dataset. Every downstream report inherits the fix.

You can also chain dataflows: dataflow A shapes raw source, dataflow B (a "staging" or "curated" layer) references A's entities. This mirrors the medallion pattern (bronze/silver/gold) inside the Power BI service.

The DAX layer then sits on top of those tables. Suppose you want year-to-date revenue with a proper date table:

```dax
Revenue YTD =
CALCULATE(
    SUM ( Sales[Amount] ),
    DATESYTD ( 'Date'[Date] )
)
```

That measure belongs in the dataset, never in the dataflow. Dataflows produce inputs; datasets produce answers.

## Where the Line Gets Blurry

A few areas trip people up.

**Computed entities are not calculated tables.** A computed entity in a dataflow is an M query that runs server-side and lands as another table in the lake. A calculated table in a dataset is DAX evaluated at refresh inside the model. Different languages, different lifecycles.

**Dataflows do not participate in relationships.** If you need a star schema, the dataset builds it. The dataflow only sees flat tables.

**Row-level security lives in the dataset.** You can scope who can refresh or view a dataflow via workspace roles, but dynamic per-user filtering is a dataset role.

**Refresh order matters.** A dataset that consumes a dataflow depends on that dataflow's most recent successful refresh. Schedule the dataflow to finish before the dataset starts. Overlapping schedules mean the dataset reads stale data.

**DirectQuery against a dataflow is not supported** the same way it is against Azure SQL. A dataset ingests dataflow entities in Import mode (or uses the dataflow's connector for DirectQuery in limited scenarios). Plan storage accordingly.

## When to Use Which

Use a **dataflow** when:

- Multiple datasets share the same upstream source and cleanup logic
- You want citizen developers to prepare data without Desktop installs
- You need a reusable ETL layer inside the service
- You're implementing a layered/staged architecture

Use a **dataset** when:

- You need relationships, measures, hierarchies, or RLS
- The report requires DAX time intelligence or complex filters
- You need incremental refresh with a model-aware schedule beyond a plain entity

In practice, mature deployments use both: dataflows for the "get and clean" layer, datasets for the "model and measure" layer, and reports bound to datasets. It is a clean separation that keeps transformation work from being duplicated across fifty PBIX files.

## Common Mistakes

- Putting business measures in a dataflow. M has no `CALCULATE`, no filter context. Do it in the dataset.
- Reusing a dataset where a dataflow was needed (or vice versa). Ask "am I sharing preparation or sharing semantics?"
- Forgetting that a dataflow refresh failure cascades—every dependent dataset fails too. Monitor refresh history for the whole chain, not just individual items.
- Over-layering. Five dataflows deep is usually three too many. Two or three well-named layers (raw, cleaned, curated) cover most needs.

## FAQ

### Q: Can a dataset be built directly on a dataflow without Power BI Desktop?

Yes, up to a point. In the service you can create a dataset from a dataflow using the built-in flow, and you can add measures in the browser's model view. But for relationships across many tables, calculation groups, and RLS roles, Desktop is still the practical authoring tool. The service is improving, but Desktop remains the full-fidelity editor.

### Q: Do dataflows require Premium capacity?

No, but with caveats. Basic dataflows on shared capacity have limitations: no computed entities in some configurations, no DirectQuery consumption, and storage is capped per user. Premium Per User (PPU) and Premium capacity unlock incremental refresh, linked entities, computed entities, and the CDM folder storage that makes dataflows genuinely useful at scale.

### Q: How is a dataflow different from a Power Query query in a PBIX?

Functionally they run similar M, but a PBIX query runs inside the report file and its results only exist in that file's dataset—or during a Desktop refresh. A dataflow query runs in the service, materialises into shared storage, and can be consumed by many datasets. Dataflows share preparation; PBIX queries are local and private.

### Q: Can two dataflows reference each other's entities?

Yes, in one direction at a time. A dataflow can reference entities from another dataflow in the same workspace, forming a chain (raw → cleaned → curated). Circular references are not allowed. This is how layered dataflow architectures are built, and it's the main reason teams adopt them.

### Q: What happens to downstream datasets if a dataflow refresh fails?

They fail too, or they refresh against the last successful dataflow snapshot. In Import mode, dependent datasets simply cannot pick up new data until the dataflow succeeds. PowerShell and the REST API can help you orchestrate refresh order so the dataflow runs first.

Microsoft documents this feature in [its Dataflows reference](https://learn.microsoft.com/en-us/power-bi/transform-model/dataflows/dataflows-introduction-self-service).

## Related Reading

- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Power Query Getting Started](/tutorials/de-power-query-getting-started/)
- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [Power BI Date Table](/tutorials/power-bi-date-table/)
- [DAX Time Intelligence: YTD, QTD, MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
