# Review: copy-conditional-formatting

# Review: `copy-conditional-formatting`

## 1. AI-isms

The draft is mostly clean, but several tells stand out.

- **Vague, throat-clearing opener.** "Conditional formatting in Power BI is stored per visual, per field, per formatting property." is fine as a hook, but the second paragraph starts with "The good news is that there are four practical ways..." — that's textbook ChatGPT scaffolding. Rewrite: *"Four methods move a rule between visuals, ordered below by how much work they save."*

- **Mechanical ordinal structuring.** "Method 1 / Method 2 / Method 3 / Method 4" is consistent (good), but the prose inside repeatedly announces itself: "The fastest method, and the one most people miss, is...", "The reliable, repeatable method is...", "This is really Method 1 with a positional twist." Cut the meta-commentary. Let the steps stand.

- **"The catch is...", "The trade-off is...", "Where people go wrong is..."** — three instances of the same rhetorical crutch. Vary or delete.

- **"That is the core reason copying conditional formatting is awkward."** / **"That is a strong argument for..."** / **"which is the main argument for..."** — you make the same "argument for a measure" point at least four times. Pick one place (Method 2) and trust the reader.

- **Em-dash abuse.** You use em-dashes correctly (no spaces, no overuse), but "— except / — because / — but" appears five times. Convert two to commas or full stops.

- **"It is tedious but deterministic."** Fine. **"which is really Method 1 with a positional twist."** Cut. **"gets you to a state where adding a new visual is a two-minute job"** — the specific "two-minute" number is unverifiable filler.

- **"This does not copy conditional formatting rules directly, because a theme has no concept of a per-field rule, but it does handle the surrounding styling so that only the rule itself needs recreating."** — 36-word sentence, reads machine-generated. Split.

- **FAQ openers all start with the question echoed as "Q:".** Fine format, but answers all open with a one-word verdict ("Not directly.", "Because...", "No.", "A card..."). Three is a pattern, five is a tic. Vary at least one into a full sentence.

## 2. Topic fit

**Rankability: good.** `copy conditional formatting power bi` is a genuine long-tail with clear intent and thin SERP coverage. The slug and title match the query cleanly.

**Goal fit (1k organic UV/day): borderline.** This is a narrow utility query. Realistic ceiling is probably 200–600 UV/day unless it ranks #1–3 and captures featured-snippet territory. To push toward the goal:

- The title is question-shaped but not literally a question. Consider: *"How to Copy Conditional Formatting Between Visuals in Power BI (4 Methods)"* — matches "how to copy" queries directly.
- Add a **methods comparison table near the top**, not just at the end. Readers bounce if they have to scroll to find "which method."
- The **"Copying rules to other report pages and files"** section is the strongest differentiator vs. the existing `/copy-conditional-formatting-power-bi/` slug — but it's buried. Either promote it earlier or split it into its own article later.

**Better angle:** You already have `/conditional-formatting-based-on-measure/` and `/copy-conditional-formatting-power-bi/`. This draft overlaps both. To avoid cannibalization, reframe this piece as **"between visuals"** specifically (which the title does), and prune re-explanations of the measure pattern that belong in the other slug. Right now Method 2 duplicates ~60% of the measure article.

**Slug risk:** Two slugs (`copy-conditional-formatting` and `copy-conditional-formatting-power-bi`) targeting the same intent. Decide which is canonical and 301 the other, or this will self-cannibalize.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-09-30` is in the future relative to a normal publication cadence. Confirm intentional or fix.
- `author: Mireia` — verify this is a real author slug used elsewhere.
- `description` is a truncated sentence: *"Conditional formatting in Power BI is stored per visual, per field, per formatting property."* It's a statement, not a description of the article. Rewrite to describe the tutorial (what the reader will learn + outcome).
- `category: visualization` — confirm this matches your site's category taxonomy (some sites use `visualizations` or `formatting`).

**Internal links — all verified against provided slugs:**
- ✅ `/tutorials/power-bi-dashboard-design-principles/`
- ✅ `/tutorials/conditional-formatting-based-on-measure/`
- ✅ `/tutorials/conditional-formatting-power-bi/`
- ✅ `/tutorials/bar-chart-conditional-formatting/`
- ✅ `/tutorials/conditional-formatting-charts-power-bi/`
- ✅ `/tutorials/copy-conditional-formatting-power-bi/`
- ✅ `/tutorials/dax-switch-function/`
- ✅ `/tutorials/dax-variables-best-practices/`

No broken links. **But** — you link to `/copy-conditional-formatting-power-bi/` as "Related Reading." If that slug is the canonical version of this topic, this article shouldn't exist; if this is the canonical, link the other as a redirect target or delete it. Decide now.

**Missing link opportunities** (slugs exist, article would benefit):
- `/tutorials/power-bi-dax-optimization/` in the measure section (colour measures iterate row-by-row — perf note is warranted).
- `/tutorials/dax-variables-guide/` where you first introduce `VAR` in the `ProfitMarginColor` measure.

**Terminology / code**
- **"Fields well"** — Power BI UI calls these **"Values"**, **"Axis"**, **"Legend"** buckets. There is no "Fields well" label. Fix.
- **`Ctrl+Shift+V`** duplicates a visual? In Desktop, `Ctrl+C` / `Ctrl+V` duplicates; `Ctrl+Shift+V` is not a standard "duplicate next to original" shortcut. **Verify before publishing** — this reads as invented.
- **`ISBLANK ( MarginPct ), "#FFFFFF"`** returns white for blanks. On a white background, blank rows will look *unformatted* rather than *flagged*. Consider `BLANK()` return (no fill) or a neutral grey, and note the choice.
- **`MarginPct < 0.10`** after `MarginPct < 0` — fine, but the comment "yellow" vs. code "#FFEB84" should match; readers will check.
- **"named CSS colours such as `"red"`"** — Power BI supports a subset of hex and named colours, but the safe, documented set is hex + RGB. Recommend dropping the named-colour claim or linking to the official supported list.
- **"*Rules* style holds hard-coded thresholds that will not follow a slicer"** — technically misleading. Rules-style *does* respect filter context of the field it evaluates, but thresholds are static. Reword: *"thresholds are fixed in the dialog and do not change with data."*
- **"a `SWITCH` returning `"1"`, `"2"`, `"3"` will silently render nothing"** — it will render *something*, typically a solid default or black, not "silently nothing." Confirm behaviour and correct.

**Format**
- **FAQ length:** five questions, each 2–4 sentences. Good. But the FAQ partially duplicates the Common Pitfalls section above it. Merge two of the weaker Q&As into pitfalls, keep three FAQs.
- **Heading hierarchy:** H2 for main sections, H3 for FAQ questions (you used H3 for FAQ `###` — good, but "## FAQ" as H2 is consistent).
- **Table in "Which method to pick"** — the "Best method" column entries reference "Method 1", "Method 2" etc. without repetition. Fine as-is since methods are number-anchored.
- **`## Related Reading`** — inconsistent capitalization with other headings (Title Case vs. Sentence case elsewhere). Match your style.

**Factual claims to verify before publish**
1. Column-bound rules "break when you remove that column" — behaviour varies by visual type; verify on a matrix and a card.
2. `Ctrl+Shift+V` duplicate behaviour.
3. Rules-style respect of filter context.

---

**VERDICT: PUBLISH-AFTER-FIX**

Fix the future pubDate, rewrite the description, verify or cut the `Ctrl+Shift+V` claim and the "Fields well" terminology, resolve the canonical-slug overlap with `/copy-conditional-formatting-power-bi/`, and relocate the cross-file section higher. Content is otherwise rankable and useful.