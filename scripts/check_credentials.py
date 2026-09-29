#!/usr/bin/env python3
"""CI 凭据落地自检（纯本地、不联网、不打印任何密钥内容）
=====================================================================
为什么需要它：报表脚本在找不到凭据时会「静默降级」成估算口径并照样发邮件，
把「配置坏了」伪装成「数据就是低」。这个自检把这类问题在跑报表前就暴露出来。

判定规则：
  - Secret 有值 + 文件不可用  → 报错退出（exit 1），这是配置 bug
  - Secret 本就为空            → 仅打印提示（exit 0），属于预期降级

用法：
  HAS_SA=true HAS_PID=true python scripts/check_credentials.py
环境变量：
  HAS_SA / HAS_PID   由 workflow 用 ${{ secrets.X != '' }} 传入（只回 true/false，不泄漏明文）
  GITHUB_STEP_SUMMARY 存在时顺带写一份表格摘要
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# 以 gsc- 为规范名；兼容历史误拼 gcs-（transposition bug），避免再次静默降级
SA_CANDIDATES = ("gsc-ga4-service-account.json", "gcs-ga4-service-account.json")
REQUIRED_KEYS = ("client_email", "private_key", "project_id")
PID_FILE = ROOT / "ga4-property-id.txt"


def find_sa():
    for name in SA_CANDIDATES:
        p = ROOT / name
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def main():
    has_sa = os.environ.get("HAS_SA", "false").strip().lower() == "true"
    has_pid = os.environ.get("HAS_PID", "false").strip().lower() == "true"
    errors = []

    sa = find_sa()
    if has_sa:
        if sa is None:
            errors.append(
                f"Secret GSC_SA_JSON 有值，但 {' / '.join(SA_CANDIDATES)} 都没落地 —— materialize 步骤异常")
        else:
            try:
                data = json.loads(sa.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(
                    f"{sa.name} 不是合法 JSON（{type(e).__name__}: {e}）"
                    " —— 常见原因：粘贴时丢了最外层花括号，或把换行写成了字面 \\n")
            else:
                missing = [k for k in REQUIRED_KEYS if not data.get(k)]
                if missing:
                    errors.append(f"{sa.name} 缺少关键字段 {missing} —— 可能粘错了文件（需服务账号密钥 JSON）")
                else:
                    print(f"[OK] SA JSON -> {data['client_email']} (project {data['project_id']})")
    else:
        print("[WARN] Secret GSC_SA_JSON 为空 -> 报表降级为非实时口径")

    pid = None
    pid_landed = PID_FILE.exists() and PID_FILE.stat().st_size > 0
    if has_pid:
        if not pid_landed:
            errors.append("Secret GA4_PROPERTY_ID 有值，但 ga4-property-id.txt 未落地")
        else:
            pid = PID_FILE.read_text(encoding="utf-8").strip()
            if not pid.isdigit():
                errors.append(f"GA4_PROPERTY_ID 不是纯数字：{pid!r} —— 应填媒体资源 ID（如 548614588），不要带 properties/ 前缀或空格")
            else:
                print(f"[OK] GA4 property id -> {pid}")
    else:
        print("[WARN] Secret GA4_PROPERTY_ID 为空 -> 报表降级为非实时口径")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        Path(summary_path).write_text(
            "\n".join([
                "### 凭据自检", "",
                "| 项 | Secret 有值 | 文件落地 |",
                "|---|---|---|",
                f"| GSC_SA_JSON | {has_sa} | {sa.name if sa else 'no'} |",
                f"| GA4_PROPERTY_ID | {has_pid} | {'yes' if pid_landed else 'no'} |",
                "",
            ]), encoding="utf-8")

    for e in errors:
        print(f"::error::{e}")
    if errors:
        return 1
    if has_sa and has_pid:
        print("[OK] 凭据自检通过（GA4 + GSC 可直连）")
    else:
        print("[OK] 凭据自检通过，但处于降级模式 —— 报表将使用静态快照/估算口径")
    return 0


if __name__ == "__main__":
    sys.exit(main())
