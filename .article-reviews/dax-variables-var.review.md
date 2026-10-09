# Review: dax-variables-var

# Editorial Review: `dax-variables-var`

## 1. AI-isms

**Vague, throat-clearing opener.** The line "Variables inside DAX measures solve a problem you feel before you can name it" is a classic ChatGPT-style grand abstraction. It promises atmosphere, not information, and the next sentence then just... names the problem. Cut the abstraction and lead with the concrete.

- *Rewrite:* "A measure that starts as three lines often grows to twelve, repeats the same sub-expression four times, and becomes hard to debug. `VAR` / `RETURN` lets you name a piece of logic once, reuse it many times, and read the measure top-to-bottom."

**Filler sentence posing as insight.** "Consistency matters more than the specific convention. New joiners read measures; variables are the primary comments in a DAX expression." The second sentence is decent; the first is a truism. Delete or fold.

**Mechanical transition headers.** "## Where VAR actually helps" is fine, but the sub-headers ("Removing repeated logic," "Conditional branching that stays readable," "Storing a filter context for reuse," "Returning two values from one pass") are all the same shape and read like a generated outline. Two of them can be merged. "Storing a filter context for reuse" actually stores a *table expression* — see Errors.

**Em-dash / dash abuse.** Not egregious here, but the piece over-uses the "X, and Y, and Z" triadic cadence. Example: "Naming it documents intent and avoids repeating the `TREATAS` call inside multiple `CALCULATE` branches." Fine as-is, but the pattern repeats across nearly every example closing sentence.

**Hedgey performance framing.** "Variables do not automatically make DAX faster, but they remove two common sources of slow measures" is followed by "if a measure slows down after you refactor to variables, test again with and without." This is correct but waffly. Pick a stance: variables are a readability tool that *usually* helps performance and *occasionally* hurts it, and the only way to know is to measure. State it once.

**Bullet list cadence.** The "Two caveats" paragraph is a list rendered as prose. Fine, but the preceding "rounds up" bullet intro ("remove two common sources") followed by only two bullets feels like padding. Either commit to a list or write it as prose.

**"Debugging with variables" section.** The `-- swap this to Revenue or Cost to inspect them` comment instruction is fine, but "This is faster than rebuilding the measure from scratch, and you delete the scaffolding when you are done" reads like a closing cliché. Trim.

No serious em-dash abuse, no "in conclusion," no "delve." Cleanup needed on openers and truisms only.

---

## 2. Topic fit

**Rankability.** The slug `dax-variables-var` targets a real long-tail query cluster ("DAX VAR", "DAX variables", "Power BI variables in measures"). Search volume is not enormous but the intent is clear and the difficulty is low. This is rankable.

**Overlap risk.** You have *three* near-identical slugs in your own inventory:

- `/tutorials/dax-variables-var/` (this article)
- `/tutorials/dax-variables-guide/`
- `/tutorials/dax-variables-best-practices/`

That is cannibalization waiting to happen. This article tries to be all three at once and so is neither the canonical beginner guide nor the canonical best-practices guide. **Pick a lane.** Given the title ("Cleaner Measures") and the FAQ depth, the natural angle is *the evaluation-order and filter-context trap*, which is genuinely differentiated. Right now that trap is buried under a generic syntax section and a naming table that belongs in `dax-variables-best-practices`.

Recommendation: retitle/refocus to something like "DAX VAR: Why Variables Capture Filter Context (and How to Fix It)" and link out the syntax, naming, and best-practices material to the existing two articles. That gives you one strong ranker instead of three weak ones.

**Goal check (1k UV/day).** A corrected, focused article on the filter-context capture trap *could* justify its slot and feed the other two. As written, it is a competent consolidation piece that will likely lose to your own siblings in the SERP.

**Better angle.** The "variable captures the value, not the expression" rule and the "wrong prior-year comparison" example are the differentiators. Lead with those. The `% of Grand Total` example and the debugging pattern are the second and third best bits. Cut or link out naming, syntax rules, and the FAQ questions that duplicate the two sibling articles.

---

## 3. Errors

### Terminology / code

1. **Wrong framing in "Storing a filter context for reuse."** A `TREATAS` result is a *table expression*, not a filter context. The heading implies you are storing context; you are storing a table. Retitle to "Storing a table filter for reuse."

