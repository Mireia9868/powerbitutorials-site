# Review: power-bi-service-vs-desktop

# Editorial Review: `power-bi-service-vs-desktop`

## 1. AI-isms

The draft is mostly clean — it has a confident, practitioner voice and avoids the usual "In today's fast-paced world" openings. But several tics are worth flagging:

- **"That table is the whole comparison compressed. The rest of this article explains the rows."** — Mechanically scaffolding. Cut the second sentence; the table speaks for itself. First sentence alone is fine but borders on filler.
- **"The rest of this article explains the rows."** — Classic LLM signposting. Delete.
- **"A few things that matter for beginners:"** — Reads like a chatbot hedging. Rewrite: "Three things trip up beginners first:" and lead with the concrete items.
- **"That tradeoff is worth its own read, and the import-vs-DirectQuery decision shapes everything downstream."** — Two clauses saying the same thing. Keep one. Suggest: "That tradeoff shapes everything downstream — see the import-vs-DirectQuery guide."
- **"That last point trips people up constantly."** — Slightly English-teacher, but acceptable. Keep.
- **"Refresh failures are the most common Service-only problem."** — Fine, but "Service-only problem" is jargon-y. "The most common problem in the Service is a failed refresh." Cleaner.
- **"Think of edit-in-browser as a patch tool, not a replacement."** — Good line. Keep.
- **Em-dash use:** One instance ("see the import-vs-DirectQuery decision...") plus a few colons and semicolons. Not excessive. Pass.
- **Vague opener** — "Power BI is two products with one name." is strong. Keep.
- **"Licences and sharing in one paragraph"** — Section header reads like a constraint ("I only have one paragraph") rather than a topic. Rename to "Licences: who pays for what."
- **"Everyone real happens by moving a file..."** — I flagged this in Errors below; it reads like a typo artifact but if intentional it's confusing.

No ChatGPT intro/outro boilerplate, no "delve," no "in conclusion." Good.

## 2. Topic fit

**Long-tail rankability: yes.** "Power BI Service vs Desktop" is a real beginner/mid query with steady volume and low commercial competition. Perfect fit for the site's tutorial positioning.

**Serves the 1k organic UV/day goal: qualified yes, with a caveat.** The article is comprehensive, but two improvements would widen its query surface:

1. **Missing high-intent H2s.** Real search queries around this topic include "can I use Power BI Desktop on Mac," "Power BI Desktop vs Service refresh difference," "do I need a license to use Power BI." Right now those are buried in FAQ. Promote a couple:
   - "Power BI on Mac: what works and what doesn't"
   - "Do you need a licence to share a report?"
2. **Latent angle you're leaving on the table:** "What can't you do in the Service?" answered as a scannable list near the top would capture a lot of long-tail. You gesture at it ("Service has no full report authoring") but don't flesh it out.

**Better angle?** Minor: the title could be sharpened for CTR. "Power BI Service vs Desktop: What's the Difference" is generic. Something like "Power BI Service vs Desktop: Where You Actually Build, Publish, and Refresh" is longer but higher signal. Optional — the current title is safe.

