---
title: "Power BI Visual Calculations: The Complete Guide (2026 GA)"
description: "Visual Calculations went GA in May 2026. Learn how RUNNINGSUM, MOVINGAVERAGE, PREVIOUS, and other visual-level functions replace dozens of measures — with real Contoso examples and copy-paste code."
pubDate: 2026-08-01
category: "dax"
difficulty: "Intermediate"
tags: ["visual calculations", "running sum", "moving average", "DAX", "Power BI Desktop"]
author: "Power BI Tutorials Team"
---

If you've ever built a running total in DAX, you know the drill: write a measure with CALCULATE, fight with ALLSELECTED for twenty minutes, then watch it break the moment someone drills into a subcategory. Visual Calculations fix that mess. They live on the visual itself — not in your semantic model — which means no measure sprawl, no filter context surprises, and no digging through 200 measures to find the one that's scoped wrong.

Microsoft shipped Visual Calculations as generally available in the May 2026 feature update. They're the most practical addition to Power BI since field parameters, and if you're not using them yet, you're probably writing DAX you don't need to.

## What Are Visual Calculations, Exactly?

A visual calculation is a DAX formula that's evaluated against the rows and columns of a specific visual — a matrix, a table, a bar chart — rather than against the entire semantic model. Think of it this way: a regular measure computes over the filter context of whatever visual you drop it on. A visual calculation computes over the *grid* of that visual, with awareness of which row is above, below, or next to the current one.

That grid awareness is the whole point. It's what lets you write `RUNNINGSUM([Sales])` instead of a six-line CALCULATE pattern. The calculation sees the visual's structure — its axis — and traverses it row by row.

Here's the kicker: visual calculations don't show up in your field list. They don't clutter your model. They're attached to the visual, so if you delete the visual, the calculation goes with it. That's a feature, not a limitation — it keeps one-off report calculations out of your shared semantic model.

## How to Create a Visual Calculation

In Power BI Desktop, select a visual (a table or matrix works best for testing), then click **New visual calculation** in the ribbon's **Calculations** group. The formula bar opens, and you type DAX — but a specific subset of DAX that includes visual-level functions.

Let's say you have a matrix showing quarterly sales for Contoso's product categories. Your base measure is `[Total Sales]`. Here's a running total:

```dax
Running Total = RUNNINGSUM([Total Sales])
```

That's it. No CALCULATE, no ALL, no ALLSELECTED, no variables. The running sum respects whatever filters are on the visual and resets per partition if you tell it to.

Want a moving average? Same deal:

```dax
3-Month Moving Avg = MOVINGAVERAGE([Total Sales], 2)
```

The second argument is the number of rows *before* the current row to include. So `2` means the current row plus the two before it — a 3-period average.

## The Core Visual Calculation Functions

Here's what's in your toolbox as of the GA release. These functions only work inside visual calculations — you can't use them in regular measures.

**Traversing the axis:**

| Function | What It Does | Equivalent Offset |
|----------|-------------|-------------------|
| `PREVIOUS([expr])` | Value from the row before the current one | `OFFSET(-1)` |
| `NEXT([expr])` | Value from the row after the current one | `OFFSET(1)` |
| `FIRST([expr])` | First row on the axis | `INDEX(1)` |
| `LAST([expr])` | Last row on the axis | `INDEX(-1)` |

**Aggregating across the axis:**

| Function | What It Does |
|----------|-------------|
| `RUNNINGSUM([expr])` | Cumulative sum from the first row to current |
| `MOVINGAVERAGE([expr], n)` | Average of current row plus `n` preceding rows |

**Comparing to a specific point:**

```dax
// Difference from first quarter
Delta from Start = [Total Sales] - FIRST([Total Sales])

// Percent of first quarter
Growth Rate = DIVIDE([Total Sales] - FIRST([Total Sales]), FIRST([Total Sales]))
```

**Percent of parent (one of the most requested patterns):**

```dax
% of Parent = DIVIDE([Total Sales], COLLAPSE([Total Sales]))
```

`COLLAPSE` moves up one level in the hierarchy. If you're at the month level, it evaluates `[Total Sales]` at the quarter level. `COLLAPSEALL` goes straight to the top — useful for percent of grand total.

## The Axis and Reset Parameters

Most visual calculation functions accept two optional parameters that control how they traverse the visual matrix: **Axis** and **Reset**.

### Axis

By default, visual calculations traverse `ROWS` — top to bottom. But you can change that:

```dax
// Running sum across columns (left to right) instead of rows
Running Total Horizontal = RUNNINGSUM([Total Sales], AXIS = COLUMNS)
```

Valid axis values:
- `ROWS` — vertical, top to bottom (default)
- `COLUMNS` — horizontal, left to right
- `ROWS COLUMNS` — vertical first, then column by column
- `COLUMNS ROWS` — horizontal first, then row by row

### Reset

Reset controls when a running calculation starts over. By default, it doesn't — `RUNNINGSUM` accumulates from the first row to the last. But in a matrix with Year > Quarter, you might want the running sum to reset at each year boundary.

```dax
// Reset running sum at the highest parent level (Year)
Running Total by Year = RUNNINGSUM([Total Sales], RESET = HIGHESTPARENT)
```

