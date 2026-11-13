/* Date table generator — DAX + Power Query M */
(function () {
  'use strict';

  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  var $ = function (id) { return document.getElementById(id); };

  function pad(n) { return String(n).padStart(2, '0'); }

  function buildColumns(opts) {
    var fs = opts.fiscalStart;
    var cols = [];
    cols.push({ name: 'Year', type: 'Int64.Type', dax: 'YEAR([Date])', m: 'Date.Year([Date])' });
    cols.push({ name: 'Quarter Number', type: 'Int64.Type', dax: 'QUARTER([Date])', m: 'Date.QuarterOfYear([Date])' });
    cols.push({ name: 'Quarter', type: 'Text.Type', dax: '"Q" & QUARTER([Date])', m: '"Q" & Text.From(Date.QuarterOfYear([Date]))' });
    cols.push({ name: 'Month Number', type: 'Int64.Type', dax: 'MONTH([Date])', m: 'Date.Month([Date])' });
    cols.push({ name: 'Month', type: 'Text.Type', dax: 'FORMAT([Date], "MMMM")', m: 'Date.MonthName([Date])' });
    cols.push({ name: 'Month Short', type: 'Text.Type', dax: 'FORMAT([Date], "MMM")', m: 'Date.ToText([Date], "MMM")' });
    cols.push({ name: 'Month Year', type: 'Text.Type', dax: 'FORMAT([Date], "MMM YYYY")', m: 'Date.ToText([Date], "MMM yyyy")' });
    cols.push({ name: 'Year Month', type: 'Text.Type', dax: 'FORMAT([Date], "YYYY-MM")', m: 'Date.ToText([Date], "yyyy-MM")' });
    cols.push({ name: 'Year Month Sort', type: 'Int64.Type', dax: 'YEAR([Date]) * 100 + MONTH([Date])', m: 'Date.Year([Date]) * 100 + Date.Month([Date])' });
    cols.push({ name: 'Day', type: 'Int64.Type', dax: 'DAY([Date])', m: 'Date.Day([Date])' });
    cols.push({ name: 'Day Name', type: 'Text.Type', dax: 'FORMAT([Date], "dddd")', m: 'Date.DayOfWeekName([Date])' });

    if (opts.weekStart === 'sunday') {
      cols.push({ name: 'Day Of Week', type: 'Int64.Type', dax: 'WEEKDAY([Date], 1)', m: 'Date.DayOfWeek([Date], Day.Sunday) + 1' });
      cols.push({ name: 'Is Weekend', type: 'Logical.Type', dax: 'WEEKDAY([Date], 1) = 1 || WEEKDAY([Date], 1) = 7', m: 'Date.DayOfWeek([Date], Day.Sunday) = 0 or Date.DayOfWeek([Date], Day.Sunday) = 6' });
    } else {
      cols.push({ name: 'Day Of Week', type: 'Int64.Type', dax: 'WEEKDAY([Date], 2)', m: 'Date.DayOfWeek([Date], Day.Monday) + 1' });
      cols.push({ name: 'Is Weekend', type: 'Logical.Type', dax: 'WEEKDAY([Date], 2) >= 6', m: 'Date.DayOfWeek([Date], Day.Monday) >= 5' });
    }

    if (opts.isoWeek) {
      cols.push({ name: 'Week Number', type: 'Int64.Type', dax: 'WEEKNUM([Date], 21)', m: 'ISOWeek([Date])' });
    } else if (opts.weekStart === 'sunday') {
      cols.push({ name: 'Week Number', type: 'Int64.Type', dax: 'WEEKNUM([Date], 1)', m: 'Date.WeekOfYear([Date], Day.Sunday)' });
    } else {
      cols.push({ name: 'Week Number', type: 'Int64.Type', dax: 'WEEKNUM([Date], 2)', m: 'Date.WeekOfYear([Date], Day.Monday)' });
    }

    if (opts.fiscal) {
      var fy = opts.fiscalNaming === 'start'
        ? 'YEAR([Date]) - IF(MONTH([Date]) < FiscalStartMonth, 1, 0)'
        : 'YEAR([Date]) + IF(MONTH([Date]) >= FiscalStartMonth, 1, 0)';
      var fyM = opts.fiscalNaming === 'start'
        ? 'Date.Year([Date]) - (if Date.Month([Date]) < FiscalStartMonth then 1 else 0)'
        : 'Date.Year([Date]) + (if Date.Month([Date]) >= FiscalStartMonth then 1 else 0)';

      cols.push({ name: 'Fiscal Year', type: 'Int64.Type', dax: fy, m: fyM });
      cols.push({
        name: 'Fiscal Quarter',
        type: 'Int64.Type',
        dax: 'INT(MOD(MONTH([Date]) - FiscalStartMonth + 12, 12) / 3) + 1',
        m: 'Number.IntegerDivide(Number.Mod(Date.Month([Date]) - FiscalStartMonth + 12, 12), 3) + 1'
      });
      cols.push({
        name: 'Fiscal Month Number',
        type: 'Int64.Type',
        dax: 'MOD(MONTH([Date]) - FiscalStartMonth + 12, 12) + 1',
        m: 'Number.Mod(Date.Month([Date]) - FiscalStartMonth + 12, 12) + 1'
      });
    }

    if (opts.currentFlags) {
      cols.push({
        name: 'Is Current Month',
        type: 'Logical.Type',
        dax: '[Date] >= DATE(YEAR(TODAY()), MONTH(TODAY()), 1) && [Date] <= EOMONTH(TODAY(), 0)',
        m: 'Date.Month([Date]) = Date.Month(DateTime.LocalNow()) and Date.Year([Date]) = Date.Year(DateTime.LocalNow())'
      });
      cols.push({
        name: 'Is Current Year',
        type: 'Logical.Type',
        dax: 'YEAR([Date]) = YEAR(TODAY())',
        m: 'Date.Year([Date]) = Date.Year(DateTime.LocalNow())'
      });
    }

    return cols;
  }

  function buildDax(opts) {
    var cols = buildColumns(opts);
    var lines = [];
    lines.push('DimDate =');
    lines.push('VAR StartDate        = DATE(' + opts.startYear + ', 1, 1)');
    lines.push('VAR EndDate          = DATE(' + opts.endYear + ', 12, 31)');
    if (opts.fiscal) lines.push('VAR FiscalStartMonth = ' + opts.fiscalStart);
    lines.push('RETURN');
    lines.push('    ADDCOLUMNS(');
    lines.push('        CALENDAR(StartDate, EndDate),');
    cols.forEach(function (c, i) {
      var comma = i === cols.length - 1 ? '' : ',';
      lines.push('        "' + c.name + '", ' + c.dax + comma);
    });
    lines.push('    )');
    return lines.join('\n');
  }

  function buildM(opts) {
    var cols = buildColumns(opts);
    var headers = [];
    headers.push(['StartDate', '#date(' + opts.startYear + ', 1, 1)']);
    headers.push(['EndDate', '#date(' + opts.endYear + ', 12, 31)']);
    if (opts.fiscal) headers.push(['FiscalStartMonth', String(opts.fiscalStart)]);
    headers.push(['DayCount', 'Duration.Days(EndDate - StartDate) + 1']);
    headers.push(['Source', 'List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0))']);
    headers.push(['ToTable', 'Table.FromList(Source, Splitter.SplitByNothing(), {"Date"})']);
    headers.push(['Typed', 'Table.TransformColumnTypes(ToTable, {{"Date", type date}})']);

    var lines = ['let'];
    headers.forEach(function (h) {
      lines.push('    ' + h[0] + ' = ' + h[1] + ',');
    });
    lines.push('');

    var prev = 'Typed';
    cols.forEach(function (c, idx) {
      var step = 'Added' + c.name.replace(/[^A-Za-z0-9]/g, '');
      var isLast = idx === cols.length - 1;
      if (c.m.indexOf('ISOWeek(') !== -1) {
        lines.push('    ' + step + ' = Table.AddColumn(' + prev + ', "' + c.name + '", each');
        lines.push('        let');
        lines.push('            _thu  = Date.AddDays([Date], 3 - Date.DayOfWeek([Date], Day.Monday)),');
        lines.push('            _jan1 = #date(Date.Year(_thu), 1, 1)');
        lines.push('        in');
        lines.push('            Number.RoundDown(Duration.Days(_thu - _jan1) / 7) + 1,');
        lines.push('        ' + c.type + ')');
      } else {
        lines.push('    ' + step + ' = Table.AddColumn(' + prev + ', "' + c.name + '", each ' + c.m + ', ' + c.type + ')');
      }
      if (!isLast) lines[lines.length - 1] += ',';
      prev = step;
    });

    lines.push('in');
    lines.push('    ' + prev);
    return lines.join('\n');
  }

  function readOptions() {
    var start = parseInt($('start-year').value, 10);
    var end = parseInt($('end-year').value, 10);
    if (!isFinite(start)) start = 2023;
    if (!isFinite(end)) end = start + 3;
    if (end < start) end = start;
    if (end - start > 60) end = start + 60;
    return {
      startYear: start,
      endYear: end,
      fiscalStart: parseInt($('fiscal-start').value, 10) || 1,
      fiscalNaming: $('fiscal-naming').value,
      weekStart: $('week-start').value,
      isoWeek: $('iso-week').checked,
      fiscal: $('fiscal-cols').checked,
      currentFlags: $('current-flags').checked
    };
  }

  function render() {
    var opts = readOptions();
    var dax = buildDax(opts);
    var m = buildM(opts);
    $('dax-out').textContent = dax;
    $('m-out').textContent = m;
    var days = Math.round((Date.UTC(opts.endYear + 1, 0, 1) - Date.UTC(opts.startYear, 0, 1)) / 86400000);
    $('range-note').textContent = opts.startYear + '–' + opts.endYear + ' · ' + days.toLocaleString() + ' rows';
    $('fiscal-naming-field').style.display = opts.fiscal ? '' : 'none';
  }

  function copy(el, btn) {
    var text = el.textContent;
    function done() {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1400);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, fallback);
    } else { fallback(); }
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
    ['start-year', 'end-year', 'fiscal-start', 'fiscal-naming', 'week-start', 'iso-week', 'fiscal-cols', 'current-flags']
      .forEach(function (id) {
        var el = $(id);
        el.addEventListener('input', render);
        el.addEventListener('change', render);
      });

    $('copy-dax').addEventListener('click', function () { copy($('dax-out'), $('copy-dax')); });
    $('copy-m').addEventListener('click', function () { copy($('m-out'), $('copy-m')); });

    var tabs = document.querySelectorAll('.tab');
    Array.prototype.forEach.call(tabs, function (tab) {
      tab.addEventListener('click', function () {
        Array.prototype.forEach.call(tabs, function (t) { t.setAttribute('aria-selected', 'false'); });
        tab.setAttribute('aria-selected', 'true');
        var target = tab.getAttribute('data-target');
        $('dax-out').style.display = target === 'dax' ? '' : 'none';
        $('m-out').style.display = target === 'm' ? '' : 'none';
      });
    });

    render();
  });
})();
