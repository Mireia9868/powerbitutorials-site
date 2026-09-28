#!/usr/bin/env python3
"""
统一投递：把报告文件发送到飞书自定义机器人 和/或 Resend 邮件。
云端版，不依赖 WorkBuddy。通道按 secret 是否存在自动启用，任一失败不影响其他。
用法：python3 deliver.py <report.md> "<标题>"
"""
import os, sys, json, urllib.request, pathlib

def feishu(title, md):
    wh = os.environ.get("FEISHU_WEBHOOK")
    if not wh:
        print("[feishu:SKIP no webhook]")
        return
    import time, base64, hashlib, hmac
    ts = str(int(time.time()))
    body = {"msg_type":"interactive","content":{
        "config":{"wide_screen_mode":True},
        "header":{"template":"blue","title":{"tag":"plain_text","content":title[:50]}},
        "elements":[{"tag":"markdown","content":md[:12000]}]}}
    secret = os.environ.get("FEISHU_SECRET")
    if secret:
        s = f"{ts}\n{secret}"
        h = hmac.new(secret.encode(), s.encode(), digestmod=hashlib.sha256).digest()
        body["timestamp"] = ts; body["sign"] = base64.b64encode(h).decode()
    data = json.dumps(body).encode()
    req = urllib.request.Request(wh, data=data, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[feishu] {r.status}: {r.read().decode()[:120]}")
    except Exception as e:
        print(f"[feishu:ERR] {e}")

def resend(title, md):
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        print("[resend:SKIP no key]")
        return
    frm = os.environ.get("RESEND_FROM", "reports@powerbitutorials.com")
    to = os.environ.get("REPORT_TO", "mireia9868@gmail.com")
    payload = {"from": frm, "to": [t.strip() for t in to.split(",")],
               "subject": title, "text": md[:18000]}
    data = json.dumps(payload).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=data,
        headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[resend] {r.status}: {r.read().decode()[:120]}")
    except Exception as e:
        print(f"[resend:ERR] {e}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    title = sys.argv[2] if len(sys.argv) > 2 else "powerbitutorials 通知"
    md = pathlib.Path(path).read_text() if path and pathlib.Path(path).exists() else title
    feishu(title, md)
    resend(title, md)
