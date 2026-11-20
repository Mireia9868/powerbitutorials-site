/*
 * dax.js — 轻量 DAX 词法分析 / 格式化 / 规则体检
 * 无依赖，浏览器与 Node 均可运行。挂载在 window.DAXTool 或 module.exports。
 *
 * 设计取舍：这不是完整的 DAX 语法解析器，而是「面向人的格式化器 + 保守的规则检查」。
 * 所有检查都必须能在词法层面确定，宁可漏报，不可误报。
 */
(function (global) {
  'use strict';

  var KEYWORDS = {
    VAR: 1, RETURN: 1, TRUE: 1, FALSE: 1, BLANK: 1, IN: 1, NOT: 1,
    DEFINE: 1, MEASURE: 1, EVALUATE: 1, ORDER: 1, BY: 1, START: 1, AT: 1,
    ASC: 1, DESC: 1, TABLE: 1, COLUMN: 1
  };

  var BINARY_OPS = { '+': 1, '-': 1, '*': 1, '/': 1, '=': 1, '<': 1, '>': 1, '<=': 1, '>=': 1, '<>': 1, '&&': 1, '||': 1, '&': 1 };

  // ---------------------------------------------------------------- tokenize

  // Identifier characters: keep the legacy Latin/Greek ranges for backwards
  // compatibility, plus Unicode letters and numbers so non-ASCII table/column
  // names (Chinese, Japanese, Cyrillic, accented Latin, ...) tokenize as one
  // identifier instead of being split into stray characters.
  function isIdStart(c) {
    return /[A-Za-z_\u00C0-\u024F\u0370-\u1FFF]/.test(c) || /\p{L}/u.test(c);
  }
  function isIdPart(c) {
    return /[A-Za-z0-9_\u00C0-\u024F\u0370-\u1FFF]/.test(c) || /[\p{L}\p{N}]/u.test(c);
  }

  function tokenize(src) {
    var tokens = [];
    var i = 0, n = src.length;

    function push(type, value) {
      tokens.push({ type: type, value: value, start: i, end: i + value.length });
    }

    while (i < n) {
      var c = src[i];

      if (/\s/.test(c)) {
        var s = i;
        while (i < n && /\s/.test(src[i])) i++;
        tokens.push({ type: 'ws', value: src.slice(s, i), start: s, end: i });
        continue;
      }

      // 行注释： // 或 --
      if ((c === '/' && src[i + 1] === '/') || (c === '-' && src[i + 1] === '-')) {
        var cs = i;
        while (i < n && src[i] !== '\n' && src[i] !== '\r') i++;
        push('comment', src.slice(cs, i));
        continue;
      }
      // 块注释： /* ... */
      if (c === '/' && src[i + 1] === '*') {
        var bs = i;
        i += 2;
        while (i < n && !(src[i] === '*' && src[i + 1] === '/')) i++;
        i = Math.min(n, i + 2);
        push('comment', src.slice(bs, i));
        continue;
      }

      // 字符串 "..."，内部 "" 表示一个引号
      if (c === '"') {
        var ss = i; i++;
        while (i < n) {
          if (src[i] === '"') {
            if (src[i + 1] === '"') { i += 2; continue; }
            i++; break;
          }
          i++;
        }
        push('string', src.slice(ss, i));
        continue;
      }

      // 引号表名 'Table Name'，内部 '' 表示一个引号
      if (c === "'") {
        var ts = i; i++;
        while (i < n) {
          if (src[i] === "'") {
            if (src[i + 1] === "'") { i += 2; continue; }
            i++; break;
          }
          i++;
        }
        push('table', src.slice(ts, i));
        continue;
      }

      // 方括号标识符 [Column] 或 [Measure]
      if (c === '[') {
        var qs = i; i++;
        while (i < n) {
          if (src[i] === ']') {
            if (src[i + 1] === ']') { i += 2; continue; }
            i++; break;
          }
          i++;
        }
        push('bracket', src.slice(qs, i));
        continue;
      }

      // 数字
      if (/[0-9]/.test(c) || (c === '.' && /[0-9]/.test(src[i + 1] || ''))) {
        var ns = i;
        while (i < n && /[0-9.]/.test(src[i])) i++;
        if (src[i] === 'e' || src[i] === 'E') {
          i++;
          if (src[i] === '+' || src[i] === '-') i++;
          while (i < n && /[0-9]/.test(src[i])) i++;
        }
        push('number', src.slice(ns, i));
        continue;
      }

      // 标识符 / 函数名 / 关键字
      if (isIdStart(c)) {
        var ws = i;
        while (i < n && isIdPart(src[i])) i++;
        push('word', src.slice(ws, i));
        continue;
      }

      // 双字符运算符
      var two = src.substr(i, 2);
      if (two === '<=' || two === '>=' || two === '<>' || two === '&&' || two === '||' || two === '==' || two === '^=') {
        i += 2; push('punct', two); continue;
      }

      i++;
      push('punct', c);
    }
    return tokens;
  }

  // ------------------------------------------------------------ 结构辅助

  function significant(tokens) {
    return tokens.filter(function (t) { return t.type !== 'ws' && t.type !== 'comment'; });
  }

  /** 为每个括号建立配对表 */
  function buildPairs(toks) {
    var pairs = {}, stack = [];
    for (var i = 0; i < toks.length; i++) {
      if (toks[i].value === '(') stack.push(i);
      else if (toks[i].value === ')') {
        var o = stack.pop();
        if (o !== undefined) { pairs[o] = i; pairs[i] = o; }
      }
    }
    return pairs;
  }

  /** 找出所有函数调用：word 后紧邻 '(' */
  function findCalls(toks, pairs) {
    var calls = [];
    for (var i = 0; i < toks.length - 1; i++) {
      if (toks[i].type !== 'word') continue;
      if (toks[i + 1].value !== '(') continue;
      if (KEYWORDS[toks[i].value.toUpperCase()] && toks[i].value.toUpperCase() !== 'BLANK') continue;
      var open = i + 1, close = pairs[open];
      if (close === undefined) continue;
      calls.push({
        name: toks[i].value,
        upper: toks[i].value.toUpperCase(),
        nameIndex: i,
        open: open,
        close: close,
        args: splitArgs(toks, open, close, pairs),
        depth: depthAt(toks, i, pairs)
      });
    }
    return calls;
  }

  function splitArgs(toks, open, close, pairs) {
    var args = [], start = open + 1;
    for (var i = open + 1; i < close; i++) {
      var v = toks[i].value;
      if (v === '(' || v === '[') {
        if (pairs[i] !== undefined) { i = pairs[i]; }
        continue;
      }
      if (v === ',') {
        args.push({ from: start, to: i - 1, toks: toks.slice(start, i) });
        start = i + 1;
      }
    }
    if (start <= close - 1) args.push({ from: start, to: close - 1, toks: toks.slice(start, close) });
    else if (args.length) args.push({ from: close, to: close - 1, toks: [] });
    return args;
  }

  function depthAt(toks, index, pairs) {
    var d = 0;
    for (var i = 0; i < index; i++) {
      if (toks[i].value === '(') d++;
      else if (toks[i].value === ')') d--;
    }
    return d;
  }

  function sliceText(toks) {
    return toks.map(function (t) { return t.value; }).join(' ');
  }

  // -------------------------------------------------------------- format

  function isSimpleArg(toks) {
    if (!toks.length) return true;
    if (toks.length === 1) return true;
    if (toks.length > 5) return false;
    return toks.every(function (t) {
      return t.value !== '(' && t.value !== ')' && t.type !== 'comment' && t.type !== 'string';
    });
  }

  function groupBreaks(toks, open, close, pairs) {
    var args = splitArgs(toks, open, close, pairs);
    var chars = 0, hasComment = false;
    for (var i = open + 1; i < close; i++) {
      if (toks[i].type === 'comment') hasComment = true;
      chars += toks[i].value.length + 1;
    }
    if (hasComment) return true;
    if (args.length <= 1) return false;
    var simple = args.every(function (a) { return isSimpleArg(a.toks); });
    if (simple && chars <= 60) return false;
    if (chars > 72) return true;
    return args.length > 1;
  }

  function tokenIsUnary(toks, idx) {
    var t = toks[idx];
    if (!t || (t.value !== '-' && t.value !== '+')) return false;
    var p = toks[idx - 1];
    if (!p) return true;
    if (p.value === '(' || p.value === ',') return true;
    if (p.type === 'punct' && BINARY_OPS[p.value]) return true;
    return false;
  }

  function inlineSpacing(toks, i) {
    var prev = toks[i - 1], cur = toks[i];
    if (!prev) return false;
    if (prev.type === 'punct' && BINARY_OPS[prev.value]) {
      if (tokenIsUnary(toks, i - 1)) return false;
      return true;
    }
    if (cur.type === 'punct' && BINARY_OPS[cur.value]) {
      if (tokenIsUnary(toks, i)) return false;
      return true;
    }
    if (prev.value === '(' || prev.value === '[' || prev.value === ',') return false;
    if (cur.value === ')' || cur.value === ',' || cur.value === '(') return false;
    if (cur.type === 'bracket' && (prev.type === 'word' || prev.type === 'table')) return false;
    return true;
  }

  function renderInline(toks, uppercase) {
    var out = '';
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], v = t.value;
      if (t.type === 'word' && uppercase !== false) {
        var up = v.toUpperCase();
        var nextIsParen = i + 1 < toks.length && toks[i + 1].value === '(';
        if (KEYWORDS[up] || nextIsParen) v = up;
      }
      if (i > 0 && inlineSpacing(toks, i)) out += ' ';
      out += v;
    }
    return out;
  }

  function hasComment(toks) {
    return toks.some(function (t) { return t.type === 'comment'; });
  }

  function varExprEnd(toks, start) {
    var d = 0;
    for (var i = start; i < toks.length; i++) {
      var v = toks[i].value;
      if (v === '(') d++;
      else if (v === ')') d--;
      else if (d === 0 && toks[i].type === 'word' && /^(VAR|RETURN)$/i.test(v)) return i;
    }
    return toks.length;
  }

  /**
   * 格式化 DAX。
   * opts.indentSize 默认 4；opts.uppercase 默认 true。
   */
  function format(src, opts) {
    opts = opts || {};
    var IND = new Array((opts.indentSize || 4) + 1).join(' ');
    var toks = tokenize(src).filter(function (t) { return t.type !== 'ws'; });
    if (!toks.length) return '';

    var pairs = buildPairs(toks);
    var breakOf = {};
    for (var k in pairs) {
      if (pairs.hasOwnProperty(k) && Number(k) < pairs[k]) {
        breakOf[k] = groupBreaks(toks, Number(k), pairs[k], pairs);
      }
    }

    var out = [], line = '', indent = 0, groupStack = [], depth = 0, base = 0;

    function pad() { line = new Array(indent + 1).join(IND); }
    function emit(s) { line += s; }
    function newline() { out.push(line.replace(/[ \t]+$/, '')); line = ''; }
    function ensure() { if (line === '') pad(); }
    function flushLine() { if (line.trim() !== '') newline(); }

    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], v = t.value;

      if (t.type === 'comment') {
        ensure();
        if (line.trim() !== '') emit(' ');
        emit(v);
        newline();
        pad();
        continue;
      }

      // DEFINE / EVALUATE 语句
      if (t.type === 'word' && depth === 0 && /^(DEFINE|EVALUATE)$/i.test(v)) {
        base = 1;
        flushLine();
        indent = 0;
        pad();
        emit(v.toUpperCase());
        newline();
        indent = 1;
        pad();
        continue;
      }

      // ORDER BY（EVALUATE 之后）
      if (t.type === 'word' && depth === 0 && /^(ORDER|START|AT)$/i.test(v)) {
        flushLine();
        indent = base;
        pad();
        emit(v.toUpperCase());
        continue;
      }

      // VAR
      if (t.type === 'word' && v.toUpperCase() === 'VAR' && depth === 0) {
        flushLine();
        indent = base;
        pad();
        emit('VAR ' + (toks[i + 1] ? toks[i + 1].value : ''));
        i += 1;
        while (i + 1 < toks.length && toks[i + 1].value !== '=') { i++; emit(' ' + toks[i].value); }
        if (i + 1 < toks.length) { i++; emit(' ='); }

        var end = varExprEnd(toks, i + 1);
        var slice = toks.slice(i + 1, end);
        var inner = renderInline(slice, opts.uppercase);
        if (slice.length && !hasComment(slice) && inner.indexOf('(') === -1 && inner.length <= 70) {
          emit(' ' + inner);
          i = end - 1;
        } else {
          newline();
          indent = base + 1;
          pad();
        }
        continue;
      }

      // RETURN
      if (t.type === 'word' && v.toUpperCase() === 'RETURN' && depth === 0) {
        flushLine();
        indent = base;
        pad();
        emit('RETURN');
        newline();
        indent = base + 1;
        pad();
        continue;
      }

      if (v === '(') {
        var breaks = !!breakOf[i];
        groupStack.push(breaks);
        depth++;
        emit('(');
        if (breaks) {
          newline();
          indent++;
          pad();
        }
        continue;
      }

      if (v === ')') {
        depth--;
        var wasBroken = groupStack.pop();
        if (wasBroken) {
          if (indent > 0) indent--;
          if (line.trim() !== '') newline();
          pad();
        }
        emit(')');
        continue;
      }

      if (v === ',') {
        emit(',');
        var broken = groupStack.length ? groupStack[groupStack.length - 1] : false;
        if (broken) { newline(); pad(); }
        else { emit(' '); }
        continue;
      }

      if (t.type === 'word') {
        var up = v.toUpperCase();
        var nextIsParen = i + 1 < toks.length && toks[i + 1].value === '(';
        var text = (opts.uppercase !== false && (KEYWORDS[up] || nextIsParen)) ? up : v;
        ensure();
        if (line !== '' && !/\s$/.test(line) && inlineSpacing(toks, i)) emit(' ');
        emit(text);
        continue;
      }

      if (t.type === 'punct') {
        if (BINARY_OPS[v] && !tokenIsUnary(toks, i)) {
          ensure();
          if (line.trim() !== '' && !/\s$/.test(line)) emit(' ');
          emit(v);
          emit(' ');
          continue;
        }
        ensure();
        emit(v);
        continue;
      }

      ensure();
      if (line !== '' && !/\s$/.test(line) && inlineSpacing(toks, i)) emit(' ');
      emit(v);
    }

    if (line.trim() !== '') newline();
    while (out.length && out[0].trim() === '') out.shift();
    while (out.length && out[out.length - 1].trim() === '') out.pop();
    return out.join('\n');
  }

  // ---------------------------------------------------------------- lint

  var TUTORIAL = {
    basics: { title: 'DAX Basics', href: '/tutorials/dax-basics/' },
    calc: { title: 'CALCULATE explained', href: '/tutorials/dax-calculate-function/' },
    perf: { title: 'Power BI performance optimisation', href: '/tutorials/power-bi-performance-optimization/' },
    summarize: { title: 'SUMMARIZE vs SUMMARIZECOLUMNS', href: '/tutorials/summarize-vs-summarizecolumns/' },
    errors: { title: 'DAX troubleshooting guide', href: '/tutorials/dax-troubleshooting-guide/' },
    time: { title: 'Time intelligence: YTD, QTD, MTD', href: '/tutorials/dax-time-intelligence-ytd-qtd-mtd/' }
  };

  function issue(sev, id, title, detail, fix, link) {
    return { severity: sev, id: id, title: title, detail: detail, fix: fix, link: link };
  }

  function analyze(src) {
    var raw = tokenize(src);
    var toks = significant(raw);
    if (!toks.length) return { issues: [], stats: { tokens: 0, calls: 0, depth: 0, lines: 0, chars: 0 } };

    var pairs = buildPairs(toks);
    var calls = findCalls(toks, pairs);
    var issues = [];

    var maxDepth = 0;
    for (var i = 0; i < calls.length; i++) maxDepth = Math.max(maxDepth, calls[i].depth);

    // R1 same measure referenced repeatedly → VAR
    // 只统计“独立引用”的度量值：排除 Table[Column] 里的列
    var refCount = {};
    toks.forEach(function (t, idx) {
      if (t.type !== 'bracket') return;
      var prev = toks[idx - 1];
      var qualified = prev && (prev.type === 'table' || prev.type === 'word' || prev.type === 'bracket');
      if (qualified) return;
      refCount[t.value] = (refCount[t.value] || 0) + 1;
    });
    var worstRef = null, worstN = 0;
    Object.keys(refCount).forEach(function (k) {
      if (refCount[k] > worstN) { worstN = refCount[k]; worstRef = k; }
    });
    if (worstN >= 3 && toks.length > 14) {
      issues.push(issue('warn', 'repeated-reference',
        'Same measure evaluated ' + worstN + ' times',
        worstRef + ' appears ' + worstN + ' times. Every reference is a separate evaluation, which is very visible in long expressions.',
        'Store it once: VAR _x = ' + worstRef + ', then reference _x.',
        TUTORIAL.basics));
    }

    // R2 nested CALCULATE
    var calculates = calls.filter(function (c) { return c.upper === 'CALCULATE' || c.upper === 'CALCULATETABLE'; });
    if (calculates.length >= 2) {
      var nested = false;
      calculates.forEach(function (outer) {
        calculates.forEach(function (inner) {
          if (inner === outer) return;
          if (inner.nameIndex > outer.open && inner.nameIndex < outer.close) nested = true;
        });
      });
      if (nested) {
        issues.push(issue('warn', 'nested-calculate', 'Nested CALCULATE',
          'The inner CALCULATE stacks its filter context on top of the outer one. The result is easy to get wrong and some optimisations are blocked.',
          'Merge into a single CALCULATE and control the filter context with KEEPFILTERS / REMOVEFILTERS.',
          TUTORIAL.calc));
      }
    }

    // R3 IFERROR
    var iferrors = calls.filter(function (c) { return c.upper === 'IFERROR'; });
    if (iferrors.length) {
      issues.push(issue('info', 'iferror', 'IFERROR hides the real problem',
        'IFERROR silently replaces errors, so the model looks healthy while divide-by-zero, empty tables or circular dependencies stay invisible. It also adds cost per cell.',
        'Fix the root cause. For division use DIVIDE(a, b) instead.',
        TUTORIAL.errors));
    }

    // R4 iterator over FILTER
    var ITER = { SUMX: 1, AVERAGEX: 1, MAXX: 1, MINX: 1, COUNTX: 1, RANKX: 1 };
    calls.forEach(function (c) {
      if (!ITER[c.upper] || !c.args.length) return;
      var first = c.args[0].toks.filter(function (t) { return t.type !== 'comment'; });
      if (first.length && first[0].type === 'word' && first[0].value.toUpperCase() === 'FILTER') {
        issues.push(issue('warn', 'iterator-over-filter', c.upper + ' over FILTER',
          c.upper + '( FILTER( ... ) ) evaluates the predicate row by row. At millions of rows this is a classic performance killer.',
          'Use CALCULATE( ' + c.upper.replace('X', '') + '( ... ), <condition> ) so the engine aggregates instead of iterating.',
          TUTORIAL.perf));
      }
    });

    // R5 COUNTROWS(FILTER(...))
    calls.forEach(function (c) {
      if (c.upper !== 'COUNTROWS' || !c.args.length) return;
      var a = c.args[0].toks;
      if (a.length && a[0].type === 'word' && a[0].value.toUpperCase() === 'FILTER') {
        issues.push(issue('warn', 'countrows-filter', 'COUNTROWS(FILTER(...))',
          'Materialising a filtered table just to count its rows is much slower than filtering the count directly.',
          'Use CALCULATE( COUNTROWS(T), <condition> ).',
          TUTORIAL.perf));
      }
    });

    // R6 bare division
    var hasSlash = toks.some(function (t) { return t.value === '/'; });
    if (hasSlash) {
      var divProtected = calls.some(function (c) {
        if (c.upper !== 'DIVIDE') return false;
        for (var j = 0; j < toks.length; j++) {
          if (toks[j].value === '/' && j > c.open && j < c.close) return true;
        }
        return false;
      });
      if (!divProtected) {
        issues.push(issue('warn', 'bare-division', 'Division without DIVIDE',
          'a / b raises an error when b is zero or blank, and the whole visual can fail instead of showing a value.',
          'Use DIVIDE(a, b) or DIVIDE(a, b, 0).',
          TUTORIAL.errors));
      }
    }

    // R7 EARLIER
    if (calls.some(function (c) { return c.upper === 'EARLIER'; })) {
      issues.push(issue('info', 'earlier', 'EARLIER is used',
        'EARLIER comes from the early days of row context. It is hard to read and easy to break when the expression is edited.',
        'Capture the current row in a VAR. Same semantics, much clearer.',
        TUTORIAL.basics));
    }

    // R8 SUMMARIZE with added columns
    calls.forEach(function (c) {
      if (c.upper !== 'SUMMARIZE') return;
      if (c.args.length >= 4) {
        issues.push(issue('info', 'summarize-addcolumns', 'SUMMARIZE used to add calculated columns',
          'Arguments after the third one are "name, expression" pairs. This is easy to confuse with group-by columns and performs poorly on large tables.',
          'Use SUMMARIZECOLUMNS, or ADDCOLUMNS( SUMMARIZE(...), ... ).',
          TUTORIAL.summarize));
      }
    });

    // R9 hard-coded DATE()
    calls.forEach(function (c) {
      if (c.upper !== 'DATE' || c.args.length !== 3) return;
      var allConst = c.args.every(function (a) {
        return a.toks.length === 1 && a.toks[0].type === 'number';
      });
      if (allConst) {
        issues.push(issue('info', 'hardcoded-date', 'Hard-coded date in the measure',
          'DATE(' + c.args.map(function (a) { return a.toks[0] ? a.toks[0].value : ''; }).join(', ') + ') bakes a business date into the formula. Next year somebody has to edit the DAX.',
          'Drive it from TODAY(), MAX( Date[Date] ), or a parameter table.',
          TUTORIAL.time));
      }
    });

    // R10 deep nesting
    if (maxDepth >= 4) {
      issues.push(issue('info', 'deep-nesting', 'Deep function nesting (' + (maxDepth + 1) + ' levels)',
        'The deeper the nesting, the harder it is to read and to profile.',
        'Break the expression into named VAR steps.',
        TUTORIAL.basics));
    }

    // R11 FILTER(ALL(...))
    calls.forEach(function (c) {
      if (c.upper !== 'FILTER' || !c.args.length) return;
      var a = c.args[0].toks;
      if (a.length && a[0].type === 'word' && /^(ALL|ALLSELECTED|ALLEXCEPT|ALLNOBLANKROW)$/i.test(a[0].value)) {
        issues.push(issue('warn', 'filter-all', 'FILTER( ' + a[0].value.toUpperCase() + '( ... ) )',
          'FILTER(ALL(...)) materialises a large table. Inside CALCULATE there is almost always an equivalent that is far cheaper.',
          'Use CALCULATE(..., REMOVEFILTERS(Table[Column])) or KEEPFILTERS to express the same intent.',
          TUTORIAL.calc));
      }
    });

    // R12 AND() / OR()
    calls.forEach(function (c) {
      if (c.upper !== 'AND' && c.upper !== 'OR') return;
      issues.push(issue('info', 'and-or-function', 'AND()/OR() instead of operators',
        'The && and || operators are shorter and their short-circuit behaviour is easier to reason about.',
        'Rewrite AND(a,b) as a && b and OR(a,b) as a || b.',
        TUTORIAL.basics));
    });

    var seen = {};
    issues = issues.filter(function (x) {
      if (seen[x.id]) return false;
      seen[x.id] = 1;
      return true;
    });

    var order = { error: 0, warn: 1, info: 2 };
    issues.sort(function (a, b) { return order[a.severity] - order[b.severity]; });

    return {
      issues: issues,
      stats: {
        tokens: toks.length,
        calls: calls.length,
        depth: maxDepth + 1,
        lines: String(src).split(/\r?\n/).length,
        chars: String(src).length
      }
    };
  }

  var API = { tokenize: tokenize, format: format, analyze: analyze, version: '0.1.0' };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  global.DAXTool = API;
})(typeof window !== 'undefined' ? window : globalThis);
