# Review: vertipaq-optimizer-power-bi

# Editorial Review: `vertipaq-optimizer-power-bi`

## 1. AI-isms

**Vague opener / thesis-statement em-dash pattern**
> "When a report feels slow, the bottleneck is rarely DAX syntax alone. It is usually how much data VertiPaq has to scan..."

Reads like an essay prompt. Rewrite: *"Slow reports are rarely a DAX syntax problem. They're a storage problem: VertiPaq has to scan and decompress too many bytes."*

**Telling, not showing ("The tool answers three questions:")**
Bolded numbered list is a classic LLM sign-post. Cut the frame; just present the three numbers inline:

> "The tool exposes three numbers per table, column, and relationship: **memory bytes**, **bits per value / dictionary size**, and **encoding (Hash vs Value)**."

**Filler transitions**
- "This article walks through installing it, reading its output, and acting on..." → Cut entirely, or one line: *"Here's how to install it, read it, and act on the four highest-impact findings."*
- "Run through this after every analyzer pass:" → "After every analyzer pass:"
- "Change the model only after the analyzer shows..." → "Don't touch the model until the analyzer shows..."

**Em-dash abuse**
Four em-dashes in the intro paragraph alone. The "X — meaning — Y — Z" cadence is a dead giveaway. Convert half to colons, commas, or periods. Example:
> "a free external tool (distributed as a Power BI template plus a Tabular Editor script) that reads the model's metadata and exposes those numbers as tables you can sort and filter."

**"VertiPaq cannot compress what you give it; it can only compress it well or badly."**
This is a fortune-cookie sentence. Delete. Same for:
> "Deleting them is free performance."
> "Memory savings compound."

**"Classic symptom:"**
LLM tell. Replace with concrete: *"Example: a `Customer Name` column with 900,000 rows and 850,000 distinct values."*

**Section titles**
"Acting on the Results: A Checklist" and "Common Mistakes" are fine, but "Reading the Columns Table" / "Reading the Relationships Table" / "Reading the Tables Table" is a mechanical trio. Vary or merge the last two.

**"VertiPaq is stored in the VertiPaq engine" (intro sentence)**
Tautology. Rewrite:
> *"Every Power BI Import model lives in a columnar, in-memory database called VertiPaq."*

---

## 2. Topic Fit

**Rankability:** The slug `vertipaq-optimizer` targets a real, low-competition long-tail — searches for the SQLBI tool and DAX Studio's VertiPaq Analyzer pane are steady. Advanced/niche, but consistent. Good.

**Fit for 1k UV/day goal:** Weak as a *driver*, strong as a *supporter*. It's a mid-funnel, advanced topic that will pull maybe 15–40 sessions/day at maturity. To contribute meaningfully to the 1k/day target it needs:
- **A clearer keyword in the H1:** "VertiPaq Analyzer: Optimize Your Power BI Data Model" — "Optimize" is too generic. Consider **"VertiPaq Analyzer: Find and Fix a Bloated Power BI Model"** (higher intent, more specific).
- **Better title tag** leveraging the SQLBI/DAX Studio split: `"VertiPaq Analyzer + DAX Studio: Locate Bloat in 5 Minutes"`.

**Angle improvements:**
- The strongest section is **Fix 1 (surrogate integers)**. That alone could be a linked standalone tutorial.
- The **DaX Studio route** is buried in step 3. Lead with it — it's the path 80% of readers will take (no external installer, no model mutation).
- Missing: **a screenshot/sample of the actual Columns table output**. Advanced readers search this page to interpret numbers; without a concrete "here's what a bad dictionary looks like" example with real byte magnitudes, the article reads abstract.
- Missing: **the "Table size > 100MB in Desktop-only" threshold is fine, but give a Service/Dataset memory ceiling reference** — that's what most readers are actually panic-searching.

**Internal link harvest opportunity:** No links to `/tutorials/dax-variables-best-practices/`, `/tutorials/power-bi-row-level-security/`, or `/tutorials/power-bi-field-parameters/`, all of which intersect with "unused column" detection. Add at least RLS (RLS rules reference columns, which kills the "delete unused columns" advice in some models).

---

## 3. Errors

**Terminology / technical**

1. **"VertiPaq Analyzer is a free external tool (distributed as a Power BI template plus a Tabular Editor script)"** — Slightly off. SQLBI's tool is primarily a **`.pbit` template** whose visuals bind to a model statistics table that must be populated (historically via Tabular Editor script, now often via DAX Studio's export). The article then says the Tabular Editor script *"writes them to a model table called `VertiPaqAnalyzer`"* — the actual table produced by the SQLBI script is named `VertiPaqAnalyzer` (or `$SYSTEM.MDSCHEMA_*` depending on version), and DAX Studio writes to its **own** internal pane, not the model. The two workflows are conflated. Tighten: distinguish (a) SQLBI `.pbit` + script → writes a model table; (b) DAX Studio pane → reads metadata from a live session without writing anything.

