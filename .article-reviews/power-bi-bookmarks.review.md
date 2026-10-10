# Review: power-bi-bookmarks

# Review: `power-bi-bookmarks`

## 1. AI-isms

Several tics present. Specifics:

- **Mechanical two-sided framing.** "Two consequences follow from this. First… Second…" — formulaic. Rewrite: "Bookmarks are cheap to create, so dozens won't hurt model performance. But they carry no data, so they aren't a substitute for a calculated table of precomputed scenarios."
- **Enumerated "gotcha" scaffolding.** "There is one gotcha worth knowing… A second gotcha…" and "The common misconception is…" / "The technical catch is…" — these hedges appear five times. Cut at least three; keep the ones that carry real weight.
- **Vague authority openers.** "In practice this means…", "The nuance: …", "Practical rule: …", "For most internal reports, …" — pick one per section, not per paragraph.
- **"here is a workflow you can repeat on almost any report"** — filler. Just present it: "Build a Trend/Detail/KPI switcher:"
- **Em-dash abuse.** Not severe here (a few in mid-sentence clauses), but tighten: e.g. "That state includes the visibility of visuals, the active filters in slicers and filter cards (if you tell it to), the sort order…" is fine; the "That is often what you want for a 'toggle view' bookmark and almost never what you want for a 'reset filters' bookmark." construction is acceptable but occurs repeatedly with the same rhythm. Vary sentence length.
- **"The reason this works reliably is that…"** — explanatory throat-clearing. State the rule directly: "Using the Selection pane (not the visual header's eye icon) keeps a stable name per visual."
- **Closing listicles** ("If stability matters more than novelty…", "Your buttons act as hard overrides; the reader's personal bookmarks act as soft overrides") — the second is genuinely useful, the first is decorative.

No hallucinated "in today's fast-paced world" openers, and no ChatGPT signature phrases like "delve" or "landscape." Baseline is decent; the mechanical transitions and the repeated "common misconception / technical catch / nuance / practical rule / gotcha" pattern are the main tell.

## 2. Topic Fit

**Long-tail rankability:** Moderate. "Power BI bookmarks" is a competitive head term, not long-tail. But the article covers underserved sub-intents well: bookmark + drill state fragility, bookmark + field parameter comparison, bookmark + disconnected table for measure switching, personal bookmarks in the service. Those FAQ-style queries ("power bi bookmark not restoring slicer", "power bi bookmark vs field parameter", "power bi bookmark with switch measure") are plausibly rankable and map to real search behavior.

**Serving the 1k UV/day goal:** As a single page, weak on the head term; could work combined with FAQ snippets. The five FAQ questions are the highest-leverage real estate — they're each a plausible featured-snippet or People-Also-Ask target.

**Better angles / gaps:**
- The title promises "Build Interactive Reports" but the article is closer to a reference on bookmark mechanics. Consider either renaming ("Power BI Bookmarks: State, Filters, and Drill (With Examples)") or adding a single end-to-end build with screenshots described in prose — currently step 4 ("Duplicate the current state by copying the page or by saving three bookmarks before changing anything") is vague and the walkthrough doesn't actually duplicate anything reusable.
- No mention of **bookmark loops/cycles** or the classic "bookmark + Play axis" pattern — both are searched.
- No mention of **Bookmarks Navigator** visual (Preview/GA in newer versions) — visible in SERPs.
- No mention of **Selection pane grouping** of visuals for bulk visibility toggles, which is the actual mechanism most tutorials rely on.
- The "Personal bookmarks" section claims `File > Options and settings > Report settings` disables personalization — the actual toggle is under **File > Options and settings > Options > Report settings** and is named for "Personalize visuals" / bookmark personalization; verify against current UI. If the path is wrong, that's an error, not just an angle gap.

Overall the topic fits the site's tutorial cluster (drill-through, field parameters, bookmarks-navigation all exist), so it's a reasonable addition. It's not going to move 1k UV/day on its own.

## 3. Errors

**Frontmatter:**
- `pubDate: 2026-10-10` — future date relative to typical publication. If the site is not scheduled-publishing aware, this is a bug. Confirm intent.
- `author: Mireia` — no other articles in the sample reference this author; verify the byline exists in `authors` config.
- `category: visualization` — bookmarks are arguably `interactivity` or `features`, not `visualization`. Check the category taxonomy.
- Missing `updatedDate` if the site uses it.

