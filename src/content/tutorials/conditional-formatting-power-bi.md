---
title: "Conditional Formatting in Power BI: A Complete Guide (Based on Measure, Formula & Text)"
description: "Learn every type of conditional formatting in Power BI — background color, font color, data bars, and icons — plus how to drive them with a measure, a formula, or a text field. Includes copy-paste DAX and real Contoso examples."
pubDate: 2026-07-20
category: "visualization"
difficulty: "Beginner"
tags: ["visualization", "conditional-formatting", "color-rules", "data-bars", "matrix", "based-on-measure", "field-value"]
author: "Power BI Tutorials Team"
featured: false
---

A matrix with 200 cells of raw numbers is unreadable. The same matrix with conditional formatting reveals patterns instantly — high values stand out, low values fade, and outliers draw the eye. Most tutorials stop at "pick a color scale." They don't show you how to make formatting follow your actual business logic, which is where the real value is. This guide covers all four formatting types and then goes deeper: how to drive each one with a measure, a formula, or plain text.

## The four formatting types

### 1. Background color scaling

Shades each cell based on its value, from a minimum color (e.g., light) to a maximum color (e.g., dark).

**When to use:** comparing values across a range, where relative magnitude matters.

**How to apply:** click the dropdown next to a measure in a visual → Conditional formatting → Background color.

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

## Pattern 4: Highlighting outliers

Use field-based formatting to highlight cells that meet a specific condition (e.g., revenue above a threshold).

```dax
// Measure that returns a color hex code
Revenue Color =
IF([Total Revenue] > 50000, "#FF6B6B", "#FFFFFF")
```

Apply this as the background color via "Field value" formatting. Cells above 50,000 get a red background; others stay white.

## Conditional formatting based on a measure

This is the pattern most people search for and the one that delivers the most control. Instead of letting Power BI auto-scale colors, you write a measure that returns a color, then point the formatting at that measure using **Field value**.

The setup is always the same:

1. Write a measure that returns a hex color string (or a number, if you want Power BI to map it onto a color scale).
2. In the visual, open the column/measure dropdown → **Conditional formatting** → **Background color** (or Font color).
3. Set **Format by** to **Field value**.
4. Pick your color measure.

Here's a practical example using Adventure Works. Suppose you want a region to turn green when it beats its sales target by more than 5%, amber when it's within 5% below target, and red when it's worse than that.

```dax
// Returns a hex color based on a measure ratio
CF Sales vs Target =
VAR Pct = DIVIDE([Total Sales], [Sales Target], 0)
RETURN
    SWITCH(
        TRUE(),
        Pct > 1.05, "#22C55E",   // green: > 5% over target
        Pct >= 0.95, "#F59E0B",  // amber: within 5% of target
        "#EF4444"                // red: more than 5% under target
    )
```

Point Background color → Field value → `CF Sales vs Target`. Now the color reflects your real business rule, not Power BI's guess about the data range.

You can also return numbers instead of colors. If you feed a measure that returns 0, 1, or 2 into **Format by: Field value** with a color scale, Power BI maps those numbers onto your chosen gradient. That's useful when the logic is simpler as an index.

```dax
// Returns an index: 2 = good, 1 = ok, 0 = bad
CF Status Index =
VAR Pct = DIVIDE([Total Sales], [Sales Target], 0)
RETURN
    SWITCH(
        TRUE(),
        Pct > 1.0, 2,
        Pct >= 0.9, 1,
        0
    )
```

Apply a three-color scale to this index with green at 2, yellow at 1, red at 0.

## Conditional formatting based on a formula

When you don't need a full DAX measure, the **Rules** option lets you build conditional formatting directly from the field value. This is the fastest route for one-off formatting and for non-numeric logic.

Open the column dropdown → **Conditional formatting** → **Font color** → **Format by: Rules**.

Each rule has three parts:
- **Field:** the column or measure the rule evaluates
- **Operator:** is greater than, is less than, contains, begins with, is blank, and more
- **Value:** a number, text, or other column

Common rule patterns:

**Numeric thresholds:**
- If `[Total Sales]` **is greater than** `1000000` → green font
- Else if `[Total Sales]` **is less than** `100000` → red font

