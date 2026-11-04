---
title: "Power BI Licensing: Free vs Pro vs PPU vs Fabric"
description: "Four licence types, one decision. What Free cannot do, when Pro is enough, and the headcount where Fabric capacity beats per-user pricing."
pubDate: 2026-11-04
category: service
tags: ["licensing", "pricing", "fabric", "pro", "premium"]
difficulty: Beginner
author: Mireia
featured: false
draft: false
---

Power BI has four ways to pay for it, and the one most people start on — Free — cannot do the thing they are trying to do. That is not a marketing trick so much as a documentation gap: Microsoft's licensing pages explain what each tier *contains*, and leave the "which one do I actually need" question to you.

This article is about the decision, not the feature list. Prices are US list, checked 4 November 2026.

## The four options, in one table

| | Free | Pro | Premium Per User | Fabric capacity |
|---|---|---|---|---|
| Price | $0 | **$14**/user/month | **$24**/user/month | per capacity, from F2 |
| Build reports in Desktop | ✅ | ✅ | ✅ | ✅ |
| Publish to the service | ❌ | ✅ | ✅ | ✅ |
| **View a shared report** | ❌ | ✅ | ✅ | ✅ (Free users can view) |
| Model size limit | 1 GB | 1 GB | 100 GB | 100 GB+ |
| Refreshes per day | 8 (personal) | 8 | 48 | 48 |
| Deployment pipelines | ❌ | ❌ | ✅ | ✅ |
| AI / Copilot features | ❌ | partial | ✅ | ✅ |
| Billing unit | — | per person | per person | per capacity |

The row that matters most is the third one. **A Free account can build a report in Desktop and cannot share it.** The moment a report is published to a workspace, every person who opens it needs a licence — or the workspace needs to sit on a Fabric capacity.

This is the single most common licensing surprise in Power BI, and it is why "we have 200 Free users" is never a valid answer to a cost question.

## Free is not a trial, but it is close

Free gives you the full Desktop authoring tool, which is genuinely useful: you can connect to data, model it, write DAX and build a report, entirely offline, forever, at no cost.

What it does not give you is distribution. No publishing, no scheduled refresh in the service, no sharing, no mobile app access to a shared report.

So Free is the right licence for exactly two groups: people learning Power BI, and people whose reports never leave their own machine. Everyone else is on it temporarily.

## Pro is the default, and stays the default

At $14 per user per month (annual billing), Pro covers publishing, sharing, workspaces, apps, row-level security, scheduled refresh up to eight times a day, and models up to 1 GB.

For a team of ten building internal dashboards, this is almost always the answer. There is no per-capacity minimum, it scales linearly, and it requires no procurement conversation.

The two constraints that eventually push teams off Pro are **model size** and **refresh frequency**. A 1 GB limit sounds generous until you load three years of transaction-level data with a wide fact table. Eight refreshes a day is plenty for daily reporting and not enough for anything resembling operational monitoring.

## PPU exists for the people who hit those limits, not for the whole team

Premium Per User is $24 per user per month and removes both constraints: 100 GB models, 48 refreshes a day, deployment pipelines, and the premium-only AI features.

The mistake is buying it for everyone. **PPU's value is concentrated in the two or three people who build the models that hit the ceiling.** The fifty people who open a dashboard on Monday morning need none of it.

The pattern that works:

```
Builders (2–5 people)      → PPU
Everyone who only views    → Pro
```

That structure typically saves 30–40% against putting the whole team on PPU, and it is the default assumption in our [Power BI licence calculator](/tools/license-calculator/).

## Fabric capacity is a different purchase

A Fabric capacity (F-SKU) is not a user licence. It is a reserved pool of compute, billed monthly whether anyone uses it or not, and it changes the licensing maths in two ways:

1. **Free users can view reports** in workspaces backed by a capacity. That removes the per-viewer cost entirely.
2. **Everything in Premium comes included**, for every user in the tenant, without a per-user charge.

