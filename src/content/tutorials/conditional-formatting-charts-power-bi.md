---
title: "Conditional Formatting for Power BI Charts & Gauges"
description: "Charts use Data colors, not cell rules. Colour a bar, column, line or gauge by value, rule or measure, add a dynamic target, and keep KPI colours consistent."
pubDate: 2026-08-28
updatedDate: 2026-09-24
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "conditional-formatting", "bar-chart", "gauge", "data-colors", "kpi"]
author: Mireia
featured: false
---

Conditional formatting on a matrix is one thing — you pick a color scale and move on. Charts are different. There are no "cells," so Power BI uses **Data colors** conditional formatting, and each visual type handles it a little differently. A bar chart colors by category; a gauge colors its fill by a single value; a KPI visual leans on its own status logic. This guide covers the two charts people ask about most — bar/column charts and gauges — in depth, then points you to the dedicated guides for [line charts](/tutorials/line-chart-conditional-formatting/) and [KPI cards](/tutorials/kpi-conditional-formatting/).

## How chart conditional formatting works

For any chart, select the visual → **Format pane → Data colors → Conditional formatting (fx)**. You get three options:

- **Format by: Color scale** — gradient mapped to a field's values.
- **Format by: Rules** — thresholds mapped to specific colors.
- **Format by: Field value** — a measure returns a hex color per data point.

The big difference from matrices: the color usually applies **per category or per data point**, not per cell. A bar chart with regions on the axis gives each region its own color.

## Bar and column charts

### The three conditional formatting paths

Power BI exposes conditional formatting for bar and column colors in three ways:

1. **Rules** — you define numeric thresholds (for example, above 1,000,000 = green, below = red). Simple, but the thresholds are static text you type into a dialog.
2. **Gradient** — Power BI maps the minimum and maximum of the current axis to two colors or a color scale. The mapping recalculates with the filter context, so it always spans the visible range.
3. **Field value** — a measure returns a color for each bar. This is the most flexible option and the only one that can react to a slicer, a target table, or a prior-year comparison.

A fourth path exists on some visuals (Rules with a "Field" source for the threshold itself), but for bar charts the three above cover almost every real requirement.

### Step-by-step: formatting bars with rules

Rules are the fastest way to get colored bars, and they work fine when your thresholds do not change.

1. Select the bar chart on the canvas.
2. Open the **Format visual** pane (the paintbrush icon).
3. Expand **Bars** (or **Columns** if you rotated the chart).
4. Next to **Color**, click the **fx** button. In newer versions the same button appears as a small calculator icon inside the color dropdown.
5. In the *Format style* dropdown, choose **Rules**.
6. Set *Apply to* to **Color by** and pick the field the rules should evaluate — typically your measure, such as `Total Sales`.
7. Define the rule: *if value is* **>=** *and* **is less than** a number, then choose a color. Use **+ New rule** to add more bands.

A common beginner mistake is leaving *Summarization* on the wrong aggregation. If the rule panel shows *Sum of Sales* but your chart plots a measure named *Total Sales*, the rule evaluates a different number than the bar height and the colors will look wrong. Match the field exactly.

Rules are evaluated against the aggregated value per category in the current filter context. They do not consider other bars, so a bar chart of monthly sales with a fixed rule "> 500K = green" will show exactly the months that passed the bar — no relative logic.

### Gradient formatting for relative comparisons

Gradient formatting does the opposite: it ignores absolute thresholds and colors bars relative to the smallest and largest values currently on the axis.

In the same **fx** dialog, choose **Gradient** as the format style, then set:

- *Minimum* value and color
- *Maximum* value and color
- Optionally a **Center** value and color for a diverging scale

If you leave minimum and maximum blank, Power BI uses the current range of the data. When a slicer filters the chart down to three months, those three bars re-scale — the largest of the three becomes the "maximum" color. That is usually desirable for a heatmap-style bar chart and usually undesirable if your audience reads color as an absolute signal. Decide which reading you want before you pick gradient.

For a diverging scale (for example, red below target, green above), set the center to your target value and give the low end and high end contrasting colors. This is the cleanest way to build a variance bar chart.

### Color by a measure (most control)

The Field value option is where conditional formatting stops being cosmetic. When you choose *Format style → Field value*, Power BI asks for a field or measure that returns a color. The measure must return a valid color string, and it is evaluated in the same filter context as the bar.

The usual pattern is a `SWITCH` over a comparison:

```dax
Bar Color =
VAR Target = 500000
VAR Actual = [Total Sales]
RETURN
    SWITCH(
        TRUE(),
        Actual = BLANK(), "#D9D9D9",
        Actual >= Target * 1.1, "#1F7A3D",
        Actual >= Target, "#8CC63F",
        Actual >= Target * 0.9, "#F5A623",
        "#D0021B"
    )
```

