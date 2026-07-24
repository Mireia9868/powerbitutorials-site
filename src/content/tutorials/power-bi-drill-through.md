---
title: "Power BI Drill Through: Jump from Summary to Detail in One Click"
description: "Drill through lets users click a data point and jump to a detailed report page filtered to that specific context. This guide covers setup, filter passthrough, cross-report drill through, and the design patterns that make drill-through reports intuitive."
pubDate: 2026-07-23
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "drill-through", "navigation", "report-design", "filters"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

Drill through lets users click a data point and jump to a detailed report page filtered to that specific context. This guide covers setup, filter passthrough, cross-report drill through, and the design patterns that make drill-through reports intuitive.

A summary dashboard shows the big picture. A detail page shows the transaction-level records behind it. Drill through connects the two — a user clicks a bar, a row, or a data point, and a separate page opens already filtered to that specific slice. This guide covers the mechanics and the design patterns that make drill-through work for real users.

## How drill through works

Drill through is a relationship between two report pages:

1. **Source page** — the summary page where the user starts
2. **Target page** — the detail page that opens when the user drills through

When the user right-clicks a data point on the source page and selects "Drill through → [target page]", Power BI opens the target page and passes all filters from the source context to the target. The target page shows only data relevant to what the user clicked.

**Key principle:** drill through passes filters, not clicks. The target page receives the filter context from the source visual and applies it automatically. You don't write any DAX to make this work — you configure it in the field well.

## Setting up a basic drill through

### Step 1: Create the target page

1. Add a new page to your report
2. Name it something descriptive (e.g., "Customer Details")
3. Build your detail visuals — a table of transactions, supporting charts, cards with key metrics

### Step 2: Add the drill-through filter

1. With the target page selected, open the Filters pane
2. Find the "Drill through" section at the bottom of the Filters pane
3. Drag the field you want to drill through by into the "Add drill-through fields here" area

For example, if you want users to click a customer name and see that customer's transactions, drag `Customer[Customer Name]` into the drill-through filter well.

**You can add multiple fields:** if you add both `Customer[Customer Name]` and `Date[Year]`, the target page will filter by both when the user drills through.

### Step 3: Test from the source page

1. Go to your summary page
2. Right-click any data point (bar, row, slice) that includes the drill-through field
3. Select "Drill through" → your target page name
4. The target page opens, filtered to the context of what you clicked

## The back button

When a user drills through, Power BI automatically adds a back button in the top-left corner of the target page. The user clicks it to return to the source page.

**Customize the back button:**

1. Select the button (it appears as a visual on the page)
2. In the Format pane, customize the icon, text, and background
3. You can also add your own button with Action type set to "Back" for more control over appearance

**Warning:** if you delete the auto-generated back button and don't add a replacement, users have no way to return to the summary page except clicking the page tab. Always include a visible back navigation element.

## Passing all filters vs. specific fields

By default, drill through passes only the fields you explicitly added to the drill-through filter well. But you can also pass all filters from the source page:

1. On the target page, go to the Filters pane
2. In the Drill through section, find the "Keep all filters" toggle
3. Turn it ON to pass every active filter from the source page
4. Turn it OFF to pass only the fields in the drill-through well

**When to use "Keep all filters":**
- ON: when the target page should reflect the user's complete context (slicers, visual filters, page filters)
- OFF: when the target page should only show the drill-through field's context, ignoring everything else

Most reports benefit from "Keep all filters" = ON, because users expect the detail page to respect their slicer selections.

## Cross-report drill through

Cross-report drill through lets a user jump from a report in one workspace to a report in another workspace. This is useful when different teams maintain different reports that share a common dimension.

### Setup

1. In Power BI Desktop, go to File → Options → Report settings
2. Enable "Allow visuals in this report to use drill-through to other reports"
3. On the target report's page, add the drill-through field to the Filters pane (same as basic drill through)
4. Publish both reports to the service
5. On the source page, right-click a data point → Drill through → the target report appears

