#!/usr/bin/env python3
"""
IndexNow 推送 —— 让 Bing / Yandex / Naver 在几小时内收录新文章。

为什么需要：这个站的实际流量来自 Bing（872 用户）而不是 Google（17）。
Bing 的收录速度直接决定新文章的见效时间，而等自然抓取通常要 1–3 周。

IndexNow 是 Bing 主导的协议，一次 POST 就能通知所有参与引擎。
Google 不参与，所以这不会影响 Google 的抓取节奏。

用法：
  python scripts/indexnow.py --days 3      # 推最近 3 天发布/更新的（CI 默认）
  python scripts/indexnow.py --all         # 全量推一次（首次用，别常跑）
  python scripts/indexnow.py --url https://powerbitutorials.com/tutorials/x/

注意：
  · key 文件必须能从公网访问：https://powerbitutorials.com/<key>.txt
    它在 public/ 下，构建后会出现在站点根目录。
  · 只推新增或实质更新的 URL。全量反复推送会被引擎当噪音。
"""
import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "src" / "content" / "tutorials"
SITE = "https://powerbitutorials.com"
HOST = "powerbitutorials.com"
KEY = "pbt2026indexnow7f3a9c2e5b8d1a4f6c0e3b7d"
ENDPOINT = "https://api.indexnow.org/indexnow"


def article_urls(days=None):
    """返回 (url, date) 列表；days=None 表示全部。"""
    today = datetime.date.today()
    out = []
    for p in sorted(CONTENT.glob("*.md")):
        if p.stem.startswith("de-"):
            continue  # 德语区 noindex，不推送
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---(.*?)---", text, re.S)
        if not m:
            continue
        fm = m.group(1)
        if re.search(r"^draft:\s*true", fm, re.M):
            continue
        pub = re.search(r"^pubDate:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        upd = re.search(r"^updatedDate:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        dates = [d.group(1) for d in (pub, upd) if d]
        if not dates:
            continue
        latest = max(datetime.date.fromisoformat(d) for d in dates)
        if days is not None:
            if (today - latest).days > days:
                continue
        out.append((f"{SITE}/tutorials/{p.stem}/", latest))
    return out


def push(urls):
    if not urls:
        print("[i] 没有符合条件的 URL，跳过")
        return 0
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"{SITE}/{KEY}.txt",
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        print(f"[✗] IndexNow {e.code}: {body}")
        print("    422 = key 文件访问不到；403 = key 不匹配；429 = 推太频繁")
        return 1
    except Exception as e:
        print(f"[✗] 请求失败: {e}")
        return 1

    print(f"[✓] 推送 {len(urls)} 条，HTTP {code}")
    for u in urls[:10]:
        print(f"    {u}")
    if len(urls) > 10:
        print(f"    ... 还有 {len(urls) - 10} 条")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.url:
        urls = args.url
    elif args.all:
        urls = [u for u, _ in article_urls(None)]
    else:
        urls = [u for u, _ in article_urls(args.days if args.days else 3)]

    if args.dry_run:
        print(f"[dry-run] 会推送 {len(urls)} 条：")
        for u in urls[:15]:
            print("   ", u)
        return 0

    return push(urls)


if __name__ == "__main__":
    sys.exit(main())
