---
title: "Role-Playing Dimensions in Power BI: One Date Table, Multiple Relationships"
description: "One date table, three roles: order, ship, due. The three ways to model role-playing dimensions without breaking relationships."
pubDate: 2026-09-23
category: "data-modeling"
difficulty: "Advanced"
tags: ["power bi", "role playing dimension", "date table", "multiple relationships", "star schema"]
author: Mireia
featured: false
draft: false
---

A `Date` table is the most common example of a **role-playing dimension**: the same calendar plays different roles depending on which date you filter — Order Date, Ship Date, Due Date. Power BI allows only one active relationship between two tables, so you cannot simply draw three lines from `Date` to `Fact`. This guide covers the three valid ways to handle it.

## Why it is a problem

A fact table often has several date columns:

| OrderID | OrderDate | ShipDate | DueDate | Amount |
|---|---|---|---|---|

You want one `Date` table, but only **one** relationship can be active. The other two would be inactive, and slicers on `Date` would only filter by the active one.

<!-- TODO: add screenshot: Figure 1: role playing dimensions illustration -->

## Option 1: USERELATIONSHIP (no extra tables)

Keep one `Date` table, mark the other two relationships **inactive**, and activate them in measures with `USERELATIONSHIP`:

```dax
Sales by Ship Date =
CALCULATE (
    [Total Amount],
    USERELATIONSHIP ( Fact[ShipDate], Date[Date] )
)
```

Pros: one date table, one set of slicers. Cons: you must write a measure per role, and time intelligence on the inactive role needs the same wrapper.

## Option 2: Separate role tables (alias Date tables)

Create `OrderDate`, `ShipDate`, `DueDate` as separate tables, each a copy of `Date` with its own relationship.

```dax
ShipDate = 'Date'   // calculated table, or reference in Power Query
```

Pros: slicers and visuals work natively per role, no `USERELATIONSHIP` in every measure. Cons: more tables, more memory, and users must pick the right slicer.

## Option 3: TREATAS (dynamic role without a physical relationship)

Pass a filter from one role's date to another using `TREATAS`:

```dax
Sales by Due Date =
CALCULATE (
    [Total Amount],
    TREATAS ( VALUES ( Fact[DueDate] ), Date[Date] )
)
```

Useful when the role table is not physically related, or you want a measure to respect a different date context.

## Which one to pick

| Need | Best option |
|---|---|
| Few roles, mostly standard reports | USERELATIONSHIP (Option 1) |
| Many roles, business users self-serve | Separate alias tables (Option 2) |
| Cross-filter between roles without relationships | TREATAS (Option 3) |

For a clean star schema, prefer Option 1 or 2 and avoid putting multiple date roles in the same slicer. See [power-bi-star-schema](/tutorials/data-modeling-star-schema/) for the surrounding model design.

## FAQ

**Q: Can I have two active relationships to the same table?**
A: No. Power BI allows one active path; the rest are inactive and reached via `USERELATIONSHIP` or `TREATAS`.

**Q: Does a role-playing dimension cause ambiguity errors?**
A: Only if you also create a bidirectional filter that creates multiple paths. Keep role relationships single-direction.

**Q: Should the Date table be marked as a date table?**
A: Yes — right-click it → Mark as Date Table. This enables proper time intelligence on the active role.

For the official documentation behind this topic, see [Microsoft Relationships in Power BI models](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand).

## Related Reading

- [Relationships: One-to-Many and Many-to-Many](/tutorials/relationships-one-to-many-many-to-many/)
- [Power BI Star Schema](/tutorials/data-modeling-star-schema/)
- [Data Modeling Star Schema](/tutorials/data-modeling-star-schema/)
- [Bidirectional Filtering Guide](/tutorials/bidirectional-filtering-guide/)
- [DAX Time Intelligence YTD/QTD/MTD](/tutorials/dax-time-intelligence-ytd-qtd-mtd/)
- [Time Intelligence Overview](/tutorials/time-intelligence/)

- [Power BI Dataflows Explained (vs Datasets)](/tutorials/power-bi-dataflows/)
- [Power BI Data Model Best Practices](/tutorials/power-bi-data-model-best-practices/)
- [Snowflake Schema vs Star Schema in Power BI](/tutorials/snowflake-schema-power-bi/)