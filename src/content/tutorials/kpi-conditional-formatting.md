---
title: "KPI Visual Conditional Formatting in Power BI"
description: "The KPI visual in Power BI is a small chart with a big constraint: it renders exactly one value per card, plus a trend axis, and it has no legend, no series color, and no per-category row"
pubDate: 2026-09-30
category: visualization
tags: ["conditional formatting", "kpi"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

The KPI visual in Power BI is a small chart with a big constraint: it renders exactly one value per card, plus a trend axis, and it has no legend, no series color, and no per-category row to format. That makes conditional formatting on the KPI visual genuinely different from formatting a bar chart or a matrix. You cannot right-click a bar and pick a color; you have to drive the formatting from a measure or from a field, and the visual only exposes a narrow set of properties that accept those inputs.

This article walks through what can actually be formatted, how to write the DAX that feeds it, and the traps that make colors behave unexpectedly.

## What the KPI visual exposes

Open the Formatting pane for a KPI visual and expand **Indicator** and **Trend axis**. The properties you can bind to data are limited compared to other visuals:

| Property | Accepts data-driven formatting? | Notes |
|---|---|---|
| Indicator color (Callout value) | Yes | The main number's font color |
| Indicator background | Yes | Background of the indicator area |
| Trend axis color | Yes | Line/dots color on the sparkline |
| Goal/target visualization | No | Fixed configuration only |
| Status icon | No | On/off only |

Note the gap: the KPI visual has no "status" data field of its own. The direction of the trend (the good/bad arrow next to the callout) is determined by the **Trend line** setting and the target value, not by a color rule. If you need a colored status dot driven by your own thresholds, you are better off with the Card (new) visual, which exposes a dedicated status color format. For the classic KPI, the callout color is usually the lever that carries the signal.

## Build the measures first

Conditional formatting is only as good as the measure behind it. Set up a base measure and a target, then a comparison measure that encodes the rule.

```dax
Sales Amount = SUM ( Sales[SalesAmount] )

Sales Target = SUM ( Targets[TargetAmount] )

Sales vs Target % =
DIVIDE ( [Sales Amount], [Sales Target] )
```

Now the color measure. Conditional formatting in Power BI expects a color string, so return a hex code or a named color. Format the measure as **Text** after creating it, otherwise Power BI may coerce the string and you will see nothing.

```dax
KPI Indicator Color =
VAR Pct = [Sales vs Target %]
VAR Threshold = 0.95
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( Pct ), "#A6A6A6",      -- grey: no data
        Pct >= 1.05, "#2E7D32",          -- green: comfortably ahead
        Pct >= Threshold, "#F9A825",     -- amber: close to target
        "#C62828"                        -- red: below threshold
    )
```

Two details matter here. First, `SWITCH ( TRUE (), ... )` evaluates conditions in order, so the most specific test goes first. Second, `VAR Pct = [Sales vs Target %]` is evaluated once in the filter context of the cell, which avoids recalculating the division for every branch. On large models this pattern is measurably cheaper than repeating the measure inside each condition.

If your thresholds come from a table rather than hard-coded constants, swap the literals for column references and make sure the color table is not related to the fact table in a way that filters the visual.

## Applying the rule to the KPI visual

1. Select the KPI visual.
2. Open the **Formatting** pane (paintbrush icon).
3. Expand **Indicator** and turn on **Callout value**.
4. Next to the color swatch, click the **fx** button. It appears only for properties that support conditional formatting.
5. In the dialog, choose **Format style: Field value**.
6. Under **What field should we base this on?**, select `KPI Indicator Color`.
7. Click **OK** and confirm the callout changes color when the underlying value crosses a threshold.

Repeat for **Indicator background** if you want the whole card tinted, and for **Trend axis color** if the sparkline should follow the same logic. Each property needs its own `fx` binding; Power BI does not propagate one rule across all three.

## Testing the rule without waiting for real data

Hard-coded thresholds are hard to validate. A common approach is to expose the threshold through a What-If parameter so you can drag a slider and watch the color flip. Create the parameter with **Modeling > New parameter > Numeric range**, then reference its value column in the measure.

```dax
KPI Indicator Color (Dynamic) =
VAR Pct = [Sales vs Target %]
VAR Cut = SELECTEDVALUE ( 'Threshold'[Threshold], 0.95 )
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( Pct ), "#A6A6A6",
        Pct >= Cut + 0.05, "#2E7D32",
        Pct >= Cut, "#F9A825",
        "#C62828"
    )
```

The measure recalculates as the slicer changes, and the callout re-colors on the next render. This is the fastest way to tune a threshold against real distributions rather than guessing.

## Where KPI formatting breaks

**The measure returns a number, not a color.** If the field is typed as a decimal, the `fx` dialog will accept it but the visual falls back to the default color. Fix: set the data type to Text and confirm the format string is not stripping the value.

**Blank filter context.** When a date or region has no rows, the measure may return `BLANK()` and the callout renders in the default color instead of your grey. The `ISBLANK` branch above handles that, but only if the base measure truly returns blank rather than zero. Use `ISBLANK` on the result of a measure that has no `+ 0` coercion.

**Row-level security interacts with color rules.** A user who cannot see a region's target rows may get a different `Sales vs Target %` than you do, and therefore a different color. That is correct behavior, but it surprises people during UAT. If the color must be identical for all viewers, base it on a measure that ignores the RLS-dimension filter, which is rarely what you want.

**Performance on DirectQuery.** Color measures are evaluated per visual render. In DirectQuery mode, a measure that triggers an extra round trip per cell adds latency. If the KPI sits on a busy page, consider moving the color logic into the model as a calculated column only when the granularity is stable, or switch the page to Import mode. See the rule-of-thumb trade-offs in our DirectQuery vs Import mode breakdown.

## Alternative: the Card (new) visual

If your requirement is "show the number, color the background red when it is bad, and show a status icon", the newer Card visual is a better fit. It has a **Status** format section where you bind a color measure directly, and it supports multiple callout values in one card. The KPI visual remains useful when you specifically want the target line and the trend sparkline in a compact footprint.

## FAQ

### Q: Why does my KPI callout ignore the color measure and stay black?

Almost always a data type problem. Open the measure in the Modeling tab and set **Data type** to Text and **Format** to Text. Conditional formatting reads the measure's output as a string; if Power BI sees a numeric type it discards it and applies the default theme color. If the type is already Text, check that the measure is not returning `BLANK()` for the current filter context, because blank resolves to the fallback color rather than your hex value.

### Q: Can I color the trend sparkline and the callout with the same measure?

Yes, but you have to bind it twice. The `fx` button on **Trend axis > Color** and on **Indicator > Callout value** are independent. Point both at the same measure if you want them synchronized, or use two measures when the trend should follow a different rule (for example, color the sparkline by month-over-month change while the callout follows year-to-date attainment).

### Q: Does the direction of the KPI arrow follow my color rule?

No. The up/down arrow and its "good/bad" coloring come from the **Trend line** setting and the target value configured on the visual, not from a conditional formatting measure. If the arrow says "good" while your callout is red, your target and your threshold measure disagree. Align them or accept that the two signals carry different meanings.

### Q: How many thresholds can I encode before the measure gets slow?

There is no hard limit, but each branch adds a comparison. A `SWITCH ( TRUE (), ... )` with eight to ten branches on a measure that already performs a division is still cheap at typical visual cardinality. The cost becomes noticeable when the measure scans a large fact table per cell and the KPI page has many visuals. Use `VAR` to compute shared subexpressions once, and profile the page with Performance Analyzer before optimizing blindly.

## Related Reading

- [Conditional formatting in Power BI: the complete overview](/tutorials/conditional-formatting-power-bi/)
- [Conditional formatting based on a measure](/tutorials/conditional-formatting-based-on-measure/)
- [Conditional formatting for charts](/tutorials/conditional-formatting-charts-power-bi/)
- [Bar chart conditional formatting](/tutorials/bar-chart-conditional-formatting/)
- [Gauge conditional formatting](/tutorials/gauge-conditional-formatting/)
- [Line chart conditional formatting](/tutorials/line-chart-conditional-formatting/)
- [Copy conditional formatting between visuals](/tutorials/copy-conditional-formatting-power-bi/)
- [The SWITCH function in DAX](/tutorials/dax-switch-function/)
- [DAX variables: best practices](/tutorials/dax-variables-best-practices/)
- [Filter context vs row context explained](/tutorials/filter-context-row-context-explained/)
- [DirectQuery vs Import mode](/tutorials/directquery-vs-import-mode/)
- [Power BI performance analyzer guide](/tutorials/power-bi-performance-analyzer-guide/)
