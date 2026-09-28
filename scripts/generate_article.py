#!/usr/bin/env python3
"""
powerbitutorials.com — 云端每日文章生成器（GitHub Actions 运行，不依赖本机/WorkBuddy）

流程：
  1. 读 topic_queue.json（按 GSC 缺口 + Trends 排好的选题队列，去重 sitemap）
  2. 取当天 1–2 个「slug 尚未存在」的选题
  3. 调用 LLM（Anthropic / OpenAI，由环境变量决定）生成英文教程
  4. 调用 LLM 做「另一 AI 视角」审稿，写入 .article-reviews/<slug>.review.md
  5. 校验 frontmatter / 代码围栏后写入 content/tutorials/<slug>.md
  6. 若 AUTO_PUBLISH=true → git commit + push（Cloudflare Pages 自动部署）

护栏（防失控）：
  - 待发布草稿 >20 篇 → 中止，避免堆积
  - 每日硬上限 2 篇
  - slug 已存在则跳过，绝不覆盖
  - 不递归、不调用子进程 LLM
"""
import os, sys, json, re, subprocess, datetime, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO / "src" / "content" / "tutorials"
REVIEW_DIR = REPO / ".article-reviews"
QUEUE = REPO / "scripts" / "topic_queue.json"
MAX_PER_DAY = 2
PILEUP_LIMIT = 20

def log(s): print(f"[gen] {s}", flush=True)

# ---------- 选题 ----------
def existing_slugs():
    slugs = set()
    out = subprocess.run(["curl","-sL","--max-time","25","https://powerbitutorials.com/sitemap.xml"],
                         capture_output=True, text=True).stdout
    for m in re.finditer(r"<loc>([^<]+)</loc>", out):
        u = m.group(1).rstrip("/")
        if "/tutorials/" in u and not u.endswith("/tutorials"):
            slugs.add(u.split("/tutorials/")[-1])
    return slugs

def load_queue():
    if QUEUE.exists():
        return json.loads(QUEUE.read_text())
    return []

def pick_topics():
    exist = existing_slugs()
    # 本地已生成但未发布的也视为已占用
    local = {p.stem for p in CONTENT_DIR.glob("*.md")} if CONTENT_DIR.exists() else set()
    taken = exist | local
    queue = load_queue()
    picked = []
    for item in queue:
        if len(picked) >= MAX_PER_DAY:
            break
        slug = item["slug"]
        if slug in taken:
            continue
        picked.append(item)
    return picked

# ---------- LLM ----------
def call_llm(system, user):
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        model = os.environ.get("LLM_MODEL", "claude-sonnet-4-20250514")
        r = client.messages.create(model=model, max_tokens=5000,
                                    system=system, messages=[{"role":"user","content":user}])
        return "".join(b.text for b in r.content if b.type == "text")
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = os.environ.get("LLM_MODEL", "gpt-4o")
        r = client.chat.completions.create(model=model, max_tokens=5000,
            messages=[{"role":"system","content":system},{"role":"user","content":user}])
        return r.choices[0].message.content
    else:
        raise SystemExit(f"unknown LLM_PROVIDER={provider}")

SYS_SPEC = """You are a senior Power BI technical writer for powerbitutorials.com, an English tutorial site that acquires traffic via Google organic search. Write a publish-ready tutorial article.

HARD RULES:
- Language: English, natural technical prose. AVOID AI clichés: no "In today's data-driven world", no "It's worth noting", no "Let's dive in", no mechanical "Moreover/Furthermore/Additionally" stacking, no over-long em-dashes, no fake enthusiasm.
- Format: Markdown. NO YAML frontmatter in the body (the system adds it separately).
- Length: >= 800 words, step-by-step, practical.
- Code: include >= 1 fenced code block (```dax or ```powerquery) with correct syntax.
- Images: use placeholders like ![Figure N: short english description](placeholder). Alt text MUST be English.
- FAQ at end: each question as a level-3 heading "### Q: ...", answer below. >= 3 Q/A pairs.
- Internal links: at the end add a "## Related Reading" section linking to >= 6 EXISTING articles using relative paths /tutorials/<slug>/. Only link slugs that are REAL (provided in the brief).
- Technical accuracy: DAX/Power Query code must be correct; state nuances precisely (e.g. EARLIER requires a nested row context, not just calculated columns).
- DO NOT invent internal links to slugs not in the provided list."""

