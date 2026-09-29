# Review: line-chart-conditional-formatting

# Review: `line-chart-conditional-formatting`

## 1. AI-isms

The draft is cleaner than most AI-generated drafts, but several tells remain.

- **Vague "The important nuance" / "The last point matters" scaffolding.** These are filler transitions that announce importance instead of demonstrating it.
  - Rewrite: "The important nuance: a line needs at least one point per category to carry a color." → **"A line only carries a color where it has a point. If markers are off and your rule colors points, nothing appears to change."**
  - Rewrite: "The last point matters. A calculated column is evaluated once at refresh..." → Delete "The last point matters." and open directly: **"Use a measure, not a calculated column. A calculated column is evaluated once at refresh and stored..."**

- **"That is usually the correct behavior, but verify it rather than assuming."** Classic LLM hedge — restates the obvious without adding information. Cut it, or replace with a concrete instruction: "Test with a mixed-legend product and one without."

- **"Check three things."** followed by "First... Second... Third..." — mechanical enumeration. Fine in a FAQ but reads templated here. Rewrite as prose or a short bullet list without the ordinal markers.

- **Triadic "X is A, Y is B, and Z is C" opener.** "A line chart in Power BI is built from a category axis, a value axis, and one or more series." This exact sentence is in the `description` frontmatter too, which is the giveaway — the description was lifted from the body. Rewrite the description to a benefit or search-intent line: *"How to color line chart points and series in Power BI with measures, rules, and field values — plus the pitfalls that make rules silently fail."*

- **Em-dash abuse.** Five em-dashes across the article, mostly in the same "statement — elaboration" pattern. Two is fine; five is a tic. Convert two of them to colons or parentheses. The FAQ answer "Not directly. Power BI colors points, not segments between points." is stronger without the following em-dash constructions.

- **"Reach for X, not Y."** Mild LLM idiom. Fine once; the article uses it once, so leave it.

- **"For the running example, choose..."** "Running example" is jargon-y LLM shortcut. Just say "Choose **Field value** and select `Revenue Color`."

- **Placeholder alt text.** All five images have `![Figure N: ...](placeholder)`. That's fine as a draft marker, but the alt text is doing the caption's job. Once figures are dropped in, replace with descriptive alt per image, not "Figure N."

## 2. Topic fit

**Rankability.** "Line chart conditional formatting" is a real long-tail query with low competition — most competitors stop at tables and matrices. The article's core insight (line charts color *points*, not the whole line, and markers must be on) is a genuinely underserved angle. Good target.

**Does it serve the 1k UV/day goal?** On its own, no — this is a 200–400 UV/month page at best. But it's a strong *support* page if it links up to the pillar (`/tutorials/conditional-formatting-power-bi/`) and captures the query variants ("power bi line chart color by value", "power bi line chart color by measure", "power bi line chart conditional formatting not working"). The current title targets only one variant.

**Better angle.** The strongest untapped intent in this space is the *bug* query: **"power bi line chart conditional formatting not working."** That's what people actually search when they hit the markers-off gotcha. Consider splitting or retitling:

- Option A (safer): Keep the title, but add an H2 "Why conditional formatting doesn't work on a line chart" near the top — this captures the debug query without sacrificing the tutorial intent.
- Option B: Two pages. This one as the how-to, a companion `/tutorials/line-chart-conditional-formatting-not-working/` as the debug page. Higher total ceiling, more internal link surface.

The "color only the section above threshold" workaround (duplicate measure with BLANK) is also a standalone query with real volume. It's currently buried in the FAQ. Promote it to its own H2 — that's the paragraph people will screenshot and share.

**Pillar fit.** Category `visualization`, tags `["conditional formatting", "line chart"]` — both too generic. Add `"line chart"` is fine but `"dax"` or `"formatting"` would help internal clustering. Consider `["conditional formatting", "line chart", "dax", "visual formatting"]`.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-09-29` is a future date. If the site renders this, the article won't appear as "new" until then. Either set to today or flag intentionally.
- `description` is a body sentence, not a meta description. It's also truncated mid-thought — it ends at "series" with no value proposition. Rewrite.
- `featured: false` — fine.
- No `canonical` or `seoTitle` fields present — check site schema, but if other articles have them, this is missing.

**Slugs — all seven Related Reading links exist in the real slug list. ✅**
- `/tutorials/conditional-formatting-power-bi/` ✅
- `/tutorials/conditional-formatting-charts-power-bi/` ✅
- `/tutorials/copy-conditional-formatting-power-bi/` ✅
- `/tutorials/dax-switch-function/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅
- `/tutorials/dax-variables-best-practices/` ✅
- `/tutorials/power-bi-visual-types-guide/` ✅
- `/tutorials/power-bi-performance-analyzer-guide/` ✅

**In-body link check.** Body text says "See the dedicated EARLIER article in Related Reading" but the Related Reading list does **not** contain the EARLIER article (`/tutorials/dax-earlier-function/` is in the valid slug list). Broken promise — either add the link or remove the sentence.

**Terminology / technical accuracy**
- "**Format by: Field value**" — the actual Power BI UI label is "Format style: **Field value**". Minor but worth fixing for search matching.
- `Revenue Color` measure: the `ISBLANK` branch returns gray, but the DAX sample uses `CurrentRevenue >= Target` before checking `< Target * 0.8`. Since SWITCH evaluates top-down, a revenue of exactly `Target` returns green — correct. But a blank revenue would fall to `ISBLANK` first — correct. No bug. However, the variable `Target = [Revenue Target]` is undefined in the article (no `Revenue Target` measure shown). Add a one-line definition or inline the value.
- "Summarization: **Average** (or Last, depending on the axis)" — the actual dropdown is "Summarization" with options Sum/Average/Min/Max/Count/Count distinct/Median. There is no "Last" option in the Rules dialog. **This is an error.** Remove "(or Last...)".
- "Format style: **Rules**" — the dialog label is "Format style", correct here.
- `EARLIER` explanation — "needs a nested row context, which a measure does not naturally have" is technically correct but oversimplified; `EARLIER` works in calculated columns and iterators, and the phrase "does not naturally have" is vague. Consider: "`EARLIER` requires a row context, which measures don't have; use `SELECTEDVALUE` or `VALUES` instead."
- Performance claim: "500 points and four series, that is 2,000 additional evaluations" — this is an estimate, not measured. Either measure it or hedge ("roughly"). The claim "Simple SWITCH and comparison logic is negligible" is generally true but unquantified.

**FAQ / format**
- Five FAQs is fine, but the "Not directly" answer to Q2 buries the lede — the workaround (two overlapping measures) is the useful content. Consider promoting to its own H2 as recommended above.
- FAQ Q4 answer conflates page-level cross-filtering with measure-visible filter context. The claim "If a user clicks a bar in a separate chart, the line chart's points are filtered and the color measure recalculates" is true only when the line chart isn't already isolated by its own filters, and only via cross-filter direction. Slight overstatement.
- No `## Conclusion` or closing thought; the article ends on FAQ. Acceptable for a reference tutorial but the Related Reading section would read better with a one-line closer.

**Structural**
- Section order is logical but "Prerequisites" appearing before the first H2 step makes the article feel front-loaded. Consider merging Prerequisites into a short intro paragraph — three prerequisites is not enough to justify its own H2.
- The table in "Test and Troubleshoot" is good; the rest of the article could use more of that density and less prose.

**VERDICT: PUBLISH-AFTER-FIX** — fix the `description`, future `pubDate`, the broken EARLIER link promise, the incorrect "Last" summarization option, promote the threshold-segment workaround to an H2, and add the "not working" H2 near the top for the debug query.