# Review: power-query-append-queries

# Review: `power-query-append-queries`

## 1. AI-isms

The draft is cleaner than most, but a few tells remain:

- **Bulleted "three situations call for append" / "prerequisite is..." blocks.** These read like a chatbot's "here are the key points" scaffold. The content is fine; the framing is the tell. Fold into prose: "You'll need append when monthly, quarterly, or regional files share a layout. The only prerequisite is aligned column names — Power Query matches by name, not position."
- **"Three situations call for append:" followed by three near-identical bullets.** The second bullet ("Multiple regions, departments, or entities sending the same report layout") is the same idea as the first with different nouns. Cut one or merge.
- **"In practice you want consistent types."** Weasel phrase. Say it directly: "Set the same type on the same column in every source query."
- **"That is expected and fine, but document it."** Generic advice padding. Either say *how* to document it or drop the clause.
- **"The safer pattern is to type each source, then let the append inherit the common type."** "Safer" is hedgy. Say "Type each source first; the append inherits the common type, which avoids a single downstream error step masking the culprit."
- **"because getting this backwards creates a rectangular mess that no DAX measure can repair cleanly."** Purple. Trim to "…because swapping them produces a wide table no measure can clean up."
- **Over-signposting:** "Step 1 / Step 2 / Step 3 / Step 4 / Step 5" plus a "Verifying the Append" section plus "Common Problems" plus "Append vs Merge, in One Line" plus six FAQ items. Structure is doing too much work; the reader loses the thread. Consider merging Step 4 into Step 3 (both are about column alignment).
- **Em-dash use is fine** — actually restrained. No complaint there.
- **"is the function underneath the button"** — slightly cute. "Table.Combine is what the UI button calls."
- **"a rectangular mess" / "you actually want"** — two instances of filler emphasis in the closing paragraph.

## 2. Topic Fit

- **Long-tail rankable?** Yes. "power query append queries" / "append vs merge power query" are real search clusters. The article handles both. The FAQ block targets plausible queries ("append more than two queries at once", "append files from a folder").
- **Serves the 1k UV/day goal?** Borderline. This is a **beginner reference page**, not a problem-driven one. High-volume Power Query queries tend to be specific errors ("append queries created extra columns", "append queries null values") rather than the concept. To push toward 1k/day, the title/H1 should chase the *problem*, not the concept:
  - Better angle: **"Power Query Append Queries: Fix Null Columns and Mismatched Headers"** — the mismatch/nulls problem is the actual long-tail with search demand.
  - Second-best angle: **"Append vs Merge in Power Query (with Examples)"** — this is a distinct, high-intent query and currently the article only addresses it in one closing section. It could be the whole article.
- **Gap worth noting:** No screenshots or visual for the Append dialog. For a beginner Power Query tutorial, the UI is the content. This will underperform without at least 3–4 annotated screenshots.

## 3. Errors

**Frontmatter**
- `description` duplicates the first paragraph of the body almost verbatim. Rewrite the description to be a distinct summary (and check length — it's long for a meta description; consider trimming to ~155 chars).
- `pubDate: 2026-10-12` is in the future. If this is intentional (scheduled), fine; if not, fix.
- `author: Mireia` — no issue if that's the convention, just flagging.
- `difficulty: Beginner` is inconsistent with the content including `Folder.Files` + `Table.Combine` custom function. Either downgrade the advanced sections or bump to Beginner–Intermediate.

**Code**
- Step 1 CSV snippet: `Csv.Document(File.Contents(...))` with `Columns=4` is OK, but `QuoteStyle=QuoteStyle.Csv` requires the correct enum — verify it's imported/available (it is in the standard library, so fine).
- `Table.Combine({Sales_Jan, Sales_Feb})` — **this is wrong as written for the append button output.** The button generates a query that references the *other* queries by name via the `#"Query Name"` syntax with `Table.Combine` only when you use the "Three or more tables" mode; for two tables via the button it generates `Table.Combine({Source, OtherQuery})` where `Source` is `Sales_Jan` only if the query itself is built that way. More importantly: the snippet claims "the generated M code for appending two queries" — but the actual generated code when you click the button in the currently selected query is:
  ```
  let
      Source = Table.Combine({Sales_Jan, Sales_Feb})
  in
      Source
  ```
  Only if the query names literally resolve. That's true only if you renamed them. The article does say to rename, so this is *technically* correct — but only because of the earlier instruction. Add a one-line caveat: "assuming you renamed the queries as above."
- Step 5 folder snippet: `Table.AddColumn(Filtered, "Data", each Csv.Document([Content], [Delimiter=","]))` — missing the `Type` argument for the added column. Works, but `Table.AddColumn` with no type defaults to `any`, which the article later warns about ("type each source"). Inconsistent with the article's own advice. Add `type table`.
- The folder snippet also skips `Table.PromoteHeaders` and type transforms on each file, contradicting the earlier "clean before appending" rule. Add a comment acknowledging the snippet is skeletal.

**Links (verified against real slugs)**
- `/tutorials/merge-vs-append-queries/` ✅ exists
- `/tutorials/power-bi-common-mistakes-beginners/` ✅ exists
- `/tutorials/data-modeling-star-schema/` ✅ exists
- `/tutorials/power-bi-excel-integration/` ✅ exists
- `/tutorials/directquery-vs-import-mode/` ✅ exists
- `/tutorials/measure-vs-calculated-column/` ✅ exists
- `/tutorials/filter-context-row-context-explained/` ✅ exists
- `/tutorials/dax-basics/` ✅ exists

All eight Related Reading links resolve. Good.

**Internal link opportunities missed:** You discuss star schema, fact tables, and dimensions in the closing paragraph but don't link to `/tutorials/data-modeling-star-schema/` *inline* — only in Related Reading. Add an inline link.

**FAQ / format**
- Six FAQ entries is heavy for a beginner article. The "affect query folding" question is arguably not beginner. Consider cutting to four: append vs merge, extra null columns, more than two queries, folder append.
- The FAQ answers restate body content nearly verbatim (mismatch/nulls, three-or-more tables, folding). Either shorten the answers to one sentence each with "see above" pointers, or remove the redundant sections from the body.
- No H1 in the markdown rendering — the frontmatter title serves that role. Consistent with likely site convention; no action if so.
- Headings use sentence case consistently. Good.

---

**VERDICT: PUBLISH-AFTER-FIX**

(Priority fixes: reframe title toward the mismatch/nulls problem, correct the folder snippet type argument, deduplicate FAQ vs body, update description, and verify the `pubDate`.)