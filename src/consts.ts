// 站点全局常量 — 改这里即可全站生效
export const SITE_TITLE = "Power BI Tutorials — DAX, Power Query & Data Modeling";
export const SITE_DESCRIPTION =
  "In-depth Power BI, DAX, and Power Query tutorials for data analysts. From beginner basics to advanced time intelligence, learn to build better dashboards.";
export const SITE_URL = "https://powerbitutorials.com";
export const SITE_AUTHOR = "Power BI Tutorials Team";
export const SITE_LANG = "en";

// 导航
export const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/tutorials/", label: "Tutorials" },
  { href: "/about/", label: "About" },
  { href: "/contact/", label: "Contact" },
];

// 教程分类 (与 content collection schema 的 category 对应)
export const CATEGORIES = [
  {
    slug: "dax",
    label: "DAX Formulas",
    description: "Master the Data Analysis Expressions language.",
  },
  {
    slug: "power-query",
    label: "Power Query",
    description: "ETL and data preparation in Power BI.",
  },
  {
    slug: "data-modeling",
    label: "Data Modeling",
    description: "Star schema, relationships, and model design.",
  },
  {
    slug: "visualization",
    label: "Visualization",
    description: "Build interactive reports and dashboards.",
  },
  {
    slug: "time-intelligence",
    label: "Time Intelligence",
    description: "Date-based calculations and YTD/MTD patterns.",
  },
  {
    slug: "service",
    label: "Power BI Service",
    description: "Workspaces, gateways, deployment, and administration.",
  },
];

// 难度
export const DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"];

// AdSense — Publisher ID
// 格式: ca-pub-XXXXXXXXXXXXXXXX，留空则不渲染广告脚本
export const ADSENSE_CLIENT = "ca-pub-2269516311541291";

// Google Search Console 验证 — 在 GSC 后台添加站点后会得到一串 verification token，填到这里
// 留空则不渲染 google-site-verification meta tag
export const GOOGLE_SITE_VERIFICATION = "RhRJDyl7Kr3qeHJGS9OgURTXvuGgzgcbYkDk47WwUHQ";

// Bing Webmaster Tools 验证 — 在 https://www.bing.com/webmasters 添加站点后获取
// 留空则不渲染 bing 验证 meta tag
export const BING_SITE_VERIFICATION = "A2FC1B495860A9DD04B4F99C18F4A9EA";

// IndexNow 密钥 — 用于 Bing/Yandex 即时索引通知
// 生成方式: 生成一个随机字符串，放到 public/indexnow-key.txt
// 留空则不启用 IndexNow 自动提交
export const INDEXNOW_KEY = "";

// 社交 (可选)
export const SOCIAL_LINKS = {
  github: "https://github.com/Mireia9868/powerbitutorials-site",
  twitter: "",
  rss: "/rss.xml",
};
