# Review: power-bi-map-visual

# Editorial Review: `power-bi-map-visual`

## 1. AI-isms

The draft is unusually clean for AI-generated content, but a few tells remain.

- **Vague opener.** "Power BI ships with several map visuals, and they are not interchangeable." This is fine as a hook but the follow-on sentence — "Picking the wrong one produces a report that either misleads the reader, renders blank tiles, or silently aggregates your data into a shape nobody asked for" — is triadic filler with a fake-conversational "nobody asked for." Tighten to: *"Pick the wrong one and your report either misleads the reader, renders blank tiles, or silently aggregates the data into an unhelpful shape."*
- **"That last question matters more than the others."** Reader-instruction filler. Cut, or fold into the previous sentence: *"That last question matters most: a map with twelve cities tells you less than a twelve-row bar chart, at higher reading cost."*
- **"It looks impressive and reads poorly, so reserve it for one or two top-level numbers."** Fine, but the "it looks impressive and reads poorly" is a stock AI contrast pair. Consider: *"The Globe style is 3D eye candy with worse legibility; reserve it for a single headline number."*
- **"worth knowing"** and **"in practice"** — soft hedges. "Two more filled map behaviours worth knowing" → "Two more filled map behaviours:".
- **"The classic mistake is…"** — acceptable but repeated AI phrase; vary or drop "classic."
- **Mechanical FAQ intros.** Each Q is fine. No issue.
- **Em-dashes.** Used sparingly and correctly given asides; no abuse. Pass.
- **"walks through"** — standard tutorial-voice filler. Consider "covers" or just delete: *"This article covers the map visuals…"*

No hallucinated "In today's fast-paced world…" opener, no "delve," no "landscape." Overall the prose is disciplined.

## 2. Topic fit

- **Long-tail rankability: strong.** `power-bi-map-visual` sits behind a genuine searcher cluster (Azure Maps vs Map vs Filled map vs Shape map), and the article answers the exact comparison query. The comparison table is the kind of thing that earns featured-snippet real estate.
- **Organic UV potential: moderate.** Map visuals are a real Power BI topic, but search volume is secondary compared to chart formatting / DAX. Realistic ceiling is a few hundred sessions/month unless it competes for "power bi filled map" and "power bi shape map topojson" — both of which it does address.
- **Gaps for the 1k UV/day goal:**
  - The article never links to a possible internal piece on **latitude/longitude data category** or **geocoding troubleshooting** — if that content exists, link it. If not, that is a stronger standalone post than this one.
  - No screenshots/diagrams referenced. Google Images and rich results for map tutorials favor visual guides. Even two annotated PNGs would lift CTR materially.
  - The M code block for lat/long cleanup is the highest-value unique asset in the piece and is buried mid-article. Promote the concept ("clean lat/long in Power Query") into the title or subheading so it can rank on its own.
- **Better angle to consider:** "Why your Power BI filled map shows only one colour" as an H1. That single question has higher intent and less competition than the generic comparison. Current piece covers it only as an FAQ.

## 3. Errors

### Terminology / code

