# DAX Guide — Power BI Tutorials Content Site

A high-performance content site for Power BI / DAX / Power Query tutorials, built for AdSense monetization. Static-first, zero-cost hosting, AI-assisted content workflow.

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Framework | **Astro 4.x** | Static-first, zero JS by default, Lighthouse 95+, best-in-class SEO |
| Hosting | **Cloudflare Pages** | Free tier covers MVP, global CDN, auto HTTPS, git-push deploy |
| CMS | **Keystatic** | Git-based, local visual editor, no database, free |
| Content | **Markdown + MDX** | Portable, version-controlled, AI-friendly |
| Analytics | GA4 + Search Console | Free, official |

**90-day hosting cost: ~$12** (domain only)

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start dev server (http://localhost:4321)
npm run dev

# 3. Build for production
npm run build

# 4. Preview production build
npm run preview
```

Requires Node.js >= 18.17.1 (Node 22 recommended).

## Project Structure

```
daxguide-site/
├── astro.config.mjs          # Astro config (integrations, sitemap)
├── keystatic.config.ts       # Keystatic CMS schema (visual editor)
├── src/
│   ├── consts.ts             # ⭐ Site-wide constants (title, nav, AdSense ID)
│   ├── content/
│   │   ├── config.ts         # Content collection schema (Zod)
│   │   └── tutorials/        # Tutorial markdown files
│   │       ├── dax-basics.md
│   │       ├── calculate-function.md
│   │       ├── power-query-getting-started.md
│   │       ├── time-intelligence.md
│   │       └── data-modeling-star-schema.md
│   ├── layouts/
│   │   └── BaseLayout.astro  # HTML shell, SEO meta, OG tags, AdSense script
│   ├── components/
│   │   ├── Header.astro      # Sticky nav with mobile menu
│   │   ├── Footer.astro      # Footer with links + disclosure
│   │   ├── Sidebar.astro     # Category nav + newsletter
│   │   ├── TutorialCard.astro
│   │   └── AdSlot.astro      # AdSense unit placeholder
│   ├── pages/
│   │   ├── index.astro       # Homepage
│   │   ├── tutorials/
│   │   │   ├── index.astro   # All tutorials (search + filter)
│   │   │   └── [slug].astro  # Tutorial detail (TOC, ads, related)
│   │   ├── category/[slug].astro
│   │   ├── about.astro       # ⭐ Required for AdSense (E-E-A-T)
│   │   ├── contact.astro     # ⭐ Required for AdSense
│   │   ├── 404.astro
│   │   └── rss.xml.js
│   └── styles/
│       └── global.css        # Theme tokens, light/dark mode
├── public/
│   ├── robots.txt
│   ├── ads.txt               # Fill in after AdSense approval
│   └── favicon.svg
└── tsconfig.json
```

## Content Production SOP

### Option A: Visual editor (Keystatic)

1. Run `npm run dev`
2. Open `http://localhost:4321/keystatic`
3. Click **Tutorials → Create**
4. Fill in frontmatter fields + write content in the rich-text editor
5. Save — Keystatic writes a markdown file to `src/content/tutorials/`
6. Commit to git

### Option B: Markdown directly

Create `src/content/tutorials/your-slug.md`:

```markdown
---
title: "Your Tutorial Title"
description: "1-2 sentence SEO description (120-200 chars)."
pubDate: 2026-07-20
category: "dax"
difficulty: "Intermediate"
tags: ["dax", "calculate"]
author: "DAX Guide Editorial Team"
featured: false
---

Your markdown content here. Use ## for section headings (auto-added to TOC).
```

### AI-assisted workflow (recommended)

1. **Keyword research** — Google Keyword Planner, find long-tail with 100-1k volume
2. **Outline by hand** — 4-6 H2 sections, differentiation is here
3. **AI draft** — feed outline + sample data to Claude/GPT
4. **Human edit** — add real examples, Power BI screenshots, fix tone
5. **Original visuals** — Excalidraw diagrams, Power BI screenshots (never stock photos)
6. **Fact-check** — verify every DAX formula runs correctly
7. **Publish** — target 2-3 per week

> AdSense does NOT ban AI content. It bans *low-value* content. The human edit step (real examples, screenshots, fact-checking) is what makes AI-assisted content approvable.

## 云端自动化（GitHub Actions）

站点内容生产与流量复盘已完全云端化，不依赖本机、也不依赖 WorkBuddy / 任何桌面端是否开机。

| Workflow | 触发（UTC） | 作用 |
|---|---|---|
| `publish.yml` | 每日 15:00（= 08:00 PDT） | 生成 1–2 篇教程 → 第二个模型审稿 → 提交推送 → 邮件汇报 |
| `daily-report.yml` | 每日 04:00（= 21:00 PDT） | GA4 真人 UV / 环比 / 增长来源 → 邮件 |
| `weekly-review.yml` | 每周一 16:00（= 周一 09:00 PDT） | 周复盘 + 异常告警 → 邮件 |

- **LLM**：DeepSeek。`deepseek-chat` 生成、`deepseek-reasoner` 审稿，两者构成"另一个 AI"复核。
- **投递优先级**：163 SMTP 邮件（主）→ 飞书机器人（备）→ Resend（备）；任一失败不影响其他。
- **护栏**：每日最多 2 篇；仓库中已存在但尚未上线（不在 sitemap）的文章超过 20 篇则中止并告警（通常意味着 Cloudflare Pages 部署中断）；sitemap 拉取失败时自动跳过该护栏。
- **内容质检**：生成后、提交前跑 `scripts/validate_content.py --changed`。它会按 `src/content/config.ts` 的 schema 校验 frontmatter（必填字段 / enum / 日期格式 / 是否有 schema 未定义的字段）。不合格就不提交并触发告警邮件——因为 Astro 构建失败会导致**整站停更**，比不发布更糟。另：`generate_article.py` 的 `repair_links()` 会把模型编造的、指向不存在文章的内链降级为纯文本，防止上线 404。
- **本地预检**：`scripts/verify_sa_access.py` 可在配 Secret 前确认服务账号对 GA4 / GSC 的读权限是否给对（用法见文件头）。

### 需要在 仓库 Settings → Secrets and variables → Actions 配置

| Secret | 必填 | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | ✅ | platform.deepseek.com 的 API key |
| `SMTP_USER` / `SMTP_PASS` | ✅ | 163 邮箱地址 / **SMTP 授权码**（不是登录密码） |
| `GSC_SA_JSON` | ✅ | Search Console + GA4 服务账号 JSON（整段粘贴） |
| `GA4_PROPERTY_ID` | ✅ | GA4 媒体资源 ID（纯数字） |
| `REPORT_TO` | ⬜ | 汇报收件人，默认 `mireia1998@163.com`，逗号可多个 |
| `SMTP_HOST` / `SMTP_PORT` | ⬜ | 默认 `smtp.163.com` / `465`（SSL） |
| `LLM_MODEL` / `REVIEW_MODEL` | ⬜ | 默认 `deepseek-chat` / `deepseek-reasoner` |
| `FEISHU_WEBHOOK` / `FEISHU_SECRET` | ⬜ | 备用通道 |
| `RESEND_API_KEY` / `RESEND_FROM` | ⬜ | 备用通道 |

配好后在 Actions 页手动 `Run workflow` 一次即可验证全链路。

## Deploy to Cloudflare Pages

### Method 1: Git integration (recommended)

1. Push this repo to GitHub
2. Cloudflare Dashboard → Pages → Create project → Connect to Git
3. Select this repo
4. Build settings:
   - **Framework preset:** Astro
   - **Build command:** `npm run build`
   - **Build output directory:** `dist`
   - **Node version:** 22 (set env var `NODE_VERSION=22`)
5. Deploy — every git push auto-deploys

### Method 2: Wrangler CLI

```bash
npm run build
npx wrangler pages deploy dist --project-name=daxguide-site
```

### Custom domain

1. Buy domain on Cloudflare Registrar (~$9-15/yr, at-cost renewal)
2. Cloudflare Dashboard → Pages project → Custom domains → Add
3. DNS auto-configured if domain is on Cloudflare

Update `site` in `astro.config.mjs` and `SITE_URL` in `src/consts.ts` to your domain.

## AdSense Integration

### Before applying (checklist)

- [ ] 25-30+ published tutorials (1,000+ words each)
- [ ] About, Contact, Privacy Policy, Terms pages exist with real content
- [ ] Custom domain (not `*.pages.dev`)
- [ ] GA4 + Search Console verified
- [ ] 2-4 weeks of content history (Google indexes first)
- [ ] Mobile-responsive (this template is)
- [ ] No copyrighted images; all original screenshots/diagrams

### After approval

1. Get your Publisher ID: `ca-pub-XXXXXXXXXXXXXXXX`
2. Edit `src/consts.ts`:
   ```ts
   export const ADSENSE_CLIENT = "ca-pub-XXXXXXXXXXXXXXXX";
   ```
3. Edit `public/ads.txt`:
   ```
   google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
   ```
4. (Optional) Create ad units in AdSense dashboard and set `slot` IDs in `<AdSlot />` components
5. Redeploy — ads appear automatically (AdSlot renders placeholders until configured)

Ad slots are already placed in the tutorial detail template: top of article, bottom of article, sidebar. Adjust positions in `src/pages/tutorials/[slug].astro`.

## SEO Configuration

Already configured:
- ✅ Sitemap (`/sitemap-index.xml`) via @astrojs/sitemap
- ✅ RSS feed (`/rss.xml`)
- ✅ Open Graph + Twitter cards in BaseLayout
- ✅ JSON-LD `TechArticle` structured data on tutorial pages
- ✅ Canonical URLs
- ✅ Semantic HTML, mobile-first
- ✅ robots.txt

**Before launch, update:**
- `src/consts.ts` → `SITE_URL` to your domain
- `astro.config.mjs` → `site` to your domain
- Create `public/og-default.png` (1200×630 social share image)
- Add Privacy Policy page (`/privacy`) and Terms page (`/terms`) — required for AdSense

## Theme & Styling

CSS variables in `src/styles/global.css` define the design system. The site auto-adapts to light/dark via `prefers-color-scheme`. To force one mode, remove the `@media (prefers-color-scheme: dark)` block.

Key tokens:
- `--c-accent` — brand green (#059669 light / #10b981 dark)
- `--max-width` — page width (1120px)
- `--content-width` — article width (760px)
- `--header-height` — sticky header (64px)

## 90-Day Roadmap

| Phase | Weeks | Goal |
|-------|-------|------|
| Build | 1-2 | Site live, 5 seed tutorials published |
| Content | 3-10 | 2-3 tutorials/week → 25-30 total |
| Apply | 10-12 | AdSense submission, pass review |
| Monetize | 12+ | Ads live, track RPM, optimize top pages |

See `../content-site-adsense-mvp-plan.html` for the full strategy document.

## License

Content: All Rights Reserved (your tutorials).
Code (this template): MIT — use it for your own content sites.
