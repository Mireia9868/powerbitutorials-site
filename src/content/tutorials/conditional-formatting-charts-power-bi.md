---
title: "Conditional Formatting for Charts, Bar Charts & Gauges in Power BI"
description: "Charts don't use cell rules — they use Data colors conditional formatting. Learn how to color bars, columns, and gauge fills by value, measure, or rule, with worked examples for bar charts and KPI gauges."
pubDate: 2026-08-28
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "conditional-formatting", "bar-chart", "gauge", "data-colors", "kpi"]
author: Mireia
featured: false
---

Conditional formatting on a matrix is one thing — you pick a color scale and move on. Charts are different. There are no "cells," so Power BI uses **Data colors** conditional formatting, and each visual type handles it a little differently. A bar chart colors by category; a gauge colors its fill by a single value; a KPI visual leans on its own status logic. This guide covers the practical patterns for the two charts people ask about most: bar charts and gauges.

## How chart conditional formatting works

For any chart, select the visual → **Format pane → Data colors → Conditional formatting (fx)**. You get three options:

- **Format by: Color scale** — gradient mapped to a field's values.
- **Format by: Rules** — thresholds mapped to specific colors.
- **Format by: Field value** — a measure returns a hex color per data point.

The big difference from matrices: the color usually applies **per category or per data point**, not per cell. A bar chart with regions on the axis gives each region its own color.

## Bar and column charts

### Color by value (gradient)

Want bars to darken as revenue rises? Set **Data colors → fx → Format by: Color scale**, pick your measure (e.g., `[Total Sales]`), and choose a two- or three-color gradient. Low values get the first color, high values the last.

This is great for a single-series bar chart where magnitude matters. It falls apart with multiple series, because each series gets its own scale and colors stop being comparable. For multi-series, use rules or field value instead.

### Color by rule (status thresholds)

A regional sales bar chart where you want West green above target, red below:

1. **Data colors → fx → Format by: Rules.**
2. **Based on field:** `[Total Sales]`.
3. Add rules: `is greater than 1000000` → green; `is less than 500000` → red; everything else → gray.

Rules give you fixed, readable colors instead of a gradient nobody can interpret.

### Color by a measure (most control)

For logic that depends on more than one column — say, color by whether the region beat its own target — use a color measure and **Format by: Field value**.

```dax
// Returns a color per region based on target attainment
CF Region Sales =
VAR Sales = [Total Sales]
VAR Target = [Sales Target]
RETURN
    SWITCH(
        TRUE(),
        Sales > Target * 1.1, "#22C55E",
        Sales >= Target, "#F59E0B",
        "#EF4444"
    )
```

Point **Data colors → fx → Field value** at `CF Region Sales`. Each bar now reflects target attainment, and the logic lives in one measure you can reuse across every bar chart in the report.

### The constant line trick

Bar charts support a **constant line** (Analytics pane) that draws a reference at a fixed or measure-driven value — handy for a target line. It's not "formatting" per se, but it pairs with color rules to make over/under-target obvious at a glance. Set the line value to `[Sales Target]` so it moves with your data.

## Gauges and KPI visuals

### Gauge fill color

A gauge shows a single value against a target, so conditional formatting is about the **fill**, not categories. Select the gauge → **Format pane → Data colors → Conditional formatting** on the fill.

Use **Rules** based on the gauge's value measure:

- `is greater than [Target]` → green fill
- `between 0 and [Target]` → amber
- `is less than 0` → red

Because a gauge has one value, the most useful pattern is a measure that picks the color from the ratio to target:

```dax
// Gauge fill color based on target attainment
CF Gauge Fill =
VAR Pct = DIVIDE([Total Sales], [Sales Target], 0)
RETURN
    SWITCH(
        TRUE(),
        Pct >= 1, "#22C55E",
        Pct >= 0.8, "#F59E0B",
        "#EF4444"
    )
```

### KPI visual status

The KPI visual has built-in **Status** and **Trend** formatting. Under **Format pane → Status**, you can set conditional colors for the indicator based on distance from target. This is effectively conditional formatting tuned for a single KPI — set the "good / neutral / bad" thresholds and Power BI colors the status accordingly.

For an Adventure Works scenario: a KPI showing monthly sales turns green when at or above target, red when more than 20% below. Define those thresholds once and the KPI stays honest across every month the user filters to.

## Cards and other visuals

Cards don't support data colors conditional formatting the way charts do — but you can still drive their font or background color via **Field value** if the card shows a measure. The same `CF Region Sales` measure works; just apply it through the card's conditional formatting option for font/background. Keep cards minimal — one color rule is plenty.

## Common mistakes

**Mistake 1: Applying a gradient to a multi-series chart.** Each series scales independently and the colors become meaningless. Switch to rules or field value.

**Mistake 2: Forgetting the gauge has one value.** People try to color a gauge "per category" — there's only one data point, so use a measure based on the value-to-target ratio.

**Mistake 3: Hard-coding threshold colors in rules.** When the target changes monthly, hardcoded rules go stale. A measure referencing `[Sales Target]` stays correct automatically.

**Mistake 4: Too many colors on one bar chart.** Six regions in six colors with no logic is noise. Use a meaningful scale or rule, not a rainbow.

## FAQ

**Can I color a stacked bar by its segments?**
Segment colors come from the legend field, not conditional formatting. You can conditionally format the legend field's Data colors, but stacking already encodes magnitude — adding color rules on top usually confuses the reader.

**Why does my bar chart color every bar the same?**
Field value formatting is evaluating at a granularity where the measure returns one value for all bars (e.g., a total). Make sure the color measure resolves per category on the axis.

**Do gauge rules reference the target automatically?**
No. Rules compare against numbers you type or a fixed value. To compare against a dynamic target, use a Field value measure that already divides by `[Sales Target]`.

## What's next

- [Conditional Formatting in Power BI: A Complete Guide](/tutorials/conditional-formatting-power-bi/) — the measure and rule foundations for all chart formatting here.
- [How to Copy Conditional Formatting in Power BI](/tutorials/copy-conditional-formatting-power-bi/) — reuse these color measures across every chart.
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/) — keep chart colors consistent with the rest of the report.
<!-- CF-CLUSTER-NAV -->
## More conditional formatting guides

- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-complete-guide/)
- [Conditional Formatting in Power BI](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)
- [Conditional Formatting for Charts](/tutorials/conditional-formatting-charts-power-bi/)
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting-power-bi/)
- [Gauge Conditional Formatting](/tutorials/gauge-conditional-formatting/)
- [Bar Chart Conditional Formatting](/tutorials/bar-chart-conditional-formatting/)
- [Line Chart Conditional Formatting](/tutorials/line-chart-conditional-formatting/)

