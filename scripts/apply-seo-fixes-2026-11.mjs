#!/usr/bin/env node
// One-off patch for the 2026-11 SEO/funnel review.
//
// Added to the branch, run once by .github/workflows/_seo-fixes.yml, then
// deleted by the very commit that carries its output: the branch keeps the
// fixes, not the machinery.
//
// Every anchor must match exactly once. If any anchor is missing or ambiguous
// the script exits non-zero before writing a single file, so a drifted source
// file can never produce a half-applied patch.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const MAX_TITLE = 55;
const staged = new Map();
const problems = [];

function current(rel) {
  if (staged.has(rel)) return staged.get(rel);
  return fs.readFileSync(path.join(ROOT, rel), "utf8");
}

function stage(rel, txt) {
  staged.set(rel, txt);
}

function replaceOnce(rel, from, to) {
  const txt = current(rel);
  const at = txt.indexOf(from);
  if (at === -1) {
    problems.push(rel + " :: anchor not found :: " + from.split("\n")[0].slice(0, 80));
    return;
  }
  if (txt.indexOf(from, at + from.length) !== -1) {
    problems.push(rel + " :: anchor not unique :: " + from.split("\n")[0].slice(0, 80));
    return;
  }
  stage(rel, txt.slice(0, at) + to + txt.slice(at + from.length));
}

function replaceRegion(rel, startMarker, endMarker, to) {
  const txt = current(rel);
  const a = txt.indexOf(startMarker);
  const b = txt.indexOf(endMarker, a + 1);
  if (a === -1 || b === -1) {
    problems.push(rel + " :: region not found :: " + startMarker.slice(0, 60));
    return;
  }
  stage(rel, txt.slice(0, a) + to + txt.slice(b));
}

// ---------------------------------------------------------------------------
// 1. Thirteen source titles were still 56-60 characters after the cap moved
//    from 60 to 55. Lowering the cap only drops the 19-character brand suffix
//    from pages whose title is 37-55 characters; a title that is itself over
//    55 keeps its length, so those thirteen have to be rewritten.
// ---------------------------------------------------------------------------
const TITLES = {
  "calculate-function": "CALCULATE in Power BI: Syntax and Filter Context",
  "conditional-formatting-power-bi": "Conditional Formatting in Power BI: Rules & Icons",
  "dax-switch-function": "DAX SWITCH: Syntax, 4 Patterns, and Why It Blanks",
  "dax-troubleshooting-guide": "DAX Troubleshooting Guide: 15 Errors and Fixes",
  "filter-context-row-context-explained": "Filter Context vs Row Context in DAX, Explained",
  "power-bi-drill-through": "Power BI Drill Through: Fields and Filters",
  "power-bi-performance-analyzer": "Performance Analyzer: Find Slow Visuals in Power BI",
  "power-bi-sales-dashboard-tutorial": "Build a Sales Dashboard in Power BI, End to End",
  "power-bi-tooltips-page-reports": "Power BI Tooltips: Hover Reports to Full Pages",
  "power-bi-visual-calculations": "Power BI Visual Calculations: 2026 Complete Guide",
  "power-query-group-by": "Power Query Group By: Count, Sum and All Rows",
  "power-query-parameters-dynamic-sources": "Power Query Parameters: Dynamic Data Sources",
  "power-query-query-folding": "Query Folding in Power BI: What Breaks It",
};

for (const slug of Object.keys(TITLES)) {
  const title = TITLES[slug];
  const rel = "src/content/tutorials/" + slug + ".md";
  if (title.length > MAX_TITLE) {
    problems.push(rel + " :: replacement title is " + title.length + " chars");
    continue;
  }
  const txt = current(rel);
  const fm = txt.match(/^---\n([\s\S]*?)\n---/);
  if (!fm) {
    problems.push(rel + " :: no frontmatter");
    continue;
  }
  if (!/^title:/m.test(fm[1])) {
    problems.push(rel + " :: no title key");
    continue;
  }
  const newFm = fm[1].replace(/^title:.*$/m, function () {
    return 'title: "' + title + '"';
  });
  stage(rel, "---\n" + newFm + "\n---" + txt.slice(fm[0].length));
}


