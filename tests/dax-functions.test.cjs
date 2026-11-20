/**
 * Tool 5/5 — dax-functions reference (src/data/dax-functions.ts + .astro page)
 * Verifies the 64-function dataset stays complete and the page consumes it correctly.
 */
'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { ROOT } = require('./helpers/dom.cjs');

function loadData() {
  const src = fs.readFileSync(path.join(ROOT, 'src/data/dax-functions.ts'), 'utf8');
  const code = src
    .replace(/export interface DaxFunction \{[\s\S]*?\n\}/, '')
    .replace(/export const/g, 'const')
    .replace(/\] as const/g, ']')
    .replace(/: DaxFunction\[\]/g, '');
  const ctx = {};
  vm.createContext(ctx);
  vm.runInContext(`${code}\nglobalThis.__d = { DAX_FUNCTIONS, CATEGORIES, FUNCTION_COUNT };`, ctx);
  return ctx.__d;
}

const { DAX_FUNCTIONS: FN, CATEGORIES: CATS, FUNCTION_COUNT: COUNT } = loadData();
const page = fs.readFileSync(path.join(ROOT, 'src/pages/tools/dax-functions.astro'), 'utf8');

describe('DAX reference — dataset integrity', () => {
  test('FUNCTION_COUNT matches the actual array length', () => {
    assert.equal(COUNT, FN.length);
  });

  test('64 functions are documented', () => {
    assert.equal(FN.length, 64, `expected 64 functions, got ${FN.length}`);
  });

  test('no duplicate function names', () => {
    const names = FN.map((f) => f.name);
    assert.equal(new Set(names).size, names.length, 'duplicate names found');
  });

  test('every function has syntax, summary and example', () => {
    for (const f of FN) {
      assert.ok(f.syntax && f.summary && f.example, `${f.name} is missing a field`);
    }
  });

  test('every function belongs to a declared category', () => {
    for (const f of FN) assert.ok(CATS.includes(f.category), `${f.name}: unknown category ${f.category}`);
  });

  test('all 8 categories are represented', () => {
    const used = new Set(FN.map((f) => f.category));
    assert.equal(used.size, CATS.length, `unused categories: ${CATS.filter((c) => !used.has(c))}`);
  });

  test('tutorial cross-links point to real tutorial slugs', () => {
    const contentDir = path.join(ROOT, 'src/content/tutorials');
    const slugs = new Set(fs.readdirSync(contentDir).filter((f) => f.endsWith('.md')).map((f) => f.slice(0, -3)));
    for (const f of FN.filter((x) => x.href)) {
      const m = f.href.match(/\/tutorials\/([^/]+)\//);
      if (m) assert.ok(slugs.has(m[1]), `${f.name} links to missing tutorial ${m[1]}`);
    }
  });

  test('page imports FUNCTION_COUNT and uses it in the heading', () => {
    assert.ok(page.includes('FUNCTION_COUNT'), 'page must import FUNCTION_COUNT');
    assert.ok(page.includes('{FUNCTION_COUNT} functions'), 'page must display the count');
  });
});
