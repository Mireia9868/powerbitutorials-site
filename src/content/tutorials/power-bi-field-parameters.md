---
title: "Power BI Field Parameters: Let Users Swap Metrics and Dimensions"
description: "Field Parameters let report users dynamically switch between measures or dimensions in a single visual — no bookmarks, no separate pages. Learn setup, slicer integration, DAX integration, limitations, and common mistakes."
pubDate: 2026-07-26
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "field-parameters", "dynamic-reports"]
author: "Power BI Tutorials Team"
---

Field Parameters are a Power BI feature that lets users dynamically choose which fields or measures appear in a visual. Instead of building separate charts for Sales, Profit, and Quantity — or creating complex bookmark navigation — you create one visual and let users swap the metric with a slicer.

This guide covers how to set up Field Parameters, integrate them with slicers, combine them with DAX, work around their limitations, and avoid the common mistakes that break dynamic reports.

## What Field Parameters Solve

Before Field Parameters, there were two ways to let users switch metrics:

1. **Bookmark navigation** — Build separate visuals for each metric, then use bookmarks and buttons to show/hide them. Complex, fragile, and doubles the visual count.
2. **SWITCH measures** — Use a disconnected table with `SELECTEDVALUE()` and a `SWITCH()` measure. Works but requires DAX knowledge and does not support swapping dimensions (only measures).

Field Parameters solve both problems. They work for measures **and** dimensions, require no DAX, and are native to Power BI's visual framework.

## Creating a Field Parameter

**Step 1:** In Power BI Desktop, go to **Modeling** tab → **New parameter** → **Fields**.

**Step 2:** In the Fields parameters dialog:
- Name the parameter (e.g., "Metric Selector")
- Add the fields or measures you want users to choose from
- Optionally set a default selection

**Step 3:** Click **Create**. Power BI generates:
- A calculated table with the parameter definition
- A slicer visual on the current page
- A card visual showing the selected value

The generated DAX table looks like this:

```dax
Metric Selector = {
    ("Total Sales", NAMEOF('Measures'[Total Sales]), 0, "Currency"),
    ("Total Profit", NAMEOF('Measures'[Total Profit]), 1, "Currency"),
    ("Total Quantity", NAMEOF('Measures'[Total Quantity]), 2, "Quantity"),
    ("Average Order Value", NAMEOF('Measures'[Average Order Value]), 3, "Currency")
}
```

Each row contains: display name, field reference (using NAMEOF), sort order, and an optional format string category.

## Using Field Parameters in Visuals

**Step 1:** Drag the Field Parameter (e.g., "Metric Selector") into the **Columns** or **Values** well of any visual.

**Step 2:** When a user selects "Total Profit" in the slicer, the visual automatically displays the Total Profit measure. When they select "Total Quantity", the visual switches to showing quantities.

The magic: Power BI treats the Field Parameter as a dynamic field reference. The visual's rendering engine swaps the underlying measure without you writing any DAX or creating bookmarks.

### Swapping Dimensions

Field Parameters are not limited to measures. You can let users switch between dimensions too:

- Create a parameter with "Category", "Sub-Category", and "Region" fields
- Drop it into the **Axis** well of a bar chart
- Users can now switch the grouping level with a slicer

This is something SWITCH measures could never do — they only swap calculations, not grouping fields.

## Combining with Slicers

The slicer that Power BI auto-generates works out of the box, but you can customize it:

**Horizontal slicer for a compact toolbar:**
1. Select the slicer → **Format** pane → **Slicer settings** → **Orientation** → **Horizontal**
2. Resize to fit across the top of the report

**Single-select enforcement:**
By default, Field Parameter slicers allow only single selection. This is correct — multi-select does not make sense for swapping fields.

**Syncing across pages:**
Use the **View** tab → **Sync slicers** pane to sync the Field Parameter slicer across multiple report pages. This lets users pick a metric once and see it applied everywhere.

## Integrating with DAX Measures

Field Parameters work alongside your existing DAX measures. You can reference the parameter selection in other calculations:

```dax
-- Get the currently selected parameter display name
Selected Metric = SELECTEDVALUE('Metric Selector'[Metric Selector])
```

This is useful for dynamic titles:

```dax
Chart Title = "Performance by " & SELECTEDVALUE('Metric Selector'[Metric Selector])
```

Or for conditional formatting based on which metric is active:

```dax
Color by Metric = SWITCH(
    TRUE(),
    SELECTEDVALUE('Metric Selector'[Metric Selector]) = "Total Profit", "#22C55E",
    SELECTEDVALUE('Metric Selector'[Metric Selector]) = "Total Quantity", "#3B82F6",
    "#F2C811"
)
```

## Field Parameters vs Bookmarks vs SWITCH Measures

