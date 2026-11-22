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