The catch is the price floor. Capacity starts at small SKUs intended for development, and the smallest SKU that replaces a Power BI Premium P1 is F64 — which costs roughly what 350 Pro licences cost per month.

So the decision is arithmetic:

| Team size | Usually cheaper |
|---|---|
| Under ~300 users | Per-user (Pro, with PPU for builders) |
| Around 350 users | Break-even against F64 |
| 500+ users | Capacity, almost always |

Two things to check before going the capacity route: the exact F-SKU price varies by region, and capacity is a commitment — you cannot pause it for a quiet month. Get a quote rather than budgeting from a blog post, including this one.

Microsoft's own [feature-by-licence reference](https://learn.microsoft.com/en-us/power-bi/fundamentals/service-features-license-type) lists every capability against each tier; the [Fabric licensing page](https://learn.microsoft.com/en-us/fabric/enterprise/licenses) covers the capacity side.

## The three questions that decide it

Forget the feature matrices. Answer these in order:

**1. Does anyone need to see a report someone else built?**

If no — Free is genuinely enough, and you can stop reading. If yes, those viewers need Pro, PPU, or a capacity. There is no free sharing path.

**2. Does anyone need more than a 1 GB model or eight refreshes a day?**

If no — put everyone on Pro and move on. If yes, put only the people who build those models on PPU. This is a two-person decision, not a company-wide one.

**3. Is the total headcount past roughly 350?**

If yes, get a Fabric capacity quote and compare it properly. Below that, per-user licensing wins almost every time, and the procurement overhead of a capacity is not worth it.

## Four mistakes worth avoiding

**Counting Free users as covered.** They can build, not view. Any cost estimate that assumes otherwise is wrong by the full viewer count.

**Buying PPU for the team to get "premium features".** Most teams need one premium feature for one model. Buy it for the model's owner.

**Assuming Fabric replaces Pro entirely.** Users still need Pro or PPU to *author* in Fabric-backed workspaces. Capacity removes the viewer licence, not the creator one.

**Forgetting the Power BI Embedded option.** If you are putting reports inside your own product, that is a separate capacity-based licence and none of the above applies.

## FAQ

### Q: Can I mix Pro and PPU in the same workspace?

Yes, but there is a catch. A workspace on shared capacity can hold Pro and PPU users together; PPU features only activate on content assigned to a PPU workspace. Mixing works, but planning the workspace layout matters as much as the seat count.

### Q: Do I need Pro to open a Power BI report someone emails me?

To open a `.pbix` file locally, no — Desktop is free. To open a published report in the browser, yes. The distinction trips people up because both actions are described as "opening a report".

### Q: Is Power BI Pro included in Microsoft 365?

It is included in Microsoft 365 E5 and Office 365 E5. It is not included in E3 or Business Standard — those need Pro added separately. Check your tenant's current assignment before buying seats.

### Q: What happens if a Pro licence lapses?

The user keeps access to Desktop and their local files. Published reports stay in the workspace but that user can no longer view them, and any scheduled subscriptions they own stop.

## Related Reading

- [Power BI Service vs Desktop: What Runs Where](/tutorials/power-bi-service-vs-desktop/)
- [Import vs DirectQuery vs Dual vs Direct Lake](/tutorials/directquery-vs-import-mode/)
- [Incremental Refresh: Setup and Gotchas](/tutorials/power-bi-incremental-refresh/)
- [Row-Level Security in Power BI](/tutorials/power-bi-row-level-security/)
- [Power BI Dataflows Explained](/tutorials/power-bi-dataflows/)
- [Tableau vs Power BI: Which Should You Choose](/tutorials/tableau-vs-power-bi/)

---

*Prices are US list from Microsoft's [Power BI pricing page](https://www.microsoft.com/en-us/power-platform/products/power-bi/pricing), checked 4 November 2026. Enterprise agreements and regional pricing differ. Work out your own numbers with the [licence calculator](/tools/license-calculator/).*
