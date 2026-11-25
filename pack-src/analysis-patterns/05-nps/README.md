# 05 — Net Promoter Score

**Question:** What share of respondents are promoters minus detractors?

## Tables and columns assumed

- `Responses` — `ResponseKey`, `CustomerKey`, `ResponseDate`, `Score` (integer 0–10)
- `Date` — marked date table with `Year`, one-to-many to `Responses[ResponseDate]`

## Build steps

1. Load `Responses`, relate it to `Date`. Make sure `Score` is a whole number, not text.
2. Paste `Measures.dax` into an `NPS` folder.
3. Put `NPS` on a card. Set the card to show 0 decimal places and append the "NPS" label manually.
4. Add a stacked bar with `Response Group` on the legend and `Responses (count)` as the value to see the three groups.
5. Add `NPS (latest year)` to a second card for the current-year reading.

## Self-check

`Promoters + Passives + Detractors` must equal `Responses (count)`. NPS must land between −100 and +100. If NPS reads 0 with responses present, the `Score` column is text ("9" instead of 9) and the `>=` filters do not match.

## Common traps

- Averaging NPS across periods. NPS is not additive: an average of monthly NPS values is not the yearly NPS. Always recompute from raw responses over the period, which is what `NPS (latest year)` does.
- Showing zero when there are no responses. The guard returns blank so an empty period does not drag a visual to zero.
- Wrong score bands. The standard is 9–10 / 7–8 / 0–6. If your survey uses a different scale, change all three measures together.
- Text scores from survey exports. Cast `Score` to a whole number in Power Query before the measures run.
