# Review: power-query-merge-queries

# Editorial Review: `power-query-merge-queries`

## 1. AI-isms

The draft is mostly clean, but a few tics stand out:

- **Opener is fine but the "familiar friend" framing is soft.** "the closest thing Excel users get to a familiar friend" is a slightly overwrought anthropomorphism. Rewrite: *"Merging queries in Power Query is the closest equivalent to Excel's VLOOKUP."*
- **"That shift is the whole reason merges belong in Power Query rather than in the data model as a calculated column."** — "the whole reason" is filler emphasis. Rewrite: *"That is why merges belong in Power Query rather than as a calculated column in the model."*
- **"Power Query does not shout at you; it silently returns a column full of `null`."** — the "does not shout at you" personification is a ChatGPT tell. Rewrite: *"Power Query returns no error; the result is simply a column of `null`."*
- **"and it is in Power Query's favour."** — throat-clearing aside. Cut or fold into the prior sentence.
- **"the distinction between merge and append trips up as many beginners as join kinds do."** — vague comparative with no source. Either drop or make concrete (*"is covered in [Merge vs Append Queries]"*).
- **"That list is almost always a data quality problem worth fixing upstream rather than a merge you should patch after the fact."** — hedge stacking ("almost always... rather than... after the fact"). Tighten: *"Treat the result as a data quality issue to fix upstream, not as a merge to patch."*
- **Em-dash / semicolon density is moderate** — acceptable here, no abuse.
- **FAQ answers have a mild "Yes./No." lead-in pattern.** It reads fine for FAQ schema, but two of the five start with a one-word answer. Vary: "Row counts grow when…", "Almost always a data type mismatch…" etc.

Nothing here rises to REWRITE on style alone; these are line edits.

## 2. Topic Fit

- **Slug and title**: `power-query-merge-queries` with the parenthetical "(VLOOKUP Equivalent)" is a strong long-tail play. "Power Query merge queries VLOOKUP" is a real query pattern with low competition on tutorial sites.
- **Goal alignment (1k organic UV/day)**: This is a mid-volume, evergreen concept that feeds the whole Power Query cluster. It is not a single-page 1k/day driver on its own, but as a hub it will pull its weight if it ranks top-5. The VLOOKUP angle is the differentiator — lean harder on it in the intro and H2s.
- **Better angle to consider**: The current draft hedges between "tutorial" and "reference." Consider retitling the H1 to *"Merge Queries in Power Query: The VLOOKUP Replacement Explained"* and adding an H2 like *"When to stop using VLOOKUP and switch to a merge."* Also, a short section on **fuzzy merge** (`JoinKind` + fuzzy options in the UI) is a high-intent long-tail ("power query fuzzy match vlookup") currently missing — worth adding if you want incremental rankability.
- **Internal link play**: You already link the natural neighbours. Adding a link to `/tutorials/calculated-tables-what-if-parameters/` or `/tutorials/dax-variables-guide/` would be off-topic — skip. The current set is fine.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-10-12` is in the future. If this is intentional scheduling, fine; if not, it will render as "scheduled" depending on the site. Verify.
- `difficulty: Beginner` is declared, but the article covers `Table.NestedJoin`, `Table.ExpandTableColumn`, `Table.Buffer`, case sensitivity, and folding. That is **Intermediate** at minimum. Either downgrade the content depth for the intro sections or bump the label.
- `featured: false` — fine.
- Missing `updatedDate` if your schema supports it; useful for evergreen content.
- Description is 102 chars, ends without a period, and mixes a colon into the sentence in a way that reads like a headline fragment. Suggested: *"Merging queries in Power Query is the closest Power BI equivalent to Excel's VLOOKUP. Here is how to do it correctly."* (~120 chars, fits the 150–160 window if you extend slightly.)

**Code**
- The duplicate-check M snippet: `Table.Group(Typed, {"CustomerID"}, {{"Rows", each Table.RowCount(_), Int64.Type}})` — correct. But the comment says "before merging" while the code re-declares `Source` from `Excel.CurrentWorkbook`. Fine, but a reader running this against an already-loaded query should know to swap the `Source` line. Add an inline comment.
- The `Table.AddColumn` conditional: `else 0, type number` — valid M, but the `type number` after the comma needs to be on the column-add signature `Table.AddColumn(Source, "DiscountRate", each ..., type number)`. As written it is syntactically correct. ✅
- `Table.NestedJoin(Source, {"CustomerID"}, Customers, {"CustomerID"}, "Customers", JoinKind.LeftOuter)` — valid, but `Customers` must be the in-scope query name. Confirm the preceding step defines or references it; in the snippet it appears as a bare identifier with no `let` binding. Add `Customers = #"Customers"` or note the assumption.
- **Case sensitivity claim**: *"Note the comparison is case-sensitive. 'acme' and 'ACME' will not match."* This is **not universally true**. Power Query's merge comparison depends on the underlying connector and locale. For Excel/CSV sources, comparisons are typically case-insensitive unless the collation says otherwise; for some SQL sources, it depends on the database collation. The claim as stated will be wrong for a meaningful share of readers. **Fix**: soften to *"Comparison case sensitivity depends on the data source and its collation. If you see missed matches, run Capitalize Each Word or lowercase both keys before merging."*
- `Table.Buffer` advice: *"Sort or buffer the right table when it is small and reused."* Buffering a small table is usually a **pessimisation** in Power Query — the engine handles small-table lookups efficiently without forcing a full materialisation and it can block query folding. This advice is directionally backwards for most scenarios. Recommended rewrite: *"`Table.Buffer` forces a table into memory. It is occasionally useful when a table is reused across many steps, but it commonly hurts performance by blocking folding — benchmark before adding it."*
- `null` vs `""` claim: *"an empty string `""` breaks numeric aggregation."* True in DAX, but the phrasing implies `null` is always preferable in Power Query too. In practice, if the destination is a text field, `""` and `null` behave the same in most visuals. The DAX point is real; the framing conflates the two engines. Minor, but tighten.

**Internal links** — all eight slugs verified against the provided list:
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/measure-vs-calculated-column/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/dax-earlier-function/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅
- `/tutorials/power-bi-excel-integration/` ✅

All resolve. The `dax-earlier-function` link is the weakest topical fit — consider swapping for `/tutorials/dax-basics/` or `/tutorials/dax-calculate-function/` (both exist) if the goal is topical adjacency.

**FAQ / format**
- Five Q&As; good for FAQ schema. Each answer is 2–4 sentences — acceptable.
- Question 3 ("Is merging the same as creating a relationship…") duplicates the body section "Merge vs. Relationship." FAQ duplication of body content is fine for schema, but trim the body redundancy or the FAQ one, not both.
- Question 5 answer mentions "query folding" without a link. Add an internal link if a folding article exists in the cluster (none in the provided list — either drop the mention or leave as a plain term).
- Table in "What a Merge Actually Does" uses `null` inside backticks but the rest of the article uses plain `null` inconsistently — pick one convention.
- No `## Conclusion` or call-to-action. For a tutorial, end with a one-line "Next step" or "Try this" prompt linking to `/tutorials/merge-vs-append-queries/`.

**Terminology**
- "left table" / "right table" is correct and consistent. ✅
- "join kind" vs "join type" — consistent. ✅
- "Left Anti" / "Left Outer" casing is consistent. ✅
- "VertiPaq engine" — correct, but introductory readers may not know the term. One clause of context would help or cut it.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the case-sensitivity claim, the `Table.Buffer` advice, the difficulty label, and the future pubDate; then ship.