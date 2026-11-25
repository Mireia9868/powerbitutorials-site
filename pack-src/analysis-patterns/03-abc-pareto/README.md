# 03 — ABC / Pareto Analysis

**Question:** Which small share of products drives most of the revenue?

## Tables and columns assumed

- `Sales` — `ProductKey`, `NetRevenue`
- `Products` — `ProductKey`, `ProductName`
- Relationship `Products[ProductKey] → Sales[ProductKey]`, one-to-many

## Build steps

1. Load and relate the tables.
2. Paste `Measures.dax` into an `ABC Pareto` folder.
3. Build a table visual with `ProductName`, `Product Revenue`, `Cumulative %` and `ABC Class`.
4. Add a card with `Products in Class`, sliced by `ABC Class`.
5. For a Pareto chart: combo visual with `Product Revenue` as columns and `Cumulative %` as a line, products sorted by `Product Rank`.

## Self-check

With no slicers, `Cumulative %` reaches exactly 100% at the last product. `ABC Class` is blank on the total row and populated on every product row. The A products should account for roughly 70% of revenue — if the number is far off, check that `Total Revenue (all)` is not being filtered by the visual.

## Common traps

- Using a calculated column for cumulative share: it freezes when a user slices by region. This pattern is measure-based and stays live.
- `ALLSELECTED` vs `ALL`: `ALLSELECTED` keeps the user's slicer context, so the classification recomputes within a selected region or year.
- Ties in `Product Rank` with `DENSE` — products with equal revenue share a rank and both get the same class, which is the desired behaviour.
- Forgetting `ISINSCOPE` in `ABC Class`: without it the total row picks an arbitrary class and the card double-counts.
