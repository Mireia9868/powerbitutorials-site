#!/usr/bin/env node
/**
 * SEO metadata guard — powerbitutorials.com
 * Run: npm run check:seo
 *
 * Bing Webmaster Tools Site Scan flags these three issues page by page:
 *   - "Title too long"                -> final <title> > 60 chars (brand suffix included)
 *   - "Meta description too short/long" -> outside 120-160 chars
 *   - "There are multiple <h1> tags"   -> >1 <h1> rendered on a page
 *
 * The writing target is title <=60 and description 130-155. These bounds are
 * slightly wider so the guard only fails on real regressions, not on a
 * five-character difference. Exits 1 on any violation.
 *
 * Dynamic pages (index.astro, tutorials/[slug].astro, category/[slug].astro)
 * pass their metadata as expressions. They are listed as skipped — their
 * rendered output is covered by the live-site check instead.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BRAND_SUFFIX = ' — Power BI Tutorials';
const MAX_TITLE = 60;
const MIN_DESC = 120;
const MAX_DESC = 160;

const consts = fs.readFileSync(path.join(ROOT, 'src/consts.ts'), 'utf8');
const SITE_TITLE = (consts.match(/SITE_TITLE\s*=\s*"([^"]*)"/) || [])[1] || '';
const SITE_DESCRIPTION = (consts.match(/SITE_DESCRIPTION\s*=\s*\n?\s*"([^"]*)"/) || [])[1] || '';

const violations = [];
const skipped = [];
let checked = 0;

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.astro')) out.push(full);
  }
  return out;
}

function parseFrontmatter(txt) {
  const m = txt.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!m) return { fm: {}, body: txt };
  const fm = {};
  for (const line of m[1].split('\n')) {
    const mm = line.match(/^(\w+):\s*(.*)$/);
    if (!mm) continue;
    let v = mm[2].trim();
    if (v.length >= 2 && (v[0] === '"' || v[0] === "'") && v.at(-1) === v[0]) v = v.slice(1, -1);
    fm[mm[1]] = v;
  }
  return { fm, body: txt.slice(m[0].length) };
}

function readAttr(block, name) {
  const re = new RegExp('\\b' + name + '=(?:"([^"]*)"|\\{([\\s\\S]*?)\\})');
  const m = block.match(re);
  if (!m) return { present: false, dynamic: false, value: null };
  return { present: true, dynamic: m[2] !== undefined, value: m[1] ?? null };
}

function check(label, rawTitle, description, body, kind) {
  const finalTitle = rawTitle
    ? (rawTitle + BRAND_SUFFIX).length <= MAX_TITLE
      ? rawTitle + BRAND_SUFFIX
      : rawTitle
    : SITE_TITLE;
  if (finalTitle.length > MAX_TITLE) {
    violations.push(`${label}: title ${finalTitle.length} > ${MAX_TITLE} — "${finalTitle}"`);
  }
  const desc = description || SITE_DESCRIPTION;
  if (desc.length < MIN_DESC || desc.length > MAX_DESC) {
    violations.push(`${label}: description ${desc.length} outside ${MIN_DESC}-${MAX_DESC}`);
  }
  const h1 = kind === 'tutorial'
    ? (body.match(/^#\s+/gm) || []).length
    : (body.match(/<h1[\s>]/gi) || []).length;
  const limit = kind === 'tutorial' ? 0 : 1;
  if (h1 > limit) violations.push(`${label}: ${h1} H1 (expected <=${limit})`);
  checked++;
}

// Tutorials: frontmatter title/description; H1 is rendered by the layout,
// so a markdown body must never contain a level-one heading.
for (const file of fs.readdirSync(path.join(ROOT, 'src/content/tutorials')).filter((f) => f.endsWith('.md')).sort()) {
  const rel = `src/content/tutorials/${file}`;
  const { fm, body } = parseFrontmatter(fs.readFileSync(path.join(ROOT, rel), 'utf8'));
  if (String(fm.draft).toLowerCase() === 'true') { skipped.push(rel + ' (draft)'); continue; }
  // de-* pages are rendered with noindex and excluded from sitemap.xml.js,
  // so they are out of scope for Bing's Site Scan. German copy is naturally
  // longer and must not be truncated to satisfy an English length rule.
  if (file.startsWith('de-')) { skipped.push(rel + ' (noindex, not in sitemap)'); continue; }
  check(rel, fm.title || '', fm.description || '', body, 'tutorial');
}

// Static Astro pages: read literal BaseLayout props.
for (const file of walk(path.join(ROOT, 'src/pages')).sort()) {
  const rel = path.relative(ROOT, file).split(path.sep).join('/');
  const txt = fs.readFileSync(file, 'utf8');
  const start = txt.indexOf('<BaseLayout');
  if (start === -1) { skipped.push(rel + ' (no BaseLayout)'); continue; }
  const end = txt.indexOf('>', start);
  const block = txt.slice(start, end);
  const t = readAttr(block, 'title');
  const d = readAttr(block, 'description');
  if ((t.present && t.dynamic) || (d.present && d.dynamic) || (!t.present && !d.present)) {
    skipped.push(rel + ' (dynamic metadata — verified on live site)');
    continue;
  }
  check(rel, t.value || '', d.value || '', txt, 'astro');
}

console.log(`SEO metadata check — ${checked} sources checked`);
if (skipped.length) {
  console.log(`\nSkipped ${skipped.length} (not statically resolvable):`);
  for (const s of skipped) console.log('  - ' + s);
}
if (violations.length) {
  console.log(`\n${violations.length} violation(s):`);
  for (const v of violations) console.log('  x ' + v);
  process.exit(1);
}
console.log('\nPASS — title <=60, description 120-160, no duplicate H1.');
