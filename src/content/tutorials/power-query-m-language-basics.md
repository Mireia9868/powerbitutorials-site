---
title: "Power Query M Language Basics: Functions, Tables, and Records"
description: "M is the functional language behind Power Query. It looks nothing like DAX or Excel formulas, but once you understand its three core data structures and how functions compose, the editor becomes far less intimidating. This guide covers the fundamentals with practical examples."
pubDate: 2026-07-16
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "m-language", "functions", "tables", "records", "lists"]
author: "Power BI Tutorials Team"
featured: false
---

Every transformation you click through in the Power Query Editor generates M code behind the scenes. The formula bar shows one line at a time, but the Advanced Editor reveals the full picture: a series of `let` expressions that transform data step by step. This guide covers the language fundamentals you need to read, write, and debug M.

## The three data structures

Everything in M is built from three structures:

### 1. Table

The most familiar — rows and columns, just like Excel.

```m
Source = #table(
    type table [Name = text, Age = number],
    {
        {"Alice", 30},
        {"Bob", 25}
    }
)
```

### 2. Record

A record is a set of named fields — like a single row or a JSON object.

```m
Person = [Name = "Alice", Age = 30, City = "Berlin"]
```

Access a field with bracket notation: `Person[Name]` returns `"Alice"`.

### 3. List

A list is a one-dimensional sequence of values.

```m
Numbers = {1, 2, 3, 4, 5}
```

Access by index (zero-based): `Numbers{0}` returns `1`.

**The relationship:** A table is a list of records. A record is a list of fields. Understanding this hierarchy makes many M functions intuitive — `Table.SelectRows` filters a list of records, `Record.AddField` adds a field to a record, and so on.

## The let expression

M code is structured as a `let` expression — a sequence of variable bindings followed by an `in` clause that returns the final result.

```m
let
    Source = Sql.Database("Server", "DB"),
    SalesTable = Source{[Schema="dbo", Item="Sales"]}[Data],
    FilteredRows = Table.SelectRows(SalesTable, each [Revenue] > 1000),
    SortedRows = Table.Sort(FilteredRows, {{"OrderDate", Order.Descending}}),
    Result = Table.SelectColumns(SortedRows, {"OrderDate", "Revenue"})
in
    Result
```

Each step references the previous one. The variable names are arbitrary — you can call them `Step1`, `Step2`, or give them descriptive names. The `in` clause determines what the query returns (usually the last step, but not required).

## Functions

M is a functional language. Functions are first-class values — you can pass them as arguments, store them in variables, and compose them.

The syntax: `parameter => expression`.

```m
// A function that squares a number
Square = (x) => x * x
Square(5)  // returns 25
```

Functions can take multiple parameters:

```m
Add = (a, b) => a + b
Add(3, 4)  // returns 7
```

And they can be curried — partially applied:

```m
AddFive = (a) => (b) => a + b
AddFive(3)(4)  // returns 7
```

Most built-in M functions accept a function as an argument. The `each` keyword is shorthand for `(x) => x` — it creates a function that takes one parameter and accesses fields via underscore.

```m
// These two are equivalent
Table.SelectRows(Sales, each [Revenue] > 1000)
Table.SelectRows(Sales, (row) => row[Revenue] > 1000)
```

`each` is the idiomatic way to write row-level conditions in Power Query.

## Common table functions

| Function | What it does |
|----------|-------------|
| `Table.SelectRows(table, condition)` | Filters rows |
| `Table.SelectColumns(table, columns)` | Keeps only specified columns |
| `Table.AddColumn(table, name, function)` | Adds a calculated column |
| `Table.Sort(table, sortCriteria)` | Sorts by one or more columns |
| `Table.GroupBy(table, keys, aggregations)` | Groups and aggregates |
| `Table.Join(table1, table2, keys, kind)` | Merges two tables |
| `Table.RenameColumns(table, renames)` | Renames columns |
| `Table.TransformColumns(table, transforms)` | Applies a function to columns |

## Practical example: cleaning a sales export

Say you have a messy CSV export. Here's a typical cleanup query:

```m
let
    Source = Csv.Document(File.Contents("C:\Data\sales.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TypedColumns = Table.TransformColumnTypes(PromotedHeaders, {
        {"OrderDate", type date},
        {"Revenue", Currency.Type},
        {"Quantity", Int64.Type}
    }),
    FilteredValid = Table.SelectRows(TypedColumns, each [Revenue] <> null and [Revenue] > 0),
    AddedMonth = Table.AddColumn(FilteredValid, "Month", each Date.Month([OrderDate]), Int64.Type),
    Result = Table.SelectColumns(AddedMonth, {"OrderDate", "Month", "Revenue", "Quantity"})
in
    Result
```

Each step is a transformation. The `each` keyword accesses the current row's fields. `Date.Month` is a built-in date function — there are dozens for date manipulation.

## Handling errors

M is strict about types. If a transformation fails (e.g., converting "abc" to a number), the cell shows `Error` in the result table. You can handle this with `try ... otherwise`:

```m
SafeConvert = Table.AddColumn(Source, "ParsedQty", each try Number.From([Qty]) otherwise null, type nullable number)
```

`try` returns a record with `HasError` and `Value` fields; `otherwise` provides the fallback.

## Common mistakes

**Mistake 1: Confusing M with DAX.** M transforms data *before* it loads into the model. DAX calculates *after* data is loaded. They serve different purposes — use M for ETL, DAX for analysis.

**Mistake 2: Not setting data types.** Every column should have an explicit type. Without types, Power BI treats everything as text, which breaks sorting, filtering, and relationships.

**Mistake 3: Over-transforming in M.** Some calculations are better done in DAX. If a value depends on user-selected filters (like "revenue for the selected period"), it belongs in DAX, not M — M runs at refresh time and can't respond to slicer selections.

## Summary

M is built on three structures (tables, records, lists) and one pattern (`let ... in`). Functions are the core abstraction, and `each` is the standard way to write row-level logic. Master these fundamentals and the Advanced Editor stops being intimidating — it becomes the most powerful part of Power Query.
