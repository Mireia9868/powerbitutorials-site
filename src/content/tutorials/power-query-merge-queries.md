---
title: "Merge Queries in Power Query (VLOOKUP Equivalent)"
description: "Merging queries in Power Query is the closest thing Excel users get to a familiar friend: VLOOKUP."
pubDate: 2026-10-12
category: power-query
tags: ["power query", "merge"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Merging queries in Power Query is the closest thing Excel users get to a familiar friend: VLOOKUP. If you have spent years writing `=VLOOKUP(A2, Sheet2!$A:$D, 4, FALSE)` and dragging it down ten thousand rows, the merge operation maps directly onto that mental model. It joins two tables on one or more matching columns and pulls in the extra columns you need.

The difference is that the work happens once, at refresh time, instead of on every recalculation. That shift is the whole reason merges belong in Power Query rather than in the data model as a calculated column.

## What a Merge Actually Does

A merge takes a **left table** (your primary table, the one you are enriching), a **right table** (the lookup table), and a join kind. Power Query matches rows where the key columns are equal, then attaches the requested columns from the right table.

There are six join kinds, and they are the part beginners get wrong most often:

| Join kind | Behaviour | VLOOKUP analogy |
|---|---|---|
| Left Outer | All left rows; `null` where no right match | Standard VLOOKUP with `IFERROR` |
| Right Outer | All right rows; `null` where no left match | Rarely used |
| Full Outer | All rows from both sides | Not expressible in VLOOKUP |
| Inner | Only rows that match on both sides | VLOOKUP with an `ISNA` filter |
| Left Anti | Left rows with **no** right match | Finding missing lookups |
| Right Anti | Right rows with no left match | Finding unused lookup values |

The default in the Power Query UI is **Left Outer**, which matches how most people use VLOOKUP. You want to keep every row of your fact table and add attributes where they exist.

## Preparing Both Tables Before You Merge

Two checks save a lot of debugging.

**Check data types on the key columns.** If `CustomerID` is text on one side and a whole number on the other, the merge produces zero matches and no error message. Power Query does not shout at you; it silently returns a column full of `null`. Set both keys to the same type first, using the data type icon in the column header.

**Watch for duplicate keys on the right side.** VLOOKUP returns the first match. Power Query does not pick a winner: it produces one output row *per match*. A lookup table with two rows for customer 1042 will silently double that customer's rows in the merged result, inflating every downstream aggregate. Before merging, verify uniqueness:

```powerquery
// Run on the RIGHT (lookup) table before merging.
// Returns any CustomerID that appears more than once.
let
    Source       = Excel.CurrentWorkbook(){[Name="Customers"]}[Content],
    Typed        = Table.TransformColumnTypes(Source, {{"CustomerID", Int64.Type}}),
    Grouped      = Table.Group(Typed, {"CustomerID"}, {{"Rows", each Table.RowCount(_), Int64.Type}}),
    Duplicates   = Table.SelectRows(Grouped, each [Rows] > 1)
in
    Duplicates
```

If that query returns rows, clean the lookup table before you merge. Merging against a non-unique key is the single most common cause of "my numbers doubled" posts on forums.

## Step-by-Step: Merge in the Power Query Editor

1. Load both tables into Power Query. In the Navigator, tick each table and choose **Transform Data** rather than **Load**, so you land in the editor.
2. From the left table's query, go to **Home > Merge Queries > Merge Queries as New**. Using "as New" keeps the original queries intact and gives you a third query containing only the join result. It is easier to reason about and easier to trace when something breaks.
3. Select the key column in the top table. Ctrl-click for a composite key across multiple columns.
4. Select the right table from the dropdown and click the matching key column or columns. The order of selection must match.
5. Choose the join kind. For a VLOOKUP replacement this is **Left Outer**.
6. Click **OK**. You now have a column containing the word `Table` on every row.

That `Table` column is not the result yet. It is an embedded table holding every matching right-side row, with all the right table's columns. Click the expand icon (the two arrows pointing outward) in the column header.

In the expand dialog:

- Untick **Use original column name as prefix** if you want clean column names. Leaving it ticked produces names like `Customers.CompanyName`, which is fine but noisier in the model.
- Tick only the columns you actually need. Pulling in every column bloats the model and slows refresh.
- If the right table has duplicate keys, the dialog warns you with an italic note showing the row multiplier, for example `3 of 5 rows matched`. That is Power Query telling you the merge will expand your row count.

## Adding Conditional Columns Instead of VLOOKUP's Column Index

This is the biggest practical difference between Excel and Power Query, and it is in Power Query's favour. VLOOKUP forces you to count column positions, so inserting a column in the source breaks every formula. With a merge you name the columns you want, and a source insertion changes nothing.

If you need a lookup that returns a value based on a category rather than an exact key, a conditional column handles it natively. Consider a table of orders where the lookup table holds the discount tier per customer segment. After merging and expanding the `Segment` column, add the rate:

```powerquery
let
    Source        = Orders,
    // 'Segment' arrived from the merged Customers query
    AddDiscount   = Table.AddColumn(Source, "DiscountRate", each
                        if [Segment] = "Enterprise"  then 0.20
                        else if [Segment] = "Mid-Market" then 0.12
                        else if [Segment] = "SMB"        then 0.05
                        else 0, type number),
    AddRevenue    = Table.AddColumn(AddDiscount, "NetRevenue", each
                        [OrderTotal] * (1 - [DiscountRate]), type number)
in
    AddRevenue
```

You can also do this with `Table.NestedJoin` and `Table.ExpandTableColumn` written by hand, which is what the UI generates. Reading the generated M is worthwhile:

```powerquery
let
    Source   = Orders,
    Merged   = Table.NestedJoin(
                   Source, {"CustomerID"},
                   Customers, {"CustomerID"},
                   "Customers", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(
                   Merged, "Customers",
                   {"CompanyName", "Segment", "Region"},
                   {"CompanyName", "Segment", "Region"})
in
    Expanded
```

Note the comparison is case-sensitive. `"acme"` and `"ACME"` will not match. If your source data arrives with inconsistent casing, run **Transform > Format > Capitalize Each Word** or lowercase both keys before merging.

## Merge vs. Relationship: Which One?

A merge physically flattens the right table's columns into the left table. A model relationship keeps the tables separate and lets the engine join them at query time.

Use a **merge** when:

- The key exists only in one of the two tables and you need it in the other.
- You need the lookup value inside a calculated column, not a measure.
- The lookup table has columns you want to slice by in a flat table visual or export.
- You are preparing a single denormalised table for Excel or CSV output.

Use a **relationship** when the lookup table is a dimension with attributes you will filter and slice by. Star schema design keeps dimensions separate and connected, and both filter propagation and model size benefit. Merging a large fact table into a dimension makes refresh slower and the file bigger with no gain.

There is one hard rule worth repeating: a merge happens at refresh, a relationship happens at query time. If the lookup table changes between refreshes, only the relationship path sees the change immediately.

## Handling Nulls and Unmatched Rows

After a Left Outer merge, unmatched rows show `null` in the expanded columns. That is correct and desirable; do not replace `null` with a blank string just to make the preview look tidy. `null` is a genuine "no value" and behaves properly in DAX comparisons, whereas an empty string `""` breaks numeric aggregation.

If you need a placeholder, use **Replace Values** deliberately and document it:

```powerquery
let
    Source    = Expanded,
    Filled    = Table.ReplaceValue(
                    Source,
                    null,
                    "Unclassified",
                    Replacer.ReplaceValue,
                    {"Segment"})
in
    Filled
```

Use **Left Anti** to audit instead. Merging your fact table against the customer dimension with Left Anti returns every order whose customer does not exist in the dimension. That list is almost always a data quality problem worth fixing upstream rather than a merge you should patch after the fact.

## Performance Notes for Large Tables

Sort or buffer the right table when it is small and reused: `Table.Buffer` forces it into memory once instead of re-reading at each step. Wider right tables and larger expansions cost more. Pull only the columns you need. Set data types explicitly on the expanded columns rather than letting Power Query infer them, because inference runs a scan over the whole column.

For the full picture on when to merge versus stack tables vertically, the distinction between merge and append trips up as many beginners as join kinds do.

## FAQ

### Q: Why did my row count increase after a Left Outer merge?

The right table contains duplicate values in the join key. A Left Outer merge keeps every left row but produces one output row per matching right row, so a right-side key that appears three times triples those rows. Check the right table for uniqueness before merging, or use **Group By** to aggregate the right table down to one row per key first.

### Q: Can I merge on more than one column?

Yes. Ctrl-click to select multiple key columns in the top table, then select the matching columns on the right in the same order. Power Query treats the combination as a composite key, which is often the correct fix when a single column is not unique. The column count and order must match on both sides.

### Q: Is merging the same as creating a relationship in the data model?

No. A merge is a physical operation performed by the Power Query engine at refresh time and it writes the joined columns into the resulting table. A relationship is metadata the VertiPaq engine uses at query time and it leaves both tables intact. Merges suit flattening and calculated columns; relationships suit star schema dimension filtering.

### Q: Why do my matches return null when the values look identical?

Almost always a data type mismatch or invisible whitespace. A text `"1001"` will never match a numeric `1001`. Check and align the types on both key columns, then run **Transform > Format > Trim** and **Clean** on both keys to remove leading spaces and non-printing characters. Case differences matter too.

### Q: Does a merge update automatically when the source table changes?

Yes, on the next refresh. The merge is baked into the query's M code, so pressing **Refresh** re-runs the join against the current source data. If you are using a DirectQuery source, the join behaviour depends on query folding, which is a separate consideration from Import mode.

For the official documentation behind this topic, see [Microsoft Merge queries](https://learn.microsoft.com/en-us/power-query/merge-queries-overview).

## Related Reading

- [Merge vs Append Queries](/tutorials/merge-vs-append-queries/)
- [Data Modeling: Star Schema](/tutorials/data-modeling-star-schema/)
- [DirectQuery vs Import Mode](/tutorials/directquery-vs-import-mode/)
- [Measure vs Calculated Column](/tutorials/measure-vs-calculated-column/)
- [Filter Context vs Row Context Explained](/tutorials/filter-context-row-context-explained/)
- [The DAX EARLIER Function](/tutorials/dax-earlier-function/)
- [Power BI Common Mistakes for Beginners](/tutorials/power-bi-common-mistakes-beginners/)
- [Power BI Excel Integration](/tutorials/power-bi-excel-integration/)
