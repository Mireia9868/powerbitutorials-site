---
title: "Power BI Conditional Formatting: Complete Guide (Formula, Measure, Text, Color Rules)"
description: "Learn Power BI conditional formatting based on formula, measure, and text. Covers background color, font color, data bars, icons, copy formatting, and design rules to make reports scannable."
pubDate: 2026-07-20
category: "visualization"
difficulty: "Beginner"
tags: ["visualization", "conditional-formatting", "color-rules", "data-bars", "matrix", "formula", "measure", "text-formatting"]
author: "Power BI Tutorials Team"
featured: false
---

A matrix with 200 cells of raw numbers is unreadable. The same matrix with conditional formatting reveals patterns instantly — high values stand out, low values fade, and outliers draw the eye. This guide covers every conditional formatting option in Power BI, including formula-based rules, measure-based formatting, and text-based formatting.

## The four formatting types

### 1. Background color scaling

Shades each cell based on its value, from a minimum color to a maximum color.

**When to use:** comparing values across a range, where relative magnitude matters.

**How to apply:** click the dropdown next to a measure in a visual → **Conditional formatting → Background color**.

**Settings:**
- **Color scale:** gradient from min to max. Choose two colors (e.g., white to blue) or three (e.g., red for low, yellow for mid, green for high).
- **Minimum / Maximum:** "Lowest value" / "Highest value" for dynamic scaling, or specific numbers for fixed thresholds.
- **Diverging:** enable if you have a meaningful midpoint (e.g., 0 for profit/loss, target for actual-vs-budget).

### 2. Font color scaling

Same as background, but changes the text color instead of the cell fill.

**When to use:** when background color would clash with other formatting, or when you want subtler emphasis.

**Tip:** use font color with a light background, or background color with dark text. Both together is usually too much.

### 3. Data bars

Draws a horizontal bar inside each cell, proportional to the value — like a mini bar chart within the matrix.

**When to use:** when you want both the exact value and a visual comparison.

**Settings:**
- **Bar color:** choose a single color or a gradient.
- **Border:** add a subtle border to separate the bar from the value.
- **Axis:** show or hide a vertical axis line at the zero point.

Data bars work best in narrow columns where the bar fills most of the cell width.

### 4. Icons

Adds an icon next to the value — arrows up/down, circles, flags, traffic lights.

**When to use:** highlighting direction (up/down) or status (good/warning/bad).

**Settings:**
- **Icon style:** arrows, circles, flags, or shapes.
- **Rules:** define thresholds (e.g., green arrow if value > 1000, yellow if 500–1000, red if < 500).
- **Layout:** icon only, icon left of value, or icon right of value.

**Caution:** icons are the most overused formatting type. Three icons per cell across 200 cells is visual noise. Use them sparingly — for status indicators, not for every value.

## Conditional formatting based on a formula

The "Rule" option in conditional formatting lets you apply formatting when a DAX expression returns true. This is useful when the condition depends on more than the cell value itself.

Example: highlight any region where revenue is above target AND growth is positive.

```dax
Format Flag =
IF(
    [Total Revenue] > [Target Revenue] && [YoY Growth %] > 0,
    1,
    0
)
```

In the conditional formatting pane, choose **Rules** and base the rule on the `Format Flag` measure. Set values equal to 1 to get a green background, and 0 to stay neutral.

**When to use a formula:**
- The condition involves multiple measures.
- You need AND/OR logic that a simple color scale can't express.
- You want to compare the cell value to a target or benchmark.

## Conditional formatting based on a measure

Sometimes you want the formatting of one column to depend on the value of another measure. Power BI lets you select **Field value** in the conditional formatting pane and point to a measure that returns a color name, hex code, or numeric flag.

Example: return a hex color based on profit margin.

```dax
Margin Color =
SWITCH(
    TRUE(),
    [Profit Margin %] >= 0.30, "#2E7D32",  -- green
    [Profit Margin %] >= 0.15, "#F9A825",  -- yellow
    "#C62828"                              -- red
)
```

Apply this measure as the **Background color → Field value**. The column does not need to display the margin measure — it just needs to exist in the model.

**Best practice:** keep the measure simple. Avoid complex filters inside the color measure because it runs once per visible cell.

## Conditional formatting based on text

Text columns can trigger conditional formatting too. You need a measure that evaluates the text value and returns a numeric flag or color.

Example: color rows where the product category is "Electronics".

```dax
Category Flag =
IF(
    SELECTEDVALUE(Products[Category]) = "Electronics",
    1,
    0
)
```

Use this flag in a rule-based background color. If you need different colors for multiple categories, return hex codes instead:

```dax
Category Color =
SWITCH(
    SELECTEDVALUE(Products[Category]),
    "Electronics", "#E3F2FD",
    "Furniture", "#F1F8E9",
    "Clothing", "#FFF3E0",
    "#FFFFFF"
)
```

Note: `SELECTEDVALUE` returns the single value in the current filter context. In a table or matrix, this works row by row.