def build_user(topic, related):
    rel_md = "\n".join(f"- /tutorials/{s}/" for s in related)
    return f"""TOPIC: {topic['title']}
SLUG (filename, no prefix): {topic['slug']}
CATEGORY (one of: dax / power-query / data-modeling / visualization / time-intelligence / service): {topic['category']}
DIFFICULTY (Beginner/Intermediate/Advanced): {topic['difficulty']}
SIGNAL (why this topic): {topic.get('signal','')}

EXISTING REAL SLOGS you may link in "Related Reading" (pick >=6 that fit):
{rel_md if rel_md else '(none provided — skip internal links or only link if you are 100% sure)'}

Write the article now. End with "## Related Reading" then the links."""

def generate(topic, related):
    return call_llm(SYS_SPEC, build_user(topic, related))

# ---------- 审稿（另一 AI 视角）----------
SYS_REVIEW = """You are a strict senior Power BI technical editor reviewing a draft for publication. Output a markdown review with three sections:
1. AI-isms: flag ChatGPT-style phrasing (vague openers, filler, mechanical transitions, em-dash abuse) with specific rewrites.
2. Topic fit: is it long-tail rankable, does it serve "1k real organic UV/day" goal, any better angle?
3. Errors: terminology/code mistakes, frontmatter issues, broken/imagined internal links (verify slugs exist), FAQ/format.
End with a one-line VERDICT: PUBLISH / PUBLISH-AFTER-FIX / REWRITE."""

def review(article_md, topic, related):
    rel_md = "\n".join(f"- /tutorials/{s}/" for s in related)
    user = f"ARTICLE SLUG: {topic['slug']}\nREAL SLAGS for link check:\n{rel_md}\n\n---\n{article_md}"
    return call_llm(SYS_REVIEW, user)

# ---------- 写出 ----------
FRONTMATTER_TMPL = """---
title: "{title}"
description: "{description}"
pubDate: {pubdate}
category: {category}
tags: [{tags}]
difficulty: {difficulty}
author: Mireia
featured: false
draft: false
---
"""

def assemble(topic, body):
    # 提取 description：取首段前 150-190 字符
    first_para = ""
    for blk in re.split(r"\n\s*\n", body):
        t = blk.strip()
        if t and not t.startswith("#") and not t.startswith("![") and "```" not in t:
            first_para = t; break
    desc = re.sub(r"\s+"," ", first_para)[:190]
    pubdate = datetime.date.today().isoformat()
    tags = ", ".join(f'"{t}"' for t in topic.get("tags", [topic["category"]]))
    fm = FRONTMATTER_TMPL.format(
        title=topic["title"].replace('"',''), description=desc.replace('"',''),
        pubdate=pubdate, category=topic["category"], tags=tags,
        difficulty=topic["difficulty"])
    return fm + "\n" + body + "\n"

def validate(md):
    if md.count("```") % 2 != 0:
        raise ValueError("unbalanced code fences")
    if "](placeholder)" in md:
        pass  # allowed; images pending
    if not re.search(r"^### Q:", md, re.M):
        raise ValueError("no FAQ level-3 headings")
    if "slug:" in md.split("---")[1] if md.startswith("---") else False:
        raise ValueError("stray slug field in body")

def main():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    # 护栏：堆积检查
    pending = list(CONTENT_DIR.glob("*.md"))
    if len(pending) > PILEUP_LIMIT:
        log(f"PILEUP guard: {len(pending)} drafts pending, abort to avoid pile-up")
        sys.exit(0)
    topics = pick_topics()
    if not topics:
        log("no new topics to generate today (queue exhausted or all exist)")
        sys.exit(0)
    related = [s for s in (load_queue() and []) ]  # placeholder
    # 真实可链 slug 列表 = sitemap 现有
    real_slugs = existing_slugs()
    auto_publish = os.environ.get("AUTO_PUBLISH","false").lower() == "true"
    for topic in topics:
        try:
            body = generate(topic, sorted(real_slugs)[:40])
            rev = review(body, topic, sorted(real_slugs)[:40])
            md = assemble(topic, body)
            validate(md)
            (CONTENT_DIR / f"{topic['slug']}.md").write_text(md)
            (REVIEW_DIR / f"{topic['slug']}.review.md").write_text("# Review: "+topic['slug']+"\n\n"+rev)
            log(f"generated + reviewed: {topic['slug']}")
        except Exception as e:
            log(f"FAILED {topic['slug']}: {e}")
            continue
    if auto_publish:
        subprocess.run(["git","add","src/content/tutorials/",".article-reviews/"], check=False)
        msg = "auto: publish tutorials "+datetime.date.today().isoformat()
        r = subprocess.run(["git","commit","-m",msg], capture_output=True, text=True)
        if r.returncode == 0:
            subprocess.run(["git","push"], check=False)
            log("committed + pushed")
        else:
            log("nothing to commit")
    else:
        log("AUTO_PUBLISH not set — drafts written locally, not pushed")

if __name__ == "__main__":
    main()
