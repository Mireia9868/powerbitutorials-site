---
title: "Power BI Matrix Visual: Best Practices and Tips"
description: "The matrix visual is the workhorse of Power BI reporting. It handles hierarchies, cross-tabulation, expand/collapse, and drill-down better than any other built-in visual."
pubDate: 2026-10-13
category: visualization
tags: ["matrix", "visualization"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

The matrix visual is the workhorse of Power BI reporting. It handles hierarchies, cross-tabulation, expand/collapse, and drill-down better than any other built-in visual. It is also the visual that new developers most often misconfigure, producing slow reports and unreadable output.

This tutorial covers the practical decisions that separate a matrix you can ship from one that generates support tickets. Everything works in both Power BI Desktop and the Service.

## Why the matrix behaves differently from a table

A table renders one row per value combination. A matrix pivots on a column well, so the data is grouped along two axes. That pivot is the reason the matrix supports:
- Stepped layouts across row hierarchies
- Expand and collapse per node
- Drill down, drill up, and drill through to a detail page
- Subtotals and grand totals that recalculate per grouping level

Those features are also the reason the matrix is the most expensive core visual. Every expanded level issues evaluation across the cells you can see plus the totals you can see. On a wide model that adds up fast.

## Step 1: Build the row hierarchy before touching the format pane

A common mistake is to drag five fields into Rows in whatever order looked good during exploration. Decide the hierarchy first, then order it top-down from coarsest to finest.

Example for a retail model:

| Row level | Field | Purpose |
|---|---|---|
| 1 | `DimProduct[Category]` | Top grouping |
| 2 | `DimProduct[Subcategory]` | Mid grouping |
| 3 | `DimProduct[Product]` | Leaf level |

Then:

1. Select the matrix.
2. Go to **Format pane → Row headers → Stepped layout** and enable it, or leave it off if you prefer a single indented column.
3. Set **Row headers → Options → +/- icons** to a reasonable size. Avoid "Expand all" as the initial state.
4. Use **Visual → Row headers → Options → Per row level → Header** to hide a level's label when it is redundant.

The initial state should be collapsed to level 1 or level 2. Opening a report to 40,000 rendered leaf rows is the single most common cause of "Power BI is slow" complaints.

## Step 2: Keep measures on Values, never in Rows

Only hierarchy fields belong in Rows. If you drop a numeric measure in Rows, you get one row per distinct value, which is almost never what you want. Measures go in Values.

```dax
Sales Amount :=
SUMX (
    FactSales,
    FactSales[Quantity] * FactSales[UnitPrice] * ( 1 - FactSales[DiscountPct] )
)

Sales YoY % :=
VAR CurrentSales = [Sales Amount]
VAR PriorSales =
    CALCULATE ( [Sales Amount], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
RETURN
    DIVIDE ( CurrentSales - PriorSales, PriorSales )
```

Both measures belong in Values. The matrix will evaluate them per visible cell, per subtotal, and per grand total, using whatever filter context the row and column headers establish.

## Step 3: Use conditional formatting as the third data dimension

A matrix with several numeric columns is hard to scan. Conditional formatting turns column values into a readable signal. The most useful pattern in a matrix is background color on a single measure, driven by the measure itself so the logic travels with the model.

```dax
Margin % Color :=
VAR MarginPct = DIVIDE ( [Gross Margin], [Sales Amount] )
RETURN
    SWITCH (
        TRUE (),
        MarginPct >= 0.30, "#2E7D32",
        MarginPct >= 0.15, "#F9A825",
        MarginPct <  0,    "#C62828",
        "#9E9E9E"
    )
```

Apply it via **Format pane → Cell elements → Background color → fx → Format style: Field value**, and point to `Margin % Color`. Use the same measure for font color only if the background is light.

Two constraints worth knowing:
- **Format style: Gradient** gives you a color scale but only supports two or three colors and no per-cell logic.
- **Format style: Rules** is evaluated per column, not per row, so a threshold that should vary by product category requires a measure instead.

If you only want to highlight outliers and not paint the whole grid, use **Cell elements → Font color** with a measure returning `BLANK()` for normal cells and a color for the exceptions. Blank means "leave as-is."

## Step 4: Control totals deliberately

Totals are on by default in both directions. That is often what you want for `[Sales Amount]` and almost never what you want for ratios, ranks, or percentages. A grand total of a `%` measure is not the average of the percentages above it; it is the percentage of the totals. That is usually correct, but you need to confirm it.

For measures where a total is meaningless, suppress it with a filter:

```dax
Ranks with Blank Total :=
IF (
    ISINSCOPE ( DimProduct[Product] ),
    RANKX ( ALLSELECTED ( DimProduct[Product] ), [Sales Amount] )
)
```

`ISINSCOPE` returns TRUE only when the current filter context is at that level. On the grand total node, `ISINSCOPE ( DimProduct[Product] )` is FALSE, so the measure returns blank and the total cell stays empty.

If you want to remove the total row entirely, turn off **Format pane → Totals → Row subtotals** and **Column subtotals**. Note the word "subtotals" covers the grand total as well; there is no separate grand total switch.

## Step 5: Widen cells and shorten numbers

Long numbers overflow into adjacent cells and break vertical scanning. Do two things:

- Set **Format pane → Values → Values → Units** to Thousands or Millions.
- Set decimal places per measure with the **Measure tools** ribbon rather than globally.

For very wide matrices, use **Format pane → Values → Options → Values fit** and **Auto-size column width**. Both are approximations; test on the smallest screen your audience uses.

## Step 6: Sorting, drill, and expand

Sorting a matrix applies to the value axis in the Values section. Click a column header to sort; click again to reverse. When multiple measures are in Values, sorting by a measure sorts row headers by that measure's values.

Drill behavior is governed by the **Drill** options in the Format pane:
- **Drill down** replaces the parent level with the child level.
- **Expand all down one level** keeps the parent and reveals children underneath.

If your report has drill-through configured, the matrix automatically exposes the drill-through context menu. Verify the page filter is set to **Keep all filters**, not **Allow drill through when: Filters are kept** misinterpreted as stripping the page filter.

## Step 7: Performance rules for large matrices

| Setting | Effect | When to change |
|---|---|---|
| Row hierarchy depth > 3 | High cardinality leaf level evaluates all visible cells | Collapse by default |
| Column field with many distinct values | One measure evaluation per column cell | Pivot columns into rows or use slicer |
| Conditional formatting via measure | One extra DAX call per cell | Accept for 1–2 measures only |
| Auto "Expand all" initial state | Renders everything on load | Always start collapsed |
| DirectQuery source | Each expansion round-trips to the source | Prefer Import for matrix-heavy report pages |

If you need many column values, consider a slicer for the column axis and a single measure column. A matrix with 200 columns evaluates 200 times per row node.

For deeper tuning, review `DAX Optimization Techniques` and the broader model design in `Data Modeling: Star Schema`.

## Step 8: Accessibility and layout

- Add a title that states the metric and the period.
- Use bold or a contrasting font size for subtotal rows; do not rely on color alone.
- Keep the number of decimal places consistent within a column.
- Test tab order with a keyboard; the matrix exposes controls in hierarchy order.

## FAQ

### Q: Why does my matrix show blank values instead of zeros?

Blanks usually mean the measure has no rows in that filter context, not that the value is zero. Wrap the measure in `COALESCE ( [Your Measure], 0 )` if you want zeros, but be aware this changes totals behavior and can hide genuine missing data. Confirm the relationship direction and the `DimDate` coverage before blanking out values.

### Q: How do I collapse all rows by default when the report opens?

Set the visual to its collapsed state and save the file. Expand/collapse state is persisted in the report definition, so the visual will open the way you left it. Do not use bookmarks for this — it works, but the bookmark panel state will drift as the model changes.

### Q: Can I use a measure in the Columns well?

No. Columns accept fields from tables, not measures. If you need dynamic column headers, you have two options: unpivot the data so the values become a field, or build a measure per column and accept the fixed layout. A disconnected table combined with `SELECTEDVALUE` can approximate dynamic columns but breaks the matrix's column grouping.

### Q: Why is the grand total for my percentage measure different from the average shown?

Because they are different calculations. The grand total recomputes the ratio using the numerator and denominator totals, which is the correct weighted result. The average of the visible percentages is an unweighted mean and will always differ unless every group has an identical denominator.

## Related Reading

- [Conditional Formatting Complete Guide](/tutorials/conditional-formatting-complete-guide/)
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)
- [Conditional Formatting Charts in Power BI](/tutorials/conditional-formatting-charts-power-bi/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [DAX RANKX Function](/tutorials/dax-rankx-function/)
- [DAX SWITCH Function](/tutorials/dax-switch-function/)
- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/)
- [DAX Optimization Techniques](/tutorials/dax-optimization-techniques/)
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
