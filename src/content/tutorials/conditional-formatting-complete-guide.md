---
title: "Power BI Conditional Formatting: The Complete Guide"
description: "Everything you can do with conditional formatting in Power BI — color rules, field-value measures, gradients, chart-level formatting, and how to reuse rules across visuals. A hub that links to the focused guides for each visual type."
pubDate: 2026-10-12
updatedDate: 2026-10-12
category: "visualization"
difficulty: "Beginner"
tags: ["conditional-formatting", "visualization", "color-rules", "field-value", "reuse"]
author: "Power BI Tutorials Team"
featured: false
---

Conditional formatting is what turns a flat Power BI table into a report that *reads itself* — red when a target is missed, green when it's beaten, a gradient that shows momentum at a glance. This guide is the hub for the whole topic. It explains the four ways Power BI can color your data, where each one applies, and links out to the focused walkthroughs for tables, measures, and every chart type.

## The four ways Power BI colors data

| Method | Best for | Set it in |
|---|---|---|
| **Rules** (color by value) | Simple thresholds: above/below a number or text match | Visual → column/field → **Conditional formatting → Background color** |
| **Field value** (a measure) | Logic that stays in sync everywhere | Same menu → **Format by → Field value** |
| **Color scale / gradient** | Show magnitude, not just pass/fail | Same menu → **Format by → Gradient** |
| **Icons / data bars** | At-a-glance status in tables and matrices | Same menu → **Icons** or **Data bars** |

The single most important habit: **prefer a measure over hand-built rules.** A color measure (Field value) is defined once and reused by every visual; hand-built rules are recreated per visual and drift the moment you change a threshold.

## Color by rules (the basics)

Right-click a field in a table or matrix → **Conditional formatting → Background color**, then choose **Format by → Rules**. You set conditions like "if Total Sales < 1000 then red, else green." This is perfect for a one-off visual.

```dax
// The measure equivalent of a rule — define once, reuse everywhere
CF Sales vs Target =
VAR Pct = DIVIDE([Total Sales], [Sales Target], 0)
RETURN
    SWITCH(TRUE(),
        Pct > 1.05, "#22C55E",
        Pct >= 0.95, "#F59E0B",
        "#EF4444")
```

Apply it with **Format by → Field value** and pick `CF Sales vs Target`. Every visual that uses this measure now shares identical logic.

## Gradients and data bars

For continuous values, a gradient (low → high color) shows ranking better than a red/green split. Data bars put a mini bar inside the cell, which is ideal for comparing values down a column without taking up more space.

## Conditional formatting on charts

Charts format differently from tables — you color the *data points*, not cells:

- **Bar / column charts** — color by a measure or by rules on the value field.
- **Line charts** — format markers or the line by a field value.
- **Gauge** — set the arc and target colors, or drive them from a measure.
- **Cards / KPIs** — use the font/background color conditional option or a KPI visual's built-in status.

Each chart type has its own quirks, covered in the focused guides linked below.

## Based on a measure (the reusable pattern)

The pattern that scales: build a color measure, then point every visual's background or font color at it via **Field value**. Change the thresholds once, and the whole report updates. This is also the only reliable way to *copy* formatting between visuals — point the new visual at the same measure. See [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting-power-bi/) for the full playbook (measures, JSON themes, and visual duplication).

## Common mistakes

1. **Hand-building the same rule in ten visuals.** They drift apart. Use a measure.
2. **Expecting Format painter to copy conditional formatting.** It copies styling, not rules.
3. **Forgetting that gradients need a meaningful range.** A gradient across near-identical values looks random.
4. **Conflicting metrics errors.** When two format rules target the same field with overlapping conditions, Power BI can throw a "conflicting metrics" message — resolve it by consolidating the logic into a single measure (see [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)).

## Focused guides by visual type

- [Conditional Formatting in Power BI](/tutorials/conditional-formatting-power-bi/) — rules, gradients, icons, and data bars on tables and matrices.
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/) — drive colors from DAX so they stay in sync.
- [Conditional Formatting for Charts, Bar Charts & Gauges](/tutorials/conditional-formatting-charts-power-bi/) — the chart-level options in one place.
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting-power-bi/) — reuse rules with measures, JSON themes, and duplication.
- [Gauge Conditional Formatting](/tutorials/gauge-conditional-formatting/) — arc and target colors.
- [Bar Chart Conditional Formatting](/tutorials/bar-chart-conditional-formatting/) — color bars by value or measure.
- [Line Chart Conditional Formatting](/tutorials/line-chart-conditional-formatting/) — markers and lines by field value.

## FAQ

**Can I base conditional formatting on a measure instead of fixed rules?**
Yes — and you should for anything reused. Use **Format by → Field value** and select a measure that returns a color hex (or a named color). This keeps every visual consistent and updates centrally.

**Why do I get a "conflicting metrics" error?**
It usually means two formatting rules overlap on the same field. Consolidate them into one color measure so there's a single source of truth for the color logic.

**Does conditional formatting work on mobile?**
Yes, the rules travel with the visual and render the same colors on mobile as on desktop. The bigger mobile risk is layout — make sure tables and matrices are readable on a phone, since a cramped visual hurts engagement even when the colors are correct.
