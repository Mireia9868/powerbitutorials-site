// 站点全局常量 — 改这里即可全站生效
export const SITE_TITLE = "DAX Guide — Power BI Tutorials";
export const SITE_DESCRIPTION =
  "In-depth Power BI, DAX, and Power Query tutorials for data analysts. From beginner basics to advanced time intelligence, learn to build better dashboards.";
export const SITE_URL = "https://daxguide.com";
export const SITE_AUTHOR = "DAX Guide Editorial Team";
export const SITE_LANG = "en";

// 导航
export const NAV_LINKS = [
  { href: "/", label: "Home" },
  { href: "/tutorials", label: "Tutorials" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
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
];

// 难度
export const DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"];

// AdSense — 部署后填入你的 Publisher ID
// 格式: ca-pub-XXXXXXXXXXXXXXXX
export const ADSENSE_CLIENT = ""; // 留空则不渲染广告脚本

// 社交 (可选)
export const SOCIAL_LINKS = {
  github: "https://github.com/your-org/daxguide",
  twitter: "",
  rss: "/rss.xml",
};