Two things matter here. First, `SWITCH(TRUE(), ...)` evaluates conditions in order and returns the first match, so the most specific band must come first. Second, the color strings are hex literals wrapped in quotes — Power BI expects text, not a color object.

You can also return named colors such as `"red"` or `"Green"`, but hex codes give you control over the exact shade. Avoid returning `BLANK()` when you actually want a neutral color; blank may fall back to the visual default, which is rarely what you intended. Return an explicit hex value instead. Microsoft documents every case in the [BLANK reference](https://learn.microsoft.com/en-us/dax/blank-function-dax).

The same pattern works for category-vs-target coloring — point **Data colors → fx → Field value** at a measure that compares each bar to its own target, and the logic lives in one measure you can reuse across every bar chart in the report:

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

### Making the color react to a slicer

Because the measure is evaluated per category, it already reacts to filters applied to the visual. If a slicer limits the chart to one region, only that region's bar is drawn and colored. What the measure cannot do on its own is react to a *selection* made somewhere else on the page, unless the two visuals are related through the filter context. Use **Edit interactions** if you need a table selection to drive the colors.

### Coloring by rank (top N)

A frequent request is "color the top 3 bars." That needs a rank, not a value comparison. The measure below ranks categories by sales and colors the top three:

```dax
Top 3 Color =
VAR SalesRank =
    RANKX(
        ALLSELECTED( Products[Category] ),
        [Total Sales],
        ,
        DESC,
        DENSE
    )
RETURN
    IF( SalesRank <= 3, "#1F7A3D", "#BFBFBF" )
```

`ALLSELECTED` keeps the ranking inside the current slicer scope, so changing a slicer re-ranks the categories, and `DENSE` avoids gaps when two categories tie. Note that `RANKX` needs a table expression as its first argument — passing a single column works, but passing the full table lets the measure include any category present in the filter context.

### Rules versus Field: which to choose

| Situation | Best option |
|---|---|
| Fixed business thresholds that rarely change | Rules |
| Quick heatmap look, relative to current data | Gradient |
| Thresholds stored in a table or driven by a slicer | Field (DAX) |
| Color depends on rank, prior year, or multiple conditions | Field (DAX) |
| One-off visual for a static report | Rules or Gradient |

If you find yourself typing thresholds into the rules dialog every quarter, move them into a small parameter table and read them with a measure. That single change removes an entire class of report maintenance.

### Bar pitfalls

- **Wrong field in the rule.** The formatting field must be the measure plotted on the axis, not a raw column with a different aggregation.
- **Gradient hiding the signal.** When all values are similar, a gradient makes small differences look dramatic. Use a fixed min/max when the comparison should be stable.
- **Text instead of color.** A measure that returns a number for the color field silently falls back to the default. Return a string.
- **Palette clashing with the report theme.** Custom hex colors ignore the report theme, so a theme change will not update them. If you rely on theming, keep custom colors to a minimum.

### Bar FAQ

**Can I apply conditional formatting to the data labels as well as the bars?**
Yes. In the Format pane, open **Data labels**, expand **Values**, and use the same **fx** dialog on the *Color* property. You can point labels at the same measure you used for the bars, or a different one if you want the label color to encode something else, such as profit margin.

**Why does my DAX color measure return the same color for every bar?**
The measure is almost certainly being evaluated without the per-category context you expected — for example, you referenced a column from a table that is not on the axis, or you wrapped the result in `CALCULATE` with a filter that removes the category filter. Check that the measure references the axis field through the filter context rather than hard-coding a single value.

**Do conditional formatting rules work in Power BI Service after publishing?**
They carry over with the report file. Rule-based formatting, gradient formatting, and measure-driven color all render in the Service the same way as in Desktop. What does not carry over is any formatting applied through the old Analytics pane preview features, which have been retired.

**Can conditional formatting read a target from a table instead of a hard-coded number?**
Yes, and this is the main reason to use the Field option. Create a one-row target table, relate or cross-filter it as needed, and replace `VAR Target = 500000` with `VAR Target = SELECTEDVALUE( Targets[Value] )`. The measure then re-colors every bar when the target row changes.

## Gauges and KPI visuals

### Why gauges resist simple conditional formatting

Open the Format pane for a gauge and you will find Fill, Target, and Callout value sections. Each one accepts a color, but the classic "fx" conditional formatting button that appears on tables and matrices is not always available. Gauge visuals expose color as a property, not as a format rule with a data-driven binding.

That limitation shapes the whole approach. Instead of relying on the built-in conditional formatting dialog, you drive gauge appearance through three levers:

1. A **dynamic maximum** measure, so the gauge rescales as data changes.
2. A **dynamic target** measure, so the goal line tracks period-specific quotas.
3. **Rule-based color logic** applied through fields, or by swapping visuals, since the gauge color itself is largely static in the standard visual.

If you have already worked with [conditional formatting in Power BI](/tutorials/conditional-formatting-power-bi/), you know the pattern: either a rules-based gradient or a field value that returns a hex color. Gauges support the second pattern partially, and understanding where the boundary sits saves a lot of trial and error.

### Step 1: Build the base measures

Start with three measures: the actual value, the target, and a maximum for the gauge axis. Keeping the maximum separate from the target is important because a gauge where the target sits at 100% of the axis leaves no headroom to show a value that exceeds goal.

```dax
Total Sales = SUM ( Sales[SalesAmount] )

Sales Target =
CALCULATE (
    SUM ( Targets[TargetAmount] ),
    ALLEXCEPT ( Targets, Targets[Region] )
)

Gauge Max =
VAR CurrentTarget = [Sales Target]
VAR CurrentSales = [Total Sales]
RETURN
    MAX ( CurrentTarget, CurrentSales ) * 1.25
```

See the [MAX reference](https://learn.microsoft.com/en-us/dax/max-function-dax) for the complete rules.

The `Gauge Max` measure multiplies the larger of target or actual by 1.25. That produces a stable axis with visible headroom. A hard-coded maximum like 1000000 breaks the moment a region reports a different scale.

Drop `Total Sales` into the **Value** field, `Sales Target` into **Target**, and `Gauge Max` into **Maximum value**. The gauge now rescales per region or period automatically.

### Step 2: Make the target dynamic

A static target is rarely what a business wants. Quotas shift by month, by territory, and by product line. If your `Targets` table has a date column, extend the measure so it respects the current filter context on dates:

```dax
Sales Target =
VAR SelectedDate = MAX ( Dates[Date] )
RETURN
    CALCULATE (
        SUM ( Targets[TargetAmount] ),
        Targets[TargetMonth] = SelectedDate
    )
```

This pattern uses a proper relationship between the `Targets` table and the `Dates` table. If that relationship is missing, `CALCULATE` will not filter as expected and the target will read as a flat total. This is the same filter context behaviour covered in [filter context and row context explained](/tutorials/filter-context-row-context-explained/), and it trips up most beginners on their first dynamic target.

### Step 3: Apply rule-based color to the fill

The gauge fill color follows the **Fill** property in the Format pane. Two practical routes exist for rule-based color.

**Route A: rules by value.** Expand Fill, click the color swatch, and in older builds you will see a **Conditional formatting** option. Set rules such as "if value is greater than or equal to target, use green; if between 80% and 100%, use amber; otherwise red." The rules evaluate against the measure placed in the Value field.

**Route B: swap the visual.** Because the standard gauge treats color as a format property rather than a data binding, the more reliable technique is to build three gauge copies stacked in a bookmark group, each pre-colored, and show the correct one via a bookmark. That is heavier, but it always works. If you go this direction, the mechanics are documented in [bookmarks navigation in Power BI](/tutorials/bookmarks-navigation-power-bi/).

For most dashboards, Route A is enough. The rules evaluate the aggregated value shown in the gauge, so a single gauge in a card-stacked layout will color correctly per region. The most useful pattern is a measure that picks the color from the ratio to target:

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

### Step 4: Format the callout value

The callout value is the big number inside the gauge. It accepts the same color rules, but you must first place a measure in the Value field for the rules engine to have something to evaluate. Use a percentage measure rather than raw sales if the audience thinks in attainment terms:

```dax
Attainment % =
DIVIDE ( [Total Sales], [Sales Target] )
```

Format this as a percentage in the Format pane, then apply color rules at thresholds of 0.8 and 1.0. The reader sees green when attainment clears 100%, amber in the 80 to 100 band, and red below.

### Step 5: Color the target line

The target line inherits the **Target** color property. It does not support rule-based formatting in the standard gauge, so pick a neutral color that contrasts with all three fill states. A dark grey or near-black line reads clearly against green, amber, and red fills.

One trap: if the target measure returns blank for a period, the target line disappears and the gauge looks broken. Guard against this with `COALESCE`:

```dax
Sales Target =
COALESCE (
    CALCULATE ( SUM ( Targets[TargetAmount] ) ),
    0
)
```

A zero target still draws the line at the origin, which is visually honest and tells you the data is missing rather than the visual.

### When to skip the gauge

Gauges consume a lot of space for one number. If your dashboard compares five regions, a bar chart with a target reference line is denser and easier to scan. Gauges earn their place when there is exactly one KPI per gauge and the target is the whole story. For layout guidance, [dashboard design principles](/tutorials/power-bi-dashboard-design-principles/) covers the trade-offs.

### Gauge pitfalls

- **Static maximum.** The gauge rescales wrongly as soon as data grows.
- **No relationship to the date table.** The dynamic target collapses to a single flat value.
- **Rules referencing the wrong field.** Color rules evaluate the Value measure, not the Target. If you write a rule against the target, nothing changes.
- **Overlapping thresholds.** Boundaries like "greater than 0.8" and "less than 0.8" leave a gap at exactly 0.8. Use inclusive operators on one side.

### Gauge FAQ

**Can I apply conditional formatting directly to the gauge fill without a workaround?**
In most current Power BI Desktop builds, the Fill property supports a conditional formatting dialog with rules or a field value. If your build does not show it, the property still accepts a static color, and the bookmark-swap technique in Step 3 is the fallback. Check your Desktop version before committing to either approach.

**Why does my dynamic target show the same number for every month?**
Almost always a missing or inactive relationship between the targets table and the date table. `CALCULATE` filters along active relationships only. Either create the relationship or use `USERELATIONSHIP` inside the measure.

**Does the target line support rule-based color?**
No. The Target color is a static property. If you need a target line that changes color, replace the gauge with a bar chart or KPI card where the target marker can be controlled through the underlying data color binding.

**How do I stop the gauge from looking empty when the target is blank?**
Wrap the target measure in `COALESCE` with a fallback of zero, or better, a sensible default pulled from a prior period. Blank targets hide the goal line entirely and make the visual look unfinished.

**Is a gauge or a KPI card better for target tracking?**
A KPI card is more compact and supports a trend sparkline. A gauge is better when the visual weight of the dial itself helps the reader grasp proximity to target at a glance. For a single hero metric on an executive page, the gauge often wins; for everything else, a card or bar chart is more efficient.

### KPI visual status

The KPI visual has built-in **Status** and **Trend** formatting. Under **Format pane → Status**, you can set conditional colors for the indicator based on distance from target. This is effectively conditional formatting tuned for a single KPI — set the "good / neutral / bad" thresholds and Power BI colors the status accordingly. For an Adventure Works scenario: a KPI showing monthly sales turns green when at or above target, red when more than 20% below. Define those thresholds once and the KPI stays honest across every month the user filters to.

The KPI visual has enough unique behavior — the Card (new) visual, sparkline coloring, and threshold counts — that it gets its own dedicated walkthrough: [KPI Visual Conditional Formatting in Power BI](/tutorials/kpi-conditional-formatting/).

## Cards and other visuals

Cards don't support data colors conditional formatting the way charts do — but you can still drive their font or background color via **Field value** if the card shows a measure. The same `CF Region Sales` measure works; just apply it through the card's conditional formatting option for font/background. Keep cards minimal — one color rule is plenty.

## Common mistakes

**Mistake 1: Applying a gradient to a multi-series chart.** Each series scales independently and the colors become meaningless. Switch to rules or field value.

**Mistake 2: Forgetting the gauge has one value.** People try to color a gauge "per category" — there's only one data point, so use a measure based on the value-to-target ratio.

**Mistake 3: Hard-coding threshold colors in rules.** When the target changes monthly, hardcoded rules go stale. A measure referencing `[Sales Target]` stays correct automatically.

**Mistake 4: Too many colors on one bar chart.** Six regions in six colors with no logic is noise. Use a meaningful scale or rule, not a rainbow.

**Mistake 5: Static gauge maximum.** The gauge rescales wrongly the moment data grows. Drive the axis with a `Gauge Max` measure.

## What's next

- [Conditional Formatting in Power BI: A Complete Guide](/tutorials/conditional-formatting-power-bi/) — the measure and rule foundations for all chart formatting here.
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/) — go deeper on the DAX color measures used above.
- [How to Copy Conditional Formatting in Power BI](/tutorials/copy-conditional-formatting/) — reuse these color measures across every chart.
- [Line Chart Conditional Formatting in Power BI](/tutorials/line-chart-conditional-formatting/) — the dedicated line-chart walkthrough.
- [KPI Visual Conditional Formatting in Power BI](/tutorials/kpi-conditional-formatting/) — the dedicated KPI card walkthrough.
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/) — keep chart colors consistent with the rest of the report.
<!-- CF-CLUSTER-NAV -->

## More conditional formatting guides

- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting in Power BI](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting/)
- [Line Chart Conditional Formatting](/tutorials/line-chart-conditional-formatting/)
- [KPI Visual Conditional Formatting](/tutorials/kpi-conditional-formatting/)

## Related Reading

- [Conditional formatting generator: build the colour rule as a DAX measure](/tools/conditional-format-generator/)
- [Conditional formatting in Power BI: the full guide](/tutorials/conditional-formatting-power-bi/)
