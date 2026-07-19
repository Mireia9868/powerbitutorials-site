---
title: "10 Common Power Query Transformations Every Analyst Should Know"
description: "Power Query has hundreds of functions, but a small set covers the vast majority of real-world cleanup tasks. This guide walks through ten transformations that handle messy exports, inconsistent naming, and malformed data — the daily reality of every data analyst."
pubDate: 2026-07-19
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "transformations", "cleanup", "data-prep", "etl"]
author: "Power BI Tutorials Team"
featured: false
---

Real-world data is messy. Column names have trailing spaces, dates arrive as text, numbers hide in formatted strings, and someone always merges first and last name into a single field. This guide covers the ten Power Query transformations that handle 90% of cleanup work, with the M code behind each.

## 1. Promote headers

CSVs and pasted data often arrive with headers as the first row. **Home → Use First Row as Headers** (or `Table.PromoteHeaders` in M) fixes this.

```m
Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
```

`PromoteAllScalars` ensures the header values are converted to their proper types (text by default).

## 2. Set data types

Every column should have an explicit type. Without it, Power BI treats everything as text, which breaks sorting, aggregation, and relationships.

```m
Typed = Table.TransformColumnTypes(Source, {
    {"OrderDate", type date},
    {"Revenue", Currency.Type},
    {"Quantity", Int64.Type},
    {"CustomerName", type text}
})
```

Use **Home → Data Type** dropdown for a no-code approach. The M is generated automatically.

**Type reference:**
- `type date` — calendar dates
- `type datetime` — timestamps
- `Currency.Type` — monetary values (stored as fixed-decimal)
- `Int64.Type` — whole numbers
- `type number` — decimals
- `type text` — strings
- `type logical` — true/false

## 3. Remove unwanted columns

Large exports often contain columns you don't need. Remove them early to reduce memory.

```m
Kept = Table.SelectColumns(Source, {"OrderDate", "Revenue", "CustomerID"})
// Or remove specific columns:
Removed = Table.RemoveColumns(Source, {"InternalCode", "AuditTrail"})
```

Selecting the columns you want is safer than removing the ones you don't — if the source adds new columns later, `SelectColumns` ignores them; `RemoveColumns` errors.

## 4. Filter rows

Remove irrelevant or invalid rows early to speed up processing.

```m
Filtered = Table.SelectRows(Source, each [Revenue] > 0 and [Revenue] <> null)
```

For date filtering:

```m
RecentOnly = Table.SelectRows(Source, each [OrderDate] >= #date(2024, 1, 1))
```

`#date(year, month, day)` creates a date literal in M.

## 5. Split columns

A single column with combined data — "John Smith", "New York, NY", "SKU-12345-Blue" — often needs splitting.

**By delimiter:**

```m
Split = Table.SplitColumn(Source, "FullName", Splitter.SplitTextByDelimiter(" ", QuoteStyle.None), {"FirstName", "LastName"})
```

**By position:**

```m
Split = Table.SplitColumn(Source, "ProductCode", Splitter.SplitTextByPositions({0, 5, 8}), {"Prefix", "ID", "Suffix"})
```

The UI version (**Transform → Split Column**) handles most cases and generates the M for you.

## 6. Merge columns

The reverse — combine first and last name, or build a full address.

```m
Merged = Table.CombineColumns(Source, {"FirstName", "LastName"}, Combiner.CombineTextByDelimiter(" ", QuoteStyle.None), "FullName")
```

For custom logic (like adding a comma between city and state):

```m
Added = Table.AddColumn(Source, "Location", each [City] & ", " & [State], type text)
```

`&` is the string concatenation operator in M.

## 7. Replace values

Inconsistent labels — "USA", "U.S.A.", "United States" — need normalization.

```m
Replaced = Table.ReplaceValue(Source, "U.S.A.", "USA", Replacer.ReplaceText, {"Country"})
```

For multiple replacements, chain them or use a lookup table with `Table.ReplaceMatchingRows`.

## 8. Pivot and unpivot

Data arrives in two shapes: **wide** (one row per entity, columns for each metric) and **long** (one row per observation, a column for the metric name). Power BI prefers long format.

**Unpivot (wide → long):**

```
Before:                      After:
Product | Jan | Feb          Product | Month | Revenue
A       | 100 | 150          A       | Jan   | 100
B       | 200 | 250          A       | Feb   | 150
                              B       | Jan   | 200
                              B       | Feb   | 250
```

```m
Unpivoted = Table.UnpivotOtherColumns(Source, {"Product"}, "Month", "Revenue")
```

`UnpivotOtherColumns` keeps the specified columns and unpivots everything else — robust against new columns being added.

**Pivot (long → wide):** Rarely needed in Power BI, but available via `Table.Pivot`.

## 9. Group and aggregate

Summarize data before loading — useful for pre-aggregated reporting tables.

```m
Grouped = Table.Group(Source, {"Category"}, {
    {"TotalRevenue", each List.Sum([Revenue]), Currency.Type},
    {"OrderCount", each Table.RowCount(_), Int64.Type},
    {"AvgOrderValue", each List.Average([Revenue]), Currency.Type}
})
```

The `_` in the aggregation functions refers to the subgroup table for each category.

## 10. Custom columns with conditional logic

Add calculated columns with `if ... then ... else` logic — M's equivalent of `IF` in Excel.

```m
Added = Table.AddColumn(Source, "Tier", each
    if [Revenue] > 10000 then "Enterprise"
    else if [Revenue] > 5000 then "Mid-Market"
    else "SMB", type text)
```

For multi-condition logic, `if` chains are readable but verbose. For lookup-based logic, consider merging with a mapping table instead.

## Bonus: Handling nulls

Null values break aggregations and display oddly. Handle them explicitly:

```m
// Replace null with 0
Filled = Table.ReplaceValue(Source, null, 0, Replacer.ReplaceValue, {"Revenue"})

// Filter out nulls
Filtered = Table.SelectRows(Source, each [Revenue] <> null)

// Coalesce — use a fallback value
Coalesced = Table.AddColumn(Source, "SafeRevenue", each [Revenue] ?? 0, Currency.Type)
```

`??` is the coalesce operator — it returns the left value if not null, otherwise the right.

## Putting it together

A typical cleanup query chains these transformations:

```m
let
    Source = Csv.Document(File.Contents("C:\Data\sales.csv"), [Delimiter=",", Encoding=65001]),
    Promoted = Table.PromoteHeaders(Source),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"OrderDate", type date},
        {"Revenue", Currency.Type},
        {"CustomerName", type text}
    }),
    Filtered = Table.SelectRows(Typed, each [Revenue] > 0),
    Split = Table.SplitColumn(Filtered, "CustomerName", Splitter.SplitTextByDelimiter(" "), {"FirstName", "LastName"}),
    Added = Table.AddColumn(Split, "Tier", each
        if [Revenue] > 10000 then "Enterprise" else "SMB", type text),
    Result = Table.SelectColumns(Added, {"OrderDate", "Revenue", "FirstName", "LastName", "Tier"})
in
    Result
```

## Summary

These ten transformations — promote headers, set types, remove columns, filter, split, merge, replace, unpivot, group, and custom columns — cover the daily reality of data cleanup. Master them and most ETL tasks become a sequence of these steps. The Power Query UI generates the M for you; understanding the M lets you debug, optimize, and build transformations the UI doesn't offer.
