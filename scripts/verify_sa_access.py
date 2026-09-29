#!/usr/bin/env python3
"""
服务账号连通性预检 —— 配 Secret 之前先在本地确认 GA4 / GSC 权限是否给对了。

用法（三种任选）：
  1) python scripts/verify_sa_access.py ~/Downloads/pbt-analytics-xxxx.json 123456789
  2) GSC_SA_JSON="$(cat ~/Downloads/pbt-analytics-xxxx.json)" GA4_PROPERTY_ID=123456789 \
       python scripts/verify_sa_access.py
  3) 把 JSON 放仓库根目录 gsc-ga4-service-account.json、属性 ID 写 ga4-property-id.txt，
     直接 python scripts/verify_sa_access.py

依赖：pip install google-api-python-client google-analytics-data

退出码：0 = GA4 + GSC 至少有一项通；2 = 两项都不通（或凭据本身有问题）
"""
import os, sys, json, glob, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://powerbitutorials.com/"
SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]


def fail(msg, code=1):
    print(msg)
    sys.exit(code)


def load_json_path():
    """按 参数 → 环境变量 → 仓库文件 → Downloads 通配 的顺序找 JSON。"""
    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        return Path(sys.argv[1])
    env_json = os.environ.get("GSC_SA_JSON", "").strip()
    if env_json:
        tmp = Path("/tmp/_sa_preflight.json")
        tmp.write_text(env_json, encoding="utf-8")
        print(f"[i] 使用环境变量 GSC_SA_JSON（已写入 {tmp}）")
        return tmp
    repo_file = REPO_ROOT / "gsc-ga4-service-account.json"
    if repo_file.is_file():
        return repo_file
    hits = sorted(glob.glob(str(Path.home() / "Downloads" / "pbt-analytics*.json")))
    if hits:
        return Path(hits[-1])
    fail("找不到服务账号 JSON。把它作为第一个参数传进来，或放仓库根目录 "
         "gsc-ga4-service-account.json")


def load_property_id():
    for i, a in enumerate(sys.argv[1:], start=1):
        if a.isdigit():
            return a
    pid = os.environ.get("GA4_PROPERTY_ID", "").strip()
    if pid:
        return pid
    f = REPO_ROOT / "ga4-property-id.txt"
    if f.is_file():
        v = f.read_text(encoding="utf-8").strip()
        if v.isdigit():
            return v
    return None


def credentials(sa_path):
    try:
        from google.oauth2 import service_account
    except ImportError:
        fail("[✗] 缺少依赖。先跑：pip install google-api-python-client google-analytics-data", 2)
    info = json.loads(Path(sa_path).read_text(encoding="utf-8"))
    print(f"[i] 服务账号：{info.get('client_email')}")
    print(f"[i] 项目：{info.get('project_id')} ｜ key_id：{info.get('private_key_id')}")
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def check_ga4(creds, pid):
    print("\n=== GA4 ===")
    if not pid:
        print("[–] 跳过：没拿到 GA4 媒体资源 ID（GA4 → 管理 → 媒体资源设置 → 媒体资源 ID，9–10 位数字）")
        return None
    print(f"[i] 媒体资源 ID：{pid}")
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Metric, Dimension,
        )
    except ImportError:
        print("[✗] 缺少 google-analytics-data：pip install google-analytics-data")
        return None
    try:
        client = BetaAnalyticsDataClient(credentials=creds)
        resp = client.run_report(RunReportRequest(
            property=f"properties/{pid}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="yesterday")],
            metrics=[Metric(name="screenPageViews")],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            limit=20,
        ))
        total = sum(int(r.metric_values[0].value) for r in resp.rows)
        print(f"[✓] 可读。近 7 天 pageViews = {total}")
        for r in sorted(resp.rows, key=lambda x: -int(x.metric_values[0].value))[:5]:
            print(f"      {r.dimension_values[0].value:<20} {r.metric_values[0].value}")
        return True
    except Exception as e:
        name = type(e).__name__
        msg = str(e)
        print(f"[✗] {name}: {msg[:200]}")
        if "PERMISSION_DENIED" in msg or "403" in msg:
            print("    → GA4 → 左下「管理」→ 媒体资源列「媒体资源访问管理」→ +「添加用户」")
            print("      邮箱填上面那个服务账号邮箱，角色选「查看者」，保存后重跑本脚本。")
        elif "not found" in msg.lower() or "404" in msg:
            print("    → 属性 ID 可能填错：GA4 →「管理」→「媒体资源设置」里那串 9–10 位数字。")
        return False


def check_gsc(creds):
    print("\n=== Search Console ===")
    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("[✗] 缺少 google-api-python-client：pip install google-api-python-client")
        return None
    try:
        svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
        sites = svc.sites().list().execute().get("siteEntry", [])
        urls = [s.get("siteUrl") for s in sites]
        print(f"[i] 账号下可见属性（{len(urls)} 个）：{urls if urls else '（空）'}")
        end = datetime.date.today() - datetime.timedelta(days=1)
        start = end - datetime.timedelta(days=6)
        resp = svc.searchanalytics().query(
            siteUrl=SITE_URL,
            body={"startDate": start.isoformat(), "endDate": end.isoformat(),
                  "dimensions": ["query"], "rowLimit": 5},
        ).execute()
        rows = resp.get("rows", [])
        clicks = sum(r.get("clicks", 0) for r in rows)
        print(f"[✓] 可读。{start} ~ {end} Top 查询（示例 {len(rows)} 条，clicks 小计 {clicks}）")
        for r in rows:
            print(f"      {r['keys'][0][:44]:<46} clicks={r.get('clicks')} imp={r.get('impressions')} pos={round(r.get('position', 0), 1)}")
        return True
    except Exception as e:
        name = type(e).__name__
        msg = str(e)
        print(f"[✗] {name}: {msg[:200]}")
        if "403" in msg or "permission" in msg.lower() or "forbidden" in msg.lower():
            print("    → GSC（search.google.com/search-console）→「设置」→「用户和权限」→「添加用户」")
            print(f"      邮箱填上面那个服务账号邮箱，权限选「受限」，保存后重跑本脚本。")
        return False


def main():
    sa = load_json_path()
    try:
        creds = credentials(sa)
    except Exception as e:
        fail(f"[✗] 凭据文件无法使用：{type(e).__name__}: {e}", 2)
    r_ga4 = check_ga4(creds, load_property_id())
    r_gsc = check_gsc(creds)
    print("\n=== 结论 ===")
    ok = [n for n, r in (("GA4", r_ga4), ("GSC", r_gsc)) if r]
    bad = [n for n, r in (("GA4", r_ga4), ("GSC", r_gsc)) if r is False]
    if ok:
        print(f"[✓] 通了：{', '.join(ok)}" + (f"；仍不通：{', '.join(bad)}" if bad else ""))
        print("    → 把 JSON 全文填进 GitHub Secret GSC_SA_JSON、属性 ID 填 GA4_PROPERTY_ID 即可。")
        sys.exit(0)
    print(f"[✗] 都不通：{', '.join(bad) or '未配置'}")
    print("    → 按上面各段的提示补权限；确认两个 API 都已在 GCP「API 和服务 → 库」里启用。")
    sys.exit(2)


if __name__ == "__main__":
    main()
