---
title: "Power BI Slicers: Sync, Hierarchy, and Bookmark-Driven Filtering"
description: "Slicers look simple but a messy set destroys a report. Learn sync slicers across pages, build hierarchy slicers, and drive filters with bookmarks."
pubDate: 2026-09-23
category: "visualization"
difficulty: "Intermediate"
tags: ["power bi", "slicer", "sync slicers", "bookmarks", "report design"]
author: Mireia
featured: false
draft: false
---

Slicers are the first thing users touch in a Power BI report, and the first thing that feels broken when they are inconsistent. This guide covers the three techniques that separate a tidy report from a frustrating one: syncing slicers across pages, using hierarchy slicers, and replacing clumsy slicers with bookmark buttons.

## 1. Sync slicers across pages

By default a slicer only filters its own page. To make one Date slicer control every page:

1. Select the slicer → **Format** pane → **Slicer** → **Sync slicers** (or right-click → **Sync slicers**).
2. In the Sync pane, check the pages you want it to apply to, and check **Sync** and **Visible** per page.

<!-- TODO: add screenshot: Figure 1: power bi slicers best practices illustration -->

Now a filter set on page 1 carries to page 3. This is the single biggest UX win for multi-page reports.

## 2. Hierarchy slicer

Drop two fields into one slicer (e.g. `Category` then `Subcategory`). Users expand and collapse. This replaces two separate slicers and keeps related filters together.

For a cleaner look, use a **Dropdown** slicer with the hierarchy, or a **Tree** visual if you want a permanent expandable list.

## 3. Bookmark-driven filtering (replace slicers)

Heavy dropdowns clutter the canvas. Replace them with buttons that apply a bookmark:

1. Set the report to the filter state you want (e.g. Region = "North").
2. **View** → **Bookmarks** pane → **Add**.
3. Add a button → **Action** → **Bookmark** → select the bookmark.
4. Hide the underlying slicer (send to back / hide on the page, keep it on a hidden layer if needed for selection).

This is the pattern behind the popular "page navigator" menu. See [bookmarks-navigation-power-bi](/tutorials/bookmarks-navigation-power-bi/) for the full menu build.

## 4. Field parameters as a slicer

Let users switch the metric a visual shows by adding a **Field Parameter** and dropping it on a slicer. One slicer now controls *what* is measured, not just *how it is filtered*.

```dax
Measure Selector = {
    ("Sales", NAMEOF ( [Total Sales] ), 1),
    ("Profit", NAMEOF ( [Total Profit] ), 2),
    ("Quantity", NAMEOF ( [Total Quantity] ), 3)
}
```

## Common mistakes

- Putting the same slicer on every page without syncing → users think they reset it.
- Slicers on a hidden page losing their target after sync → always verify with a test click.
- Too many slicers → move secondary filters into drill-through or bookmarks.

## FAQ

**Q: Sync slicer vs filter pane — which is better?**
A: Slicers for the 2–3 filters users touch most; the Filters pane for fixed, report-level constraints.

**Q: Can a slicer filter another slicer's values?**
A: Yes, with "Edit interactions" → the slicer can filter a second slicer, but use it sparingly to avoid confusion.

**Q: Why do my synced slicers not match?**
A: They were added as separate visuals. Sync copies *values*, not the visual — rebuild one and sync it rather than copying.

Behaviour described here follows [Microsoft's Slicers in Power BI documentation](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers).

## Related Reading

- [Bookmarks Navigation](/tutorials/bookmarks-navigation-power-bi/)
- [Field Parameters](/tutorials/power-bi-field-parameters/)
- [Visual Types Guide](/tutorials/power-bi-visual-types-guide/)
- [Drill Through](/tutorials/power-bi-drill-through/)
- [Tooltips, Page, and Report](/tutorials/power-bi-tooltips-page-reports/)
- [Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/)
