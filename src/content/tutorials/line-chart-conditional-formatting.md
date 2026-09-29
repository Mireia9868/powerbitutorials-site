---
title: "Line Chart Conditional Formatting in Power BI"
description: "A line chart in Power BI is built from a category axis, a value axis, and one or more series."
pubDate: 2026-09-29
category: visualization
tags: ["conditional formatting", "line chart"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What Line Chart Conditional Formatting Actually Changes

A line chart in Power BI is built from a category axis, a value axis, and one or more series. Conditional formatting on that visual does not recolor the whole line in the way people expect from a table or matrix. The formatting targets narrow, well-defined properties:

- **Data point colors** — the markers or the line segments at each category, driven by a color rule.
- **Line series colors** — one color per series when you have multiple measures.
- **Data labels** — font and background color per data point.
- **Markers** — shown or hidden, with a per-point color.
- **Legend** — color only, and only when the visual uses series-level formatting.

The important nuance: a line needs at least one point per category to carry a color. If you turn off markers *and* use a rule that colors points, nothing appears to change, because the colored element is invisible. Always enable markers when you test a point-level rule, then decide whether to keep them on.

![Figure 1: Line chart with per-point conditional formatting on revenue](placeholder)

## Prerequisites

Before you start, confirm the following:

1. Your model has a date or category column on the axis and at least one numeric measure.
2. The measure returns values for most categories. Gaps on the axis come from missing rows, not from formatting.
3. You build the color logic as a measure rather than a calculated column, unless the rule only needs row-level inputs.

The last point matters. A calculated column is evaluated once at refresh and stored, so it cannot react to slicers, filters, or a visual-level context. A measure is evaluated at query time and can respond to anything the user clicks. For formatting rules that change with a slicer, you need a measure.

```dax
Revenue = SUM ( Sales[Revenue Amount] )

Revenue Color =
VAR CurrentRevenue = [Revenue]
VAR Target = [Revenue Target]
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( CurrentRevenue ), "#B3B3B3",
        CurrentRevenue >= Target, "#2E7D32",
        CurrentRevenue >= Target * 0.8, "#F9A825",
        "#C62828"
    )
```

That measure returns a hex string. Power BI accepts hex strings for the **Format by: Field value** option in the color dialog.

![Figure 2: Assigning a measure to the conditional color of a line chart](placeholder)

## Step 1: Open the Conditional Formatting Dialog

Select the line chart. In the Visualizations pane, open the **Format** tab (the paint roller, not the magnifier). Expand the section that holds the element you want to color.

- For per-point colors: **Markers** > **Color** > click the **fx** icon.
- For per-series colors: **Lines** > **Color** > **fx**.
- For data labels: **Data labels** > **Color** > **fx**.

The **fx** icon only appears when the property supports conditional formatting. If you do not see it, you are on the wrong property.

## Step 2: Choose the Formatting Type

The dialog offers three options.

**Gradient.** Maps a continuous measure onto a two- or three-color scale with a minimum and maximum. Good for revenue, margin percentage, or any value with a natural midpoint. It requires a numeric field.

**Rules.** You define thresholds manually. Each rule has a condition (greater than, less than, between, is blank) and a color. Good for bucketing values into bands without writing DAX.

**Field value.** You supply a measure that returns either a hex color string or a color name. This is the most flexible and the only option that lets you apply business logic such as "color by region" or "color the point only if it beats the prior period."

For the running example, choose **Field value** and select `Revenue Color`.

![Figure 3: Format by field value using a DAX measure](placeholder)

## Step 3: Use Rules When You Do Not Need DAX

Rules are faster to set up and easier to hand off to someone who does not read DAX. A common pattern for a margin line:

1. Format style: **Rules**
2. Summarization: **Average** (or Last, depending on the axis)
3. Rule 1: value is `>= 0.3` and `< 1` → green
4. Rule 2: value is `>= 0.2` and `< 0.3` → amber
5. Rule 3: value is `>= 0` and `< 0.2` → red
6. Enable **If value is blank** and set gray.

Rules are evaluated top to bottom. The first match wins, so put the tightest band first. If two rules overlap, the upper one takes precedence and the lower never fires.

One limitation: rules apply to the field you choose in **Based on field**, and that field must be in the visual. If your threshold depends on a measure you do not want on the chart, use a field-value measure instead and hide the measure from the tooltip if needed.

![Figure 4: Rule-based formatting with three thresholds](placeholder)

## Step 4: Color by a Related Dimension

"Color this line green when the product is profitable" is dimension-driven, not value-driven. Write a measure that reads the dimension in the current context:

```dax
Profitability Color =
SWITCH (
    SELECTEDVALUE ( Products[Profitability Band] ),
    "High", "#1565C0",
    "Medium", "#FB8C00",
    "Low", "#6A1B9A",
    "#9E9E9E"
)
```

`SELECTEDVALUE` returns the value only when exactly one row of `Products[Profitability Band]` is in context. On a line chart with product on the legend, each series has one product in context per data point, so it works. If the legend holds a category with many products, the measure returns the fallback color. That is usually the correct behavior, but verify it rather than assuming.

Note the distinction from `EARLIER`: that function needs a nested row context, which a measure does not naturally have. Reach for `SELECTEDVALUE` or `VALUES` here, not `EARLIER`. See the dedicated EARLIER article in Related Reading if you need to understand when it does apply.

## Step 5: Test and Troubleshoot

Common failures and their causes:

| Symptom | Cause |
|---|---|
| Nothing changes | Markers are off, or the rule is applied to the wrong property |
| All points same color | Measure returns a constant; check the filter context |
| Colors do not respond to a slicer | You used a calculated column, not a measure |
| Blank points stay unformatted | No rule for `ISBLANK`; add one |
| Colors differ from expected hex | Theme overrides, or you pasted a name Power BI does not recognize |

To confirm the measure is correct, drop it into a table visual with the axis field. The values you see are exactly what the color rule receives. If the table looks right and the chart does not, the problem is the formatting property, not the DAX.

![Figure 5: Table visual used to debug the color measure](placeholder)

## Performance Notes

Field-value formatting runs one extra measure evaluation per data point. On a line chart with 500 points and four series, that is 2,000 additional evaluations. Simple SWITCH and comparison logic is negligible. Avoid measures that scan large fact tables inside the color logic, and never call an iterator over the fact table just to pick a color. If the visual feels slow, check it in Performance Analyzer before blaming the rule.

## When Not to Use Conditional Formatting

Conditional formatting adds cognitive load. If a single threshold is the story, an analytic reference line or a constant line drawn at the target is clearer than recoloring points. Use point-level color when the pattern across categories matters, for example spotting spikes above target across a twelve-month axis. Use series color when the meaning is categorical and stable.

## FAQ

### Q: Why does my line chart ignore the conditional formatting measure?

Check three things. First, confirm you applied the rule to **Markers > Color** or **Lines > Color**, not to a title or background. Second, turn markers on so a colored element is visible. Third, verify the measure returns a valid hex string such as `#C62828` with a leading hash and six digits. A measure returning `"red"` works, but returning `255,0,0` does not.

### Q: Can I format only the section of a line above a threshold?

Not directly. Power BI colors points, not segments between points. The common workaround is to duplicate the measure, return `BLANK()` below the threshold in one copy and `BLANK()` above it in the other, and place both on the chart. The two lines overlap at the crossing point and read as one line with two colors. Disable markers on both or you will see a color seam at every category.

### Q: Does conditional formatting survive a theme change or a copied visual?

The rule survives, but the theme can override colors if the rule uses theme-relative colors. Copying a visual with **Ctrl+C** and **Ctrl+V** within the same report keeps the rule intact, including the measure reference. Copying to a different report requires the measure to exist there too, or the format resets to a default color.

### Q: Can the color measure reference another visual's selection?

No, there is no cross-filter between measures. What the measure can see is the filter context of its own data point, which includes slicers, page filters, and cross-filtering from other visuals on the page. If a user clicks a bar in a separate chart, the line chart's points are filtered and the color measure recalculates for the remaining points.

### Q: Why do some points stay gray when I have a rule for blanks?

The blank rule fires only when the measure itself returns `BLANK()`. A value of zero is not blank. If your underlying data has zeros for months with no sales, apply a rule for `= 0` separately, or wrap the measure so zeros return `BLANK()`.

## Related Reading

- [Conditional Formatting in Power BI: The Complete Guide](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting for Charts in Power BI](/tutorials/conditional-formatting-charts-power-bi/)
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting-power-bi/)
- [SWITCH Function in DAX](/tutorials/dax-switch-function/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX Variables Best Practices](/tutorials/dax-variables-best-practices/)
- [Power BI Visual Types Guide](/tutorials/power-bi-visual-types-guide/)
- [Power BI Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer-guide/)
