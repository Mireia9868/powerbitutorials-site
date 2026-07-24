---
title: "Power BI Row-Level Security: Control Who Sees What Data"
description: "Row-Level Security (RLS) filters data at the row level based on the user viewing the report. This guide covers static RLS, dynamic RLS with USERNAME(), deployment to the Power BI Service, and the design patterns for multi-tenant security models."
pubDate: 2026-07-23
category: "data-modeling"
difficulty: "Intermediate"
tags: ["data-modeling", "rls", "security", "dynamic-rls", "userprinciplename"]
author: "Power BI Tutorials Team"
featured: false
draft: false
---

Row-Level Security (RLS) filters data at the row level based on the user viewing the report. This guide covers static RLS, dynamic RLS with USERNAME(), deployment to the Power BI Service, and the design patterns for multi-tenant security models.

When multiple users share a report but should only see their own data, RLS is the answer. A regional manager sees only their region. A sales rep sees only their customers. An executive sees everything. The same report, the same data model — different rows visible per user. This guide covers the two RLS approaches and the patterns that make them maintainable.

## How RLS works

RLS applies a DAX filter to a table in your data model. When a user views the report, the filter is applied automatically before any visual renders. The user never sees the filtered-out rows, and they can't bypass the filter — it's enforced at the query level by the Power BI engine.

**Key principle:** RLS filters flow through relationships just like any other filter. If you apply RLS to a dimension table, the filter propagates to connected fact tables through the relationship. You only need to secure the dimension table.

## Static RLS

Static RLS uses a hardcoded filter rule per role. Each role has a fixed DAX filter expression that doesn't change based on the user.

### Step 1: Define roles in Power BI Desktop

1. Go to the **Modeling** tab
2. Click **Manage roles**
3. Click **New** to create a role
4. Name the role (e.g., "West Region")
5. Select the table you want to filter
6. Enter a DAX filter expression in the field

### Step 2: Write the filter expression

For a region security table:

```dax
// In the Manage Roles dialog, on the Region table:
[Region] = "West"
```

This filter means: when the "West Region" role is active, only rows where `Region[Region] = "West"` are visible. The filter propagates through relationships to connected fact tables.

### Step 3: Test in Power BI Desktop

1. Click **View as** in the Modeling tab
2. Check the "West Region" role
3. The report now shows only West region data
4. Uncheck to return to full data view

### Step 4: Assign users in the Power BI Service

1. Publish the report to the Power BI Service
2. Go to the dataset's Security settings
3. Add users or groups to each role

**Limitation of static RLS:** every role is a separate rule with a hardcoded value. If you have 50 regions, you need 50 roles. When regions change, you must update the roles manually. This doesn't scale.

## Dynamic RLS

Dynamic RLS uses a single role with a filter that reads the current user's identity and looks up their permissions from a security table. One role, infinite users.

### Step 1: Create a security table

Add a table to your data model that maps users to their security context:

| Email | Region |
|-------|--------|
| alice@company.com | West |
| bob@company.com | East |
| carol@company.com | All |

Connect this table to your Region dimension table with a relationship. The security table should filter the region table (security → region, single direction).

### Step 2: Create a single role

1. Go to **Manage roles**
2. Create one role called "Dynamic RLS"
3. On the security table, enter this filter:

```dax
// Filter the security table by the current user's email
[Email] = USERPRINCIPALNAME()
```

`USERPRINCIPALNAME()` returns the user's email address from Azure AD (e.g., `alice@company.com`). When Alice views the report, the security table is filtered to her row, which filters the region table to "West", which filters all fact tables to West region data.

### Step 3: Assign everyone to the single role

In the Power BI Service, add all users to the "Dynamic RLS" role. Each user will see different data because the filter expression evaluates differently for each one.

### The "All" pattern

For users who should see everything (executives, admins), add a special row to the security table and handle it in the filter:

**Security table:**

| Email | Region |
|-------|--------|
| alice@company.com | West |
| bob@company.com | East |
| carol@company.com | All |

**Filter expression:**

```dax
// On the Region table (not the security table):
[Region] =
    IF(
        LOOKUPVALUE(Security[Region], Security[Email], USERPRINCIPALNAME()) = "All",
        [Region],  // If "All", show every region (no filter)
        LOOKUPVALUE(Security[Region], Security[Email], USERPRINCIPALNAME())
    )
```

**Better approach:** Instead of a complex DAX expression, use a many-to-many security table with one row per user-region combination. An admin gets a row for every region. This avoids the "All" special case entirely:

| Email | Region |
|-------|--------|
| alice@company.com | West |
| bob@company.com | East |
| carol@company.com | West |
| carol@company.com | East |
| carol@company.com | North |
| carol@company.com | South |

The filter `[Email] = USERPRINCIPALNAME()` on the security table naturally returns all of Carol's region rows, and the relationship propagates all of them.

## USERNAME() vs USERPRINCIPALNAME()

Two functions return the current user's identity, but they return different values depending on where the report is viewed:

| Function | Power BI Desktop | Power BI Service |
|----------|-----------------|-----------------|
| `USERNAME()` | `DOMAIN\User` | `user@company.com` |
| `USERPRINCIPALNAME()` | `user@company.com` | `user@company.com` |

