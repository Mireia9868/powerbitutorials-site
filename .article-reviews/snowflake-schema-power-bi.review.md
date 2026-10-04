# Review: snowflake-schema-power-bi

# Review: `snowflake-schema-power-bi`

## 1. AI-isms

**Vague opener / filler closing.** The intro and the "Recommendation" both use the "real constraints" / "When in doubt, model the star first" cadence that reads as generic LLM wrap-up. The near-duplicate sentence "For typical import models built from a handful of source tables, flatten and stay flat." re-states the recommendation verbatim from the intro — delete it.

**Mechanical "There are X cases" scaffold.** "There are practical cases where keeping a normalized dimension pays off:" followed by a 4-bullet list, then later "These are real constraints." is the classic ChatGPT hedge move. Rewrite as a tighter para: "Snowflaking pays off in four narrow cases:…" and drop the second hedge.

**Em-dash / semicolon staccato.** "That is the trade: snowflaking pushes complexity into DAX and relationships; flattening pushes it into Power Query, once, at load time." Two clauses balanced by colon+semicolon is a fingerprint. Rewrite plain: "You are trading DAX complexity for Power Query complexity. Pay it once at load time, or pay it forever in every measure."

**Cliché signpost.** "Choosing correctly affects DAX complexity, refresh time, and how easily users find their way around the model." — "find their way around the model" is filler. Cut to: "It affects DAX complexity, refresh time, and discoverability."

**Hollow verbs.** "invite relationship sprawl", "matters if you later use…", "can produce unexpected results" — replace with specifics (e.g., "produces wrong subtotals when the many-side of a chain hop is filtered both ways").

**FAQ voice.** All four answers repeat the pattern *[direct answer] → [rephrase] → [caveat]*. Answers 2 and 4 are literal restatements of body paragraphs. Either cut them or replace with questions that add value ("Does snowflaking hurt DirectQuery more or less than Import?").

**"A subtle accuracy point" / "The stronger argument" / "That is the trade."** Rhetorical pauses that add words without content. Delete.

## 2. Topic fit

- **Rankability:** Yes — "snowflake schema vs star schema Power BI" is a real long-tail with buyer intent (modeling decision). Search volume is modest but the query has low competition and high conversion to your star-schema cluster.
- **Goal fit (1k UV/day):** On its own, no. It's a support post. Value comes from internal-linking it into `/tutorials/data-modeling-star-schema/` and `/tutorials/filter-context-row-context-explained/` and treating it as the *contra* piece to the star-schema pillar. It only earns its traffic if the pillar links back, which the draft doesn't currently do from that side.
- **Better angle:** Narrow to a decision-shaped query, e.g. **"When to snowflake a dimension in Power BI (and when not to)"**, or add a concrete before/after model-diagram walkthrough with a real schema showing filter-propagation timing. Right now the post is conceptual; it lacks a single reproducible example (no screenshots, no numbers, no Performance Analyzer figures). A screenshot of a 3-hop snowflake with a slow visual + the same model flattened would double time-on-page and make it citable.
- **Overlap risk:** ~30% of the body duplicates what a good "star schema" pillar already says. Trim the "Why Power BI Prefers Stars" section to 1/3 its current length and lean harder on the snowflake-specific content (re-flattening patterns, DAX implications, hybrid models).

## 3. Errors

**Code — `USERELATIONSHIP` misuse (blocking).** The `Total Sales by Category` measure is wrong. `USERELATIONSHIP` is for activating an *inactive* relationship between two tables; it does not "traverse" a chain, and it explicitly requires the relationship to already exist as inactive. As written this measure won't compile in a typical Fact→Product→Subcategory→Category snowflake because there is no inactive `DimProduct[CategoryKey] ↔ DimCategory[CategoryKey]` relationship — the path already goes Product→Subcategory→Category. Replace with a plain propagation example:
```dax
Total Sales by Category =
CALCULATE ( SUM ( FactSales[SalesAmount] ) )
-- visual filter on DimCategory[CategoryName] propagates through Subcategory to Product
```
Or, if you're demonstrating `USERELATIONSHIP`, choose a role-playing-date scenario, which is what the function is actually for.

