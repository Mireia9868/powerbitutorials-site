# Review: what-is-power-bi

# Editorial Review: `what-is-power-bi`

## 1. AI-isms

The draft is better than average here, but there are still tells.

- **"It bundles together three things that used to require separate tools"** — This is a nice concrete framing, keep. But the following sentence "a data preparation engine (Power Query), an analytical calculation language (DAX), and a visualization layer" is fine. No fix needed here.

- **"Most of the confusion beginners hit comes from not realizing Power BI is really three products sharing one file format."** — Mild LinkedIn-ism. Rewrite: "Beginners usually get confused because Power BI is three separate engines sharing one `.pbix` file."

- **"Two habits pay off here."** — Generic connective filler. Cut it and just list the habits. The reader doesn't need a runway.

- **"The layout rules that matter most:"** — Same pattern. These "rules that matter" openers are the AI default when it has a list and no thesis. Either lead with the strongest rule as prose ("The single most important layout rule is one question per visual — if a chart answers two, split it. Beyond that: …") or drop the framing sentence entirely.

- **"That loop covers every concept you need to understand the rest of the platform. Everything after that is depth: better DAX, better modeling, better visual design."** — The colon list at the end is a classic ChatGPT closer. Rewrite: "Once you've done that once, the rest of Power BI is depth — better DAX, tighter models, cleaner visuals — not new concepts."

- **"A quick note on a common beginner misconception:"** — This template phrase appears in almost every LLM intro article. Replace with something direct: "One caveat on `EARLIER`, which is often described as 'the previous row' — it actually refers to an outer row context..."

- **"The choice that matters most early on is the storage mode:"** — Also slightly LLM-y ("the X that matters most"). Rewrite: "Your first real decision is storage mode."

- **Em-dash usage**: only two in the article — actually restrained. Good.

- **"It is not a spreadsheet replacement... It is not a database. It is not a place to store your source of truth."** — The triple negative is effective here, keep.

- **FAQ intro question phrasing** is clean, no "Great question!" tics.

Overall the AI-ism density is low but the "framing sentence before every list" habit is the main tell. Fix that rhythm and it reads human.

## 2. Topic Fit

**Verdict on fit: weak for the stated 1k UV/day organic goal.**

- "what is power bi" is a head term dominated by Microsoft's own product page, Wikipedia, and every enterprise blog on the internet (Microsoft Learn, SQLBI, Guy in a Cube, Enterprise DNA, Datacamp, Coursera, Simplilearn, etc.). A small site will not rank top-20 for this in any realistic timeframe.
- The slug `/what-is-power-bi` is also a one-shot: it can't be expanded into a cluster without competing with itself.
- Category is `visualization`, which is wrong — this is a fundamentals/overview piece. Misfiled category will hurt internal linking and taxonomy.

**Better angle than the head term**, to actually pull evergreen long-tail UV:

- `/power-bi-vs-excel-pivot-tables/` — narrower, high commercial intent, links naturally to your existing Excel-flavored tutorials.
- `/power-bi-free-vs-pro-license/` — real search volume, unclear answers elsewhere, fits your FAQ voice.
- `/power-bi-desktop-vs-service/` — you already answer this in FAQ; promote it to its own page.
- `/power-bi-import-vs-directquery-beginner/` — you have a `/tutorials/directquery-vs-import-mode/` already, so this would cannibalize. Consider instead `/power-bi-star-schema-explained-simply-for-beginners/` targeting the "what is star schema power bi" mid-tail.

If you keep this URL, treat it as a **hub page** and ensure every related tutorial links back up to it, and it links down aggressively. Right now the Related Reading section is doing the work but the article body only has ~2 internal links organically. For a pillar page that's too few.

## 3. Errors

### Frontmatter

- `category: visualization` — should be `fundamentals` or `getting-started`. This is not a visualization tutorial.
- `pubDate: 2026-10-14` — future date. If the site publishes in real time, this will not publish. Flag it.
- `tags: ["fundamentals"]` — tags are too thin; add `intro`, `overview`, `power-query`, `dax` for discoverability.
- `author: Mireia` — confirm this matches the expected author slug convention elsewhere.
- No `readingTime`, `ogImage`, or `canonical` — check whether your schema requires these. If other articles have them, add.

### Terminology / code

