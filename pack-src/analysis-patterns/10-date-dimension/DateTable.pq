// ============================================================
// 10 — DYNAMIC DATE DIMENSION
// A marked date table with fiscal-year support, built in Power
// Query. Paste into Advanced Editor as a new query named "Date".
// Set StartDate / EndDate / FiscalStartMonth for your model.
// No dependency on any fact table — the range is explicit.
// ============================================================

let
    // --- Configuration ---------------------------------------
    StartDate = #date(2020, 1, 1),
    EndDate   = #date(2027, 12, 31),
    FiscalStartMonth = 7,   // 7 = July start; set 1 for calendar year

    // --- Generate the date column ----------------------------
    DateCount = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, DateCount, #duration(1, 0, 0, 0)),
    T = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    TypedDate = Table.TransformColumnTypes(T, {{"Date", type date}}),

    // --- Standard columns ------------------------------------
    WithYear    = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    WithMonthNo = Table.AddColumn(WithYear, "MonthNo", each Date.Month([Date]), Int64.Type),
    WithMonth   = Table.AddColumn(WithMonthNo, "Month", each Date.ToText([Date], "MMM"), type text),
    WithQuarter = Table.AddColumn(WithMonth, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    WithDay     = Table.AddColumn(WithQuarter, "DayOfWeek", each Date.DayOfWeekName([Date]), type text),
    WithISOWeek = Table.AddColumn(WithDay, "ISOWeek", each Date.WeekOfYear([Date]), Int64.Type),

    // YearMonth as sortable integer (e.g. 202607), plus a label.
    WithYearMonth = Table.AddColumn(WithISOWeek, "YearMonthNo", each [Year] * 100 + [MonthNo], Int64.Type),
    WithYMLabel   = Table.AddColumn(WithYearMonth, "YearMonth", each Text.From([Year]) & "-" & Text.PadStart(Text.From([MonthNo]), 2, "0"), type text),

    // --- Fiscal columns --------------------------------------
    FiscalYear = Table.AddColumn(WithYMLabel, "FiscalYear",
        each if [MonthNo] >= FiscalStartMonth then [Year] + 1 else [Year],
        Int64.Type),
    FiscalQuarter = Table.AddColumn(FiscalYear, "FiscalQuarter",
        each "Q" & Text.From(Number.IntegerDivide(
            Number.Mod([MonthNo] - FiscalStartMonth, 12), 3) + 1),
        type text),

    // --- Helpers ---------------------------------------------
    IsWeekend = Table.AddColumn(FiscalQuarter, "IsWeekend",
        each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical),

    // Sort Month labels by MonthNo so visuals order correctly.
    Sorted = Table.Sort(IsWeekend, {{"Date", Order.Ascending}})
in
    Sorted

// After loading:
//  1. Select the Date column → Column tools → Mark as date table.
//  2. Set "Sort by column": Month sorted by MonthNo.
//  3. Relate Date[Date] one-to-many to each fact's date column.
//  4. Hide MonthNo, ISOWeek, YearMonthNo if you do not plot them.
