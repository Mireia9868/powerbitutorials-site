---
title: "Power Query Conditional Columns: Build If-Then-Else Logic Without Code"
description: "Conditional columns let you create new columns based on if-then-else logic using a visual interface — no M code required. This guide covers the UI, nested conditions, the M code underneath, and the patterns for categorizing, flagging, and bucketing data."
pubDate: 2026-07-23
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "conditional-columns", "if-then-else", "m-language", "transformations"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

Conditional columns let you create new columns based on if-then-else logic using a visual interface — no M code required. This guide covers the UI, nested conditions, the M code underneath, and the patterns for categorizing, flagging, and bucketing data.

Excel users know `IF()` formulas. Power Query has the same concept — conditional logic that creates a new column value based on rules — but with a visual builder instead of nested function calls. This guide covers the Conditional Column dialog, when to use it vs. Custom Column, and the practical patterns every analyst needs.

## Creating a conditional column

### Step 1: Open the dialog

1. In Power Query Editor, select the table you want to modify
2. Go to the **Add Column** tab on the ribbon
3. Click **Conditional Column**

### Step 2: Configure the condition

The Conditional Column dialog presents a visual rule builder:

- **New column name:** what to call the result
- **If:** select a column, an operator, and a value
- **Then:** the output value when the condition is true
- **Else:** the output value when the condition is false
- **Add clause:** adds another if-then-else rule (evaluated in order)

For example, to categorize order amounts:

| Setting | Value |
|---------|-------|
| New column name | Order Size |
| If | `[OrderAmount]` `is greater than` `10000` |
| Then | `"Large"` |
| Else | `"Small"` |

Click OK, and Power Query creates the column. No code written.

### Step 3: Review the result

The new column appears at the end of the table. Power Query evaluates each row against the condition and assigns the output value. The column type is automatically set to Text (or Number, depending on the output values).

**Tip:** Always verify the data type after creating a conditional column. Power Query sometimes defaults to `Any` type, which causes issues downstream. Click the type icon next to the column name and set it explicitly.

## Adding multiple conditions

Click "Add clause" in the Conditional Column dialog to chain multiple if-then-else rules. Conditions are evaluated top to bottom — the first match wins:

| If | Then |
|----|------|
| `[OrderAmount]` `is greater than` `10000` | `"Large"` |
| `[OrderAmount]` `is greater than` `5000` | `"Medium"` |
| Else | `"Small"` |

This categorizes every order as Large, Medium, or Small. An order of 7,500 matches the second rule (Medium) because the first rule (greater than 10,000) fails. An order of 3,000 matches neither rule and falls through to Else (Small).

**Key behavior:** conditions are evaluated in order. Put the most specific or highest-threshold condition first. If you reversed the order and checked `> 5000` first, every order above 5,000 would be categorized as Medium — including orders above 10,000.

## Available operators

The Conditional Column dialog supports these operators depending on the column's data type:

**Text columns:**
- equals / does not equal
- begins with / does not begin with
- ends with / does not end with
- contains / does not contain

**Number columns:**
- equals / does not equal
- is greater than / is greater than or equal to
- is less than / is less than or equal to
- is between

**Date columns:**
- equals / does not equal
- is before / is on or before
- is after / is on or after
- is between

**Note:** The "is between" operator is only available in the Custom Column dialog, not in the Conditional Column UI. For between logic, use two conditions (greater than or equal to X, and less than or equal to Y) or write a Custom Column.

## The M code underneath

Every conditional column generates M code behind the scenes. Click **View → Advanced Editor** or the `fx` formula bar to see it:

```powerquery
// Simple conditional column
= if [OrderAmount] > 10000 then "Large" else "Small"

// Multiple conditions
= if [OrderAmount] > 10000 then "Large"
  else if [OrderAmount] > 5000 then "Medium"
  else "Small"
```

**M syntax rules:**
- `if`, `then`, `else` are lowercase keywords (M is case-sensitive)
- Conditions use standard comparison operators: `>`, `<`, `=`, `>=`, `<=`, `<>`
- Text values use double quotes: `"Large"`
- `and` / `or` combine conditions: `if [Amount] > 100 and [Status] = "Paid" then ...`

Understanding the M code helps when you need logic that the visual builder can't express.

## When to use Conditional Column vs. Custom Column

| Feature | Conditional Column | Custom Column |
|---------|-------------------|--------------|
| Simple if-then-else | ✓ Visual builder | ✓ Write M code |
| Multiple conditions | ✓ Add clause | ✓ else if chains |
| AND / OR logic | ✗ Not supported | ✓ Use `and`, `or` |
| Reference other columns in output | ✗ Fixed values only | ✓ Any expression |
| Nested functions | ✗ | ✓ Any M function |
| Between logic | ✗ Use two conditions | ✓ `>= and <=` |

**Rule of thumb:** start with Conditional Column. If the dialog can't express what you need (AND/OR logic, dynamic output values, function calls), switch to Custom Column and write the M code.

## Pattern 1: Categorize numeric values

The most common use case — bucket continuous values into discrete categories:

```powerquery
// Conditional Column dialog:
// If [Revenue] > 50000 then "Enterprise"
// Else if [Revenue] > 10000 then "Mid-Market"
// Else if [Revenue] > 1000 then "SMB"
// Else "Startup"
```