**Internal-link strategy:** 9 related links is generous but weak. Six of the nine (star schema, bidirectional filtering, DAX basics, dashboard design, drill-through, calc tables) are generic "beginner model" links, not topical continuations. Better set:
- Keep: `directquery-vs-import-mode`, `power-bi-common-mistakes-beginners`
- Add: `power-bi-field-parameters` (edit-in-browser context), `power-bi-performance-analyzer-guide` (troubleshooting after publish), `power-bi-percentage-of-total` (only if you mention it — you don't) — actually **drop this**
- Add: `power-bi-drill-through` is fine; keep.
- Recommend paring to 5-6 focused links. Scattershot related-reading dilutes signal.

## 3. Errors

### Terminology / factual
- **"Service has no full report authoring."** — Slightly overstrong. Edit-in-browser exists (you clarify later). Recommend: "Service has limited authoring — no Power Query or model editor."
- **"Row-level security enforcement | Preview only"** in the table. "Preview only" is confusing; Desktop *does* fully evaluate RLS via View-as-role, it just doesn't enforce it for other users. Rewrite the cell: "Test only (View as role)."
- **"Scheduled refresh... from 8 times a day on Pro up to 48 on Premium/Fabric capacity."** — Numbers are correct for Pro (8) and Premium (48), but **PPU is also 48**, and you list PPU as a tier elsewhere without the refresh rate. Consider: "8×/day on Pro; 48×/day on PPU/Premium/Fabric capacity." Small accuracy win.
- **`USERPRINCIPALNAME()` returns empty string in Desktop.** — This is *conditionally* true. In Desktop it returns the value of the effective user in View-as-role; in the *preview/default* context it can return the Windows UPN or be blank depending on the Desktop version and whether "Account" is configured. The DAX snippet implies it's always blank. Soften: "often returns blank or the local user; in the Service it always resolves to the signed-in account." Also consider `USERNAME()` vs `USERPRINCIPALNAME()` — the latter is the one the Service uses for RLS, so this is a defensible pick, but call out the caveat.
- **"OneDrive... no gateway" FAQ.** — Correct for OneDrive for Business / SharePoint via cloud connection, but the "Excel file on a network share" example at the end of the same sentence contradicts it under a careless read. The share needs a gateway; OneDrive doesn't. Reword for clarity: "…such as a SQL Server on an internal VM or an Excel file on a UNC network share."
- **"Desktop works... macOS via VM or Fabric"** in table. — Fabric isn't a macOS workaround for Desktop; it's a separate cloud authoring environment. The parenthetical is misleading. Either delete or rewrite: "Windows only (macOS users: VM, or build in Fabric/Service)."
- **"That last point trips people up constantly."** — Fine, but the preceding bullet ("You edit the report in the Service... Republishing from Desktop overwrites it") is the load-bearing point and could use a bold callout. Optional.

### Code
- The DAX snippet is syntactically correct (`VAR/RETURN`, `USERPRINCIPALNAME()`, `ISBLANK`). No issues. Consider adding expected outputs as a comment for the Service case.

### Frontmatter
- `pubDate: 2026-10-08` — Future date. If this is genuinely scheduled, fine; otherwise a slip. Verify.
- `category: service` — Presumably valid for your schema; check against your category enum (common alternative: `service` vs `power-bi-service`).
- `difficulty: Beginner` — Matches content. Good.
- `description` truncates mid-thought ("...you install to build reports."). Reads like it was cut to hit a character count. Rewrite to be self-contained: "Power BI Desktop builds reports; Power BI Service hosts and shares them. Here's the difference that matters in practice."
- `tags: ["service", "desktop"]` — Redundant with category, low SEO value. Suggest: `["power-bi-service", "power-bi-desktop", "sharing", "refresh"]`.
- `author: Mireia` — Fine.
- `featured: false`, `draft: false` — Fine.

### Internal links
All nine slugs exist in the real slugs list. Verified:

| Link | Exists? |
|---|---|
| directquery-vs-import-mode | ✅ |
| power-bi-common-mistakes-beginners | ✅ |
| power-bi-excel-integration | ✅ |
| data-modeling-star-schema | ✅ |
| bidirectional-filtering-guide | ✅ |
| dax-basics | ✅ |
| power-bi-dashboard-design-principles | ✅ |
| power-bi-drill-through | ✅ |
| calculated-tables-what-if-parameters | ✅ |

However:
- **Link syntax is broken.** You wrote `[url](/url/)` twice for every link — markdown will render the URL as both text and destination. Standard form is `[descriptive text](/url/)`. This is repeated 9 times. Fix across the whole block.
- **No in-body links.** The Related Reading section is a wall of links; the article body doesn't link out once. Add inline links at "import-vs-DirectQuery decision" → `/tutorials/directquery-vs-import-mode/`, and at "star schema" if you mention it (you don't — fine, drop it from related instead).
- **`calculated-tables-what-if-parameters`** is weakly related. Consider swapping for `power-bi-field-parameters` (edit-in-browser adjacent) or `power-bi-performance-analyzer-guide` (Service troubleshooting).

### FAQ / format
- FAQ uses `### Q:` prefix. Confirm this matches your site's FAQ schema regex. Many Astro/MDX setups expect `<FAQ>` components or `## Q:` — verify. If it renders as plain H3 with "Q:" visible, that's ugly.
- Q4 ("Can I edit in Service and download?") overlaps Q1's "without installing Desktop" and the handoff section. Consider merging or dropping.
- No `## Conclusion` — the "Practical advice" section acts as one. That's fine stylistically but your site may expect a conclusion header for TOC consistency. Check.

### One more thing
- **"Everyone real happens by moving a file..."** If this is a typo, fix. If you meant "Everything real happens..." — fix. As written it's incoherent.

---

**VERDICT: PUBLISH-AFTER-FIX** — fix the broken markdown link syntax (9 instances), the "Everyone real" typo, the `USERPRINCIPALNAME()` overstatement, and trim 3-4 weaker related links; then publish.