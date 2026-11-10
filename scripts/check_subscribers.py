#!/usr/bin/env python3
"""
每天检查 Buttondown 有没有新订阅者。

为什么单独做一个：邮箱列表是这个站唯一真正属于自己的资产，但它增长得很慢
（一个月可能只有几十人），所以不会有人天天登录后台看。没有通知，就等于
「有人订阅了但没人知道」——而第一个订阅者往往是验证整条链路是否通的关键。

设计：
  · 拉最近的订阅者列表，按 creation_date 筛出最近 26 小时（覆盖时区误差）
  · 有新增 → 输出摘要，workflow 决定是否发邮件
  · 没有新增 → 静默，只写进 job summary，不打扰

环境变量：
  BUTTONDOWN_API_KEY   在 Buttondown → Settings → API keys 生成

用法：
  python scripts/check_subscribers.py
  python scripts/check_subscribers.py --hours 48
"""
import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.buttondown.email/v1/subscribers"
KEY = os.environ.get("BUTTONDOWN_API_KEY", "").strip()


def fetch(limit=100):
    req = urllib.request.Request(
        f"{API}?limit={limit}",
        headers={"Authorization": f"Token {KEY}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def parse_date(value):
    """Buttondown 返回 ISO 8601，可能带 Z。"""
    if not value:
        return None
    v = value.replace("Z", "+00:00")
    try:
        dt = datetime.datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=26)
    args = ap.parse_args()

    if not KEY:
        print("::error::BUTTONDOWN_API_KEY 未配置。Buttondown → Settings → API keys，存到仓库 Secrets。")
        return 2

    try:
        data = fetch()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200]
        print(f"::error::Buttondown API {e.code}: {body}")
        if e.code == 401:
            print("::error::key 无效或已被轮换。去 Settings → API keys 生成新的，更新仓库 Secrets 里的 BUTTONDOWN_API_KEY。")
        return 1
    except Exception as e:
        print(f"::error::请求失败：{e}")
        return 1

    subs = data.get("results", [])
    total = data.get("count", len(subs))
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=args.hours)

    fresh = []
    for s in subs:
        created = parse_date(s.get("creation_date"))
        if created and created >= cutoff:
            fresh.append((created, s.get("email_address", "?"),
                          s.get("type", s.get("status", ""))))

    fresh.sort(reverse=True)

    print(f"## 订阅者检查 — {datetime.date.today().isoformat()}")
    print()
    print(f"- 历史累计：**{total}** 人")
    print(f"- 最近 {args.hours} 小时新增：**{len(fresh)}** 人")

    if fresh:
        print()
        print("| 时间 (UTC) | 邮箱 | 状态 |")
        print("|---|---|---|")
        for created, email, kind in fresh:
            print(f"| {created.strftime('%Y-%m-%d %H:%M')} | {email} | {kind} |")
        # 给 workflow 用的标记：有新增才发通知
        print()
        print("NEW_SUBSCRIBERS=1")
    else:
        print()
        print("_没有新订阅。_")
        print("NEW_SUBSCRIBERS=0")

    # 顺带提示容量：免费档 100 人封顶
    if total >= 80:
        print()
        print(f"::warning::已用 {total}/100 免费额度，接近上限时要决定升级还是迁移。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
