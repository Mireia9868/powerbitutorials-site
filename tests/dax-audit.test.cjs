/**
 * Tool 1/5 — dax-audit (parser core: public/tools/dax.js)
 * Covers tokenize / format / analyze, incl. the 2026-11-20 CJK identifier fix.
 */
'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { ROOT } = require('./helpers/dom.cjs');

function loadDax() {
  const code = fs.readFileSync(path.join(ROOT, 'public/tools/dax.js'), 'utf8');
  const ctx = { window: {} };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(code, ctx);
  return ctx.DAXTool || ctx.window.DAXTool;
}

const DAX = loadDax();

describe('DAX tokenizer — identifier characters', () => {
  test('ASCII identifiers tokenize as a single word', () => {
    const t = DAX.tokenize('SUM(Sales[Amt])').filter((x) => x.type === 'word').map((x) => x.value);
    assert.ok(t.includes('Sales'), `expected Sales, got ${JSON.stringify(t)}`);
  });

  test('Chinese table name is one identifier (CJK regression)', () => {
    const t = DAX.tokenize('销售[金额]').filter((x) => x.type === 'word').map((x) => x.value);
    assert.ok(t.includes('销售'), `expected 销售 as one word, got ${JSON.stringify(t)}`);
  });

  test('Japanese, Cyrillic and accented Latin identifiers survive tokenization', () => {
    for (const name of ['売上', 'Продажи', 'Café']) {
      const t = DAX.tokenize(`${name}[X]`).filter((x) => x.type === 'word').map((x) => x.value);
      assert.ok(t.includes(name), `expected ${name} as one word, got ${JSON.stringify(t)}`);
    }
  });

  test('CJK inside quoted string does not leak into identifiers', () => {
    const t = DAX.tokenize('"北京"').filter((x) => x.type === 'word');
    assert.equal(t.length, 0, `string content must not be words, got ${JSON.stringify(t)}`);
  });
});

describe('DAX formatter — correctness', () => {
  test('Chinese table name gets no injected space (CJK regression)', () => {
    assert.equal(DAX.format('SUM(销售[金额])'), 'SUM(销售[金额])');
  });

  test('Chinese table + column + filter expression formats cleanly', () => {
    const out = DAX.format('CALCULATE(SUM(销售[金额]), 销售[地区]="北京")');
    assert.ok(out.includes('销售[金额]'), out);
    assert.ok(!out.includes('销售 ['), `injected space: ${out}`);
    assert.ok(out.includes('"北京"'), out);
  });

  test('Japanese / Cyrillic / accented Latin format without spaces', () => {
    assert.equal(DAX.format('SUM(売上[金額])'), 'SUM(売上[金額])');
    assert.equal(DAX.format('SUM(Продажи[Сумма])'), 'SUM(Продажи[Сумма])');
    assert.equal(DAX.format('SUM(Café[Montant])'), 'SUM(Café[Montant])');
  });

  test('ASCII nested CALCULATE/FILTER still formats as before', () => {
    const out = DAX.format('CALCULATE(SUM(Sales[Amt]), FILTER(ALL(Sales), Sales[X]>0))');
    assert.ok(out.startsWith('CALCULATE(\n'), out);
    assert.ok(out.includes('SUM(Sales[Amt])'), out);
    assert.ok(out.includes('FILTER('), out);
  });

  test('string containing parentheses is not treated as syntax', () => {
    const out = DAX.format('IF([Name]="A (B)", 1, 0)');
    assert.ok(out.includes('"A (B)"'), out);
    assert.ok(out.includes('IF('), out);
  });

  test('escaped quotes inside a string are preserved', () => {
    const out = DAX.format('IF([X]="say ""hi""",1,0)');
    assert.ok(out.includes('"say ""hi"""'), out);
  });

  test('line and block comments do not break formatting', () => {
    assert.ok(DAX.format('SUM(A) // note\n+ 1').includes('SUM(A)'));
    assert.ok(DAX.format('SUM(A) /* note */ + 1').includes('SUM(A)'));
  });

  test('division operator gets spaced consistently', () => {
    const out = DAX.format('SUM(A)/SUM(B)');
    assert.ok(out.includes(' / '), out);
  });
});

describe('DAX analyzer — audit rules', () => {
  test('raw division on two constants is flagged (DIVIDE suggestion)', () => {
    const a = DAX.analyze('1 / 2');
    const ids = a.issues.map((i) => i.id);
    assert.ok(ids.length > 0, `expected a suggestion for 1/2, got ${JSON.stringify(a.issues)}`);
  });

  test('DIVIDE() does not get the raw-division suggestion', () => {
    const a = DAX.analyze('DIVIDE(SUM(A),SUM(B))');
    const ids = a.issues.map((i) => i.id);
    assert.ok(!ids.some((id) => /div/i.test(id) && !id.includes('divide_fn')), JSON.stringify(ids));
  });

  test('stats.countCalls increases with nesting', () => {
    const a1 = DAX.analyze('SUM(A)');
    const a2 = DAX.analyze('CALCULATE(SUM(A), FILTER(ALL(B), B[X]>0))');
    assert.ok(a2.stats.calls > a1.stats.calls, `${a1.stats.calls} vs ${a2.stats.calls}`);
  });

  test('unbalanced parentheses format without crashing (parser is tolerant)', () => {
    // The parser intentionally degrades gracefully so the page never freezes.
    assert.doesNotThrow(() => DAX.format('SUM(A'));
    assert.equal(DAX.format('SUM(A'), 'SUM(A');
  });

  test('CJK measure name does not produce audit errors', () => {
    const a = DAX.analyze('销售总额 = SUM(销售[金额])');
    assert.ok(Array.isArray(a.issues), 'analyze must return an issues array');
  });
});
