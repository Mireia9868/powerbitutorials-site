#!/usr/bin/env python3
"""
选题研究状态汇总 —— 配合《选题研究工作流》使用。

工作流里判断「写不写」靠人/agent 查 SERP，这个脚本只做两件机械的事：
  1. 列出哪些选题还没做过研究（避免凭感觉开写）
  2. 把已研究的按分数排序（决定本周先写哪个）

研究结论存在 topic_queue.json 每个条目的 research 字段里：
  {
    "date": "2026-10-27",
    "serp": {"official": 0, "farm": 2, "forum": 1, "competitor": 0, "video": 0},
    "score": 6,
    "verdict": "go",
    "angle": "症状→原因→修复→验证",
    "rewrite_of": "dax-troubleshooting-guide"
  }

用法：
  python scripts/research_report.py            # 全部状态
  python scripts/research_report.py --pending  # 只看待研究
  python scripts/research_report.py --go       # 只看判定为 go 的
"""
import argparse
import json
from pathlib import Path

QUEUE = Path(__file__).resolve().parent.parent / "scripts" / "topic_queue.json"
GO_THRESHOLD = 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending", action="store_true", help="只列未研究的")
    ap.add_argument("--go", action="store_true", help="只列 score>=5 的")
    args = ap.parse_args()

    if not QUEUE.exists():
        print(f"[!] 找不到 {QUEUE}")
        return

    items = json.loads(QUEUE.read_text(encoding="utf-8"))
    pending = [t for t in items if not t.get("research")]
    done = [t for t in items if t.get("research")]

    if args.pending:
        if not pending:
            print("全部选题都已研究。")
            return
        print(f"待研究 {len(pending)} 个：\n")
        for t in pending:
            print(f"  {t['slug']}")
            print(f"     {t['title']}")
            if t.get("signal"):
                print(f"     信号：{t['signal']}")
        print("\n跑法：web_search 查前 10 构成 → 套评分卡 → 写回 research 字段")
        return

    if args.go:
        go = [t for t in done if t["research"].get("score", 0) >= GO_THRESHOLD
              and t["research"].get("verdict") == "go"]
        go.sort(key=lambda t: -t["research"]["score"])
        if not go:
            print(f"没有判定为 go 且分数 >= {GO_THRESHOLD} 的选题。")
            return
        print(f"可写选题 {len(go)} 个（按分数降序）：\n")
        for t in go:
            r = t["research"]
            print(f"  [{r['score']}/9] {t['slug']}")
            print(f"         角度：{r.get('angle', '—')}")
            if r.get("rewrite_of"):
                print(f"         扩写：{r['rewrite_of']}（不是新写）")
        return

    # 默认：概览
    print(f"选题总数 {len(items)}｜已研究 {len(done)}｜待研究 {len(pending)}\n")

    if done:
        print("已研究（按分数）：")
        for t in sorted(done, key=lambda x: -x["research"].get("score", 0))[:15]:
            r = t["research"]
            flag = "✅" if r.get("verdict") == "go" else "❌"
            print(f"  {flag} [{r.get('score', 0)}/9] {t['slug']}")

    if pending:
        print(f"\n待研究（前 10 个）：")
        for t in pending[:10]:
            print(f"     {t['slug']}")


if __name__ == "__main__":
    main()
