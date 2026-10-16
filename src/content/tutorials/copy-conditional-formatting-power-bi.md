---
title: "How to Copy Conditional Formatting in Power BI Reports"
description: "Power BI has no native copy-paste for conditional formatting between visuals — but you have three reliable ways to reuse color rules at scale. Learn how to share formatting with measures, JSON themes, and report-level settings."
pubDate: 2026-08-28
updatedDate: 2026-10-12
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "conditional-formatting", "json-theme", "report-design", "reuse"]
author: Mireia
featured: false
---

You built perfect conditional formatting on one matrix. Now you have nine more visuals that need the same logic, and Power BI doesn't have a "copy formatting" button. Recreating color scales by hand is tedious and guaranteed to drift out of sync. Here are the three approaches that actually work — ranked by how much maintenance they save you.

## Why there's no copy button

Conditional formatting in Power BI is stored per visual, attached to the specific measure or column it targets. There's no clipboard for "take these exact rules and apply them elsewhere." That limitation is the whole reason this question shows up so often in the Power BI community forums. The workaround isn't a button — it's designing your formatting so it's reusable from the start.

## Method 1: Reuse a color measure (best for logic-based formatting)

If your formatting comes from a measure using **Field value** (the pattern in our [conditional formatting guide](/tutorials/conditional-formatting-power-bi/)), copying is trivial: point every visual at the same measure.

```dax
// One measure, used by every visual that needs this color logic
CF Sales vs Target =
VAR Pct = DIVIDE([Total Sales], [Sales Target], 0)
RETURN
    SWITCH(
        TRUE(),
        Pct > 1.05, "#22C55E",
        Pct >= 0.95, "#F59E0B",
        "#EF4444"
    )
```

To "copy" the formatting to a new visual:

1. Add the visual.
2. Open the measure dropdown → **Conditional formatting** → **Background color**.
3. Set **Format by** to **Field value**.
4. Select `CF Sales vs Target`.

That's it. The new visual inherits the exact same logic, and when you change the thresholds, every visual updates at once. This is the only method where "copy" means "do nothing twice."

**Gotcha:** the measure has to make sense at the new visual's granularity. A color measure built for a region-level matrix will paint a product-level table incorrectly if the ratio calculation changes meaning at that grain. Test on a sample cell before trusting it.

## Method 2: JSON theme for report-wide color rules

When you want consistent formatting across an entire report — not just one measure — a custom JSON theme is the real answer. Themes carry color definitions and, with a bit of structure, conditional formatting rules that apply wherever the theme's rules match.

Export the current theme: **View → Themes → Customize → JSON theme file**. You get a `json` file describing your palette. The part you care about for conditional formatting is the `"visualStyles"` block, where you can pin default formatting per visual type.

A simpler, lower-risk use: define your brand colors once in the theme, then reference those same hex values in every color measure (Method 1). That way your red is always `#EF4444`, not three slightly different reds across the report.

To apply an updated theme, go to **View → Themes → Browse for themes** and select the file. Every visual using theme colors updates instantly.

**When to use this:** you're standardizing a corporate report (think Contoso's monthly finance pack) where color meaning must be identical everywhere. It's overkill for a one-off matrix.

## Method 3: Manual copy via visual duplication

For a quick one-to-one copy between two similar visuals, duplication beats rebuilding:

1. Select the formatted visual.
2. **Ctrl+C / Ctrl+V** (or right-click → copy) to duplicate it.
3. Swap the field or measure in the new copy. The conditional formatting rules carry over with the visual.

This works because the duplicate is a literal copy — rules included. Then you only adjust the field, not the formatting. It's fast for "I want this same table but for a different region," and useless for "I want this formatting on a completely different visual type."

## Copying between reports

Cross-report reuse needs a theme file (Method 2) or a measure in a shared dataset. If your color measures live in a shared Power BI dataset that multiple reports connect to, every report can use the same `CF Sales vs Target` measure without redefining it. That's the enterprise-grade answer — define once, consume everywhere.

For a standalone report, save your JSON theme and import it into the new report. The colors transfer; the measure-based rules transfer only if the measure exists in that model too.

## Common mistakes

**Mistake 1: Rebuilding rules by hand in every visual.** You get five matrices with five slightly different thresholds. Use a color measure instead.

**Mistake 2: Expecting "Format painter" to copy conditional formatting.** Power BI's format painter copies visual styling (fonts, borders) but not conditional formatting rules. Don't waste time hunting for it.

**Mistake 3: Editing the threshold in one visual and forgetting the others.** If you hand-built rules, this drift is guaranteed. Method 1 eliminates it.

## FAQ

**Is there really no copy-paste for conditional formatting?**
Not between unrelated visuals. Duplication copies it within a report; measures and themes are the only ways to share it broadly.

**Can I export just the formatting rules?**
No standalone export. Your closest option is a JSON theme (carries visual defaults) plus keeping your color logic in measures.

**Does copying via duplication break if I later change the source measure?**
Yes. Duplicated visuals keep their own rule settings; they don't link back to the original. Only measure-based formatting stays in sync automatically.

**What about paginated reports?**
Paginated (SSRS-style) reports handle color through expressions, which are inherently reusable across textboxes. Different tool, same principle: define the logic once.


**How do I copy conditional formatting from one column to another?**
Duplicate the visual (Method 3) and change only the field feeding the new column — the rules travel with the copy. For logic-based rules, point both visuals at the same color measure (Method 1) so the rule applies to any column automatically, with no per-column setup.

**Can I copy conditional formatting to another visual or another column?**
Within one report, duplication carries the rules to the new visual. To apply the same rule to a different column, the cleanest path is a Field-value color measure that any visual can reference. There is no "paste formatting" button across unrelated visuals.

**Why does my copied formatting look different on the new visual?**
Two causes: the color measure's granularity doesn't match the new visual's grain, or you duplicated a visual whose rules were hand-built and now drift from the original. Measure-based formatting stays identical everywhere; hand-built rules don't.

## What's next

- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-complete-guide/) — the full cluster, from rules to reuse.
- [Conditional Formatting in Power BI: A Complete Guide](/tutorials/conditional-formatting-power-bi/) — the measure and rule patterns this article builds on.
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/) — drive colors from a DAX measure instead of fixed rules.
- [Conditional Formatting for Charts, Bar Charts & Gauges](/tutorials/conditional-formatting-charts-power-bi/) — gauge, bar, and line chart guides.
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/) — keep color consistent across the whole report, not just formatted cells.