You can also use integers:
- `RESET = 1` — reset at the top level (same as `HIGHESTPARENT`)
- `RESET = 2` — reset at the second level
- `RESET = 0` — never reset (same as `NONE`, the default)

Negative integers work in relative mode — useful when your hierarchy depth varies.

## A Real Example: Quarterly P&L with Running Total

Let's build something you'd actually use. Adventure Works wants a quarterly P&L view that shows:
1. Revenue per quarter
2. Running total of revenue (resetting each fiscal year)
3. Year-over-year comparison (same quarter last year)

```dax
// Base revenue measure — already in the model
// Revenue = SUM(Sales[Amount])

// Visual calculation 1: Running total, resets at fiscal year
YTD Revenue = RUNNINGSUM([Revenue], RESET = HIGHESTPARENT)

// Visual calculation 2: Same quarter last year
Prior Year Qtr = LOOKUP([Revenue], [Fiscal Year], "FY" & VALUE(LEFT([Fiscal Year], 4)) - 1)

// Visual calculation 3: YoY change
YoY Change = [Revenue] - [Prior Year Qtr]
```

`LOOKUP` evaluates an expression at a specific coordinate in the visual matrix. It's the visual-calc equivalent of using CALCULATE with a filter modification — except it operates on the visual's grid, not the model's filter context.

## When to Use Visual Calculations vs. Measures

Here's the decision framework:

**Use a visual calculation when:**
- The calculation is specific to one visual's layout (running total down a matrix, percent of parent in a specific hierarchy)
- You don't want to pollute the shared semantic model with one-off report calculations
- The logic depends on visual structure (row position, hierarchy level) rather than model data

**Use a regular measure when:**
- The calculation needs to work across multiple visuals
- The logic is a business rule that should live in the semantic model
- You need the calculation in a KPI card, scorecard, or elsewhere outside a matrix/table

**Use both when:** You have a base measure (like `[Revenue]`) that powers a visual calculation (like `RUNNINGSUM([Revenue])`). The measure stays in the model; the visual calculation stays on the visual.

## Visual Calculations and Field Parameters

If you're using [field parameters](/tutorials/power-bi-field-parameters/) for dynamic measure switching, visual calculations work alongside them — but with a catch. Visual calculations reference the visual's axis, not the field parameter's selection. If you swap measures via a field parameter slicer, your visual calculations will stay in place but may show unexpected results if the axis structure changes.

The workaround: keep visual calculations on visuals with a fixed axis (like a matrix with stable row headers), and use field parameters on visuals where the structure doesn't change.

## Common Mistakes

**Mistake 1: Expecting visual calculations to work in KPI cards.**
They don't. Visual calculations require an axis — a grid of rows and/or columns. A KPI card has no axis, so there's nothing to traverse. If you need a running total in a KPI, you still need a traditional DAX measure.

**Mistake 2: Forgetting that visual calculations don't appear in the field list.**
If you build a visual calculation on one matrix and then try to reuse it on a bar chart, you can't. You'll need to recreate it on the second visual. This is by design — the calculation is tied to the visual's specific structure.

**Mistake 3: Using visual calculations for cross-table logic.**
Visual calculations operate on what's displayed in the visual. If you need to pull a value from a different table that isn't in the visual, use a regular measure with CALCULATE instead. Visual calculations can't reach into the model's filter context the way measures can.

**Mistake 4: Ignoring the Reset parameter on multi-level hierarchies.**
If you have Year > Quarter > Month and you write `RUNNINGSUM([Sales])` without a Reset parameter, the running sum accumulates from January of the first year all the way through December of the last year. That's rarely what finance teams want. Add `RESET = HIGHESTPARENT` to reset at each year.

## FAQ

**Can I use visual calculations in the Power BI Service?**
Yes. They work in both Desktop and the Service, and they carry through to embedded analytics scenarios. Whatever you build in Desktop renders the same way when published.

**Do visual calculations slow down my report?**
For most scenarios, no — they're evaluated against the visual's data, which is already loaded. But if you're running complex LOOKUP patterns on a matrix with thousands of rows, you may see a performance hit. Test on your largest visual before rolling out.

**Can I apply conditional formatting based on a visual calculation?**
Absolutely. Create a visual calculation that returns a color code or a value, then use it as the basis for conditional formatting via the Format pane → Cell elements → Background color → fx → Field value. This is one of the most useful patterns — your formatting logic stays next to the visual it applies to.

**What happens if I delete a visual with visual calculations on it?**
The visual calculations are deleted with the visual. They don't linger in the model. This is actually a benefit — no orphaned calculations from deleted visuals.

**Can I use DAX variables (VAR/RETURN) in visual calculations?**
Yes, but they work the same way as in measures — they capture a value at evaluation time. If you need a refresher on VAR/RETURN, check out our [DAX Variables guide](/tutorials/dax-variables-guide/).

## What's Next

- Master [CALCULATE](/tutorials/dax-calculate-function/) to understand the filter context that visual calculations sidestep
- Learn [field parameters](/tutorials/power-bi-field-parameters/) for dynamic measure switching alongside visual calculations
- Read our [DAX time intelligence guide](/tutorials/dax-time-intelligence-ytd-qtd-mtd/) for traditional YTD/QTD/MTD patterns — then see how visual calculations simplify some of those same scenarios