// ---------------------------------------------------------------------------
// 2. FAQPage schema only ever matched one of the three question shapes.
// ---------------------------------------------------------------------------
const NEW_FAQ = String.raw`// FAQPage schema. 57 of the 81 articles carry a Q&A section, but they use two
// heading spellings and three question shapes, so the original single regex
// only ever matched a third of them:
//   ## FAQ (54 articles) / ## Frequently Asked Questions (3 articles)
//   **Question?** followed by the answer        -> 30 articles
//   ### Q: Question? followed by the answer     -> 27 articles
// Matching one shape silently drops the others. 28 pages emitted FAQPage
// before this, 57 do now, 246 questions in total.
// Google tightened FAQ rich results in 2023-08, so treat this as semantic
// markup rather than a CTR lever.
const FAQ_HEADING = /^##\s+(?:FAQ|Frequently\s+Asked\s+Questions)\s*$/im;

function extractFaq(body: string): { q: string; a: string }[] {
  const heading = body.match(FAQ_HEADING);
  if (!heading || heading.index === undefined) return [];
  const rest = body.slice(heading.index + heading[0].length);
  const stop = rest.search(/^##\s+/m);
  const section = stop === -1 ? rest : rest.slice(0, stop);

  const items: { q: string; a: string }[] = [];
  const clean = (s: string) =>
    s
      .replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
      .replace(/\s+/g, " ")
      .trim();
  const keep = (q: string, a: string) => {
    if (q.endsWith("?") && a.length > 40) items.push({ q, a });
  };

  // Shape A — "### Q: question?" headings
  const h3 = /^###\s+(?:Q:\s*)?(.+?)\s*\n+([\s\S]*?)(?=\n###\s|\n##\s|$)/gm;
  let m: RegExpExecArray | null;
  while ((m = h3.exec(section))) {
    keep(m[1].replace(/^Q:\s*/i, "").trim(), clean(m[2]));
  }
  if (items.length) return items;

  // Shape B — bold question line followed by the answer
  const bold = /\*\*(.+?)\*\*\s*\n+([\s\S]*?)(?=\n\*\*|\n#{2,3}\s|$)/g;
  while ((m = bold.exec(section))) {
    keep(m[1].trim(), clean(m[2]));
  }
  return items;
}
`;

replaceRegion(
  "src/pages/tutorials/[slug].astro",
  "// FAQPage schema: 58 articles",
  "const faqItems = extractFaq(tutorial.body);",
  NEW_FAQ + "\n"
);


// ---------------------------------------------------------------------------
// 3. Privacy policy never mentioned the newsletter. The signup form posts an
//    address to Buttondown, which was disclosed nowhere on the site.
// ---------------------------------------------------------------------------
const P_DESC_FROM = String.raw`  description="How Power BI Tutorials collects and protects your data: cookie consent, analytics and advertising, plus how to opt out or request deletion."
`;
const P_DESC_TO = String.raw`  description="How Power BI Tutorials handles your data: cookies, analytics, advertising and newsletter signups, plus how to opt out or request deletion."
`;
const P_LEADIN_FROM = String.raw`        We use this solely to respond to your inquiry.
      </p>
`;
const P_LEADIN_TO = String.raw`        We use this solely to respond to your inquiry.
      </p>
      <p>
        When you subscribe to the newsletter we collect the email address you
        type into the signup form and the date you subscribed. We use it for
        one purpose: sending you the newsletter.
      </p>
`;
const P_SECTION_FROM = String.raw`      <h2>How we use information</h2>
`;
const P_SECTION_TO = String.raw`      <h2>Newsletter</h2>
      <p>
        The signup form is not hosted by us. It posts the address straight to
        <strong>Buttondown</strong> (Buttondown, LLC), our email service
        provider, which stores it in the audience list for this site and sends
        the emails on our behalf. The address never passes through a server we
        control.
      </p>
      <ul>
        <li><strong>What is collected</strong> — the email address you type, the time you subscribed, and the usual delivery metadata (opens, clicks, and an approximate location derived from the IP address used at signup). Nothing else.</li>
        <li><strong>What we do with it</strong> — send new tutorials and occasional product updates. We do not sell, rent, or share the list, and we do not add subscribers to any advertising audience.</li>
        <li><strong>Confirming</strong> — if a confirmation step is enabled on the sending account, you receive one email asking you to click a link. Until that link is clicked the subscription stays inactive and no newsletter is sent.</li>
        <li><strong>Unsubscribing</strong> — every email carries a one-click unsubscribe link. It takes effect immediately and needs no reply.</li>
        <li><strong>Deleting</strong> — email <a href="mailto:privacy@powerbitutorials.com">privacy@powerbitutorials.com</a> and we delete the address from Buttondown.</li>
        <li><strong>Buttondown's own processing</strong> — described in <a href="https://buttondown.com/legal/privacy" rel="noopener">Buttondown's privacy policy</a>.</li>
      </ul>
      <p>
        The newsletter is a separate relationship from analytics and
        advertising: subscribing does not opt you into either, and refusing
        cookies does not unsubscribe you from the newsletter.
      </p>

      <h2>How we use information</h2>
`;
const P_VENDOR_FROM = String.raw`        <li><strong>Google Analytics</strong> — web analytics (Google LLC)</li>
`;
const P_VENDOR_TO = String.raw`        <li><strong>Google Analytics</strong> — web analytics (Google LLC)</li>
        <li><strong>Buttondown</strong> — newsletter delivery (Buttondown, LLC)</li>
`;
const P_RETENTION_FROM = String.raw`        We retain contact-form messages for up to 12 months. Analytics data
`;
const P_RETENTION_TO = String.raw`        We retain contact-form messages for up to 12 months. Newsletter
        addresses stay in Buttondown until you unsubscribe or ask us to delete
        them. Analytics data
`;
const PRIVACY = "src/pages/privacy.astro";
replaceOnce(PRIVACY, "<p class=\"updated\">Last updated: July 19, 2026</p>", "<p class=\"updated\">Last updated: November 18, 2026</p>");
replaceOnce(PRIVACY, P_DESC_FROM, P_DESC_TO);
replaceOnce(PRIVACY, P_LEADIN_FROM, P_LEADIN_TO);
replaceOnce(PRIVACY, P_SECTION_FROM, P_SECTION_TO);
replaceOnce(PRIVACY, P_VENDOR_FROM, P_VENDOR_TO);
replaceOnce(PRIVACY, P_RETENTION_FROM, P_RETENTION_TO);

