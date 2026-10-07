# Review: power-query-from-excel

# Review: `power-query-from-excel`

## 1. AI-isms

**Filler openers disguised as substance.**
- "Excel remains the most common starting point for Power BI projects. Most analysts have data sitting in `.xlsx` files…" — The second sentence is throat-clearing. **Rewrite:** "Excel files are the most common Power BI source. Power Query is the engine that cleans them — same engine in Desktop, Excel's Get & Transform, and Dataflows."
- "It stays at beginner level, but the details matter, so the steps are explicit." — Self-referential meta commentary. Cut entirely, or replace with one concrete promise: "The steps below assume no prior M experience."

**Mechanical transitions / list-then-restate pattern.**
- The "Repeatability / Auditability / Reusability" bullet list is fine, but the trailing paragraph "The trade-off is that Power Query operates on a load step, not on live cells" reads like the model reflexively balancing every positive list. Keep it — but it's already covered again in the FAQ ("Can I edit the original Excel file while Power BI is open?"). Pick one location.
- "A few notes on the code above, since the shape is what causes most beginner friction." — "since the shape is what causes most beginner friction" is vague hedging. **Rewrite:** "Why each step matters:"

**Em-dash / colon tic.**
- "the choice is really import vs reading the workbook through a gateway" — missing em dash, actually fine. But the article leans on the connective "which is why…" three times ("which is why the second step drills", "which is what a star schema wants", "which is what"). Vary.
- "The generated query after connecting will look close to this:" — "look close to this" is waffle. **Rewrite:** "The generated query looks like this:"

**Hedging adverbs.**
- "The distinction matters more than most beginners expect." — cut, or replace with the concrete consequence (you *do* cover it in the next sentence, so the sentence is pure padding).
- "which is a feature, not a bug" — a cliché. **Rewrite:** "That failure tells you the source shape changed — usually what you want."

**FAQ answers that start by restating the question.** All five do. E.g. "Why does the file path in Power Query break after I move the workbook?" → "`File.Contents` stores an absolute path." Fine — actually this one is OK. Check the others: "Can I edit the original Excel file while Power BI is open? Yes, but…" is acceptable. The bigger offender is **"What happens if a column name changes…"** which opens with "The step that references the old name fails" — good, keep.

Net: AI-ism density is moderate. No "in today's data-driven world" or "delve" or "landscape". Mostly filler sentences around paragraph openings.

---

## 2. Topic fit

**Long-tail rankable?** Yes — `power-query-from-excel` is a solid long-tail with clear intent (how-to for a beginner). Good candidate to rank for queries like "power query import excel", "power query excel table vs worksheet", "connect power bi to excel file".

**Serves the 1k real organic UV/day goal?** Maybe, but this article is competing against Microsoft Learn, Enterprise DNA, Guy in a Cube, and a hundred blog posts on the exact same topic. It is a *commodity* keyword. To hit 1k/day on this slug alone, you need either (a) an unusually specific angle, or (b) it to sit inside a cluster that already ranks.

**What this article does well that competitors don't:** the Table vs Worksheet vs Named Range table, the "renaming the table in Excel breaks the step — that's a feature" framing, and the `Record.FieldValues` blank-row trick. Those are the differentiators.

**Better angle options:**
1. **Narrow to "Excel Table vs Worksheet in Power Query — which should you pick?"** — much lower competition, higher intent, easier to rank. Could be a sibling article that internal-links here.
2. **Add a troubleshooting section** ("Query didn't pick up my changes", "Privacy level blocked a combine", "credentials prompt loops on refresh"). These long-tail error queries are where the traffic actually is.
3. **Concrete before/after example with data** — you describe an example, but no actual output table. A single screenshot paragraph of the final shape would lift engagement and dwell time.

Current angle is fine for a hub page. Expect it to rank slowly, not spike.

---

## 3. Errors

**Frontmatter / metadata**
- `pubDate: 2026-10-07` is in the future. If this is a scheduled post, fine — but confirm the pipeline supports it. If not, it will display wrong or not publish.
- `description` is a fragment, not a description: *"Excel remains the most common starting point for Power BI projects."* — that's the opening line, not a meta description. **Fix:** something like *"Connect, clean, and load Excel data into Power BI with Power Query — tables vs worksheets, transformations, parameters, and refresh troubleshooting."*
- `tags: ["excel", "power query"]` — fine, but consider `["excel", "power query", "import"]` for discoverability.
- `author: Mireia` — no surname. Check house style.

