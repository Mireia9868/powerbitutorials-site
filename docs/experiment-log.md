# Experiment log

记录会影响 GA4 归因的站点变更。**改版期间的任何视觉/结构变更都要追加一行**，
否则 A/C 对比会被污染。

## site_design_ac_202610 — 首页 + 全站视觉 A/C

| 日期 (Asia/Taipei) | 变更 | 影响 | 提交 |
|---|---|---|---|
| 2026-10-21 | 实验上线：50/50 随机分配 A（原版）/ C（实验视觉），localStorage 记忆，key `pbi-design-ac-202610-v2` | 开始分流 | `41eac71` |
| 2026-11-19 | 内嵌工具打开事件埋点 | 新增事件 | `ed8fed2` |
| 2026-11-22 | ① **根因修复**：`define:vars` 把 GA 初始化脚本包进函数作用域，`gtag` 从未挂到 `window`，所有 `typeof window.gtag === 'function'` 守卫静默失败 → 自定义事件 30 天 0 条；补 `window.gtag = gtag` 修复（提交 `ff205f4`）。② 变体改为写 GA4 user property `design_variant`（每个 hit 携带，含首个 page_view）；③ 自定义事件不再受 cookie 同意 gate（与 page_view 的采集口径对齐）；④ 新增 `purchase_intent` 转化事件（覆盖所有 Creem 购买按钮，`data-pack` 标注产品） | 实验从今天起才算真正开始 | `ff205f4` / `b914d91` |
| 2026-11-22 | www → 裸域 301（`functions/_middleware.js`） | 归因域名统一 | `d7b8129` |
| 2026-11-22 | `/templates/` 与 `/tools/` 页面级视觉改版（网格 hero、卡片网格、FAQ、final CTA），新增页面级样式 `src/styles/hub-design.css`；**仅这两个页面**，未改 BaseLayout / 全局 token / 全站实验脚本。A/C 两变体使用同一套结构，仅配色随 `data-design-variant` 变化；保留英文文案、Creem `buy-btn` + `data-pack`、GA4 埋点 | 两页视觉/结构变更，会进入参与率与 `purchase_intent` 统计；A/C 两组同步变化，不能把这两页的指标变化归因于变体差异 | `901a4bd` |
| 2026-11-23 | Bing SEO 批次：7 篇文章改标题 + 首段（`dax-basics`、`power-bi-row-level-security`、`dax-switch-function`、`calculate-function`、`power-query-parameters-dynamic-sources`、`tableau-vs-power-bi` 加结论表、`power-bi-drill-through`）+ `/tools/` meta description；新增文章 `convert-power-query-to-power-bi`。**对照组**（不动）：`power-bi-incremental-refresh`（549 展示 / 位 5.0–5.7）、`power-bi-performance-analyzer`（176 / 5.4–5.9）、`power-bi-dataflows`（157 / 4.3）。验证看 Bing 后台 12 个目标词的 position + CTR，14 天后回收；不看 GA（Bing 点击噪声大） | 标题/首段变更会影响这些页在 GA 的参与率；与 11-22 `/tools/` 视觉改版叠加，`/tools/` 一项无法拆分贡献。A/C 两组同变，不能归因于变体 | `0fe1be3` |

### 基线（2026-10-23 → 2026-11-22，GA4 属性 548614588）

| 指标 | 数值 |
|---|---|
| 会话 / 用户 | 3,346 / 2,631 |
| 参与会话率 | 27.3% |
| 页面浏览 | 3,723 |
| 关键事件 | 0（此前未配置） |

### 判定规则

- 主指标：**参与会话率（engagement rate）**；副指标：`purchase_intent` 每千次会话。
- 每组至少 1,250 会话（检测 +5pp）或 3,460 会话（检测 +3pp）。
- 按 111 会话/天、50/50 分流：+5pp 需约 23 天，+3pp 需约 62 天。
- 期间**冻结**其他视觉/结构改动。

## 2026-11-22 验证（GA4 realtime）

修复后实测通过：

```
page_view 6 · session_start 3 · experiment_exposure 2
first_visit 2 · outbound_click 1 · purchase_intent 1
```

即曝光事件与购买意图事件都已真实抵达 GA4。

## 待办

- [ ] GA4 后台注册自定义维度：`design_variant`（用户级 + 事件级各一个；注册只对之后的数据生效）
- [ ] 把 `purchase_intent` 标为 key event（否则转化口径仍为空）
- [ ] 评估 GA4 的 consent 架构：目前 page_view 与事件都无 gate，需决定是否切 Consent Mode v2
- [ ] 过滤 `(not set)` 落地页的可疑流量（爬虫）
