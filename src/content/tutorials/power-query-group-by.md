---
title: "Power Query Group By: Aggregate Data Without Writing Formulas"
description: "Group By in Power Query lets you summarize rows by category — count, sum, average, min, max — using a visual interface. Learn the UI, advanced grouping with multiple columns, the M code behind it, and the mistakes that produce wrong totals."
pubDate: 2026-07-26
category: "power-query"
difficulty: "Beginner"
tags: ["power-query", "group-by", "aggregation"]
author: "Power BI Tutorials Team"
---

Group By is a Power Query transformation that takes a table of detailed rows and collapses them into summary rows based on one or more grouping columns. It is the Power Query equivalent of a SQL GROUP BY clause or an Excel pivot table — but with a visual interface and no formulas required.

If you have a sales table with 100,000 rows and want to see total sales by region, Group By turns those 100,000 rows into 5 rows (one per region) with a sum column. This guide covers the UI, multi-column grouping, the M code underneath, and the common mistakes that produce wrong totals.

## Using the Group By Dialog

**Step 1:** In Power Query Editor, select the table you want to group.

**Step 2:** On the **Home** tab, click **Group By**.

**Step 3:** In the Group By dialog:
- **Group by:** Select the column(s) to group by (e.g., "Region")
- **New column name:** Name the aggregation output (e.g., "Total Sales")
- **Operation:** Choose the aggregation type (Sum, Average, Count, etc.)
- **Column:** Select which column to aggregate (e.g., "Sales Amount")

**Step 4:** Click **OK**. Power Query collapses the table and adds the aggregation column.

### Available Aggregation Operations

| Operation | What it does | Example |
|-----------|-------------|---------|
| Sum | Adds all values | Total Sales = Sum of Sales Amount |
| Average | Arithmetic mean | Avg Order Value = Average of Order Total |
| Median | Middle value | Median Price = Median of Unit Price |
| Min | Smallest value | Lowest Price = Min of Unit Price |
| Max | Largest value | Highest Price = Max of Unit Price |
| Count Rows | Counts all rows | Order Count = Count of all rows |
| Count Distinct Rows | Counts unique rows | Unique Customers = Count distinct of Customer ID |
| All Rows | Keeps all rows as nested tables | Used for sub-grouping |

## Grouping by Multiple Columns

You can group by more than one column to create hierarchical summaries. For example, grouping by both "Region" and "Product Category" gives you total sales for each region-category combination.

**Step 1:** Open the Group By dialog.

**Step 2:** Click **Add grouping** to add a second grouping column.

**Step 3:** Configure:
- Group by: "Region" (first level)
- Group by: "Product Category" (second level)
- New column name: "Total Sales"
- Operation: Sum
- Column: "Sales Amount"

**Result:** A table with one row per unique Region + Product Category combination, with a Total Sales column.

```
Region     | Product Category | Total Sales
-----------|-----------------|------------
East       | Electronics      | 450,000
East       | Home & Garden    | 180,000
West       | Electronics      | 520,000
West       | Home & Garden    | 210,000
```

## Adding Multiple Aggregations

You can add multiple aggregation columns in a single Group By operation. For example, sum of sales, count of orders, and average order value — all grouped by region.

**Step 1:** In the Group By dialog, after configuring the first aggregation, click **Add aggregation**.

**Step 2:** Configure additional aggregations:
- "Total Sales" → Sum of "Sales Amount"
- "Order Count" → Count Rows
- "Avg Order Value" → Average of "Sales Amount"

**Result:** A table with Region, Total Sales, Order Count, and Avg Order Value columns.

## The M Code Behind Group By

When you use the Group By dialog, Power Query generates M code in the background. Understanding the M code helps you debug issues and write custom grouping logic. See our [Power Query M language basics](/tutorials/power-query-m-language-basics/) guide for M fundamentals.

**Single column group by:**

```m
= Table.Group(
    Source,
    {"Region"},
    {{"Total Sales", each List.Sum([Sales Amount]), type number}}
)
```

**Multi-column group by with multiple aggregations:**

```m
= Table.Group(
    Source,
    {"Region", "Product Category"},
    {
        {"Total Sales", each List.Sum([Sales Amount]), type number},
        {"Order Count", each Table.RowCount(_), type number},
        {"Avg Order Value", each List.Average([Sales Amount]), type number}
    }
)
```

**Syntax breakdown:**
- `Source` — the previous step's table
- `{"Region", "Product Category"}` — the grouping columns
- `{...}` — a list of aggregation definitions, each with: name, function, type
- `each List.Sum([Sales Amount])` — the M function that calculates the aggregation
- `_` — refers to the sub-table of rows for the current group

