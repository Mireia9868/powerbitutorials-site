# Review: power-query-query-folding

# Review: `power-query-query-folding`

## 1. AI-isms

**Vague opener in the lede.** The first sentence is a definition, which is fine, but it's the exact phrasing ChatGPT would produce ("Query folding is the process where..."). It restates the title and the description with no hook. Consider opening with the symptom instead, e.g.: *"Your query refreshes fine on 50k rows in dev and times out at 8M in prod. Nine times out of ten, it's query folding — or the lack of it."* Then define it.

**Mechanical transition filler.**
- *"The practical effect is enormous."* — empty intensifier. Cut or replace with the concrete consequence (already in the next sentence).
- *"This is the single most important rule to remember."* — writer telling reader what matters instead of showing. The rule is clear; trust it.
- *"Why It Matters More Than You Think"* — classic ChatGPT section header. Try "What Actually Breaks in Production" or "The Dev-vs-Prod Failure Mode."
- *"The pattern is that row-and-column shaping folds; per-row computation and order-dependent logic generally do not."* — good summary, keep, but drop the throat-clearing "The pattern is that."
- *"Now move a single non-folding step to the top."* — actually a good teaching line, keep.

**Hedging adverbs.** "generally fold," "usually do not fold," "historically a break point," "in some narrow scenarios," "in some configurations." Some hedging is honest (folding is connector-dependent), but the article alternately sounds vague and confident. Either commit ("`Table.Distinct` does not fold on SQL Server, Oracle, or PostgreSQL") or drop the claim.

**Em-dash abuse.** You have a lot of them — `— no equivalent server-side concept`, `— explicitly forces materialization`, `— historically a break point`. Three in one bullet list is a tell. Convert most to colons or parens.

**"The single biggest …" / "enormous" / "trivial."** Recurring superlatives. Fine once; picking one per section is enough.

**No fix needed:** the FAQ, the code examples, and the "Practical Habits" section read human.

## 2. Topic fit

**Long-tail rankable?** Yes — `query folding`, `power query query folding`, `power query folding breaks`, `view native query greyed out`, and `does power query fold table.addindexcolumn` are all real query patterns with healthy volume. The slug is clean and matches the head term.

**Does it serve the 1k organic UV/day goal?** Marginally. Query folding is a mid-volume topic; the slug will not compete with Microsoft Learn or Enterprise DNA on the head term, but it *will* rank for the long-tail break-point queries if the article is structured to answer them. Right now the article is a survey; it does not have a strong "answer this specific question" section. To hit volume:

- Add an H2 like **"Which Power Query steps break folding? (full list)"** with a single scannable table called out early. That's the search intent behind most of the tail.
- Add an H2 like **"View Native Query is greyed out — what now?"** That is a real query and the current article buries the answer in two sentences.
- Consider a sibling article idea: **"DirectQuery and Query Folding: What Folds, What Doesn't"** — the last FAQ half-answers this and would be a stronger standalone targeting `directquery query folding`.

**Better angle?** Two candidates:
1. **"Query Folding Break Points — the 12 Transformations That Kill Performance"** — narrower, more rankable, more useful.
2. **"Query Folding vs Table.Buffer: When Buffering Helps and When It Kills Your Refresh"** — Tabular Editor / community searches on this are fragmented and the current article only gives it one bullet.

If you keep the current slug, restructure to lead with the diagnostic ("how to find your fold break") rather than the definition. The current opening three sections are groundwork that most searchers already have.

## 3. Errors

**Frontmatter.**
- `pubDate: 2026-10-02` — future date. If the site renders as-is, the article will be hidden or `draft` will be forced. Confirm this is intentional (scheduled publishing) and not a typo for 2025.
- `description:` is the definition again, not a hook. Same problem as the lede. Rewrite to state the payoff.
- `tags: ["performance", "query folding"]` — fine, but consider adding `"power query"`.
- No `canonical` or `og:image` fields — check whether that's the site convention.

