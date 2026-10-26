#!/usr/bin/env python3
"""
SEO 自动驾驶 —— 把 GSC 数据变成「这周该改哪几篇」的清单。

为什么需要：现有 daily_report / weekly_review 只「报告」数据，不产出动作。
选题一直是人工从 GSC 里看（topic_queue.json 的 signal 字段就是人抄进去的）。
这个脚本把中间那一步自动化：拉数 → 分类 → 输出可执行清单 → 可选的写回队列。

四个分类，对应四种完全不同的动作：

  quick_win    排名 5–20，展示够     → 改现有文章（加段落、补内链），最快见效
  ctr_gap      排名 ≤10，CTR 很低     → 改 title / meta description，不动正文
  rising       展示环比大涨           → 加码同类选题，趁势扩写
  zero_click   有展示、排名很差       → 判断值不值得做新文章，或直接放弃

用法：
  python scripts/seo_autopilot.py                    # 28 天，输出报告
  python scripts/seo_autopilot.py --days 90          # 换窗口
  python scripts/seo_autopilot.py --apply            # 同时把候选写进 topic_queue.json
  python scripts/seo_autopilot.py --offline          # 无凭据时读 gcs-export.csv

依赖：pip install google-api-python-client google-auth

关于 Google Trends（重要）
  pytrends 已于 2025 年归档，且长期返回 429。任何照着旧教程写的采集都会卡死。
  对这个站来说，Trends 的价值本来也有限：Power BI 是垂直 B2B 工具，
  搜索量曲线平稳，真正的「趋势」来自 Microsoft 每月发版，不是大众热度。
  所以这里不接 Trends，改抓官方 release notes（--release-notes）。
  如果你确实要 Trends 数据，用 rimulabs-trends 或 trendreq（pytrends 的维护中替代品），
  并接受它们随时可能被限流。
"""
import argparse
import csv
import datetime
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "reports"
QUEUE = REPO / "scripts" / "topic_queue.json"
SITE_URL = "https://powerbitutorials.com/"
SA_NAMES = ("gsc-ga4-service-account.json", "gcs-ga4-service-account.json")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# ---- 分类阈值（可调，改这里就能改判据）----
# 默认值按「小站」设定的：本站 28 天总展示约 2,360，最大单词展示约 55。
# 用大站的标准（imp >= 50 / >= 100）会一条都命中不了，报告全是空的。
# 站长大后把这些值往上调，否则会淹没在低样本噪音里。
QUICK_WIN = {"pos_min": 5, "pos_max": 30, "imp_min": 8}
CTR_GAP = {"pos_max": 15, "ctr_max": 0.02, "imp_min": 15}
RISING = {"growth_min": 0.5, "imp_min": 5}
ZERO_CLICK = {"imp_min": 15, "ctr_max": 0.01}


def find_sa():
    for name in SA_NAMES:
        p = REPO / name
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def gsc_pull(creds, start, end, dimensions, row_limit=500):
    from googleapiclient.discovery import build
    sc = build("webmasters", "v3", credentials=creds, cache_discovery=False)
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    resp = sc.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return resp.get("rows", [])


def rows_to_dicts(rows, dims):
    out = []
    for r in rows:
        keys = r.get("keys", [])
        d = {f"d{i}": (keys[i] if i < len(keys) else "") for i in range(len(dims))}
        d.update({
            "clicks": r.get("clicks", 0),
            "impressions": r.get("impressions", 0),
            "ctr": r.get("ctr", 0.0),
            "position": r.get("position", 0.0),
        })
        out.append(d)
    return out


def load_offline():
    """无凭据时读仓库里的 gcs-export.csv（Top queries 快照）。"""
    p = REPO / "gcs-export.csv"
    if not p.exists():
        print("[!] 没有凭据也没有 gcs-export.csv，无法运行")
        sys.exit(2)
    rows = []
    with open(p, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "d0": r["Top queries"],
                "clicks": int(float(r["Clicks"] or 0)),
                "impressions": int(float(r["Impressions"] or 0)),
                "ctr": float((r["CTR"] or "0").replace("%", "")) / 100,
                "position": float(r["Position"] or 0),
            })
    return rows


