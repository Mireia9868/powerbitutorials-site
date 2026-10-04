# Review: star-schema-power-bi

# Review: `star-schema-power-bi`

## 1. AI-isms

The draft is mostly clean and concrete — far better than typical ChatGPT output. But a handful of tells remain:

- **"What a Star Schema Actually Is"** — the "Actually" is an AI-ism (faux-authoritative header). Drop it: **"What a Star Schema Is"**.
- **"The shape looks like a star because…"** — the etymological explainer is filler for an Intermediate audience. Cut or shorten to one clause.
- **"In Power BI, this shape matters more than it does in most relational databases."** — vague comparative claim with no evidence. Either back it or delete.
- **"There is almost always a cleaner modeling fix."** — soft, hand-wavy. Replace with a pointer, e.g., *"use a bridge table or a `TREATAS` pattern"* and link.
- **"from there, measure optimization is the next lever."** — mechanical transition ("next lever"). Cut or convert to a link to the DAX optimization post.
- **"A star schema gives the engine a clean filter graph"** — this sentence restates the intro almost verbatim. Redundant.
- **Em-dash / colon cadence** — fine here, not abused. No action.
- **"Three Mistakes That Break the Star"** — header promises three, body delivers three, but the third ("Calculated columns that should be measures") is a DAX modeling issue, not a star-schema one. Either rename to **"Three Modeling Mistakes That Break the Star"** or swap for a genuine star-schema anti-pattern (e.g., a degenerate dimension promoted to its own table, or dimensions connected to a fact that doesn't share grain).

## 2. Topic Fit

**Rankability:** Weak-to-moderate as a long-tail target. "Star schema Power BI" is a broad, high-competition head term dominated by Microsoft Learn, SQLBI, and Enterprise DNA. The draft doesn't pick a long-tail angle — it's a general primer, and it overlaps heavily with `/tutorials/data-modeling-star-schema/`, which appears to be the canonical star-schema page on this site.

**Problem:** You now have two pages competing for the same query. That's cannibalization, and the older/canonical one will usually lose to the newer or vice versa, spreading authority across both.

**Against the "1k organic UV/day" goal:** A generic primer won't get there. The site already has 40+ tutorials; the win is in angles the big players haven't covered.

**Better angles (pick one and own it):**

- **"Star Schema vs Snowflake Schema in Power BI: When the Extra Relationship Is Worth It"** — concrete decision framework, real performance data.
- **"How to Convert a Flat Excel Export into a Star Schema in Power Query"** — step-by-step with a downloadable PBIX, targets a very specific search behavior.
- **"Bridge Tables in Power BI: The Proper Alternative to Many-to-Many Relationships"** — currently only a paragraph here; deserves its own post.
- **"Debugging a Broken Star Schema: Why Your Totals Are Wrong"** — troubleshooting intent, high conversion to email signup.

If you keep this slug, **differentiate it** with benchmarks (VertiPaq compression, query duration before/after), a downloadable PBIX, and a "when *not* to use a star schema" section. Otherwise, redirect to `/tutorials/data-modeling-star-schema/` and write one of the above instead.

## 3. Errors

**Frontmatter:**
- Structure looks valid: title, description, pubDate, category, tags, difficulty, author, featured, draft. ✅
- `pubDate: 2026-10-04` is in the **future** relative to typical current dates. If this repo builds at publish time, it will be hidden until that date. Verify this is intentional (queued post) — otherwise a typo for 2025.
- `author: Mireia` — inconsistent with typical byline format (first name only). Confirm this is the site convention.
- `description` is a full sentence with the same content as the opening paragraph — OK, but consider tightening to ~155 chars for SERP.

**Content / code:**

- **`CALENDAR ( MinDate, MaxDate )` with hardcoded `DATE(2021,1,1)` / `DATE(2025,12,31)`** — this is the exact thing the following sentence then tells the reader to fix. Lead with the dynamic version (`CALENDAR(MIN(FactSales[OrderDate]), MAX(FactSales[OrderDate]))`) and note the limitation (a date dimension should extend past the fact range to support time-intelligence edge cases). The current ordering teaches the anti-pattern first.
- **`FORMAT([Date],"YYYY-MM")`** — `YYYY` in DAX format strings is not ISO-strict and can be confused with `yyyy` (week-year). Use `"yyyy-MM"` (lowercase) to be safe, and note the distinction. Same for `"Q"` — that's a valid DAX quarter literal, but worth a one-line note.
- **`"Day of Week", FORMAT([Date],"dddd")`** — this produces an alphabetically-sorted day name, which will sort incorrectly in visuals. You need a `"Day of Week Number", WEEKDAY([Date],2)` sort column. The article calls out the import of sort columns elsewhere ("sort key" in the calculated-columns section) but omits it here — inconsistent.
- **`Table.Distinct(KeepColumns, {"ProductID"})`** — the second argument limits distinctness to the key, but the *other* columns retained may differ arbitrarily per key if the source has inconsistencies. Add a `Table.Group` + aggregate step, or note the assumption that ProductID → attributes is 1:1 in source.
- **`Table.SelectColumns(Source, {...})` then `Table.Distinct(..., {"ProductID"})`** — subtly: if the source has a ProductID with two names, `Table.Distinct` on `{"ProductID"}` keeps an arbitrary one. Call this out or use `Table.Group`.
- **`LineAmount` materialized in Power Query "reduces model size and memory VertiPaq must allocate"** — half true. A Power Query–materialized column **is** stored in VertiPaq; a DAX calculated column **also** is. The real win of doing it upstream is that Power Query can fold to source for DirectQuery and it's a simpler pipeline. The stated reason is misleading. Reword.
- **"Data types on both sides match exactly. An Int64 key joined to a text key silently fails."** — Power BI doesn't silently fail; it typically won't let you create the relationship, or coerces with warnings. "Silently fails" is incorrect. Reword to "will not form a valid relationship / will trigger a coercion warning."
- **`Sales by Category` measure** — this is a broken example. `CALCULATE([Total Sales], ALL(DimProduct), VALUES(DimProduct[Category]))` inside a measure is not how you'd write a working "Sales by Category"; `ALL(DimProduct)` removes the filter you just tried to reapply with `VALUES`. As written it will return all-products sales, or error depending on context. Replace with either a plain measure (`Total Sales` on a visual with Category on rows) or a genuinely meaningful example like a "% of parent category" pattern.
- **"Many-to-many relationships without a bridge."** — the phrasing is ambiguous. Should be: "Using many-to-many where a bridge is needed." The current wording reads as "never use M2M," which is too broad.
- **"A model with multiple fact tables sharing conformed dimensions is called a galaxy schema or a fact constellation."** — Both terms are accepted; fine. Add the note that Power BI handles this natively with conformed dimensions.
- **`USERELATIONSHIP` mention** — fine, but the link target `/tutorials/dax-earlier-function/` isn't used and `/tutorials/calculate-function/` is smaller than `/tutorials/dax-calculate-function/` (both exist in the slug list — **you have two CALCULATE tutorials**, a pre-existing problem).

**Internal links — all verified against the real slug list:**
- `/tutorials/data-modeling-star-schema/` ✅ (but see cannibalization note above)
- `/tutorials/bidirectional-filtering-guide/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/calculate-function/` ✅ (exists, but consider whether this or `dax-calculate-function` is canonical)
- `/tutorials/dax-basics/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/power-bi-performance-analyzer-guide/` ✅

No broken links. But the "Related Reading" list is generic. Given the slug list, you're missing obvious in-body links to:
- `/tutorials/calculated-tables-what-if-parameters/` (in the date-table section)
- `/tutorials/dax-variables-best-practices/` or `/tutorials/dax-variables-guide/` (worth a callout in the measure validation step)
- `/tutorials/dax-optimization-techniques/` or `/tutorials/power-bi-dax-optimization/` (in the optimization section)
- `/tutorials/power-bi-common-mistakes-beginners/` (in the "Three Mistakes" section)

**FAQ:**
- Well-formed, five Q's, natural voice. ✅
- Q3 (`TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATEADD`) is where you should link `/tutorials/dax-time-intelligence-ytd-qtd-mtd/`. Currently unlinked.
- Q5 partially duplicates the Step 5 bullet on bidirectional filters. Trim one.

**Format:**
- Section H2s are consistent, but "Three Mistakes That Break the Star" is anomalously short/narrative compared to the numbered steps — stylistic mismatch, minor.
- No code fence language on the DAX block `DimDate = ...` (missing ```dax). Actually it's present — ✅.
- Power Query fences use ```powerquery — non-standard; Power BI community usually uses ```powerquery or ```m. Confirm your site highlighter supports `powerquery` (Prism/Shiki may not).

---

**VERDICT: PUBLISH-AFTER-FIX** — the draft is competent but the `Sales by Category` measure is broken, the sort-column omission contradicts the article's own advice, the hardcoded date range teaches the anti-pattern the next line warns against, and the topic cannibalizes `/tutorials/data-modeling-star-schema/`. Fix code, resolve cannibalization (differentiate or consolidate), trim AI-isms, then publish.