Or in M code:

```powerquery
= if [Revenue] > 50000 then "Enterprise"
  else if [Revenue] > 10000 then "Mid-Market"
  else if [Revenue] > 1000 then "SMB"
  else "Startup"
```

## Pattern 2: Flag rows based on text matching

Flag orders that need attention based on their status:

```powerquery
// If [Status] equals "Cancelled" then "Review"
// Else if [Status] equals "Refunded" then "Review"
// Else if [Status] equals "Pending" and [DaysOld] > 7 then "Overdue"
// Else "OK"
```

**Note:** the third condition uses AND logic, which the Conditional Column dialog doesn't support. For this pattern, use Custom Column:

```powerquery
= if [Status] = "Cancelled" then "Review"
  else if [Status] = "Refunded" then "Review"
  else if [Status] = "Pending" and [DaysOld] > 7 then "Overdue"
  else "OK"
```

## Pattern 3: Date-based categorization

Categorize records by age:

```powerquery
// Custom Column M code:
= if [OrderDate] >= Date.From(Date.AddDays(DateTime.LocalNow(), -30)) then "Recent"
  else if [OrderDate] >= Date.From(Date.AddDays(DateTime.LocalNow(), -90)) then "This Quarter"
  else if [OrderDate] >= Date.From(Date.AddDays(DateTime.LocalNow(), -365)) then "This Year"
  else "Historical"
```

This uses `DateTime.LocalNow()` for a dynamic reference to today's date, so the categorization updates automatically every time the query refreshes.

## Pattern 4: Fallback values for nulls

Replace null values with a default:

```powerquery
// If [Discount] equals null then 0
// Else [Discount]
```

In M code:

```powerquery
= if [Discount] = null then 0 else [Discount]
```

**Alternative:** use the `??` coalesce operator, which is a shorthand for this pattern:

```powerquery
= [Discount] ?? 0
```

`??` returns the left value if it's not null, otherwise the right value. It's cleaner than an if-then-else for simple null replacement.

## Common mistakes

### 1. Case sensitivity in text comparisons

M is case-sensitive. `"Paid"` and `"paid"` are different values:

```powerquery
// Only matches exactly "Paid" — "PAID" and "paid" won't match
= if [Status] = "Paid" then "Complete" else "Pending"

// Case-insensitive comparison
= if Text.Lower([Status]) = "paid" then "Complete" else "Pending"
```

**Fix:** use `Text.Lower()` or `Text.Upper()` to normalize before comparing, or use `Comparer.OrdinalIgnoreCase` in `Text.Equals()`.

### 2. Null handling

In M, `null` comparisons behave differently than in other languages:

```powerquery
// This does NOT work — null doesn't equal null in comparisons
= if [Value] = null then "Empty" else "Has Value"

// Correct — use "is null" check in Conditional Column, or:
= if [Value] = null then "Empty" else "Has Value"

// Actually in M, = null DOES work for null comparison
// But the Conditional Column UI uses "equals" which may behave differently
```

**Important:** in the Conditional Column dialog, select the operator "equals" and type `null` (without quotes) to compare against null. In M code, `= null` works correctly.

### 3. Forgetting the Else clause

Every conditional needs an Else. If you omit it in the M code, you get a syntax error. In the Conditional Column dialog, the Else is required — it's the fallback for rows that don't match any condition.

```powerquery
// WRONG — missing else clause, syntax error
= if [Value] > 100 then "High"

// Correct
= if [Value] > 100 then "High" else "Low"
```

### 4. Wrong data type for output values

If you mix text and number outputs in the same column, Power Query creates an `Any` type column that can cause errors downstream:

```powerquery
// Mixed types — creates Any column, causes issues
= if [Score] > 90 then "A" else 0

// Consistent types — creates Text column
= if [Score] > 90 then "A" else "F"
```

**Fix:** keep output value types consistent within a conditional column. If you need mixed types, create separate columns or use a text representation for everything.

## FAQ

**Can I reference another column in the "Then" value?**
Not in the Conditional Column dialog — the Then field only accepts literal values. To reference another column, use Custom Column: `= if [Status] = "Active" then [Revenue] else 0`.

**How many conditions can I add?**
There's no hard limit, but each condition is evaluated sequentially. For more than 5-6 conditions, consider using a lookup table and `Table.Lookup` or a Merge operation instead — it's more maintainable.

**Does the Conditional Column update when source data changes?**
Yes. The condition is part of the query steps and re-evaluates on every refresh. If you change the thresholds, edit the step in Applied Steps.

**Can I use conditional columns with calculated tables in DAX?**
No. Conditional columns are created in Power Query (M language) before the data reaches the DAX engine. If you need conditional logic after the data is loaded, use a DAX calculated column with the `IF()` or `SWITCH()` function instead.

## What's next

- Learn [Power Query M language basics](/tutorials/power-query-m-language-basics) to go beyond the visual builder
- Read the [10 common Power Query transformations](/tutorials/power-query-common-transformations) guide for more cleanup patterns
- See [merge vs. append queries](/tutorials/merge-vs-append-queries) to combine data from multiple sources
- Check the [getting started with Power Query](/tutorials/power-query-getting-started) guide if you're new to the editor
