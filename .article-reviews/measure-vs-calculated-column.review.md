# Review: measure-vs-calculated-column

# Review: `measure-vs-calculated-column`

## 1. AI-isms

Overall the writing is tighter than typical AI output, but several tells remain.

- **"The first real decision you make in a Power BI model…"** — used in the frontmatter `description` *and* the opening sentence *and* echoed again in "That single difference drives everything else." Repetition of the "this is the one big idea" framing is a classic AI opener. Rewrite the intro to be concrete, e.g.: *"Two calculations can look identical in the formula bar and behave completely differently. This tutorial covers when each one is correct."*
- **"Full stop."** (Decision rule #1) — ChatGPT-flavored emphatic filler. Cut it.
- **"The rule is: columns trade memory for speed and lose flexibility; measures trade CPU for flexibility and cost nothing when unused."** — sounds quotable, but "lose flexibility" and "cost nothing when unused" are hand-wavy and not strictly true (measure *definitions* cost nothing; measure *evaluations* do). Rewrite as a plain sentence or drop.
- **"That single difference drives everything else: memory usage, evaluation context, and where you can use the calculation at all."** — mechanical transition trope. Also lists three things then the section already covers them. Delete or fold in.
- **Em-dash usage** is heavy: "materialized — it physically lives", "40 minutes, some of that time is this column", "filtering a measure — the filter simply", "Measures are not automatically faster — a badly written", "a fixed attribute — a bucket, a flag". At least half can be converted to commas, colons, or parentheses. The "fixed attribute — a bucket, a flag, a concatenated key" one in particular reads like an AI list inside a dash.
- **"A classic pattern is…"** — throwaway genAI phrase. Drop "classic."
- **"Two functions trip up beginners…"** — the "X things trip up beginners" construction is a giveaway. Vary: *"RELATED and EARLIER only work in calculated columns."*
- **"Ask these questions in order:"** then a numbered list where item 1 already answers everything ("Full stop"). The list is padded.

No hallucinated statistics (good). No "In today's data-driven world" (good). No "Let's dive in" (good).

## 2. Topic fit

- **Long-tail rankability**: Good. "measure vs calculated column" and "calculated column vs measure power bi" are real search queries with clear intent. The slug is clean and evergreen.
- **Serves the 1k organic UV/day goal**: Realistically this is a **mid-volume** head-adjacent term, not long-tail — it sits on the boundary between a "definition" query and a "when to use" query. It can rank and pull traffic, but as a single tutorial it likely brings a few hundred UV/month at maturity, not 1k/day. It's a *good* pillar candidate that needs supporting content, not a standalone traffic driver.
- **Angle problem**: the piece is currently encyclopedic ("here is what each object is") when the search intent is decisional ("which do I use, and why was my number wrong?"). The strongest, most differentiated section is **"Common mistakes"** and the ratio-summing point. Consider either:
  - **Retitling** to match intent: *"Calculated Column vs Measure in Power BI: When to Use Each (with Wrong-Total Example)"*, or
  - **Promoting** the "sum of ratios is not the ratio of totals" example into the hero of the piece with a worked dataset. That's the hook that converts readers and earns links.
- **Missing angle**: no mention that in **DirectQuery** calculated columns are especially costly (they run at the source and may not fold). One sentence here would substantially deepen the answer, and there's an existing slug to link (`/tutorials/directquery-vs-import-mode/`).
- **Missing angle**: **calculation groups / field parameters** as the modern alternative for some use cases. There is a `/tutorials/power-bi-field-parameters/` slug available.

## 3. Errors

**Terminology / DAX**

- "*A measure is written in the Report view*" — false. Measures can be created from any view via the ribbon, and DAX Studio / Tabular Editor entirely outside Power BI Desktop. Rephrase: "typically authored in the Report or Data view."
- "*A calculated column is created in the Data view (or from the Modelling tab).*" — inconsistent UK/US spelling ("Modelling" vs. the rest of the article's US English). The ribbon tab in current Power BI Desktop is **"Modeling"** (US). Fix.
- "*`Profit Margin % =`* … followed by `Profit Margin % :=`" — **inconsistent assignment operators**. In Power BI Desktop the `=` form is what you type; `:=` is Tabular Editor / SSAS / XMLA convention. Pick one and note it, otherwise this reads as an error.
- "*A calculated column cannot reference another table's columns without `RELATED` or `RELATEDTABLE`*" — mostly true but incomplete: it also can use `LOOKUPVALUE`, `TREATAS`+`CALCULATE`, or `RELATEDTABLE` only for the *many* side. Also, **`RELATEDTABLE` is not in the `RELATED`/`EARLIER` "only in calculated columns" bucket the way the article implies** — the article says "Two functions trip up beginners because they only work in calculated columns" then presents `RELATED` and `EARLIER`. That's the two, fine — but the very next paragraph calls `EARLIER` "more subtle" as if `RELATED` also requires two row contexts. Tighten.
- "*`EARLIER` requires a **nested row context** — two row contexts stacked, with `EARLIER` referring to the outer one.*" — correct in spirit, but the phrasing "two row contexts stacked" is loose. Better: "It requires a row context that is outer to the current one — i.e., a row-context-producing iterator nested inside another row-context-producing iterator."
- "*`RANKX` … works in both columns and measures*" — true, but the linked `/tutorials/dax-rankx-function/` is not in Related Reading (see below). Either link it or drop the name.
- "*A `SWITCH`-heavy column can add hundreds of megabytes*" — plausible but unsourced. Either soften ("can add substantial size") or cite a concrete example with row count and cardinality. As written it reads like invented precision.
- "*Performance Analyzer … storage engine versus formula engine queries*" — correct, but the follow-on "*If a measure is causing a large number of formula engine calls, it usually needs rewriting rather than converting to a column*" is a non-sequitur in a beginner article and mildly misleading (FE-vs-SE is not the whole story). Either expand or trim.
- "*Push the logic upstream into Power Query*" — for a **calculated column replacement**, Power Query is correct; for a **measure**, it's usually wrong advice (measures aren't computable in M). The decision rule #5 conflates them.

**Frontmatter**

- `pubDate: 2026-10-09` — a future date relative to typical review workflow. If this is intentional scheduling, fine; if not, it's a red flag for a `published` post with `draft: false`. Confirm.
- `description` is vague marketing copy ("The first real decision you make…"). Rewrite to match search intent, e.g.: *"When to use a calculated column vs a measure in Power BI, with decision rules and the ratio-totaling mistake that breaks reports."*
- `tags: ["dax", "data modeling"]` — slug-cased tags elsewhere? Check site convention; if other posts use `"Data Modeling"`, match it.
- Missing `updatedDate` if the site supports it — this is the kind of evergreen post where it matters.

**Broken / mismatched internal links**

Every link in **Related Reading** resolves against the REAL SLAGS list — verified:
- `/tutorials/dax-basics/` ✓
- `/tutorials/filter-context-row-context-explained/` ✓
- `/tutorials/calculate-function/` ✓
- `/tutorials/dax-earlier-function/` ✓
- `/tutorials/dax-variables-best-practices/` ✓
- `/tutorials/data-modeling-star-schema/` ✓
- `/tutorials/power-bi-common-mistakes-beginners/` ✓
- `/tutorials/power-bi-percentage-of-total/` ✓

**Missed links** — the article names topics whose target slugs exist but are not linked:
- `RANKX` is mentioned → `/tutorials/dax-rankx-function/` exists, link it.
- "Push the logic upstream into Power Query" → `/tutorials/merge-vs-append-queries/` is the closest match; consider linking `/tutorials/directquery-vs-import-mode/` instead for the deeper point.
- "`CALCULATE` modifiers" in the measure section → link `/tutorials/dax-calculate-function/` in addition to `/tutorials/calculate-function/` (they appear to be duplicate topics — flag to editor which is canonical).
- Decision rule #3 mentions slicers/axes → `/tutorials/power-bi-field-parameters/` is a legitimate "modern alternative" cross-link.
- If you add a DirectQuery caveat, link `/tutorials/directquery-vs-import-mode/`.

**FAQ / format**

- FAQ Q&A format is inconsistent: three answers start with a "Yes/No/Because" and two don't. That's fine stylistically but the headings use `### Q: …` while Related Reading uses `##`. Decide on one H-level for FAQ.
- FAQ question **"Why does my total row show a wrong number when I use a calculated column?"** duplicates the earlier paragraph "*This is why measures are the correct choice for ratios…*" almost verbatim. Either delete the FAQ or delete the earlier paragraph — repeating the same fact in body and FAQ is a known AI pattern.
- FAQ answer **"Can I put a measure on a slicer?"** → "No. Slicers need a column." True, but the follow-on advice ("build a calculated column for the categories") is worth a link to `/tutorials/power-bi-field-parameters/` as the modern alternative.
- The `-->` comment inside the conversion code block (`-- Column (per row)`) is fine but the *second* block starts with `-- Measure (aggregated over the filter context)` while the article hasn't told readers that `--` is DAX line comment syntax. One-line note would help beginner audience.
- No `## Conclusion` — the article ends on Related Reading. Given the FAQ is the last substantive section, add a two-sentence takeaway or drop to make the FAQ the deliberate close.

**Other**

- Comparison table row *"Can reference other measures | No | Yes"* is correct for the column side, but a calculated column **can** reference another calculated column in the same table. Add a parenthetical so it isn't misread.
- "*A measured … cost nothing when unused*" — a measure defined but never evaluated indeed costs no engine time, but its definition still exists in the model metadata. Not worth belaboring, but the phrasing invites pedantry.
- "*filtering a measure with a slicer set to the same column*" — the sentence assumes the reader knows the slicer column and the measure's column are physically different objects. As a beginner article, this needs one clarifying clause.
- The `RELATED` example uses `Products[Category]` — no indication whether the relationship is active or what direction. Fine for a beginner, but the phrase "*across a many-to-one relationship*" should be "*from the many side to the one side*."

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the `=` vs `:=` inconsistency, "Report view" claim, UK/US spelling of Modeling, the duplicated FAQ/body ratio-totaling paragraph, the misleading "push logic to Power Query" advice for measures, and the AI-ism openers; add RANKX and DirectQuery links; retitle/reframe to match search intent.