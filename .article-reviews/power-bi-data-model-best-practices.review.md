# Review: power-bi-data-model-best-practices

# Review: `power-bi-data-model-best-practices`

## 1. AI-isms

The draft is cleaner than most ChatGPT-shaped content, but a few tells remain:

- **"The single highest-impact decision is…"** / **"The practical test:"** / **"Note the use of `VAR`…"** — these "announcer" openers are a strong AI cadence. Rewrite as plain declaratives:
  - "The single highest-impact decision is the shape of your tables." → "Table shape has the biggest impact on model performance."
  - "The practical test: draw your tables on paper…" → "If your sketched relationships form loops, or a fact table joins another fact table, the model needs rework."
  - "Note the use of `VAR` to compute each branch once…" → "`VAR` computes each branch once and keeps the formula readable."

- **"A model is a product other people maintain. Conventions pay off:"** — vague platitude opener. Cut or replace with the concrete rule: "Follow these conventions so the next developer can read your model."

- **"Performance work starts before DAX. A few habits:"** — filler transition + listicle tic. Drop "A few habits" entirely; the bullets are self-evident.

- **Em-dash usage** — mostly controlled. The two offenders are "a Product dimension with 50,000 rows… is cheap; splitting it into three tables is not free" (fine) and the description sentence "share one root cause: a weak data model" (fine). No over-the-top abuse, but you do have three `—` splices in a single paragraph under "Cardinality" ("A column's cardinality — the count of distinct values — drives…"). Convert the first pair to parentheses or rewrite.

- **"quietly cost performance"** — mildly editorializing. "Quietly" adds nothing. Cut.

- **FAQ answers all open with "Yes / Use / Occasionally / Technically / Open the Model view"** — good, no "Great question!" filler. Keep.

- **"they seem convenient and create non-deterministic results"** — fine voice; leave.

## 2. Topic fit

- **Long-tail rankability:** The slug is head-term, not long-tail. "Power BI data model best practices" is a competitive SERP (Microsoft docs, SQLBI, Enterprise DNA, Guy in a Cube). For a 1k organic UV/day contributor piece, this is a stretch as-is. You will not outrank SQLBI on the head term.
- **Better angle:** Retitle to a long-tail problem-first variant that this article actually delivers. Suggestions that match the body's real value:
  - `power-bi-star-schema-vs-snowflake-when-to-flatten`
  - `power-bi-data-model-mistakes-to-avoid`
  - `power-bi-relationship-direction-best-practices`
  
  The star-schema-vs-snowflake overlap with your existing `/tutorials/data-modeling-star-schema/` is also a cannibalization risk — see §3.
- **Serves 1k UV/day goal?** Only if it ranks for a narrower modifier. As written it is a hub/roundup page, which is fine for internal linking and topical authority but unlikely to pull the traffic target by itself.
- **Best angle for volume:** A comparison/decision piece ("Star vs Snowflake: when to flatten in Power BI") is far more winnable and still internal-links cleanly to your star-schema pillar.

## 3. Errors

**Frontmatter**
- `title` and `slug` are fine.
- `pubDate: 2026-10-15` is a future date (today is 2026-10-15 per slug context — confirm it is not a typo for 2025). If it is intentional embargo, ok; otherwise fix.
- `difficulty: Intermediate` — the piece drifts between beginner (what is a calculated column vs measure) and intermediate (VertiPaq compression, aggregations). Not fatal.
- No `updatedDate`, no `canonical`, no `ogImage` — check your site schema; if other tutorials carry these, add them.
- `tags` uses spaces ("data modeling", "best practices"). If your build normalizes, fine; otherwise use `data-modeling`.

