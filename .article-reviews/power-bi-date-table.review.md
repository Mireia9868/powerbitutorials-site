# Review: power-bi-date-table

# Review: `power-bi-date-table`

## 1. AI-isms

The prose is mostly clean and technically grounded, but there are several tells:

- **Vague opener / filler in the intro.** "The good news is that building one takes a few minutes, and Power BI gives you three solid options..." — "solid" is a filler adjective. Rewrite: *"Power BI gives you three ways to build one, depending on your data source and how much control you want."*
- **Overused "It also..." construction.** Appears in the intro, the DAX section, and elsewhere. Vary or drop entirely.
- **Empty transition:** "An alternative is `CALENDARAUTO()`..." is fine, but the preceding paragraph ends with "which is wrong in every chart that isn't using the month number directly" — a slightly performative flourish. Trim to *"...which is wrong in most charts."*
- **Stock hedging:** "That almost always means..." in the FAQ is fine; but "This tutorial walks through all three methods" is redundant with the intro paragraph directly above it. Cut one.
- **Em-dash / colon tic.** Three colons in four sentences near "The requirements for a date table that Power BI recognizes are precise:" and "It also lets you add columns Power BI can't derive on the fly:" — the second one actually delivers a list of three items with no list markup. Convert to a proper bullet list or inline comma series.
- **"matters more than it looks"** — mildly folksy, borderline. Acceptable once; don't reuse.
- **"pay for themselves the moment a stakeholder asks..."** — closing flourish, slightly ChatGPT-y. Fine to keep, but tighten: *"...all of which you'll need the moment someone asks for a rolling 13-week view."*
- **"The good news is..."** — classic filler opener; remove.

No em-dash abuse. Paragraph rhythm is reasonable.

## 2. Topic fit

**Rankability:** Yes — "create a date table in Power BI" / "Power BI date table" is a well-established long-tail cluster with commercial intent and low-to-medium KD. The "3 methods" framing is standard but defensible; it matches search intent (users want the fastest path + the "right" path).

**Serving the 1k UV/day goal:** Moderate. This is a foundational, high-volume-search topic, but it's also one of the most heavily covered queries on the web (Microsoft docs, Enterprise DNA, SQLBI, Guy in a Cube). To rank, the article needs a differentiator. Right now it's a competent-but-generic explainer.

**Better angle suggestions:**
- Retitle toward a specific pain point: *"Power BI Date Table: The Only 3 Methods That Actually Work (and When Auto Date/Time Fails)"* — captures the troubleshooting angle.
- Add a section on **role-playing dimensions + USERELATIONSHIP** with a worked example (currently mentioned in one sentence). That's where most users actually get stuck and where competitors are thin.
- Add a comparison table (DAX vs M vs Auto) with model size, refresh impact, and DirectQuery support — that's a snippet-friendly asset.
- Consider a companion FAQ block on **fiscal year with non-December fiscal end** — currently `CALENDARAUTO(12)` is mentioned but fiscal-month offset is not.

Current angle will rank for the head term eventually but will struggle to outrank the incumbents without the differentiators above.

## 3. Errors

**Frontmatter:**
- `pubDate: 2026-10-08` is in the **future** relative to typical publication cadence. If this is a real draft being published today-ish, this is a bug. Verify intent.
- `category: time-intelligence` — confirm this matches your taxonomy (some sites use `time_intelligence` or `Time Intelligence`). Slug-consistency is usually fine, but the frontmatter on other tutorials should be the reference.
- `author: Mireia` — first-name-only is inconsistent if other posts use full name or handle. Verify.
- `tags` array is minimal; consider adding `dax`, `power query`, `time intelligence` variants already used elsewhere.

**Terminology / code:**
- `CALENDARAUTO(12)` — the argument is the **fiscal year end month**. `12` means December, which is the default. Claiming "The `12` argument tells Power BI to treat the fiscal year as ending in December" is correct but tautological — consider showing a non-default example (e.g., `CALENDARAUTO(6)` for June fiscal year-end) to prove the point. As written, a reader learns nothing.
- `WEEKDAY([Date], 2)` returns 1=Monday..7=Sunday. The column is named `Weekday Number` — fine, but should note the convention in a comment or inline note.
- Power Query block: `Date.QuarterOfYear` is a valid M function (`Date.QuarterOfYear`). ✅
- `List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0))` — correct. The note about off-by-one is good but vague; show the fix, not just warn.
- `AddMonthName` uses `Date.ToText([Date], "MMMM")` — this is **locale-dependent**. In a non-English locale it returns the localized name. Worth a one-line note since this is a common cross-environment gotcha.
- Table of mistakes row: "Using `SELECTEDVALUE` or a join inside the DAX table instead of `CALENDAR`" — this is confusing and not a real common mistake. `SELECTEDVALUE` doesn't produce duplicate dates in a calculated table. **Remove or replace** with a real cause (e.g., using `DISTINCT` on a fact date column instead of a proper calendar).
- The `EARLIER` pitfall paragraph is a bit of a non-sequitur — nobody tries to use `EARLIER` in a date table. Either cut it or move it into a footnote; it dilutes the section.

**Internal links (verified against the slug list):**
All seven "Related Reading" links resolve to real slugs. ✅
No in-body internal links exist — the article would benefit from at least one contextual link to `/tutorials/dax-calculate-function/` or `/tutorials/filter-context-row-context-explained/` where `USERELATIONSHIP` / filter context is mentioned.

**FAQ / format:**
- FAQ headings use `###` under an `## FAQ` — consistent, good.
- The "Q:" prefix inside each H3 is redundant since all headers are questions. Consider dropping the `Q: ` prefix (also helps anchor text parsing).
- No `## Conclusion` — the article ends on Related Reading. Acceptable, but a 2-line wrap-up after the FAQ would help dedwell time and reinforce the CTA.
- The mistakes table is good; consider adding a "Fix" column for SEO snippet potential.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the future pubDate, remove/rewrite the bogus `SELECTEDVALUE` mistake row, add a non-default `CALENDARAUTO` example, and tighten the AI-isms in the intro and CALENDARAUTO paragraphs.