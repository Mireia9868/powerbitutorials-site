#!/usr/bin/env python3
"""One-shot revision of the 3 striking-distance P0 articles + CF cluster nav.
Safe: asserts on exact anchors so nothing is silently mis-applied. No images.
"""
import os
BASE = os.path.join(os.path.dirname(__file__), "..", "src", "content", "tutorials")

def p(f): return os.path.join(BASE, f)
def read(f):
    with open(p(f), encoding="utf-8") as fh: return fh.read()
def write(f, s):
    with open(p(f), "w", encoding="utf-8") as fh: fh.write(s)

# ---------- 1) copy-conditional-formatting-power-bi ----------
f = "copy-conditional-formatting-power-bi.md"
s = read(f)
assert "pubDate: 2026-08-28\n" in s
s = s.replace("pubDate: 2026-08-28\n", "pubDate: 2026-08-28\nupdatedDate: 2026-10-12\n", 1)

faq_extra = '''
**How do I copy conditional formatting from one column to another?**
Duplicate the visual (Method 3) and change only the field feeding the new column — the rules travel with the copy. For logic-based rules, point both visuals at the same color measure (Method 1) so the rule applies to any column automatically, with no per-column setup.

**Can I copy conditional formatting to another visual or another column?**
Within one report, duplication carries the rules to the new visual. To apply the same rule to a different column, the cleanest path is a Field-value color measure that any visual can reference. There is no "paste formatting" button across unrelated visuals.

**Why does my copied formatting look different on the new visual?**
Two causes: the color measure's granularity doesn't match the new visual's grain, or you duplicated a visual whose rules were hand-built and now drift from the original. Measure-based formatting stays identical everywhere; hand-built rules don't.

'''
assert "## What's next\n" in s
s = s.replace("## What's next\n", faq_extra + "## What's next\n", 1)

old_next = '''- [Conditional Formatting in Power BI: A Complete Guide](/tutorials/conditional-formatting-power-bi/) — the measure and rule patterns this article builds on.
- [Conditional Formatting for Charts, Bar Charts & Gauges](/tutorials/conditional-formatting-charts-power-bi/) — applying the same reuse principles to visual elements.
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/) — keep color consistent across the whole report, not just formatted cells.'''
new_next = '''- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-complete-guide/) — the full cluster, from rules to reuse.
- [Conditional Formatting in Power BI: A Complete Guide](/tutorials/conditional-formatting-power-bi/) — the measure and rule patterns this article builds on.
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/) — drive colors from a DAX measure instead of fixed rules.
- [Conditional Formatting for Charts, Bar Charts & Gauges](/tutorials/conditional-formatting-charts-power-bi/) — gauge, bar, and line chart guides.
- [Power BI Dashboard Design Principles](/tutorials/power-bi-dashboard-design-principles/) — keep color consistent across the whole report, not just formatted cells.'''
assert old_next in s, "copy-CF What's-next anchor not found"
s = s.replace(old_next, new_next, 1)
write(f, s)
print("updated:", f)

# ---------- 2) relationships-one-to-many-many-to-many ----------
f = "relationships-one-to-many-many-to-many.md"
s = read(f)
assert "pubDate: 2026-07-11\n" in s
s = s.replace("pubDate: 2026-07-11\n", "pubDate: 2026-07-11\nupdatedDate: 2026-10-12\n", 1)

