# Review: dax-optimization-techniques

# Editorial Review: `dax-optimization-techniques`

## 1. AI-isms

The draft is more disciplined than most, but several patterns still read as machine-generated:

- **"walks through the techniques that consistently move the needle"** — "move the needle" is a LinkedIn cliché. Rewrite: *"covers the techniques that produce the largest measured reductions in query time."*
- **"The classic symptom is..."** — vague opener. Replace with a concrete threshold: *"A typical complaint is a visual that takes 4 seconds to render against a 200,000-row fact table."*
- **"The fix is rarely 'add more memory.' It is restructuring..."** — the negation-then-assertion tic. Collapse: *"The fix is almost always restructuring the calculation so the storage engine does the heavy lifting in a single pass."*
- **"The second version does not just look cleaner."** — "does not just X, it Y" is a strong AI tell. Cut outright: *"The second version materializes the SUMMARIZE result once; the SUMX then iterates it a single time."*
- **"This is the single most common performance mistake in production Power BI models."** — unverifiable superlative. Either cite a source or soften: *"This is one of the most common performance mistakes in production models."*
- **"will melt on a fact table with a million rows"** — colloquial filler. Replace with the mechanism: *"is O(n²) and becomes unusable above roughly 10⁵ fact rows."*
- **"Do not guess."** — imperative throat-clearing. Cut; start directly with *"Open Performance Analyzer..."*
- **Em-dash check:** none abused. Body is clean on this front.
- **Mechanical structure:** Techniques 1–8 with H2s is fine, but numbers 7 and 8 are much shorter and thinner than 1–6 — the list-feel is uneven. Either merge 7 and 8 into a single "Formula engine hygiene" section, or expand each to comparable depth.

## 2. Topic Fit

- **Long-tail rankability:** "dax optimization techniques" is a head term, not long-tail. You are competing directly with SQLBI, Enterprise DNA, and Microsoft Learn. This will not rank without a different angle.
- **Overlap risk:** you already publish `/tutorials/power-bi-dax-optimization/` and `/tutorials/power-bi-performance-optimization/`. Three slugs chasing the same SERP will cannibalize each other. Pick one canonical and 301 the others, or differentiate hard.
- **1k UV/day goal:** unlikely from this slug alone. The query volume for "dax optimization techniques" is real but the top 3 are entrenched.
- **Better angle:** narrow to a symptom-first long-tail that SQLBI has not saturated:
  - `why-is-my-dax-measure-slow-power-bi` (diagnostic intent)
  - `dax-sumx-vs-sum-calculated-column-performance` (single A/B decision)
  - `power-bi-filtr-on-column-vs-boolean-filter-dax` (specific mistake)
  - `dax-server-timings-explained-beginners` (tool walkthrough)
  
  Any of these has clearer intent, less competition, and can internally link up to the broader optimization pillar — which is exactly what this article should become: a pillar, not a post.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-10-02` is in the future. If the site's build renders future-dated posts as unpublished, this will 404. Confirm the CMS handling or change to a past date.
- `author: Mireia` — inconsistent with a first-name-only schema if other posts use full names. Verify.

**Slug / link check (all verified against provided list)**
- `/tutorials/dax-variables-guide/` ✅
- `/tutorials/dax-variables-best-practices/` ✅
- `/tutorials/power-bi-dax-optimization/` ✅ (but see cannibalization note)
- `/tutorials/power-bi-performance-analyzer-guide/` ✅
- `/tutorials/power-bi-performance-optimization/` ✅ (cannibalization)
- `/tutorials/dax-earlier-function/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/dax-rankx-function/` ✅
- **Missing opportunities:** you link to `dax-rankx-function` but not `/tutorials/dax-calculate-function/` or `/tutorials/dax-calculate-function/` (both exist as separate slugs — pick one; publishing two slugs on the same function is itself a bug). Technique 4 is literally about CALCULATE and should link to one of them.
- You discuss time intelligence (`TOTALYTD`, `DATESINPERIOD`) but do not link `/tutorials/dax-time-intelligence-ytd-qtd-mtd/`. Add it.
- No link to `/tutorials/dax-troubleshooting-guide/`, which is the natural sibling. Add under "Measuring the Impact."

**Technical / terminology**
- **"storage engine (VertiPaq)"** — imprecise. VertiPaq is the in-memory *column store*; the storage engine (SE) is the query layer that reads it. In Import mode they are commonly conflated, but in DirectQuery the SE is the source database. Either be precise or note the Import-mode scope.
- **Technique 1 code block:** the "Slow" version is not actually a meaningful slow/fast comparison — the fast version computes the exact same `SUMMARIZE` once and the slow version relies on DAX's own expression caching, which in modern engines often produces near-identical plans. This example risks being wrong. Replace with a case where the same *expensive* expression genuinely appears twice in different contexts, e.g. a `FILTER` over a `SUMMARIZE` recomputed in numerator and denominator.
- **`FILTER` claim:** "Column predicates inside CALCULATE are translated into storage engine queries." — mostly correct, but oversimplified. `CALCULATE` with a boolean predicate on a column of the same table does push down; on a *related* table it goes through the relationship and may or may not. Tighten the wording.
- **`RANKX` example:** `ADDCOLUMNS ( ProductSales, "Rank", RANKX ( ProductSales, [Sales] ) )` — `[Sales]` here refers to the column added by `SUMMARIZE` named `"Sales"`. That is legal but confusing because `[Sales]` normally denotes a measure. Add a one-line note or rename the column to `"ProductSales"`.
- **"Calculated column that references a measure is a mistake"** — technically a calculated column *cannot* reference a measure in the same table in a straightforward way; it can reference measures only via `CALCULATE`/context transition hacks and is generally disallowed or produces misleading results. The sentence as written is ambiguous. Rewrite: *"A calculated column cannot meaningfully reference a measure; context transition at refresh time will either error or produce a per-row value that bears no relation to the measure as used in a visual."*
- **`EARLIER` code comment:** *"Valid: EARLIER references the outer row context created by the FILTER's SUMX"* — `FILTER` does not create a row context; the `SUMX`'s iteration does, and `FILTER` iterates internally. The comment is misleading. Rewrite the comment to name the iterator explicitly.
- **`DIVIDE` claim:** *"`DIVIDE` is faster than `A / B`"* — for scalar arguments this is not reliably true; `DIVIDE` exists primarily to handle divide-by-zero semantics, not as a performance win. Remove the performance framing and keep the semantic one.

**Format / FAQ**
- FAQ questions are good and long-tail friendly. Consider promoting Q3 ("Why is FILTER on a column slower than a column predicate?") into the body as a callout — it is the strongest single nugget.
- Table in "A Checklist" is clean. Consider adding a column for expected speedup so it is skimmable.
- "Related Reading" list is 8 items — trim to 5 highest-signal, or the internal-link juice dissipates.

**Cannibalization (repeat, but important)**
Publishing this alongside `/tutorials/power-bi-dax-optimization/` and `/tutorials/power-bi-performance-optimization/` without a clear differentiation strategy will hurt all three. Decide now: is this the pillar (and the other two become spoke posts linking up), or is this the spoke (and the pillar gets rewritten to link down)?

---

**VERDICT: PUBLISH-AFTER-FIX** — correct the two technically wrong claims (Technique 1 slow/fast example, DIVIDE performance framing), fix the future pubDate, resolve the three-way slug cannibalization, and add the missing internal links to CALCULATE and time-intelligence posts before it goes live.