# Review: power-bi-sales-dashboard

# Review: `power-bi-sales-dashboard`

## 1. AI-isms

The draft is mostly clean, but several tell-tale patterns stand out.

- **Vague authority openers.** "Real exports are rarely this clean, which is exactly why step one is about cleanup" and "Note that `Gross Margin %` uses `DIVIDE` rather than the `/` operator" both preface the point with throat-clearing. Rewrite: "Clean the dates, costs, and keys first" / "`DIVIDE` returns blank on zero denominators; `/` throws an error."
- **Mechanical list framing.** "Three things usually need fixing...", "Three formatting rules that separate...", "Two features raise the value..." — the counted intro is the classic LLM tic. Drop the number and let the list speak: "Fix these in Power Query first:" / "Formatting rules:" / "Two features are worth the time:" (keep numbers only if they carry information).
- **"Worth doing" / "worth the time" filler.** "That is worth doing on the margin matrix" adds nothing. Cut the sentence or replace with the concrete effect: "Driving the margin matrix from a color measure makes weak regions read as red without extra labels."
- **Em-dash habit.** "The usual failure mode is not a broken chart: it is a report..." and "`Sales LY` ... is not decoration: it guarantees..." — two colons used in the same rhetorical slot within a short piece reads as a style crutch. Vary with a period or restructure.
- **Hollow transitions.** "Keep the line chart as the hero" is fine, but "Comparison against last year is the fastest way for a reader to answer..." is explanation-of-explanation. Trim to: "Current-year solid, prior-year dashed and muted."
- **"Not X: it is Y" formula repeated.** Appears in intro and again with the `VAR` paragraph. Once is voice; twice is template.

No major em-dash abuse, no "In today's fast-paced world," no "Let's dive in." Tone is actually decent for the category.

## 2. Topic fit

- **Rankability.** "Power BI sales dashboard" is a competitive head term, not long-tail. The slug `power-bi-sales-dashboard` will struggle against Microsoft Learn, Enterprise DNA, and YouTube results for the bare phrase. That's a problem for a 1k UV/day goal.
- **Better angles** (pick one, retitle, keep the body):
  - `power-bi-sales-dashboard-step-by-step` — captures "step by step" intent, still broad.
  - `power-bi-sales-dashboard-beginner-tutorial` — clearer intent match to the difficulty tag.
  - `power-bi-sales-dashboard-dax-measures` — narrows to the differentiating part (the `_Measures` table, YoY pattern), where your DAX cluster already ranks and can internally link.
  - `power-bi-sales-dashboard-from-flat-csv` — long-tail, matches the actual hook of the article ("from a flat order table").
