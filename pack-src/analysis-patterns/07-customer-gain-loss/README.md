# 07 — Customer Gain / Loss

**Question:** Did the active customer base grow this period, and from whom?

## Tables and columns assumed

- `Sales` — `CustomerKey`, `OrderDate`, `NetRevenue`
- `Date` — marked date table with `Year`, `Month`, one-to-many to `Sales[OrderDate]`

## Build steps

1. Load and relate the tables.
2. Paste `Measures.dax` into a `Customer Movement` folder.
3. Use a `Year` / `Month` slicer on `Date` to define "this period". Everything compares to the immediately preceding period via `PREVIOUSPERIOD`.
4. Put `Customers (period)`, `New Customers`, `Retained Customers`, `Lost Customers` and `Net Customer Change` on cards.
5. Add `Revenue from Retained` alongside total `Revenue (period)` to see how much income depends on returning customers.

## Self-check

`New Customers + Retained Customers` should equal `Customers (period)` when every customer active now was either active before or genuinely new. If the numbers do not reconcile, check the `Date` table is contiguous and marked — `PREVIOUSPERIOD` needs a proper date table.

## Common traps

- Comparing to the same period last year when you meant last month. `PREVIOUSPERIOD` steps back one grain of the current `Date` context; put a single `Month` in scope, not a whole year, or the comparison silently changes meaning.
- Counting distinct customers across a broken date table. Gaps in `Date` make `PREVIOUSPERIOD` skip days.
- Treating "Lost" as churn forever. A lost customer this month can return next month and become reactivated. This pattern measures period-to-period movement, not lifetime churn.
- Reading these at grand-total level. The `FILTER ( VALUES ( Sales[CustomerKey] ) ... )` pattern is designed to work per customer and roll up; make sure the customer key is in the visual when debugging.
