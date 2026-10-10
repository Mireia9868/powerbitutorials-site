---
title: "Power BI Bookmarks: Build Interactive Reports"
description: "A Power BI bookmark captures the state of a report page at a point in time."
pubDate: 2026-10-10
category: visualization
tags: ["bookmarks", "interactivity"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

## What Bookmarks Actually Store

A Power BI bookmark captures the state of a report page at a point in time. That state includes the visibility of visuals, the active filters in slicers and filter cards (if you tell it to), the sort order of a table or matrix, drilled-down states, and the current selection in any visual that uses the *Selection pane*.

The common misconception is that a bookmark saves your data. It does not. A bookmark stores a snapshot of the report's *view state*. If your data model refreshes and the underlying numbers change, the bookmark still restores the same visual layout and filters, but the values shown will be the new ones. Bookmarks are a presentation-layer feature, not a data-layer one.

Two consequences follow from this. First, bookmarks are extremely cheap to create and maintain, so you can build dozens without hurting model performance. Second, any DAX or Power Query logic that drives the numbers is completely independent, so a bookmark is not a substitute for a calculated table of precomputed scenarios. If you want to store a reusable snapshot of *values*, you need a disconnected table or a What If parameter instead.

## Enabling and Using the Bookmarks Pane

Open the **View** ribbon and enable **Bookmarks** and **Selection** panes. Both are needed for most real workflows. The Selection pane controls which visuals are visible and their z-order; the Bookmarks pane stores which of those states to remember.

The capture behavior is controlled by three checkboxes that appear when you open the bookmark's context menu:

| Option | What it records |
|---|---|
| Data | Filter/slicer selections, drill state |
| Display | Visual visibility, focus mode, the current page |
| Current page | Whether the bookmark should jump to a specific page |

If you leave **Data** unchecked, the bookmark will restore visuals but respect whatever the user has currently filtered. That is often what you want for a "toggle view" bookmark and almost never what you want for a "reset filters" bookmark.

The technical catch: bookmarks read state from *report-level* and *visual-level* filters, but they do not capture cross-filter selection made by clicking a data point in a visual unless that visual is a slicer or you also captured the visual container's state. Clicking a bar to cross-filter does not get stored. If you need a persistent "selected category" state, use a slicer or a sync slicer behind the scenes.

## A Concrete Build: Sales Views Switcher

Here is a workflow you can repeat on almost any report. Suppose you have a Sales page with a line chart, a matrix, and a card visual.

1. Build the three visuals. Set visibility so all are shown.
2. Open **Selection** and rename the visuals to something readable: `line_sales`, `matrix_detail`, `card_kpi`.
3. Create a rectangle shape for a button background (optional) and add three buttons: "Trend", "Detail", "KPI".
4. Duplicate the current state by copying the page or by saving three bookmarks before changing anything.

Now configure each bookmark:

- **Bookmark "Trend"**: hide `matrix_detail` and `card_kpi`, show `line_sales`. Check **Data** and **Display**.
- **Bookmark "Detail"**: show only `matrix_detail`. Check **Data** and **Display**.
- **Bookmark "KPI"**: show only `card_kpi`. Check **Data** and **Display**.

Finally, select each button, open **Format > Action**, set Type to **Bookmark**, and pick the matching bookmark. Test with Ctrl+click in the Power BI service or just normal click in Desktop.

The reason this works reliably is that you are using the Selection pane, not hiding visuals with the "eye" in the canvas. Hiding via Selection and hiding via the visual header both record *Display* state, but the Selection pane keeps a stable name so you can reason about which visual is which. Rename everything.

## Driving a Measure with a Bookmark

Bookmarks are visual, but you can pair them with a disconnected table so the *measure* changes too. This is the pattern people reach for when they want "Show as %" toggles.

Create a small disconnected table:

```dax
ViewMode =
DATATABLE (
    "Mode", STRING,
    "Order", INTEGER,
    {
        { "Absolute", 1 },
        { "Percent",  2 }
    }
)
```

Make no relationship to the fact table. Then a measure that reacts to the selected mode:

```dax
Sales Display =
VAR SelectedMode =
    SELECTEDVALUE ( ViewMode[Mode], "Absolute" )
VAR TotalSales =
    SUM ( Sales[Amount] )
VAR GrandTotal =
    CALCULATE (
        SUM ( Sales[Amount] ),
        REMOVEFILTERS ( Product[Category] )
    )
RETURN
    SWITCH (
        SelectedMode,
        "Percent", DIVIDE ( TotalSales, GrandTotal ),
        TotalSales
    )
```

Bind `ViewMode[Mode]` to a slicer. Now create a bookmark per mode and capture **Data** so the slicer selection is stored. Clicking the bookmark sets the slicer value, which recalculates the measure.

The nuance: `SELECTEDVALUE` returns `BLANK()` if more than one value is selected in the slicer context, which is why the default value "Absolute" is supplied as the second argument. Without a default, the code would fall through to `SWITCH`'s else branch and show raw sales anyway, but explicit defaults make it obvious what happens on a multi-select.

## Bookmarks with Drill State

Drill state is stored when **Data** is captured on a matrix. If a user drills from Year to Month and you save the bookmark, restoring it will re-expand to Month for those rows. This is fragile if the underlying members change, since a bookmark references hierarchies and levels by ID. If someone deletes a member referenced by the drilled row, the restore can show an expanded-but-empty row.

Practical rule: save drill bookmarks only for hierarchies that will not be restructured, and always re-test them after a model refactor. If stability matters more than novelty, use drill-through pages instead and treat the bookmark as a navigation shortcut.

## Sync, Personalize, and the "Selected Visual" Gotcha

Bookmarks have a **group** concept. Grouping bookmarks is purely organizational; it does not sync state across pages. To carry state across pages, you need *sync slicers* with both the **Sync** and **Visible** columns checked, combined with a bookmark that captures the slicer selection. The bookmark restores the slicer on the target page.

There is one gotcha worth knowing. If a bookmark is triggered while a visual is selected on the canvas, the bookmark's *Display* state can conflict with the current selection highlight. Clearing the visual selection (click empty canvas) before saving the bookmark avoids a class of "my visual disappears when I click the button" bugs.

A second gotcha: bookmarks do not capture dynamic format strings. If a measure uses conditional formatting that reads `SELECTEDVALUE ( ViewMode[Mode] )`, changing the bookmark's slicer value will change the format only after recalculation on the next render. In practice this means avoid mixing bookmark-driven slicer values with dynamic format strings on the same visual unless you test each combination.

## Personal Bookmarks and Audience Assumptions

The service allows any reader to create *personal bookmarks* through the **Bookmarks** menu in the report header. These store per-user state and are visible only to that user. If your report relies on a bookmark to switch views, readers may create their own and get confused when your buttons override their saved view. Document the intended interaction on a help page, or disable personalization by setting the report's bookmark options to **None** under **File > Options and settings > Report settings**, if the audience requires it.

For most internal reports, leave personal bookmarks enabled and treat your own as the "official" views. Your buttons act as hard overrides; the reader's personal bookmarks act as soft overrides they can restore.

### Q: Why does my bookmark not restore the selected slicer value?

The most common cause is that **Data** was not checked when the bookmark was created. Open the bookmark's context menu in the Bookmarks pane and confirm Data is enabled, then re-save. Also verify the slicer is *not* in a sync group scoped to a different page without visibility enabled.

### Q: Can a bookmark change which measure is displayed?

Not directly. A bookmark restores filters and visibility. To change the *value* shown, pair the bookmark with a slicer bound to a disconnected table and a `SWITCH`-based measure, as shown above. Capture Data on the bookmark so the slicer selection is restored.

### Q: Do bookmarks survive a data refresh?

Yes, because they store view state, not data. The layout and filters restore exactly as saved, but the numbers behind them will reflect the latest refresh. If a saved bookmark referenced a drilled member that no longer exists, the expanded row can appear empty.

### Q: What is the difference between a bookmark and a field parameter?

A field parameter swaps the fields bound to a visual (for example, choosing between `Sales[Region]` and `Sales[Country]` on an axis) and is defined in the model. A bookmark swaps visual *state*. They complement each other: use a field parameter when the axis itself changes, and a bookmark when the layout, filters, or visibility changes.

### Q: How many bookmarks can a report have?

There is no documented hard limit, but the usability limit is around 20 on a single page before buttons crowd the canvas. Group bookmarks in the pane by purpose and consider splitting views across pages once you cross that threshold.

## Related Reading

- /tutorials/bookmarks-navigation-power-bi/
- /tutorials/power-bi-drill-through/
- /tutorials/power-bi-field-parameters/
- /tutorials/calculated-tables-what-if-parameters/
- /tutorials/dax-switch-function/
- /tutorials/power-bi-dashboard-design-principles/
- /tutorials/measure-vs-calculated-column/
