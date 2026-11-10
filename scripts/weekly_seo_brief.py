#!/usr/bin/env python3
"""
每周一的内容简报 —— 回答「这周该动哪三件事」。

不依赖任何外部 API，全部从仓库自身算出来，所以它永远能跑：
  · 内链健康（孤儿页、自链、指向不存在页面的链接）
  · 内容质量的四个硬指标分布（标题长度、描述长度、FAQ、引用）
  · 选题队列里判定为 go 的前几个
  · 三条排序后的建议

GSC 的「快赢词」由 seo_autopilot.py 单独产出（需要服务账号），
这个脚本不重复那部分工作，只保证即使在没凭据的环境里也有输出。

用法：
  python scripts/weekly_seo_brief.py
  python scripts/weekly_seo_brief.py --md out.md
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "src" / "content" / "tutorials"
QUEUE = REPO / "scripts" / "topic_queue.json"


def frontmatter(text):
    m = re.match(r"^---(.*?)---", text, re.S)
    return m.group(1) if m else ""


def field(fm, name):
    m = re.search(rf'^{name}:\s*"?(.*?)"?\s*$', fm, re.M)
    return m.group(1) if m else ""


def audit():
    docs = {}
    for p in sorted(CONTENT.glob("*.md")):
        t = p.read_text(encoding="utf-8")
        fm = frontmatter(t)
        docs[p.stem] = {
            "title": field(fm, "title"),
            "desc": field(fm, "description"),
            "body": t,
            "category": field(fm, "category"),
        }

    # 内链
    inbound = Counter()
    dead = Counter()
    for slug, d in docs.items():
        for link in set(re.findall(r"\]\(/tutorials/([a-z0-9\-]+)/?\)", d["body"])):
            if link not in docs:
                dead[link] += 1
            elif link != slug:
                inbound[link] += 1

    orphans = [s for s in docs if inbound[s] == 0]
    self_links = [s for s, d in docs.items() if f"/tutorials/{s}/" in d["body"]
                  and re.search(rf"^- \[[^\]]*\]\(/tutorials/{re.escape(s)}/\)", d["body"], re.M)]

    # 质量
    long_title = [(len(d["title"]), s) for s, d in docs.items() if len(d["title"]) > 60]
    short_desc = [(len(d["desc"]), s) for s, d in docs.items() if len(d["desc"]) < 150]
    long_desc = [(len(d["desc"]), s) for s, d in docs.items() if len(d["desc"]) > 162]
    no_faq = [s for s, d in docs.items()
              if not re.search(r"^(?:###\s+Q[:：]|\*\*Q[:：])", d["body"], re.M)]
    no_cite = [s for s, d in docs.items()
               if "learn.microsoft.com" not in d["body"] and "sqlbi.com" not in d["body"]
               and not s.startswith("de-")]

    return dict(docs=docs, inbound=inbound, dead=dead, orphans=orphans,
                self_links=self_links, long_title=long_title, short_desc=short_desc,
                long_desc=long_desc, no_faq=no_faq, no_cite=no_cite)


def queue_go(limit=5):
    if not QUEUE.exists():
        return []
    existing = {p.stem for p in CONTENT.glob("*.md")}
    items = json.loads(QUEUE.read_text(encoding="utf-8"))
    go = [t for t in items
          if t.get("research", {}).get("verdict") == "go"
          and t.get("research", {}).get("score", 0) >= 5
          and t["slug"] not in existing]
    go.sort(key=lambda t: -t["research"]["score"])
    return go[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", default="")
    args = ap.parse_args()

    a = audit()
    n = len(a["docs"])
    out = []
    A = out.append

    A(f"# 内容简报")
    A("")
    A(f"文章 {n} 篇｜入链中位数 "
      f"{sorted(a['inbound'].values())[n // 2] if n else 0}"
      f"｜零入链 {len(a['orphans'])} 篇")
    A("")

    # 1. 硬问题
    A("## 一、必须修的")
    A("")
    hard = []
    if a["dead"]:
        for slug, c in a["dead"].most_common(5):
            hard.append(f"指向不存在页面的链接：`/tutorials/{slug}/`（{c} 处）")
    if a["orphans"]:
        hard.append(f"零入链文章 {len(a['orphans'])} 篇：{', '.join(a['orphans'][:5])}")
    if a["long_title"]:
        worst = sorted(a["long_title"], reverse=True)[:3]
        hard.append("标题超 60 字符：" + "；".join(f"{s}({l})" for l, s in worst))
    if a["long_desc"]:
        hard.append(f"描述超 162 字符 {len(a['long_desc'])} 篇")
    if not hard:
        hard.append("无。死链、孤儿页、超长标题/描述均为 0。")
    for h in hard:
        A(f"- {h}")
    A("")

    # 2. 质量分布
    A("## 二、质量分布")
    A("")
    A("| 指标 | 达标 | 未达标 |")
    A("|---|---|---|")
    A(f"| 标题 ≤60 字符 | {n - len(a['long_title'])} | {len(a['long_title'])} |")
    A(f"| 描述 150–162 | {n - len(a['short_desc']) - len(a['long_desc'])} | "
      f"{len(a['short_desc'])} 偏短 / {len(a['long_desc'])} 偏长 |")
    A(f"| 有 FAQ | {n - len(a['no_faq'])} | {len(a['no_faq'])} |")
    A(f"| 有权威引用 | {n - len(a['no_cite'])} | {len(a['no_cite'])} |")
    A("")

    # 3. 选题
    go = queue_go()
    A("## 三、队列里可写的")
    A("")
    if go:
        for t in go:
            r = t["research"]
            A(f"- **[{r['score']}/9] {t['title']}**")
            A(f"  - 角度：{r.get('angle', '—')}")
            if r.get("rewrite_of"):
                A(f"  - 扩写 `{r['rewrite_of']}`，不是新写")
    else:
        A("_队列为空或没有 go 状态的选题，跑 `research_report.py --pending` 补充。_")
    A("")

    # 4. 建议
    A("## 四、本周三个动作")
    A("")
    picks = []
    if a["dead"]:
        picks.append("修掉上面列出的死链——它们在把权重丢进黑洞")
    if a["orphans"]:
        picks.append(f"给零入链的 {len(a['orphans'])} 篇各补 2 条内链")
    if a["long_title"]:
        picks.append(f"缩短 {len(a['long_title'])} 个超长标题（Bing 会截断）")
    if a["no_faq"]:
        picks.append(f"给 {len(a['no_faq'])} 篇补 FAQ，从曝光最高的开始")
    if go:
        picks.append(f"写 1 篇：{go[0]['title']}")
    for i, p in enumerate(picks[:3], 1):
        A(f"{i}. {p}")
    if not picks:
        A("1. 没有硬问题，按队列写内容即可。")
    A("")
    A("---")
    A("_GSC 的快赢词看 `reports/seo-actions-*.md`（需要服务账号，单独跑 seo_autopilot）。_")

    text = "\n".join(out)
    if args.md:
        Path(args.md).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
