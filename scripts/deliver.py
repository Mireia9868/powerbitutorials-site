#!/usr/bin/env python3
"""
统一投递（云端版，不依赖 WorkBuddy）。

通道优先级：
  1) SMTP 邮件（默认 163 邮箱 smtp.163.com:465 SSL）— 主通道
  2) 飞书自定义机器人 webhook           — 备通道
  3) Resend API                        — 备通道
任一失败不影响其他，全部失败才退出码 1。

用法：python3 deliver.py <report.md> "<标题>"
环境变量：
  SMTP_HOST(默认 smtp.163.com) SMTP_PORT(465) SMTP_SSL(true)
  SMTP_USER(登录账号) SMTP_PASS(授权码) SMTP_FROM(默认=SMTP_USER)
  REPORT_TO(默认=SMTP_USER，逗号分隔多收件人)
"""
import os, sys, re, json, smtplib, pathlib, email.policy, urllib.request
from email.message import EmailMessage

# ---------- markdown -> html（轻量，够读报告即可） ----------
def md_to_html(md):
    import html as _h
    out, in_table, list_tag, in_code = [], False, None, False

    def close_blocks():
        nonlocal in_table, list_tag
        if in_table:
            out.append("</table>"); in_table = False
        if list_tag:
            out.append(f"</{list_tag}>"); list_tag = None

    def inline(t):
        t = _h.escape(t, quote=False)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
        return t

    for raw in md.split("\n"):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            close_blocks()
            out.append("<pre><code>" if not in_code else "</code></pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(_h.escape(raw)); continue
        if re.match(r"^\s*\|.*\|\s*$", line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c != "") and cells:
                continue  # 分隔行
            if not in_table:
                out.append('<table border="1" cellpadding="6" cellspacing="0" '
                           'style="border-collapse:collapse;font-size:14px;margin:8px 0">')
                in_table = True
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        close_blocks()
        if not line.strip():
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lv = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>"); continue
        if re.match(r"^\s*[-*]\s+", line):
            if list_tag != "ul":
                close_blocks(); out.append("<ul>"); list_tag = "ul"
            out.append("<li>" + inline(re.sub(r"^\s*[-*]\s+", "", line)) + "</li>"); continue
        if re.match(r"^\s*\d+[.)]\s+", line):
            if list_tag != "ol":
                close_blocks(); out.append("<ol>"); list_tag = "ol"
            out.append("<li>" + inline(re.sub(r"^\s*\d+[.)]\s+", "", line)) + "</li>"); continue
        if re.fullmatch(r"-{3,}", line.strip()):
            out.append("<hr>"); continue
        out.append(f"<p>{inline(line)}</p>")
    close_blocks()
    if in_code:
        out.append("</code></pre>")
    return ('<html><body style="font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\','
            'Roboto,Arial,sans-serif;font-size:15px;line-height:1.65;color:#1f2328;'
            'max-width:820px;margin:0 auto;padding:8px">' + "\n".join(out) + "</body></html>")

# ---------- 通道 1：SMTP 邮件（主） ----------
def smtp_email(title, md):
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")
    if not (user and pwd):
        print("[smtp:SKIP] SMTP_USER/SMTP_PASS 未配置")
        return False
    host = os.environ.get("SMTP_HOST") or "smtp.163.com"
    port = int(os.environ.get("SMTP_PORT") or 465)
    use_ssl = (os.environ.get("SMTP_SSL") or "true").lower() != "false"
    frm = os.environ.get("SMTP_FROM") or user
    to = [a.strip() for a in (os.environ.get("REPORT_TO") or user).split(",") if a.strip()]

    msg = EmailMessage(policy=email.policy.SMTP)
    msg["Subject"] = title
    msg["From"] = frm
    msg["To"] = ", ".join(to)
    msg.set_content(md, subtype="plain", charset="utf-8")
    msg.add_alternative(md_to_html(md), subtype="html", charset="utf-8")
    last = None
    for attempt in (1, 2):
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(host, port, timeout=30) as s:
                    s.login(user, pwd)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(host, port, timeout=30) as s:
                    s.ehlo(); s.starttls(); s.login(user, pwd); s.send_message(msg)
            print(f"[smtp] OK -> {', '.join(to)} via {host}:{port}")
            return True
        except Exception as e:
            last = e
            print(f"[smtp:ERR attempt{attempt}] {type(e).__name__}: {e}")
            if attempt == 1:
                import time as _t; _t.sleep(5)
    return False

# ---------- 通道 2：飞书机器人 ----------
def feishu(title, md):
    wh = os.environ.get("FEISHU_WEBHOOK")
    if not wh:
        print("[feishu:SKIP] no webhook")
        return False
    import time, base64, hashlib, hmac
    ts = str(int(time.time()))
    body = {"msg_type": "interactive", "content": {
        "config": {"wide_screen_mode": True},
        "header": {"template": "blue", "title": {"tag": "plain_text", "content": title[:50]}},
        "elements": [{"tag": "markdown", "content": md[:12000]}]}}
    secret = os.environ.get("FEISHU_SECRET")
    if secret:
        s = f"{ts}\n{secret}"
        h = hmac.new(secret.encode(), s.encode(), digestmod=hashlib.sha256).digest()
        body["timestamp"] = ts; body["sign"] = base64.b64encode(h).decode()
    req = urllib.request.Request(wh, data=json.dumps(body).encode(),
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[feishu] {r.status}: {r.read().decode()[:120]}")
        return True
    except Exception as e:
        print(f"[feishu:ERR] {e}")
        return False

# ---------- 通道 3：Resend ----------
def resend(title, md):
    key = os.environ.get("RESEND_API_KEY")
    if not key:
        print("[resend:SKIP] no key")
        return False
    payload = {"from": os.environ.get("RESEND_FROM", "reports@powerbitutorials.com"),
               "to": [t.strip() for t in (os.environ.get("REPORT_TO") or "").split(",") if t.strip()],
               "subject": title, "text": md[:18000]}
    req = urllib.request.Request("https://api.resend.com/emails",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[resend] {r.status}: {r.read().decode()[:120]}")
        return True
    except Exception as e:
        print(f"[resend:ERR] {e}")
        return False

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    title = sys.argv[2] if len(sys.argv) > 2 else "powerbitutorials 通知"
    if path and pathlib.Path(path).exists():
        md = pathlib.Path(path).read_text()
    elif path:
        print(f"[warn] report file not found: {path} (若上游步骤失败则为空)")
        md = f"{title}\n\n(报告文件 {path} 未生成，请查看 Actions 日志)"
    else:
        md = title
    results = [smtp_email(title, md), feishu(title, md), resend(title, md)]
    print(f"[deliver] channels ok={sum(1 for r in results if r)}/{len(results)}")
    sys.exit(0 if any(results) else 1)
