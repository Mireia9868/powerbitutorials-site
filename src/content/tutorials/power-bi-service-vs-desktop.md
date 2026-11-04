---
title: "Power BI Service vs Desktop: What's the Difference"
description: "Power BI is two products with one name. Power BI Desktop is a free Windows application you install to build reports."
pubDate: 2026-10-08
updatedDate: 2026-11-04
category: service
tags: ["service", "desktop"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Power BI is two products with one name. Power BI Desktop is a free Windows application you install to build reports. Power BI Service is the cloud platform where those reports get published, shared, secured, and refreshed. Beginners hit the confusion early: a visual looks broken online but fine locally, a dataset refresh fails at 3 AM, or a colleague says "just open the workspace" and you have no idea what that means.

This article separates the two clearly, walks through the handoff between them, and covers the differences that actually cause problems: what you can edit where, how refresh works, and how sharing and permissions behave.

## The one-sentence version

Power BI Desktop is where reports are authored. Power BI Service is where they are hosted, distributed, scheduled, and governed.

Desktop has no sharing. Service has no full report authoring. Everything real happens by moving a file from the first to the second.

| Capability | Power BI Desktop | Power BI Service |
|---|---|---|
| Cost | Free download | Free tier; Pro / PPU / Fabric capacity for sharing |
| Platform | Windows only (macOS via VM or Fabric) | Browser + mobile apps |
| Connect to data sources | Yes, full range | Yes, via dataflows, datasets, gateways |
| Build reports from scratch | Yes, full editor | Limited (edit-in-browser for simple changes) |
| Publish / share with others | No | Yes |
| Scheduled refresh | No | Yes |
| Row-level security enforcement | Preview only | Enforced |
| Workspaces, apps, permissions | No | Yes |
| Dashboards | No | Yes |
| Subscriptions, alerts, metrics | No | Yes |
| Version history / deployment pipelines | No | Yes (with capacity or PPU) |

That table is the whole comparison compressed. The rest of this article explains the rows. If the cost row is what is blocking a decision, [model it at your real headcount](/tools/license-calculator/) before going further.

## Power BI Desktop: the authoring tool

Desktop is a single executable that bundles four tools: Power Query (data preparation), the data model (relationships, measures, storage mode), the report canvas (visuals and formatting), and a local analysis engine. If you have used Excel's Power Pivot and Power Query, Desktop will feel familiar.

A few things that matter for beginners:

- Desktop connects to files, databases, cloud services, and web APIs. Import mode copies data into a compressed local model; DirectQuery sends queries back to the source. That tradeoff is worth its own read, and the import-vs-DirectQuery decision shapes everything downstream.
- Everything you build is stored in a single `.pbix` file. That file is your project. Back it up locally or in OneDrive, because it is not automatically versioned.
- Desktop does not enforce row-level security for other users; it only lets you test roles with "View as role". Real enforcement happens after publishing.
- Desktop works entirely offline. No license check for authoring.

A typical workflow: connect, clean in Power Query, build relationships, write DAX measures, design the report page, save the `.pbix`, then publish.

## Power BI Service: the hosting and distribution layer

The Service is a multi-tenant cloud application at app.powerbi.com. Publishing from Desktop uploads a copy of the model and report into a *workspace*.

Once there, the report is a hosted artifact. You can open it in a browser, pin visuals to dashboards, share it with people, embed it in Teams, subscribe to it by email, and point mobile users at it. None of that is possible from Desktop.

The Service also brings capabilities that exist nowhere else:

- **Scheduled refresh.** The model pulls updated data on a timer, from 8 times a day on Pro up to 48 on Premium/Fabric capacity. Requires an on-premises data gateway if the source lives behind your firewall.
- **Dashboards.** A separate canvas that pins visuals from one or more reports onto a single page. Dashboards live only in the Service and cannot be created or edited in Desktop.
- **Apps.** A packaged, read-only bundle of reports and dashboards published to an audience. This is the standard way to distribute to many users.
- **Row-level security enforcement.** Members are filtered by the roles defined in Desktop.
- **Deployment pipelines and version history** on Premium, PPU, or Fabric capacity.

## The handoff: what actually moves when you publish

When you click Publish in Desktop, two artifacts travel to the workspace: the dataset (the semantic model) and the report. They are linked but stored separately.

That split is the source of a lot of confusion. Any of these can happen independently:

- You update a DAX measure, republish, and the report picks up the new logic automatically because both artifacts came from the same file.
- You build a *new* report in the Service on top of an existing dataset (using "Create report" from the workspace) and now two reports share one model. Editing the model in Desktop republishes over it and affects both.
- You edit the report in the Service with edit-in-browser, and the change is saved to the Service copy, not your local `.pbix`. Republishing from Desktop overwrites it.

That last point trips people up constantly. If a colleague fixes a visual online, your next Publish will silently discard their edit unless you first download the updated `.pbix`.

## Refresh: where the two really diverge

Desktop reads from its source every time you hit Refresh in the Home ribbon. That is a manual, local operation. The Service cannot "read" anything the way Desktop can, so refresh has to be configured.

For an on-premises SQL Server, the flow is: install a gateway on a machine with network access, register it in the Service, then configure credentials on the dataset. Without a gateway, only cloud sources and sources reachable by the Service itself will refresh.

Refresh failures are the most common Service-only problem. "Data source credentials are invalid" almost always means the Service is using a different set of credentials than Desktop. Desktop cached your Windows login; the Service needs its own.

A DAX measure that behaves differently after publishing is usually not a refresh problem at all. It is context. Service renders fewer, or different, rows than your Desktop preview. Useful debugging tip: keep a measure that surfaces the current user so you can test RLS behaviour online.

```dax
Current User =
VAR _upn = USERPRINCIPALNAME ()
RETURN
    IF ( ISBLANK ( _upn ), "No user context (Desktop)", _upn )
```

`USERPRINCIPALNAME()` returns an empty string in Desktop preview but resolves to the logged-in account in the Service, which is exactly the difference you want to see when RLS is misbehaving.

## Licences and sharing in one paragraph

Desktop is free; publishing requires an account. With a **free** account you can publish to a personal workspace and use it yourself. To share with others you need **Pro** (all parties need Pro), **Premium Per User** (PPU, per-user equivalent of Premium), or access to a workspace on **Fabric/Premium capacity** (viewers generally do not need a licence). Sharing reports with someone who lacks the right licence is the single most common "it doesn't work" issue for new users.

## Editing: who can change what

You can edit reports directly in the Service, but the experience is stripped down. It supports adding visuals, changing fields, formatting, and bookmarks, but not Power Query transformations, relationship editing, or new tables. Think of edit-in-browser as a patch tool, not a replacement.

If you hit the "Edit" button and it is greyed out, it is almost always a permissions issue: you have View access, not Edit, or you are working in an App rather than the underlying workspace.

## Practical advice

- Keep the `.pbix` as the source of truth. Do not let anyone edit reports in the Service unless you have a way to sync the file back.
- Use a gateway for any on-premises source. Test with a small manual refresh before setting a schedule.
- Test RLS with "View as role" in Desktop and then again in the Service as the actual user. UI differences and `USERPRINCIPALNAME()` behaviour are the two places the two environments genuinely behave differently.
- If you deploy widely, publish an App, not a workspace. Apps give you a stable URL and a controlled audience.
- Watch out for gateway and personal credentials being used by scheduled refresh; a task account is safer than a personal one.

If you have never opened the Service at all, the fastest way to see the difference is to build a trivial report in Desktop, publish it, then pin a visual to a dashboard in the Service. The dashboard artefact has no Desktop equivalent, and that single fact explains the whole architecture.

### Q: Can I use Power BI without installing Desktop?

Yes, if someone else built the report and shared it with you. As a pure consumer you open app.powerbi.com, log in, and view reports and dashboards. You cannot author a report from scratch without Desktop or Fabric access.

### Q: Is Power BI Desktop free?

Yes, the Desktop download is free and unlimited for authoring. Sharing with other people requires a paid licence (Pro, PPU) or a Fabric capacity for the workspace.

### Q: Why does a report look different in Service than in Desktop?

Most commonly because of a missing refresh, a filter that references a different user context, or a page size that is different from the Desktop canvas. Compare the two by checking the "Last refreshed" timestamp on the dataset and, if RLS is in play, logging in as the affected user via "View as role".

### Q: Can I edit a report in the Service and then download it?

Yes. Open the report in the Service, use File → Download a copy to get a `.pbix`, then open it in Desktop. Be careful: any edits made in the Service after your last publish are lost if you republish from an older local file.

### Q: Do I need a gateway if my data is in SharePoint or OneDrive?

Usually not. Cloud-to-cloud sources work without a gateway. You need one when the source is on-premises or behind a corporate network, such as SQL Server on an internal VM or an Excel file on a network share.

For the official documentation behind this topic, see [Microsoft Power BI service overview](https://learn.microsoft.com/en-us/power-bi/fundamentals/power-bi-service-overview).

## Related Reading

- [/tutorials/directquery-vs-import-mode/](/tutorials/directquery-vs-import-mode/)
- [/tutorials/power-bi-common-mistakes-beginners/](/tutorials/power-bi-common-mistakes-beginners/)
- [/tutorials/power-bi-excel-integration/](/tutorials/power-bi-excel-integration/)
- [/tutorials/data-modeling-star-schema/](/tutorials/data-modeling-star-schema/)
- [/tutorials/bidirectional-filtering-guide/](/tutorials/bidirectional-filtering-guide/)
- [/tutorials/dax-basics/](/tutorials/dax-basics/)
- [/tutorials/power-bi-dashboard-design-principles/](/tutorials/power-bi-dashboard-design-principles/)
- [/tutorials/power-bi-drill-through/](/tutorials/power-bi-drill-through/)
- [/tutorials/calculated-tables-what-if-parameters/](/tutorials/calculated-tables-what-if-parameters/)
- [Power BI Licensing: Free vs Pro vs PPU vs Fabric](/tutorials/power-bi-licensing-explained/)
- [Scheduled Refresh Failed: Seven Causes and the Fix](/tutorials/scheduled-refresh-failed-gateway/)
