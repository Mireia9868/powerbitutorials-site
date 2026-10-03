# Review: power-bi-performance-analyzer

# Review — `power-bi-performance-analyzer`

## 1. AI-isms

**Vague openers / filler intensifiers**

- *"It answers a **narrow but important question**"* — unfalsifiable editorializing. Cut the adjective pair, keep the question. → "It answers one question: where is the time going — the visual, the DAX query, or the rendering engine?"
- *"should be your **first stop**"* — generic advice voice. Fine once, but it recurs as a pattern (see below).
- *"A slow report is **almost always** dominated by one of three causes"* — hedge stacking. Either commit ("Three causes dominate") or don't list exactly three.

**Mechanical transitions**

- Section openers are formulaic: "For a fair baseline…", "Before you optimize…", "A few patterns and what they mean". Not egregious, but the *"A common culprit is…"* opener in the same section as *"A slow report is almost always…"* reads as templated problem-framing.
- *"This is the point where Performance Analyzer hands off to better tools."* — throwaway hand-holding sentence. The next two sentences already say it.

**Em-dash abuse**

- At least 5 em-dashes used as parenthetical commas where a comma or colon is cleaner. Worst offender: *"those usually account for most of the time"* paragraph has three dashes in two sentences. Convert to commas or parentheses. Example: *"If warm is fast and cold is slow, your bottleneck is data scan or cardinality, not the visual."*

**LLM cadence in the FAQ**

- *"Treat it as directionally useful"*, *"you should treat it as a bug regardless of how many visuals are on the page"* — scripted-sounding imperatives. Fine as editing guidance to yourself, weak in published voice.
- The bullet list of "patterns and what they mean" uses the same syntactic template four times (*"DAX query > X, Visual display < Y. [Diagnosis]."*). Deliberate parallelism would be good; incidental sameness reads generated.

**Rewrites (spot list)**

| Draft | Rewrite |
|---|---|
| "It answers a narrow but important question: where is the time going…" | "It tells you which component is slow: the visual, the DAX query, or the rendering engine." |
| "The tool separates these so you stop guessing." | "Read the table wrong and you'll optimize the wrong component." (or delete) |
| "This is the point where Performance Analyzer hands off to better tools." | Delete. The next sentence is the point. |
| "Treat it as directionally useful…" | "It's a lower bound on user-perceived latency." |

The prose is on the better end of AI-assisted drafts (concrete numbers, real DAX, specific tools), but the flourishes above are the tells.

---

## 2. Topic fit

**Long-tail rankability — yes, but the title is weak.**

- Target query is almost certainly `power bi performance analyzer` (head term, dominated by Microsoft docs and Enterprise DNA). The title *"Using Performance Analyzer to Find Slow Visuals in Power BI"* targets `performance analyzer slow visuals` — lower volume than the head but still contested.
- Stronger long-tail angles this draft already partially hits but doesn't target in the H1:
  - `performance analyzer dax query vs visual display` — this is the actual, specific intent the article serves well.
  - `power bi performance analyzer copy query dax studio` — the section that adds genuine procedural value.
  - `power bi performance analyzer directquery` — currently a one-liner, but a real search.
- Suggest retitling to something like **"Power BI Performance Analyzer: How to Read DAX Query vs Visual Display (with DAX Studio Handoff)"** — uglier, but matches the query.

**Serves the 1k UV/day goal?** Marginal on its own. This competes with existing `/tutorials/power-bi-performance-analyzer-guide/` — see Errors below; this is the biggest problem. Two articles on the same topic dilute each other and neither wins the head term. Either:
- **Merge** into the existing guide as a deeper section, or
- **Differentiate hard**: make this explicitly the "read the numbers / DAX Studio handoff" article and rename it that way, and cross-link from the guide.

**Better angle available:** the worked example table (4 visuals, misdiagnosis → fix → 900 ms) is the strongest original piece. A title like *"Diagnosing a 3.8-Second Power BI Page with Performance Analyzer"* would be more rankable in the "power bi slow report" cluster and less cannibalizing.

---

## 3. Errors

### Frontmatter
- `pubDate: 2026-10-03` — a **future date**. Either the site runs on a future-dated queue (fine) or this is a typo (2025?). Flag for verification.
- `category: visualization` — this article is about **performance/optimization**, not visualization. Mismatch with `/tutorials/power-bi-performance-optimization/` which presumably sits in a performance category. Move category.
- `tags: ["performance", "optimization"]` — thin. Add `"dax"`, `"dax-studio"`, `"performance-analyzer"`.
- `author: Mireia` — verify this matches the site's author slug convention (other articles?).