**Terminology / technical accuracy.**
- *"Query folding is the process where Power Query translates the steps you build in the editor into a single query statement"* — `single` is misleading. Folder can emit multiple statements, or one statement per branch in a merge/append. Rewrite to "a native query statement (or set of statements)."
- *"Possibly folded — Power Query cannot determine folding until runtime"* — this is not a standard state shown in the UI. The Applied Steps pane shows a folding indicator: **folded**, **not folded**, or **unsupported**. "Possibly folded" is not a Microsoft-documented state. Cut it or reword to "Unknown / indicator absent."
- *"Right-click any step ... If the context menu shows View Native Query, that step folds."* — correctly nuanced, but note that **View Native Query can be enabled by a user setting even when the step does not fold** (File > Options > Global > "Always allow viewing of native query"). The article should mention this caveat, otherwise readers will be misled.
- *"Open Tools > Diagnostics in Power Query Desktop"* — Power Query Desktop does not have a Tools > Diagnostics menu in standard Power BI Desktop. The correct tool is **Power Query Diagnostics** (a separate feature: Tools tab in Power BI Desktop's Power Query editor has "Start Diagnostics" / "Diagnose Step"). Fix or remove.
- *"`Table.TransformColumnTypes` (Basic type changes)" listed as folding* — true, but `Table.TransformColumnTypes` with `Int64.Type` on a source column typed as `varchar` or `decimal` will often not fold because the type is not representable. The article touches this later ("Declare types after filtering") but the bullet is too flat.
- *"`Table.AddIndexColumn` — no equivalent server-side concept for arbitrary ordering"* — SQL has `ROW_NUMBER() OVER (ORDER BY ...)`, so there *is* an equivalent, but Power Query does not know the ordering to pass in. Reword to: *"no deterministic ordering is provided, so Power Query cannot emit a `ROW_NUMBER() OVER (...)`."* As written it's technically wrong.
- *"`Table.Distinct` on many connectors — historically a break point"* — actually `Table.Distinct` folds on most modern relational connectors via `SELECT DISTINCT`. The claim is backwards. Verify and correct.
- *"In DirectQuery mode, folding is not optional: only folded operations can be sent, and non-folding steps are either flagged as unsupported or handled with a slower fallback."* — mostly correct, but the "slower fallback" framing is off. DirectQuery does not fall back to local processing; unsupported steps either error or trigger a warning in the editor. Fix.
- *"Load the raw file into your data warehouse, an Azure SQL Database, or a Power BI dataflow"* — dataflows use the same Power Query engine; folding into a dataflow only helps if the dataflow's *source* is foldable. As written, this is a circular suggestion. Reword.

**Code blocks.**
- `powerquery` language tag — check the site's highlighter supports it (Prism/Shiki usually use `powerquery` or `m`). If not, switch to `m`.
- The "single statement roughly like this" is accurate.
- `Sql.Database("myserver.database.windows.net", "SalesDW")` is a valid pattern but incomplete — a real example typically uses `Sql.Database(server, database, [Query=...])` or includes `[HierarchicalNavigation=true]`. Fine as a teaching example, but flag in a note that it's abbreviated.
- Comments in the M code use `//` — valid M.

**FAQ.**
- Q1 and Q5 duplicate content from the body but packaged for SERP impression. Good.
- Q2 ("Can I force folding...") — the answer is correct but should mention that `Value.NativeQuery` lets you write raw SQL, which *is* a way to control the sent statement (though not "force folding" in the strict sense). Worth a one-liner link.
- Q3 conflates two things: a step not folding vs. folding stopping earlier. The answer is on the right track but the last sentence ("Inspect upward until you find a step whose native query is viewable") contradicts the caveat that View Native Query can be enabled globally. Fix consistency.

**Internal links.** All eight links in "Related Reading" resolve against the real slugs list:
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/power-bi-performance-analyzer-guide/` ✅
- `/tutorials/power-bi-performance-optimization/` ✅
- `/tutorials/power-bi-dax-optimization/` ✅
- `/tutorials/calculated-tables-what-if-parameters/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅

No broken links. However, there are **missed opportunities**: `/tutorials/directquery-vs-import-mode/` is linked once in Related Reading but should be linked *inline* in the DirectQuery paragraphs, and `/tutorials/power-bi-performance-analyzer-guide/` is linked but never referenced in the "Diagnosing Production Issues" section where it belongs. Add both inline.

**Format.**
- The heading `## What Query Folding Actually Is` — "Actually" is an AI-tell. Cut it.
- The folding state table has a row (`Possibly folded`) that should not exist. Remove.
- The article is long for the topic without a TL;DR. Consider adding a two-sentence summary callout at the top.

---

**Top three fixes before publishing:**
1. Correct the four technical errors (View Native Query global setting, Tools > Diagnostics, `Table.Distinct` folding, `Table.AddIndexColumn` SQL equivalent).
2. Restructure to lead with the diagnostic, not the definition.
3. Add an inline link to `/tutorials/directquery-vs-import-mode/` and `/tutorials/power-bi-performance-analyzer-guide/` in the body.

**VERDICT: PUBLISH-AFTER-FIX**