## Using "All Rows" for Nested Grouping

The "All Rows" operation keeps all original rows as a nested table within each group. This is useful when you need to group data but still want access to the detail rows for further transformations.

```m
= Table.Group(
    Source,
    {"Region"},
    {
        {"Total Sales", each List.Sum([Sales Amount]), type number},
        {"All Orders", each _, type table}
    }
)
```

Each row in the result has a "Total Sales" value and an "All Orders" column containing a nested table with all the original rows for that region. You can click the green "Table" link in the Power Query preview to expand and explore the nested data.

**Common use case:** Group orders by customer to calculate total spend, then expand the nested table to add a calculated column showing each order's percentage of the customer's total.

## Group By vs Power BI Summarize

A common question: should you Group By in Power Query or summarize in DAX?

| Aspect | Group By (Power Query) | DAX Summarize |
|--------|----------------------|---------------|
| When it runs | At data refresh | At query time |
| Data stored | Pre-aggregated rows | Calculated on the fly |
| Flexibility | Fixed at refresh | Dynamic based on filters |
| Performance | Faster (less data) | Slower (more data to process) |
| Best for | Static summaries | Interactive filtering |

**Rule of thumb:** Use Group By when you need a fixed summary table that does not change with user filters. Use DAX measures when users need to dynamically slice and filter the aggregation. See our [CALCULATE function](/tutorials/calculate-function/) guide for dynamic DAX aggregation patterns.

## Common Mistakes

### 1. Grouping by a Column with Too Many Unique Values
```
❌ Group by "Order ID" → produces one row per order, no summarization
✅ Group by "Region" or "Product Category" → meaningful summary
```

Group By only makes sense when the grouping column has fewer unique values than the source table. If the result has almost as many rows as the source, you are not summarizing anything.

### 2. Choosing the Wrong Aggregation Type
```
❌ Count Rows when you want Count Distinct Customers
   → Count Rows gives total order count, not unique customer count
✅ Use "Count Distinct Rows" on the Customer ID column
```

### 3. Forgetting That Group By Removes Other Columns
After Group By, only the grouping columns and aggregation columns remain. All other columns from the source table are removed.

**Fix:** If you need other columns, either:
- Add them as grouping columns (if they have a 1:1 relationship with the group)
- Use "All Rows" to keep the detail data as a nested table
- Merge the grouped result back with the original table

### 4. Data Type Issues After Grouping
```
❌ "Total Sales" column has type "any" after Group By → DAX treats it as text
✅ Set the data type explicitly in the Group By dialog or add a Changed Type step
```

Always verify data types after Group By. The M code includes a `type number` or `type text` declaration, but Power Query sometimes infers the wrong type from the source data.

## FAQ

**Q: Can I undo a Group By?**

Yes, but only if you delete the Group By step in the Applied Steps pane. Once Group By runs, the detailed rows are gone from that step forward. If you need the detail data later, add a new step before the Group By or keep a reference to the pre-grouped table.

**Q: Can I group by a calculated column?**

Yes. Add a calculated column first (using **Add Column** → **Custom Column**), then use that column in the Group By dialog. The calculated column must exist in the table before you open Group By. See our [conditional columns guide](/tutorials/power-query-conditional-columns/) for creating calculated columns with if-then-else logic.

**Q: How does Group By handle null values?**

Group By treats null values as a distinct group. If your grouping column contains nulls, you will get a group for null values. Aggregation functions like `List.Sum` ignore nulls in the values being summed, but `List.Average` also ignores them (it divides by non-null count).

**Q: Is there a limit to how many rows Group By can handle?**

No hard limit, but performance depends on the source data size and the number of unique groups. For extremely large datasets (10M+ rows), consider filtering the data before grouping or using a database-level aggregation instead.

**Q: Can I group by date components (year, month)?**

Yes. First, add calculated columns for the date parts you need:
```m
Year = Date.Year([Order Date])
Month = Date.Month([Order Date])
```
Then use those columns in the Group By dialog. For more date-based transformations, see our [Power Query common transformations](/tutorials/power-query-common-transformations/) guide.

## What's Next

- Learn the M language fundamentals behind Group By: [Power Query M language basics](/tutorials/power-query-m-language-basics/)
- Create columns to group by with conditional logic: [Power Query conditional columns](/tutorials/power-query-conditional-columns/)
- Transform data before grouping: [Power Query common transformations](/tutorials/power-query-common-transformations/)
- Compare with merging data instead of grouping: [Merge vs append queries](/tutorials/merge-vs-append-queries/)
