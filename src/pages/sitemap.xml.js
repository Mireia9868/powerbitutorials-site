import { getCollection } from "astro:content";
import { CATEGORIES } from "../consts";

export async function GET({ site }) {
  const baseUrl = site?.toString().replace(/\/$/, "") || "https://powerbitutorials.com";

  const tutorials = await getCollection("tutorials");
  const urls = [];

  // 静态页面 (trailing slash matches Astro build.format: "directory")
  const staticPages = [
    { loc: "/", priority: "1.0", changefreq: "weekly" },
    { loc: "/de/", priority: "0.7", changefreq: "weekly" },
    { loc: "/tutorials/", priority: "0.9", changefreq: "weekly" },
    { loc: "/about/", priority: "0.5", changefreq: "monthly" },
    { loc: "/author/mireia/", priority: "0.5", changefreq: "monthly" },
    { loc: "/templates/", priority: "0.8", changefreq: "monthly" },
    { loc: "/pricing/", priority: "0.9", changefreq: "monthly" },
    { loc: "/templates/finance-starter/", priority: "0.9", changefreq: "monthly" },
    { loc: "/tools/", priority: "0.8", changefreq: "monthly" },
    { loc: "/tools/embed/", priority: "0.4", changefreq: "yearly" },
    { loc: "/tools/license-calculator/", priority: "0.7", changefreq: "monthly" },
    { loc: "/tools/dax-audit/", priority: "0.8", changefreq: "monthly" },
    { loc: "/tools/dax-functions/", priority: "0.9", changefreq: "monthly" },
    { loc: "/tools/date-table/", priority: "0.8", changefreq: "monthly" },
    { loc: "/tools/conditional-format-generator/", priority: "0.8", changefreq: "monthly" },
    { loc: "/contact/", priority: "0.5", changefreq: "monthly" },
    { loc: "/privacy/", priority: "0.3", changefreq: "yearly" },
    { loc: "/terms/", priority: "0.3", changefreq: "yearly" },
  ];
  for (const p of staticPages) {
    urls.push({ ...p, loc: `${baseUrl}${p.loc}` });
  }

  // 分类页 — 使用 slug 而非数组索引
  for (const cat of CATEGORIES) {
    urls.push({
      loc: `${baseUrl}/category/${cat.slug}/`,
      priority: "0.7",
      changefreq: "weekly",
    });
  }

  // 教程详情页
  // noindex 的页（含德语半成品摘要）不进 sitemap —— 一个 noindex URL
  // 出现在 sitemap 里是明确的实现错误。完整翻译的德语页正常收录。
  const deTranslated = new Set(
    tutorials.filter((t) => t.slug.startsWith("de-") && !t.data.draft && !t.data.noindex)
      .map((t) => t.slug.slice(3))
  );
  for (const t of tutorials) {
    if (t.data.draft || t.data.noindex) continue;
    const loc = `${baseUrl}/tutorials/${t.slug}/`;
    const alternates = [];
    if (t.slug.startsWith("de-")) {
      const en = t.slug.slice(3);
      alternates.push({ hreflang: "de", href: loc });
      alternates.push({ hreflang: "en", href: `${baseUrl}/tutorials/${en}/` });
      alternates.push({ hreflang: "x-default", href: `${baseUrl}/tutorials/${en}/` });
    } else if (deTranslated.has(t.slug)) {
      alternates.push({ hreflang: "en", href: loc });
      alternates.push({ hreflang: "de", href: `${baseUrl}/tutorials/de-${t.slug}/` });
      alternates.push({ hreflang: "x-default", href: loc });
    }
    urls.push({
      loc,
      priority: "0.8",
      changefreq: "monthly",
      lastmod: t.data.updatedDate?.toISOString() || t.data.pubDate.toISOString(),
      alternates,
    });
  }

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>${
      u.lastmod ? `\n    <lastmod>${u.lastmod}</lastmod>` : ""
    }${
      u.alternates?.length
        ? `\n${u.alternates
            .map(
              (a) =>
                `    <xhtml:link rel="alternate" hreflang="${a.hreflang}" href="${a.href}" />`
            )
            .join("\n")}`
        : ""
    }
  </url>`
  )
  .join("\n")}
</urlset>`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml" },
  });
}
