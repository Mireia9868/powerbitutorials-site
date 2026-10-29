---
title: "Copy Conditional Formatting Between Visuals in Power BI"
description: "Conditional formatting in Power BI is stored per visual, per field, per formatting property."
pubDate: 2026-09-30
category: visualization
tags: ["conditional formatting", "tips"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Conditional formatting in Power BI is stored per visual, per field, per formatting property. There is no global "formatting style" object that you can apply across a report the way you apply a theme. That is the core reason copying conditional formatting is awkward: every rule set lives inside the visual that owns it.

The good news is that there are four practical ways to move a rule from one visual to another, and each one suits a different situation. This tutorial walks through all four in order of how much work they save you, from simple clipboard tricks to a design pattern that only requires you to write the formatting rule once.

## How Power BI stores conditional formatting

Before copying anything, it helps to know what you are copying. When you set a conditional format on a column or a measure, Power BI stores three things:

| Component | What it defines | Where you set it |
|---|---|---|
| Format style | Gradient, Rules, or Field value | Format pane, e.g. Background color |
| Rule or field | The measure/column and the thresholds | The conditional formatting dialog |
| Target property | Background color, Font color, Data bars, Icons | Format pane section |

The target property matters most. A background color rule on a table column is not portable to a card visual, because a card has no per-category background. A data bar rule on a matrix works fine on a bar chart, because both expose a value axis. Copying is only clean when the source and destination visuals support the same property type.

## Method 1: Copy and paste the visual, then re-point the field

The fastest method, and the one most people miss, is that formatting travels with the visual itself.

1. Select the visual on the canvas.
2. Press `Ctrl+C`, then `Ctrl+V`. You now have an exact duplicate, including every conditional format rule.
3. With the copy selected, go to the **Fields** well (the Values / Axis / Legend buckets) and replace the source field with the destination field.
4. Open the Format pane and check the conditional formatting rule. If it was bound to a measure, the rule still points at that measure. If it was bound to a column of the original table, Power BI may drop the rule when you remove the column.

The catch is step 4. Rules bound to a *measure* survive a field swap, because the measure still exists in the model. Rules bound to a *column* usually break, because Power BI stores them as a reference to that specific column reference inside the visual. For column-bound rules, use Method 2 instead.

This approach is the fastest way to standardise a report page, and it pairs well with the workflow in [Power BI dashboard design principles](/tutorials/power-bi-dashboard-design-principles/).

## Method 2: Recreate the rule using a shared measure

The reliable, repeatable method is to move the logic out of the visual and into the model. Write one measure that returns a hex colour string, then point every visual at that measure.

```dax
Profit Margin Color =
VAR MarginPct =
    DIVIDE ( [Total Profit], [Total Sales] )
RETURN
    SWITCH (
        TRUE (),
        ISBLANK ( MarginPct ), "#FFFFFF",
        MarginPct < 0, "#F8696B",
        MarginPct < 0.10, "#FFEB84",
        MarginPct < 0.25, "#B1D580",
        "#63BE7B"
    )
```

Then, in each visual you want to format:

1. Select the visual and open the **Format** pane.
2. Expand the property you want, for example **Cells** > **Background color**.
3. Click the small `fx` button to open the conditional formatting dialog.
4. Set **Format style** to *Field value*.
5. In **What field should we base this on?**, pick `Profit Margin Color`.
6. Click OK.

Now the identical colour logic applies to a table, a matrix, a bar chart, a card, and a KPI visual. If you later decide that under 10% should be orange rather than yellow, you edit one measure and every visual updates together. No copying required.

A measure-based rule is the only approach that scales past a handful of visuals. The trade-off is that *Field value* rules need a text value that is a valid colour, so your measure has to return hex codes or named CSS colours such as `"red"`. If you return a number between 1 and 5, you must instead use *Rules* style with the measure as the basis and define the numeric bands in the dialog.

## Method 3: Copy the rule between visuals with identical structure

If two visuals share the same structure, for example two matrix visuals sitting on different pages with the same rows and columns, you can copy the rule almost literally.

1. Open the Format pane on the source visual.
2. Expand the formatted property and click `fx`. Note the exact settings: format style, the field used, and any threshold values.
3. Select the destination visual, expand the same property, and click `fx`.
4. Re-enter the same settings, picking the **same field** from the destination's own field well where Power BI offers it.

Between identical visual types with identical field structures, this takes about twenty seconds per property. It is tedious but deterministic. Where people go wrong is assuming the field list in the dialog will match. The dialog only lists fields available in that visual's scope, which is the same reason the measure-based approach in Method 2 is worth the extra upfront effort.

One shortcut: if the two visuals are the same type and you have not changed anything else, `Ctrl+Shift+V` after `Ctrl+C` on the visual duplicates the visual next to the original. Move it to the target position afterwards. That is really Method 1 with a positional twist.

## Method 4: Use a theme file for property defaults

Report themes set defaults for visual properties, and JSON theme files can carry some formatting defaults across visuals. This does not copy conditional formatting rules directly, because a theme has no concept of a per-field rule, but it does handle the surrounding styling so that only the rule itself needs recreating.

```json
{
  "name": "CF Base",
  "dataColors": ["#118DFF", "#12239E", "#E66C37"],
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "show": true, "color": { "solid": { "color": "#FFFFFF" } } }]
      }
    }
  }
}
```

Save that as a `.json` file, then use **View** > **Themes** > **Browse for themes**. Every new visual starts with the same background, which means the only thing left to configure per visual is the conditional rule itself. Combined with Method 2, that gets you to a state where adding a new visual is a two-minute job: drop the field, click `fx`, pick the colour measure.

## Copying rules to other report pages and files

Conditional formatting does not travel between separate `.pbix` files through the clipboard. To move a rule set between reports you have three options:

- Copy the measure definitions from the source model using **DAX Studio** or by opening the source file's model view. Measure-bound rules then transfer by recreating the `fx` binding in the destination, which is quick once the measure exists.
- Copy the JSON theme file across, which carries every non-conditional default.
- Recreate the rule manually with identical thresholds. For more than a handful of rules this is rarely worth it compared to rebuilding around a single colour measure.

If the two reports share a dataset in the Power BI Service, measure-bound formatting transfers automatically as long as the measure exists in the shared model. That is a strong argument for centralising colour logic in the semantic model rather than in individual reports, an idea covered in more depth in [conditional formatting based on a measure](/tutorials/conditional-formatting-based-on-measure/).

## Which method to pick

| Situation | Best method |
|---|---|
| Same field, new visual | Method 1, copy the visual |
| Many visuals, same rule | Method 2, shared colour measure |
| Two identical visuals | Method 3, manual re-entry |
| New report, standard look | Method 4, theme file plus Method 2 |
| Cross-file transfer | Measure definitions plus theme JSON |

## Common pitfalls

Rules that were bound to a column break when you remove that column from a visual. Rules that reference a measure keep working, which is the main argument for the measure-based pattern. Text-valued colour measures must return valid colour strings, so a `SWITCH` returning `"1"`, `"2"`, `"3"` will silently render nothing. And a rule created with *Rules* style holds hard-coded thresholds that will not follow a slicer, while a *Field value* rule reads a measure at query time and does respond to filters. Pick deliberately.

## FAQ

### Q: Can I copy conditional formatting between two different visual types?

Not directly. A background-colour rule on a matrix column has no equivalent on a card. What transfers is the *field* used, so the practical approach is to write a colour measure and bind it to whatever property the destination visual does support.

### Q: Why did my conditional formatting disappear after I changed the field?

Because the rule was bound to a column rather than a measure. Power BI stores column-bound rules against the visual's field reference, so replacing the field removes the reference and the rule with it. Rebind it, or convert to a measure-based rule to prevent it happening again.

### Q: Does a theme file copy my conditional formatting rules?

No. Themes set visual property defaults such as backgrounds, fonts, and data colours. They cannot express a rule like "colour this cell red when margin is below 10%", because that requires a field and a threshold. Use a theme for the styling and a measure for the logic.

### Q: Will a colour measure work on a card visual?

A card does not expose a per-value background property, so it cannot take a background-colour rule. It does support **Font color** and **Callout value** colour, and a field-value rule works on those properties.

### Q: How do I copy formatting between pages in the same report?

Copy the visual with `Ctrl+C` and `Ctrl+V`, then paste it onto the target page. All rules that are measure-bound are preserved. Column-bound rules survive only if the columns remain in the visual.

Behaviour described here follows [Microsoft's Conditional formatting in Power BI documentation](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-conditional-table-formatting).

## Related Reading

- [Conditional formatting in Power BI: the complete guide](/tutorials/conditional-formatting-power-bi/)
- [Conditional formatting based on a measure](/tutorials/conditional-formatting-based-on-measure/)
- [Bar chart conditional formatting](/tutorials/conditional-formatting-charts-power-bi/)
- [Conditional formatting for charts](/tutorials/conditional-formatting-charts-power-bi/)
- [Copy conditional formatting in Power BI](/tutorials/copy-conditional-formatting/)
- [DAX SWITCH function](/tutorials/dax-switch-function/)
- [DAX variables best practices](/tutorials/dax-variables-guide/)
- [Power BI dashboard design principles](/tutorials/power-bi-dashboard-design-principles/)

- [Power BI Conflicting Metrics Error: Causes and Fixes](/tutorials/power-bi-conflicting-metrics/)