**Code / terminology**
- `Excel.Workbook(File.Contents("C:\Data\SalesData.xlsx"), null, true)` — the third argument `true` is `useHeaders`. Correct in current builds but worth a one-line comment, since it is the source of many "my headers didn't promote" complaints. Also the second arg (delayTypes) being `null` is legacy; current signature accepts it, so OK.
- `Table.SelectRows(CleanedRegion, each not List.IsEmpty(List.RemoveMatchingItems(Record.FieldValues(_), {"", null})))` — this does not do what the surrounding sentence claims. The sentence says it "drop[s] rows where every field is empty." `List.RemoveMatchingItems` removes `""` and `null` values from the list of field values, then `List.IsEmpty` is true only if *every* field was `""` or `null`. So the logic is correct — but `Record.FieldValues` may include non-text types (numbers, dates) that are not matched by `{"", null}`, which is fine. **The real issue:** if a row has one column with `0` or a whitespace `" "`, it survives. Whitespace-only rows will not be dropped. Worth flagging as a limitation, or change the example to use a key column and note the caveat you already give.
- `CleanedRegion = Table.TransformColumns(..., {{"Region", each Text.Proper(Text.Trim(_))}})` — say it "Normalises the region". `Text.Proper` on `"NORTH"` gives `"North"`; on `"north "` gives `"North"`. Correct. But `Text.Proper` also title-cases hyphenated/compound names oddly (`"new-york"` → `"New-York"`), which is a known gotcha. Consider a one-liner.
- `"tblSales" wasn't found` — the actual Power Query error message is closer to `The name 'tblSales' wasn't recognized` or `Expression.Error: The field 'tblSales' of the record wasn't found.` Quote the real one or hedge ("an error naming the missing table").
- *"Data > Get data > Excel workbook on the ribbon if the Home tab is collapsed"* — the Home tab cannot be "collapsed" in Desktop in a way that moves Get data to a Data tab. **Rewrite:** "Home > Get data > Excel workbook."
- *"Get data > Folder"* — correct path is **Home > Get data > More > Folder** in Desktop. As written it implies a direct Folder button.
- *"Home > Manage Parameters > New Parameter"* — correct is **Home > Manage Parameters > New Parameter** in Power Query Editor; from the Desktop ribbon it's **Transform data > Manage Parameters**. As written is fine if you're inside the editor — but the surrounding text moves between Desktop and editor. Disambiguate.
- *"Close & Apply > Connection only from the dropdown next to Close & Apply"* — the *Connection only* option is inside the **Close & Apply** dropdown, correct. But wording is confusing; rewrite: "**Close & Apply** dropdown > **Close & Apply To…** > check **Connection only**." (Or in modern Desktop: **Home > Close & Apply > Close & Apply To…**.)
- *"File > Options > Current File > Privacy"* — correct.
- *"Combine data according to your Privacy Level settings for each source"* — matches the actual UI string. Good.
- *"DirectQuery against Excel is not supported"* — correct.
- *"Excel Online files refreshed through the Service can also use `Web.Contents` against the workbook URL"* — misleading. For SharePoint/OneDrive for Business, use **SharePoint.Files** or **SharePoint.Tables**; `Web.Contents` against an xlsx URL generally returns binary that you'd feed to `Excel.Workbook`, and it's not the recommended path. **Fix or remove.**
- `type number` for `UnitPrice` — fine, but note that if the column truly contains `"$12.50"` text, `Table.TransformColumnTypes` to `type number` will throw a conversion error, not silently fix it. The article says "sometimes arrives as text because of a stray currency symbol" and then applies a number cast with no error handling. **This is a real gap.** Add: either `Text.Replace` the `$` before casting, or use `Table.TransformColumns` with `try ... otherwise null`. As written, a reader following the example will hit conversion errors.

**Broken / imagined internal links**
All eight "Related Reading" links resolve against the supplied slug list:
- `/tutorials/power-bi-excel-integration/` ✅
- `/tutorials/merge-vs-append-queries/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅
- `/tutorials/dax-basics/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/dax-earlier-function/` ✅

**Missing internal-link opportunities** (slugs exist, article mentions the concepts in prose but doesn't link):
- "star schema wants downstairs" → should link `/tutorials/data-modeling-star-schema/` inline (only in Related Reading now).
- "Group and aggregate" → mention of pre-aggregation vs DAX could link `/tutorials/dax-optimization-techniques/` or `/tutorials/power-bi-performance-analyzer/`.
- "DirectQuery vs import mode article" — in prose, unlinked. Link it.

**FAQ format**
- H3 questions in FAQ are fine.
- Marked as `### Q:` — inconsistent with likely house style. Check whether the site uses `Q:` prefix or plain question text. If plain, drop the `Q:`.
- No `FAQPage` schema note — check whether the head/frontmatter needs a flag.
- One FAQ answer (**Power Query in Excel vs Power BI**) has factual slack: "The engine is the same M language" — the engines are *the same codebase family* but versioned differently and feature-flagged differently. Excel's PQ lags Power BI's. **Rewrite:** "The M language is the same, and most steps are identical, but Excel's Power Query tends to lag Power BI's in features."

**Structural**
- Article opens twice: title context paragraph, then "Why Power Query beats copying and pasting". The second H2 restates the first paragraph's argument. Trim the intro paragraph so it doesn't step on the H2.
- Two H2s on the same topic (*Connecting to a workbook* and *A worked example*) with no transition to signal they are sequential. Fine, but the "worked example" H2 should probably be a sub-section of connecting.

---

**VERDICT: PUBLISH-AFTER-FIX**

Priority fixes: (1) the `UnitPrice` type-cast example will fail for readers as written — add `Text.Replace` or error handling; (2) rewrite the meta `description`; (3) fix the *SharePoint Folder / Web.Contents* claim in the first FAQ; (4) trim the AI-ism filler sentences in the opening and the "A few notes on the code above" transition; (5) confirm `pubDate: 2026-10-07` is intentional.