// ---------------------------------------------------------------------------
// 4. INDEXNOW_KEY in src/consts.ts was imported by nothing, and both the
//    script and the workflow carried their own copy of the literal.
// ---------------------------------------------------------------------------
const I_KEY_FROM = String.raw`KEY = "pbt2026indexnow7f3a9c2e5b8d1a4f6c0e3b7d"
`;
const I_KEY_TO = String.raw`CONSTS = REPO / "src" / "consts.ts"


def indexnow_key() -> str:
    """key 只在 src/consts.ts 里维护一份。

    脚本、workflow、前端各存一份的话，改一处忘一处就会变成
    「key 文件能访问、请求里的 key 对不上」这种最难查的 403。
    """
    text = CONSTS.read_text(encoding="utf-8")
    m = re.search(r'INDEXNOW_KEY\s*=\s*"([^"]*)"', text)
    if not m or not m.group(1):
        sys.exit("[x] src/consts.ts 里 INDEXNOW_KEY 为空，IndexNow 无法使用")
    return m.group(1)

`;
const I_PUSH_FROM = String.raw`def push(urls):
    if not urls:
        print("[i] 没有符合条件的 URL，跳过")
        return 0
`;
const I_PUSH_TO = String.raw`def push(urls):
    if not urls:
        print("[i] 没有符合条件的 URL，跳过")
        return 0
    key = indexnow_key()
`;
const I_ARGS_FROM = String.raw`    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
`;
const I_ARGS_TO = String.raw`    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--print-key",
        action="store_true",
        help="打印 src/consts.ts 里的 INDEXNOW_KEY（workflow 用它校验 key 文件）",
    )
    args = ap.parse_args()

    if args.print_key:
        print(indexnow_key())
        return 0
`;
const I_DOC_FROM = String.raw`  · key 文件必须能从公网访问：https://powerbitutorials.com/<key>.txt
    它在 public/ 下，构建后会出现在站点根目录。
`;
const I_DOC_TO = String.raw`  · key 只在 src/consts.ts 的 INDEXNOW_KEY 里维护，文件名必须与它一致：
    public/<KEY>.txt，构建后出现在站点根目录，公网地址
    https://powerbitutorials.com/<KEY>.txt
    --print-key 会打印当前值，workflow 用它拼校验地址，不再另存一份。
`;
const IDX_PY = "scripts/indexnow.py";
replaceOnce(IDX_PY, I_DOC_FROM, I_DOC_TO);
replaceOnce(IDX_PY, I_KEY_FROM, I_KEY_TO);
replaceOnce(IDX_PY, I_PUSH_FROM, I_PUSH_TO);
replaceOnce(IDX_PY, '"key": KEY,', '"key": key,');
replaceOnce(IDX_PY, '"keyLocation": f"{SITE}/{KEY}.txt",', '"keyLocation": f"{SITE}/{key}.txt",');
replaceOnce(IDX_PY, I_ARGS_FROM, I_ARGS_TO);

