---
title: "DAX User-Defined Functions (UDF): Reusable Logic Without Calculation Groups"
description: "DAX UDFs went GA in June 2026. Learn how the FUNCTION keyword lets you package reusable parameterized logic — tax calculations, currency conversion, margin formulas — and call it from any measure or column."
pubDate: 2026-08-03
category: "dax"
difficulty: "Intermediate"
tags: ["DAX UDF", "user-defined functions", "FUNCTION keyword", "reusable logic", "DAX"]
author: "Power BI Tutorials Team"
---

Every Power BI developer hits the same wall eventually: you write a margin calculation, it works, and then you copy-paste it into six different measures because DAX doesn't have functions. You try calculation groups, but they're overkill for a simple parameterized formula. You look at Power Query's custom functions with envy.

That wall is gone. DAX User-Defined Functions (UDFs) shipped as generally available in the June 2026 release, and they bring the `FUNCTION` keyword to DAX — letting you define reusable, parameterized logic once and call it from any measure, calculated column, visual calculation, or even another UDF.

## What DAX UDFs Actually Are

A UDF is a first-class model object. You define it once, it lives in the semantic model under the **Functions** node in Model Explorer, and you call it by name — exactly like you'd call `SUM()` or `DIVIDE()`. The difference is you wrote it yourself.

Here's the simplest possible UDF:

```dax
DEFINE
/// Adds tax to a given amount at the default 10% rate
/// @param {NUMERIC} amount - The pre-tax value
/// @returns The amount including 10% tax
FUNCTION AddTax = (amount : NUMERIC, taxRate : NUMERIC = 0.1) => amount * (1 + taxRate)

EVALUATE { AddTax(100) }  // Returns 110
EVALUATE { AddTax(100, 0.2) }  // Returns 120
```

A few things to notice:
- `DEFINE` introduces the function definition (same keyword as DAX queries)
- `///` comments are JSDoc-style annotations — they show up in IntelliSense when you call the function
- Parameters can have **type hints** (`: NUMERIC`) and **default values** (`= 0.1`)
- The `=>` arrow separates the signature from the body
- Once saved to the model, you call it like any built-in function: `AddTax(100)`

## Where You Define UDFs

Three entry points, all equivalent:

**1. DAX Query View (DQV)** — Type the `DEFINE FUNCTION ...` block, then click **Update model with changes** to save it to the model. You can also evaluate the function right there with an `EVALUATE` statement before committing.

**2. TMDL View** — For those working with Power BI projects (PBIP format), UDFs are stored in `functions.tmdl` inside the definition folder. The syntax is slightly different:

```tmdl
createOrReplace
/// Adds tax to a given amount
function AddTax = (amount : NUMERIC) => amount * 1.1
```

**3. Model Explorer** — The Functions node shows all UDFs in the model. Right-click for quick actions: Evaluate, Define and evaluate, or Script TMDL to edit in TMDL view.

UDFs require database compatibility level 1702 or higher. Power BI Desktop June 2026 and later handles this automatically for new models.

## A Real Example: Multi-State Tax Calculator

Contoso sells across all 50 states, and each state has a different sales tax rate. Before UDFs, you'd either hardcode rates in a disconnected table and use LOOKUPVALUE, or write a bloated SWITCH statement in every revenue measure. With UDFs, the logic lives in one place.

```dax
DEFINE
/// Calculates after-tax revenue based on state-specific rates
/// @param {NUMERIC} preTaxAmount - Revenue before tax
/// @param {STRING} stateCode - Two-letter US state code (e.g., "CA", "TX")
/// @returns Revenue after applying state sales tax
FUNCTION AfterTaxRevenue =
    (preTaxAmount : NUMERIC, stateCode : STRING) =>
    preTaxAmount * (1 + SWITCH(
        stateCode,
        "CA", 0.0725,
        "NY", 0.08,
        "TX", 0.0625,
        "FL", 0.06,
        "WA", 0.065,
        0.07  -- default for states not listed
    ))
```

Now you can call it from a measure:

```dax
Net Revenue = AfterTaxRevenue([Gross Sales], SELECTEDVALUE(Stores[State]))
```

Or from a calculated column:

```dax
Net Amount = CONVERT(AfterTaxRevenue('Sales'[Amount], 'Sales'[State]), CURRENCY)
```

Or even from a visual calculation (new since GA):

```dax
Tax-Adjusted Revenue = AfterTaxRevenue([Revenue], "CA")
```

When the finance team says "Florida's rate changed to 6.5%," you update one function instead of hunting through twelve measures.

## Parameter Types and Type Hints

UDF parameters can be typed, untyped, or a mix. Here's what's available:

**Scalar types (most common):**
- `NUMERIC` — accepts Int64, Decimal, Double (use this for most numbers)
- `STRING` — text values
- `BOOLEAN` — true/false
- `DATETIME` — date/time values
- `INT64` — specific integer type
- `DECIMAL` — specific decimal type
- `DOUBLE` — specific float type
- `VARIANT` — any scalar type (loosest, least safe)

**Reference types (advanced):**
- `COLUMNREF` — a reference to a column (not its value)
- `MEASUREREF` — a reference to a measure
- `TABLEREF` — a reference to a table
- `CALENDARREF` — a reference to a date table

Type hints are optional. Skip them if you want flexibility, but the trade-off is no compile-time checking. For shared team models, type hints are worth the few extra characters.

### Parameter Evaluation Mode

Each parameter can specify how it's evaluated:

```dax
-- val mode: argument is evaluated immediately (eager)
FUNCTION Example1 = (x : NUMERIC val) => x * 2

-- expr mode: argument is evaluated lazily when referenced
FUNCTION Example2 = (x : NUMERIC expr) => x * 2
```

