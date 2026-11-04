---
title: "Scheduled Refresh Failed: Seven Causes and the Fix"
description: "Your refresh worked yesterday. Seven reasons it stopped, in the order worth checking — from gateway offline to a query that times out only under load."
pubDate: 2026-11-04
category: service
tags: ["refresh", "gateway", "troubleshooting", "service"]
difficulty: Intermediate
author: Mireia
featured: false
draft: false
---

A scheduled refresh that worked yesterday and failed today is one of the least informative errors in Power BI. The email says "refresh failed" and the workspace says "failed", and neither tells you whether the gateway is offline, a credential expired, or a query that takes 90 seconds finally exceeded a timeout.

This is an ordered diagnosis, not a list. Work down it — the causes are sorted by how often they occur and how cheap they are to rule out.

## Before anything: read the actual error

Click into the failure. In the workspace, hover the refresh time and open the history; the error message there is often specific even when the notification is not.

| Message fragment | Points to |
|---|---|
| "unable to connect to the data source" | Gateway or network (cause 1–2) |
| "the credentials provided are invalid" | Cause 3 |
| "the operation has timed out" | Cause 5 or 6 |
| "the query referenced a column that doesn't exist" | Cause 7 |
| "the gateway is offline" | Cause 1 |

If the message is genuinely generic, start at cause 1.

## 1. The gateway is offline or was updated

The most common cause, and the fastest to check. Go to **Settings → Manage connections and gateways** and look at the gateway status.

A machine that reboots for Windows updates and does not restart the gateway service produces exactly this: a few failed refreshes, then it works again when someone logs in. The gateway service is set to start automatically by default, but an update can change that, and a machine that is asleep cannot run it.

**Fix:** check the service is running (`services.msc` → "Power BI gateway"), and set recovery options to restart on failure. On a production gateway, run it on a machine that does not sleep and is excluded from automatic reboots.

## 2. The gateway cannot reach the source

Gateway online, refresh still fails with a connection error. The gateway cluster is a Windows service on your network, so it needs the same access your own machine has — and it runs under a service account, not your user.

**Check:** on the gateway machine itself, try connecting to the source with the same credentials the data source uses. If that fails, the problem is network or permissions, not Power BI.

Common variants:

- **Firewall rule added for your IP, not the gateway's.**
- **VPN required** — the gateway machine is not on it.
- **DNS** — the gateway resolves an internal name the PowerShell test resolves differently.
- **TLS version** — an older gateway build against a source that dropped TLS 1.0/1.1.

Microsoft's [gateway troubleshooting guide](https://learn.microsoft.com/en-us/data-integration/gateway/service-gateway-tshoot) covers the connectivity tests in detail.

## 3. Credentials expired

The second most common cause, and the one that produces the most confusing symptoms — because the report *opens fine* in Desktop, where your interactive credentials are used.

Three places credentials live, and each expires independently:

| Where | What expires |
|---|---|
| Data source credentials in the gateway | OAuth tokens, password changes |
| Dataset credentials in the service | Same, per dataset |
| Scheduled refresh owner's account | Password reset, MFA change, account disabled |

The third one catches people constantly. **A scheduled refresh runs as the person who configured it.** If that person changes their password, goes on leave with an expired account, or leaves the company, the refresh fails with a credential error that has nothing to do with the data source.

**Fix:** set the refresh owner to a service account, not an individual. In the dataset settings, use "Take over" and assign it to an account that does not belong to one person.

## 4. The dataset is too large for the capacity

Refresh works manually, fails on schedule — or works for months and then starts failing as data grows.

If the model exceeds the memory limit of its capacity, the refresh fails near the end, after the expensive part has already run. Pro allows 1 GB; PPU and Fabric capacities allow more. Check the model size under **Settings → Large dataset storage format** and in the refresh history's duration column — a refresh that runs for 40 minutes and then fails is usually memory, not a query problem.

**Fix:** reduce the model before buying capacity. Removing unused columns, disabling Auto Date/Time, and dropping high-cardinality text columns is often enough. If it genuinely needs more memory, that is a licensing decision — our [licence calculator](/tools/license-calculator/) covers the PPU-versus-capacity trade-off.

## 5. The refresh window is too short

Power BI has a default refresh timeout of **two hours** for a scheduled refresh. A refresh that takes 1h55m succeeds; add 10% more data and it fails with a timeout that looks like a performance problem.

This one hides well because the failure is intermittent and correlates with data volume rather than with any code change.

**Fix:** check the duration history. If refreshes are trending toward two hours, the fix is incremental refresh, not a longer timeout — Microsoft does not expose the timeout setting for scheduled refresh on shared capacity.

## 6. The source is slow at the scheduled time

Everybody schedules refreshes for 06:00. If the source database is also running its own overnight jobs, the refresh competes with them and loses.

Symptom: manual refresh at 14:00 takes 4 minutes; the 06:00 scheduled refresh times out. The dataset is fine; the schedule is the problem.

**Fix:** stagger. Move the refresh to 05:30 or 07:00, or split a large model into two datasets with different schedules.

## 7. A query broke because the source schema changed

The only cause on this list where the error message is usually specific. A column renamed, a table dropped, a data type changed from text to integer upstream — Power BI says so.

It appears in the scheduled refresh first because that is when the query actually runs. Nobody notices in Desktop until they reopen the file.

**Fix:** fix the query in Power Query, republish, and add a schema check to whatever produces the source. This is the one cause where the fix is in the data pipeline, not in Power BI.

## The three-minute triage

When a refresh fails and you do not want to read the history:

1. **Gateway status** — online? (30 seconds, rules out cause 1)
2. **Refresh duration in history** — close to 2 hours? (rules out 4, 5, 6)
3. **Error text** — contains "credentials"? (rules out 3)
4. **Manual refresh now** — works? Then it is timing (5, 6), not definition (7)

That sequence resolves most incidents without opening a ticket.

## FAQ

### Q: Why does manual refresh work but scheduled refresh fail?

Manual refresh runs as you, interactively, with your credentials and without the two-hour timeout. Scheduled refresh runs as the configured owner, through the gateway, under the timeout. Any of the three differing is enough — check the owner first, it is the most common.

### Q: Refresh fails every time for one specific table. Why?

Usually a query problem rather than a gateway problem: a step that references a column the source no longer returns, or a parameter that resolves differently on the gateway machine (a local file path is the classic). Test that table alone in Power Query on the gateway machine.

### Q: Do I need a gateway for cloud sources like SharePoint or Azure SQL?

Not if Power BI can reach the source directly. You need a gateway when the source is on-premises, or when it is in a private network. For cloud sources the gateway only adds a failure point.

### Q: How do I know whether it was memory or timeout?

Look at the duration. A refresh that fails after a long run is usually memory (the engine spent the time building the model, then could not fit it). A refresh that fails at almost exactly two hours is the timeout. A refresh that fails in seconds is a connection or credential problem.

## Related Reading

- [Incremental Refresh: Setup and Gotchas](/tutorials/power-bi-incremental-refresh/)
- [Power BI Service vs Desktop: What Runs Where](/tutorials/power-bi-service-vs-desktop/)
- [Power BI Licensing: Free vs Pro vs PPU vs Fabric](/tutorials/power-bi-licensing-explained/)
- [Power BI Dataflows Explained](/tutorials/power-bi-dataflows/)
- [Row-Level Security in Power BI](/tutorials/power-bi-row-level-security/)
- [DAX Optimization: 10 Patterns That Work](/tutorials/power-bi-dax-optimization/)
- [Calculation Groups: One Slicer for Every Time Grain](/tutorials/calculation-groups-power-bi/)