**Code — Power Query comment style.** `// comment` works in the Power Query advanced editor, but your code block is fenced as `powerquery`. Confirm your highlighter supports `powerquery`; if not, use `m` or the language string Prism expects (this is a live-render risk, not a content bug).

**Terminology.** "Denormalized" vs "denormalized" — you use both `*denormalized*` (italic) and plain. Pick one. Also "conformed dimension" is used once in the bullet list without definition; for the audience of this slug, either define it or drop it.

**Frontmatter.**
- `tags: ["data modeling", "schema"]` — "schema" is too generic to be useful for filtering. Change to `["data modeling", "star schema", "snowflake schema", "power query"]`.
- `pubDate: 2026-10-04` is in the future relative to any plausible publish date today; if this Astro site filters drafts by date, the post won't render. Verify or move to the intended date.
- `author: Mireia` — single-name authors are fine if that matches your schema; verify against other posts.
- `difficulty: Intermediate` is consistent with the body. Good.

**Broken / mislinked internal links.**

All URLs in the body and Related Reading exist in the provided slug list **except** every one of the raw-slug links is missing its leading `/tutorials/…` path check is fine, but two issues:

1. **Bare-slug links.** In "Related Reading" you list `/tutorials/data-modeling-star-schema/` etc. as plain text, not markdown links. If your renderer doesn't auto-link, these are dead strings. Convert to `[text](/tutorials/…)`.
2. **Anchor-text link in body** to `/tutorials/bidirectional-filtering-guide/` — exists ✅. `/tutorials/merge-vs-append-queries/` ✅. `/tutorials/calculate-function/` ✅. `/tutorials/filter-context-row-context-explained/` ✅. `/tutorials/power-bi-performance-analyzer/` ✅. `/tutorials/directquery-vs-import-mode/` ✅. `/tutorials/data-modeling-star-schema/` ✅. `/tutorials/dax-variables-best-practices/` ✅. In Related Reading, `/tutorials/dax-optimization-techniques/` ✅ and `/tutorials/power-bi-performance-analyzer-guide/` ✅.

   Missing from links you *mentioned in prose* but didn't link: `/tutorials/calculated-tables-what-if-parameters/` (n/a), `/tutorials/power-bi-common-mistakes-beginners/` (would fit the FAQ about flattening breaking measures), `/tutorials/power-bi-performance-optimization/` (fits Performance section as an alternative to just Performance Analyzer). Add one of these — the post is thin on internal links for its length.

**Duplicate canonical risk.** `/tutorials/power-bi-performance-analyzer/` and `/tutorials/power-bi-performance-analyzer-guide/` both appear. Confirm which is canonical and link only to that one — you currently reference both, which fragments ranking signal.

**FAQ format.** Fine structurally, but see §1: answers 2 and 4 are redundant with body copy. Also, none of the FAQ questions match patterns users actually search ("snowflake schema power bi", "should i snowflake in power bi", "star vs snowflake performance power bi"). Rewrite at least two questions into query-shaped phrasing.

**Missing elements.**
- No diagram/image referenced. For a schema-shape article this is a serious omission — you need at least a side-by-side star vs snowflake PNG, plus ideally a Performance Analyzer screenshot.
- No alt-text placeholder or image frontmatter field.
- "The VertiPaq engine and the DAX formula engine both reward simplicity." — the formula engine and VertiPaq (storage engine) work differently; the sentence is a hand-wave. Either cite a real mechanism (relationship hops become `TREATAS`-style virtual filters; chained relationships add scan cost in the storage engine) or cut.

---

**VERDICT: PUBLISH-AFTER-FIX** — replace the broken `USERELATIONSHIP` measure, convert Related Reading to real markdown links, add at least one diagram, and prune the FAQ/AI-isms before shipping.