**Requirements:**
- Both reports must be in workspaces the user has access to
- Both reports must share the same field name (the drill-through field must exist in both data models)
- The target report must be published to the Power BI Service (doesn't work in Desktop-only mode)

## Design patterns

### Pattern 1: Summary-to-transaction detail

The most common pattern. A summary page shows aggregated metrics (revenue by customer, sales by region). The detail page shows a table of individual transactions.

**Summary page:** Bar chart of revenue by customer
**Target page:** Table with transaction ID, date, amount, product, and quantity
**Drill-through field:** `Customer[Customer Name]`

Add a card visual at the top of the target page showing the customer name and total revenue — this orients the user when they arrive:

```dax
// Display on the target page
Selected Customer = SELECTEDVALUE(Customer[Customer Name], "Multiple Customers")
```

### Pattern 2: Drill through with dynamic titles

Make the target page self-documenting by showing what was drilled through:

1. Create a measure that captures the drill-through context:

```dax
Drill Through Title =
VAR Customer = SELECTEDVALUE(Customer[Customer Name])
VAR Product = SELECTEDVALUE(Product[Product Name])
RETURN
    "Details for " &
    IF(ISBLANK(Customer), "All Customers", Customer) &
    IF(ISBLANK(Product), "", " - " & Product)
```

2. Add a text box to the target page
3. Set the text box value to this measure (use the "Field" option in the text box formatting)

### Pattern 3: Multiple drill-through targets from one visual

A single visual can support multiple drill-through targets. Add multiple fields to the drill-through well on different pages:

- Page "Customer Details" drills through by `Customer[Customer Name]`
- Page "Product Details" drills through by `Product[Product Name]`

When the user right-clicks a data point, they see both options in the drill-through menu. This lets users choose their own level of detail.

### Pattern 4: Button-driven drill through

Instead of right-clicking, you can trigger drill through with a button:

1. Add a Button visual to the source page
2. Set the Action type to "Drill through"
3. Set the Destination to your target page
4. The button is grayed out until the user selects a data point
5. When a bar or row is selected, the button activates

This is more discoverable than right-click for users unfamiliar with Power BI.

## Common mistakes

### 1. Drill-through option doesn't appear

**Cause:** The visual on the source page doesn't include the drill-through field in any capacity (axis, legend, or detail).

**Fix:** The drill-through field must be present in the visual's field configuration. If you're drilling through by customer, the source visual must include the customer field somewhere — as the axis, legend, or in the tooltips.

### 2. Target page shows all data (no filter applied)

**Cause:** The drill-through field in the source visual doesn't match the field in the drill-through filter well. This often happens when the same column exists in multiple tables.

**Fix:** Ensure you're using the same field from the same table. If the source visual uses `Sales[Customer Name]` but the drill-through well has `Customer[Customer Name]`, the filter won't pass correctly.

### 3. Drill through works in Desktop but not in the Service

**Cause:** Cross-report drill through requires both reports to be published. Basic drill through can break if the target page was renamed after publishing.

**Fix:** Republish the report. If the issue persists, remove and re-add the drill-through field on the target page.

### 4. Too many fields passed to target page

**Cause:** "Keep all filters" is ON, and the source page has many slicers. The target page receives all of them, which may over-filter the results.

**Fix:** Turn off "Keep all filters" and manually add only the fields you need to the drill-through well. Or use `REMOVEFILTERS` on the target page to clear unwanted filters.

## Drill through vs. drill down vs. expand

These three features sound similar but do completely different things:

| Feature | What it does | When to use |
|---------|-------------|-------------|
| **Drill through** | Jumps to a different page, filtered to the clicked context | Summary → detail across different page layouts |
| **Drill down** | Expands a hierarchy within the same visual (Year → Quarter → Month) | Exploring hierarchical data in one visual |
| **Expand** | Shows all levels of a hierarchy at once | Quick view of all hierarchy levels |

Drill through changes pages. Drill down changes the level within a visual. Expand shows everything at once.

## FAQ

**Can I drill through from a matrix visual?**
Yes. Right-click a cell in the matrix and select "Drill through." The target page receives the filter context of that specific cell, including all row and column groupings.

**Can I pass a measure value through drill through?**
No. Drill through passes fields (dimensions), not measures. If you need the target page to show data related to a specific metric range, filter the source visual to that range and then drill through.

**How many drill-through fields can I add?**
There's no hard limit, but each additional field narrows the target page's context. In practice, 2-3 fields is the sweet spot. More than that, and users will struggle to understand why the target page shows what it shows.

**Does drill through work in Power BI mobile?**
Yes, but right-clicking isn't available on mobile. Use button-driven drill through (Pattern 4 above) for mobile-friendly reports. Tapping the button after selecting a data point triggers the drill through.

## What's next

- Learn [bookmarks and navigation](/tutorials/bookmarks-navigation-power-bi) to build interactive report tours that complement drill-through pages
- Read the [dashboard design principles](/tutorials/power-bi-dashboard-design-principles) guide to lay out your summary and detail pages effectively
- See the [tooltips guide](/tutorials/power-bi-tooltips-page-reports) for another way to show contextual detail without leaving the page
- Check the [sales dashboard tutorial](/tutorials/power-bi-sales-dashboard-tutorial) for an end-to-end walkthrough that includes drill-through pages
