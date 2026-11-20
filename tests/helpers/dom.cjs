/**
 * Minimal DOM + script loader for testing the site's browser-only tool scripts
 * under Node's built-in test runner. No jsdom dependency.
 *
 * Usage:
 *   const { loadScript, createDom } = require('./helpers/dom.cjs');
 *   const dom = createDom({ 'start-year': { value: '2020' }, ... });
 *   loadScript('public/tools/date-table.js', { document: dom.document });
 *   dom.fire('DOMContentLoaded');
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '../..');

function makeEl(id, overrides = {}) {
  const listeners = {};
  const el = {
    id,
    value: '',
    checked: false,
    textContent: '',
    innerHTML: '',
    style: {},
    dataset: {},
    attributes: {},
    classList: { contains: () => false, add() {}, remove() {} },
    _listeners: listeners,
    addEventListener(type, fn) { (listeners[type] ||= []).push(fn); },
    removeEventListener(type, fn) {
      if (listeners[type]) listeners[type] = listeners[type].filter((f) => f !== fn);
    },
    dispatch(type, ev = {}) { (listeners[type] || []).forEach((fn) => fn({ target: el, ...ev })); },
    getAttribute(name) { return el.attributes[name]; },
    setAttribute(name, v) { el.attributes[name] = v; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    appendChild() {},
    removeChild() {},
    select() {},
    focus() {},
    insertBefore() {},
    ...overrides,
  };
  return el;
}

/**
 * createDom(spec) — spec maps element id -> overrides for that element.
 * Returns { document, window, navigator, fire(type), el(id), els }.
 */
function createDom(spec = {}) {
  const els = {};
  for (const [id, overrides] of Object.entries(spec)) els[id] = makeEl(id, overrides);

  const docListeners = {};
  const document = {
    getElementById: (id) => els[id] || null,
    querySelector: (sel) => {
      // supports "#id .class" minimal case used by conditional format tool
      const m = sel.match(/^#([\w-]+)\s+\.([\w-]+)$/);
      if (m && els[m[1]]) return els[m[1]].querySelector(`.${m[2]}`);
      return null;
    },
    querySelectorAll: (sel) => {
      const m = sel.match(/^#([\w-]+)\s+\.([\w-]+)$/);
      if (m && els[m[1]]) return els[m[1]].querySelectorAll(`.${m[2]}`);
      return [];
    },
    createElement: (tag) => makeEl(`<${tag}>`),
    createDocumentFragment: () => makeEl('#fragment'),
    addEventListener(type, fn) { (docListeners[type] ||= []).push(fn); },
    removeEventListener(type, fn) {
      if (docListeners[type]) docListeners[type] = docListeners[type].filter((f) => f !== fn);
    },
    body: makeEl('body'),
  };

  const window = {
    document,
    navigator: { clipboard: { writeText: async () => {} } },
    localStorage: {
      _d: {},
      getItem(k) { return this._d[k] ?? null; },
      setItem(k, v) { this._d[k] = String(v); },
      removeItem(k) { delete this._d[k]; },
    },
    setTimeout: (fn) => { if (typeof fn === 'function') fn(); return 0; },
    clearTimeout() {},
    location: { pathname: '/tools/' },
    addEventListener(type, fn) { (docListeners[type] ||= []).push(fn); },
  };
  window.window = window;
  window.globalThis = window;

  return {
    document,
    window,
    navigator: window.navigator,
    localStorage: window.localStorage,
    els,
    el: (id) => els[id],
    fire(type, ev = {}) { (docListeners[type] || []).forEach((fn) => fn({ target: document, ...ev })); },
  };
}

/**
 * loadScript(relPath, globals) — execute an IIFE browser script in a sandbox.
 * The script's `window`, `document`, `navigator`, `localStorage`, `setTimeout`
 * are taken from `globals` (see createDom).
 */
function loadScript(relPath, globals) {
  const file = path.isAbsolute(relPath) ? relPath : path.join(ROOT, relPath);
  const code = fs.readFileSync(file, 'utf8');
  const sandbox = {
    console,
    Date,
    Math,
    JSON,
    parseInt,
    parseFloat,
    isFinite,
    String,
    Number,
    Array,
    Object,
    RegExp,
    setTimeout: globals.setTimeout || ((fn) => { if (typeof fn === 'function') fn(); return 0; }),
    clearTimeout: globals.clearTimeout || (() => {}),
    ...globals,
  };
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { filename: path.basename(file) });
  return sandbox;
}

module.exports = { createDom, loadScript, makeEl, ROOT };