const I_WF_FROM = String.raw`          KEY=pbt2026indexnow7f3a9c2e5b8d1a4f6c0e3b7d
`;
const I_WF_TO = String.raw`          # key 从 src/consts.ts 读，这里不再另存一份
          KEY=$(python scripts/indexnow.py --print-key)
`;
replaceOnce(".github/workflows/indexnow.yml", I_WF_FROM, I_WF_TO);

// ---------------------------------------------------------------------------
// 5. Every redirect target was written without a trailing slash. astro.config
//    sets trailingSlash: "always", so /tutorials/foo itself answers 308 to
//    /tutorials/foo/ — two hops before a page renders, and one more for the
//    .html rule, which pointed at the no-slash form as well.
// ---------------------------------------------------------------------------
const REDIRECTS = String.raw`# AdSense low-value-content remediation — consolidate duplicate tutorials (301)
#
# Every target carries its trailing slash. astro.config.mjs sets
# trailingSlash: "always", so a target written as /tutorials/foo answers
# /tutorials/foo -> 308 -> /tutorials/foo/, i.e. two hops before the page
# renders. The old .html rule pointed at the no-slash form, which stacked a
# third hop on top. One hop is enough.
#
# P1 首批 3 对
/tutorials/power-bi-drillthrough /tutorials/power-bi-drill-through/ 301
/tutorials/power-bi-drillthrough/ /tutorials/power-bi-drill-through/ 301
/tutorials/dax-calculate-function /tutorials/calculate-function/ 301
/tutorials/dax-calculate-function/ /tutorials/calculate-function/ 301
/tutorials/power-bi-sales-dashboard /tutorials/power-bi-sales-dashboard-tutorial/ 301
/tutorials/power-bi-sales-dashboard/ /tutorials/power-bi-sales-dashboard-tutorial/ 301
# P1 余下集群（8 对）
/tutorials/conditional-formatting-complete-guide /tutorials/conditional-formatting-power-bi/ 301
/tutorials/conditional-formatting-complete-guide/ /tutorials/conditional-formatting-power-bi/ 301
/tutorials/copy-conditional-formatting-power-bi /tutorials/copy-conditional-formatting/ 301
/tutorials/copy-conditional-formatting-power-bi/ /tutorials/copy-conditional-formatting/ 301
/tutorials/dax-variables-var /tutorials/dax-variables-guide/ 301
/tutorials/dax-variables-var/ /tutorials/dax-variables-guide/ 301
/tutorials/dax-variables-best-practices /tutorials/dax-variables-guide/ 301
/tutorials/dax-variables-best-practices/ /tutorials/dax-variables-guide/ 301
/tutorials/star-schema-power-bi /tutorials/data-modeling-star-schema/ 301
/tutorials/star-schema-power-bi/ /tutorials/data-modeling-star-schema/ 301
/tutorials/power-bi-star-schema /tutorials/data-modeling-star-schema/ 301
/tutorials/power-bi-star-schema/ /tutorials/data-modeling-star-schema/ 301
/tutorials/power-bi-performance-analyzer-guide /tutorials/power-bi-performance-analyzer/ 301
/tutorials/power-bi-performance-analyzer-guide/ /tutorials/power-bi-performance-analyzer/ 301
/tutorials/what-is-dax-power-bi /tutorials/dax-basics/ 301
/tutorials/what-is-dax-power-bi/ /tutorials/dax-basics/ 301
# P1 图表 4 篇（轻合并：bar+gauge 并入 charts 入口，line+kpi 保留独立）
/tutorials/bar-chart-conditional-formatting /tutorials/conditional-formatting-charts-power-bi/ 301
/tutorials/bar-chart-conditional-formatting/ /tutorials/conditional-formatting-charts-power-bi/ 301
/tutorials/gauge-conditional-formatting /tutorials/conditional-formatting-charts-power-bi/ 301
/tutorials/gauge-conditional-formatting/ /tutorials/conditional-formatting-charts-power-bi/ 301

# 2026-11 GA4 cleanup: legacy URLs still receiving traffic but returning 404
/tutorials/dax-storage-vs-formula-engine /tutorials/power-bi-performance-optimization/ 301
/tutorials/dax-storage-vs-formula-engine/ /tutorials/power-bi-performance-optimization/ 301
/tutorials/copy-conditional-formatting.html /tutorials/copy-conditional-formatting/ 301
/privacy-policy /privacy/ 301
/privacy-policy/ /privacy/ 301
`;
stage("public/_redirects", REDIRECTS);