**Text contains:**
- If `[Region]` **contains** `West` → blue font

**Date rules:**
- If `[Order Date]` **is after** `August 1, 2026` → purple font

The catch: rules evaluate the formatted field only. If you want a cell's color to depend on a *different* column, you need a measure (the previous section) or a calculated column. Rules can't reference arbitrary other columns directly.

```dax
// Use a calculated column when rule needs another column's value
Is High Priority =
IF(
    Sales[Region] = "West" && Sales[Total Sales] > 500000,
    "Yes",
    "No"
)
```

Then apply a rule: If `[Is High Priority]` **is** `Yes` → orange background.

## Conditional formatting based on text

Text columns can't be color-scaled the way numbers can, but they're some of the most useful formatting targets — status, category, region, owner. You have two routes.

**Route A: Rules with text operators.** As above, use **contains**, **begins with**, or **is** to map text values to colors. A column of order statuses (Shipped, Pending, Cancelled) maps cleanly:

- `[Status]` **is** `Shipped` → green
- `[Status]` **is** `Pending` → amber
- `[Status]` **is** `Cancelled` → red

**Route B: A measure that translates text into color.** When the text logic is reusable across multiple visuals, wrap it in a measure so you maintain it in one place.

```dax
// Text-to-color measure for an Order Status column
CF Order Status =
SWITCH(
    SELECTEDVALUE(Orders[Status]),
    "Shipped", "#22C55E",
    "Pending", "#F59E0B",
    "Cancelled", "#EF4444",
    "Returned", "#8B5CF6",
    "#64748B"   // default gray for anything else
)
```

Apply as Field value → Background color on any visual that shows `Orders[Status]`. If you later add a "Refunded" status, you edit one measure instead of hunting through every visual.

**Combining text and value:** a real report often needs both. At Contoso, the shipping manager wants overdue orders flagged red, but only when the status is still "Pending." That's a measure, not a rule:

```dax
CF Overdue Pending =
VAR DaysLate = DATEDIFF(SELECTEDVALUE(Orders[Due Date]), TODAY(), DAY)
VAR Status = SELECTEDVALUE(Orders[Status])
RETURN
    IF(Status = "Pending" && DaysLate > 0, "#EF4444", "#FFFFFF")
```

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

**Mistake 5: Pointing Field value at the wrong aggregation.** When you use a color measure via Field value, make sure the measure is at the same granularity as the visual. A color measure that returns one value for the whole table will paint every cell the same color.

## FAQ

**Can I copy conditional formatting from one visual to another?**
There's no native "copy formatting" button between unrelated visuals, but you can reuse the same color measure across every visual, which achieves the same result. For report-level consistency, a JSON theme applied in the report settings carries color rules across visuals. See our guide on [copying conditional formatting](/tutorials/copy-conditional-formatting-power-bi/).

**Does conditional formatting slow down my report?**
Field-value formatting that relies on a heavy measure adds DAX evaluation per cell, so yes, it can — but only noticeably on very large matrices. Keep color measures simple (SWITCH + DIVIDE, no iterators) and you'll be fine.

**Why does my text-based rule color every cell the same?**
Usually because the rule field and the visual field don't match, or the text has trailing spaces. Trim the source column in Power Query and confirm the rule field equals the exact displayed value.

**Can I format charts the same way as tables?**
Partially. Charts use "Data colors" conditional formatting rather than cell rules. Bar charts, gauges, and KPI visuals all support it differently. We cover the specifics in [conditional formatting for charts](/tutorials/conditional-formatting-charts-power-bi/).

## What's next

- [How to Copy Conditional Formatting in Power BI](/tutorials/copy-conditional-formatting-power-bi/) — reuse color rules across visuals and reports without rebuilding them.
- [Conditional Formatting for Charts, Bar Charts & Gauges](/tutorials/conditional-formatting-charts-power-bi/) — apply color logic to visual elements, not just matrix cells.
- [The DAX SWITCH Function Explained](/tutorials/dax-switch-function/) — the backbone of most color measures in this guide.
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