**Always use `USERPRINCIPALNAME()`** for RLS. It returns the email address consistently in both Desktop and Service, which matches how users are identified in Azure AD and the Power BI Service.

`USERNAME()` returns a Windows-style domain\user format in Desktop, which won't match your security table. This causes RLS to work in the Service but fail in Desktop testing.

## Multi-table security

When security depends on multiple dimensions (e.g., a user can see specific regions AND specific product categories), the security table needs a composite structure:

| Email | Region | Product Category |
|-------|--------|-----------------|
| alice@company.com | West | Electronics |
| alice@company.com | West | Accessories |
| bob@company.com | East | Electronics |

The filter `[Email] = USERPRINCIPALNAME()` on this table returns all matching rows. The relationships to both the Region and Product Category tables propagate the filters independently.

**Warning:** this requires the security table to have relationships to both dimension tables, and both relationships must be single-direction. Bidirectional filtering here can create ambiguous filter paths.

## RLS and the data model

RLS filters respect your data model's relationship directions. A few rules:

1. **Single-direction relationships:** RLS on a dimension table flows to fact tables. This is the standard pattern.
2. **Bidirectional relationships:** RLS can flow both ways, but this risks unintended filtering. Avoid bidirectional filtering in security scenarios.
3. **Disconnected tables:** RLS on a disconnected table does nothing — there's no relationship to propagate the filter through.

**Best practice:** Apply RLS to dimension tables, not fact tables. Filtering a dimension table is faster (fewer rows) and propagates naturally to all connected fact tables.

## Testing RLS

### In Power BI Desktop

1. Go to **Modeling → View as**
2. Select the role to test
3. The report renders with that role's filters applied
4. For dynamic RLS, enter a specific email in the "View as" dialog to simulate that user

### In Power BI Service

1. Go to the dataset → Security
2. Click "Test as role" next to a user's name
3. The report opens in a test mode showing what that user would see
4. Verify the data matches expectations

### Common testing issues

- **Everything is blank:** the user's email in the security table doesn't match their Power BI Service email. Check for typos, domain differences (onmicrosoft.com vs company.com), or case sensitivity.
- **User sees too much:** the user is assigned to multiple roles, and one of them has no filter. A user with no role assignment sees all data by default — make sure every user is assigned to at least one RLS role.
- **User sees too little:** the security table has the wrong region value, or the relationship between the security table and dimension table is missing or reversed.

## Common mistakes

### 1. Forgetting to assign users to roles

After publishing, roles have no members. If you don't assign users in the Power BI Service Security settings, RLS isn't active for anyone — all users see all data.

**Fix:** Always verify user assignments after publishing. Go to dataset → Security and confirm every user is in the correct role.

### 2. Using USERNAME() instead of USERPRINCIPALNAME()

As explained above, `USERNAME()` returns different formats in Desktop vs. Service. This causes RLS to work in testing but fail in production.

### 3. Applying RLS to fact tables

```dax
// WRONG — filters the fact table directly, slow and error-prone
Security filter on Sales table: [RegionKey] = LOOKUPVALUE(...)

// RIGHT — filters the dimension table, propagates through relationship
Security filter on Region table: [Region] = LOOKUPVALUE(Security[Region], Security[Email], USERPRINCIPALNAME())
```

### 4. RLS conflicts with measures using ALL()

```dax
// This measure ignores RLS — shows total revenue across ALL regions
Total Revenue All = CALCULATE([Total Revenue], ALL(Region))
```

`ALL()` removes filters from the Region table, including RLS filters. If a measure uses `ALL()` on a secured table, it can leak data to users who shouldn't see it.

**Fix:** Use `ALLSELECTED()` instead of `ALL()` where possible. `ALLSELECTED` respects RLS because it works with the filter context after RLS is applied. If you must use `ALL()`, verify the measure doesn't expose secured data.

## FAQ

**Does RLS work with DirectQuery?**
Yes. RLS is applied as a WHERE clause in the SQL query sent to the source database. The performance impact depends on the source database's indexing and the complexity of the RLS filter.

**Can users see RLS filters?**
No. RLS is invisible to report viewers. Users don't know which rows are filtered out unless they compare their view with someone else's.

**Can I use RLS with embedded reports?**
Yes, but the embedding application must pass the effective identity (user email and optionally role) when generating the embed token. Without an effective identity, RLS isn't applied.

**How does RLS interact with row-level security in the source database?**
They're independent. If your SQL database has RLS, and Power BI also has RLS, both filters apply. The result is the intersection — a user sees only rows that pass both filters.

**Can I bypass RLS for specific users?**
Yes. Users with "Admin" or "Member" access to the workspace can view the report without RLS by using "View as" and unchecking all roles. For Service-level bypass, mark the dataset to allow admin override in the tenant settings.

## What's next

- Learn [star schema data modeling](/tutorials/data-modeling-star-schema) to understand how RLS filters propagate through dimension tables
- Read the [bidirectional filtering guide](/tutorials/bidirectional-filtering-guide) to understand why bidirectional relationships can break RLS
- See the [performance optimization guide](/tutorials/power-bi-performance-optimization) if RLS filters are slowing down your reports
- Check the [one-to-many vs many-to-many relationships](/tutorials/relationships-one-to-many-many-to-many) guide for designing security table relationships