// ---------------------------------------------------------------------------
// 6. RelatedProduct bailed out with a top-level `return null` before the
//    template, which Astro has no precedent for. Guard the markup instead.
// ---------------------------------------------------------------------------
const RP = "src/components/RelatedProduct.astro";
replaceOnce(RP, "const pick = scored[0]?.product;\nif (!pick) return null;\n", "const pick = scored[0]?.product;\n");
replaceOnce(RP, '\n<aside class="rp-card">\n', '\n{pick && (\n<aside class="rp-card">\n');
const RP_CLOSE_FROM = String.raw`</aside>

<script is:inline>
`;
const RP_CLOSE_TO = String.raw`</aside>
)}

<script is:inline>
`;
replaceOnce(RP, RP_CLOSE_FROM, RP_CLOSE_TO);

// ---------------------------------------------------------------------------
// 7. The guard and the layout disagreed about the cap and about what the
//    previous commit had achieved.
// ---------------------------------------------------------------------------
const GUARD = "scripts/check-seo-meta.mjs";
const G_BULLET_FROM = String.raw` *   - "Title too long"                -> final <title> > 60 chars (brand suffix included)
`;
const G_BULLET_TO = String.raw` *   - "Title too long"                -> final <title> > 55 chars (brand suffix included)
`;
const G_PARA_FROM = String.raw` * The writing target is title <=60 and description 130-155. These bounds are
 * slightly wider so the guard only fails on real regressions, not on a
 * five-character difference. Exits 1 on any violation.
`;
const G_PARA_TO = String.raw` * 60 is the hard limit; 55 is "not truncated" (desktop SERP cuts around
 * 580px). The bound matches BaseLayout.MAX_FINAL_TITLE exactly, so this guard
 * and the rendered <title> cannot drift apart. Description bounds are
 * 120-160. Exits 1 on any violation.
`;
replaceOnce(GUARD, G_BULLET_FROM, G_BULLET_TO);
replaceOnce(GUARD, G_PARA_FROM, G_PARA_TO);
const G_PASS_FROM = 'PASS — title <=60, description 120-160, no duplicate H1.';
const G_PASS_TO = 'PASS — title <=55, description 120-160, no duplicate H1.';
replaceOnce(GUARD, G_PASS_FROM, G_PASS_TO);

const LAYOUT = "src/layouts/BaseLayout.astro";
const B_ONE_FROM = '会在本地拦下任何超过 60 字符的最终标题。';
const B_ONE_TO = '会在本地拦下任何超过 55 字符的最终标题。';
const B_TWO_FROM = String.raw`// 2026-11: cap lowered from 60 to 55. 60 is "not over the limit", 55 is
// "not truncated" — desktop SERP cuts around 580px. 22 pages measured >= 55
// final characters, 5 of them exactly 60.
`;
const B_TWO_TO = String.raw`// 2026-11: cap lowered from 60 to 55. 60 is "not over the limit", 55 is
// "not truncated" — desktop SERP cuts around 580px. Lowering the cap only
// drops the 19-character brand suffix from titles of 37-55 characters; a
// source title that is itself over 55 still renders over 55, so those get
// rewritten rather than shortened. check-seo-meta.mjs enforces the same 55.
`;
replaceOnce(LAYOUT, B_ONE_FROM, B_ONE_TO);
replaceOnce(LAYOUT, B_TWO_FROM, B_TWO_TO);

// ---------------------------------------------------------------------------
// write — nothing is touched until every anchor above resolved
// ---------------------------------------------------------------------------
if (problems.length) {
  console.error("PATCH ABORTED — " + problems.length + " problem(s), nothing written:");
  for (const p of problems) console.error("  x " + p);
  process.exit(1);
}

for (const rel of staged.keys()) {
  fs.writeFileSync(path.join(ROOT, rel), staged.get(rel));
  console.log("patched  " + rel);
}

const redirects = staged.get("public/_redirects");
for (const raw of redirects.split("\n")) {
  const line = raw.trim();
  if (!line || line.startsWith("#")) continue;
  const parts = line.split(/\s+/);
  if (parts.length !== 3) {
    console.error("malformed redirect line: " + line);
    process.exit(1);
  }
  if (!parts[1].endsWith("/")) {
    console.error("redirect target without trailing slash: " + line);
    process.exit(1);
  }
}

console.log("");
console.log("done — " + staged.size + " files patched, every redirect is one hop");
