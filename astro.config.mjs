import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import keystatic from "@keystatic/astro";

// Keystatic admin 仅在 dev 模式加载。
// 纯静态构建/部署不含 admin 路由（admin 需要 SSR，静态站点不支持）。
// 本地编辑: npm run dev → /keystatic
// 生产编辑: 切换 Keystatic 到 GitHub 存储模式，部署到支持 SSR 的平台
const enableKeystatic = process.env.NODE_ENV !== "production";

// https://astro.build/config
export default defineConfig({
  site: "https://daxguide.com",
  integrations: [
    mdx(),
    // sitemap 改用自定义端点 src/pages/sitemap.xml.js，避免 @astrojs/sitemap 兼容问题
    ...(enableKeystatic ? [keystatic()] : []),
  ],
  markdown: {
    shikiConfig: {
      theme: "github-dark",
      wrap: true,
    },
  },
  build: {
    inlineStylesheets: "auto",
  },
  prefetch: {
    prefetchAll: true,
    defaultStrategy: "viewport",
  },
});