- **"VertiPaq"** — correct spelling. Good.
- **EARLIER paragraph**: "it actually refers to an outer row context and only behaves as expected when there is a nested row context" — this is accurate but the phrasing "only behaves as expected" is misleading. `EARLIER` works on any row context; the issue is that inside a *calculated column*, the implicit row context is already the current row, so `EARLIER` refers to that same row (useless). The "previous row" description is wrong because `EARLIER` doesn't iterate. Suggested fix: "`EARLIER` refers to a row context from an outer iterator, not 'the previous row'. It's most useful when you have nested row contexts — for example, a `SUMX` over a table inside a calculated column."
- **DAX example `Sales YoY %`**: Variable name `PriorSales` gets assigned the result of `CALCULATE([Total Sales], SAMEPERIODLASTYEAR(...))`, but the comment above the block calls the whole thing a "basic revenue measure using `CALCULATE`". The first measure (`Total Sales`) doesn't use `CALCULATE` at all — it uses `SUMX`. The intro line is wrong. Rewrite: "A basic revenue measure, plus a time-intelligence measure built on `CALCULATE`."
- **`SAMEPERIODLASTYEAR`** requires a marked date table or an explicit date column; the example assumes `'Date'[Date]` is a proper date table. Add a half-sentence noting that, or beginners will copy it and get wrong results.
- **Power Query example**: `Excel.Workbook(File.Contents("C:\Reports\Sales.xlsx"), null, true)` — this is valid but you never explain the `null, true` arguments. Either drop them into a comment or omit for the reader's sake.
- **"`Import mode` copies data into Power BI's in-memory engine (VertiPaq)"** — accurate. Fine.
- **"Fabric capacities sit above both and add shared compute"** — correct but "sit above both" is loose. Fabric capacities can host Pro and PPU workspaces; they're not a "higher tier" of PbI license in the ordering you imply. Rewrite or cut.

### Internal linking

All links in Related Reading verify against the provided slug list:

- `/tutorials/power-bi-common-mistakes-beginners/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/dax-basics/` ✅
- `/tutorials/de-power-query-getting-started/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/measure-vs-calculated-column/` ✅
- `/tutorials/power-bi-dashboard-design-principles/` ✅
- `/tutorials/filter-context-row-context-explained/` ✅

**However**: the article body contains **zero inline internal links**. For a pillar page, that's an error of omission. Add links where the text already names the topic:

- "star schema" → `/tutorials/data-modeling-star-schema/`
- "`CALCULATE` is the function that makes Power BI powerful" → `/tutorials/calculate-function/` or `/tutorials/dax-calculate-function/`
- "date table" → `/tutorials/power-bi-date-table/`
- "Conditional formatting is where a lot of report polish lives" → `/tutorials/conditional-formatting-complete-guide/`
- "row-level security" — no matching slug, leave unlinked
- "DirectQuery" in FAQ → `/tutorials/directquery-vs-import-mode/`

### FAQ / format

- FAQ format (H3 `### Q: ...`) is consistent. Good.
- Six FAQs is a lot for a 1,400-word article. Two of them ("Do I need a paid license", "Do I need to know DAX") are essentially the same question from different angles. Consider merging.
- The FAQ answers overlap significantly with body content (Import vs DirectQuery, Excel vs Power BI, star schema). Consider trimming the FAQ to the three genuinely supplementary questions so Google doesn't see duplication between your own body and FAQ sections.
- No `FAQPage` schema instructions indicated — confirm your Astro layout emits JSON-LD for the FAQ block, otherwise the format is costing you SERP real estate for nothing.

### Other

- Register in the article is inconsistent: mostly second-person ("you connect once"), but "A `.pbix` file holds all three layers" and the closing paragraph switch to a more formal instruction voice. Pick one and stick.
- The "What Power BI Is Not" section is the strongest part of the article and is buried too late. Consider pulling it up to right after the intro — it disambiguates the topic faster than five step-by-step sections do.
- Title "What Is Power BI? A Complete Beginner Overview" — "Complete Beginner Overview" is a weak modifier. If keeping this URL, retitle to "What Is Power BI? A Beginner's Guide to Power Query, DAX, and Reports" for a more specific SERP snippet.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the frontmatter category and future date, correct the `CALCULATE`/`SUMX` label on the DAX block, tighten the `EARLIER` explanation, and add inline internal links before publishing. Longer term, treat this as a hub, not a ranker.