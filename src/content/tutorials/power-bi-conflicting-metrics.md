---
title: "Power BI Conflicting Metrics Error: Causes and Fixes"
description: "The 'conflicting metrics' error in Power BI stops a visual from rendering and confuses even experienced users. Learn what actually triggers it, the four most common causes, and the step-by-step fixes that resolve it."
pubDate: 2026-10-15
updatedDate: 2026-10-15
category: "visualization"
difficulty: "Intermediate"
tags: ["conditional formatting", "troubleshooting", "errors", "data model"]
author: "Power BI Tutorials Team"
---

You build a report, drop a field onto a visual, and Power BI throws a **"Conflicting metrics"** error. No clear line number, no obvious culprit. This guide breaks down what the error really means and how to fix it without guessing.

## What the "Conflicting metrics" error actually means

Power BI raises this error when a single visual tries to evaluate **two or more measures (or aggregations) that disagree about how to summarize the same underlying data in the same context**. The engine can't reconcile the conflict, so it refuses to render the visual rather than show you wrong numbers.

It is not a syntax error. It is a *modeling* conflict — usually between implicit and explicit aggregations, or between measures that pull the same column through incompatible paths.

## Cause 1: Mixing implicit and explicit aggregations on the same column

The most common trigger: you dragged a numeric column onto the visual (creating an *implicit* measure that sums/averages it), and at the same time added an *explicit* measure that also aggregates that same column.

**Fix:** Pick one. Convert the implicit column into an explicit measure, or remove the explicit measure. Never let both summarize the same field in one visual.

## Cause 2: A field used both as a dimension and a measure

If a column is placed in the Values well (as a measure) and also used as an axis or legend (as a dimension), Power BI sees it in two incompatible roles.

**Fix:** Decide the role. If you need it as both, create a explicit measure (e.g. `SUM(Table[Amount])`) for the Values well and keep the raw column only as the axis.

## Cause 3: Relationship ambiguity (multiple paths to the same table)

When your model has more than one active path between two tables — for example a direct relationship and an indirect one through a bridge — a measure can resolve to two different totals. This often surfaces as a conflicting-metrics error inside visuals that cross those tables.

**Fix:** Review your relationships. Use a single active relationship where possible, and fall back to `USERELATIONSHIP` only when you deliberately need the inactive path. Our guide on [one-to-many vs many-to-many relationships](/tutorials/relationships-one-to-many-many-to-many/) covers how to choose the right structure, and [star schema design](/tutorials/data-modeling-star-schema/) explains how to keep paths unambiguous.

## Cause 4: Conditional formatting pointing at a measure that conflicts with the value

This error frequently appears when [conditional formatting based on a measure](/tutorials/conditional-formatting-based-on-measure/) is applied, but the formatting measure and the visual's value measure aggregate the same column differently or come from mismatched filter contexts.

**Fix:** Make sure the formatting measure and the value measure share the same granularity and filter context. If the formatting measure uses a different table path, reconcile it with the approach in [conditional formatting in Power BI](/tutorials/conditional-formatting-power-bi/).

## Step-by-step troubleshooting checklist

1. Remove one aggregation at a time until the error disappears — that isolates the conflict.
2. Check the Values well: are there both raw columns and measures summarizing the same field?
3. Open **Manage Relationships** and look for multiple paths between the tables in the visual.
4. If conditional formatting is on, temporarily turn it off to see if the error clears.
5. Rebuild the visual with a single explicit measure per field.

## FAQ

**Does the conflicting metrics error mean my data is wrong?**
Not necessarily. It means Power BI can't decide *which* aggregation to use. The data may be fine; the model expression is ambiguous.

**Why does it only happen in one visual and not others?**
Because the conflict depends on the exact combination of fields in that visual. Another visual may not include the conflicting pair.

**Can I prevent this with a better data model?**
Yes. A clean [star schema](/tutorials/data-modeling-star-schema/) with explicit measures — and no raw numeric columns dragged into visuals — eliminates almost all of these conflicts.