- **"Rectangle Polygon + layers" in Azure Maps row.** Azure Maps is not purely polygon; it is point/bubble + heatmap + reference layers. The Geometry column value "Point + layers" in the table is OK but the "Best for" text mentions "live traffic layers" — Azure Maps in Power BI does not expose live traffic layers as a feature. Remove or soften to "reference tile layers."
- **"hard limit: 3,500 data points."** Microsoft documentation specifies the Map visual caps at 3,500 points, but the visual *does not* silently drop rows above that — it plots the first 3,500 and warns. "Starts dropping rows" implies random loss; be precise: *"only the first 3,500 points are plotted."*
- **Shape map "no basemap"** — technically correct, but the shape map does render the polygon fills over a neutral canvas; the phrasing implies it renders nothing. Reword: *"it has no tile basemap, so roads and city labels cannot be shown underneath."*
- **Filled map "no drill-down"** — correct.
- **"Bing's geocoder"** — Bing Maps for Enterprise was retired; Power BI now uses the Azure Maps geocoder backend even for legacy Map/Filled Map visuals. The article uses "Bing's geocoder handles these inconsistently" — technically outdated. Replace "Bing's geocoder" with "the built-in geocoder" throughout, or note that the geocoding service has migrated to Azure Maps.
- **"It only works with a single geographic category in the Location well and a single measure in Legend."** Wrong well. Filled map uses **Location** and **Color saturation** (in newer versions) or **Legend** (older builds). As written it conflates wells. State the version or say "the measure well (labelled Colour saturation or Legend depending on your build)."
- **M code — `Table.SplitColumn` signature.** The 4-argument form is `Table.SplitColumn(table, column, splitter, newColumnNames)`. The draft passes `{"LatDeg", "LatHemi"}` as the 4th argument — that is the *new column names list*. Correct. But `Splitter.SplitTextByAnyDelimiter({" ", "°"})` will produce no split on the string `"51.5074 N"` because there is a space, which is fine — but the resulting `LatHemi` will be `"N"` with no trailing whitespace. OK. However `Text.Upper([LatHemi]) = "S"` — if `LatHemi` is `null` (no hemisphere suffix), `Text.Upper(null)` errors. Add a null guard: `each if [LatHemi] <> null and Text.Upper([LatHemi]) = "S" then -_ else _`.
- **Same block:** the code never references the `SignedLat`/`SignedLon` chain end to a final `in` value consistently — the `in SignedLon` returns the table after both transforms, which is fine, but the intermediate `SignedLat` is assigned and immediately overwritten. Cosmetic, but rename to `Step1`/`Step2` or inline.
- **DAX `Revenue per Capita`:** `SUM(Population[TotalPopulation])` assumes a Population table joined correctly. Since this is a ratio across time, if the measure is sliced by anything other than region the denominator may aggregate incorrectly. Add a one-line note or use `AVERAGE`.
- **"Colour"** vs **"Color"** — the article mixes British ("colour", "categorised", "bucketises") and American spelling ("Color saturation" is the actual UI label). Standardize to American unless the site's locale is UK. This is a real SERP/consistency issue.

### Frontmatter

- `pubDate: 2026-10-13` — future date. If today is before that, the article will not publish on most Astro setups. Flag for the editor to confirm intent.
- `category: visualization` — verify the site's canonical category slug. Others may use `visualizations` or `visuals`.
- `tags: ["maps", "visualization"]` — fine.
- `featured: false` — fine.
- `draft: false` with a future `pubDate` is contradictory for most SSGs. Pick one.

### Internal links

All seven links in **Related Reading** verified against the real slug list:
- `/tutorials/power-bi-dashboard-design-principles/` ✅
- `/tutorials/power-bi-common-mistakes-beginners/` ✅
- `/tutorials/data-modeling-star-schema/` ✅
- `/tutorials/measure-vs-calculated-column/` ✅
- `/tutorials/conditional-formatting-charts-power-bi/` ✅
- `/tutorials/directquery-vs-import-mode/` ✅
- `/tutorials/dax-basics/` ✅

**Inline link in FAQ** — "our DirectQuery vs Import mode guide" links to `/tutorials/directquery-vs-import-mode/`. ✅

**Missed link opportunities** (all available in your real-slug list and topically relevant):
- "conditional formatting" mentioned in FAQ Q3 → link `/tutorials/conditional-formatting-complete-guide/` or `/tutorials/conditional-formatting-power-bi/`.
- "calculated column" in FAQ Q3 → link `/tutorials/measure-vs-calculated-column/` (already in Related; consider an inline link instead of or in addition to the tail link).
- "Power Query" in the M code section → link `/tutorials/de-power-query-getting-started/`.
- "DAX variables" if you add a note about the measure structure → `/tutorials/dax-variables-best-practices/`.

No broken or imagined links found. Good hygiene.

### FAQ / format

- Five FAQs — reasonable. Each answer is 2–4 sentences.
- **Q: "Can I use conditional formatting on map bubbles?"** The answer correctly says no, but should point to a workaround article. Add the internal link noted above.
- **Q: "Why does my filled map show only one colour?"** Overlaps with the "additive measure" warning in the body. Fine, but the FAQ answer repeats "switch to a bar chart" verbatim from the body. Vary the phrasing.
- Missing: a "further reading" mention of the Azure Maps account / pricing. Not required, but a reader hitting the Azure Maps recommendation will want it.
- **Heading levels:** H2 for sections, H3 only within FAQ as bold rather than H3 — consistent. Pass.

---

VERDICT: PUBLISH-AFTER-FIX — correct the Filled map / Legend well terminology, replace outdated "Bing's geocoder" references, add the null guard in the M code, standardize US vs UK spelling, resolve the future `pubDate`, and add the two missed internal links.