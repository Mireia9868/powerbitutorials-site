---
title: "Power BI Slicers: Sync, Hierarchy and Filtering"
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

## 5. Dropdown slicer: fit more filters in less space

A dropdown slicer collapses its values behind a single control, so you can keep six or seven filters on one page without stacking full lists. It is the default choice when a field has more than about ten distinct values.

1. Add a slicer, put the field in **Field**.
2. In **Format → Slicer → Slicer type**, choose **Dropdown**.
3. Turn on **Show search** if the list is longer than a screen, and enable **Multi-select** (Ctrl+click) for users who need several values at once.
4. Set **Selection** to **All** so no filter is applied when the page first opens.

The trade-off is discoverability: users cannot see which values are selected without opening the control. If the visible selection state matters more than space, use the checkbox slicer below. Dropdowns also work as hierarchy slicers — drop `Category` then `Subcategory` into one control — but a nested dropdown shows one level at a time, so keep the hierarchy two levels deep.

The sync behaviour described in section 1 still applies: a dropdown synced across pages carries its selection exactly like a list slicer does.

## 6. Checkbox slicer: let users see and multi-select values

The checkbox slicer (**Format → Slicer → Slicer type → Checkbox**) shows a tick box next to every value, so the current selection is visible at a glance. It replaced the older "Tile" style and is the better pick for short lists — regions, channels, business years — where users regularly select several values.

- **Best for:** 3–15 values, frequent multi-select, selection state that must be obvious without clicking.
- **Search and Select all:** enable **Show search** for longer lists and **Show Select all** so users can reset in one click.
- **Single value only?** Use a dropdown or a button-driven bookmark instead; a checkbox with one possible tick wastes space.

One caution: checkbox slicers filter *other* visuals, but are not filtered by them unless you set **Edit interactions** deliberately. If the checkbox list collapses when a user clicks a chart, select the chart → **Format → Edit interactions** and set the slicer interaction to **None**. Keep the list short — a 200-value checkbox list becomes a scroll trap and makes the report feel slower than it is.

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

- [Tableau vs Power BI: Which Should You Choose in 2026](/tutorials/tableau-vs-power-bi/)
- [Power BI Bookmarks: Build Interactive Reports](/tutorials/power-bi-bookmarks/)
- [Power BI Conflicting Metrics Error: Causes and Fixes](/tutorials/power-bi-conflicting-metrics/)
- [What Is Power BI? A Complete Beginner Overview](/tutorials/what-is-power-bi/)