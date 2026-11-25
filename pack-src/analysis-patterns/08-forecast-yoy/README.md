# 08 — Sales Forecast (YoY Growth Method)

**Question:** What does next period look like at last year's level plus an assumed growth rate?

## Tables and columns assumed

- `Sales` — `OrderDate`, `NetRevenue`
- `Date` — marked date table with `YearMonth`, `Year`
- `GrowthRate` — a what-if parameter table with a decimal column `GrowthRate` (e.g. 0.00 to 0.30, increment 0.01)

## Build steps

1. Load and relate the tables; make sure `Date` covers at least two full years.
2. Create the `GrowthRate` what-if parameter (Modeling → New parameter, decimal).
3. Paste `Measures.dax` into a `Forecast` folder.
4. Build a line chart with `Date[YearMonth]` on the axis, `Revenue` and `Forecast` as lines.
5. Add the `GrowthRate` slicer and cards for `Forecast Variance %` and `Months Above Forecast`.

## Self-check

With growth = 0, `Forecast` must equal `Revenue PY` exactly. The first year shows blank forecast (no prior year) — that is correct, not an error. `Months Above Forecast` counts only months where a forecast exists.

## Common traps

- Applying growth to current-year revenue instead of prior-year. That compounds the rate on itself and inflates the forecast. The baseline is always `Revenue PY`.
- Comparing forecast to the wrong actual. Align `Revenue` to the same period grain (month vs month) as the forecast.
- Expecting seasonality. This method carries last year's shape forward, so it keeps seasonal peaks. What it cannot do is predict a change in trend — that is why it is a baseline, not a forecast model.
- Using a non-contiguous date table. `SAMEPERIODLASTYEAR` and `DATESINPERIOD` both require a complete marked date table.