**Terminology / code:**
- "current selection in any visual that uses the *Selection pane*" — visuals don't "use" the Selection pane; the pane lists visuals on the page. Rewrite: "the state of the Selection pane (which visuals are visible and their z-order)."
- "Bookmarks read state from *report-level* and *visual-level* filters" — also page-level filters, which are the most commonly bookmarked. Add page-level.
- The claim that Data captures "the current page" is wrong — **Current page** is its own checkbox; Data does *not* capture the page. The table row for "Current page" correctly lists it, but the prose later ("Check **Data** and **Display**") implies Data+Display is sufficient to restore the page. It isn't; add **Current page** for buttons that also navigate.
- "Ctrl+click in the Power BI service" — in the *service*, a bookmark action triggers on single click; in Desktop, Ctrl+click is needed to fire the action without entering edit mode. Clarify which context each applies to.
- `SELECTEDVALUE ( ViewMode[Mode], "Absolute" )` — correct. However the follow-up claim "Without a default, the code would fall through to `SWITCH`'s else branch and show raw sales anyway" is correct but omits that `SELECTEDVALUE` returns BLANK which is technically not the else branch in `SWITCH` unless no match — BLANK matches no string, so it *does* fall to else. Statement is fine but slightly muddled; simplify.
- Dynamic format strings: "changing the bookmark's slicer value will change the format only after recalculation on the next render" — misleading. Format strings recompute on the same render as the value; there is no "next render" lag. This is likely wrong. Either remove or verify.
- "bookmarks do not capture dynamic format strings" — bookmarks don't need to; format strings are measure-driven, not state. The paragraph conflates two things and should be rewritten or cut.
- "If someone deletes a member referenced by the drilled row, the restore can show an expanded-but-empty row." — Plausible but unverified. Better to show the actual behavior (drill state falls back to top level, or the visual errors) or drop the claim.
- The What If / calculated table reference says "you need a disconnected table or a What If parameter" — accurate, but linked article is `/tutorials/calculated-tables-what-if-parameters/`, which exists. Fine.

**Internal links — all present in the allowed set:**
- `/tutorials/bookmarks-navigation-power-bi/` ✅
- `/tutorials/power-bi-drill-through/` ✅
- `/tutorials/power-bi-field-parameters/` ✅
- `/tutorials/calculated-tables-what-if-parameters/` ✅
- `/tutorials/dax-switch-function/` ✅
- `/tutorials/power-bi-dashboard-design-principles/` ✅
- `/tutorials/measure-vs-calculated-column/` ✅

No broken links. But: none of the internal links appear **inline** in the body — they're all in a trailing "Related Reading" block. Given the slugs available, there are missed opportunities to inline-link `bookmarks-navigation-power-bi`, `power-bi-field-parameters`, and `dax-switch-function` in their respective sections. That's an SEO/UX miss, not an error.

**FAQ:**
- FAQ block is not marked up as FAQ schema frontmatter or wrapped in any structured heading convention (it uses `### Q:` style, which is fine for rendering but not for FAQPage JSON-LD). If the site supports FAQ frontmatter, add it; otherwise note it.
- FAQ answers are solid and specific. The "How many bookmarks" question has no authoritative source for "around 20" — that's a made-up usability threshold. Either attribute it as a rule of thumb (fine) or cite community consensus.

**Format:**
- The `| Option | What it records |` table's "Data" row says "Filter/slicer selections, drill state" — correct. "Display" row says "Visual visibility, focus mode, the current page" — **incorrect**, current page belongs to its own checkbox. Fix.
- Headings are inconsistent in depth usage — H2s and one H3 (Q&A) — acceptable but the "Related Reading" H2 wraps a bullet list of links that should probably use the site's related-content component if one exists.
- No alt/caption text on what should obviously be a visual walkthrough. If the site supports images, this article needs at least 3 (Bookmarks pane context menu, Selection pane renamed visuals, button action config).

**VERDICT: PUBLISH-AFTER-FIX** (fix Data/Current-page table row, remove or verify the dynamic-format-strings paragraph, verify the personal-bookmark disable path, correct pubDate, inline 2–3 internal links, trim the repeated "gotcha" scaffolding).