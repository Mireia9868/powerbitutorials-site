#!/usr/bin/env python3
"""
IndexNow 推送 —— 让 Bing / Yandex / Naver 在几小时内收录新文章。

为什么需要：这个站的实际流量来自 Bing（872 用户）而不是 Google（17）。
Bing 的收录速度直接决定新文章的见效时间，而等自然抓取通常要 1–3 周。

IndexNow 是 Bing 主导的协议，一次 POST 就能通知所有参与引擎。
Google 不参与，所以这不会影响 Google 的抓取节奏。

用法：
  python scripts/indexnow.py --changed     # 推这次 push 改动过的文章（CI 默认）
  python scripts/indexnow.py --days 3      # 推最近 3 天发布/更新的（定时兜底）
  python scripts/indexnow.py --all         # 全量推一次（首次用，别常跑）
  python scripts/indexnow.py --url https://powerbitutorials.com/tutorials/x/

为什么默认用 git diff 而不是 frontmatter 日期：
  2026-11-12 到 11-20 之间，CI 每天跑但推送 0 条 —— 因为脚本只看 pubDate/updatedDate，
  而改标题、改描述、加内链都不改这两个字段（甚至提交说明里明确写了"No pubDate /
  updatedDate changes"）。结果 78 篇文章从建站起一次都没提交过，Bing 后台开始报
  "Some important pages weren't submitted via IndexNow"。
  git diff 记录的是"这次真的改了什么"，才是推送的正确口径。

注意：
  · key 文件必须能从公网访问：https://powerbitutorials.com/<key>.txt
    它在 public/ 下，构建后会出现在站点根目录。
  · 只推新增或实质更新的 URL。全量反复推送会被引擎当噪音。
  · Cloudflare Pages 的部署比 GitHub Actions 慢，key 文件早就上线了不代表新文章已经
    可访问。推之前要确认 URL 真的返回 200，否则引擎抓到的是一批 404。
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT = REPO / "src" / "content" / "tutorials"
SITE = "https://powerbitutorials.com"
HOST = "powerbitutorials.com"
KEY = "pbt2026indexnow7f3a9c2e5b8d1a4f6c0e3b7d"
ENDPOINT = "https://api.indexnow.org/indexnow"

# Cloudflare 会拦掉 urllib 的默认 UA（403），探测存活必须带浏览器 UA。
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


def parse_frontmatter(path):
    """返回 frontmatter 文本；不是合法文章返回 None。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---(.*?)---", text, re.S)
    return m.group(1) if m else None


def is_publishable(path):
    if path.suffix != ".md":
        return False
    if path.stem.startswith("de-"):
        return False  # 德语区 noindex，不推送
    fm = parse_frontmatter(path)
    if fm is None:
        return False
    if re.search(r"^draft:\s*true", fm, re.M):
        return False
    return True


def url_for(path):
    return f"{SITE}/tutorials/{path.stem}/"


def article_urls(days=None):
    """返回 (url, date) 列表；days=None 表示全部。"""
    today = datetime.date.today()
    out = []
    for p in sorted(CONTENT.glob("*.md")):
        if not is_publishable(p):
            continue
        fm = parse_frontmatter(p)
        pub = re.search(r"^pubDate:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        upd = re.search(r"^updatedDate:\s*(\d{4}-\d{2}-\d{2})", fm, re.M)
        dates = [d.group(1) for d in (pub, upd) if d]
        if not dates:
            continue
        latest = max(datetime.date.fromisoformat(d) for d in dates)
        if days is not None and (today - latest).days > days:
            continue
        out.append((url_for(p), latest))
    return out


def changed_urls(base="HEAD^"):
    """这次 push 里改动过的文章 URL。git 不可用（浅克隆/首次提交）时返回 None。"""
    try:
        res = subprocess.run(
            ["git", "-C", str(REPO), "diff", "--name-only", base, "HEAD", "--", "src/content/tutorials"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    urls = []
    for line in res.stdout.splitlines():
        p = REPO / line.strip()
        # 删除的文章、草稿、德语页不推
        if not p.is_file() or not is_publishable(p):
            continue
        u = url_for(p)
        if u not in urls:
            urls.append(u)
    return urls


def wait_until_live(urls, timeout=240, interval=15):
    """等这些 URL 真的返回 200；Cloudflare Pages 部署通常 30–120 秒。"""
    pending = list(urls)
    deadline = time.monotonic() + timeout
    while pending and time.monotonic() < deadline:
        still = []
        for u in pending:
            try:
                req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": BROWSER_UA})
                with urllib.request.urlopen(req, timeout=20) as r:
                    if r.status != 200:
                        still.append(u)
            except Exception:
                still.append(u)
        pending = still
        if pending:
            print(f"[i] 还有 {len(pending)} 条未上线，{(deadline - time.monotonic()):.0f}s 后重试")
            time.sleep(interval)
    if pending:
        print(f"[!] {len(pending)} 条在 {timeout}s 内仍未上线，本次不推送：")
        for u in pending[:10]:
            print(f"    {u}")
        return False
    return True


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
    ap.add_argument("--changed", action="store_true", help="推 git diff 改动过的文章（CI 默认）")
    ap.add_argument("--base", default="HEAD^", help="--changed 的比较基线，默认 HEAD^")
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-wait", action="store_true", help="跳过上线探测，直接推")
    ap.add_argument("--wait", type=int, default=240, help="上线探测最长等待秒数，默认 240")
    args = ap.parse_args()

    if args.url:
        urls = args.url
    elif args.all:
        urls = [u for u, _ in article_urls(None)]
    elif args.changed:
        urls = changed_urls(args.base)
        if urls is None:
            print("[i] 拿不到 git diff（浅克隆或首次提交），退回 --days 3")
            urls = [u for u, _ in article_urls(3)]
    else:
        urls = [u for u, _ in article_urls(args.days if args.days else 3)]

    if args.dry_run:
        print(f"[dry-run] 会推送 {len(urls)} 条：")
        for u in urls[:15]:
            print("   ", u)
        return 0

    if urls and not args.no_wait and not wait_until_live(urls, timeout=args.wait):
        return 1

    return push(urls)


if __name__ == "__main__":
    sys.exit(main())
