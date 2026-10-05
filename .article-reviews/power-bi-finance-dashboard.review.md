# Review: power-bi-finance-dashboard

# Review: `power-bi-finance-dashboard`

## 1. AI-isms

The prose is comparatively clean — no "In today's fast-paced world" openers, no "Let's dive in," no "delve." But several tics remain:

- **Em-dash / colon cadence is uniform.** Nearly every paragraph opens with a short declarative sentence, then a colon or a dash, then an explanation. Examples: *"Finance reporting has a shape that generic dashboards ignore."* / *"Two rules matter here:"* / *"Finance readers scan for exceptions. Formatting should encode one meaning only."* / *"Executives will ask 'why is marketing overspent in March.' Give them the answer in two clicks."* The metronome is the giveaway. Vary sentence length; merge one or two of these into a longer sentence, or split another into fragments.

- **"Two rules matter here" / "Three habits keep a finance report responsive"** — the filler-count construction ("N things matter") is a ChatGPT tell. Rewrite as *"Keep actuals and budget as separate fact tables."* then the second rule as its own sentence.

- **"Everything else is built step by step."** — padding. Cut. Same for *"You should already be comfortable with basic measures and relationships."* which is fine but duplicated by the earlier framing; pick one.

- **"The constraint is cognitive, not technical."** — plausible-sounding but empty. Either cite why (F-pattern scanning, Miller's 7±2) or drop.

- **"matters when the same expression appears more than once"** in Step 2 — *"appears more than once"* is vague; say *"when you reference [Total Revenue] twice."*

- **"Roughly ten to twelve"** in the last FAQ — pick a number or say *"around a dozen."* The hedged range reads as a model avoiding commitment.

- **Section headings are mechanical** ("Step 1:", "Step 2:", ...). Acceptable for a tutorial, but the ordinal steps mean any future reordering breaks the headers. Consider "Model the data first," "Base measures," "Variance," etc.

None of these are fatal. The article reads better than most AI-assisted drafts.

## 2. Topic Fit

**Rankable?** Yes — "finance dashboard Power BI" / "Power BI P&L dashboard" are real long-tail queries with commercial intent and low competition from the big SEO players. The article is *specific enough to win*: budget vs actual, fiscal year, GL sign convention, drill-through to transactions. Those are exactly the search modifiers finance analysts append.

**Does it serve the 1k UV/day goal?** Marginal on its own. It's a "one big tutorial" play, not a cluster. To push traffic you want companion pieces it can link *out to* and *receive links from*:

- **"Budget vs actual in Power BI"** — extract Step 3 into its own article. This is the highest-volume sub-query.
- **"Fiscal year in Power BI"** — extract the July fiscal year FAQ. Real search volume.
- **"GL sign convention in Power BI"** — niche, but a hook piece for finance audiences.
- **"Drill-through to transaction detail"** — you already have `/tutorials/power-bi-drill-through/`, so extend it rather than create a new one.

**Better angle?** The current framing ("Build a Finance Dashboard") competes head-on with generic dashboard tutorials. A stronger wedge: **"P&L dashboard in Power BI from a GL export"** — earns the finance-specific long-tail and differentiates from the design-heavy "dashboard" SERP. Consider retitling.

## 3. Errors

### Frontmatter
- `pubDate: 2026-10-05` is in the **future**. Either the site predates this review or the date is wrong. Set to actual publish date or remove.
- `category: visualization` — fine, but a finance dashboard article arguably belongs under `analytics` or `modeling` depending on your taxonomy. Cross-check against sibling articles.
- `author: Mireia` — no last name; consistent with other posts? Verify.

### Code
- `[Total Amount]` is referenced in Step 2 (`Total Revenue`, `Total Cost`) but **never defined**. This is a real bug for a reader following along. Add a `Total Amount = SUM(FactGL[Amount])` measure in Step 2, or move the definition earlier.
- `Gross Margin` returns a *ratio* (0.42), not a percentage. Fine, but the KPI strip calls it "Gross Margin %" — make sure the card formats it as a percentage; note this in Step 5.
- `Budget Status` uses `SWITCH(TRUE(), ...)`. `TRUE()` is correct but the more common idiom is `SWITCH(TRUE, ...)`. Both work; leave as-is but be consistent if you use SWITCH later.
- Sign convention paragraph is good, but the `IN` operator note — *"optimizes the same way"* — is a claim. Either cite or soften to *"generally compiles to the same query plan."*
- `TOTALYTD([Total Revenue], DimDate[Date], "06/30")` — **the third argument format is locale-dependent.** In en-US it's `"06/30"`; in en-GB or with different locale settings it's `"30/06"`. This will bite readers. Add a one-line warning.
- `SAMEPERIODLASTYEAR` is fine but `DATEADD(DimDate[Date], -1, YEAR)` is the more commonly recommended form in modern Power BI. Not wrong — just be aware you may get comments.
- `FactGL`, `FactBudget`, `DimAccount` casing — `FactGL` uses caps, `FactBudget` camel. Inconsistent. Pick one convention (e.g., `FactGL`, `FactBudget`, `DimAccount` — fine; or `Fact_GL`).

### Internal links — all verified against the real slug list
Every link in **Related Reading** resolves:
- `/tutorials/power-bi-dashboard-design-principles/` ✓
- `/tutorials/data-modeling-star-schema/` ✓
- `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` ✓
- `/tutorials/dax-calculate-function/` ✓
- `/tutorials/power-bi-mom-yoy-dax-template/` ✓
- `/tutorials/conditional-formatting-based-on-measure/` ✓
- `/tutorials/power-bi-drill-through/` ✓
- `/tutorials/dax-variables-best-practices/` ✓

**Missed opportunities for contextual internal links** (the article is link-starved mid-body — only the footer is linked):
- Step 7 drill-through paragraph → link `/tutorials/power-bi-drill-through/` inline.
- Step 6 conditional formatting → link `/tutorials/conditional-formatting-based-on-measure/` inline.
- Step 8 performance → link `/tutorials/power-bi-performance-analyzer/` and `/tutorials/directquery-vs-import-mode/` on the "weigh the trade-off" sentence. `directquery-vs-import-mode` is in your slug list and is *exactly* the right link there — currently unlinked.
- Step 4 time intelligence debug note → link `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` inline.
- Step 2 variables paragraph → link `/tutorials/dax-variables-guide/` or `/tutorials/dax-variables-best-practices/` inline.

### FAQ / format
- Five FAQs, all substantive. Good.
- No `### Q:` numbering inconsistency — clean.
- Consider adding a FAQ for *"Import vs DirectQuery for finance data"* — that's a real search and you already reference it in Step 8. Turns a passing mention into a rankable Q&A.

### Terminology
- "FactGL" — the industry term is usually `FactGL` or `Fact_GeneralLedger`. Fine.
- "AccountType" filter values `"Revenue"`, `"COGS"`, `"OpEx"` — make sure these match whatever an actual GL chart-of-accounts taxonomy looks like. A reader on SAP or NetSuite will map this to their own.
- "treemap" kept lowercase mid-sentence — fine, but Power BI's visual is officially "Treemap" in the ribbon.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the future `pubDate`, define `[Total Amount]`, add the locale warning on `TOTALYTD`, and insert the 5 missed inline internal links (especially `/tutorials/directquery-vs-import-mode/` in Step 8). Everything else is polish.