def classify(cur, prev, pages):
    """返回四组分类结果。prev 用于环比，pages 用于判断承接页。"""
    prev_map = {r["d0"]: r for r in prev}
    page_by_query = {}
    for p in pages:
        pass  # query+page 联合维度在下面单独拉，见 main

    out = {"quick_win": [], "ctr_gap": [], "rising": [], "zero_click": []}

    for r in cur:
        q = r["d0"]
        pos, imp, ctr, clicks = r["position"], r["impressions"], r["ctr"], r["clicks"]

        # 1) 快赢：排名 5–20，已经有展示，差临门一脚
        if QUICK_WIN["pos_min"] <= pos <= QUICK_WIN["pos_max"] and imp >= QUICK_WIN["imp_min"]:
            out["quick_win"].append(r)

        # 2) CTR 缺口：排名已经很靠前，但没人点 → title/description 问题
        if pos <= CTR_GAP["pos_max"] and ctr < CTR_GAP["ctr_max"] and imp >= CTR_GAP["imp_min"]:
            out["ctr_gap"].append(r)

        # 3) 上升：展示环比涨 50% 以上，值得加码
        old = prev_map.get(q)
        if old and old["impressions"] >= RISING["imp_min"]:
            growth = (imp - old["impressions"]) / max(old["impressions"], 1)
            if growth >= RISING["growth_min"]:
                r = dict(r, growth=growth, prev_imp=old["impressions"])
                out["rising"].append(r)

        # 4) 有展示但几乎零点击：判断值不值得投入
        if imp >= ZERO_CLICK["imp_min"] and ctr < ZERO_CLICK["ctr_max"] and pos > 20:
            out["zero_click"].append(r)

    for k in out:
        out[k].sort(key=lambda r: (-r["impressions"], r["position"]))
    return out


def fmt_table(rows, extra=None):
    if not rows:
        return "_（本期没有命中）_\n"
    head = "| 查询 | 展示 | 点击 | CTR | 排名 |" + (" 环比 |" if extra else "")
    sep = "|---|---|---|---|---|" + ("---|" if extra else "")
    lines = [head, sep]
    for r in rows[:15]:
        line = (f"| {r['d0']} | {r['impressions']:,} | {r['clicks']} | "
                f"{r['ctr']*100:.1f}% | {r['position']:.1f} |")
        if extra:
            line += f" +{r.get('growth', 0)*100:.0f}% |"
        lines.append(line)
    return "\n".join(lines) + "\n"


def fetch_release_notes():
    """Power BI 官方更新日志 —— 对内容站来说这才是真正的「趋势」。"""
    import urllib.request
    urls = [
        "https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-latest-update",
    ]
    heads = []
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                html = r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"[!] release notes 抓取失败：{e}")
            continue
        for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html, re.S):
            t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            t = re.sub(r"\s+", " ", t)
            if t and len(t) < 90:
                heads.append(t)
    return heads[:20]


