---
title: "Power BI Visual Types: A Practical Guide to Choosing the Right Chart"
description: "Power BI offers dozens of visual types, but most reports use the same handful. This guide covers the core visuals — bar, line, card, matrix, map, and scatter — with guidance on when each is appropriate, common mistakes, and the visual hierarchy that makes reports readable."
pubDate: 2026-07-18
category: "visualization"
difficulty: "Beginner"
tags: ["visualization", "charts", "bar-chart", "line-chart", "matrix", "visual-types"]
author: "Power BI Tutorials Team"
featured: false
---

Choosing the right visual is part art, part science. The wrong chart doesn't just look bad — it misleads. A bar chart on non-ordinal categories implies an order that doesn't exist. A pie chart with 15 slices is unreadable. This guide covers the visuals that cover 90% of reporting needs and the rules for choosing between them.

## The core visuals

### Bar and column charts

**When to use:** comparing a measure across discrete categories.

- **Column chart** (vertical bars): 2–12 categories, short labels.
- **Bar chart** (horizontal bars): 8+ categories or long labels.

```dax
// Typical use: revenue by product category
Revenue by Category = SUM(Sales[Revenue])  // plotted against Product[Category]
```

**Common mistakes:**
- Starting the y-axis above zero — exaggerates differences.
- Using a column chart when labels overlap — switch to horizontal bar.
- Sorting alphabetically — sort by value so the chart reads as a ranking.

### Line charts

**When to use:** showing trends over a continuous axis (usually time).

- X-axis: date or sequential number.
- Y-axis: a measure that changes over time.

**Common mistakes:**
- Using a line chart for non-continuous data (e.g., revenue by category). Use a bar chart instead — categories aren't ordered.
- Too many lines (5+) — the chart becomes spaghetti. Use small multiples or filter to top N.
- Not handling gaps — if data is missing for a period, decide whether to show a gap or interpolate.

### Cards and KPIs

**When to use:** highlighting a single key number.

- **Card:** just the value, large and prominent.
- **KPI visual:** value + a target + trend indicator (up/down arrow).

**Common mistakes:**
- Too many cards on a page — it becomes a dashboard of numbers with no context.
- No comparison — a card showing "$1.2M revenue" is meaningless without "vs $1.0M last month."

### Matrix and table

**When to use:** showing precise values across two dimensions.

- **Table:** rows only, for detailed listings.
- **Matrix:** rows + columns, for cross-tabulations (e.g., revenue by product × region).

**Common mistakes:**
- Matrix with too many columns — it becomes unreadable. Filter or group.
- Not using conditional formatting — a matrix of raw numbers is hard to scan. Add background color scaling to highlight highs and lows.

### Maps

**When to use:** geographic data (country, state, city, postal code).

- **Filled map (choropleth):** regions shaded by value. Good for comparisons.
- **Bubble map:** circles sized by value. Good for showing magnitude at a point.

**Common mistakes:**
- Using a map when a bar chart would do — if you only have 5 regions, a bar chart is clearer.
- Ambiguous location names — "Springfield" exists in 30+ US states. Use country + state + city for precision.

### Scatter plot

**When to use:** showing the relationship between two measures.

- X-axis: one measure.
- Y-axis: another measure.
- Bubble size (optional): a third measure.
- Play axis (optional): a date field for animated trends over time.

**Common mistakes:**
- Too many points — the chart becomes a blob. Filter to a subset or use transparency.
- Not labeling outliers — interesting points should be identifiable.

## The visual hierarchy

A good report follows a visual hierarchy: top-level summary, supporting detail, drill-down. Users should answer "how are we doing?" in 5 seconds, then dig deeper if needed.

**Layer 1: Summary (top of page)**
- 2–4 cards showing key metrics (revenue, orders, conversion rate).
- 1 KPI visual per metric with target and trend.

**Layer 2: Trend (middle of page)**
- A line chart showing the main metric over time (last 12 months).
- A bar chart showing the metric by primary dimension (e.g., by category).

**Layer 3: Detail (bottom of page)**
- A matrix showing the metric across two dimensions (e.g., category × region).
- A table for users who want exact numbers.

**Layer 4: Drill-down (separate page)**
- A detailed view accessible via a button or bookmark.
- Full transaction-level data for users who need it.

## Choosing between visuals

| Question | Visual |
|----------|--------|
| How does this change over time? | Line chart |
| How do categories compare? | Bar chart |
| What's the single most important number? | Card |
| How do two dimensions cross? | Matrix |
| Where are our customers? | Map |
| Is there a correlation? | Scatter plot |
| What's the composition? | Stacked bar (avoid pie for 5+ slices) |

## Common report design mistakes

**Mistake 1: Cramming everything on one page.** A page with 15 visuals overwhelms users. Aim for 4–7 visuals per page, with clear hierarchy.

**Mistake 2: No filtering context.** Users need to know what they're looking at. Add a title, a date range, and any active filters.

**Mistake 3: Inconsistent color usage.** Use color intentionally — one color for the primary metric, a contrasting color for targets, muted colors for context. Don't use 10 different colors across 5 visuals.

**Mistake 4: Forgetting mobile layout.** If the report will be viewed on phones, use Power BI's mobile layout view to arrange visuals for small screens. The desktop layout doesn't translate well.

## Summary

Most reports need only five visual types: bar, line, card, matrix, and map. Choose based on the question — trends use lines, comparisons use bars, single numbers use cards, cross-tabs use matrices, geography uses maps. Structure reports in layers: summary at the top, trends in the middle, detail at the bottom. Keep pages to 4–7 visuals, use color intentionally, and always provide context with titles and filter indicators.
