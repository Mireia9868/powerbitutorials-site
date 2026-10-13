# Review: power-bi-matrix-visual

# Review: `power-bi-matrix-visual`

## 1. AI-isms

The draft is mostly clean — concrete, opinionated, mostly free of throat-clearing. A few flags:

- **Mechanical step headers with empty openers.** "Step 1: Build the row hierarchy before touching the format pane", "Step 2: Keep measures on Values, never in Rows" — the imperatives are good, but Steps 5–8 drift into listicle cadence ("Widen cells and shorten numbers", "Sorting, drill, and expand", "Performance rules", "Accessibility and layout"). Steps 5 and 8 in particular are grab-bags, not decisions. Consider collapsing Step 8 into a short "Layout and accessibility" prose block, or merging into Step 5.
- **"Two constraints worth knowing:"** — textbook AI framing. Rewrite: "Two limits:" or just lead with the limits.
- **"Do two things:"** — same pattern. Drop it; the bullets carry the instruction.
- **"Everything works in both Power BI Desktop and the Service."** — filler sentence that neither adds information nor is verifiable. Cut.
- **"For deeper tuning, review `DAX Optimization Techniques` and the broader model design in `Data Modeling: Star Schema`."** — backticked titles read oddly in prose; also this is a lazy conveyor to the Related Reading list immediately below. Either hyperlink properly (see Errors) or delete the sentence.
- **Em-dashes:** used sparingly and correctly. One questionable case: "Do not use bookmarks for this — it works, but the bookmark panel state will drift as the model changes." The pause reads forced. Try: "Do not use bookmarks for this. They work, but the panel state drifts as the model changes."
- **"Third data dimension"** is a nice framing — keep.

Overall AI-ism level: low. The tone is a working consultant, not ChatGPT.

## 2. Topic Fit

- **Long-tail rankability:** `power-bi-matrix-visual` is a solid, low-competition slug. Head term "Power BI matrix visual" has decent search demand, and "best practices" + "tips" as title qualifiers are fine but generic; consider a sharper title like *"Power BI Matrix Visual: 7 Settings That Fix Slow Reports"* to capture intent around performance, which is where the actual pain is.
- **Goal alignment (1k organic UV/day):** a single matrix tutorial won't get there alone — it needs to be a hub. The internal links do some of this. To push harder, the article should explicitly target the queries that drive matrix traffic: *"Power BI matrix collapsed by default"*, *"Power BI matrix conditional formatting"*, *"Power BI matrix slow"*, *"Power BI matrix subtotal blank"*. Right now the FAQ covers these but the H2s don't — the H2s are "Step 1..Step 8". Rewrite step headers as question-shaped H2s where possible.
- **Better angle suggestion:** the strongest unique claim in this draft is *"the matrix is the most expensive core visual"* and the Step 7 performance table. That could be the lead, with a "why your matrix is slow" framing. It would differentiate from the dozen generic matrix walkthroughs already ranking.

## 3. Errors

### Frontmatter
- All fields valid. `pubDate: 2026-10-13` is in the future relative to a typical `publishedDate` review window — confirm this is intentional (scheduled) and not a typo for 2025.
- `featured: false` + `draft: false` — consistent.
- `category: visualization` and `tags: ["matrix", "visualization"]` — acceptable, though adding `["matrix", "visualization", "performance", "conditional-formatting"]` would help discovery given the content.
- `description` is 158 chars and duplicates the first body sentence verbatim. Rewrite the description so it doesn't echo the opening.

