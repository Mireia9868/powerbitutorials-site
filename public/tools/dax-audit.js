/* DAX audit page controller */
(function () {
  'use strict';

  var STORAGE_KEY = 'pbit-dax-audit-v1';
  var SAMPLE = [
    'Sales LY Growth =',
    'IFERROR(',
    '  (SUM(Sales[Amount]) - CALCULATE(SUM(Sales[Amount]), FILTER(ALL(\'Date\'[Date]), \'Date\'[Date] < DATE(2024,1,1))))',
    '  / CALCULATE(SUM(Sales[Amount]), FILTER(ALL(\'Date\'[Date]), \'Date\'[Date] < DATE(2024,1,1))),',
    '  0',
    ')'
  ].join('\n');

  var $ = function (id) { return document.getElementById(id); };

  var input, output, issueList, statsEl, summaryEl, copyBtn, clearBtn, sampleBtn;

  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }

  function severityLabel(sev) {
    if (sev === 'warn') return 'Fix';
    if (sev === 'error') return 'Error';
    return 'Tip';
  }

  function render() {
    var src = input.value;
    if (!src.trim()) {
      output.textContent = '// Your formatted DAX will appear here';
      output.classList.add('empty');
      issueList.innerHTML = '<div class="empty-state">Paste a measure on the left to see the checks.</div>';
      summaryEl.textContent = 'Waiting for input';
      statsEl.innerHTML = '';
      return;
    }

    var formatted, analysis;
    try {
      formatted = window.DAXTool.format(src);
      analysis = window.DAXTool.analyze(src);
    } catch (err) {
      output.textContent = '// Could not parse this input.\n// ' + (err && err.message ? err.message : err);
      issueList.innerHTML = '<div class="empty-state">The parser stopped on this input. Check for unbalanced parentheses or quotes.</div>';
      summaryEl.textContent = 'Parse error';
      statsEl.innerHTML = '';
      return;
    }

    output.textContent = formatted;
    output.classList.remove('empty');

    var s = analysis.stats;
    statsEl.innerHTML =
      '<span><b>' + s.calls + '</b> function calls</span>' +
      '<span><b>' + s.depth + '</b> max nesting</span>' +
      '<span><b>' + s.tokens + '</b> tokens</span>' +
      '<span><b>' + s.lines + '</b> input lines</span>';

    var issues = analysis.issues;
    if (!issues.length) {
      issueList.innerHTML = '<div class="empty-state">No issues found by the current rule set. That does not prove the measure is correct — only that it avoids the common traps we check for.</div>';
      summaryEl.textContent = 'No issues found';
      summaryEl.className = 'summary ok';
      return;
    }

    summaryEl.textContent = issues.length + (issues.length === 1 ? ' issue' : ' issues') + ' to review';
    summaryEl.className = 'summary has-issues';

    var frag = document.createDocumentFragment();
    issues.forEach(function (it) {
      var wrap = document.createElement('article');
      wrap.className = 'issue ' + it.severity;

      var h = document.createElement('h4');
      var badge = document.createElement('span');
      badge.className = 'sev';
      badge.textContent = severityLabel(it.severity);
      h.appendChild(badge);
      h.appendChild(document.createTextNode(it.title));
      wrap.appendChild(h);

      var p = document.createElement('p');
      p.textContent = it.detail;
      wrap.appendChild(p);

      if (it.fix) {
        var fix = document.createElement('div');
        fix.className = 'fix';
        fix.textContent = it.fix;
        wrap.appendChild(fix);
      }
      if (it.link) {
        var a = document.createElement('a');
        a.className = 'learn';
        a.href = it.link.href;
        a.textContent = 'Read: ' + it.link.title + ' →';
        wrap.appendChild(a);
      }
      frag.appendChild(wrap);
    });
    issueList.innerHTML = '';
    issueList.appendChild(frag);
  }

  var runSoon = debounce(render, 220);

  function copy(text, btn) {
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else {
      fallback();
    }
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
      document.body.removeChild(ta);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    input = $('dax-input');
    output = $('dax-output');
    issueList = $('issues');
    statsEl = $('stats');
    summaryEl = $('summary');
    copyBtn = $('copy-btn');
    clearBtn = $('clear-btn');
    sampleBtn = $('sample-btn');

    var saved = '';
    try { saved = localStorage.getItem(STORAGE_KEY) || ''; } catch (e) { saved = ''; }
    input.value = saved || SAMPLE;

    input.addEventListener('input', function () {
      try { localStorage.setItem(STORAGE_KEY, input.value); } catch (e) { /* ignore */ }
      runSoon();
    });

    input.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        render();
      }
    });

    copyBtn.addEventListener('click', function () {
      copy(output.textContent, copyBtn);
    });

    clearBtn.addEventListener('click', function () {
      input.value = '';
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) { /* ignore */ }
      render();
      input.focus();
    });

    sampleBtn.addEventListener('click', function () {
      input.value = SAMPLE;
      try { localStorage.setItem(STORAGE_KEY, SAMPLE); } catch (e) { /* ignore */ }
      render();
    });

    render();
  });
})();
