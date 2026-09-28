# Review: conditional-formatting-based-on-measure

# Review: `conditional-formatting-based-on-measure`

## 1. AI-isms

**Vague opener / throat-clearing**
- The opening paragraph ("splits into two worlds… the simple one… the more useful one") is the classic ChatGPT "binary framing" hook. It's not terrible, but it's padded. Rewrite tighter:
  > *Conditional formatting in Power BI accepts a numeric field, a set of rules, or a color returned by a measure. Only the third option lets you color a cell by margin, variance to target, rank, or year-over-year change. This tutorial covers all three, in the order you'll actually need them.*

**Mechanical transitions / filler**
- "Before touching the format pane, understand the contract." — "contract" is a LinkedIn-word. Say "understand what Power BI expects."
- "That third option is the most powerful and the least used." — pure AI-signposting. Cut or replace with a concrete fact (e.g., "Field value is the only style that accepts a text result").
- "A nuance that trips people up" / "There is one more subtlety worth internalizing" / "Most failures fall into four buckets" — three different versions of the same tic. Keep one, delete the rest. Prefer concrete verbs: "Two things go wrong here often:".
- "Two details matter." — same formula. Just state the two things.
- "That is almost always what you want, and it is precisely why…" — "precisely why" is a ChatGPT tell. Use "which is why."

**Hedging cadence**
- "is fine and cheaper" / "is fine for continuous values" / "a column is fine" — three "fine"s. Vary or cut.

**Em-dash abuse**
- The article has at least a dozen em-dashes, several used as false drama: "It costs more and requires you to think in filter context." is fine, but "For anything dynamic — top N, above/below average, variance to target — use a measure" could just be a comma list. Reduce by ~60%; keep them only where they substitute for a genuine parenthetical.

**FAQ phrasing**
- Opening every question with "Can I…" or "Why is…" is fine, but the answers open with "Yes." / "Yes, but…" / "Yes…" in three of five. Vary structure and lead with the substantive answer.

**Figure placeholders**
- "![Figure 1: …](placeholder)" — five of them. If images aren't produced yet, that's a publication blocker, not an AI-ism, but it should be flagged. If they are placeholders in the draft pipeline, note it for the editor, don't ship.

Net: the prose is competent but reads like a produced-by-LLM first draft. It needs a human pass to remove the signposting and tighten topic sentences. Roughly a 20–25% word cut is achievable without losing information.

## 2. Topic fit

**Long-tail rankability: yes, mostly.**
- "conditional formatting based on a measure" is a real search phrase with clear intent. The slug is clean.
- The FAQ already targets adjacent long-tails ("conditional formatting greyed out", "measure missing from formatting dropdown", "row level security conditional formatting"). Good.
- But the article tries to be too many things: gradient, rules, field value, charts, debugging, column-vs-measure comparison, and five FAQs. That breadth dilutes topical focus. Google may not know whether this is the *field value* page, the *gradient* page, or the *troubleshooting* page.

**Serving the 1k UV/day goal:**
Realistic. `conditional-formatting-power-bi` (the parent) likely already carries the volume. This page's job is to capture the *long-tail* modifiers:
- "conditional formatting by measure"
- "conditional formatting field value DAX"
- "conditional formatting not working power bi"
- "power bi conditional formatting hex color"

The article touches all of these, but the H2s don't front-load the search phrase. Consider renaming:
- "Returning a color from DAX" → "Field value conditional formatting: returning a color from DAX"
- "Debugging: when the color does not appear" → "Conditional formatting not working? Debug it in four steps"

**Better angle:**
The differentiator vs. the existing `/tutorials/conditional-formatting-power-bi/` page should be *measure-driven logic*, not a general rehash. The current draft re-explains gradients and rules, which the parent tutorial almost certainly already covers. If the parent covers rules by field, this page could cut the "Rules instead of gradients" section down to three lines and pivot hard into:
- parameterized colors via `SWITCH` (already present, good)
- field parameters for switching the *metric* that drives the color (link to `/tutorials/power-bi-field-parameters/` — currently missing)
- calculation groups / visual calculations for reusable format logic (link to `/tutorials/power-bi-visual-calculations/` — currently missing)

Those adjacent topics are where the long-tail strength lives, and they aren't shown in the "Related Reading" block, which means the internal linking is not doing its job.

**Verdict on fit:** rankable but overlapping with an existing page. Recommend the editor decide: either (a) sharpen this into a strict "field value / measure-returning-color" page and cross-link aggressively to the parent, or (b) merge with the parent. Half-measure won't rank.

## 3. Errors

**Frontmatter**
- `description` is truncated mid-sentence: *"…sales above a threshold turn green, below turn red."* — this reads like a copy of the first body sentence rather than a meta description. Rewrite as a proper 150–160 char summary targeting the search query.
- `pubDate: 2026-09-28` — future date. Confirm it's intentional (scheduled) or correct it. If RSS/templates treat future dates as drafts, this will silently not publish.
- `category: visualization` — verify against the site's category taxonomy. The article is as much DAX as visualization; consider `dax` or `visualization,dax` if the CMS supports it.
- `tags` are thin. Add `dax`, `field value`, `gradient`, maybe `troubleshooting`.
- `featured: false, draft: false` — fine.

