// 站点全局常量 — 改这里即可全站生效
export const SITE_TITLE = "Power BI Tutorials — DAX, Power Query & Data Modeling";
export const SITE_DESCRIPTION =
  "In-depth Power BI, DAX, and Power Query tutorials for data analysts. From beginner basics to advanced time intelligence, learn to build better dashboards.";
export const SITE_URL = "https://powerbitutorials.com";
export const SITE_AUTHOR = "Mireia";
export const SITE_LANG = "en";

// 导航
export const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/tutorials/", label: "Tutorials" },
  { href: "/de/", label: "Deutsch" },
  { href: "/about/", label: "About" },
  { href: "/contact/", label: "Contact" },
];

// 教程分类 (与 content collection schema 的 category 对应)
export const CATEGORIES = [
  {
    slug: "dax",
    label: "DAX Formulas",
    description: "Master the Data Analysis Expressions language.",
    intro: [
      "DAX is where a Power BI report stops being a reshuffled spreadsheet and starts producing numbers you could not get any other way: year-to-date revenue that respects a slicer, share of total that ignores one, ranking that recalculates at whatever granularity the visual asks for. Almost all of it runs through two ideas — filter context, and the row-by-row evaluation that iterators perform — and almost all DAX bugs come from losing track of which one is in play.",
      "If you are new to the language, start with the basics guide, then read filter context and row context before touching CALCULATE. That order matters: CALCULATE is short and simple only once you already understand what it is modifying. From there the natural progression is CALCULATE itself, then time intelligence, then the iterator functions — and only after that the optimisation material, because tuning a formula you do not understand is guesswork.",
      "The recurring mistake at this level is reaching for nested IFs where SWITCH belongs, or rebuilding a measure in every visual instead of fixing the model underneath. Each article here states the evaluation order it relies on and links to Microsoft's reference for the function involved, so you can check the behaviour against your own build rather than trusting a screenshot.",
    ],
  },
  {
    slug: "power-query",
    label: "Power Query",
    description: "ETL and data preparation in Power BI.",
    intro: [
      "Power Query is the part of Power BI that runs before any DAX does: connecting to a source, fixing the column types, unpivoting the month columns, merging in the lookup table. Every click in the editor writes M code, and that code is what actually executes — on refresh, against the source, possibly on a schedule you are not watching.",
      "The sensible reading order is the getting-started walkthrough, then the transformations you will use every week (group by, unpivot, merge, append, conditional columns), then the M language underneath. Query folding belongs early too, even for beginners: folding is the difference between a refresh that takes four seconds and one that takes forty minutes, and a single step in the wrong place can break it without any error message appearing.",
      "What this section deliberately avoids is doing work in Power Query that belongs in the model, or vice versa. Cleaning that never changes should happen upstream and be forgotten; logic that changes with every report belongs in a measure. Most slow models we look at are a case of that boundary being crossed in both directions at once.",
    ],
  },
  {
    slug: "data-modeling",
    label: "Data Modeling",
    description: "Star schema, relationships, and model design.",
    intro: [
      "The model is the part of Power BI that is hardest to change later and easiest to get wrong early. A star schema — fact tables of events, dimension tables that describe them, one-to-many relationships flowing downhill — is not a style preference. It is the shape that lets the VertiPaq engine compress well and lets DAX measures stay short enough to read.",
      "Start with the star schema guide and the relationship cardinality explainer, then the many-to-many and bidirectional material. Those two topics account for most of the models that look fine until a filter behaves unexpectedly, and both are easier to reason about once the one-to-many baseline is solid. Incremental refresh and aggregation belong here too, but they are scale decisions rather than design decisions.",
      "The pattern that causes the most trouble is using bidirectional filtering to make a visual work instead of fixing the relationships underneath. It usually does make that one visual work. It also introduces ambiguity into every other filter path in the model, and the cost shows up later, in a report that is slow for reasons nobody can locate.",
    ],
  },
  {
    slug: "visualization",
    label: "Visualization",
    description: "Build interactive reports and dashboards.",
    intro: [
      "Report design in Power BI is mostly a decision about what to leave out. A page has room for roughly one question; a visual has room for roughly one comparison. Most reports that feel hard to read are not badly styled — they are answering four questions at once with six charts that each try to answer all of them.",
      "The visual types guide is the place to start, followed by dashboard layout and then the interaction features: drill through, bookmarks, tooltips and slicers. Conditional formatting is worth learning properly rather than by trial and error, since it is the cheapest way to make a table readable without adding another visual to the page.",
      "Two things are worth saying plainly. Colour should carry meaning or be absent; a report with eleven accent colours is not more informative than one with two. And charts are expensive at query time — a page of twenty visuals runs twenty queries, which is why a report that was fast with three can crawl with twenty.",
    ],
  },
  {
    slug: "time-intelligence",
    label: "Time Intelligence",
    description: "Date-based calculations and YTD/MTD patterns.",
    intro: [
      "Year-to-date, month-over-month, rolling twelve weeks — this is most of what business reporting actually asks for, and it is also where DAX fails most quietly. The functions are short. The reason they return the wrong number is almost never the function itself: it is the date table underneath.",
      "Read the calendar table setup before anything else. A marked date table that is contiguous, starts before your earliest fact and ends after your latest one, and is related to every fact table is the precondition for all of it. After that, the YTD/QTD/MTD pattern and the year-over-year comparisons cover the bulk of real requests, with rolling averages as the generalisation once windows stop being calendar-aligned.",
      "Power BI's automatic date/time is the usual culprit in a model that produces plausible but wrong time intelligence. It creates hidden tables that work well enough to hide the problem until you add a second fact table or a fiscal calendar, at which point the numbers drift and nothing in the measure looks wrong.",
    ],
  },
  {
    slug: "service",
    label: "Power BI Service",
    description: "Workspaces, gateways, deployment, and administration.",
    intro: [
      "Everything up to this point happens on one machine, in Desktop. The service is where a report becomes something other people depend on: scheduled refresh through a gateway, row-level security that decides who sees which rows, workspaces that separate build from publish, and capacity that determines whether the thing stays fast at 9am on a Monday.",
      "Begin with the service-versus-desktop overview and incremental refresh, then read row-level security — including the dynamic version, since a static role rarely survives contact with real users. Dataflows and deployment pipelines come next, and only after that the capacity and licensing decisions, which are much easier to make once you know how the model will actually be refreshed and shared.",
      "The two assumptions that cause the most trouble are that a .pbix file can be shared like a spreadsheet, and that a refresh that works in Desktop will work in the service. Neither survives the first week. Credentials, gateway placement and the source's own timeouts live outside the file, and they are the reasons most scheduled refreshes fail.",
    ],
  },
];