- **Fit with the 1k UV/day goal.** As written, it's a beginner tutorial competing with the entire internet for a head term. It will rank poorly and cannibalize nothing, but contribute little. The realistic play: retitle to a long-tail variant, and lean on the existing DAX cluster (which you clearly have — see the real slugs list) for internal link juice.
- **FAQ section is good.** Long-tail queries ("why does my YoY percentage show infinity", "how many visuals per dashboard page") are exactly the kind of questions that surface in People Also Ask and ranked snippets. Keep and expand.
- **Missing angle that would differentiate:** a downloadable `.pbix` or the sample CSV. Without it, this is one of ten thousand "build a sales dashboard" posts. Even a Gist link moves the needle.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-10-05` — future date. If this is a scheduled draft, fine; if not, it will read as broken. Confirm publishing tooling handles it.
- `description` is a rephrase of the first sentence of the body. Duplicated lead hurts SERP snippet uniqueness. Write a distinct description that names the outcome (e.g., "Build a decision-ready Power BI sales dashboard from a flat CSV: clean data, model a star schema, write YoY measures, and lay out the page.").
- `difficulty: Beginner` is inconsistent with the DAX depth in steps 3–4 (time intelligence, `SUMX` vs `SUM`, variables). Either mark `Intermediate` or explicitly flag which steps a beginner can skip.

**Terminology / code**
- "`Int64.Type` on Quantity prevents accidental decimals" — overstated. It coerces; it doesn't "prevent" anything if the source is dirty. Trim the claim.
- "a text date breaks every time intelligence calculation later" — mostly true but too absolute. It breaks everything that relies on date semantics; some measures just return garbage. Rephrase to "breaks time intelligence and silently produces wrong totals."
- `DimDate` code: `FORMAT([Date], "Q")` returns "1".."4", so `"Q" & FORMAT(...)` gives `Q1`..`Q4` — correct. But `FORMAT([Date], "mmm")` is locale-dependent and the Year Month `"yyyy-mm"` uses numeric month, which will sort correctly only if a sort-by-column is set. You never mention **Sort by column**. Add it: sort `Month` by `Month Number`, sort `Year Month` by the date.
- `Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(DimDate[Date]))` — fine, but you never tell readers the date table must also be related to Sales. Step 2 says "relationships go one-to-many from each dimension to the fact table," which covers it, but a reader scanning Step 3 in isolation will miss it.
- "`CALCULATE` rewrites the filter context" — imprecise. It *modifies* the filter context; "rewrites" implies replacement. Small but a technical editor should catch it.
- "Which returns blank for invalid divisions" — `DIVIDE` returns the alternate result (blank by default) only for *divide-by-zero* and blank denominators. Calling every case "invalid divisions" is loose.
- Step 6 table: "Using `SUM` on a column with blanks instead of `SUMX`" — this is not the cause of totals not matching row sums. `SUM` ignores blanks; it will match row sums. The real cause of mismatched totals is iterating rows in a visual but aggregating differently in the total, or filters applied only at the row level. **This row is wrong** and should be rewritten or cut.
- `Sales[Quantity] * Sales[UnitPrice]` inside `SUMX` — fine, but if `Quantity` or `UnitPrice` can be blank (you filled `UnitCost` but not the others), you get blank propagation. You explicitly fill `UnitCost` in Power Query but not `UnitPrice` or `Quantity`. Inconsistent.

**Internal links — all verified against real slugs list:** ✅
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/dax-variables-best-practices/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/conditional-formatting-charts-power-bi/` ✅
- `/tutorials/power-bi-drill-through/` ✅
- `/tutorials/bookmarks-navigation-power-bi/` ✅
- `/tutorials/dax-basics/` ✅
- `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` ✅
- `/tutorials/power-bi-mom-yoy-dax-template/` ✅
- `/tutorials/power-bi-dashboard-design-principles/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅

No broken links. Good restraint — the draft resists the temptation to link every mention of "DAX."

**Suggested additions you have real slugs for and should use:**
- Step 3 → `/tutorials/dax-calculate-function/` or `/tutorials/calculate-function/` when introducing `CALCULATE`.
- Step 6 → `/tutorials/power-bi-performance-analyzer-guide/` (you mention Performance Analyzer without linking).
- Step 6 → `/tutorials/directquery-vs-import-mode/` for the "DirectQuery instead of Import" row.
- Step 2 → `/tutorials/power-bi-field-parameters/` since you mention field parameters in Step 5 without explaining them.

**Format / structure**
- The table in Step 4 ("Zone | Visual | Fields") mixes prose and data; fine, but the "Top strip" row says "Orders" as a card field without ever defining an Orders measure. Either add `Orders = COUNTROWS(Sales)` or drop it.
- FAQ answers use "Q:" prefix in headings. Standard markdown H3 is sufficient; the prefix is redundant and clutters the TOC.
- No images or video embeds. For a 1k-UV beginner tutorial, at least one annotated screenshot of the finished page is expected. Adding one is the single highest-leverage fix after the retitle.

---

**VERDICT: PUBLISH-AFTER-FIX** — retitle to a long-tail variant, fix the wrong "totals do not match row sums" row, add sort-by-column note, dedupe description from intro, and add 1–2 screenshots before publishing.