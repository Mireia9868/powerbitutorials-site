import { getCollection } from "astro:content";
import { CATEGORIES } from "../consts";

export async function GET({ site }) {
  const baseUrl = site?.toString().replace(/\/$/, "") || "https://daxguide.com";

  const tutorials = await getCollection("tutorials");
  const urls = [];

  // 静态页面
  const staticPages = [
    { loc: "/", priority: "1.0", changefreq: "weekly" },
    { loc: "/tutorials", priority: "0.9", changefreq: "weekly" },
    { loc: "/about", priority: "0.5", changefreq: "monthly" },
    { loc: "/contact", priority: "0.5", changefreq: "monthly" },
    { loc: "/privacy", priority: "0.3", changefreq: "yearly" },
    { loc: "/terms", priority: "0.3", changefreq: "yearly" },
  ];
  for (const p of staticPages) {
    urls.push({ ...p, loc: `${baseUrl}${p.loc}` });
  }

  // 分类页
  for (const cat of Object.keys(CATEGORIES)) {
    urls.push({
      loc: `${baseUrl}/category/${cat}`,
      priority: "0.7",
      changefreq: "weekly",
    });
  }

  // 教程详情页
  for (const t of tutorials) {
    urls.push({
      loc: `${baseUrl}/tutorials/${t.slug}`,
      priority: "0.8",
      changefreq: "monthly",
      lastmod: t.data.updatedDate?.toISOString() || t.data.pubDate.toISOString(),
    });
  }

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <changefreq>${u.changefreq}</changefreq>
    <priority>${u.priority}</priority>${
      u.lastmod ? `\n    <lastmod>${u.lastmod}</lastmod>` : ""
    }
  </url>`
  )
  .join("\n")}
</urlset>`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml" },
  });
}
