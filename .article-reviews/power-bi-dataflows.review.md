# Review: power-bi-dataflows

# Review: `power-bi-dataflows`

## 1. AI-isms

- **Vague opener / thesis-restating intro.** The first sentence duplicates the title's promise and the second ("Confusing the two leads to...") is a filler scare-clause. Rewrite to a concrete hook:
  > *A dataflow has no relationships, no measures, and no DAX. That single fact decides when to use one—and when a dataset is the only viable option.*
- **"the rest of the semantic model"** — hand-wavy. Name it: "relationships, measures, hierarchies, calculated columns, calculated tables, and RLS roles."
- **Mechanical transition / ChatGPT tell: "Now here's the payoff."** Cut it. Just state the fact:
  > *Update the dataflow once and every downstream dataset inherits the fix on next refresh.*
- **"That measure belongs in the dataset, never in the dataflow. Dataflows produce inputs; datasets produce answers."** The parallel-structure aphorism is classic LLM cadence. Keep the first sentence, drop the second.
- **"It is a clean separation that keeps transformation work from being duplicated across fifty PBIX files."** "fifty" is an invented number. Replace: "across every report in the workspace."
- **Repetitive framing.** "Reuse" is hammered in the comparison table, the "Where the Line Gets Blurry" section, and "Common Mistakes." The table's "single most important row is reuse" line is a meta-commentary filler. Either trust the table or cut the sentence.
- **Em-dash abuse.** Multiple sentences lean on `—` as a soft conjunction: "you update the dataflow once and refresh the dataset—every downstream report..."; "A dataflow refresh failure cascades—every dependent dataset fails too." Convert some to periods or commas.
- **"This is why you can have one dataset serving twenty reports"** — "twenty" again feels templated. "many reports" is fine.

## 2. Topic Fit

- **Rankability:** Solid long-tail shape. "Power BI Dataflows" is a real search head with meaningful volume; the "vs datasets" and "when to use" angles pull in modifier traffic. The FAQ block is well-targeted for featured snippets ("Can a dataset be built directly on a dataflow...", "Do dataflows require Premium capacity").
- **1k UV/day goal:** Attainable only if this piece is positioned against the handful of high-authority incumbents (Microsoft Learn, Radacad, SQLBI). The current draft is *correct* but generic — it does not contain a distinctive hook that would win ranking over Learn docs. Two improvements:
  1. Add a **comparison-to-fabric** callout. As of 2024–2026 the FAQ "do dataflows still matter next to Fabric lakehouses / mirrored databases" is what readers actually search. Currently absent.
  2. Add a concrete **worked architecture diagram in prose** (e.g., "SQL → raw dataflow → curated dataflow → thin dataset → 12 reports") with refresh-chain timing. That's the differentiator LLM-incumbents can't easily reproduce.
- **Better angle:** Consider retitling to *"Power BI Dataflows vs Datasets: When to Use Which (and When to Skip Dataflows for Fabric)."* "Explained" is weak SEO — nobody types it.

## 3. Errors

**Link check (all verified against the slug list):**
- `/tutorials/directquery-vs-import-mode/` ✓
- `/tutorials/measure-vs-calculated-column/` ✓
- `/tutorials/de-power-query-getting-started/` ✓
- `/tutorials/merge-vs-append-queries/` ✓
- `/tutorials/data-modeling-star-schema/` ✓
- `/tutorials/filter-context-row-context-explained/` ✓
- `/tutorials/power-bi-date-table/` ✓
- `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` ✓

All internal links resolve. No broken slugs.

**Terminology / technical accuracy:**
- **"CDM folder format"** — Microsoft has moved CDM to the legacy lane. As of 2024+ the current storage is **Azure Data Lake Storage Gen2 with Delta tables** for Fabric-backed workspaces, and CDM (.crm) for the older Power BI-native dataflow path. The draft presents CDM as universal. Fix: "in the comma-delimited CDM format for legacy dataflows, or as Delta Parquet in Fabric-backed workspaces."
- **"You cannot reference another entity with a calculated column here"** — wording is confused. The real constraint is that Power Query in a dataflow cannot use DAX `CALCULATE`/`RELATED`; computed entities reference other entities by name. Rewrite: "You can't use DAX here; cross-entity enrichment happens via computed entities, not calculated columns."
- **"DirectQuery against a dataflow is not supported the same way it is against Azure SQL"** — muddled. The honest statement: **DirectQuery against a dataflow is not supported**; datasets ingest dataflow entities in Import mode. The current phrasing implies there's a "limited scenario" path. There isn't, for dataflow-backed entities. Cut the hedge.
- **"you cannot reference another entity with a calculated column"** — appears twice; second instance (in the computed entities paragraph) is correct, first is misleading. Reconcile.
- **"Power BI Dataflows connector"** row in table vs body text calling it "Power BI dataflows" — pick one casing, capitalization of connector names should match UI: "Power BI dataflows."
- **PPU caveat on computed entities:** The FAQ says shared capacity has "no computed entities in some configurations." This is under-specified. PPU/ Premium unlocks computed entities; shared capacity does **not** support them at all. Fix accuracy.
- **Incremental refresh** listed as a dataset-only benefit is fine, but the draft implies dataflows lack any incremental capability — dataflows **do** support incremental refresh since 2020 (Premium only). Add a parenthetical.

**Frontmatter:**
- `pubDate: 2026-10-14` — future date. If this is intentional scheduling, fine; if not, it will be flagged by build. Confirm.
- `difficulty: Advanced` — reasonable for the audience, but the body reads more Intermediate. Consider `Intermediate` unless the Fabric angle is added.
- `tags: ["dataflows", "etl"]` — add "architecture" and "premium" to widen discoverability. Current tags are thin.
- `category: data-modeling` — acceptable, though "ingestion" or "architecture" would rank better against the dataflow cluster.

**Format / FAQ:**
- FAQ uses `### Q:` headers. Most site conventions prefer `###` question text without the "Q:" prefix (or `**Q:**` inline). Check the pattern in other published posts; the "Q:" prefix is unusual.
- The comparison table uses sentence case inconsistent with the header row ("Contains measures" vs "Row-level security"). Minor, but normalize.
- Code block language tag `powerquery` may not be recognized by the MDX/highlighter. Common alternates: `m`, `powerquery-m`. Verify the renderer accepts it; otherwise the block will render unhighlighted.
- DAX block is fine but the `Revenue YTD` example references a `Sales[Amount]` column never shown being bound to a date table — an unfamiliar reader can't reproduce it. Add one line: "with a marked Date table related to `Sales[OrderDate]`."

---

**VERDICT: PUBLISH-AFTER-FIX** (address the CDM/Delta accuracy issue, the muddled DirectQuery and "calculated column" wording, the future pubDate, and cut the AI-isms in the payoff/aphorism paragraphs).