**Terminology / technical errors**
1. **"That third option… expects the field to resolve to a color"** — the section title says *"Color by field (format style = Field value)"* and then later text calls it "Field value" inconsistently. The UI label is "Field value"; the punchline in the intro list ("or even a `#RRGGBB` value") is redundant with `"#2E7D32"` earlier. Trim.
2. **`Gross Margin %` example** — `DIVIDE(a, b)` returns `BLANK()` if denominator is blank or zero by default, which is correct, but the article never mentions this when it later says "without that guard, `BLANK() >= 0.35` evaluates to FALSE". `BLANK() >= 0.35` actually evaluates to FALSE in DAX (BLANK behaves as 0 in comparisons with numbers *and* as FALSE in boolean context), so the ISBLANK guard is good practice but the stated rationale is subtly imprecise. Rewrite: *"Without the guard, a blank margin is compared as zero and would fall through to the red branch."*
3. **`Revenue Rank` example** — `RANKX ( ALLSELECTED ( 'Product'[Product Name] ), [Total Revenue] )` — the second argument should be an expression evaluated per row of the first argument's table. This is valid DAX, but the default order is descending, which is what the example wants (top 3 by revenue). Add a one-line note that `RANKX` is descending by default; otherwise readers who expect ascending will be confused.
4. **`ISINSCOPE` claim** — *"`ISINSCOPE` is one of the few functions that inspects the visual's row/column structure rather than the filter context"* — this is not accurate. `ISINSCOPE` checks whether a column is in scope of the current group, which is a context property, not "inspects the visual's structure." The correct frame: it returns TRUE when the specified column is part of the current *group-by* level. Fix.
5. **Rule ordering claim** — "Rules evaluate top to bottom in the order you create them" — the Power BI UI has explicit up/down arrows and rules fire in the listed order, which the user controls, not necessarily creation order. Soften: "Rules fire in the order shown in the list; use the arrows to reorder."
6. **"color by value (gradient)"** vs later "**Format style** to *Gradient*" — the UI calls the option "Gradient" in modern Power BI; "Color by value" is older phrasing. Pick one and stick to it.
7. **`#1565C080` alpha hex** — Power BI's field-value color parser supports `#RRGGBB` and (in recent versions) `#AARRGGBB`, but 8-digit `#RRGGBBAA` (trailing alpha, CSS-style) is **not** reliably accepted. The article claims it is. Verify against your target Power BI version or remove this example. This is the kind of error that generates support tickets in comments.
8. **"you can comment it"** — DAX measures cannot contain comments via the standard measure formula bar in Desktop (you can add `//` in Tabular Editor or in the DAX editor in newer Desktop versions, but the claim as written is misleading for beginners). Reword or cut.

**Internal links — verification**
All nine links in "Related Reading" exist in the supplied slug list:
- ✅ `/tutorials/conditional-formatting-power-bi/`
- ✅ `/tutorials/conditional-formatting-charts-power-bi/`
- ✅ `/tutorials/copy-conditional-formatting-power-bi/`
- ✅ `/tutorials/dax-switch-function/`
- ✅ `/tutorials/filter-context-row-context-explained/`
- ✅ `/tutorials/dax-variables-best-practices/`
- ✅ `/tutorials/dax-rankx-function/`
- ✅ `/tutorials/power-bi-performance-analyzer-guide/`
- ✅ `/tutorials/dax-troubleshooting-guide/`

No broken links. However:
- **Missing opportunities** (real slugs, deliberately not linked, should be):
  - `/tutorials/power-bi-field-parameters/` — where parameterizing the color metric belongs
  - `/tutorials/power-bi-visual-calculations/` — modern alternative to per-cell measures
  - `/tutorials/dax-variables-guide/` or `/tutorials/dax-variables-best-practices/` (only the latter is linked)
  - `/tutorials/power-bi-performance-optimization/` — the per-cell cost warning should link here
  - `/tutorials/power-bi-row-level-security/` — the RLS FAQ should link here
  - `/tutorials/calculated-tables-what-if-parameters/` — tangential but relevant to the column-vs-measure section
- No body links at all. Everything is in the footer block. At least three body links should be inserted inline (filter context → filter-context page; RANKX → RANKX page; performance → optimization page). Google and readers both weight inline links higher.

**FAQ / format**
- Five questions, no `FAQPage` schema hint in the frontmatter — if the CMS generates JSON-LD from an `faq` frontmatter array, this is missed opportunity. Check site convention.
- FAQ answers are long enough to be useful but "Q:" prefixes plus `###` headings is redundant; the site template probably handles the visual Q via the heading alone.
- The FAQ section isn't linked from anywhere in the body. Add a one-line pointer above the debugging section.

**Structural**
- "Choosing between a column and a measure" is the weakest section and reads like the model ran out of things to say. It could be a callout box inside "Writing a measure that returns a number" instead of its own H2.
- No conclusion. The article just stops after FAQ. Either add a two-sentence wrap or delete the "Related Reading" header and let the FAQ stand as the closer. Current state feels truncated.
- Figure alt text is descriptive but repeated five times with placeholder URLs. If images aren't shipping, either remove the figure lines or comment them out; leaving `placeholder` in a live post looks broken to crawlers.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the description frontmatter and pubDate, correct the `#RRGGBBAA` alpha-hex and `ISINSCOPE` claims, cut the AI-isms and the redundant column-vs-measure section, add inline body links plus the four missing internal links, and ensure figures ship with real assets.