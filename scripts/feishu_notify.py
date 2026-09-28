#!/usr/bin/env python3
"""
飞书自定义机器人通知（云端版，不依赖 WorkBuddy 飞书 connector）。
用法：echo "<markdown 内容>" | python3 feishu_notify.py "标题"
环境变量：
  FEISHU_WEBHOOK  - 自定义机器人 webhook URL
  FEISHU_SECRET   - 机器人签名密钥（启用了"签名校验"时必填）
内容通过 interactive 卡片的 markdown 元素发送。若未配置 webhook，打印到 stdout 并退出 0。
"""
import os, sys, time, base64, hashlib, hmac, json, urllib.request

def sign(secret, timestamp):
    s = f"{timestamp}\n{secret}"
    h = hmac.new(secret.encode(), s.encode(), digestmod=hashlib.sha256).digest()
    return base64.b64encode(h).decode()

def send(title, md):
    wh = os.environ.get("FEISHU_WEBHOOK")
    if not wh:
        print(f"[feishu:SKIP no webhook] {title}\n{md}")
        return
    ts = str(int(time.time()))
    body = {"msg_type": "interactive", "content": {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"tag": "plain_text", "content": title[:50]}},
        "elements": [{"tag": "markdown", "content": md[:12000]}]
    }}
    secret = os.environ.get("FEISHU_SECRET")
    if secret:
        body["timestamp"] = ts
        body["sign"] = sign(secret, ts)
    data = json.dumps(body).encode()
    req = urllib.request.Request(wh, data=data, headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[feishu] status {r.status}: {r.read().decode()[:120]}")
    except Exception as e:
        print(f"[feishu:ERR] {e}")

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "powerbitutorials 通知"
    md = sys.stdin.read()
    send(title, md)
