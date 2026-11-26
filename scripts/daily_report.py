#!/usr/bin/env python3
"""
powerbitutorials.com — 每日真实流量达成汇报引擎（前 30 天试点用）
==================================================================
数据源（按可用度自动降级，与 weekly_review.py 同源）：
  1) 仓库根目录 gsc-ga4-service-account.json + ga4-property-id.txt 存在（Actions 由 Secrets 生成）→ 直连 GA4 + GSC（全自动）
  2) 否则 → CSV 回退 + sitemap 文章数 + 本地生产进度（仍可汇报「内容引擎」达成情况）

汇报口径（对齐用户要求）：
  - 浏览量（pageViews）：GA4 screenPageViews，昨日完整日
  - 环比增长：DoD（昨日 vs 前日）+ WoW（昨日 vs 7 天前同日）
  - 增长来源：① GA4 渠道构成（sessionDefaultChannelGroup，近 7 天）② GSC 上升查询（近 7 天 vs 前 7 天）
产出：
  daily-YYYYMMDD.md（仓库根目录，邮件正文）
  末尾打印 ALERT / INFO 行，供自动化区分「日报」与「告警」
"""
import os, json, re, datetime, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT
DRAFTS = OUT / "powerbitutorials-drafts"
CONTENT_DIR = REPO_ROOT / "src" / "content" / "tutorials"
# 凭据文件名以 gsc- 为准；同时接受历史误拼 gcs-，避免命名漂移再次造成静默降级
SA_JSON_NAMES = ("gsc-ga4-service-account.json", "gcs-ga4-service-account.json")
def _resolve_sa_json():
    for n in SA_JSON_NAMES:
        p = OUT / n
        if p.exists() and p.stat().st_size > 0:
            return p
    return OUT / SA_JSON_NAMES[0]
SA_JSON = _resolve_sa_json()
GA4_PID_FILE = OUT / "ga4-property-id.txt"
GSC_CSV = OUT / "gcs-export.csv"
SITE_URL = "https://powerbitutorials.com/"
SITEMAP = "https://powerbitutorials.com/sitemap.xml"

TARGET_UV = 1000
TODAY = datetime.date.today()
Y = TODAY - datetime.timedelta(days=1)          # 昨日（完整日）
D2 = TODAY - datetime.timedelta(days=2)         # 前日（DoD 基准）
W7 = TODAY - datetime.timedelta(days=8)         # 7 天前同日（WoW 基准）
GSC_END = Y.isoformat()
GSC_S7 = (Y - datetime.timedelta(days=6)).isoformat()
GSC_P7 = (Y - datetime.timedelta(days=13)).isoformat()

def pct(n, d):
    return (n - d) / d * 100 if d else 0.0

# ---- 文章数 + 生产进度 ----
def fetch_live_urls():
    """已上线教程 URL 集合。拉取失败返回 None。
    必须区分「拉取失败」与「0 篇」——否则一次网络抖动就会被报成"线上 0 篇文章"。"""
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", SITEMAP],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return None
        urls = {u.rstrip("/") for u in re.findall(r"<loc>([^<]+)</loc>", r.stdout)
                if "/tutorials/" in u and not u.rstrip("/").endswith("/tutorials")}
        return urls or None
    except Exception:
        return None

def production_progress():
    """本地内容引擎达成：草稿数、待发布数、日历发布日志条数。"""
    draft_md = 0
    pending = 0
    if DRAFTS.exists():
        for f in DRAFTS.glob("*.md"):
            if f.name in ("00-content-calendar.md", "REVIEW-PROMPT.md"):
                continue
            if f.name.endswith(".review.md"):
                continue
            draft_md += 1
        # 待发布：有草稿但发布日志未回填 24h PV（粗略：日历里「待发布」字样计数）
    log_lines = 0
    cal = DRAFTS / "00-content-calendar.md"
    if cal.exists():
        for ln in cal.read_text(encoding="utf-8").splitlines():
            if "待发布" in ln or "已发布" in ln or "草稿已生成" in ln:
                log_lines += 1
    return draft_md, log_lines

