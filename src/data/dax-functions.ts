/**
 * DAX function reference data.
 *
 * Only functions people actually search for: aggregation, filter context,
 * time intelligence, logical, text, table and relationship.
 * Every entry needs: copyable syntax, a one-line explanation, a working example.
 */

export interface DaxFunction {
  name: string;
  category: string;
  syntax: string;
  summary: string;
  example: string;
  /** Optional related tutorial on this site */
  href?: string;
}

export const CATEGORIES = [
  "Aggregation",
  "Filter context",
  "Time intelligence",
  "Logical",
  "Text",
  "Math & statistics",
  "Tables & relationships",
  "Information",
] as const;

export const DAX_FUNCTIONS: DaxFunction[] = [
  // ---------------------------------------------------------- Aggregation
  {
    name: "SUM",
    category: "Aggregation",
    syntax: "SUM ( <Column> )",
    summary: "Adds up every visible row of a single column. It takes a column, not an expression — use SUMX when you need row-level maths.",
    example: "Total Sales = SUM ( Sales[Amount] )",
  },
  {
    name: "SUMX",
    category: "Aggregation",
    syntax: "SUMX ( <Table>, <Expression> )",
    summary: "Evaluates the expression row by row, then sums the results. Required for line-level maths such as quantity × price.",
    example: "Revenue = SUMX ( Sales, Sales[Qty] * Sales[Price] )",
  },
  {
    name: "AVERAGE",
    category: "Aggregation",
    syntax: "AVERAGE ( <Column> )",
    summary: "Arithmetic mean of a column, ignoring blanks. It does not weight anything, so the answer depends on what is on the axis.",
    example: "Avg Order Value = AVERAGE ( Sales[OrderAmount] )",
  },
  {
    name: "AVERAGEX",
    category: "Aggregation",
    syntax: "AVERAGEX ( <Table>, <Expression> )",
    summary: "Averages the result of an expression evaluated per row. Use it for things like average revenue per customer.",
    example: "Avg per Customer = AVERAGEX ( VALUES ( Customer[Id] ), [Total Sales] )",
  },
  {
    name: "COUNTROWS",
    category: "Aggregation",
    syntax: "COUNTROWS ( <Table> )",
    summary: "Counts the rows of a table. Prefer it to COUNT on a key column — it is explicit and cannot be fooled by blanks.",
    example: "Orders = COUNTROWS ( Sales )",
  },
  {
    name: "DISTINCTCOUNT",
    category: "Aggregation",
    syntax: "DISTINCTCOUNT ( <Column> )",
    summary: "Counts distinct values. Note that BLANK counts as a value; use DISTINCTCOUNTNOBLANK when that matters.",
    example: "Customers = DISTINCTCOUNT ( Sales[CustomerId] )",
  },
  {
    name: "MIN",
    category: "Aggregation",
    syntax: "MIN ( <Column> | <Expression1>, <Expression2> )",
    summary: "With a column: the smallest value, blanks ignored. With two arguments: the smaller of the two expressions.",
    example: "First Sale = MIN ( Sales[OrderDate] )",
  },
  {
    name: "MAX",
    category: "Aggregation",
    syntax: "MAX ( <Column> | <Expression1>, <Expression2> )",
    summary: "With a column: the largest value. With two arguments: the larger expression. The column form drives most dynamic date filters.",
    example: "Last Date = MAX ( 'Date'[Date] )",
  },

  // ------------------------------------------------------- Filter context
  {
    name: "CALCULATE",
    category: "Filter context",
    syntax: "CALCULATE ( <Expression>, <Filter1>, <Filter2>, … )",
    summary: "Evaluates an expression in a modified filter context, and performs context transition. The most important function in DAX.",
    example: "Red Sales = CALCULATE ( [Total Sales], Product[Color] = \"Red\" )",
    href: "/tutorials/calculate-function/",
  },
  {
    name: "CALCULATETABLE",
    category: "Filter context",
    syntax: "CALCULATETABLE ( <Table>, <Filter>, … )",
    summary: "Same filtering semantics as CALCULATE but returns a table. Used to build intermediate result sets.",
    example: "Red Products = CALCULATETABLE ( Product, Product[Color] = \"Red\" )",
  },
  {
    name: "FILTER",
    category: "Filter context",
    syntax: "FILTER ( <Table>, <Condition> )",
    summary: "Returns the rows that satisfy a condition, evaluated row by row. The easiest way to write a slow measure — prefer CALCULATE's filter arguments.",
    example: "Big Orders = FILTER ( Sales, Sales[Amount] > 1000 )",
    href: "/tutorials/dax-optimization-techniques/",
  },
  {
    name: "ALL",
    category: "Filter context",
    syntax: "ALL ( <TableOrColumn>, … )",
    summary: "Removes filters from a table or column. The standard way to compute a share of the total, because it also ignores slicers.",
    example: "Share of All = DIVIDE ( [Total Sales], CALCULATE ( [Total Sales], ALL ( Product ) ) )",
  },
  {
    name: "ALLSELECTED",
    category: "Filter context",
    syntax: "ALLSELECTED ( <TableOrColumn> )",
    summary: "Removes filters but keeps the current slicer selection. The difference from ALL shows up as soon as a visual has its own filters.",
    example: "Share of Selected = DIVIDE ( [Total Sales], CALCULATE ( [Total Sales], ALLSELECTED ( Product ) ) )",
    href: "/tutorials/summarize-vs-summarizecolumns/",
  },
  {
    name: "ALLEXCEPT",
    category: "Filter context",
    syntax: "ALLEXCEPT ( <Table>, <ColumnToKeep>, … )",
    summary: "Removes every filter on a table except the listed columns. The usual tool for \"share within this customer\".",
    example: "Customer Share = DIVIDE ( [Total Sales], CALCULATE ( [Total Sales], ALLEXCEPT ( Customer, Customer[Id] ) ) )",
  },
  {
    name: "REMOVEFILTERS",
    category: "Filter context",
    syntax: "REMOVEFILTERS ( <TableOrColumn>, … )",
    summary: "Same result as ALL but states the intent explicitly. Prefer it in new code for readability.",
    example: "All Years = CALCULATE ( [Total Sales], REMOVEFILTERS ( 'Date' ) )",
  },
  {
    name: "KEEPFILTERS",
    category: "Filter context",
    syntax: "KEEPFILTERS ( <Expression> )",
    summary: "Intersects a filter with the existing context instead of replacing it. Use it when filters should stack, not override.",
    example: "Keep Selection = CALCULATE ( [Total Sales], KEEPFILTERS ( Product[Color] = \"Red\" ) )",
  },
  {
    name: "SELECTEDVALUE",
    category: "Filter context",
    syntax: "SELECTEDVALUE ( <Column>, <AlternateResult> )",
    summary: "Returns the single value in context, or the alternate result when there is more than one. The standard pattern for dynamic titles and slicer-driven measures.",
    example: "Currency = SELECTEDVALUE ( Config[Currency], \"EUR\" )",
  },
  {
    name: "VALUES",
    category: "Filter context",
    syntax: "VALUES ( <TableOrColumn> )",
    summary: "The distinct values visible in the current context. Unlike DISTINCT, it keeps the blank row that relationships can introduce.",
    example: "Visible Products = COUNTROWS ( VALUES ( Product[Id] ) )",
  },
  {
    name: "ISFILTERED",
    category: "Filter context",
    syntax: "ISFILTERED ( <Column> )",
    summary: "True when a column is directly filtered. Useful for wording a title around what the user actually selected.",
    example: "Label = IF ( ISFILTERED ( Product[Category] ), \"Filtered\", \"All products\" )",
  },

  // ----------------------------------------------------- Time intelligence
  {
    name: "TOTALYTD",
    category: "Time intelligence",
    syntax: "TOTALYTD ( <Expression>, <Dates>, <Filter>, <YearEndDate> )",
    summary: "Year-to-date total. For a non-December fiscal year the fourth argument is the fiscal year end, and omitting it produces wrong numbers with no error.",
    example: "Sales YTD = TOTALYTD ( [Total Sales], 'Date'[Date] )",
    href: "/tutorials/dax-time-intelligence-ytd-qtd-mtd/",
  },
  {
    name: "DATEADD",
    category: "Time intelligence",
    syntax: "DATEADD ( <Dates>, <NumberOfIntervals>, <Interval> )",
    summary: "Shifts a set of dates by N intervals (DAY, MONTH, QUARTER, YEAR). Month-end dates can produce blanks, which is why it disagrees with PREVIOUSMONTH.",
    example: "Sales LM = CALCULATE ( [Total Sales], DATEADD ( 'Date'[Date], -1, MONTH ) )",
    href: "/tutorials/previousmonth-vs-dateadd/",
  },
  {
    name: "SAMEPERIODLASTYEAR",
    category: "Time intelligence",
    syntax: "SAMEPERIODLASTYEAR ( <Dates> )",
    summary: "Returns the equivalent dates one year earlier. Same result as DATEADD with -1 YEAR, easier to read.",
    example: "Sales LY = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )",
    href: "/tutorials/sameperiodlastyear-comparison-patterns/",
  },
  {
    name: "DATESINPERIOD",
    category: "Time intelligence",
    syntax: "DATESINPERIOD ( <Dates>, <StartDate>, <NumberOfIntervals>, <Interval> )",
    summary: "A contiguous run of dates starting at a point. The building block for rolling 12 months and rolling 90 days.",
    example: "Sales R12M = CALCULATE ( [Total Sales], DATESINPERIOD ( 'Date'[Date], MAX ( 'Date'[Date] ), -12, MONTH ) )",
    href: "/tutorials/rolling-averages-moving-sums-dax/",
  },
  {
    name: "DATESYTD",
    category: "Time intelligence",
    syntax: "DATESYTD ( <Dates>, <YearEndDate> )",
    summary: "The set of dates from the start of the year to the current date. TOTALYTD is essentially sugar on top of it.",
    example: "Sales YTD = CALCULATE ( [Total Sales], DATESYTD ( 'Date'[Date] ) )",
  },
  {
    name: "STARTOFMONTH",
    category: "Time intelligence",
    syntax: "STARTOFMONTH ( <Dates> )",
    summary: "The first day of the month in the current context. Useful for month-to-date comparisons.",
    example: "MTD Start = STARTOFMONTH ( 'Date'[Date] )",
  },
  {
    name: "ENDOFMONTH",
    category: "Time intelligence",
    syntax: "ENDOFMONTH ( <Dates> )",
    summary: "The last day of the current month, as a date. Not a day number.",
    example: "Month End = ENDOFMONTH ( 'Date'[Date] )",
  },
  {
    name: "EOMONTH",
    category: "Time intelligence",
    syntax: "EOMONTH ( <StartDate>, <Months> )",
    summary: "The last day of the month N months away. Common for due dates and accounting periods.",
    example: "Due Date = EOMONTH ( Invoice[Date], 1 )",
  },
  {
    name: "YEAR",
    category: "Time intelligence",
    syntax: "YEAR ( <Date> )",
    summary: "Extracts the year as an integer. Don't use it for year-to-date maths — that needs the time intelligence functions over a marked date table.",
    example: "Year = YEAR ( 'Date'[Date] )",
  },
  {
    name: "MONTH",
    category: "Time intelligence",
    syntax: "MONTH ( <Date> )",
    summary: "Extracts the month number, 1 to 12. Format the name separately and sort it with a month-number column.",
    example: "Month No = MONTH ( 'Date'[Date] )",
  },

  // ---------------------------------------------------------------- Logical
  {
    name: "IF",
    category: "Logical",
    syntax: "IF ( <Condition>, <ResultIfTrue>, <ResultIfFalse> )",
    summary: "Branching. Past two branches, switch to SWITCH: nested IFs are slower to read and harder to debug.",
    example: "Target Met = IF ( [Total Sales] >= [Target], \"Yes\", \"No\" )",
    href: "/tutorials/dax-switch-function/",
  },
  {
    name: "SWITCH",
    category: "Logical",
    syntax: "SWITCH ( <Expression>, <Value1>, <Result1>, …, <Else> )",
    summary: "Multi-branch logic that reads like a table. Pair it with TRUE() to express ranges.",
    example: "Band = SWITCH ( TRUE (), [Margin] > 0.4, \"High\", [Margin] > 0.2, \"Mid\", \"Low\" )",
    href: "/tutorials/dax-switch-function/",
  },
  {
    name: "DIVIDE",
    category: "Logical",
    syntax: "DIVIDE ( <Numerator>, <Denominator>, <AlternateResult> )",
    summary: "Safe division: returns the alternate result instead of an error when the denominator is zero or blank. Use it for every ratio; never use /.",
    example: "Margin % = DIVIDE ( [Gross Profit], [Revenue] )",
  },
  {
    name: "COALESCE",
    category: "Logical",
    syntax: "COALESCE ( <Expression>, <Expression>, … )",
    summary: "The first non-blank value. Replaces the IF( ISBLANK( … ), … ) pattern.",
    example: "Name = COALESCE ( Customer[Company], Customer[Email], \"Unknown\" )",
  },
  {
    name: "AND",
    category: "Logical",
    syntax: "AND ( <Condition1>, <Condition2> )",
    summary: "Logical AND. In practice use && — it is shorter and its short-circuit behaviour is easier to reason about.",
    example: "Valid = AND ( [Sales] > 0, [Qty] > 0 )",
  },
  {
    name: "OR",
    category: "Logical",
    syntax: "OR ( <Condition1>, <Condition2> )",
    summary: "Logical OR. In practice use ||.",
    example: "Priority = OR ( [Value] > 1000, [Flag] = TRUE () )",
  },
  {
    name: "NOT",
    category: "Logical",
    syntax: "NOT ( <Condition> )",
    summary: "Negates a condition. Often a <> comparison is clearer.",
    example: "Not Red = NOT ( Product[Color] = \"Red\" )",
  },
  {
    name: "IFERROR",
    category: "Logical",
    syntax: "IFERROR ( <Value>, <AlternateResult> )",
    summary: "Catches errors and substitutes a value. It hides the real cause (divide by zero, empty table, circular dependency), so only use it when you mean to.",
    example: "Safe = IFERROR ( [Risky Measure], BLANK () )",
    href: "/tutorials/dax-troubleshooting-guide/",
  },

  // ------------------------------------------------------------------ Text
  {
    name: "FORMAT",
    category: "Text",
    syntax: "FORMAT ( <Value>, <FormatString> )",
    summary: "Formats a value as text. The result can no longer be summed and follows the model culture — never use it to sort dates.",
    example: "Month Label = FORMAT ( 'Date'[Date], \"MMM YYYY\" )",
  },
  {
    name: "CONCATENATE",
    category: "Text",
    syntax: "CONCATENATE ( <Text1>, <Text2> )",
    summary: "Joins two strings. The & operator is shorter and easier to read.",
    example: "Label = CONCATENATE ( Product[Brand], Product[Model] )",
  },
  {
    name: "CONCATENATEX",
    category: "Text",
    syntax: "CONCATENATEX ( <Table>, <Expression>, <Delimiter> )",
    summary: "Joins the values of an expression across a table. The tool for \"list this customer's orders\" in one cell.",
    example: "Order List = CONCATENATEX ( Sales, Sales[OrderId], \", \" )",
  },
  {
    name: "LEFT",
    category: "Text",
    syntax: "LEFT ( <Text>, <NumberOfCharacters> )",
    summary: "The first N characters of a string.",
    example: "Prefix = LEFT ( Product[Code], 3 )",
  },
  {
    name: "RIGHT",
    category: "Text",
    syntax: "RIGHT ( <Text>, <NumberOfCharacters> )",
    summary: "The last N characters of a string.",
    example: "Suffix = RIGHT ( Product[Code], 4 )",
  },
  {
    name: "MID",
    category: "Text",
    syntax: "MID ( <Text>, <StartPosition>, <Length> )",
    summary: "Characters from the middle of a string. Positions start at 1, not 0.",
    example: "Middle = MID ( Product[Code], 4, 3 )",
  },
  {
    name: "SEARCH",
    category: "Text",
    syntax: "SEARCH ( <FindText>, <WithinText>, <StartPosition>, <NotFoundValue> )",
    summary: "Finds a substring, case-insensitive, and returns an error when it is missing. Use FIND for case-sensitive matching.",
    example: "Pos = SEARCH ( \"Pro\", Product[Name], 1, 0 )",
  },
  {
    name: "SUBSTITUTE",
    category: "Text",
    syntax: "SUBSTITUTE ( <Text>, <OldText>, <NewText>, <InstanceNumber> )",
    summary: "Replaces by content rather than by position — the usual way to strip fixed junk out of imported text.",
    example: "Clean = SUBSTITUTE ( Customer[Phone], \" \", \"\" )",
  },
  {
    name: "TRIM",
    category: "Text",
    syntax: "TRIM ( <Text> )",
    summary: "Removes leading and trailing spaces and collapses internal runs of spaces. Do it right after importing.",
    example: "Clean Name = TRIM ( Customer[Name] )",
  },

  // ------------------------------------------------------ Math & statistics
  {
    name: "ROUND",
    category: "Math & statistics",
    syntax: "ROUND ( <Number>, <NumberOfDigits> )",
    summary: "Rounds to N digits. To display two decimals, set the format string instead of rounding the measure.",
    example: "Rounded = ROUND ( [Margin %], 2 )",
  },
  {
    name: "ABS",
    category: "Math & statistics",
    syntax: "ABS ( <Number> )",
    summary: "Absolute value. Common in variance analysis and volatility measures.",
    example: "Abs Variance = ABS ( [Variance] )",
  },
  {
    name: "RANKX",
    category: "Math & statistics",
    syntax: "RANKX ( <Table>, <Expression>, <Value>, <Order>, <Ties> )",
    summary: "Ranks rows by an expression. Descending by default and skips ties unless you pass DENSE. It evaluates per row, so keep the table small.",
    example: "Product Rank = RANKX ( ALL ( Product ), [Total Sales] )",
    href: "/tutorials/dax-rankx-function/",
  },
  {
    name: "PERCENTILE.INC",
    category: "Math & statistics",
    syntax: "PERCENTILE.INC ( <Column>, <K> )",
    summary: "The K-th percentile, endpoints included. Usually a better description of response times than an average.",
    example: "P90 = PERCENTILE.INC ( Sales[DeliveryDays], 0.9 )",
  },
  {
    name: "MEDIAN",
    category: "Math & statistics",
    syntax: "MEDIAN ( <Column> )",
    summary: "The middle value. More representative than AVERAGE when there are outliers.",
    example: "Median Order = MEDIAN ( Sales[OrderAmount] )",
  },

  // ------------------------------------------------- Tables & relationships
  {
    name: "SUMMARIZE",
    category: "Tables & relationships",
    syntax: "SUMMARIZE ( <Table>, <GroupByColumn>, …, <Name>, <Expression> )",
    summary: "Groups and summarises. Arguments after the group-by columns are name/expression pairs, which is easy to confuse with columns — prefer SUMMARIZECOLUMNS in new code.",
    example: "By Category = SUMMARIZE ( Sales, Product[Category], \"Total\", SUM ( Sales[Amount] ) )",
    href: "/tutorials/summarize-vs-summarizecolumns/",
  },
  {
    name: "SUMMARIZECOLUMNS",
    category: "Tables & relationships",
    syntax: "SUMMARIZECOLUMNS ( <GroupByColumn>, …, <FilterTable>, <Name>, <Expression> )",
    summary: "Built for visuals and usually faster than SUMMARIZE. It cannot be used as a filter table inside CALCULATE.",
    example: "Summary = SUMMARIZECOLUMNS ( Product[Category], \"Total\", [Total Sales] )",
    href: "/tutorials/summarize-vs-summarizecolumns/",
  },
  {
    name: "ADDCOLUMNS",
    category: "Tables & relationships",
    syntax: "ADDCOLUMNS ( <Table>, <Name>, <Expression>, … )",
    summary: "Adds calculated columns to a table expression. Often paired with SUMMARIZE to avoid its name/expression syntax.",
    example: "With Margin = ADDCOLUMNS ( VALUES ( Product[Category] ), \"Margin\", [Margin %] )",
  },
  {
    name: "SELECTCOLUMNS",
    category: "Tables & relationships",
    syntax: "SELECTCOLUMNS ( <Table>, <Name>, <Expression>, … )",
    summary: "Keeps only the columns you need and renames them. Cheaper than ADDCOLUMNS when building a small intermediate table.",
    example: "Light = SELECTCOLUMNS ( Product, \"Id\", Product[Id], \"Name\", Product[Name] )",
  },
  {
    name: "RELATED",
    category: "Tables & relationships",
    syntax: "RELATED ( <Column> )",
    summary: "Pulls a column from the one side of a relationship. Requires row context; it fails on many-to-many relationships.",
    example: "Category = RELATED ( Product[Category] )",
  },
  {
    name: "RELATEDTABLE",
    category: "Tables & relationships",
    syntax: "RELATEDTABLE ( <Table> )",
    summary: "The rows on the many side of a relationship, as a table. Handy for aggregating inside a calculated column.",
    example: "Order Count = COUNTROWS ( RELATEDTABLE ( Sales ) )",
  },
  {
    name: "TREATAS",
    category: "Tables & relationships",
    syntax: "TREATAS ( <Table>, <Column>, … )",
    summary: "Applies the values of one column as a filter on another column, for tables with no physical relationship.",
    example: "Virtual = CALCULATE ( [Total Sales], TREATAS ( Region, 'Date'[Region] ) )",
  },
  {
    name: "CROSSFILTER",
    category: "Tables & relationships",
    syntax: "CROSSFILTER ( <ColumnName1>, <ColumnName2>, <Direction> )",
    summary: "Changes relationship direction for a single measure. Much safer than making the whole relationship bidirectional in the model.",
    example: "Both Ways = CALCULATE ( [Total Sales], CROSSFILTER ( Product[Id], Sales[ProductId], BOTH ) )",
  },
  {
    name: "USERELATIONSHIP",
    category: "Tables & relationships",
    syntax: "USERELATIONSHIP ( <ColumnName1>, <ColumnName2> )",
    summary: "Activates an inactive relationship for the duration of the calculation — the standard fix for role-playing dates.",
    example: "Shipped Sales = CALCULATE ( [Total Sales], USERELATIONSHIP ( Sales[ShipDate], 'Date'[Date] ) )",
    href: "/tutorials/role-playing-dimensions/",
  },

  // ----------------------------------------------------------- Information
  {
    name: "ISBLANK",
    category: "Information",
    syntax: "ISBLANK ( <Value> )",
    summary: "True when a value is blank. An empty string \"\" is not blank, which is why some IF checks silently fail.",
    example: "No Sales = IF ( ISBLANK ( [Total Sales] ), \"—\", FORMAT ( [Total Sales], \"#,##0\" ) )",
  },
  {
    name: "HASONEVALUE",
    category: "Information",
    syntax: "HASONEVALUE ( <Column> )",
    summary: "True when a column has exactly one value in context. Used for dynamic titles and conditional display.",
    example: "Title = IF ( HASONEVALUE ( Product[Category] ), SELECTEDVALUE ( Product[Category] ), \"All categories\" )",
  },
  {
    name: "CONTAINS",
    category: "Information",
    syntax: "CONTAINS ( <Table>, <Column>, <Value> )",
    summary: "True when a row with that value exists. Common in security predicates.",
    example: "Has Red = CONTAINS ( Product, Product[Color], \"Red\" )",
  },
  {
    name: "PATH",
    category: "Information",
    syntax: "PATH ( <Id>, <ParentId> )",
    summary: "Turns a parent/child hierarchy into a path string. Pair it with PATHITEM to read a level back.",
    example: "Node Path = PATH ( Account[Id], Account[ParentId] )",
  },
];

export const FUNCTION_COUNT = DAX_FUNCTIONS.length;
