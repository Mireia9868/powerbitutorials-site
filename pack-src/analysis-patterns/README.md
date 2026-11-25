# Analysis Patterns Pack — 10 classic business models, rebuilt in DAX

Ten self-contained analysis patterns for Power BI. Each one is a plain-text
package: a commented `.dax` measure file, a build README, and (where relevant)
a Power Query script. No `.pbix`, no external data, no custom visuals.

Everything here is written from scratch against generic tables. Nothing is
copied from any third-party report. Use the files in your own models and in
client work. Do not resell or redistribute them as your own template pack.

## The ten patterns

| # | Pattern | Question it answers | Files |
|---|---------|--------------------|-------|
| 01 | RFM Segmentation | Which customers are worth reactivating? | Measures.dax, README.md |
| 02 | Market Basket Analysis | Which products are bought together? | Measures.dax, MakePairs.pq, README.md |
| 03 | ABC / Pareto | Which 20% of products drive 80% of revenue? | Measures.dax, README.md |
| 04 | BCG Portfolio Matrix | Which products are stars, cows, questions or dogs? | Measures.dax, README.md |
| 05 | NPS | What share of customers are promoters minus detractors? | Measures.dax, README.md |
| 06 | Dynamic Top-N | Show the top N by a measure, with a live "Other" bucket | Measures.dax, README.md |
| 07 | Customer Gain / Loss | Did the customer base grow, and from whom? | Measures.dax, README.md |
| 08 | Sales Forecast (YoY) | What does next month look like at last year's growth? | Measures.dax, README.md |
| 09 | Grand Total Fixes | Why does the total row show the wrong number? | Measures.dax, README.md |
| 10 | Dynamic Date Dimension | A marked date table with fiscal-year support | DateTable.pq, Measures.dax, README.md |

## How to use a pattern

1. Open the pattern's `README.md`. It lists the exact table and column names
   the measures assume.
2. Load your data into Power BI with those names, or rename your columns to
   match. The DAX assumes a single fact table and a marked `Date` table where
   a pattern is date-based.
3. Paste `Measures.dax` into a new measure folder. Every measure is commented
   with the trap it avoids.
4. Follow the build steps in the README and check the numbers against the
   self-check section before adding visuals.

## Conventions used throughout

- Fact tables are named `Sales` or `Responses`. Dimensions are `Customers`,
  `Products`, `Date`.
- Revenue and cost are stored positive. Margin is a subtraction, never a
  sign-flip.
- The date table is marked as a date table and related one-to-many,
  single-direction to each fact.
- Measures live in display folders. Base measures come first; derived measures
  reference them rather than repeating logic.
- `DIVIDE` is used wherever a denominator can be zero.

## Licence

Personal and commercial use, including client work, is permitted. You may
modify the files and use them in reports you deliver. You may not resell,
redistribute or republish the `.dax`, `.pq` or README files as your own
template pack, course asset or marketplace product.

Corrections: if a measure is wrong or a step is unclear, email
hello@powerbitutorials.com. Fixed files are sent to everyone who bought the
pack.

---

Power BI Tutorials — https://powerbitutorials.com
