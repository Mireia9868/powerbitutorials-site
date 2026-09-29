#!/usr/bin/env python3
"""
powerbitutorials.com — 每周真实流量复盘引擎
===========================================
数据源（按可用度自动降级）：
  1) 仓库根目录 gsc-ga4-service-account.json 存在 + 库已装（Actions 从 Secrets 生成）  → 直连 GA4 Data API + GSC Search Console API（全自动）
  2) 否则 → 读仓库根目录 gcs-export.csv（手动导出的 GSC 查询表快照）+ 实时 sitemap 文章数
产出：
  review-YYYYMMDD.md（仓库根目录，完整复盘报告）
  末尾打印 ALERT / INFO 行，供自动化邮件发送时区分「周报」与「告警」

口径说明：
  - 真实 UV = GA4 activeUsers（JS 口径，已剔除非 JS 爬虫）。Cloudflare UV 含 ~80% 机器人，仅作趋势参考。
  - 目标：1,000 真人 UV/天（2026-09-24 起 26 周内）。
  - 文章目标：200 篇（30,000 访问/月 ÷ 150 访问/页/月）。当前 51 篇。
"""
import os, json, re, sys, datetime, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT
SA_JSON_NAMES = ("gsc-ga4-service-account.json", "gcs-ga4-service-account.json")
def _resolve_sa_json():
    for n in SA_JSON_NAMES:
        p = OUT / n
        if p.exists() and p.stat().st_size > 0:
            return p
    return OUT / SA_JSON_NAMES[0]
SA_JSON = _resolve_sa_json()
GSC_CSV = OUT / "gcs-export.csv"
GA4_PID_FILE = OUT / "ga4-property-id.txt"
SITE_URL = "https://powerbitutorials.com/"          # GSC 属性（URL 前缀）；若是网域属性改 "sc-domain:powerbitutorials.com"
SITEMAP = "https://powerbitutorials.com/sitemap.xml"

# ---- 目标轨迹参数 ----
TARGET_UV = 1000
BASELINE_UV = 85          # 估算基线；首个周一复盘用 GA4 实测覆盖
TARGET_ARTICLES = 200
START_ARTICLES = 51
START_DATE = datetime.date(2026, 9, 23)
HORIZON_WEEKS = 26

TODAY = datetime.date.today()
WEEK_ID = TODAY.strftime("%Y%m%d")
WEEKS = max(0, (TODAY - START_DATE).days // 7)

def expected_articles(w=WEEKS):
    if w <= 0: return START_ARTICLES
    first4 = min(w, 4) * 7
    rest = max(0, w - 4) * 8
    return START_ARTICLES + first4 + rest

def expected_uv(w=WEEKS):
    if w <= 0: return BASELINE_UV
    if w >= HORIZON_WEEKS: return TARGET_UV
    if w <= 4:  return BASELINE_UV + (150 - BASELINE_UV) * (w / 4)
    if w <= 12: return 150 + (500 - 150) * ((w - 4) / 8)
    if w <= 20: return 500 + (850 - 500) * ((w - 12) / 8)
    return 850 + (1000 - 850) * ((w - 20) / 6)

# ---- 实时文章数（sitemap）----
SNAP_FILE = OUT / ".article-snapshot.json"

def fetch_live_urls():
    """返回文章 URL 集合（排除 /tutorials/ 列表页）。sitemap 无 lastmod，新文章用周快照 diff 判定。"""
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "25", SITEMAP],
                             capture_output=True, text=True).stdout
        locs = re.findall(r"<loc>([^<]+)</loc>", out)
        urls = set()
        for u in locs:
            if "/tutorials/" in u and not u.rstrip("/").endswith("/tutorials"):
                urls.add(u.rstrip("/"))
        return urls
    except Exception:
        return set()

def new_from_snapshot(urls):
    """与上周快照 diff，返回新增 URL；首跑只存快照不告警。"""
    new = []
    if SNAP_FILE.exists():
        try:
            prev = set(json.loads(SNAP_FILE.read_text()))
            new = sorted(urls - prev)
        except Exception:
            pass
    SNAP_FILE.write_text(json.dumps(sorted(urls)))
    return new

