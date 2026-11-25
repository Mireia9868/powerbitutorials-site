# 01 — RFM Segmentation

**Question:** Which customers are worth reactivating, and which are worth protecting?

## Tables and columns assumed

- `Sales` — `CustomerKey`, `OrderKey`, `OrderDate`, `NetRevenue`
- `Customers` — `CustomerKey`, `CustomerName`
- `Date` — `Date`, marked as a date table, one-to-many to `Sales[OrderDate]`

## Build steps

1. Load the three tables and create the relationship `Date[Date] → Sales[OrderDate]` (one-to-many, single direction).
2. Paste `Measures.dax` into a display folder called `RFM`.
3. Put `CustomerKey` and `CustomerName` from `Customers` on a table visual.
4. Add `Recency`, `R Score`, `F Score`, `M Score`, `RFM Cell` and `Segment` as columns.
5. Add `Customers in Segment` to a card, and `Segment` to a slicer using the values from the table.

## Self-check

With all filters cleared, every customer resolves to exactly one `RFM Cell` and one `Segment`. `Recency` is never negative. If `Last Order Date` returns blank, the relationship to `Date` is missing or the fact dates are outside the date table range.

## Common traps

- Using `TODAY()` for recency. On a static dataset this marks everyone lapsed and the scores become meaningless. Anchor to the last model date.
- Scoring with fixed buckets (e.g. "recency < 30 = 5") — those thresholds do not survive a change in dataset size. `RANKX` adapts.
- Reading a segment at total level. `Segment` returns blank unless a customer is in scope, which is deliberate: a total row has no segment.
- Forgetting `ALLSELECTED` in the rank. `ALL` ignores slicers; `ALLSELECTED` respects them, which is what you want when a user filters to one region.
