# 04 — BCG Portfolio Matrix

**Question:** Which products are stars, cash cows, question marks or dogs?

## Tables and columns assumed

- `Sales` — `ProductKey`, `NetRevenue`, `OrderDate`
- `Products` — `ProductKey`, `ProductName`
- `Market` — `ProductKey`, `MarketRevenue` (category total including competitors)
- `Date` — marked date table with a `Year` context

## Build steps

1. Load the four tables; relate `Products` and `Market` to `Sales` on `ProductKey`, and `Date` to `Sales[OrderDate]`.
2. Paste `Measures.dax` into a `BCG` folder.
3. Build a scatter chart: x-axis `Relative Market Share` (set axis to reverse so the leader is on the left), y-axis `Market Growth`, and drop `ProductName` into Details.
4. Add `BCG Class` to a table with `ProductName`, and `Products in Class` to a card.

## Self-check

`Relative Market Share` of 1.0 means the product equals the market leader. A product with our revenue below the leader's gets a value under 1. `Market Growth` is blank in the first year (no prior period) — those products fall to "Dog" by the SWITCH; filter them out or supply a prior-year benchmark.

## Common traps

- Mixing time grains. `Market Revenue` and `Product Revenue` must cover the same period, or relative share is meaningless. Align both to the same year before plotting.
- Treating the 1.0 and 10% thresholds as universal. They are defaults; real portfolios use industry-specific cut-offs. Change the two literals in `BCG Class`.
- Forgetting to reverse the x-axis. Standard BCG convention puts high share on the left; without reversing it the quadrants read backwards.
- Reading a class at total level. The `ISINSCOPE` guard blanks it deliberately.
