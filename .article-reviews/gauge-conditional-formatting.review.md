# Review: gauge-conditional-formatting

# Review: `gauge-conditional-formatting`

## 1. AI-isms

| Location | Issue | Rewrite |
|---|---|---|
| Opening line | "The gauge visual has a reputation problem. Analysts either love it or dismiss it as a decoration that wastes dashboard space." Reproduced verbatim in the **description frontmatter**. | Description should be a standalone meta sentence, not the article's first line. e.g. `"How to drive gauge fill, target, and callout colors from DAX — dynamic targets, rule-based formatting, and the patterns that actually work in current Desktop builds."` |
| Intro para 1 | "The truth is that…" — classic filler pivot. | Cut. Start: "A gauge answers one question well: how close is the current value to its target? It gets more useful when it reacts to the data underneath it." |
| Intro para 1 | "This tutorial walks through…, then…, and finally…" — mechanical three-beat transition recycled across thousands of posts. | "Below: setting fixed target and bands, moving to DAX-driven dynamic targets, and applying rule-based color to fill, target line, and callout." |
| Step 1 | "Keeping the maximum separate from the target is important because…" — soft assertion. | "Separate the maximum from the target — otherwise a target at 100% of the axis leaves no headroom when the value exceeds goal." |
| Step 1 | "That produces a stable axis with visible headroom." — marketing cadence. | "The axis stays stable and leaves headroom." |
| Step 1 | "A hard-coded maximum like 1000000 breaks the moment a region reports a different scale." — "the moment" is an AI tell. | "A hard-coded maximum (e.g. `1000000`) breaks as soon as a region reports at a different scale." |
| Step 2 | "This is the same filter context behaviour covered in…, and it trips up most beginners on their first dynamic target." — "trips up most beginners" is a recycled blog cliché. | "If the relationship is missing, `CALCULATE` won't filter as expected and the target reads as a flat total. See [filter context and row context explained](/tutorials/filter-context-row-context-explained/)." |
| Step 3 | "That is heavier, but it always works." — vague. | "It's more setup, but it works in every Desktop build." |
| Step 5 | "A zero target still draws the line at the origin, which is visually honest…" — "visually honest" is a tic. | "A zero target still draws a line at the origin, which signals missing data instead of a broken visual." |
| FAQ Q5 | "For a single hero metric on an executive page, the gauge often wins; for everything else, a card or bar chart is more efficient." — "often wins" hedge. | "Use the gauge for one hero KPI on an exec page; cards and bar charts elsewhere." |
| Throughout | Em-dash frequency is high (~15 in ~900 words). Several are decorative (e.g. "the target line — which"). | Reduce by ~50%. Convert many to commas or periods. |
| Meta | **Zero code fences for DAX in the frontmatter delimiters.** The doc uses ` ```dax ` — fine. But the article ships **no working screenshot**, just `(placeholder)` image stubs. Ship-blocker. | Replace with real captures before publish. |

## 2. Topic fit

- **Long-tail rankability:** Yes. "gauge conditional formatting power bi" is a real long-tail query with thin competition. Slug is clean. Difficulty marked `Beginner` is defensible for the target audience.
- **Goal fit for 1k organic UV/day:** This is a supporting article, not a traffic magnet. Realistic ceiling: a few hundred UV/month once ranked. Fine as part of a cluster with the existing `/conditional-formatting-power-bi/`, `/conditional-formatting-charts-power-bi/`, and `/copy-conditional-formatting-power-bi/` pieces feeding it.
- **Bigger angle to consider:** The single most-searched sub-question in this space is *"Power BI gauge color based on value"* and *"Power BI gauge conditional formatting not working."* The draft treats Route A (built-in rules) with visible uncertainty — the FAQ admits "in older builds" and "check your Desktop version." That hedging will hurt rankings against tutorials that just give the current answer. Either test the actual build behavior and commit, or retitle around the workaround: **"How to Color a Power BI Gauge by Value (When fx Isn't Available)"** — more specific, better CTR, and honest about the constraint.
- **Angle currently missing:** A comparison of gauge vs. KPI card vs. bar-with-target is buried in FAQ Q5 and a "When to skip the gauge" section. That's the section most likely to be linked to from other pages. Consider promoting it higher or splitting into its own piece.

## 3. Errors

**Factual / technical**

1. **Step 3, Route A claims gauges have conditional formatting on Fill.** This is inconsistent with the article's own opening claim ("the classic fx conditional formatting button… is not always available… Gauge visuals expose color as a property, not as a format rule with a data-driven binding"). Pick a position. Current Desktop builds do expose the fx dialog on gauge Fill, Target, and Callout — so the opening framing is the error. Fix the intro to state the actual constraint (why it's confusing, not that it's absent) rather than build the whole article around a premise the FAQ later walks back.

2. **Step 2 date filter bug.** `Targets[TargetMonth] = SelectedDate` uses `MAX ( Dates[Date] )`. If the visual is not filtered to a single month, this collapses to the last visible date and returns one month's target against many months of sales. Either wrap in `HASONEVALUE` or state clearly the visual must be month-filtered. As written, this is a copy-paste trap.

3. **Step 5 `COALESCE` example drops the date filter.** The guarded version no longer respects `TargetMonth`, so it silently reverts to the Step 1 behavior. Learners will paste this and get a flat target.

4. **FAQ Q2 answer is correct but the body doesn't prepare for it.** The Step 2 code uses an implicit relationship; the FAQ says to use `USERELATIONSHIP` when inactive. Mention this in Step 2, not just in the FAQ.

5. **"Rules referencing the wrong field" bullet** — this is sourced from the article's own confusion in Step 3/Step 4. Rules evaluate the Value measure; the Target is not passed to the rules engine. That's correct, but it contradicts Step 5's later suggestion that the target line inherits a color. Clarify that this is about the *fill* rules, not the target line.

**Frontmatter**

6. **`description` duplicates the opening sentence verbatim.** Search engines and social previews will look duplicated. Rewrite (see AI-isms table).
7. **`pubDate: 2026-09-29`** is in the future. Confirm this is intentional scheduling; if not, it won't index.
8. **`author: Mireia`** — no surname and no `author` field in the schema shown for other posts. Verify against site convention.
9. **Tags: `["conditional formatting", "gauge"]`.** Only two tags; every other piece in the link set uses richer tag arrays. Add `power bi`, `visualization`, `dax`.

**Links**

10. All internal links resolve to real slugs on the provided list. ✅ None are imagined. But:
    - `/tutorials/conditional-formatting-power-bi/` is linked **twice** (intro and Related Reading) — fine.
    - `/tutorials/power-bi-visual-types-guide/` is linked in Related Reading but never referenced in the body. Either drop or add an inline mention.
    - `/tutorials/dax-switch-function/` linked in Related Reading is never mentioned in the body — SWITCH isn't used anywhere in the article. Broken reader expectation. Remove or actually use SWITCH in a color-rule example.
    - Good opportunities missed: `/tutorials/power-bi-visual-calculations/` and `/tutorials/power-bi-percentage-of-total/` would both fit naturally in Step 4.

**Images**

11. All four images are `(placeholder)`. Real screenshots are the difference between this ranking and not. Specifically:
    - Fig 1: gauge with three-band fill.
    - Fig 2: Fields well with Value/Target/Maximum populated.
    - Fig 3: the actual fx dialog on gauge Fill (this is the payoff image for the whole article).
    - Fig 4: side-by-side gauge vs. bar.

**Format**

12. `### Q:` FAQ prefix is inconsistent — most FAQ blocks use `**Q:**` or plain headings. Confirm site convention.
13. "Related Reading" heading capitalization: verify it matches other posts (`Related reading` vs `Related Reading`).
14. `**Route A:**` / `**Route B:**` bold lead-ins are fine but the paragraph after Route A is one long sentence; split.

---

**VERDICT: REWRITE** — the premise (gauge doesn't support conditional formatting) contradicts the FAQ and current Desktop behavior, the DAX examples have real copy-paste bugs (Step 2 and Step 5 target filters), and all figures are placeholders. Fix the technical claims first, then the AI-isms become a second pass.