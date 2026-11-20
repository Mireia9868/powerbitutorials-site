/**
 * Tool 2/5 — date-table generator (public/tools/date-table.js)
 * Verifies generated DAX/M code for fiscal year, ISO week, week start and row counts.
 */
'use strict';

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const { createDom, loadScript } = require('./helpers/dom.cjs');

const BASE = {
  'start-year': { value: '2020' },
  'end-year': { value: '2024' },
  'fiscal-start': { value: '7' },
  'fiscal-naming': { value: 'start' },
  'week-start': { value: 'monday' },
  'iso-week': { checked: false },
  'fiscal-cols': { checked: false },
  'current-flags': { checked: false },
  'dax-out': {}, 'm-out': {}, 'range-note': {}, 'fiscal-naming-field': { style: {} },
  'copy-dax': {}, 'copy-m': {},
};

function generate(overrides = {}) {
  const spec = {};
  for (const [k, v] of Object.entries(BASE)) spec[k] = { ...v, ...(overrides[k] || {}) };
  const dom = createDom(spec);
  loadScript('public/tools/date-table.js', {
    window: dom.window, document: dom.document, navigator: dom.navigator,
  });
  dom.fire('DOMContentLoaded');
  return { dax: dom.el('dax-out').textContent, m: dom.el('m-out').textContent, note: dom.el('range-note').textContent, dom };
}

describe('Date table — date range', () => {
  test('generates CALENDAR with correct start/end years', () => {
    const { dax } = generate();
    assert.ok(dax.includes('DATE(2020, 1, 1)'), dax.slice(0, 200));
    assert.ok(dax.includes('DATE(2024, 12, 31)'), dax.slice(0, 200));
  });

  test('row count is correct for a full 5-year range (2020–2024 = 1827)', () => {
    const { note } = generate();
    assert.equal(note, '2020–2024 · 1,827 rows');
  });

  test('leap-year 2024 is counted (2024 only = 366)', () => {
    const { note } = generate({ 'start-year': { value: '2024' }, 'end-year': { value: '2024' } });
    assert.equal(note, '2024–2024 · 366 rows');
  });

  test('end year before start year is clamped (no negative range)', () => {
    const { dax } = generate({ 'start-year': { value: '2024' }, 'end-year': { value: '2020' } });
    assert.ok(dax.includes('DATE(2024, 1, 1)'), dax.slice(0, 200));
    assert.ok(dax.includes('DATE(2024, 12, 31)'), dax.slice(0, 200));
  });

  test('range is capped at 60 years', () => {
    const { dax } = generate({ 'start-year': { value: '2000' }, 'end-year': { value: '2099' } });
    assert.ok(dax.includes('DATE(2060, 12, 31)'), dax.slice(0, 200));
  });
});

describe('Date table — week numbering', () => {
  test('ISO week uses WEEKNUM(..., 21) and the Thursday-anchored M algorithm', () => {
    const { dax, m } = generate({ 'iso-week': { checked: true } });
    assert.ok(dax.includes('WEEKNUM([Date], 21)'), dax);
    assert.ok(m.includes('Date.DayOfWeek([Date], Day.Monday)'), m);
    assert.ok(m.includes('Number.RoundDown(Duration.Days(_thu - _jan1) / 7) + 1'), m);
  });

  test('Monday week start uses WEEKNUM(..., 2)', () => {
    const { dax } = generate({ 'week-start': { value: 'monday' } });
    assert.ok(dax.includes('WEEKNUM([Date], 2)'), dax);
  });

  test('Sunday week start uses WEEKNUM(..., 1) and Sunday weekend flags', () => {
    const { dax } = generate({ 'week-start': { value: 'sunday' } });
    assert.ok(dax.includes('WEEKNUM([Date], 1)'), dax);
    assert.ok(dax.includes('WEEKDAY([Date], 1) = 1 || WEEKDAY([Date], 1) = 7'), dax);
  });

  test('ISO week takes precedence over week-start setting', () => {
    const { dax } = generate({ 'iso-week': { checked: true }, 'week-start': { value: 'sunday' } });
    assert.ok(dax.includes('WEEKNUM([Date], 21)'), dax);
    assert.ok(!dax.includes('WEEKNUM([Date], 1)'), dax);
  });
});

describe('Date table — fiscal year', () => {
  test('fiscal columns are absent when the option is off', () => {
    const { dax } = generate();
    assert.ok(!dax.includes('Fiscal Year'), dax);
  });

  test('fiscal year named by start year subtracts 1 before the start month', () => {
    const { dax } = generate({ 'fiscal-cols': { checked: true }, 'fiscal-start': { value: '7' }, 'fiscal-naming': { value: 'start' } });
    assert.ok(dax.includes('VAR FiscalStartMonth = 7'), dax);
    assert.ok(dax.includes('YEAR([Date]) - IF(MONTH([Date]) < FiscalStartMonth, 1, 0)'), dax);
  });

  test('fiscal year named by end year adds 1 from the start month', () => {
    const { dax } = generate({ 'fiscal-cols': { checked: true }, 'fiscal-naming': { value: 'end' } });
    assert.ok(dax.includes('YEAR([Date]) + IF(MONTH([Date]) >= FiscalStartMonth, 1, 0)'), dax);
  });

  test('fiscal quarter and month use 12-month modulo', () => {
    const { dax } = generate({ 'fiscal-cols': { checked: true } });
    assert.ok(dax.includes('MOD(MONTH([Date]) - FiscalStartMonth + 12, 12)'), dax);
  });

  test('current flags use EOMONTH / TODAY when enabled', () => {
    const { dax } = generate({ 'current-flags': { checked: true } });
    assert.ok(dax.includes('EOMONTH(TODAY(), 0)'), dax);
    assert.ok(dax.includes('YEAR([Date]) = YEAR(TODAY())'), dax);
  });

  test('generated M code has a valid let/in structure', () => {
    const { m } = generate({ 'iso-week': { checked: true }, 'fiscal-cols': { checked: true } });
    assert.ok(m.startsWith('let\n'), m.slice(0, 80));
    assert.ok(m.includes('\nin\n    '), m.slice(-120));
  });
});
