# Review: power-bi-incremental-refresh

# Editorial Review: `power-bi-incremental-refresh`

## 1. AI-isms

The draft is generally clean and reads like a practitioner wrote it. A few tics to trim:

| Location | Issue | Rewrite |
|---|---|---|
| Opening: *"Incremental refresh splits a large fact table into two logical halves: the part that never changes… and the part that can change…"* | This **exactly duplicates the frontmatter `description`**. Reads as machine-generated boilerplate. | Open with the operational pain instead: *"A 300-million-row sales table refreshed fully every night will eventually miss its window. Incremental refresh exists to prevent that — it keeps historical data frozen and reloads only a rolling window."* Then introduce the two-halves framing in the second sentence. |
| "The upside is measurable." | Filler transition. | Delete, or fold into the next sentence: *"Full refreshes scale linearly with total data volume; incremental refreshes scale with window size."* |
| "Three things make this work: …" | Borderline mechanical, but acceptable — it's a real list. Keep, but tighten. | Acceptable as-is. |
| "Point 3 catches a lot of people." | Fine, human. Keep. | — |
| "A final note for troubleshooting:" | Slightly ChatGPT-ish run-in. | *"To isolate a failure, refresh a single partition from SSMS with `Process Data`."* |
| Em-dash usage | Low. No abuse detected. | — |
| "**Timezone drift.**" / "**Gateway credentials.**" / etc. | Bolded noun-phrase headers — clean, no problem. | — |

No vague openers ("In today's data-driven world…"), no "Let's dive in", no "It's important to note". Good.

## 2. Topic Fit

**Rankability: strong.** `power-bi-incremental-refresh` is a real long-tail query with commercial intent (Premium customers searching for setup help). Low competition relative to head terms like "power bi refresh". The gotchas section and FAQ are the differentiator — most competing posts stop at "configure RangeStart/RangeEnd".

**Serving the 1k UV/day goal:** plausible but not guaranteed. This is an "Advanced" + "Premium" topic — narrower audience than a chart-formatting tutorial. Expect lower ceiling than your conditional-formatting posts but higher conversion to newsletter/return visits. Two improvements:

1. **Add a "before you start" checklist** near the top (Premium capacity check, XMLA endpoint enabled, gateway configured) so Pro users don't waste time following Steps 1–4 and discover the paywall at Step 5. Currently the capacity caveat is buried at the end of section 1.
2. **Consider splitting off `dax-time-intelligence-incremental-refresh`** as a separate piece. The rolling-30-day DAX snippet is a distinct query ("does incremental refresh break time intelligence?") and would earn its own long-tail rank. Right now it's buried and under-served.
3. **Angle upgrade:** the strongest angle here isn't "how to set up" — it's **"why your incremental refresh silently reloads everything."** That's the actual search phrase. Consider retitling: *"Incremental Refresh in Power BI: Why It Silently Reloads Everything (and How to Verify Partitions)"*. The troubleshooting content is currently subordinated to the setup tutorial.

## 3. Errors

### Frontmatter
- ✅ `pubDate`, `category`, `draft`, `featured` all valid.
- ⚠️ `description` is 190+ chars — check your CMS field limit. Also, it duplicates the first paragraph verbatim; even if under limit, rewrite to avoid the duplicate-content artifact.
- ⚠️ `tags: ["refresh", "performance"]` — consider adding `"premium"` or `"xmla"` since those are the real gating concepts.
- `difficulty: Advanced` — accurate.

### Technical accuracy
- ✅ RangeStart/RangeEnd case sensitivity — correct.
- ✅ UTC boundary evaluation — correct.
- ✅ Pro vs Premium partition drop — correct.
- ✅ `before` / `after` partition naming — correct.
- ⚠️ **"Partition pruning happens at the storage engine level, so the query touches only the needed partitions."** — This is stated too confidently. Partition pruning only happens if the measure's filter context aligns with the partition key. In the rolling-30-day example, if `MaxDate` lands inside the refresh window, yes; but a report showing two-year-old data still scans the historical partitions. Rephrase: *"The storage engine can prune partitions when the query's date range maps onto partition boundaries."*
- ⚠️ **SQL Server Management Studio connection string** — you say `connected to the XMLA endpoint`, but SSMS needs to be launched with `/dax` or via the "Analysis Services" connection type with a `<WorkspaceName>` URL in the format you gave. Fine as-is for readers who know, but add: *"use the Analysis Services connection type in SSMS"*.
- ⚠️ **"Detect data changes"** — accurate, but you should mention it requires the source column to be a `datetime` and that it adds a query per partition; you do say the second part. The date-type requirement is missing.
- ⚠️ **`DATESYTD` / `DATEADD`** — correct, but note these need `Mark as Date Table` set; you do say this. Good.

### Power Query code
- ⚠️ The parameter block uses `#datetime(...) meta [ IsParameterQuery = true, ... ]`. Parameters created via the UI use `#datetime` for current value but the `meta` record with `IsParameterQueryRequired` is set by the UI editor, not usually hand-authored. This looks like syntax a reader copying into the Advanced Editor will get wrong. **Recommend rewriting the block as plain instructions** ("create two parameters in the UI, set type to Date/Time, leave current value at any date") and drop the pseudo-M. The second code block (the `Table.SelectRows` filter) is the one readers actually need.
- ✅ Filter with `>= RangeStart and < RangeEnd` — correct.
- ✅ `Table.SelectRows` placement guidance (put as late as possible) — correct.

### DAX snippet
- ✅ `MAX ( 'Date'[Date] )`, `VAR`, `CALCULATE` filter — syntactically correct.
- ⚠️ `MAX` on a Date column will fail if the date table has blanks; trivial, not worth flagging in-body.

### FAQ
- ✅ Four questions, all real, all answered without padding.
- ⚠️ The first FAQ *"Why is my incremental refresh reloading the entire table?"* answers the same question as the "Gotchas" section. Consider merging, or at least internally linking: "see Gotchas above". Currently reads duplicated.
- ⚠️ *"Dataflows Gen1 and Gen2 both support incremental refresh"* — Gen1 supports it in Premium only; Gen2 supports it more broadly. Add the qualifier.

### Internal links
All eight slugs verified against the real slugs list:
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/dax-optimization-techniques/` ✅
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/power-bi-date-table/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅
- `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` ✅

**No broken links.** Consider adding one more: `/tutorials/power-bi-drill-through/` is not relevant, but `/tutorials/calculated-tables-what-if-parameters/` is not relevant either. No obvious additions from the list.

### Formatting
- ✅ Headings consistent.
- ✅ Code fences have language tags (`powerquery`, `dax`).
- ⚠️ Two H2 sections ("What Incremental Refresh Actually Does", the four "Step N" sections, "Gotchas", "Related Reading") — but the FAQ uses H3s without a parent H2. Wrap them in `## Frequently Asked Questions` for clean TOC generation.
- ⚠️ The intro paragraph after `## What Incremental Refresh Actually Does` is the same as the description — the duplicate is more jarring when the reader sees it twice above the fold.

---

**VERDICT: PUBLISH-AFTER-FIX** — rewrite the frontmatter description (currently duplicates the opening para verbatim), relocate the capacity caveat higher, replace the `meta [ IsParameterQuery = … ]` M block with UI instructions, soften the "partition pruning happens at storage-engine level" claim, wrap the FAQ in an H2, and merge or cross-reference the duplicated first FAQ against the Gotchas section. All internal links verified real. No AI-isms beyond the description/opening duplication.