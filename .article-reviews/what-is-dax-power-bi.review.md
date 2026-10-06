# Review: what-is-dax-power-bi

# Editorial Review: `what-is-dax-power-bi`

## 1. AI-isms

The draft is broadly clean, but a handful of phrasing tells and structural tics need attention.

**In-body:**

- **"That responsiveness is the whole point."** — Vague intensifier filler. Rewrite: "A measure's value changes on every visual interaction, which is why it must be stored as a recipe rather than a value."
- **"Two terms appear constantly in DAX documentation. Getting them straight removes most of the confusion."** — Generic textbook opener. The "removes most of the confusion" claim is unearned. Rewrite: "Filter context and row context drive nearly every DAX quirk, including the errors that send beginners to forums."
- **"If you only take one thing from this article, take this:"** — Overused LLM transitional device. Cut or replace with a plain statement: "The most useful mental model: a calculated column cannot see the whole table; a measure cannot see individual rows unless you hand it one with an iterator."
- **"That last point is worth restating."** — Self-referential filler. Delete and let the bullet stand.
- **"That fifth step is the moment DAX usually clicks."** — Slightly salesy but acceptable; keep but tighten.
- **"Ask whether the answer depends on what the user has selected. If it does, it is a measure."** — This is good, keep it. Not AI-ish.
- **Em-dash abuse:** only one in the body ("— you do not need..."), used correctly. Clean on that front.
- **"The single most common source of 'my DAX is broken' complaints."** — Quoted shorthand is fine but borderline cliché; consider "the most frequent cause of wrong-looking time intelligence results."
- **FAQ Q: "How do I learn DAX faster?"** — Classic filler FAQ. It restates generic advice. Either cut the question or replace with something query-shaped, e.g. "How do I debug a DAX measure that returns the wrong number?"

**Openers:** "DAX stands for Data Analysis Expressions. It is the formula language..." — acceptably direct, no "In today's world" preamble. Good.

## 2. Topic Fit

- **Long-tail rankability:** Weak. "What is DAX in Power BI" is a head term dominated by Microsoft Docs, SQLBI, and Enterprise DNA. This article will not crack page one on the exact query without domain authority you almost certainly don't have. It *is* a reasonable **intro hub** for internal linking, but not a traffic driver on its own.
- **1k UV/day goal:** As written, this article will not contribute meaningfully to that target on its own. It competes with the definitive explainer for the term.
- **Better angles that are actually rankable:**
  - "CALCULATE vs FILTER in DAX (with when-to-use examples)" — you already have `/tutorials/calculate-function/` and `/tutorials/dax-calculate-function/` (note: those two slugs may be duplicate content — see Errors). This is the query that has real long-tail volume and commercial intent.
  - "Why does my DAX measure return blank?" — FAQ-style, matches how beginners actually search.
  - "DAX calculated column vs measure (with performance numbers)" — includes a comparison a head-term article never shows.
- **Strategic role:** Keep this page as a top-of-funnel pillar only if you funnel hard with contextual links into the specific tutorials above. As an orphan intro piece it will get impressions and almost no clicks.

## 3. Errors

**Frontmatter**
- `pubDate: 2026-10-06` — future date relative to today. Unless scheduled drafting is a convention on this site, flag for correction.
- `category: dax` and `tags: ["dax","fundamentals"]` — fine, assuming those tokens exist in your taxonomy.
- `difficulty: Beginner` — inconsistent capitalisation vs. `dax` in tags. Confirm schema expects this casing.

**Internal links (verified against the real slug list)**
- `/tutorials/dax-basics/` ✅ exists
- `/tutorials/filter-context-row-context-explained/` ✅ exists
- `/tutorials/calculate-function/` ✅ exists
- `/tutorials/dax-calculate-function/` ✅ exists — **but you are linking to two slugs that appear to be the same article.** `calculate-function`, `dax-calculate-function`, and the implied duplicate `dax-basics`/`dax-variables-guide`/`dax-variables-best-practices` pairs suggest duplicate-content problems in your library. Pick one canonical target and consolidate.
- `/tutorials/dax-variables-guide/` ✅ exists (but see duplicate `dax-variables-best-practices/` — audit which one you mean)
- `/tutorials/dax-time-intelligence-ytd-qtd-mtd/` ✅ exists
- `/tutorials/data-modeling-star-schema/` ✅ exists
- `/tutorials/power-bi-common-mistakes-beginners/` ✅ exists
- `/tutorials/directquery-vs-import-mode/` ✅ exists
- `/tutorials/dax-troubleshooting-guide/` ✅ exists

All ten links resolve. No invented slugs.

**Terminology / code**
- `DIVIDE ( [Total Sales], SUM ( Targets[TargetAmount] ) )` — the `Sales vs Target %` measure is fine syntactically but references a `Targets` table introduced nowhere. Either explain the table or drop this example.
- `SWITCH ( TRUE (), ... )` — correctly idiomatic. ✅
- `CALCULATE ( [Total Sales], Sales[Region] = "West" )` — works, but note in the prose that the boolean short-circuits to a filter on the Region column. You do say this later, but the example appears before the explanation. Reorder or add a one-line gloss.
- "DAX is case-insensitive for function and identifier names" — mostly correct, but column/measure resolution rules and locale collation can bite. This is a fair simplification for beginners; no change needed.
- "`=` for equality... `==` is not valid" — correct. Excel's `=` is also equality; the wording "unlike Excel's `=` convention confusion" is muddled. Rewrite: "Use `=` for equality; `==` is not valid in DAX."
- The claim "CALCULATE... does not replace the existing filters; it overrides the filter on the Region column specifically" — accurate but worth noting it *does* replace any filter on `Sales[Region]` specifically. Slight clarification recommended.

**Structure / FAQ**
- Six FAQ entries is on the high side for a 1,500-word intro. Cut to four by removing "How do I learn DAX faster?" (filler) and merging the DirectQuery answer into the body's workflow section.
- The "Related Reading" list has 10 links, several of which cover overlapping ground (`calculate-function` and `dax-calculate-function`; two variables guides). Prune to 6 unique, high-value targets.
- Headings use sentence case consistently. Good.
- Table renders correctly. Good.
- No images, no alt text, no diagrams. For a conceptual intro (filter context vs row context) a single diagram would earn featured-snippet eligibility. Recommend adding one.

**Missing**
- No mention of evaluation order (verti-paq vs. formula engine) — fine for beginner level, but if a reader searches "what is DAX" they may land here expecting it. A one-sentence denylist of "what this article does not cover" would improve trust.

---

**VERDICT:** PUBLISH-AFTER-FIX (trim AI-isms, resolve duplicate-slug internal links, fix the `Targets` orphan reference, cut two FAQs, and reframe positioning as a hub rather than a head-term play)