# ---- GSC CSV 回退 ----
def read_gcs_csv():
    rows = []
    if not GSC_CSV.exists():
        return rows
    import csv
    with open(GSC_CSV, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

# ---- GA4 + GSC API ----
def load_api():
    """SA 缺失与 GA4 属性缺失分开报，避免把「凭据文件没落地」误诊成「Secret 没填」。"""
    pid = None
    if GA4_PID_FILE.exists():
        pid = GA4_PID_FILE.read_text(encoding="utf-8").strip() or None
    if not (SA_JSON.exists() and SA_JSON.stat().st_size > 0):
        found = [n for n in SA_JSON_NAMES if (OUT / n).exists()]
        return None, pid, f"no-service-account（期望 {SA_JSON_NAMES[0]}，实际存在：{found or '无凭据文件'}）"
    try:
        from google.oauth2 import service_account
        SCOPES = ["https://www.googleapis.com/auth/analytics.readonly",
                  "https://www.googleapis.com/auth/webmasters.readonly"]
        creds = service_account.Credentials.from_service_account_file(str(SA_JSON), scopes=SCOPES)
        return creds, pid, f"ok（{SA_JSON.name}）" if pid else "no-ga4-pid"
    except Exception as e:
        return None, pid, f"load-error:{e}"

def ga4_pull(creds, pid, start, end):
    """返回 dict: activeUsers(区间合计), sessions, screenPageViews, daily(list of (date,au)), top_pages, channels"""
    if not pid:
        return None
    try:
        from google.analytics.data_v1beta import (BetaAnalyticsDataClient, RunReportRequest,
                                                  DateRange, Metric, Dimension)
        client = BetaAnalyticsDataClient.from_service_account_json(str(SA_JSON))
        def run(dims, mets, dr):
            req = RunReportRequest(property=f"properties/{pid}", date_ranges=[dr],
                                   dimensions=[Dimension(name=d) for d in dims],
                                   metrics=[Metric(name=m) for m in mets])
            return client.run_report(req)
        dr = DateRange(start_date=start, end_date=end)
        # 区间合计
        tot = run([], ["activeUsers", "sessions", "screenPageViews"], dr)
        au = sess = pv = 0
        if tot.rows:
            au = int(tot.rows[0].metric_values[0].value)
            sess = int(tot.rows[0].metric_values[1].value)
            pv = int(tot.rows[0].metric_values[2].value)
        # 每日
        daily = run(["date"], ["activeUsers"], dr)
        daily_list = [(r.dimension_values[0].value, int(r.metric_values[0].value)) for r in daily.rows]
        # Top 页面
        tp = run(["pagePath"], ["screenPageViews"], dr)
        top_pages = [(r.dimension_values[0].value, int(r.metric_values[0].value)) for r in tp.rows[:10]]
        # 渠道
        ch = run(["sessionDefaultChannelGroup"], ["activeUsers"], dr)
        channels = [(r.dimension_values[0].value, int(r.metric_values[0].value)) for r in ch.rows[:8]]
        return {"activeUsers": au, "sessions": sess, "screenPageViews": pv,
                "daily": daily_list, "top_pages": top_pages, "channels": channels}
    except Exception as e:
        return {"error": str(e)}

def gsc_pull(creds, start, end, dimension="query", row_limit=25, page_url=None):
    try:
        from googleapiclient.discovery import build
        sc = build("webmasters", "v3", credentials=creds)
        body = {"startDate": start, "endDate": end, "dimensions": [dimension], "rowLimit": row_limit}
        if page_url:
            body["dimensionFilterGroups"] = [{"filters": [{"dimension": "page",
                                                           "expression": page_url}]}]
        resp = sc.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
        return resp.get("rows", [])
    except Exception as e:
        return [{"error": str(e)}]

def daterange(days):
    end = TODAY - datetime.timedelta(days=1)   # 昨天的完整日
    start = end - datetime.timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()

def main():
    alerts = []
    info = []
    lines = []
    A = lines.append
    A(f"# powerbitutorials.com 周复盘 — {WEEK_ID}（第 {WEEKS} 周）")
    A("")
    A(f"> 生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 口径：GA4 真人 UV / GSC 自然搜索")
    A("")

    # 文章数
    urls = fetch_live_urls()
    cnt = len(urls)
    new_urls = new_from_snapshot(urls)
    A(f"## 一、内容资产")
    A(f"- 当前教程文章数（sitemap）：**{cnt}** 篇（目标 {TARGET_ARTICLES} 篇）")
    exp_a = expected_articles()
    A(f"- 本周轨迹预期文章数：**{exp_a}** 篇 ｜ 偏差：{cnt - exp_a:+d} 篇")
    if cnt < exp_a - 3:
        alerts.append(f"[节奏] 文章数 {cnt} 落后轨迹预期 {exp_a}（差 {exp_a - cnt} 篇），发布节奏需加速到 8 篇/周")
    if SNAP_FILE.exists() and not new_urls:
        A(f"- 本周无新增文章（快照 diff 为 0）→ 发布节奏断档，需补发")
        alerts.append("[节奏] 本周快照 diff 为 0，未发布任何新文章，节奏断档")
    A(f"- 本周新增文章（vs 上周快照）：{len(new_urls)} 篇")
    for u in new_urls[:20]:
        A(f"  - {u}")
    A("")

    # 数据源
    creds, pid, status = load_api()
    A(f"## 二、数据源状态")
    A(f"- 服务账号：{status} ｜ GA4 数字属性 ID：{pid or '未配置(Secrets: GA4_PROPERTY_ID)'}")
    A("")

    # GA4 真实 UV
    A(f"## 三、真实流量（GA4 真人 UV）")
    s7, e7 = daterange(7)
    p_s, p_e = daterange(14)
    ga4 = None
    if creds and pid:
        ga4 = ga4_pull(creds, pid, s7, e7)
        if ga4 and "error" not in ga4:
            au7 = ga4["activeUsers"]
            uv_day = round(au7 / 7)
            A(f"- 近 7 天真人活跃用户（activeUsers）：**{au7}**（≈ **{uv_day}/天**）")
            A(f"- 近 7 天 sessions：{ga4['sessions']} ｜ pageViews：{ga4['screenPageViews']}")
            exp_uv = expected_uv()
            A(f"- 本周轨迹预期 UV：**{exp_uv:.0f}/天** ｜ 偏差：{uv_day - exp_uv:+.0f}/天")
            if uv_day < exp_uv * 0.8:
                alerts.append(f"[UV] 真实 UV {uv_day}/天 低于轨迹预期 {exp_uv:.0f}（差 {exp_uv-uv_day:.0f}），检查收录/排名")
            # WoW
            ga4_prev = ga4_pull(creds, pid, p_s, p_e)
            if ga4_prev and "error" not in ga4_prev:
                prev_au = ga4_prev["activeUsers"]
                wow = (au7 - prev_au) / prev_au * 100 if prev_au else 0
                A(f"- WoW（vs 前 7 天 {prev_au}）：**{wow:+.1f}%**")
                if wow <= -20:
                    alerts.append(f"[告警] 真实 UV WoW {wow:.1f}% 跌幅 >20%，排查流量异常/索引丢失")
            A("- Top 页面（pageViews）：")
            for p, v in ga4.get("top_pages", [])[:8]:
                A(f"  - {p}: {v}")
            A("- 渠道（sessionDefaultChannelGroup / activeUsers）：")
            for c, v in ga4.get("channels", [])[:6]:
                A(f"  - {c}: {v}")
        else:
            A(f"- ⚠️ GA4 拉取失败：{ga4.get('error') if ga4 else 'unknown'}")
            info.append("GA4 拉取失败，UV 用估算基线；检查服务账号 GA4 属性 Viewer 权限与 ga4-property-id.txt")
    else:
        A(f"- ⚠️ 未配置服务账号/GA4 属性 ID → 真实 UV 暂用估算基线 **~{BASELINE_UV}/天**（在仓库 Secrets 配好 GSC_SA_JSON + GA4_PROPERTY_ID 后自动接管）")
        A(f"- 本周轨迹预期 UV：{expected_uv():.0f}/天（当前估算 {BASELINE_UV}/天，缺口 {expected_uv()-BASELINE_UV:.0f}/天）")
    A("")

    # GSC 健康
    A(f"## 四、Google 自然搜索健康（GSC）")
    if creds:
        rows28 = gsc_pull(creds, s7, e7, "query", 25)
        if rows28 and "error" not in rows28:
            tot_clicks = sum(int(r["clicks"]) for r in rows28)
            tot_impr = sum(int(r["impressions"]) for r in rows28)
            # 全量合计需单独查（query 维度只给前 25）。用无维度查合计：
            tot = gsc_pull(creds, s7, e7, "date", 1)
            A(f"- 近 7 天 Top 查询（前 25）：clicks 合计 ≈ {tot_clicks}，impressions 合计 ≈ {tot_impr}")
            A("- 高曝光低排名（内容缺口，优先扩写）：")
            gaps = [r for r in rows28 if int(r["impressions"]) > 0 and float(r["position"]) > 15]
            gaps.sort(key=lambda r: int(r["impressions"]), reverse=True)
            for r in gaps[:10]:
                A(f"  - 「{r['keys'][0]}」曝光 {r['impressions']} / 排名 {float(r['position']):.0f} / CTR {float(r['ctr'])*100:.1f}%")
            if gaps:
                info.append(f"本周内容缺口 Top：{gaps[0]['keys'][0]}（曝光 {gaps[0]['impressions']}，排名 {float(gaps[0]['position']):.0f}）— 优先扩写")
            # WoW clicks
            prev = gsc_pull(creds, p_s, p_e, "date", 1)
            # 简化：只报当前
        else:
            A(f"- ⚠️ GSC 拉取失败：{rows28}")
        # 新文章收录检查
        if new_urls:
            A("- 新文章收录检查（GSC 近 28 天 impressions）：")
            s28, e28 = daterange(28)
            not_indexed = []
            for u in new_urls:
                pr = gsc_pull(creds, s28, e28, "page", 1, page_url=u)
                if pr and "error" not in pr:
                    impr = sum(int(x["impressions"]) for x in pr)
                    if impr == 0:
                        not_indexed.append(u)
                        A(f"  - ❌ {u} ：28 天 0 曝光（未收录/未排名）")
                    else:
                        A(f"  - ✅ {u} ：{impr} 曝光")
                else:
                    A(f"  - ⚠️ {u} ：查询失败")
            if not_indexed:
                alerts.append(f"[收录] {len(not_indexed)} 篇新文章 28 天 0 曝光，未收录或未排名：{', '.join(not_indexed[:3])}…")
    else:
        rows = read_gcs_csv()
        if rows:
            A(f"- 手动 GSC 导出 {len(rows)} 条 query（来自仓库内 gsc-export.csv）。Top 曝光低排名查询：")
            parsed = []
            for r in rows:
                try:
                    q = r.get("Top queries") or r.get("Query") or list(r.values())[0]
                    impr = int(r.get("Impressions", r.get("暴露量", 0)) or 0)
                    pos = float(r.get("Position", r.get("位置", 0)) or 0)
                    clk = int(r.get("Clicks", r.get("点击", 0)) or 0)
                    parsed.append((q, impr, pos, clk))
                except Exception:
                    pass
            parsed.sort(key=lambda x: x[1], reverse=True)
            gaps = [p for p in parsed if p[1] > 0 and p[2] > 15]
            for p in gaps[:10]:
                A(f"  - 「{p[0]}」曝光 {p[1]} / 排名 {p[2]:.0f} / 点击 {p[3]}")
            if gaps:
                info.append(f"本周内容缺口 Top：{gaps[0][0]}（曝光 {gaps[0][1]}，排名 {gaps[0][2]:.0f}）— 优先扩写")
        else:
            A("- ⚠️ 无 GSC 数据（既无服务账号也无 gcs-export.csv 快照）")
    A("")

    # 总结与下一步
    A(f"## 五、结论与下一步")
    if alerts:
        A(f"- 🚨 告警 {len(alerts)} 条：")
        for a in alerts:
            A(f"  - {a}")
    else:
        A("- ✅ 本周无越阈值告警")
    A(f"- 轨迹：第 {WEEKS} 周，文章 {cnt}/{TARGET_ARTICLES}，UV ~{BASELINE_UV if not (creds and pid and ga4 and 'error' not in ga4) else round(ga4['activeUsers']/7)}/天（目标 {TARGET_UV}）")
    A("- 内容缺口（下一周选题优先）：见第四节")
    A("- 每日动作：发布当日草稿 + 1 个技术微任务（内链/schema/索引/CTR 轮换）")
    A("")
    A("---")
    A("自动生成 · 由「powerbitutorials 周复盘」自动化触发")

    report = "\n".join(lines)
    out_file = OUT / f"review-{WEEK_ID}.md"
    out_file.write_text(report, encoding="utf-8")
    print(report)
    print("\n===ALERT_SUMMARY===")
    for a in alerts:
        print("ALERT:", a)
    for i in info:
        print("INFO:", i)
    print(f"REPORT_FILE={out_file}")

if __name__ == "__main__":
    main()
