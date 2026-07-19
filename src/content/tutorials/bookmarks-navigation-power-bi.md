---
title: "Bookmarks and Navigation in Power BI: Build Interactive Report Tours"
description: "Bookmarks capture the state of a report page — filters, selections, visibility, and sort order. Combined with buttons, they turn a static page into an interactive experience: tabbed navigation, drill-through stories, and self-guided report tours. This guide covers the mechanics and four patterns that work."
pubDate: 2026-07-19
category: "visualization"
difficulty: "Intermediate"
tags: ["visualization", "bookmarks", "navigation", "buttons", "report-design"]
author: "Power BI Tutorials Team"
featured: false
---

A Power BI report page is a snapshot — but business questions are sequential. "Show me the overview, then let me drill into the problem region, then show me the underlying transactions." Bookmarks make this sequence navigable. This guide covers the mechanics and the patterns that transform a flat report into a guided experience.

## What bookmarks capture

A bookmark stores:

1. **Filters** — all slicers and visual-level filters on the page.
2. **Selection state** — which visual is selected, any cross-highlighting.
3. **Sort order** — how visuals are sorted.
4. **Visibility** — which visuals are showing and which are hidden.
5. **Spotlight** — whether any visual is in spotlight mode.
6. **Drill location** — the current drill level on visuals with hierarchies.

When a user clicks a bookmark, the page returns to that exact state.

## Creating bookmarks

**View → Bookmarks Pane → Add.** Each bookmark gets a name and can be renamed. Bookmarks are added to the pane in sequence.

**Bookmark properties** (right-click a bookmark):

- **Data:** capture current filter/slicer state. Disable if you want the bookmark to change only visibility, not filters.
- **Display:** capture visual visibility and selection. Disable if you want the bookmark to change only filters.
- **Current page:** if disabled, the bookmark stays on the current page. Enable to make the bookmark navigate to a specific page.

## Pattern 1: Tabbed navigation

Build tabs at the top of the page that switch between different views (e.g., "Revenue," "Orders," "Customers").

**Step 1:** Create one visual set per view. Position them in the same area so switching looks seamless.

**Step 2:** Create a bookmark for each view, with only that view's visuals visible. Hide the others.

**Step 3:** Add buttons at the top (Insert → Button → Blank). Each button's action is "Bookmark," pointing to the corresponding bookmark.

**Step 4:** Set the button text to the view name ("Revenue," "Orders," "Customers").

Now clicking a button shows one set of visuals and hides the others — a tabbed interface within a single page.

## Pattern 2: Drill-through story

Guide users from summary to detail within one page.

**Step 1:** Create a summary view (cards and a bar chart) at the top of the page.

**Step 2:** Create a detail view (a matrix with transaction-level data) below it, initially hidden.

**Step 3:** Create two bookmarks:
- "Summary" — detail hidden, summary visible.
- "Detail" — detail visible, summary hidden.

**Step 4:** Add a "Drill Down" button on the summary view that navigates to the "Detail" bookmark. Add a "Back" button on the detail view that returns to "Summary."

Users click "Drill Down" to see transactions, "Back" to return. The interaction is explicit and guided.

## Pattern 3: Self-guided report tour

Build a sequence of bookmarks that walk a user through the report, like a presentation.

**Step 1:** Create bookmarks in the order you want the tour to proceed: "Step 1: Overview," "Step 2: Trend Analysis," "Step 3: Regional Drill-Down," etc. Each bookmark captures the state for that step.

**Step 2:** Add "Next" and "Previous" buttons. Each button's action navigates to the next or previous bookmark in sequence.

**Step 3:** Optionally, add a text box that explains each step — visible only on that bookmark.

This pattern is excellent for executive reports where the audience needs context for each view.

## Pattern 4: Dynamic filter buttons

Use bookmarks to apply preset filters via buttons (e.g., "This Year," "Last Year," "Year-to-Date").

**Step 1:** Set the slicer to "This Year" and create a bookmark named "This Year" (with Data enabled, Display disabled).

**Step 2:** Set the slicer to "Last Year" and create a bookmark named "Last Year."

**Step 3:** Add two buttons. Each button's action points to the corresponding bookmark.

Users click "Last Year" and the slicer (and all visuals) update instantly — without touching the slicer directly.

## Common mistakes

**Mistake 1: Too many bookmarks.** A page with 20 bookmarks is as confusing as no bookmarks. Aim for 3–7 per page, each with a clear purpose.

**Mistake 2: Not naming bookmarks clearly.** "Bookmark 1," "Bookmark 2" means nothing a month later. Name them by purpose: "Revenue View," "Orders View," "Detail Drill."

**Mistake 3: Forgetting to update bookmarks after changing the page.** If you add a visual or change a filter, existing bookmarks may not capture the new state. Review bookmarks after any page edit.

**Mistake 4: Bookmark buttons that don't look clickable.** Users won't click something that looks like a label. Style buttons with a hover state, a border, or an icon (arrow, chevron) to signal interactivity.

## Button styling tips

- **Shape:** use rectangles with rounded corners for a modern look.
- **Fill:** a subtle background color (light gray) with a darker fill on hover.
- **Text:** clear, action-oriented labels ("View Detail," "Reset Filters," "Next").
- **Icon:** add a small icon (→ for next, ← for back) to reinforce clickability.
- **Alignment:** align buttons consistently — a row at the top or a column on the left.

## Summary

Bookmarks capture report state — filters, visibility, selections — and buttons let users navigate between states. Use them for tabbed navigation, drill-through stories, self-guided tours, and preset filter buttons. Keep bookmark counts low (3–7 per page), name them clearly, and style buttons to look interactive. The result is a report that guides users through a narrative rather than dumping data on a page.
