# 06 — Dynamic Top-N with "Other" Bucket

**Question:** Show me the top N products — and everything else as one row — controlled by a slicer.

## Tables and columns assumed

- `Sales` — `ProductKey`, `NetRevenue`
- `Products` — `ProductKey`, `ProductName`
- `TopN` — a what-if parameter table with a whole-number column `TopN` (1–20)
- `RankBucket` — a disconnected table with a `Label` column: numbers 1–20 as text, plus the text value "Other"

## Build steps

1. Create the what-if parameter in Power BI (Modeling → New parameter) named `TopN`, whole number, 1 to 20.
2. Create the disconnected `RankBucket` table: enter data with `Label` values "1","2",…,"20","Other". Do not relate it to anything.
3. Paste `Measures.dax` into a `Top N` folder.
4. Build a bar chart: `RankBucket[Label]` on the axis, `Display Revenue` as the value. Sort the axis by a helper numeric column if needed.
5. Add the `TopN` slicer and a card with `Display %`.

## Self-check

With N = 5, the six bars (top 5 + Other) must sum exactly to `Total Revenue (all)`. `Display %` across all bars must be 100%. If Other is negative, the ranks are not DENSE or `Total Revenue (all)` is being filtered.

## Common traps

- Forgetting that `RankBucket` is disconnected. If you relate it to `Products`, `SELECTEDVALUE` stops working and every row shows the same number.
- Using a calculated table for the top N. It will not respond to the what-if slicer; the measure-based approach here does.
- Ranks computed with `ALL` instead of `ALLSELECTED` — the top N would ignore a region slicer. `ALLSELECTED` is correct.
- Not including the "Other" row: a top-N chart that silently drops the rest makes the total wrong. The residual measure fixes that.
