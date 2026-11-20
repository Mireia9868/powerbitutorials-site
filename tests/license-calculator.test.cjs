/**
 * Tool 4/5 — license-calculator (inline <script> in src/pages/tools/license-calculator.astro)
 * Loads the actual inline script (TS types stripped) so tests track source changes.
 */
'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { createDom, ROOT } = require('./helpers/dom.cjs');

function loadLicenseScript() {
  const file = path.join(ROOT, 'src/pages/tools/license-calculator.astro');
  const source = fs.readFileSync(file, 'utf8');
  const match = source.match(/<script>([\s\S]*?)<\/script>/);
  assert.ok(match, 'license-calculator.astro must contain an inline <script>');
  return match[1]
    .replace(/const \$ = [^\n]+;/, 'const $ = (id) => document.getElementById(id);')
    .replace(/\(n: number\)/g, '(n)')
    .replace(/\(id: string\)/g, '(id)')
    .replace(/ as HTMLInputElement \| null/g, '')
    .replace(/ as number/g, '');
}

const CODE = loadLicenseScript();

function setup(creators, viewers, premium) {
  const dom = createDom({
    creators: { value: String(creators) },
    viewers: { value: String(viewers) },
    premium: { checked: !!premium },
    rows: {}, verdict: {},
  });
  const ctx = { document: dom.document, Date, Math, parseInt, setTimeout: (f) => f && f() };
  ctx.window = ctx;
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(CODE, ctx);
  return dom;
}

function rowsText(dom) { return dom.el('rows').innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' '); }

describe('License calculator — pricing constants', () => {
  test('Pro list price is $14/user/month', () => {
    const d = setup(1, 0, false);
    assert.ok(rowsText(d).includes('$14'), rowsText(d));
  });

  test('PPU list price is $24/user/month', () => {
    const d = setup(1, 0, false);
    assert.ok(rowsText(d).includes('$24'), rowsText(d));
  });

  test('all-Pro yearly total is headcount × 14 × 12', () => {
    const d = setup(3, 17, false);
    assert.ok(d.el('verdict').innerHTML.includes('$3,360'), d.el('verdict').innerHTML);
  });
});

describe('License calculator — cheapest option', () => {
  test('builders=0, viewers>0 → All Pro is cheapest', () => {
    const d = setup(0, 10, false);
    assert.ok(d.el('verdict').innerHTML.includes('All Pro is cheapest'), d.el('verdict').innerHTML);
  });

  test('viewers=0, builders>0 → mixed equals all-PPU, no mixed saving claim', () => {
    const d = setup(10, 0, false);
    assert.ok(!d.el('verdict').innerHTML.includes('saves you'), d.el('verdict').innerHTML);
  });

  test('both zero → empty-state row, no verdict', () => {
    const d = setup(0, 0, false);
    assert.ok(rowsText(d).includes('Enter at least one person'), rowsText(d));
    assert.equal(d.el('verdict').innerHTML, '');
  });

  test('All Pro is always cheapest without premium (PPU costs $10 more per seat)', () => {
    // mixed = allPro + creators*10, so it can never beat All Pro when premium is off.
    for (const [c, v] of [[10, 2], [10, 100], [1, 1]]) {
      const d = setup(c, v, false);
      assert.ok(d.el('verdict').innerHTML.includes('All Pro is cheapest'),
        `c=${c} v=${v}: ${d.el('verdict').innerHTML}`);
    }
  });

  test('premium=true excludes All Pro from the comparison', () => {
    const d = setup(1, 0, true);
    assert.ok(!d.el('verdict').innerHTML.includes('All Pro is cheapest'), d.el('verdict').innerHTML);
  });

  test('premium=true with builders=0 does not claim 0 builders on PPU', () => {
    const d = setup(0, 10, true);
    const v = d.el('verdict').innerHTML;
    assert.ok(!v.includes('0 builders on PPU'), `boundary wording bug: ${v}`);
    assert.ok(!v.includes('saves you $0'), `zero-saving bug: ${v}`);
  });

  test('premium=true with builders>0 recommends mixed/PPU without per-seat inconsistency', () => {
    const d = setup(5, 10, true);
    const v = d.el('verdict').innerHTML;
    assert.ok(v.length > 0, 'verdict must be present');
    assert.ok(!v.includes('$0'), v);
  });

  test('verdict updates when inputs change', () => {
    const d = setup(1, 1, false);
    const before = d.el('verdict').innerHTML;
    d.el('creators').value = '20';
    d.el('creators').dispatch('input');
    assert.notEqual(d.el('verdict').innerHTML, before);
  });

  test('negative inputs are clamped to zero', () => {
    const d = setup(-5, -3, false);
    assert.ok(rowsText(d).includes('Enter at least one person'), rowsText(d));
  });
});
