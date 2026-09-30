# Review: kpi-conditional-formatting

# Editorial Review: `kpi-conditional-formatting`

## 1. AI-isms

The draft is cleaner than most LLM drafts, but a few patterns stand out.

- **Vague universal opener.** *"That makes conditional formatting on the KPI visual genuinely different from formatting a bar chart or a matrix."* — "genuinely" is filler. Rewrite: *"Conditional formatting on the KPI visual works differently from a bar chart or matrix: there is no per-category row to color."*
- **Mechanical transition sentence.** *"This article walks through what can actually be formatted, how to write the DAX that feeds it, and the traps that make colors behave unexpectedly."* — this is a roadmap sentence that says nothing. Cut it or replace with something concrete: *"The KPI visual exposes three bindable color properties; everything else is fixed. Below: the measure pattern, the `fx` binding, and four failure modes."*
- **"Two details matter here."** — throat-clearing before a list. Lead with the first detail directly.
- **"A common approach is..."** (§Testing the rule) — vague hedge. Say who does this or drop the framing: *"Wrap the threshold in a What-If parameter so you can drag a slider and watch the color flip."*
- **"measurably cheaper"** — unsupported claim. Either cite a benchmark or soften to *"avoids re-evaluating the division per branch."*
- **"surprises people during UAT"** — acceptable, keep, but the surrounding sentence (`"That is correct behavior, but..."`) is a filler pivot. Trim to: *"That is correct, but it trips up UAT sign-off if reviewers expect identical colors."*
- **Em-dash check:** none present in body; frontmatter `description` is the only place with punctuation drift (see §3).
- **List-of-three reflex:** the opener, the "This article walks through" sentence, and "First... Second..." all lean on enumeration as structure. Fine in moderation; three in one article is a tell.

## 2. Topic fit

**Rankability:** Moderate-to-long-tail. "KPI visual conditional formatting Power BI" is a real query with low competition, and the article answers the exact confusion (why doesn't the `fx` button work on a KPI like it does on a card?) that People Also Ask surfaces. Good pick.

**Serving the 1k UV/day goal:** This alone will not move the needle — KPI visual is a minority visual. But it slots cleanly into the conditional-formatting cluster you already rank for (`conditional-formatting-power-bi`, `-based-on-measure`, `-charts-power-bi`, `gauge-`, `line-chart-`, `bar-chart-`). Its value is **cluster reinforcement and internal-link density**, not standalone traffic. It is a supporting post, not a pillar.

**Better angle to consider:** The strongest section is "Alternative: the Card (new) visual." That is the actual decision most readers face — *KPI visual vs Card (new) when you need status colors*. Consider reframing the title/description around that comparison (`"KPI visual vs Card (new): conditional formatting in Power BI"`) to capture comparison-intent traffic, which converts to longer sessions and feeds the conditional-formatting cluster from a new query vector. Current angle is fine as-is; this is an upside note, not a blocker.

**Gap:** No mention of the **Card (classic)** visual or **Multi-row card**, which some readers will still be stuck with on older tenants. One sentence would close the loop.

## 3. Errors

**Frontmatter / format:**
- `description` is truncated mid-word and mid-sentence: *"...and no per-category row"* — cuts off before the noun. Fix or replace with a full sentence: *"How to apply conditional formatting to the Power BI KPI visual using DAX color measures — including the callout, indicator background, and trend axis."*
- `pubDate: 2026-09-30` is in the future relative to any plausible review date. Confirm this is intentional (scheduled) or correct it.
- `author: Mireia` — fine if that matches your author registry; otherwise full name.
- `tags` is thin (`["conditional formatting", "kpi"]`). Add `"dax"`, `"visualization"` for cluster discovery.

**Technical / code:**
- **DAX comment style:** The `--` inline comments inside `SWITCH` are valid DAX, but be aware they strip on copy-paste into some tools. Not an error, just fragile for a tutorial. Consider `//` for line comments, which survives more pastes.
- **`KPI Indicator Color (Dynamic)` — misleading name.** The dynamic behavior comes from the What-If parameter's *slicer binding*, not the measure itself. The measure is still static per filter context. Rename to `KPI Indicator Color (Parameterized)` or note explicitly that "dynamic" here means "re-colors when the slicer changes."
- **`SELECTEDVALUE ( 'Threshold'[Threshold], 0.95 )`** — correct, but does not explain *why* the default matters (it fires when the slicer is multi-select or has no selection). Add a half-sentence.
- **Claim: "the `fx` dialog will accept it but the visual falls back to the default color"** — subtly wrong. `fx` on Indicator > Callout value will generally reject or gray out a numeric field at bind time rather than accept-then-fallback. The fallback-to-default behavior occurs when the *measure returns BLANK* or an invalid hex string. Verify this against current Power BI Desktop before publishing; if uncertain, restate as *"Power BI will not color the callout from a numeric field; the property stays on the theme color."*
- **`Format style: Field value`** — the dialog actually offers *"Format style: Gradient / Rules / Field value"* only in some contexts; on Indicator > Callout value it typically goes straight to a field picker. Verify the step sequence in current Desktop; if the intermediate screen differs, either generalize the step or match the actual UI. This is the kind of small mismatch that erodes trust in a tutorial.
- **`Sales Target = SUM ( Targets[TargetAmount] )`** — fine, but assumes a `Targets` table exists with no relationship discussion. One sentence on how targets relate (dimension target table joined on the same date/category keys) would prevent a "why is my target wrong" follow-up.
- **RLS section claim:** *"If the color must be identical for all viewers, base it on a measure that ignores the RLS-dimension filter, which is rarely what you want."* — This is technically muddled. RLS on a *dimension* filters the sales/measure aggregation, so the color difference is downstream of the same filter, not a separate coloring decision. Either explain via `CROSSFILTER`/`REMOVEFILTERS` on the specific dimension or cut the paragraph. As written it will confuse intermediate readers.

**Internal links — verified against provided slugs:**
- ✅ `/tutorials/conditional-formatting-power-bi/`
- ✅ `/tutorials/conditional-formatting-based-on-measure/`
- ✅ `/tutorials/conditional-formatting-charts-power-bi/`
- ✅ `/tutorials/bar-chart-conditional-formatting/`
- ✅ `/tutorials/gauge-conditional-formatting/`
- ✅ `/tutorials/line-chart-conditional-formatting/`
- ✅ `/tutorials/copy-conditional-formatting-power-bi/`
- ✅ `/tutorials/dax-switch-function/`
- ✅ `/tutorials/dax-variables-best-practices/`
- ✅ `/tutorials/filter-context-row-context-explained/`
- ✅ `/tutorials/directquery-vs-import-mode/`
- ✅ `/tutorials/power-bi-performance-analyzer-guide/`

All Related Reading slugs exist. No broken links.

**Missing internal links worth adding:** `/tutorials/calculated-tables-what-if-parameters/` (you discuss What-If parameters but the Related Reading list omits the canonical What-If page — a notable gap), and `/tutorials/power-bi-row-level-security/` (RLS section without a link to the RLS hub).

**FAQ:** Three of four questions are genuinely useful. Q4 (*"How many thresholds before it gets slow?"*) is a soft question with a soft answer. Consider replacing with *"Why does the KPI callout color differ between Desktop and the Service?"* (theme caching, Service-side render differences) — more actionable and more searched.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the truncated description, verify the `fx` binding steps and the numeric-field behavior against current Power BI Desktop, tighten the RLS paragraph, and resolve the future pubDate.