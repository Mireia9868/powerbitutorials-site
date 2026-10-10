---
title: "Power BI Drillthrough: Step-by-Step Setup"
description: "Power BI drillthrough turns a summary visual into a starting point for investigation."
pubDate: 2026-10-10
category: visualization
tags: ["drillthrough"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

Power BI drillthrough turns a summary visual into a starting point for investigation. A user sees a bar for one region, right-clicks, and lands on a page that shows only that region's orders, customers, and products. The report stays one artifact, but the navigation behaves like a small application.

This tutorial walks through the complete setup: creating the detail page, wiring the drillthrough field, controlling what carries over, and handling the problems that show up most often (blank pages, disabled menu items, and filter state that refuses to clear).

## What drillthrough actually does

Drillthrough is a page-level filter. When a user triggers drillthrough on a visual, Power BI takes the value of the drillthrough field from the clicked data point and applies it as a filter on the target page. Every visual on the target page then renders with that filter in place.

Two things follow from that definition:

- The target page is a normal report page with visuals on it. There is no special visual type for drillthrough.
- The filter is driven by a field, not by a measure. Measures are not valid drillthrough targets because Power BI needs a column or hierarchy to pass through.

A common point of confusion: the drillthrough page is not a child of the source page. It is a sibling page that has been tagged as a drillthrough destination. The Back button that appears in the header is generated automatically.

## Step 1: Build or pick a detail page

Start with a page you already have, or add a blank one. Name it something a human can read, for example `Order Details`. The page name shows up in the drillthrough menu, so avoid names like `Page 3`.

The page should contain the visuals that answer "what happened here?" Typical candidates:

| Visual | Purpose on detail page |
|---|---|
| Table | Row-level transaction listing with order IDs and amounts |
| Card | Total sales, order count, average order value |
| Line chart | Trend over time for the filtered slice |
| Matrix | Product or category breakdown |

Resist the temptation to put twenty visuals on it. Drillthrough pages load on click, and a heavy page makes the transition feel broken.

If you want a visual to show a different value than the drillthrough filter implies, you can add page-level filters on top. Those stack with the drillthrough filter.

## Step 2: Add the drillthrough field

With the detail page selected, open the Visualizations pane and find the **Drill through** section. It may be collapsed at the bottom of the pane.

Drag the field you want users to drill by into **Add drill-through fields here**. In a star schema that is usually a dimension column such as `DimProduct[Category]` or `DimGeography[Country]`.

Behavior to note:

- **One field per bullet.** Each field you add creates a separate drillthrough action in the right-click menu.
- **Date hierarchies work.** Dropping `DimDate[Date]` gives you drillthrough at day, month, quarter, and year granularity depending on the level the user clicks.
- **Only columns and hierarchies qualify.** A measure dropped here is rejected or silently ignored.

Once a field is dropped in, Power BI adds a Back button and the page becomes reachable only through drillthrough. Users can still navigate to it via bookmarks or custom buttons, but it disappears from the normal page tab sequence.

## Step 3: Keep filters from the source page

By default, drillthrough carries two things: the drillthrough field value, and any filters that were active on the source page when the click happened. That second behavior surprises people.

Consider a source page where a user has already filtered to `Fiscal Year = FY2025`. They drill through on Region `EMEA`. The detail page opens with both filters applied. That is usually correct, but not always. If your detail page has its own slicers, the carried-over filter state can conflict with what the user expects.

Two controls matter:

- **Keep all filters** (default) passes everything through.
- Turning it off passes only the drillthrough field, giving a clean slate.

You configure this through the page's filter pane settings in the Format pane under **Page information**, or by clearing the slicer selections before publishing if the page is meant to be self-contained.

If the detail page has its own slicers, set them so they do not fight the incoming drillthrough filter. A slicer on the same column as the drillthrough field will show the drilled value pre-selected, which is fine. A slicer on an unrelated column just adds noise.

## Step 4: Measures on the detail page

Detail pages usually need measures that respond to the incoming filter. Standard measures do this automatically because the drillthrough filter becomes part of the filter context.

```dax
Orders in Slice =
COUNTROWS ( 'FactSales' )

Sales in Slice =
SUMX (
    'FactSales',
    'FactSales'[Quantity] * 'FactSales'[UnitPrice]
)

Average Order Value =
DIVIDE (
    [Sales in Slice],
    [Orders in Slice]
)
```

Nothing about these measures is drillthrough-specific. The filter context arrives from the page, and each measure evaluates inside it.

Where people get tripped up is measures that were authored to ignore filters with `ALL` or `REMOVEFILTERS`. If a measure clears the drillthrough column, the detail page will show company-wide numbers instead of the drilled subset. Check the filter modifiers before assuming drillthrough is broken.

## Step 5: Other ways to trigger drillthrough

Right-clicking a data point is the default gesture, but it is not the only one.

**Drillthrough button.** Insert a Button, set its Action type to **Drill through**, then choose the destination page and the field value to pass. This is how you build a clean "View details" affordance on a dashboard.

**Cross-report drillthrough.** In the Power BI Service, you can enable drillthrough to a page in a *different* report, provided both reports live in the same workspace or app and share the drillthrough field. Enable it in the Options dialog under **Report settings** (the target report must also opt in).

**Hierarchy drilling vs drillthrough.** These are different tools. The drill icons on a visual expand the visual in place; drillthrough navigates to another page. Mixing them up in documentation frustrates users.

## Common problems and fixes

**The drillthrough menu item is greyed out.** The visual you right-clicked does not contain the drillthrough field. A card showing Total Sales has no row to take a value from. Add the field to the visual (for example as a tooltip or in a table) or use a button instead.

**The detail page is blank.** Most often the drillthrough field is on the *wrong side* of a relationship, or the relationship is inactive. Filters flow one way from the one-side to the many-side by default. If you drilled on a fact column that has no filter path to your detail visuals, nothing renders. Check the model with reference to how relationships propagate.

**Users cannot see the page.** If the target page has no drillthrough field, it is a normal page and shows in the tab strip. Once a field is added, it leaves the tab strip. Some report authors panic and remove the field; instead, add a Back-friendly navigation button for direct access.

**Filter state feels stale.** If the detail page keeps showing an old region, a carried-over page filter is likely pinned. Clear page-level filters or set the page to not retain them.

**Drillthrough from a matrix does not pass the right level.** Matrix drillthrough passes the value at the level the user clicked. If the user clicks a subtotal row, the passed value is the subtotal, which may filter to multiple leaves. Design your detail visuals for that possibility.

## Testing checklist

Before publishing, run through this:

1. Drill through from every visual that offers the action.
2. Drill from the highest and lowest levels of any hierarchy.
3. Drill with no slicers active, then with two or three active, and confirm the carried state is what you want.
4. Check the Back button returns users to the source page with filters intact.
5. Verify that measures on the detail page respect the incoming filter.
6. Confirm that users without access to the underlying data see appropriate blanks rather than errors (row-level security interacts with drillthrough filters).

Drillthrough is one of the cheapest ways to make a report feel responsive. The setup is under ten minutes; the debugging is where the time goes, and almost all of it traces back to model relationships and filter propagation rather than the drillthrough configuration itself.

## FAQ

### Q: Can I drill through using a measure instead of a column?

No. The Drill through well accepts columns and hierarchies only. A measure has no stored row values for Power BI to pass from a clicked data point. If you need to segment by something only a measure can express, materialize it as a calculated column or use a field parameter, then drill on that.

### Q: Why does my drillthrough page show data from other regions too?

Something is clearing the drillthrough filter. The usual suspects are a measure using `ALL` or `REMOVEFILTERS` on the same column, a visual with "Edit interactions" set to None on the page, or a slicer on the detail page that was pre-set at publish time and overrides the incoming value. Check the filter pane's "Filters on this page" list first.

### Q: How do I let users drill through to a page in another report?

Both reports must be in the same workspace or app, and the drillthrough field must exist in both. In the target report, add the field to the Drill through well. In the source report, enable cross-report drillthrough in the Options dialog. In the Service, the feature must be enabled at the workspace level. Note that cross-report drillthrough does not work when the files are opened in Desktop.

### Q: Does drillthrough work with row-level security?

Yes, and RLS applies on the detail page exactly as it does elsewhere. If a user drills on a region their role does not permit, the detail page renders empty. That is expected behavior, not a bug, but it does mean you should test drillthrough under each RLS role before shipping.

### Q: Can I drill through on more than one field at once?

You can add multiple fields to the well, but each becomes its own separate menu entry. A single click passes one field's value. To filter by two columns simultaneously, either put a composite column in the model, or use a button with a `Drillthrough` action and pass the additional context through slicers or bookmarks.

### Q: What happens when a user drills from a subtotal?

Power BI passes the value of the cell the user clicked. For a subtotal row that means the parent-level value, so the detail page can legitimately show more rows than a leaf click would. If you want leaf-only behavior, hide subtotals on the source visual or restrict the drillthrough action through explicit buttons.

## Related Reading

- [Power BI Drill-Through](/tutorials/power-bi-drill-through/)
- [Bookmarks and Navigation in Power BI](/tutorials/bookmarks-navigation-power-bi/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/)
- [Bidirectional Filtering Guide](/tutorials/bidirectional-filtering-guide/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [DAX CALCULATE Function](/tutorials/calculate-function/)
- [Power BI Field Parameters](/tutorials/power-bi-field-parameters/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
