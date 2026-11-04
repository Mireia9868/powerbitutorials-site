---
title: "Fix: A Circular Dependency Was Detected in Power BI"
description: "Why Power BI refuses to compute a column that refers back to itself, the three shapes this error takes, and the fix for each — with working DAX."
pubDate: 2026-11-04
category: dax
tags: ["dax", "troubleshooting", "calculated-columns", "relationships"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

`A circular dependency was detected` is one of the few DAX errors that names the problem accurately. A column, a table or a relationship is defined in terms of itself, and the engine cannot work out what to calculate first.

It sounds exotic. In practice it comes from three specific shapes, and each has a different fix.

## Why it happens at all

DAX is not a spreadsheet. In Excel a circular reference is a live loop, recalculated until it settles or until Excel gives up. In Power BI, calculated columns and calculated tables are **materialised** — computed once, stored in the model, and then compressed by VertiPaq.

That has a consequence: when Power BI evaluates a calculated column, every column it references must already have a value. If two columns each need the other, there is no valid starting point, so the engine stops.

Measures are different. A measure is evaluated at query time, so two measures can reference each other in ways that would be impossible for columns — as long as the reference chain terminates.

## Shape 1: A column that references itself

The simplest case, and the most obvious once you look:

```dax
-- A calculated column in the Sales table
Margin % =
Sales[Margin] / Sales[Revenue]
```

If `Margin` is itself a calculated column that uses `Margin %`, the two are mutually dependent. Power BI reports the error on whichever one it tried to compute first, which is why the message often points at the wrong column.

**The fix** is to break the chain by inlining the definition. If `Margin` was `Sales[Revenue] - Sales[Cost]`, then:

```dax
Margin % =
DIVIDE ( Sales[Revenue] - Sales[Cost], Sales[Revenue] )
```

Both source columns are physical or already materialised, so there is no loop.

**How to find it fast:** open the model view, click the column the error names, and read its formula. Follow every reference. If any of them points back to the column you started with, you have found the loop. On a large model, the Dependency view in DAX Studio does this visually.

## Shape 2: Two calculated columns that need each other

More common, and harder to see because the formulas are usually in different tables:

```dax
-- Orders table
First Order Date = MINX ( RELATEDTABLE ( Orders ), Orders[OrderDate] )

-- Customers table
Customer Since = MIN ( Customers[First Order Date] )
```

If `First Order Date` is calculated on the Orders table but reads a column that only exists on Customers, and `Customer Since` reads back into Orders, the engine has a two-way dependency across tables.

**The fix**: pick one direction and stop.

```dax
-- Keep this on the Customers table, remove the column from Orders
Customer Since =
MINX ( RELATEDTABLE ( Orders ), Orders[OrderDate] )
```

`RELATEDTABLE` reads the orders that belong to the current customer row, so the
calculation flows one way only. Writing `MIN ( Orders[OrderDate] )` also works
here because the relationship filters the Orders table from the row context —
but it relies on that implicit behaviour, and it breaks the moment someone adds
a second relationship to Orders.

Now the calculation flows one way — from the fact table up to the dimension — and there is no loop. This is also the correct place for it: a customer's first order date is a property of the customer, not of the order.

**Rule of thumb:** a calculated column should read from tables on the *one* side of a relationship, not write across it and back.

## Shape 3: A relationship cycle

The third shape has nothing to do with a single formula. Three tables related in a loop — A→B, B→C, C→A — put the model itself in a state Power BI cannot resolve, especially when more than one relationship is bidirectional.

The symptom is usually not the circular dependency error but filters that behave strangely, or a refresh that hangs. When the error does appear, it points at a table rather than a column.

**The fix**: remove one edge of the triangle.

```dax
-- Instead of activating the third relationship, deactivate it
-- and bring it in explicitly where you need it
Sales by Ship Date =
CALCULATE ( [Total Sales], USERELATIONSHIP ( Sales[ShipDate], 'Date'[Date] ) )
```

That is the standard pattern for role-playing dimensions: one active relationship to the date table, the others inactive and invoked with `USERELATIONSHIP`. Microsoft's
[relationship guidance](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand)
covers the cardinality rules that make this work.

If you genuinely need a triangular flow, the honest answer is usually that two of the tables belong in one, or that the third relationship should be single-direction rather than bidirectional. Bidirectional filtering is the single most common cause of a model that "works" but returns nonsense.

## What does not cause this error

Worth saying, because these get blamed constantly:

- **Two measures referencing each other.** Measures are query-time, and Power BI handles mutual references between them as long as there is no infinite recursion on the same row context. If you do see an error here, it is a real recursion, not a materialisation cycle.
- **A calculated column referencing a measure.** This is legal. The measure is evaluated in the row context of the column, which is exactly what context transition does. It is often slow, but it is not circular.
- **A relationship filter flowing both ways between two tables.** Two tables with a single bidirectional relationship is fine. It becomes a problem only when it closes a loop through a third table.

## Debugging order that works

When the error appears and the named column looks innocent:

1. **Open the named column's formula** and follow every reference by hand. Most loops are two hops long.
2. **Switch to Dependency view in DAX Studio** if the model is large. It draws the graph, and the cycle is visible immediately.
3. **Check for calculated columns that reference RELATED or RELATEDTABLE** across a relationship that is also used in the other direction. That is shape 2.
4. **List the bidirectional relationships.** In Model view, filter the relationship list. If two or more form a triangle, that is shape 3.
5. **Comment out half the formula** and re-validate. Crude, but faster than reasoning when you have four levels of nesting.

One practical note: Power BI caches the error until you change something. After editing a formula, click away from the field before concluding it is still broken — and if the error persists on a column you just simplified, the loop is in a *different* column that references it.

## FAQ

### Q: Can I just replace the calculated column with a measure?

Often yes, and it is usually the better design. Measures evaluate at query time, which removes the materialisation ordering problem entirely. The trade-off is that measures cannot be used as slicer fields or on rows without an aggregation, so it only works if the column was feeding a visual value rather than a filter.

### Q: Why does the error point at a column that looks correct?

Because Power BI reports the error on the item it was evaluating when the cycle was detected, not necessarily the one that closes the loop. Treat the named column as a starting point for the search, not as the culprit.

### Q: Does this error relate to the "A circular dependency was detected" message in Power Query?

No, that is a different engine. Power Query raises its own circular reference error when a query references another query that depends on it. Same wording, different fix — check the query steps, not the DAX.

### Q: Will this break again after a refresh?

The definition is static, so a fixed model stays fixed. But if the error returns after adding a new calculated column, it usually means the new column references a chain that already had a latent loop — something that only became a cycle when the new edge closed it.

## Related Reading

- [DAX Troubleshooting Guide: Fifteen Errors and Their Fixes](/tutorials/dax-troubleshooting-guide/)
- [Filter Context and Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [One-to-Many vs Many-to-Many Relationships](/tutorials/relationships-one-to-many-many-to-many/)
- [Bidirectional Filtering: When to Use It](/tutorials/bidirectional-filtering-guide/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [DAX Variables: Cleaner Measures](/tutorials/dax-variables-guide/)
- [Role-Playing Dimensions](/tutorials/role-playing-dimensions/)