2. **Ambiguous first syntax rule.** "A variable name must be unique within the expression and cannot collide with a column or measure name in scope without causing ambiguity." This is not quite right. Variables *may* shadow column and measure names; DAX resolves to the variable. The real failure mode is *within the same scope*, not collision with a column. Rewrite: "A variable name must be unique within its declaring scope. A variable may shadow a column or measure name — the variable wins — which is legal but confusing." Verify against current DAX docs; the "cannot collide" phrasing will get corrected in the comments.

3. **"Variables are also evaluated once per query, not once per cell."** This contradicts the immediately following clause ("each cell gets its own evaluation of the variables, so the cost is per-cell"). This is a genuine factual error as written. Variables are evaluated once *per evaluation context* in which the measure is invoked; in a table visual that means per row, per cell. Fix: delete the sentence or rewrite to "Variables evaluate once per evaluation context the measure is invoked in — in a table visual, that is once per visible row."

4. **`SAMEPERIODLASTYEAR` correctness.** The "Wrong Prior Year Comparison" example is a good trap illustration, but as written the `CALCULATE` wrapper is pointless — it will return `CurrentSales` unchanged. That is the *point*, but a reader will ask "so why have CALCULATE at all?" Add one clause: "the `CALCULATE` is a no-op here because `CurrentSales` was already fixed."

5. **`RETURN` "takes exactly one expression, though that expression can be a table."** True, but misleading for a "Cleaner Measures" article — a measure returning a table is not valid in a visual. Either drop the parenthetical or clarify it applies to calculated tables and DAX Studio queries.

6. **FAQ: "Can variables be declared inside a `CALCULATE` filter argument?"** DAX does not allow `VAR` inside a `CALCULATE` argument list in most engines. What the author likely means is declaring a variable *before* `CALCULATE` and referencing it inside a filter argument. Verify. If it errors in current DAX, this answer is wrong and must be corrected or removed.

### Frontmatter

- `pubDate: 2026-10-09` — future-dated. Fine if intentional scheduling, but confirm the CMS treats it as scheduled, not published.
- `category: dax` — consistent with siblings. OK.
- `tags: ["dax", "variables"]` — thin. Add `dax-var`, `measures`, `performance` to align with the article's actual content and the query cluster.
- `author: Mireia` — consistent with other pieces (assumed). OK.
- `description` duplicates the AI-ism from the body verbatim. Replace with a specific meta description that includes "VAR", "filter context", and "DAX measures."

### Internal links (verified against provided slugs)

All eight links in Related Reading resolve to real slugs. No imagined links. Cross-check done:

- `dax-variables-best-practices` ✓
- `dax-variables-guide` ✓
- `calculate-function` ✓
- `filter-context-row-context-explained` ✓
- `dax-optimization-techniques` ✓
- `dax-troubleshooting-guide` ✓
- `power-bi-percentage-of-total` ✓
- `dax-basics` ✓

**However:** you never link `/tutorials/dax-calculate-function/`, `/tutorials/dax-user-defined-functions/`, or `/tutorials/dax-variables-guide/` inline in the body where they would be more valuable than at the bottom. The "Storing a filter context" and "Debugging" sections should link to `dax-troubleshooting-guide` and `dax-optimization-techniques` inline.

Also note: you have both `/tutorials/calculate-function/` and `/tutorials/dax-calculate-function/` in inventory — that is a slug duplication problem outside this review, but pick the canonical one consistently.

### FAQ / format

- Five questions is fine. Q1 is likely wrong (see Errors #6) — verify before publish.
- Q4 ("Can a variable hold a table, a filter, or a measure reference?") answers a question nobody in the target cluster asks. Replace with "Can I use the same variable name in nested expressions?" or delete.
- Q5 duplicates `dax-variables-best-practices` content. Link out instead.
- Code blocks: all use `dax` fence, good. One inline comment uses `--`, correct for DAX.

### Structure

- The article is long (~1,600 words) for what it covers, and half of it duplicates sibling articles.
- "Naming conventions" table is a candidate to move to `dax-variables-best-practices` and link from here.

---

**VERDICT: PUBLISH-AFTER-FIX** — correct the filter-context-capture wording, delete the "once per query" contradiction, verify FAQ Q1 and Q2 against current DAX behavior, and refocus the angle away from the two sibling slugs to avoid cannibalization.