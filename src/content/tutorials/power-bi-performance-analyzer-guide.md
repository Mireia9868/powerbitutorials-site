---
title: "Power BI Performance Analyzer: A Practical Guide to Faster Reports"
description: "Power BI Desktop's Performance Analyzer tells you exactly which visual is slow and why. Learn to record, export, and read its data — plus how to turn those numbers into a fix using DAX Studio."
pubDate: 2026-08-28
category: "data-modeling"
difficulty: "Intermediate"
tags: ["performance", "performance-analyzer", "dax-studio", "troubleshooting", "optimization"]
author: Mireia
featured: false
---

Your report feels slow, but "slow" isn't a diagnosis. Power BI's built-in **Performance Analyzer** turns that vague complaint into a ranked list of culprits — which visual, how long, and whether the time went to DAX, rendering, or the network. This guide walks through recording, exporting, and actually using that data. It pairs with the broader [performance optimization guide](/tutorials/power-bi-performance-optimization/) once you know what to fix.

## Where to find it

In Power BI Desktop: **View → Performance Analyzer**. A pane opens on the right with a **Start recording** button. Click it, then interact with your report — switch pages, click slicers, hover visuals. Every interaction gets timed.

## What the numbers mean

Each visual reports three timings:

- **DAX query** — time spent evaluating the measure(s). High here means DAX or model problems.
- **Visual display** — time spent rendering the chart. High here means too many visuals, too many data points, or a heavy custom visual.
- **Network** — time fetching data from the source. High here points at the data connection, not your model.

There's also a small overhead line for "Other." Ignore it for tuning.

The key insight: the *largest* number tells you where to look. A visual with 8s DAX and 0.2s display is a DAX problem (see our [DAX optimization guide](/tutorials/power-bi-dax-optimization/)). A visual with 0.1s DAX and 6s display is a rendering problem — cut visuals or simplify.

## Recording properly

Bad recordings produce misleading data. Follow this:

1. **Refresh the model first** so timings reflect cached data, not a cold refresh.
2. **Start recording, then interact once per visual** you care about. Don't click randomly — you want a clean per-visual read.
3. **Sort by DAX query time** in the pane to find the worst offenders instantly.
4. **Record the same action twice.** The first run often includes one-time compilation; the second is your real number.

## Exporting to JSON

The pane has an **Export** button that saves a JSON file with every recorded event. This is where it gets useful for serious analysis — you can slice the data in Power Query or Excel.

To analyze in Power BI itself:

1. **Export** the JSON from Performance Analyzer.
2. Open a new Power BI file → **Get Data → JSON** → load the file.
3. Expand the `events` and `metrics` records.
4. Build a simple visual: Visual Name on axis, sum of DAX query time on values.

Now you have a sortable, shareable table of exactly where time goes — far better than squinting at the pane. At Contoso, this export is how the BI team justifies model rework to finance: "Visual X is 60% of total report time" is a compelling argument.

## From number to fix

Once you've found a slow visual, the path is usually:

- **High DAX time** → open DAX Studio, run **Server Timings** on that visual's measure. Look for Formula Engine dominance (see the [DAX optimization guide](/tutorials/power-bi-dax-optimization/)). Common fixes: column predicates instead of FILTER, variables to stop recomputation, a marked date table.
- **High display time** → reduce visuals on the page (cap at 8–10), remove heavy custom visuals, or split content across pages with bookmarks.
- **High network time** → check the data source. A slow SQL view or throttled gateway shows up here, not in your model.

## A worked example

A regional sales page at Adventure Works took 22 seconds to render on first open. Performance Analyzer showed:

- Map visual: 14s display, 0.3s DAX
- Matrix: 0.5s display, 7s DAX
- Everything else: under 1s

Two fixes, two different layers: the map was rendering 400k points — reduced to a summarized aggregate (display fixed). The matrix measure used `FILTER(ALL(Sales), ...)` — replaced with a column predicate (DAX fixed). Page load dropped to 3 seconds.

## Common mistakes

**Mistake 1: Reading the first run.** The initial evaluation includes compilation overhead. Always record the action twice and trust the second number.

**Mistake 2: Optimizing the wrong visual.** The visual that *looks* complex isn't always the slow one. Sort by DAX time and let the data decide.

**Mistake 3: Fixing display time with DAX changes.** If display dominates, no amount of DAX tuning helps. Reduce visuals instead.

**Mistake 4: Not exporting.** The pane is fine for a quick look, but the JSON export is what makes the problem visible to a team and trackable over time.

## FAQ

**Is Performance Analyzer available in Power BI Service?**
Not directly — it's a Desktop tool. For Service-side slowness, use the dataset's refresh history and capacity metrics. Desktop analysis catches most problems before they reach Service.

**Why is my first interaction always slow?**
One-time query plan compilation and cache warming. That's normal; measure the second run.

**Can I use this to compare before and after a change?**
Yes — export before, make the change, export after, and compare the DAX/display totals. It's the cleanest way to prove an optimization worked.

**Does it work with DirectQuery?**
It does, but most time lands in Network or DAX pushed to the source. Read those numbers as "fix the source query," not "fix the model."

## What's next

- [Power BI Performance Optimization: Complete Guide](/tutorials/power-bi-performance-optimization/) — the full tuning playbook once you've found the bottleneck.
- [Power BI DAX Optimization](/tutorials/power-bi-dax-optimization/) — turn a high DAX time into a concrete fix.
- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/) — most DAX slowness traces back to a weak model.