### Terminology / code

- *"open DAX Studio and profile the query"* — DAX Studio doesn't "profile" in the trace sense people expect; it uses Server Timings. Suggest "trace" or "measure". Minor.
- *"File > Connect > PBI / XMLA endpoint"* — DAX Studio menu is **Home → Connect** (not File), and the connection options are "PBI / SSDT Model" and "XMLA Endpoint" separated, not a single item. Verify before publishing.
- *"`VALUES(Customer[CustomerKey])` can produce hundreds of thousands of rows"* — dimension tables rarely have hundreds of thousands of customers. This example is slightly unrealistic and undermines the credibility of the diagnosis. Either pick a fact table, or say "tens of thousands".
- **`TOPN` typo in the Practical Fixes section**: the worked example says *"Rewrite using `TOPN` with variables"* — correct. But later the same section header calls the good pattern out. No bug, but check the **Featured** callout: *"the top-N filter to the visual's Top N filter (which is optimized to use the storage engine)"* — this is **not always true**. Visual-level Top N is not guaranteed to push to the SE; it depends on the visual and query plan. Soften: "often better optimized".
- *"Split into date and time, or round to the nearest minute (or hour), and compress the whole column."* — "compress the whole column" is imprecise. Compression benefit comes from **reducing cardinality**, not splitting per se. Rewrite: "Reducing cardinality lets the storage engine encode the column far more efficiently."
- *"Calculated columns cannot be compressed by the storage engine"* — **this is wrong as stated**. Calculated columns *are* stored and compressed (they materialize at refresh and persist in the VertiPaq store). The correct caution is that they're **computed at refresh**, consume memory, and can't benefit from query-time optimizations. Fix this sentence — it's a factual error a knowledgeable reader will catch.
- *"a `DateTime` column with second-level granularity has 86,400 values per day"* — correct math; but DateTime columns in Power BI typically encode as a numeric (date + fraction), so the cardinality argument should say "distinct values", not "values". Minor.

### Internal links — all verified

The 8 links in "Related Reading" all resolve against the provided slug list. No broken links in the body either (there are none — consider adding 1–2 inline, e.g. linking `[DAX variables best practices](/tutorials/dax-variables-best-practices/)` in the Practical Fixes section where variables are mentioned).

**However:** `/tutorials/power-bi-performance-analyzer-guide/` already exists and is linked at the **top** of Related Reading. Two articles on the same topic, with this one positioned as the "advanced" version, is fine *only if*:
- The existing guide is updated to link here as the deep-dive, and
- This article's intro explicitly differentiates ("This is the read-the-numbers companion to the [Performance Analyzer guide]").

Without that, this is keyword cannibalization.

### FAQ / format

- Q&A format is consistent and matches the pattern the "1k UV/day" goal usually wants (schema-friendly).
- Consider adding a title line above the first Q (some sites want `## FAQ` alone; others want a lead-in). Currently fine.
- *"You cannot run Performance Analyzer in the browser"* — correct.
- *"the issue is likely gateway, capacity, or a different dataset version"* — misleading. Gateway and capacity are not the same class of problem, and "different dataset version" is vague. Either expand to three sentences or cut the list.
- *"Above 500 ms is when users start to notice, and above 1 second you should treat it as a bug"* — the second clause is subjective and hard to defend. Soften to "above 1 second warrants investigation".

### Factual claim worth checking

- *"Ten visuals on a page mean ten queries fired in parallel; the page waits for the slowest."* — Power BI issues one query per visual in most cases, but the parallelism and count can be affected by caching, visuals sharing a query, and the query limit per page (which is a real, documented constraint). The number "ten" → "ten" is fine; the assumption of *parallel* firing is not universally true. Reword: "each visual generates its own query, and the page completes when the last one finishes."

---

**VERDICT: PUBLISH-AFTER-FIX** — most urgent: (1) resolve cannibalization with `/tutorials/power-bi-performance-analyzer-guide/`, (2) correct the "calculated columns cannot be compressed" claim, (3) fix the category to performance, (4) confirm the future pubDate, (5) trim the em-dash/filler tells in the opening two sections.