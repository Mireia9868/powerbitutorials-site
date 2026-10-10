# Review: power-bi-drillthrough

# Review: `power-bi-drillthrough`

## 1. AI-isms

The prose is cleaner than most drafts, but a few patterns stand out.

- **"One of the cheapest ways to make a report feel responsive."** — Closing cliché. Cut or rewrite to something concrete: *"Drillthrough config takes ten minutes; the rest of the time goes into relationship and filter debugging."*
- **"That second behavior surprises people."** — Hedge filler. Either commit (*"Authors routinely miss this: the source page's filter state travels with the click."*) or delete.
- **"Resist the temptation to put twenty visuals on it."** — Generic advice voiced as a maxim. Better: *"Keep the detail page under ~8 visuals; drillthrough load time scales with the page."*
- **"A report stays one artifact, but the navigation behaves like a small application."** — Vague marketing opener in the lede. The concrete example (bar for one region → detail page) already does the work. Cut the abstraction.
- **"Nothing about these measures is drillthrough-specific."** — Correct but reads as AI reassurance. Merge into the next paragraph.
- **Em-dash check:** none abused. Good.
- **"Two things follow from that definition:"** → **"Two consequences:"** is tighter. The "definition/formulaic" scaffolding ("Consider a…", "Typical candidates:", "Behavior to note:") repeats across sections and reads templated.
- **"Design your detail visuals for that possibility."** — Ends a bullet on a limp imperative. Say what to do: *"Show a row count and let the user pivot; or restrict drillthrough to leaf rows via explicit buttons."*

## 2. Topic fit

**Rankable?** Moderate. "Power BI drillthrough" is a solid long-tail head term, but you're competing against Microsoft Learn (which owns the SERP top) and a handful of high-DA tutorial sites. The article's edge is the problem/fix and testing-checklist sections — that is where the long-tail queries live ("power bi drillthrough greyed out", "power bi drillthrough blank page", "drillthrough from matrix subtotal").

**Serves the 1k UV/day goal?** Needs revision as-is. Currently the title targets the head term you won't win, and the article buries its differentiated content in section 5+. Two moves:

1. **Retarget the H1/meta to long-tail intent.** e.g. *"Power BI Drillthrough: Setup + Fixing Blank Pages and Greyed-Out Menu Items"*. That captures the troubleshooting queries where you can actually rank.
2. **Promote the "Common problems" section above Step 5.** Searchers arriving with a broken drillthrough don't want the full tutorial first.

**Better angle?** A dedicated troubleshooting piece ("Power BI Driftthrough Not Working: 7 Causes") would likely out-earn the setup tutorial given your existing corpus already has `/power-bi-drill-through/` (see Errors below). Right now you have two slugs targeting the same intent.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-10-10` — future date. If past publication, fix to actual date.
- `tags: ["drillthrough"]` — single tag; add `["drillthrough", "navigation", "visualizations"]` for internal search parity with sibling posts.
- `description` restates the title verbatim. Rewrite to what the article *does*: *"Set up a Power BI drillthrough page, control which filters carry over, and fix the blank-page and disabled-menu problems."*

**Terminology / code**
- Step 2: *"**One field per bullet.**"* — The UI label is **Add drill-through fields here**; the bullets are the field entries. "Bullet" is ambiguous. Say "each field added becomes its own right-click menu entry."
- Step 3: *"You configure this through the page's filter pane settings in the Format pane under **Page information**"* — This control is not under **Page information**. The correct path is **Format pane → Page → Filter pane → Keep all filters / Do not keep filters** (and it is a page-level Format option, not "filter pane settings"). Verify and correct — this is the kind of detail that erodes trust fastest.
- Step 5: *"In the Power BI Service… Enable it in the Options dialog under **Report settings** (the target report must also opt in)."* — Cross-report drillthrough is enabled in **File → Options and settings → Options → Report settings → "Enable cross-report drillthrough"** AND at the target report. The "(target must also opt in)" clause is doing real work and should be its own sentence.
- DAX block: `Sales in Slice = SUMX('FactSales', [Quantity] * [UnitPrice])` — fine, but `Quantity * UnitPrice` as a revenue proxy is a common beginner trap (ignores discounts, tax, returns). Add a one-line caveat or swap to `SUM('FactSales'[SalesAmount])` for realism.
- "cross-report drillthrough does not work when the files are opened in Desktop" — True for one direction (Desktop can trigger, but Service-only for cross-workspace), but as written it is over-broad. Soften or cite Microsoft's documented restriction.

**Internal links — verified against real slugs**
All nine links in **Related Reading** resolve to real slugs in your list. However:

- `/tutorials/power-bi-drill-through/` exists **and this article** (`power-bi-drillthrough`) exists. You now have two near-duplicate slugs. Decide: either this article *is* the canonical and the old one should redirect, or this one should be retitled ("…Troubleshooting & Filters") to disambiguate. As published they will cannibalize.
- FAQ / Step 5 both mention field parameters but never link `/tutorials/power-bi-field-parameters/` inline (it's in Related Reading only). Add the inline link in Step 5 or the "measure as drillthrough" FAQ.
- No link to `/tutorials/power-bi-common-mistakes-beginners/` — a natural cross-sell given the troubleshooting framing.

**FAQ / format**
- FAQ Q1 (*measure instead of column*) is already answered in Step 2 (*"Only columns and hierarchies qualify"*). Redundant. Either remove Step 2's line or reframe FAQ Q1 as an edge-case ("Can I drill on a measure that returns a single value?").
- Q5 and Q6 overlap (both about multi-value / subtotal drillthrough). Consider merging.
- Missing FAQ that searchers actually ask: **"Can I pass a dynamic value into drillthrough from a button?"** — you allude to it but never confirm.
- No `##` heading uses sentence case consistently: "What drillthrough actually does" (sentence) vs "Step 1: Build or pick a detail page" (title). Normalize.

---

**VERDICT: PUBLISH-AFTER-FIX** (fix the Format-pane location, retitle to disambiguate from the existing drillthrough slug, retarget meta to troubleshooting intent, and trim the AI-ism closer)