# ---- API ----
def load_api():
    """返回 (可用标志, GA4 属性 ID, 状态描述)。
    注意：SA 缺失与 GA4 属性缺失是两件事，必须分别报出，否则会把「凭据文件没落地」误诊为「Secret 没填」。"""
    sa_ok = SA_JSON.exists() and SA_JSON.stat().st_size > 0
    pid = None
    if GA4_PID_FILE.exists():
        pid = GA4_PID_FILE.read_text(encoding="utf-8").strip() or None
    if sa_ok and pid:
        return True, pid, f"ok（{SA_JSON.name}）"
    if not sa_ok:
        found = [n for n in SA_JSON_NAMES if (OUT / n).exists()]
        return None, pid, f"no-service-account（期望 {SA_JSON_NAMES[0]}，实际存在：{found or '无凭据文件'}）"
    return "creds", None, "no-ga4-pid"

def ga4_day(pid, start, end, dims, mets):
    from google.analytics.data_v1beta import (BetaAnalyticsDataClient, RunReportRequest,
                                              DateRange, Metric, Dimension)
    client = BetaAnalyticsDataClient.from_service_account_json(str(SA_JSON))
    req = RunReportRequest(property=f"properties/{pid}", date_ranges=[DateRange(start_date=start, end_date=end)],
                           dimensions=[Dimension(name=d) for d in dims],
                           metrics=[Metric(name=m) for m in mets])
    return client.run_report(req)

def ga4_pull(pid):
    res = {}
    try:
        # 单日 pageViews / activeUsers
        for label, s, e in [("y", Y.isoformat(), Y.isoformat()),
                            ("d2", D2.isoformat(), D2.isoformat()),
                            ("w7", W7.isoformat(), W7.isoformat())]:
            r = ga4_day(pid, s, e, [], ["screenPageViews", "activeUsers"])
            if r.rows:
                res[label] = (int(r.rows[0].metric_values[0].value),
                              int(r.rows[0].metric_values[1].value))
        # 渠道（近 7 天）
        ch = ga4_day(pid, GSC_S7, GSC_END, ["sessionDefaultChannelGroup"], ["activeUsers"])
        res["channels"] = [(row.dimension_values[0].value, int(row.metric_values[0].value))
                          for row in ch.rows[:8]]
        # Top 页面（近 7 天）
        tp = ga4_day(pid, GSC_S7, GSC_END, ["pagePath"], ["screenPageViews"])
        res["top_pages"] = [(row.dimension_values[0].value, int(row.metric_values[0].value))
                           for row in tp.rows[:8]]
        return res
    except Exception as e:
        return {"error": str(e)}

# ---- 转化漏斗（近 28 天滚动，对齐用户导出的 GA4 事件口径）----
# 环节定义：名称 / 事件名（用 totalUsers 去重人数）/ 或页面路径前缀
# 说明：漏斗用「用户数」而非「事件数」，否则同一人多次滚动会被重复计入。
FUNNEL_DAYS = 28
FUNNEL_START = (Y - datetime.timedelta(days=FUNNEL_DAYS - 1)).isoformat()
FUNNEL_END = Y.isoformat()
FUNNEL_EVENTS = [
    ("到达站点", "page_view"),
    ("产生互动", "user_engagement"),
    ("实质滚动", "scroll_depth"),
    ("探索工具/模板", None),          # 用页面路径判定，见下
    ("模板页访问", None),
    # 旧事件 purchase_intent 于 2026-11-25 改名 checkout_click 且去掉了
    # value/currency —— 它只是点击，不是成交，绝不能当转化终点。
    ("结账点击(非成交)", "checkout_click"),
    ("真实成交(purchase)", "purchase"),   # 仅 Gumroad webhook 服务端回传
    ("订阅提交", "form_submit"),
]
# 路径判定必须互斥，否则 /templates/finance-starter 会被两个环节重复计数，
# 导致「探索→模板」转化率虚高、丢失人数被抹平。
EXPLORE_PREFIXES = ("/tools",)          # /tools/* 视为工具探索（与模板页互斥）
PRODUCT_PREFIXES = ("/templates", "/resources/time-intelligence-starter")