def write_queue_candidates(result):
    """把 quick_win / rising 的查询追加到 topic_queue 的候选区，不覆盖已有条目。"""
    if not QUEUE.exists():
        print("[!] topic_queue.json 不存在，跳过")
        return 0
    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    existing = {item.get("slug") for item in q}
    added = 0

    for r in result["quick_win"][:10]:
        slug = re.sub(r"[^a-z0-9]+", "-", r["d0"].lower()).strip("-")
        if not slug or slug in existing:
            continue
        q.append({
            "slug": f"{slug}-guide",
            "title": r["d0"].title(),
            "category": "dax",
            "difficulty": "Intermediate",
            "tags": ["auto-candidate"],
            "signal": (f"GSC quick win: {r['impressions']} impr / pos {r['position']:.0f} / "
                       f"ctr {r['ctr']*100:.1f}% — 先考虑扩写现有承接页，再决定是否新写"),
        })
        existing.add(slug)
        added += 1

    if added:
        QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--apply", action="store_true", help="把候选写回 topic_queue.json")
    ap.add_argument("--offline", action="store_true", help="用 gcs-export.csv 而不是 API")
    ap.add_argument("--release-notes", action="store_true", help="附带抓取 Power BI 更新日志")
    args = ap.parse_args()

    today = datetime.date.today()
    end = today - datetime.timedelta(days=2)   # GSC 有 2 天延迟
    start = end - datetime.timedelta(days=args.days)
    p_end = start - datetime.timedelta(days=1)
    p_start = p_end - datetime.timedelta(days=args.days)

    if args.offline:
        print("[i] offline 模式：使用 gcs-export.csv 快照，无环比")
        cur = load_offline()
        prev = []
        pages = []
        pages_cur = []
    else:
        from google.oauth2 import service_account
        sa = find_sa()
        if not sa:
            print("[!] 找不到服务账号 JSON。用 --offline 或先配置 gsc-ga4-service-account.json")
            sys.exit(2)
        creds = service_account.Credentials.from_service_account_file(str(sa), scopes=SCOPES)
        print(f"[i] GSC {start} → {end}（对比 {p_start} → {p_end}）")
        cur = rows_to_dicts(gsc_pull(creds, start, end, ["query"]), ["query"])
        prev = rows_to_dicts(gsc_pull(creds, p_start, p_end, ["query"]), ["query"])
        pages = rows_to_dicts(gsc_pull(creds, start, end, ["page"], 200), ["page"])
        pages_cur = pages

    result = classify(cur, prev, pages)

    OUT.mkdir(exist_ok=True)
    md = []
    A = md.append
    A(f"# SEO 动作清单 — {today.isoformat()}\n")
    A(f"窗口：{start} → {end}（{args.days} 天）｜查询数 {len(cur)}\n")

    A("## 一、快赢：排名 5–20，改现有文章就能进前 5\n")
    A("动作：给承接页补 200–300 词、加 2–3 条内链、补一张截图。**不要新写文章。**\n")
    A(fmt_table(result["quick_win"]))

    A("\n## 二、CTR 缺口：排名够好但没人点\n")
    A("动作：只改 title 和 meta description。正文不动。\n")
    A(fmt_table(result["ctr_gap"]))

    A("\n## 三、上升：展示环比上涨\n")
    A("动作：趁势扩写这篇，或补一个同主题的相邻选题。\n")
    A(fmt_table(result["rising"], extra=True))

    A("\n## 四、有展示、零点击、排名很差\n")
    A("动作：先判断值不值得做。同类站已有强对手时，放弃比硬做便宜。\n")
    A(fmt_table(result["zero_click"]))

    if args.release_notes:
        A("\n## 五、Power BI 官方更新（内容机会）\n")
        heads = fetch_release_notes()
        if heads:
            for h in heads:
                A(f"- {h}")
        else:
            A("_抓取失败或页面结构变化_")

    A("\n---\n")
    A("下一步：把「快赢」的 3 个词挑出来，本周改对应的 3 篇。不要一次改 15 篇。\n")

    report = OUT / f"seo-actions-{today.isoformat()}.md"
    report.write_text("\n".join(md), encoding="utf-8")

    (OUT / "seo-candidates.json").write_text(
        json.dumps({k: v[:40] for k, v in result.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"[✓] {report}")
    print(f"    快赢 {len(result['quick_win'])} ｜ CTR缺口 {len(result['ctr_gap'])} ｜ "
          f"上升 {len(result['rising'])} ｜ 零点击 {len(result['zero_click'])}")

    if args.apply:
        n = write_queue_candidates(result)
        print(f"[✓] 写入 topic_queue.json 候选 {n} 条")


if __name__ == "__main__":
    main()
