---
title: "Power BI Tooltips: From Basic Hover to Full Page Reports"
description: "Tooltips are the most underrated interaction in Power BI. A default tooltip shows the data point's values — useful but limited. Custom tooltip pages turn a hover into a mini-report: related metrics, trends, and context. This guide covers building both and the three patterns where tooltips shine."
pubDate: 2026-07-20
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "tooltips", "tooltip-pages", "hover", "report-design"]
author: "Power BI Tutorials Team"
featured: false
---

Tooltips are the quiet workhorse of Power BI reports. Users hover without thinking — and the information that appears shapes their next click. Default tooltips show raw values, which is fine for simple visuals. But custom tooltip pages transform a hover into a contextual mini-report: trends, comparisons, and related metrics. This guide covers both and the patterns where custom tooltips make a real difference.

## Default tooltips

Every visual has a default tooltip that shows the data point's values. No configuration needed — it appears on hover.

**To customize the default tooltip:** click the visual → Format pane → Tooltip → Tooltip fields. Add or remove fields to control what appears.

**Tip:** keep default tooltips concise. 3–5 fields is ideal. A tooltip with 15 fields is unreadable and slow.

## Custom tooltip pages

A custom tooltip page is a dedicated report page designed to appear as a tooltip. It can contain any visual — cards, mini charts, text — and it inherits the filter context from the data point being hovered.

### Creating a custom tooltip page

**Step 1:** Create a new page. In the Format pane → Page information → Type → **Tooltip**. Set the page size to "Tooltip" (320×240 px by default).

**Step 2:** Add visuals to the page. These will appear in the tooltip on hover. The page inherits the filter context from the hovered data point — so if you hover over "Bikes" in a bar chart, the tooltip visuals filter to Bikes.

**Step 3:** Connect the tooltip page to a visual. Click the source visual (the bar chart) → Format pane → Tooltip → Type → **Report page**. Select the tooltip page you created.

Now hovering over any data point in the bar chart shows the custom tooltip page instead of the default tooltip.

## Pattern 1: Trend-on-hover

A bar chart shows revenue by product category. The tooltip shows a 12-month trend line for the hovered category.

**Tooltip page contents:**
- A line chart showing `[Total Revenue]` by `Date[YearMonth]` over the last 12 months.
- A card showing the current month's value.
- A card showing the YoY change percentage.

Users see the bar (current performance) and the trend (historical context) without leaving the page.

## Pattern 2: Composition breakdown

A KPI card shows total revenue. The tooltip shows the breakdown by region, product, and channel.

**Tooltip page contents:**
- A small bar chart showing revenue by region.
- A donut chart showing revenue by channel (online vs. retail).
- A table showing the top 5 products.

This pattern lets users explore composition without adding visuals to the main page.

## Pattern 3: Comparison to benchmark

A matrix shows actual revenue vs. target. The tooltip shows how the selected category compares to the overall average and to the best-performing category.

**Tooltip page contents:**
- A card showing the selected category's revenue.
- A card showing the overall average.
- A card showing the best-performing category and its value.
- A small bar chart showing all categories with the selected one highlighted.

This gives users context for whether a number is good, bad, or average.

## Design principles for tooltip pages

### Keep it small

Tooltip pages are 320×240 px by default. Don't try to fit a full dashboard. 3–5 visuals maximum, each simple (a card, a mini chart, a small table).

### Keep it fast

Tooltips render on hover — if they're slow, the interaction feels broken. Avoid complex measures or large tables in tooltip pages. Test on a realistic dataset.

### Keep it focused

A tooltip should answer one question: "tell me more about this data point." Don't try to show everything — that's what drill-through is for.

### Use consistent styling

Tooltip pages should match the report's visual style — same fonts, same color palette, same card formatting. A tooltip that looks different from the main report is jarring.

## Tooltip vs. drill-through

Tooltips and drill-through both provide "more detail," but they serve different purposes:

| Aspect | Tooltip | Drill-through |
|--------|---------|---------------|
| Trigger | Hover | Right-click → Drill through |
| Commitment | Low — just looking | High — navigating to a new page |
| Depth | Summary context | Full detail page |
| Best for | "What's the trend for this?" | "Show me all the transactions" |

Use tooltips for context the user wants without leaving the page. Use drill-through when the user wants to investigate deeply.

## Common mistakes

**Mistake 1: Tooltip pages that are too complex.** A tooltip with 10 visuals takes 2 seconds to render and fills the screen. Keep it to 3–5 simple visuals.

**Mistake 2: Forgetting to set the page type.** If the page type isn't set to "Tooltip," it won't appear as a tooltip — it'll just be a regular page. Always verify the page type after creating a tooltip page.

**Mistake 3: Tooltip fields that don't match the visual.** If the tooltip page expects a filter from `Product[Category]` but the source visual is grouped by `Region`, the tooltip will show blank or unfiltered data. Match the tooltip's filter context to the source visual's grouping.

**Mistake 4: Not testing on touch devices.** Hover doesn't exist on tablets and phones — tooltips require a click-and-hold. If your report is mobile-bound, ensure critical information isn't tooltip-only.

## Summary

Default tooltips show values; custom tooltip pages show context. Use them for trend-on-hover, composition breakdowns, and benchmark comparisons. Keep tooltip pages small (3–5 visuals), fast (simple measures), and focused (one question per tooltip). Match the tooltip's filter context to the source visual's grouping, and remember that tooltips don't work on touch devices — don't hide critical information behind a hover.
