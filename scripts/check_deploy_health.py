#!/usr/bin/env python3
"""部署健康检查：仓库里已有、但线上 sitemap 里还没有的文章 = 未上线。

部署链路正常时，这个数字每天都应归零（Cloudflare Pages 在 push 后数分钟内部署完）。
持续不为零 = 部署中断（Git 集成断开 / 构建失败 / 自动部署被关），
此时继续生成只会让文章无限堆积，线上却一篇都不涨。

用法：
    python scripts/check_deploy_health.py              # 只报告
    python scripts/check_deploy_health.py --fail 4     # 未上线 > 4 篇则 exit 1
    python scripts/check_deploy_health.py --json       # 输出机器可读结果

退出码：
    0  未上线数量在阈值内（或 sitemap 拉取失败，无法判定 —— 不明着报错，避免网络抖动误杀）
    1  未上线数量超过 --fail 阈值
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO / "src" / "content" / "tutorials"
SITEMAP = "https://powerbitutorials.com/sitemap.xml"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")


def fetch_live_slugs():
    """返回线上教程 slug 集合（与仓库文件名 stem 同一口径）；
    拉取失败返回 None（与「真的 0 篇」区分开）。"""
    try:
        out = subprocess.run(
            ["curl", "-sL", "--max-time", "25", "-A", UA, SITEMAP],
            capture_output=True, text=True,
        ).stdout
        slugs = set()
        for u in re.findall(r"<loc>([^<]+)</loc>", out):
            if "/tutorials/" not in u:
                continue
            slug = u.rstrip("/").rsplit("/", 1)[-1]
            if slug and slug != "tutorials":
                slugs.add(slug)
        # curl 遇 403 也返回 exit 0，所以用「解析结果为空」判定失败
        return slugs or None
    except Exception:
        return None


def git_first_seen(slug: str) -> str:
    """文章进入仓库的时间（ISO 日期）；拿不到则返回空串。"""
    f = CONTENT_DIR / f"{slug}.md"
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%ad", "--date=short", "--", str(f)],
            cwd=REPO, capture_output=True, text=True,
        )
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        return lines[-1].strip() if lines else ""
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fail", type=int, default=0,
                    help="未上线篇数超过该值则 exit 1（0 = 永不失败）")
    ap.add_argument("--json", action="store_true", help="输出 JSON，便于其他脚本消费")
    args = ap.parse_args()

    local = {p.stem for p in CONTENT_DIR.glob("*.md")} if CONTENT_DIR.exists() else set()
    live = fetch_live_slugs()

    if not live:
        res = {"ok": None, "reason": "sitemap_unreachable",
               "local": len(local), "pending": [], "pending_count": None}
        if args.json:
            print(json.dumps(res, ensure_ascii=False))
        else:
            print("[WARN] sitemap 拉取失败 —— 无法判定部署状态（不阻断）")
        return 0

    # 防御：两边集合若完全无交集，说明口径不一致（如一边是 URL、一边是 slug），
    # 此时「全部未上线」是假结论，必须报错而不是照常出报告。
    if local and not (local & live):
        msg = (f"口径不一致：仓库 {len(local)} 篇与线上 {len(live)} 篇无任何交集 —— "
               f"多半是某边取的是完整 URL 而另一边取的是 slug，请修脚本后再判定")
        print(f"::error::{msg}")
        if args.json:
            print(json.dumps({"ok": None, "reason": "slug_mismatch", "local": len(local),
                              "live": len(live)}, ensure_ascii=False))
        return 1

    pending = sorted(local - live)
    res = {"ok": not pending, "local": len(local), "live": len(live),
           "pending": pending, "pending_count": len(pending)}

    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"仓库文章 {len(local)} 篇 | 线上 {len(live)} 篇 | 未上线 {len(pending)} 篇")
        if pending:
            print("\n未上线（已入库但未出现在 sitemap）：")
            for s in pending:
                seen = git_first_seen(s)
                print(f"  - {s}" + (f"  （入库 {seen}）" if seen else ""))
            print("\n判定：Cloudflare Pages 部署已中断 —— 现在的生成只会堆积，线上不会涨。")
        else:
            print("\n判定：部署链路正常，仓库与线上一致。")

    # 写进 GitHub Actions 的 run summary
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("### 部署健康检查\n\n")
            fh.write("| 指标 | 值 |\n|---|---|\n")
            fh.write(f"| 仓库文章 | {len(local)} 篇 |\n")
            fh.write(f"| 线上文章 | {len(live)} 篇 |\n")
            fh.write(f"| 未上线 | **{len(pending)} 篇** |\n\n")
            if pending:
                fh.write("未上线清单（入库日期）：\n\n")
                for s in pending:
                    seen = git_first_seen(s)
                    fh.write(f"- `{s}`" + (f" — {seen}\n" if seen else "\n"))

    if pending:
        for s in pending:
            print(f"::warning::未上线：{s}")
        if args.fail and len(pending) >= args.fail:
            print(f"::error::未上线 {len(pending)} 篇（阈值 {args.fail}）—— "
                  f"部署已中断，停止继续生成以免无限堆积")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
