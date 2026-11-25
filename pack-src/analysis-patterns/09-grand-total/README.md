# 09 — Grand Total Fixes

**Question:** Why does the total row show a number that disagrees with the rows above it?

## Tables and columns assumed

- `Sales` — `Category`, `NetRevenue`, `Units`, `UnitPrice`, `UnitCost`

This pattern is four independent fixes in one file. Use the one that matches your symptom.

## Build steps

1. Load `Sales`.
2. Paste `Measures.dax` into a `Total Fixes` folder.
3. Build a table with `Category` on rows and add the measures one at a time to see each behaviour.
4. Compare `Unit Price (correct)` against `Unit Price (wrong)` at the total row — the wrong one sums prices, which is meaningless.
5. Compare `Margin %` and `Margin % (display)` at the total to see weighted vs simple logic.

## Self-check

`Unit Price (correct)` at total = total revenue ÷ total units. `Categories with Sales` at total = the number of non-empty category rows, not the count of all rows. `Rank (display)` is blank on the total row and an integer on each category.

## Common traps — the four fixes explained

- **Summing a ratio.** A ratio (price, margin %, average) has no additive total. Recompute it from its numerator and denominator at the current grain.
- **Counting rows when you mean distinct groups.** `COUNTROWS(Sales)` at total counts transactions, not categories. Iterate `VALUES(Category)` instead.
- **Letting a measure use row logic at total.** `HASONEVALUE` tells you whether you are at one category or at the total; switch to weighted logic at the total.
- **Showing a rank or score at total.** There is nothing to rank at the total level. `ISINSCOPE` blanks it so the total stays honest.

The general rule: at the total row, ask "what does this number mean here?" If it has no meaning, blank it. If it has a different meaning, write different logic.
