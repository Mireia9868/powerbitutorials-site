---
title: "Conditional Formatting Based on a Measure in Power BI"
description: "Rule-based formatting only goes so far. Drive colours from a DAX measure instead, with a worked example and copy-paste formulas."
pubDate: 2026-09-28
category: visualization
tags: ["conditional formatting", "measures"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

Conditional formatting in Power BI splits into two worlds. The simple one is rules you set from a field in your data: sales above a threshold turn green, below turn red. The more useful one is rules driven by a DAX measure. A measure lets you color a cell by margin percentage, by variance to target, by a rank, by a running total, or by whether this month beat last month. None of those can be expressed by pointing at a single column, and that is exactly where most people get stuck.

This tutorial walks through the whole flow: writing a measure that returns something the formatter can interpret, wiring it into a table or matrix, doing the same for a chart, and debugging the cases where the color simply does not show up.

## What conditional formatting actually consumes

Before touching the format pane, understand the contract. Power BI formats a cell, bar, or data point using one of three inputs:

- **Color by value (gradient):** a numeric field or measure. Power BI maps the lowest value to one color and the highest to another, interpolating between them.
- **Color by rules:** a set of conditions. Each rule compares a field or measure against a constant and assigns a color.
- **Color by field (format style = Field value):** a measure or column that returns a color string, or a hex code, or a valid CSS color name, or even a `#RRGGBB` value.

That third option is the most powerful and the least used. When you pick *Format style → Field value*, Power BI expects the field to resolve to a color. You can therefore write a measure that returns `"#2E7D32"` or `"Green"` and let DAX decide everything.

The first two options need a **numeric** result. If your measure returns text, the gradient and rules options will not work. This is the single most common cause of "conditional formatting greyed out."

## Writing a measure that returns a number

Start with a base measure. Suppose you have a `Sales` table with `Revenue` and `Cost` columns, and a `Product` dimension.

```dax
Total Revenue = SUM ( Sales[Revenue] )

Total Cost = SUM ( Sales[Cost] )

Gross Margin % =
DIVIDE (
    [Total Revenue] - [Total Cost],
    [Total Revenue]
)
```

`Gross Margin %` is a valid numeric measure and can be dropped straight into a gradient rule. Open the visual's Format pane, expand **Cell elements**, turn **Background color** on, set **Format style** to *Gradient*, and choose `Gross Margin %` as the **What field should we base this on?** field.

A nuance that trips people up: measures are evaluated in the filter context of the cell, not the filter context of the visual. When you apply the gradient to a matrix cell that sits at Product × Month, `Gross Margin %` is computed for that Product and that Month, not for the grand total. That is almost always what you want, and it is precisely why a measure beats a calculated column here. A calculated column would be evaluated at row level in the source table and would ignore the matrix layout entirely.

## Rules instead of gradients

Gradients are fine for continuous values. For business thresholds you want rules. Keep the same measure but switch **Format style** to *Rules*. Add three rules:

| Condition | Value | Color |
|---|---|---|
| if value is | >= 0.35 | Green |
| if value is | >= 0.2 and < 0.35 | Amber |
| if value is | < 0.2 | Red |

Rules evaluate top to bottom in the order you create them, so put the most specific first. A rule that says ">= 0.2" placed above ">= 0.35" will catch everything and the second rule never fires.

You can also base rules on a different measure than the one displayed. A matrix showing Revenue as the value can still color its background by `Gross Margin %`. Power BI allows any measure in the *What field should we base this on?* dropdown that is valid in the current context.

## Returning a color from DAX

When thresholds depend on logic that the rule builder cannot express — for example, comparing this month against the same month last year, or coloring a cell only when it is above the row average — return the color from DAX and use *Field value*.

```dax
Margin Color =
VAR MarginPct = [Gross Margin %]
VAR PrevYearMargin =
    CALCULATE ( [Gross Margin %], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
VAR Delta = MarginPct - PrevYearMargin
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( MarginPct ), "#FFFFFF",
        MarginPct >= 0.35 && Delta >= 0, "#C8E6C9",
        MarginPct >= 0.35 && Delta < 0, "#FFF9C4",
        MarginPct >= 0.20, "#FFE0B2",
        "#FFCDD2"
    )
```

Two details matter. First, `SWITCH ( TRUE (), ... )` is the standard way to express if/else-if chains in DAX; each condition is evaluated until one returns TRUE. Second, `ISBLANK` is checked first because a blank margin (no sales in the period) should not be colored red. Without that guard, `BLANK() >= 0.35` evaluates to FALSE and a missing month would render as a failure. Refer to the [BLANK reference](https://learn.microsoft.com/en-us/dax/blank-function-dax) for edge cases.

To apply it: set **Format style** to *Field value*, then select `Margin Color`. The cell background now reflects the measure's own decision.

## Formatting a chart's data points

Charts use the same machinery, with a slightly different entry point. Select the column chart, go to **Format → Columns → Color**, and click the small *fx* icon. You get the same dialog: Gradient, Rules, or Field value.

A practical case is coloring bars by rank. Suppose you want the top 3 products by revenue highlighted and everything else muted.

```dax
Revenue Rank =
IF (
    ISINSCOPE ( 'Product'[Product Name] ),
    RANKX ( ALLSELECTED ( 'Product'[Product Name] ), [Total Revenue] ),
    BLANK ()
)
```

Note the `ISINSCOPE` guard. `RANKX` with `ALLSELECTED` needs an explicit scope check, otherwise the measure also computes at higher levels of the matrix where it produces meaningless values. `ISINSCOPE` is one of the few functions that inspects the visual's row/column structure rather than the filter context, so it is the correct tool here.

Then a companion measure returns a color:

```dax
Rank Color =
IF ( [Revenue Rank] <= 3, "#1565C0", "#B0BEC5" )
```

Set the column color with *Field value* and pick `Rank Color`.

## Debugging: when the color does not appear

Most failures fall into four buckets.

**The measure returns text where a number is required.** Gradient and Rules both reject text. If you built a color-string measure, you must use *Field value*. If you built a numeric measure and the dialog refuses to list it, check for a `FORMAT` call or a text concatenation inside it.

**The measure references a column that is not in the visual's context.** A measure using `SAMEPERIODLASTYEAR` requires a marked date table. Without one, the measure errors and the formatting falls back to default.

**Rules are ordered wrong.** The first matching rule wins. Sort them from most specific to least specific.

**You are formatting the wrong element.** In a matrix, *Cell elements → Background color* colors values; *Column headers* and *Row headers* are separate sections with their own color controls. People often configure the value section and wonder why the header stays stubbornly grey.

There is one more subtlety worth internalizing: conditional formatting measures are evaluated **per rendered cell**, which means a large matrix with a heavy measure can become slow. If you notice lag, check Performance Analyzer and look at the DAX query count. A simple `DIVIDE`-based measure is cheap; one that iterates `ALLSELECTED` across a wide table is not, and the cost multiplies by the number of cells on screen.

## Choosing between a column and a measure

A calculated column can also drive formatting, and beginners often reach for it because it feels simpler. The trade-off is real:

- A **column** is computed once at refresh. It is fast to render and works in the field-value style if it stores colors. But it cannot see filter context, so it cannot compare a cell to the visual's total, to last year, or to a rank.
- A **measure** is computed per cell at query time. It can reference anything in the model, including other measures, time intelligence, and ranking functions. It costs more and requires you to think in filter context.

For anything dynamic — top N, above/below average, variance to target — use a measure. For a static lookup, like mapping a status code to a color, a column is fine and cheaper.

## FAQ

### Q: Can I use a measure that returns a hex code directly, without rules?

Yes. Set the format style to *Field value* and pass a measure whose return type is text containing a valid color: `"#1565C0"`, `"Red"`, `"rgb(21,101,192)"`, or `"#1565C080"` for a hex value with alpha. Power BI parses the string at render time. If the string is not a color Power BI understands, the cell falls back to the default color with no error message.

### Q: Why is my measure missing from the formatting dropdown?

The dropdown only lists measures whose data type is numeric for gradient and rules styles, and text for the field-value style. If you see a blank list, your measure is probably text while the style expects a number, or the measure references a table not present in the current visual's query. Try dragging the measure into the visual as a temporary value to confirm it resolves.

### Q: Does conditional formatting respect row-level security?

Yes, but with an important consequence. RLS filters the data before the measure is evaluated, so a cell can be green for one viewer and red for another. If your formatting encodes a target that is fixed per region, make sure the target measure is also filtered correctly under the role, otherwise the color assignment will look inconsistent between users.

### Q: Can I apply conditional formatting to a text column like a status label?

Background color and font color accept a measure regardless of whether the displayed value is text or a number. So a text column of statuses can be colored by an unrelated numeric or color-string measure. What you cannot do is change the text itself through formatting — that requires a DAX measure returning a different string, or a calculation group.

### Q: Is there a limit on how many conditional formatting rules I can add?

There is no documented hard limit, but the format pane becomes unwieldy past a handful of rules, and rule order becomes hard to audit. When you need more than about five bands, move the logic into a DAX measure returning a color and switch to the field-value style. The logic stays in one place, is easier to test, and you can comment it.

## Related Reading

- [Conditional formatting generator: build the colour rule as a DAX measure](/tools/conditional-format-generator/)

- [Conditional Formatting in Power BI: The Complete Guide](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting for Charts in Power BI](/tutorials/conditional-formatting-charts-power-bi/)
- [How to Copy Conditional Formatting in Power BI](/tutorials/copy-conditional-formatting/)
- [DAX SWITCH Function](/tutorials/dax-switch-function/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX Variables Best Practices](/tutorials/dax-variables-guide/)
- [DAX RANKX Function](/tutorials/dax-rankx-function/)
- [Power BI Performance Analyzer Guide](/tutorials/power-bi-performance-analyzer/)
- [DAX Troubleshooting Guide](/tutorials/dax-troubleshooting-guide/)
<!-- CF-CLUSTER-NAV -->
## More conditional formatting guides

- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting in Power BI](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting for Charts](/tutorials/conditional-formatting-charts-power-bi/)
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting/)
- [Gauge Conditional Formatting](/tutorials/conditional-formatting-charts-power-bi/)
- [Bar Chart Conditional Formatting](/tutorials/conditional-formatting-charts-power-bi/)
- [Line Chart Conditional Formatting](/tutorials/line-chart-conditional-formatting/)