## How to copy conditional formatting

To copy conditional formatting from one visual to another, use **Format painter**:

1. Select the visual with the formatting you want to copy.
2. Click the **Format painter** icon in the Home ribbon (it looks like a paintbrush).
3. Click the target visual.

Format painter copies most formatting settings, including conditional formatting rules, color scales, data bars, and icons. It does **not** copy field-level settings like which measure is in each column.

**Limitation:** format painter works within the same report page or across pages in the same file. It does not work across separate `.pbix` files. For reusable formatting across files, document your color hex codes and threshold rules, then recreate them manually.

## Pattern 1: Highlighting performance vs. target

A matrix showing actual revenue by region vs. target. Use diverging background color with the midpoint at 100% (on target).

- **Below 80%:** red
- **80–100%:** yellow
- **Above 100%:** green

```dax
// Measure used for formatting
Revenue vs Target Pct = DIVIDE([Total Revenue], [Target Revenue], 0)
```

Apply background color scaling to this measure with diverging colors and a midpoint at 1.0 (100%).

## Pattern 2: Trend indicators with icons

A table showing monthly revenue with a "trend" column. Use icons to show whether each month is up or down vs. the previous month.

```dax
// Measure for the trend column
Revenue Trend =
VAR Current = [Total Revenue]
VAR Previous = CALCULATE([Total Revenue], PREVIOUSMONTH(Date[Date]))
VAR Diff = Current - Previous
RETURN
    SWITCH(
        TRUE(),
        Diff > 0, 1,    // up
        Diff < 0, -1,   // down
        0               // flat
    )
```

Apply icon formatting with rules: 1 → green up arrow, -1 → red down arrow, 0 → gray circle.

## Pattern 3: Data bars in a matrix

A matrix showing revenue by product per month. Add data bars to the revenue values so each cell shows both the number and a proportional bar.

This combines the precision of numbers with the visual comparison of a bar chart — ideal for detailed analysis tables.

## Design principles

### Principle 1: One formatting type per cell

Don't combine background color, font color, data bars, and icons on the same value. Choose one that fits the goal.

### Principle 2: Use color intentionally

- **Red/green:** performance vs. target (but be mindful of colorblindness — use icons as a backup).
- **Blue scale:** magnitude comparisons.
- **Single color with intensity:** clean, professional look.

### Principle 3: Don't format everything

Conditional formatting on every cell of every visual is exhausting. Apply it where comparison adds value — matrices, tables, and specific KPIs. Leave cards and chart visuals alone.

### Principle 4: Test for colorblindness

Red/green is the most common formatting choice and the most common accessibility failure. Use a colorblind-friendly palette (e.g., blue/orange) or add icons as a redundant signal.

## Common mistakes

**Mistake 1: Using default colors without checking contrast.** A light yellow font on a white background is invisible. Test formatting with actual data.

**Mistake 2: Forgetting to handle blanks.** Blank cells may show formatting (or not) depending on the rule. Use "Show a blank value" in the formatting settings to control this.

**Mistake 3: Over-formatting small tables.** A table with 5 rows doesn't need conditional formatting — the numbers are already comparable. Save formatting for tables and matrices with 20+ cells.

**Mistake 4: Not updating formatting after changing measures.** If you swap the measure in a visual, the conditional formatting may point to the old measure. Check formatting settings after any measure change.

## FAQ

**Can Power BI conditional formatting use a formula?**
Yes. Choose **Conditional formatting → Background color (or font color) → Rules** and write a DAX expression that returns true or false. You can also use a measure that returns a numeric flag.

**Can conditional formatting be based on another measure?**
Yes. Select **Field value** in the conditional formatting pane and point to a measure that returns a color hex code or numeric flag. The target column's formatting will then depend on that measure.

**How do I conditionally format text in Power BI?**
Create a measure that evaluates the text value (using `SELECTEDVALUE`) and returns a flag or color. Then apply that measure as a rule-based or field-value background color.

**How do I copy conditional formatting to another visual?**
Use the **Format painter** tool in the Home ribbon. Select the source visual, click Format painter, then click the target visual. It copies conditional formatting rules, color scales, data bars, and icons.

**Why is my conditional formatting not showing?**
Common causes: the measure returns blank, the threshold is wrong, the color contrast is too low, or the formatting is applied to a different field than you expect. Check the conditional formatting pane and test with a simple rule first.

## What's next

- [Power BI Performance Optimization: Make Slow Reports Fast](/tutorials/power-bi-performance-optimization/)
- [DAX Variables Guide: Cleaner, Faster Measures](/tutorials/dax-variables-guide/)
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)

## Summary

Conditional formatting turns walls of numbers into scannable visuals. Use background color for magnitude comparisons, data bars for combined precision and visual comparison, and icons for direction or status. Formula-based and measure-based formatting give you precise control over when colors apply. Apply one formatting type per cell, choose colors intentionally, and test for accessibility. The goal is to make patterns visible — not to color every cell for the sake of it.