2. **`INFO.COLUMNS()`** — This function **requires a model with compatibility level 1200+ and is only available in Power BI Desktop / SSAS 2016+**, but more importantly it is **not queryable from a report visual** — it only works from DAX Studio / Tabular Editor / a tool that has metadata access. Presenting it as a plain `EVALUATE` inside the article is fine, but the reader needs to know it won't run in the report. Add: *"Run this in DAX Studio against the Desktop instance."*

3. **`SELECTCOLUMNS(INFO.COLUMNS(), "Table", [TableID], ...)`** — `[TableID]` here returns the table's **internal ID (an integer)**, not its name. You want `[Table]` (or `[ExplicitName]` on the table). As written, the "Table" column in the output will be a numeric hash and useless for the stated purpose. Fix:
   ```dax
   EVALUATE
   SELECTCOLUMNS(
       INFO.COLUMNS(),
       "Table", [Table],
       "Column", [ExplicitName],
       "Data Type", [ExplicitDataType]
   )
   ORDER BY [Table], [Column]
   ```

4. **"Many-to-many relationships force VertiPaq to hash two large dictionaries at query time"** — Imprecise. M2M is materialized as an intermediate table at processing time in modern VertiPaq; the *query-time* cost is not "hashing two dictionaries" but scanning the bridge and expanding the result set. The claim as written is technically wrong.

5. **`EARLIER` explanation** —
   > "Watch out for `EARLIER`, which needs a nested row context to make sense. It works inside a calculated column only against an outer row context, not as a general aggregation function"

   Confusing and partly wrong. `EARLIER` **requires an inner and outer row context** — a single row context is not enough. Fix: *"`EARLIER` only works when there are two nested row contexts (e.g., a calculated column iterating an outer table). It has no meaning in a single-row-context calculated column and will error."*

6. **DirectQuery storage claim (FAQ):**
   > "DirectQuery tables have no compressed storage in VertiPaq, so their byte-level stats are not meaningful."

   Correct in spirit, but the FAQ also says "you can still inspect cardinality" — cardinality *is* available for DQ only if the model has statistics/sampling enabled. Add caveat.

7. **Dual mode recommendation:**
   > "dual mode with a pre-aggregation table is often the right compromise."

   Directionally right, but "dual + pre-aggregation" is not a single mechanism. Dual = storage mode that allows either engine to serve; pre-aggregation = separate table. Either clarify or cut the sentence.

**Frontmatter**
- `pubDate: 2026-10-03` — future date. If the pub system gates on this, it will not publish. Verify.
- `description` is a sentence fragment and duplicates the H1/opening line. Rewrite as a proper 140–155 char meta description with a hook: *"VertiPaq Analyzer exposes the byte-level cost of every column in your Power BI model. Here's how to read it and fix the four biggest offenders."*
- `tags` only two; add `"dax-studio"`, `"vertipaq"`, `"tablar-editor"` (or `"tabular-editor"` — verify spelling; the tool is **Tabular Editor**, not "Tablar", but check the tag taxonomy).

**Internal links (verified against the provided real slugs)**
All eight Related Reading links exist. ✅ No broken links.

But the body has **zero inline internal links** despite the article calling out star schema, DAX optimization, Performance Analyzer, bidirectional filtering, and RLS-adjacent workflows. Add inline links at:
- "star schema" → `/tutorials/data-modeling-star-schema/`
- "Bidirectional filters invite ambiguous paths" → `/tutorials/bidirectional-filtering-guide/`
- "Use Performance Analyzer for query timing" → `/tutorials/power-bi-performance-analyzer-guide/`
- "row context" → `/tutorials/filter-context-row-context-explained/`

Consider also linking `/tutorials/power-bi-row-level-security/` in the "unused columns" section (RLS rules silently reference columns and will break deletion).

**FAQ / formatting**
- FAQ headings use `###` — consistent. Good.
- FAQ answers are long for FAQ schema; Google prefers 40–60 words. The DirectQuery answer runs ~55 words, fine; the first answer runs ~40, fine. The "high cardinality acceptable" answer is vague — it doesn't give a number. Add a rule of thumb (>1M distinct text values = investigate).
- No FAQ JSON-LD mention. If the site supports it, add structured data.
- Missing `<h2>` repetition: "Reading the Relationships Table" and "Reading the Tables Table" both start with "Reading the". Vary.
- Table columns use `|` correctly, but the `Encoding` row says "Value for sorted/compressed, Hash for unsortable" — misleading (Value encoding requires sorted data and is preferred; Hash is fallback). Reword: *"Value (preferred, sorted) / Hash (fallback)"*.

**Code blocks**
- Power Query block: fine, but `type number` should be `type number` (correct) — no issue. `Int64.Type` requires `Table.TransformColumnTypes`, used correctly.
- DAX comments use `--` — valid inside DAX, but in the article readers may paste into a measure editor where `--` works, so acceptable. Note the first comment says "Cheap: integer flag, low cardinality" — this is a **calculated column**, so calling it "cheap" relative to a text column is fair, but readers may infer calculated columns are generally cheap. Add a one-line caveat.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the `INFO.COLUMNS()` column bug, the conflated SQLBI/DAX Studio workflow, and the `EARLIER` description; otherwise the article is technically competent but reads a notch too "essay-like" and needs inline internal links to earn its traffic.