| Feature | Field Parameters | Bookmarks | SWITCH Measures |
|---------|-----------------|-----------|-----------------|
| Swap measures | ✅ | ✅ (show/hide visuals) | ✅ |
| Swap dimensions | ✅ | ✅ (show/hide visuals) | ❌ |
| DAX required | ❌ | ❌ | ✅ |
| Single visual | ✅ | ❌ (one per metric) | ✅ |
| Cross-page sync | ✅ | ❌ | ✅ |
| Dynamic formatting | ✅ | ❌ | ⚠️ Manual |
| Learning curve | Low | Medium | High |

**When to use Field Parameters:** Most dynamic metric/dimension switching scenarios. This should be your default choice.

**When to use bookmarks:** Complex navigation with layout changes (different visual types per view, not just different fields). See our [bookmarks navigation guide](/tutorials/bookmarks-navigation-power-bi/).

**When to use SWITCH measures:** When you need custom logic that Field Parameters cannot handle (e.g., conditional calculations based on the selection rather than just swapping the displayed measure).

## Limitations and Workarounds

### 1. Not Available in All Visuals
Field Parameters work in most standard visuals (bar, column, line, pie, table, matrix). Some custom visuals and the Q&A visual do not support them.

**Workaround:** Test your specific visual before building the full report. If unsupported, fall back to bookmarks.

### 2. Cannot Be Used in Calculated Tables
You cannot create a calculated table that references a Field Parameter. The parameter is a runtime concept — it exists in the report layer, not the model layer.

### 3. Format Strings Are Per-Field
Each measure retains its own format string. If your measures have inconsistent formatting (some with currency symbols, some without), the visual will look inconsistent when users switch between them.

**Fix:** Standardize format strings across all measures included in the parameter, or use the optional format string category in the parameter definition.

### 4. Does Not Work with Row-Level Security Filtering
Field Parameters themselves are not filtered by RLS. However, the underlying measures they reference are. This is usually fine — just be aware that the parameter slicer shows all options regardless of the user's RLS role. See our [Row-Level Security guide](/tutorials/power-bi-row-level-security/) for more details.

### 5. Performance with Large Parameter Lists
Field Parameters with 10+ options can slow down the slicer rendering. Keep parameter lists to 5-7 options for best UX.

## Common Mistakes

### 1. Adding the Parameter to the Wrong Visual Well
```
❌ Adding "Metric Selector" to the Filters well → does nothing useful
✅ Adding "Metric Selector" to the Columns or Values well → visual swaps fields
```

### 2. Trying to Multi-Select
Field Parameters are single-select by design. If you try to enable multi-select, the visual will show blank or error because it cannot display two measures simultaneously in the same axis position.

### 3. Forgetting to Sync Slicers Across Pages
If you use the Field Parameter on multiple report pages but do not sync the slicer, users will be confused when different pages show different metrics.

**Fix:** Use **View** → **Sync slicers** to sync the parameter across all pages where it appears.

### 4. Editing the Generated Table Manually
Power BI generates the parameter table with `NAMEOF()` references. If you edit the DAX manually and break the NAMEOF syntax, the parameter stops working.

**Fix:** Use the **Edit** button in the Fields parameter dialog (Modeling → New parameter → Fields → right-click existing parameter → Edit) rather than editing the DAX directly.

## FAQ

**Q: Do Field Parameters work in Power BI Service (online)?**

Yes. Field Parameters are fully supported in the Power BI Service, including in published reports, dashboards, and embedded scenarios. They also work in Power BI mobile apps.

**Q: Can I use Field Parameters with calculated measures that use CALCULATE?**

Yes. Any measure — including complex CALCULATE-based measures with filter modifications — can be added to a Field Parameter. The parameter simply swaps which measure the visual renders. See our [CALCULATE function guide](/tutorials/calculate-function/) for building measures that work well in dynamic contexts.

**Q: Are Field Parameters supported in Excel?**

No. Field Parameters are a Power BI feature. Excel PivotTables do not support dynamic field swapping in the same way.

**Q: Can I sort the parameter options alphabetically?**

Yes. By default, the parameter uses the sort order you defined during creation. To change it, edit the parameter and reorder the fields, or sort the parameter column directly in the Data view.

**Q: Do Field Parameters affect report performance?**

Minimally. The parameter itself adds no query overhead — it simply tells the visual which measure to request. Performance depends on the complexity of the underlying measures. For optimization tips, see our [Power BI performance optimization](/tutorials/power-bi-performance-optimization/) guide.

## What's Next

- Learn an alternative dynamic reporting technique: [Bookmarks and navigation](/tutorials/bookmarks-navigation-power-bi/)
- Build measures that work well in Field Parameters: [CALCULATE function](/tutorials/calculate-function/)
- Design report pages that leverage dynamic switching: [Dashboard design principles](/tutorials/power-bi-dashboard-design-principles/)
- Add interactivity layers with drill-through: [Power BI drill through](/tutorials/power-bi-drill-through/)