For 95% of use cases, the default (`val`) is fine. Use `expr` when you're passing a measure reference that should be evaluated in a modified filter context within the function body.

## Nesting UDFs

UDFs can call other UDFs. This is where the real power shows up — you can build a library of small, composable functions.

```dax
DEFINE
/// Applies a discount to a given amount
FUNCTION ApplyDiscount = (amount : NUMERIC, discountPct : NUMERIC = 0.1) =>
    amount * (1 - discountPct)

/// Adds tax to a given amount
FUNCTION AddTax = (amount : NUMERIC, taxRate : NUMERIC = 0.1) =>
    amount * (1 + taxRate)

/// Full pipeline: discount first, then tax
FUNCTION NetPrice =
    (amount : NUMERIC, discountPct : NUMERIC = 0.1, taxRate : NUMERIC = 0.08) =>
    AddTax(ApplyDiscount(amount, discountPct), taxRate)

EVALUATE { NetPrice(100, 0.15, 0.08) }
-- 100 → discount 15% → 85 → tax 8% → 91.80
```

That's three functions, each testable in isolation, composed into a pricing pipeline. Try doing that cleanly with calculation groups.

## UDFs vs. Calculation Groups: When to Use Which

This question comes up on r/PowerBI at least once a week. The short answer:

| Aspect | UDFs | Calculation Groups |
|--------|------|-------------------|
| **Purpose** | Reusable parameterized logic | Apply a transformation across all measures |
| **Scope** | Called explicitly where needed | Applied automatically via slicer/filter |
| **Parameters** | Yes — multiple, typed, with defaults | No parameters |
| **Where it runs** | Anywhere DAX runs | Report-level (calculation item selection) |
| **Best for** | Tax, margin, conversion formulas | Time intelligence on/off, currency conversion toggle |

A good rule of thumb: if your logic takes parameters, use a UDF. If your logic is "apply the same transformation to every measure on the page," use a calculation group. They're complementary, not competing.

## Inspecting UDFs with DMVs

You can query your model's UDFs programmatically using Dynamic Management Views:

```dax
-- Full metadata for all UDFs (requires write permission)
EVALUATE INFO.USERDEFINEDFUNCTIONS()

-- Lightweight list of UDF names and basic info
EVALUATE INFO.FUNCTIONS("ORIGIN", "2")
```

This is handy for governance — you can export all UDF definitions to a table and review them for compliance, or check which models have a specific function before pushing updates.

## Common Mistakes

**Mistake 1: Using UDFs where a measure would be simpler.**
If your "function" takes no parameters and always references the same columns, it's a measure. UDFs shine when you need parameterization. `TotalSales = SUM(Sales[Amount])` doesn't need to be a function.

**Mistake 2: Forgetting to save to the model.**
In DAX Query View, typing a `DEFINE FUNCTION` block and running `EVALUATE` tests the function — but it doesn't save it. You need to click **Update model with changes** (or **Update model: Add new function**) to persist it. If you close Desktop without saving, the function is gone.

**Mistake 3: Naming conflicts with built-in functions.**
You can't name a UDF `SUM` or `CALCULATE` — the system blocks reserved words. But you *can* accidentally shadow a function name in a way that confuses other developers. Prefix your UDFs if there's any risk: `fn_AddTax` or `Contoso.NetPrice`.

**Mistake 4: Over-typing parameters.**
If you type everything as `INT64` and then pass a decimal value, the function errors at runtime. Use `NUMERIC` for general numeric parameters — it's the broadest numeric type and covers integers, decimals, and floats.

**Mistake 5: Ignoring JSDoc comments.**
The `///` comments above your function aren't just decoration — they populate IntelliSense tooltips for everyone who calls your function. If your team is going to use a UDF, document it. Include `@param` tags with descriptions so callers know what to pass.

## FAQ

**Can I share UDFs across multiple Power BI reports?**
UDFs live in the semantic model. If multiple reports connect to the same shared semantic model (Power BI Service), they all have access to the same UDFs. For separate PBIX files, you'd need to export/import the TMDL definition.

**Do UDFs work in DirectQuery mode?**
Yes, with the same compatibility level requirement (1702+). The function is evaluated in the context of the query, so DQ-specific limitations (like not being able to use certain DAX functions) still apply to the function body.

**Can I version-control UDFs?**
Absolutely — that's one of the biggest advantages over calculation groups. If you're using Power BI Projects (PBIP), UDFs are stored as TMDL in `functions.tmdl`, which is plain text and diff-friendly. You can track changes, review pull requests, and roll back if needed.

**What's the performance difference between a UDF and inline DAX?**
In most cases, negligible. The DAX engine inlines UDF calls during query optimization — the generated query plan is similar to what you'd get from writing the logic inline. For deeply nested UDFs (4+ levels), you may see slightly more complex query plans, but it rarely matters in practice.

**Can I use [variables](/tutorials/dax-variables-guide/) inside a UDF?**
Yes. The function body supports `VAR`/`RETURN` just like a measure. This is useful for intermediate calculations:

```dax
FUNCTION GrossMargin = (revenue : NUMERIC, cost : NUMERIC) =>
    VAR gross = revenue - cost
    VAR pct = DIVIDE(gross, revenue)
    RETURN pct
```

## What's Next

- Brush up on [CALCULATE](/tutorials/dax-calculate-function/) — UDFs don't replace filter context modification, they complement it
- Learn [DAX variables](/tutorials/dax-variables-guide/) — they work inside UDF bodies and make complex functions readable
- Read about [field parameters](/tutorials/power-bi-field-parameters/) for another approach to dynamic measure logic (complementary, not competing with UDFs)
- Check the [DAX troubleshooting guide](/tutorials/dax-troubleshooting-guide/) when your UDF returns unexpected results — the same debugging principles apply
