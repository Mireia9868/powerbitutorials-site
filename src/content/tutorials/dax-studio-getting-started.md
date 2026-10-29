---
title: "DAX Studio Getting Started: Connect to Power BI"
description: "DAX Studio is the free tool for writing, tracing, and tuning DAX. Learn how to connect to a Power BI model, read a query plan, and find slow measures."
pubDate: 2026-09-23
category: "dax"
difficulty: "Intermediate"
tags: ["power bi", "dax studio", "query plan", "performance", "vertipaq"]
author: Mireia
featured: false
draft: false
---

DAX Studio is a free, open-source tool every serious Power BI developer should have. It lets you write DAX against a live model, capture the **query plan**, and see exactly how VertiPaq executes it. This guide gets you connected and shows the three features that pay for the install.

## Install and connect

1. Download DAX Studio (free) and install.
2. Open Power BI Desktop with your model loaded.
3. In DAX Studio, **Connect** → choose **Power BI / SSDT Model** → select your open .pbix.

<!-- TODO: add screenshot: Figure 1: dax studio getting started illustration -->

The connection reads the live model in memory — no export needed.

## Feature 1: write and run DAX freely

The main window is a DAX editor with IntelliSense. Run a measure definition to test it without touching your report:

```dax
EVALUATE
SUMMARIZECOLUMNS (
    'Product'[Category],
    "Total Sales", [Total Sales]
)
```

## Feature 2: read the query plan

Click **Query Plan** before running. You get two trees:
- **Logical Plan** — what DAX intended.
- **Physical Plan** — what the Storage Engine actually did.

A measure is fast when the Physical Plan shows few `Scan_Vertipaq` calls and the Formula Engine (FE) does little. Many `CallbackDataID` nodes mean the Storage Engine could not do the work natively — a red flag.

## Feature 3: capture traces (Server Timings)

The **Server Timings** tab breaks a query into Storage Engine (SE) vs Formula Engine (FE) time. The golden rule: push work to the SE. If FE time dominates, your DAX is doing row-by-row logic that should be a variable or a calculated column.

This pairs directly with [power-bi-performance-analyzer-guide](/tutorials/power-bi-performance-analyzer/) inside Power BI — DAX Studio gives the deeper view.

## When to reach for it

- A visual is slow and you need the *why*.
- You want to test a measure rewrite without editing the model.
- You are learning why `EARLIER` or `FILTER ( FullTable )` is expensive (see [power-bi-dax-optimization](/tutorials/power-bi-dax-optimization/)).

## FAQ

**Q: Does DAX Studio change my model?**
A: No. It is read-only against the connected model. You can run any query safely.

**Q: Can I use it with the Power BI Service?**
A: Yes, with an XMLA endpoint enabled on Premium/Premium Per User. Desktop connect is the easiest start.

**Q: What is the difference from Performance Analyzer?**
A: Performance Analyzer lives inside Power BI and times whole visuals. DAX Studio times individual queries and shows the SE/FE split.

DAX Studio itself is free and open source; its documentation lives at [daxstudio.org](https://daxstudio.org/).

## Related Reading

- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/)
- [Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer/)
- [DAX Troubleshooting Guide](/tutorials/dax-troubleshooting-guide/)
- [DAX Basics](/tutorials/dax-basics/)
- [Filter Context vs Row Context](/tutorials/filter-context-row-context-explained/)
- [DAX Performance Optimization](/tutorials/power-bi-dax-optimization/)