### Terminology / DAX
- `Sales Amount :=` uses `:=` — valid but Power BI's Measure editor and most tutorials use `=`. The `:=` convention is from SSAS/Tabular. Either is correct; be consistent. The rest of the snippet uses `=`, creating a mixed style within a single block. **Fix:** use `=` throughout.
- `SAMEPERIODLASTYEAR ( DimDate[Date] )` — correct, but the article never mentions the requirement of a marked date table. Add a one-line note or this will generate "my YoY is blank" support tickets.
- `ISINSCOPE ( DimProduct[Product] )` — correct usage. The example `Ranks with Blank Total` correctly suppresses the grand total. Good.
- **Step 4 code block has a logic issue:** the measure is named `Ranks with Blank Total`, but the article immediately says *"If you want to remove the total row entirely, turn off Format pane → Totals → Row subtotals"*. The two techniques are presented as alternatives but aren't clearly separated. Minor clarity fix.
- **Step 6 claim:** *"Sorting a matrix applies to the value axis in the Values section."* — this is imprecise. Sorting in a matrix sorts **row headers** by the selected measure's value; the "column headers by measure" behavior does not exist for the column axis. The follow-up sentence contradicts: *"When multiple measures are in Values, sorting by a measure sorts row headers by that measure's values."* Pick one framing.
- **Step 6 drill-through text is mangled:** *"Verify the page filter is set to `Keep all filters`, not `Allow drill through when: Filters are kept` misinterpreted as stripping the page filter."* — this sentence is ungrammatical and the second option doesn't exist as a UI label. Actual options are **Keep all filters** vs **Allow drill through when: Filters are kept / Cross-report drill through is on / The user right-clicks a data point**. Rewrite the sentence entirely.
- **Step 3:** *"Use the same measure for font color only if the background is light."* — the logic is backwards as written; you want dark font on light background, and you'd want the *same measure* only if the measure produces a text color that contrasts with the background it produced. Clarify or drop.
- **Step 7 table:** *"DirectQuery source | Each expansion round-trips to the source | Prefer Import for matrix-heavy report pages"* — accurate but understated. Expand/collapse in DQ can trigger full re-queries; a short note on **"Automatic page refresh"** off would be useful.
- **FAQ Q3:** *"A disconnected table combined with `SELECTEDVALUE` can approximate dynamic columns but breaks the matrix's column grouping."* — accurate and a good caveat.
- Missing term definition: the article never mentions **"stepped layout"** semantics before telling the reader to toggle it. One sentence explaining stepped vs. tabular is warranted.

### Broken / imagined internal links

Cross-referencing against the REAL SLAGS list:

| Link in draft | Status |
|---|---|
| `/tutorials/conditional-formatting-complete-guide/` | ✅ exists |
| `/tutorials/conditional-formatting-based-on-measure/` | ✅ exists |
| `/tutorials/conditional-formatting-charts-power-bi/` | ✅ exists |
| `/tutorials/filter-context-row-context-explained/` | ✅ exists |
| `/tutorials/dax-rankx-function/` | ✅ exists |
| `/tutorials/dax-switch-function/` | ✅ exists |
| `/tutorials/data-modeling-star-schema/` | ✅ exists |
| `/tutorials/dax-optimization-techniques/` | ✅ exists |
| `/tutorials/power-bi-dashboard-design-principles/` | ✅ exists |

All nine Related Reading links are valid.

**However — two inline references are NOT hyperlinked but should be:**
- `DAX Optimization Techniques` in Step 7 body — the slug exists (`/tutorials/dax-optimization-techniques/`), link it.
- `Data Modeling: Star Schema` in Step 7 body — the slug exists (`/tutorials/data-modeling-star-schema/`), link it.

Also flagging **unlinked missed opportunities** given the article's content: it references conditions formatting, totals, drill-through, and date tables without linking to existing slugs such as `/tutorials/power-bi-date-table/`, `/tutorials/copy-conditional-formatting/`, `/tutorials/conditional-formatting-power-bi/`, and `/tutorials/dax-calculate-function/`. Adding 3–4 of these in-context (not just in Related Reading) would strengthen topical authority for the site.

### FAQ / format
- Four Q&As, reasonable length, no schema issues. The `### Q:` prefix pattern is consistent.
- Q2's advice — *"Do not use bookmarks for this"* — is opinionated but defensible; keep, but soften as noted above.
- No FAQPage schema visible; if the site generates it from the FAQ section, confirm the `### Q:` headers parse correctly. If it requires `### Question` / `### Answer`, this will silently fail. Verify.

## Summary of required fixes

1. Fix `:=` → `=` inconsistency in the DAX block.
2. Rewrite the mangled drill-through sentence in Step 6.
3. Fix the sorting claim in Step 6 (contradicts itself).
4. Hyperlink the two backticked slugs in Step 7 body, or delete the sentences.
5. Rewrite the frontmatter `description` so it doesn't duplicate the body's first sentence.
6. Add a one-line note about the marked date table before the YoY example.
7. Optional but recommended: sharpen Step headers into question-shaped H2s for SEO.

VERDICT: PUBLISH-AFTER-FIX