**Terminology / code**
- **"Fixed decimal number"** — correct Power Query nomenclature is **Fixed decimal number**; ok. But your table's "Why" says "Avoids floating-point rounding in aggregations" — technically you should note fixed decimal has higher storage cost and is slower; the table presents it as a free win. Add the tradeoff.
- **`Total Sales :=`** uses `:=` for measures — this is accepted, but modern convention and your F2 parser typically use `=`. Inconsistent with `Date =` a few sections later. Pick one across the article.
- **`Sales[Unit Price]`** — column names in DAX with a space are legal but unusual; if the model convention earlier says "Use spaces in measure names and no spaces in column names where you write a lot of DAX," then `Sales[Unit Price]` contradicts your own rule. Either rename to `UnitPrice` in the code, or soften the rule to "pick one convention."
- **`SAMEPERIODLASTYEAR ( 'Date'[Date] )`** — requires the Date table to be marked as a date table. You say this three paragraphs later; move the requirement up or annotate inline.
- **Date table snippet** uses `[Date]` reference inside `ADDCOLUMNS`'s `CALENDAR` — correct because the base column is named `Date`. Fine.
- **`"Quarter", "Q" & QUARTER ( [Date] )`** — concatenation of string + int works in DAX, but returns a **text** column, which sorts "Q1" before "Q10" only if the number is always 1–4 — ok, but "Q10" never occurs. Fine.
- **`FORMAT ( [Date], "YYYY-MM" )`** — should be lowercase `"yyyy-mm"` per ISO/DAX convention. `YYYY` in DAX format strings is not a valid token in all regions (it is interpreted as year in some locales, but `yyyy` is the canonical form). Fix.
- **Power Query example:** `Sql.Database("server", "warehouse")` then `Source{[Schema="dbo", Item="FactSales"]}[Data]` — this works only if the source is a SQL Server data source with navigation. Fine for illustration, but you wrote `"server", "warehouse"` without a `.database.windows.net` note; minor.
- **`Table.Buffer` "can help iterative lookups but hurts memory on large tables"** — the parenthetical is correct but flip the phrasing: it *forces* buffering and *increases* memory on large tables. The current wording ("hurts memory") is vague.
- **"roughly a hundred million rows"** — arbitrary. SQLBI's guidance varies by column count/width; consider "when a single fact table exceeds your Import refresh window" instead.
- **"Null keys break relationships silently"** — Power BI actually logs a warning/count of unmatched rows in the relationship dialog. "Silently" is wrong. Say "Break the join and show a blank row in the related table; check the relationship dialog for the unmatched count."

**Internal links — verification against provided slug list**
All eight links in "Related Reading" resolve against the provided list. Confirmed:
- `data-modeling-star-schema` ✓
- `bidirectional-filtering-guide` ✓
- `measure-vs-calculated-column` ✓
- `filter-context-row-context-explained` ✓
- `power-bi-date-table` ✓
- `directquery-vs-import-mode` ✓
- `dax-optimization-techniques` ✓
- `dax-variables-best-practices` ✓

**Missing internal links (opportunities):**
- Section "Choose Relationship Directions Deliberately" mentions `USERELATIONSHIP` and role-playing dimensions — link to `/tutorials/dax-calculate-function/` or `/tutorials/calculate-function/` (you have both — pick one, duplicates are a flag).
- Section "Build a Dedicated Date Table" → should link `/tutorials/dax-time-intelligence-ytd-qtd-mtd/`.
- Section "Common Data Model Mistakes" → link `/tutorials/power-bi-common-mistakes-beginners/`.

**Duplicate slugs to flag to editorial:** your site has both `/tutorials/calculate-function/` and `/tutorials/dax-calculate-function/`; both `/tutorials/dax-variables-guide/` and `/tutorials/dax-variables-var/`; both `/tutorials/copy-conditional-formatting/` and `/tutorials/copy-conditional-formatting-power-bi/`. Not this article's problem, but worth raising.

**FAQ**
- Five questions is heavy but acceptable. The Q3 answer ("How many relationships can a single table have?") answers a question nobody asks. Replace with one that matches search intent: **"Should I use one big flat table instead of a star schema?"** — that is a real long-tail query and a natural extension of this article.
- FAQ answers lack an explicit "short answer first" pattern in Q1 and Q4 — they start with "Yes"/"Occasionally" which is fine, but Q5 buries the tool name mid-sentence. Lead with "DAX Studio's VertiPaq Analyzer."

**Formatting**
- Description field is 140 chars and ends mid-thought ("share one root cause: a weak data model."). Fine but front-loaded keyword "Power BI data model" is missing from the description — hurts CTR on SERPs. Rewrite: *"Power BI data model best practices: star schema design, relationship direction, measure vs calculated column, and the mistakes that slow reports down."*
- Code fences: `dax` and `powerquery` are both supported by your renderer (verify — some Astro setups use `pq`).
- No H1 inside the body — correct, assuming your layout injects the title.
- Bullets under "Naming, Hiding, and Formatting" mix "and" naming with three unrelated concerns; consider renaming the section to **"Model Hygiene."**

## VERDICT
**PUBLISH-AFTER-FIX** — fix the `FORMAT "YYYY-MM"` token, `:=` vs `=` inconsistency, `Sales[Unit Price]` vs your own naming rule, the false "silently" claim about null keys, tighten the AI-ism openers, add the two missing internal links, retitle toward a long-tail angle (or accept it as a hub page), and replace FAQ Q3.