/**
 * Tool 3/5 — conditional-format-generator (public/tools/conditional-format-generator.js)
 * Verifies threshold reversal, SWITCH TRUE, VAR and BLANK wrapping.
 */
'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { createDom, makeEl, loadScript } = require('./helpers/dom.cjs');

function setup(opts = {}) {
  const n = opts.bands ?? 3;
  const defaults = [0, 0.15, 0.3];
  const thrs = [];
  const clrs = [];
  for (let i = 0; i < n; i++) {
    thrs.push(makeEl(`thr${i}`, {
      value: String(opts.thresholds?.[i] ?? defaults[i]),
      classList: { contains: (c) => c === 'thr', add() {}, remove() {} },
    }));
    clrs.push(makeEl(`clr${i}`, {
      value: opts.colors?.[i] ?? '#C0392B',
      classList: { contains: (c) => c === 'clr', add() {}, remove() {} },
    }));
  }
  const finalLabel = makeEl('final-label', { textContent: opts.finalColor ?? '#1F3A5F' });
  const bands = makeEl('bands', {
    querySelectorAll: (sel) => (sel === '.thr' ? thrs : sel === '.clr' ? clrs : []),
    querySelector: (sel) => (sel === '.final .final-label' ? finalLabel : null),
  });
  const spec = {
    measure: { value: opts.measure ?? '[Value]' },
    name: { value: opts.name ?? 'Colour' },
    mode: { value: String(n + 1) },
    direction: { value: opts.direction ?? 'low' },
    'as-var': { checked: !!opts.useVar },
    'with-blank': { checked: !!opts.guardBlank },
    output: {}, 'copy-btn': {}, bands,
    'preset-pl': {}, 'preset-tl': {},
  };
  const dom = createDom(spec);
  loadScript('public/tools/conditional-format-generator.js', {
    window: dom.window, document: dom.document, navigator: dom.navigator,
  });
  return { dom, thrs, clrs, finalLabel, out: () => dom.el('output').textContent };
}

describe('Conditional format — thresholds', () => {
  test('low-is-bad keeps thresholds ascending with < operator', () => {
    const { out } = setup({ direction: 'low' });
    assert.ok(out().includes('[Value] < 0,'), out());
    assert.ok(out().includes('[Value] < 0.15,'), out());
    assert.ok(out().includes('[Value] < 0.3,'), out());
  });

  test('high-is-good reverses thresholds and uses > operator', () => {
    const { out } = setup({ direction: 'high' });
    const lines = out().split('\n').filter((l) => l.includes('[Value]'));
    const vals = lines.map((l) => parseFloat(l.match(/> ([\d.]+)/)[1]));
    assert.deepEqual(vals, [0.3, 0.15, 0], `expected descending, got ${vals}`);
  });

  test('direction switches the comparison operator (< for low, > for high)', () => {
    const low = setup({ direction: 'low' }).out();
    const high = setup({ direction: 'high' }).out();
    assert.ok(low.includes(' < '), low);
    assert.ok(!low.includes(' > '), low);
    assert.ok(high.includes(' > '), high);
    assert.ok(!high.includes(' < '), high);
  });

  test('custom measure name is used in every condition', () => {
    const { out } = setup({ measure: 'SUM(Sales[Amount])' });
    assert.equal((out().match(/SUM\(Sales\[Amount\]\)/g) || []).length, 3, out());
  });

  test('final else-colour comes from the swatch label', () => {
    const { out } = setup({ finalColor: '#123456' });
    assert.ok(out().includes('"#123456"'), out());
  });
});

describe('Conditional format — structure', () => {
  test('emits SWITCH ( TRUE () with a default value', () => {
    const { out } = setup();
    assert.ok(out().includes('SWITCH (\n    TRUE (),'), out());
    assert.ok(out().endsWith('\n)'), out());
  });

  test('VAR mode introduces _v and RETURN', () => {
    const { out } = setup({ useVar: true, measure: '[Margin]' });
    assert.ok(out().includes('VAR _v = [Margin]'), out());
    assert.ok(out().includes('RETURN'), out());
    assert.ok(out().includes('_v < 0'), out());
    assert.ok(!out().includes('[Margin] < 0,'), out());
  });

  test('BLANK guard wraps SWITCH inside IF(ISBLANK)', () => {
    const { out } = setup({ guardBlank: true });
    assert.ok(out().includes('IF ('), out());
    assert.ok(out().includes('ISBLANK ( [Value] )'), out());
    assert.ok(out().includes('BLANK ()'), out());
  });

  test('VAR + BLANK together nest in the right order', () => {
    const { out } = setup({ useVar: true, guardBlank: true });
    assert.ok(out().includes('VAR _v = [Value]'), out());
    assert.ok(out().includes('ISBLANK ( _v )'), out());
    assert.ok(out().indexOf('VAR _v') < out().indexOf('ISBLANK'), out());
  });

  test('custom measure name appears in the output', () => {
    assert.ok(setup({ name: 'MarginColour' }).out().startsWith('MarginColour ='));
  });

  test('single threshold (2-band preset) emits one condition', () => {
    const { out } = setup({ bands: 1 });
    assert.equal((out().match(/< /g) || []).length, 1, out());
  });

  test('colours are upper-cased from the colour input', () => {
    const { out } = setup({ colors: ['#c0392b'] });
    assert.ok(out().includes('"#C0392B"'), out());
  });

  test('threshold changes re-render without reload', () => {
    const s = setup({ direction: 'low' });
    s.thrs[0].value = '0.5';
    s.dom.fire('input', { target: s.thrs[0] });
    assert.ok(s.out().includes('[Value] < 0.5,'), s.out());
  });
});