// 难度
export const DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"];

// AdSense — Publisher ID
// 格式: ca-pub-XXXXXXXXXXXXXXXX，留空则不渲染广告脚本
// AdSense 当前未启用（空值则不渲染任何 AdSense 广告脚本）；此前因站点被 AdSense 标记为低价值内容而暂停，恢复前需先解决内容合规问题
export const ADSENSE_CLIENT = "";

// 邮件订阅 —— 只有一个配置点，迁到 MailerLite 时只改这里
// ---------------------------------------------------------------------------
// 现状：Buttondown 免费档（100 订阅，无 Automation）。
// 迁移到 MailerLite（免费档 1000 订阅，自带 welcome automation）时：
//   1. MailerLite → Forms → Embedded form → 复制 action URL
//   2. 把 action 换成 https://assets.mailerlite.com/jsonp/<ACCOUNT>/forms/<FORM>/subscribe
//   3. 把 fieldName 改成 "fields[email]"
//   4. 在 MailerLite → Automation 建 "新订阅者 → 发欢迎邮件"，邮件里放下载链接
// 表单只需要 email 一个字段，多一个字段少一半转化。
export const NEWSLETTER = {
  provider: "buttondown" as "buttondown" | "mailerlite",
  action: "https://buttondown.com/api/emails/embed-subscribe/mireia",
  fieldName: "email",
  iframeName: "newsletter-frame",
};

// Google Search Console 验证 — 在 GSC 后台添加站点后会得到一串 verification token，填到这里
// 留空则不渲染 google-site-verification meta tag
export const GOOGLE_SITE_VERIFICATION = "RhRJDyl7Kr3qeHJGS9OgURTXvuGgzgcbYkDk47WwUHQ";

// Bing Webmaster Tools 验证 — 在 https://www.bing.com/webmasters 添加站点后获取
// 留空则不渲染 bing 验证 meta tag
export const BING_SITE_VERIFICATION = "A2FC1B495860A9DD04B4F99C18F4A9EA";

// IndexNow 密钥 — 用于 Bing/Yandex 即时索引通知
// 生成方式: 生成一个随机字符串，放到 public/indexnow-key.txt
// 留空则不启用 IndexNow 自动提交
// Google Analytics 4 — Measurement ID
// 格式: G-XXXXXXXXXX，留空则不渲染 GA4 脚本
export const GA4_MEASUREMENT_ID = "G-GMYRVPSEHX";

export const INDEXNOW_KEY = "";

// 社交 (可选)
export const SOCIAL_LINKS = {
  github: "https://github.com/Mireia9868/powerbitutorials-site",
  twitter: "",
  rss: "/rss.xml",
};