decision = '''
## One-to-many or many-to-many: which should you use?

| Use one-to-many when… | Use many-to-many (or a bridge) when… |
|---|---|
| One side of the join has unique keys | Both tables have duplicate values in the join column |
| You're building a star schema | You have a genuine shared-dimension or multi-attribute problem |
| Filter flow should be unambiguous | A single active path can't connect the two tables |
| The model is large or production-bound | The dataset is small, or it's a quick prototype |

Rule of thumb: default to one-to-many. Reach for a bridge table (not native many-to-many) in any production model where the join is truly many-to-many — it keeps filter direction predictable and performs better.

## FAQ

**When should I use many-to-many in Power BI?**
Only when both tables genuinely have duplicate values in the join column and no single shared dimension connects them — for example, a customer belonging to multiple segments. Prefer a bridge table in production; native many-to-many is fine for prototypes.

**Can I have two active relationships between the same tables?**
No — only one active relationship can exist between two tables. For a second path (such as `OrderDate` vs `ShipDate` on a date table), mark it inactive and activate it in a measure with `USERELATIONSHIP`.

**Does many-to-many hurt performance?**
It can, especially on large models, because the engine resolves the ambiguous path at query time. A bridge table with two one-to-many relationships is usually faster and easier to reason about.

'''
assert "## Summary\n" in s
s = s.replace("## Summary\n", decision + "## Summary\n", 1)

rel_links = '''
## Related

- [Star Schema Design in Power BI](/tutorials/data-modeling-star-schema/) — the pattern one-to-many relationships are built on.
- [Role-Playing Dimensions in Power BI](/tutorials/role-playing-dimensions/) — handling multiple date relationships with `USERELATIONSHIP`.
- [Bidirectional Filtering in Power BI](/tutorials/bidirectional-filtering-guide/) — when (and when not) to open filter flow both ways.
'''
assert s.rstrip().endswith("don't assume the model view tells the full story.") or "## Summary" in s
s = s.rstrip() + "\n" + rel_links
write(f, s + "\n")
print("updated:", f)

# ---------- 3) power-query-conditional-columns ----------
f = "power-query-conditional-columns.md"
s = read(f)
assert "pubDate: 2026-07-23\n" in s
s = s.replace("pubDate: 2026-07-23\n", "pubDate: 2026-07-23\nupdatedDate: 2026-10-12\n", 1)

faq_extra2 = '''
**What is the Power Query "if then else" syntax?**
In a Custom Column it's `if [Score] > 90 then "A" else "B"`. The keywords are lowercase and case-sensitive. The Conditional Column dialog builds the same logic visually — its If / Then / Else fields map directly to `if` / `then` / `else` in M.

**How do I handle nulls in a conditional column?**
Use `if [Discount] = null then 0 else [Discount]`, or the shorter coalesce form `[Discount] ?? 0`. In the Conditional Column dialog, choose the "equals" operator and type `null` (without quotes) to compare against a blank.

'''
assert "## What's next\n" in s
s = s.replace("## What's next\n", faq_extra2 + "## What's next\n", 1)
write(f, s)
print("updated:", f)

# ---------- 4) CF cluster nav appended to the 6 other CF sub-articles ----------
cf_others = [
    "conditional-formatting-power-bi.md",
    "conditional-formatting-based-on-measure.md",
    "conditional-formatting-charts-power-bi.md",
    "gauge-conditional-formatting.md",
    "bar-chart-conditional-formatting.md",
    "line-chart-conditional-formatting.md",
]
nav = '''
## More conditional formatting guides

- [Power BI Conditional Formatting: The Complete Guide](/tutorials/conditional-formatting-complete-guide/)
- [Conditional Formatting in Power BI](/tutorials/conditional-formatting-power-bi/)
- [Conditional Formatting Based on a Measure](/tutorials/conditional-formatting-based-on-measure/)
- [Conditional Formatting for Charts](/tutorials/conditional-formatting-charts-power-bi/)
- [Copy Conditional Formatting Between Visuals](/tutorials/copy-conditional-formatting-power-bi/)
- [Gauge Conditional Formatting](/tutorials/gauge-conditional-formatting/)
- [Bar Chart Conditional Formatting](/tutorials/bar-chart-conditional-formatting/)
- [Line Chart Conditional Formatting](/tutorials/line-chart-conditional-formatting/)
'''
for cf in cf_others:
    s = read(cf)
    if "<!-- CF-CLUSTER-NAV -->" in s:
        print("skip (already patched):", cf); continue
    s = s.rstrip() + "\n" + "<!-- CF-CLUSTER-NAV -->" + nav
    write(cf, s + "\n")
    print("patched cluster nav:", cf)

print("DONE")