# 每一步的「可落地优化动作」——只在诊断输出，不自动改代码。
FUNNEL_ACTIONS = {
    "到达站点→产生互动": "首屏与搜索意图错配：检查 Top 落地页 H1/首段是否匹配查询词；不匹配的页面 48h 内重写首屏。",
    "产生互动→实质滚动": "正文太长或排版劝退：给跳动最高的 3 页加目录锚点 + 把结论前置到首屏。",
    "实质滚动→探索工具/模板": "教程页缺少横向入口：在正文 1/3 处插入对应工具/模板卡（当前教程页零 Gumroad 链接）。",
    "探索工具/模板→模板页访问": "工具页没有承接购买：工具结果页底部加 1 条直达 Gumroad 的转换 CTA。",
    "模板页访问→结账点击(非成交)": "产品页说服不足：补 1 张真实 PBIX 截图 + 明确 $9/$19 的差异对比表。",
    "结账点击(非成交)→真实成交(purchase)": "点击没变成付款：确认 Gumroad webhook 已配置（Settings>Advanced>Ping），且 Secrets 已填 GA4_API_SECRET / GUMROAD_WEBHOOK_TOKEN。",
    "真实成交(purchase)→订阅提交": "成交后未进邮件列表：在 Gumroad 感谢页加 Buttondown 订阅入口。",
}

def _funnel_filter(field, values, begins=False):
    from google.analytics.data_v1beta.types import Filter, FilterExpression, FilterExpressionList
    exprs = []
    for v in values:
        if begins:
            sf = Filter.StringFilter(value=v, match_type=Filter.StringFilter.MatchType.BEGINS_WITH)
            exprs.append(FilterExpression(filter=Filter(field_name=field, string_filter=sf)))
        else:
            exprs.append(FilterExpression(
                filter=Filter(field_name=field,
                              in_list_filter=Filter.InListFilter(values=list(values)))))
    return FilterExpression(or_group=FilterExpressionList(expressions=exprs))

def ga4_funnel(pid):
    """返回 [(环节名, 去重用户数)]；任一步失败则该步为 0 并记 error。"""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient, RunReportRequest, DateRange, Metric, Dimension
    client = BetaAnalyticsDataClient.from_service_account_json(str(SA_JSON))
    dr = [DateRange(start_date=FUNNEL_START, end_date=FUNNEL_END)]
    out, errors = [], []
    try:
        ev_names = [e for _, e in FUNNEL_EVENTS if e]
        r = client.run_report(RunReportRequest(
            property=f"properties/{pid}", date_ranges=dr,
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="totalUsers")],
            dimension_filter=_funnel_filter("eventName", ev_names),
        ))
        ev_users = {row.dimension_values[0].value: int(row.metric_values[0].value)
                    for row in r.rows}
    except Exception as e:
        ev_users, _ = {}, errors.append(f"事件漏斗：{e}")

    def path_users(prefixes):
        try:
            r = client.run_report(RunReportRequest(
                property=f"properties/{pid}", date_ranges=dr,
                dimensions=[Dimension(name="pagePath")],
                metrics=[Metric(name="totalUsers")],
                dimension_filter=_funnel_filter("pagePath", prefixes, begins=True),
            ))
            return sum(int(row.metric_values[0].value) for row in r.rows)
        except Exception as e:
            errors.append(f"页面漏斗：{e}")
            return 0

    explore = path_users(EXPLORE_PREFIXES)
    product = path_users(PRODUCT_PREFIXES)
    for name, ev in FUNNEL_EVENTS:
        if ev:
            out.append((name, ev_users.get(ev, 0)))
        elif name == "探索工具/模板":
            out.append((name, explore))
        elif name == "模板页访问":
            out.append((name, product))
    return out, errors

def gsc_query(creds, start, end, dimension, row_limit=20):
    from googleapiclient.discovery import build
    sc = build("webmasters", "v3", credentials=creds)
    body = {"startDate": start, "endDate": end, "dimensions": [dimension], "rowLimit": row_limit}
    resp = sc.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return resp.get("rows", [])

def load_creds():
    from google.oauth2 import service_account
    return service_account.Credentials.from_service_account_file(
        str(SA_JSON),
        scopes=["https://www.googleapis.com/auth/analytics.readonly",
                "https://www.googleapis.com/auth/webmasters.readonly"])

