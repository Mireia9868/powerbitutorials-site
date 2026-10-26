#!/usr/bin/env python3
"""
每周一发送 newsletter —— 从 newsletters/ 队列取最早一篇，推到 Buttondown。

为什么需要：Buttondown 免费档没有 Automations（+$29/月），但又不想靠人记着
每周一发。这个脚本把「按时发」交给 GitHub Actions，把「写什么」留给人。

设计原则：内容必须人工写。自动生成的邮件发给订阅者，比不发更糟 ——
读者是主动留了邮箱的，一次敷衍就会退订。

用法：
  python scripts/send_newsletter.py --list          # 看队列
  python scripts/send_newsletter.py                 # 建草稿（安全默认）
  python scripts/send_newsletter.py --send          # 真的发出去
  python scripts/send_newsletter.py --only 2026-11-02.md

环境变量：
  BUTTONDOWN_API_KEY   在 Buttondown → Settings → API keys 生成

内容文件格式（newsletters/YYYY-MM-DD.md）：
  ---
  subject: "The fiscal year trap in TOTALYTD"
  preheader: "Why your YTD is six months off"
  ---

  正文 Markdown...

发出去之后文件会移到 newsletters/sent/，避免重复发送。
"""
import argparse
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
QUEUE = REPO / "newsletters"
SENT = QUEUE / "sent"
API = "https://api.buttondown.email/v1/emails"


def api_key():
    k = os.environ.get("BUTTONDOWN_API_KEY", "").strip()
    if not k:
        print("[!] 缺少 BUTTONDOWN_API_KEY。")
        print("    Buttondown → Settings → API keys → 生成后存到 GitHub Secrets 或本地环境变量。")
        sys.exit(2)
    return k


def parse(path):
    """返回 (subject, preheader, body)；frontmatter 缺失时用文件名兜底。"""
    raw = path.read_text(encoding="utf-8")
    subject = preheader = None
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            m = re.search(r'^subject:\s*"?(.*?)"?\s*$', fm, re.M)
            subject = m.group(1) if m else None
            m = re.search(r'^preheader:\s*"?(.*?)"?\s*$', fm, re.M)
            preheader = m.group(1) if m else None
    if not subject:
        subject = path.stem
    body = body.strip()
    # 不要把 preheader 拼进正文 —— 它会原样出现在邮件第一行。
    # Buttondown 用正文开头做预览文字，所以正文第一句本身就该是钩子。
    # preheader 只用于日志和人工检查。
    return subject, body, preheader


def post(payload, key, endpoint=API):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        endpoint, data=data, method="POST",
        headers={"Authorization": f"Token {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit(f"[✗] Buttondown API {e.code}: {detail}")
    except Exception as e:
        raise SystemExit(f"[✗] 请求失败: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="只看队列不发")
    ap.add_argument("--send", action="store_true", help="真的发送（默认只建草稿）")
    ap.add_argument("--only", default="", help="指定某个文件")
    args = ap.parse_args()

    if not QUEUE.exists():
        print("[!] newsletters/ 目录不存在")
        sys.exit(1)
    queue = sorted(p for p in QUEUE.glob("*.md"))

    if args.list:
        if not queue:
            print("队列为空。下次要发的内容放到 newsletters/YYYY-MM-DD.md")
            return
        for p in queue:
            subj, _, _ = parse(p)
            print(f"  {p.name}  →  {subj}")
        return

    if not queue:
        print("[i] 队列为空，本周不发。这不是错误 —— 没内容就不该发。")
        return

    target = None
    if args.only:
        target = QUEUE / args.only
        if not target.exists():
            print(f"[!] 找不到 {args.only}")
            sys.exit(1)
    else:
        target = queue[0]

    subject, body, preheader = parse(target)
    key = api_key()

    words = len(re.findall(r"\b\w+\b", body))
    print(f"[i] 待发：{target.name}")
    print(f"    subject: {subject}")
    print(f"    正文 {words} 词")
    if preheader:
        print(f"    preheader: {preheader}")

    status = "about_to_send" if args.send else "draft"
    resp = post({"subject": subject, "body": body, "status": status}, key)
    email_id = resp.get("id", "?")

    if args.send:
        print(f"[✓] 已提交发送，id={email_id}")
        SENT.mkdir(exist_ok=True)
        shutil.move(str(target), str(SENT / target.name))
        print(f"[i] 已归档到 newsletters/sent/{target.name} —— 记得 commit 这次移动")
    else:
        print(f"[✓] 已创建草稿，id={email_id}")
        print("    去 Buttondown 后台看一眼预览，确认没问题后用 --send 发，")
        print("    或者在 Actions 里手动触发并勾选 send。")


if __name__ == "__main__":
    main()
