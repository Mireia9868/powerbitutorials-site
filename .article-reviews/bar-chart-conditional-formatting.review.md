# Review: bar-chart-conditional-formatting

# Editorial Review — `bar-chart-conditional-formatting`

## 1. AI-isms

The draft is mostly disciplined, but a few tics stand out:

- **Filler transition sentence:** "A fourth path exists on some visuals (Rules with a "Field" source for the threshold itself), but for bar charts the three above cover almost every real requirement." This is a hedge that adds no information and undermines the clean list above. **Rewrite:** delete the sentence entirely, or replace with a concrete caveat: "Script-based rules exist but don't apply to bar chart fill color."
- **"Two things matter here."** Classic ChatGPT scaffolding. **Rewrite:** fold the two points directly into prose or a two-bullet list without the throat-clearing intro.
- **"That single change removes an entire class of report maintenance."** Marketing-ish closer that sounds generated. **Rewrite:** "That change means threshold edits happen in one place instead of inside every visual's dialog."
- **"This is the cleanest way to build a variance bar chart."** Assertion without justification. Either justify (contrast with rules) or cut.
- **"Decide which reading you want before you pick gradient."** Imperative filler; the preceding sentences already made the point. Cut.
- **Em-dash audit:** Four em-dashes across the piece. All are legitimately parenthetical, none are the "list of three — each with a clause" AI pattern. Acceptable.
- **Opening line** ("A bar chart that renders every bar in the same shade of blue forces the reader to do the comparison work themselves") is strong and specific — keep. Description field duplicates it verbatim, which is a mild SEO anti-pattern (see §3).

No vague openers ("In today's fast-paced world…"), no "Let's dive in," no "It's important to note." Good baseline.

## 2. Topic Fit

**Long-tail rankability:** Moderate. "Bar chart conditional formatting" is a real query and the article is unusually focused on the bar-chart-specific workflow (Rules / Gradient / Field), which differentiates it from the generic `/tutorials/conditional-formatting-power-bi/` slug. That's the right play — but it's competing with a slug you already own.

**Against the 1k UV/day goal:** This is a support/long-tail article, not a hub. Realistic ceiling is a few hundred monthly visits unless you differentiate. Two levers:

1. **Own the "gradient vs rules vs measure" decision.** That table is the highest-value asset here and could be its own section titled around a searchable phrase like *"bar chart conditional formatting: rules vs gradient vs measure."* Pull it up near the top, not buried after DAX territory.
2. **Add the screenshot-heavy "color top N bars" recipe as a subsection header.** "How to color the top 3 bars in a Power BI bar chart" is a distinct, low-competition query that this article already half-answers.

**Better angle:** Consider tightening scope to *"Bar chart conditional formatting: rules, gradient, and DAX"* and dropping the "Related Reading" sprawl (7 links dilutes internal link equity for a support article).

**Overlap risk:** You have three sibling slugs on this exact topic (`conditional-formatting-charts-power-bi`, `conditional-formatting-power-bi`, `copy-conditional-formatting-power-bi`). Differentiate in the intro with one line: "This article focuses on bars specifically; for matrix/table formatting see [link]." Otherwise you're cannibalizing.

## 3. Errors

**Frontmatter**
- `description` is a word-for-word copy of the first body sentence. Search engines and social cards will render duplicate text. **Fix:** write a distinct description, e.g., *"Color bars by rules, gradient, or a DAX measure — with the RANKX recipe for top-N highlights."*
- `pubDate: 2026-09-28` is in the future. Confirm intent (scheduled vs. stale placeholder).
- `author: Mireia` — no surname; verify against your author schema pattern.

**Terminology / code**
- Opening of "Rules" section: "Rule-based formatting, gradient formatting, and measure-driven color all render in the Service the same way as in Desktop." Fine. But the FAQ answer claims *"any formatting applied through the old Analytics pane preview features … have been retired."* This is too vague to verify — either cite the specific feature name or cut. Analytics pane still exists for some features; a blanket "retired" claim is risky.
- `SWITCH(TRUE(), ...)` block: valid, but `RETURN` indentation (`RETURN` on its own line vs. inline) is inconsistent with the second code block. Pick one style.
- `RANKX( ALLSELECTED( Products[Category] ), [Total Sales], , DESC, DENSE )` — the blank third argument (value expression) is legal but confusing to beginners. Add a one-line comment: `-- third argument omitted = use [Total Sales] as the value`. Without it, readers will copy-paste and wonder why it errors in older DAX Studio.
- "passing a single column works, but passing the full table lets the measure include any category present in the filter context" — this is **wrong as written**. `ALLSELECTED( Products[Category] )` already returns all categories in scope; passing the full table would produce a different result (rank across row combinations), typically *not* what you want for coloring one bar per category. Correct this paragraph — currently it gives bad advice and asserts it confidently.
- "Edit interactions" phrasing: you say "Use **Edit interactions** if you need a table selection to drive the colors." Edit interactions controls whether cross-filtering *applies*, not color logic. Reword: "Cross-filtering from another visual already flows into the color measure via filter context; use Edit interactions to *stop* it if the colors shouldn't respond."
- "A measure that returns a number for the color field silently falls back to the default." Verify this claim in current Desktop. My recollection is newer versions may error or render black; either way, "silently falls back to the default" is a specific behavior worth confirming before publishing.

**Internal links**
All eight links in Related Reading verified against the real slug list — no broken links. But you're **not linking** to several obviously relevant slugs that exist:
- `/tutorials/conditional-formatting-power-bi/` (yes, linked once — good)
- `/tutorials/dax-calculate-function/` — would be a better link than `/tutorials/calculate-function/` if the FAQ mentions `CALCULATE`
- `/tutorials/dax-variables-best-practices/` — the `VAR` usage in both DAX blocks begs for this link
- `/tutorials/power-bi-dashboard-design-principles/` — supports the "palette clashing" pitfall

Adding 2 of these improves the internal-link graph; the current list of 7 is already on the high side.

**FAQ / formatting**
- Q2 answer: "you wrapped the result in `CALCULATE` with a filter that removes the category filter" works, but should link to the `filter-context-row-context-explained` slug you already cite below — inline links beat Related Reading for FAQ answers.
- Q4 answer reintroduces `SELECTEDVALUE` without ever showing it. Consider a two-line code snippet.
- Figure captions are all `placeholder` — confirm alt-text will be written before publish.
- Headings are consistent; no H1 inside body (correct, since `title` is H1).

## VERDICT: **PUBLISH-AFTER-FIX**

Two factual issues (the `ALLSELECTED`/full-table claim in the RANKX paragraph, and the Edit interactions sentence) plus the duplicate frontmatter description must be corrected before publishing; the AI-ism cleanup and added internal links to `dax-variables-best-practices` and `filter-context-row-context-explained` (inline, in FAQ) are strongly recommended.