def main():
    alerts, info, lines = [], [], []
    A = lines.append
    did = TODAY.strftime("%Y%m%d")
    A(f"# powerbitutorials.com 每日达成汇报 — {did}（昨日 {Y.isoformat()}）")
    A("")
    A(f"> 生成：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 口径：GA4 pageViews（JS 真人）/ GSC 自然搜索")
    A("")

    # 数据源
    creds_flag, pid, status = load_api()
    A(f"## 一、数据源")
    A(f"- 服务账号：{status} ｜ GA4 属性：{pid or '未配置'}")
    A("")

    # 浏览量 + 环比
    A(f"## 二、浏览量与环比增长")
    ga4 = None
    if creds_flag and pid:
        ga4 = ga4_pull(pid)
        if ga4 and "error" not in ga4:
            pv_y, au_y = ga4.get("y", (0, 0))
            pv_d2, au_d2 = ga4.get("d2", (0, 0))
            pv_w7, au_w7 = ga4.get("w7", (0, 0))
            dod = pct(pv_y, pv_d2)
            wow = pct(pv_y, pv_w7)
            A(f"- **昨日浏览量（pageViews）：{pv_y:,}** ｜ 真人活跃用户：{au_y:,}")
            A(f"- 环比（DoD，vs 前日 {pv_d2:,}）：**{dod:+.1f}%**")
            A(f"- 同比周（WoW，vs 7 天前同日 {pv_w7:,}）：**{wow:+.1f}%**")
            if wow <= -20:
                alerts.append(f"[流量] 浏览量 WoW {wow:.1f}% 跌幅>20%（{pv_w7:,}→{pv_y:,}），排查索引/排名/异常")
            if dod <= -35:
                alerts.append(f"[流量] 浏览量 DoD {dod:.1f}% 骤降（{pv_d2:,}→{pv_y:,}），疑似单日异常或抓取问题")
            # 进度条
            pct_uv = min(100, round(au_y / TARGET_UV * 100))
            A(f"- 距日均 1k UV 目标：{au_y}/{TARGET_UV} = {pct_uv}%（单日，非均值）")
        else:
            A(f"- ⚠️ GA4 拉取失败：{ga4.get('error') if ga4 else 'unknown'}")
            info.append("GA4 拉取失败，检查服务账号 Viewer 权限 / ga4-property-id.txt")
    else:
        A(f"- ⚠️ 未授权 → 实时浏览量暂不可用。仓库 Secrets 配好 `GSC_SA_JSON` + `GA4_PROPERTY_ID` 后自动接管（脚本会写到仓库根目录的 gsc-ga4-service-account.json / ga4-property-id.txt）。")
        A("- ⚠️ 无实时数据源：本段**不提供任何估算数字**（此前的「Cloudflare 估算 ~85/天」是硬编码残留，已移除，避免陈旧数字被当成当日数据）。")
    A("")

    # 增长来源
    A(f"## 三、增长来源")
    if creds_flag and pid:
        # 渠道
        A("- 渠道构成（GA4 sessionDefaultChannelGroup，近 7 天 activeUsers）：")
        if ga4 and "channels" in ga4:
            tot_ch = sum(v for _, v in ga4["channels"]) or 1
            for c, v in ga4["channels"][:6]:
                A(f"  - {c}: {v:,}（{v/tot_ch*100:.0f}%）")
        # GSC 上升查询
        try:
            c = load_creds()
            rows_now = gsc_query(c, GSC_S7, GSC_END, "query", 30)
            rows_prev = {(r["keys"][0]): r for r in gsc_query(c, GSC_P7, GSC_S7, "query", 30)}
            A("- 上升查询（GSC 近 7 天 vs 前 7 天，按曝光增量）：")
            gains = []
            now_map = {r["keys"][0]: r for r in rows_now}
            for r in rows_now:
                q = r["keys"][0]
                impr_now = int(r["impressions"]); impr_prev = int(rows_prev.get(q, {}).get("impressions", 0))
                delta = impr_now - impr_prev
                gains.append((q, delta, impr_now, float(r["position"])))
            gains.sort(key=lambda x: x[1], reverse=True)
            shown = 0
            for q, d, im, pos in gains:
                if d > 0 and shown < 8:
                    A(f"  - 「{q}」曝光 +{d:,}（{im:,} / 排名 {pos:.0f}）")
                    shown += 1
            if shown == 0:
                A("  - 近 7 天无显著上升查询（曝光增量<=0）")
        except Exception as e:
            A(f"  - ⚠️ GSC 来源查询失败：{e}")
    else:
        rows = []
        if GSC_CSV.exists():
            import csv
            with open(GSC_CSV, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    rows.append(row)
        if rows:
            A(f"- 手动 GSC 导出 {len(rows)} 条（静态快照，非实时）。高曝光低排名（潜在增长来源）：")
            parsed = []
            for r in rows:
                try:
                    q = r.get("Top queries") or list(r.values())[0]
                    impr = int(r.get("Impressions", 0) or 0); pos = float(r.get("Position", 0) or 0)
                    parsed.append((q, impr, pos))
                except Exception:
                    pass
            for p in sorted(parsed, key=lambda x: x[1], reverse=True)[:6]:
                A(f"  - 「{p[0]}」曝光 {p[1]} / 排名 {p[2]:.0f}")
        else:
            A("- ⚠️ 无 GSC 数据（待授权或手动导出）")
    A("")

    # 转化漏斗（近 28 天滚动，与用户导出口径一致）
    A(f"## 四、转化漏斗（近 {FUNNEL_DAYS} 天 {FUNNEL_START} ~ {FUNNEL_END}）")
    funnel = None
    if creds_flag and pid:
        funnel, ferr = ga4_funnel(pid)
        for e in ferr:
            info.append(f"漏斗数据不完整：{e}")
        A("> 口径：各环节去重用户数（totalUsers），非事件数；同一用户多步只计一次。")
        A("> 「结账点击」是点击购买按钮，不是成交；「真实成交」只来自 Gumroad webhook 服务端回传的 purchase 事件。")
        A("")
        A("| 环节 | 用户数 | 上一步→本步 | 累计转化（vs 到达） |")
        A("|---|---:|---:|---:|")
        base = funnel[0][1] if funnel else 0
        prev = None
        drops = []
        for name, users in funnel:
            if prev is None:
                step_rate = "—"
            else:
                step_rate = f"{users/prev*100:.1f}%" if prev else "—"
                drops.append((f"{prev_name}→{name}", prev - users, prev, users))
            cum = f"{users/base*100:.2f}%" if base else "—"
            A(f"| {name} | {users:,} | {step_rate} | {cum} |")
            prev, prev_name = users, name
        A("")
        # 诊断：同时给「绝对丢失最多」和「流失率最高」两个视角。
        # 只看绝对人数会永远指向第一步（到达→互动），掩盖后段近乎归零的变现断点。
        real_drops = [d for d in drops if d[1] > 0]
        if real_drops:
            by_volume = sorted(real_drops, key=lambda x: x[1], reverse=True)[0]
            by_rate = sorted(real_drops, key=lambda x: x[1] / x[2] if x[2] else 0, reverse=True)[0]
            v_label, v_lost, v_up, v_down = by_volume
            r_label, r_lost, r_up, r_down = by_rate
            r_rate = r_lost / r_up * 100 if r_up else 0
            A(f"- **丢失人数最多：{v_label}** — {v_lost:,} 人（{v_up:,}→{v_down:,}）")
            A(f"- **流失率最高：{r_label}** — {r_rate:.1f}%（{r_up:,}→{r_down:,}）")
            # 优化动作优先指向「变现链后段」的高流失环节（模板页及之后），
            # 前段流量流失另由内容侧处理，避免每天重复同一条建议。
            late = [d for d in real_drops if d[0].startswith(
                ("模板页访问", "结账点击", "真实成交", "探索工具"))]
            focus = sorted(late, key=lambda x: x[1] / x[2] if x[2] else 0, reverse=True)
            focus = focus[0] if focus else by_rate
            f_label, f_lost, f_up, f_down = focus
            f_rate = f_lost / f_up * 100 if f_up else 0
            A(f"- **本轮优化板块：{f_label}**（流失 {f_rate:.1f}%）")
            action = FUNNEL_ACTIONS.get(f_label, "定位该环节落地页，排查内容/入口/信任信号。")
            A(f"- 针对该板块的动作：{action}")
            if f_rate >= 50:
                alerts.append(f"[漏斗] {f_label} 流失 {f_rate:.1f}%（{f_up:,}→{f_down:,}），变现链最大断点")
        # 硬指标告警：真实成交为 0 时必须暴露，并区分「没人点」与「点了没回传」
        clicks = dict(funnel).get("结账点击(非成交)", 0)
        purchases = dict(funnel).get("真实成交(purchase)", 0)
        if purchases == 0 and clicks > 0:
            alerts.append(
                f"[变现] 近 28 天结账点击 {clicks} 人但真实成交 = 0："
                "优先查 Gumroad webhook 是否配置、Secrets(GA4_API_SECRET/GUMROAD_WEBHOOK_TOKEN) 是否填写；"
                "不要再把 checkout_click 当作成交")
        elif purchases == 0:
            info.append("[变现] 近 28 天真实成交 = 0 且无结账点击：CTA 触达是瓶颈，先解决入口")
        elif purchases < 10:
            info.append(f"近 28 天真实成交仅 {purchases} 人，样本太小，暂不做转化率归因")
    else:
        A("- ⚠️ 无 GA4 授权 → 本段不输出任何漏斗数字（不用静态快照冒充实时转化数据）。")
        A("- 配好 Secrets 后自动启用：事件环节取 totalUsers，模板/工具页取 pagePath 去重用户。")
    A("")

    # 内容引擎达成（无论是否授权都可见）
    A(f"## 五、内容引擎达成（本地）")
    urls = fetch_live_urls()
    dm, ll = production_progress()
    if urls is None:
        A("- 线上教程文章数（sitemap）：⚠️ 本次拉取异常，文章数不可用（**不要按 0 篇解读**）")
    else:
        A(f"- 线上教程文章数（sitemap）：**{len(urls)}** 篇（目标 200）")
    A(f"- 草稿目录文章草稿数：{dm} 篇 ｜ 日历发布日志记录：{ll} 条")
    # 部署健康：仓库有、线上没有 = 已入库未上线。持续不为零 = 部署链路断了，
    # 此时「生成成功」是假象——文章只会在仓库里堆积，线上篇数纹丝不动。
    if urls is not None:
        live_slugs = {u.rstrip("/").rsplit("/", 1)[-1] for u in urls}
        local_slugs = {p.stem for p in CONTENT_DIR.glob("*.md")} if CONTENT_DIR.exists() else set()
        if local_slugs and (local_slugs & live_slugs):
            not_live = sorted(local_slugs - live_slugs)
            if not_live:
                shown = "、".join(not_live[:5]) + ("…" if len(not_live) > 5 else "")
                A(f"- 🚨 部署健康：**{len(not_live)} 篇已入库但未上线**（{shown}）"
                  f" → 生成在继续但线上不涨，Cloudflare Pages 部署多半已中断，需人工确认")
                alerts.append(f"部署中断：{len(not_live)} 篇已入库未上线，线上文章数停止增长")
            else:
                A("- ✅ 部署健康：仓库与线上文章一致，新文章可正常上线")
    A(f"- 今日待办：发布当日草稿 + 1 个技术微任务（内链/schema/索引/CTR 轮换）")
    A("")

    A(f"## 六、告警与提示")
    if alerts:
        A(f"- 🚨 {len(alerts)} 条：")
        for a in alerts: A(f"  - {a}")
    else:
        A("- ✅ 无越阈值告警")
    for i in info:
        A(f"- ℹ️ {i}")
    A("")
    A("---")
    A("自动生成 · 前 30 天每日汇报试点 · 由「powerbitutorials 每日达成汇报」自动化触发")

    report = "\n".join(lines)
    out_file = OUT / f"daily-{did}.md"
    out_file.write_text(report, encoding="utf-8")
    print(report)
    print("\n===ALERT_SUMMARY===")
    for a in alerts: print("ALERT:", a)
    for i in info: print("INFO:", i)
    print(f"REPORT_FILE={out_file}")

if __name__ == "__main__":
    main()
