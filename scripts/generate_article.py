#!/usr/bin/env python3
"""
powerbitutorials.com — 云端每日文章生成器（GitHub Actions 运行，不依赖本机/WorkBuddy）

流程：
  1. 读 topic_queue.json（按 GSC 缺口 + Trends 排好的选题队列，去重 sitemap）
  2. 取当天 1–2 个「slug 尚未存在」的选题
  3. 调用 LLM（DeepSeek / OpenAI / Anthropic，由 LLM_PROVIDER 决定）生成英文教程
  4. 调用「另一个模型」做第二视角审稿，写入 .article-reviews/<slug>.review.md
     （默认 生成=deepseek-chat、审稿=deepseek-reasoner，可用 REVIEW_MODEL 覆盖）
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

def pick_topics(exist=None):
    exist = existing_slugs() if exist is None else exist
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

def pending_pileup(exist):
    """堆积 = 仓库里有、但还没上线（sitemap 里没有）的文章数。
    sitemap 拉不到时返回 None（跳过护栏，避免网络抖动误杀）。"""
    if not exist:
        return None
    local = {p.stem for p in CONTENT_DIR.glob("*.md")} if CONTENT_DIR.exists() else set()
    return len(local - exist)

# ---------- LLM ----------
# DeepSeek 走 OpenAI 兼容协议：base_url=https://api.deepseek.com，模型 deepseek-chat / deepseek-reasoner
DEFAULT_MODELS = {"deepseek": "deepseek-chat", "openai": "gpt-4o",
                  "anthropic": "claude-sonnet-4-20250514"}
TOKEN_USAGE = []   # 累计用量，便于监控异常消耗

def _record_usage(tag, usage):
    if not usage:
        return
    p = getattr(usage, "prompt_tokens", None) or 0
    c = getattr(usage, "completion_tokens", None) or 0
    TOKEN_USAGE.append((tag, p, c))
    log(f"LLM usage[{tag}] prompt={p} completion={c}")

def call_llm(system, user, purpose="generate", _force_model=None):
    provider = (os.environ.get("LLM_PROVIDER") or "deepseek").lower()
    model_env = "REVIEW_MODEL" if purpose == "review" else "LLM_MODEL"
    if provider == "deepseek":
        from openai import OpenAI
        key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")
        client = OpenAI(api_key=key,
                        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
        model = _force_model or os.environ.get(model_env) or DEFAULT_MODELS["deepseek"]
        r = client.chat.completions.create(model=model, max_tokens=6000,
            messages=[{"role":"system","content":system},{"role":"user","content":user}])
        _record_usage(f"{purpose}:{model}", getattr(r, "usage", None))
        return r.choices[0].message.content
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        model = _force_model or os.environ.get(model_env) or DEFAULT_MODELS["openai"]
        r = client.chat.completions.create(model=model, max_tokens=5000,
            messages=[{"role":"system","content":system},{"role":"user","content":user}])
        _record_usage(f"{purpose}:{model}", getattr(r, "usage", None))
        return r.choices[0].message.content
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        model = _force_model or os.environ.get(model_env) or DEFAULT_MODELS["anthropic"]
        r = client.messages.create(model=model, max_tokens=5000,
                                    system=system, messages=[{"role":"user","content":user}])
        _record_usage(f"{purpose}:{model}", getattr(r, "usage", None))
        return "".join(b.text for b in r.content if b.type == "text")
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
    return call_llm(SYS_SPEC, build_user(topic, related), purpose="generate")

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
    # 去掉与 frontmatter title 重复的首行标题（避免页面出现两个 H1/H2）
    body = body.lstrip("\n")
    lines = body.split("\n")
    if lines and re.match(r"^#{1,3}\s+", lines[0]):
        head = re.sub(r"^#{1,3}\s+", "", lines[0]).strip().strip("*").strip()
        norm = lambda t: re.sub(r"[^a-z0-9]+", "", t.lower())
        if norm(head) == norm(topic["title"]) or norm(head).startswith(norm(topic["title"])[:30]):
            body = "\n".join(lines[1:]).lstrip("\n")
    # 提取 description：取首段前 150-190 字符
    first_para = ""
    for blk in re.split(r"\n\s*\n", body):
        t = blk.strip()
        if t and not t.startswith("#") and not t.startswith("![") and "```" not in t:
            first_para = t; break
    desc = re.sub(r"\s+", " ", first_para).strip()
    if len(desc) > 190:
        m = re.search(r"^(.{60,190}?[.!?])(\s|$)", desc)
        if m:
            desc = m.group(1)
        else:
            cut = desc[:190]
            desc = cut[:cut.rfind(" ")] if " " in cut else cut
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
    real_slugs = existing_slugs()
    # 护栏：堆积检查（仓库里存在但尚未上线 sitemap 的文章）
    pend = pending_pileup(real_slugs)
    if pend is None:
        log("WARN sitemap unreachable — pileup guard skipped this run")
    elif pend > PILEUP_LIMIT:
        log(f"PILEUP guard: {pend} articles not live yet (> {PILEUP_LIMIT}), abort + alert "
            f"(Cloudflare Pages 部署可能已中断，请检查)")
        sys.exit(1)
    topics = pick_topics(real_slugs)
    if not topics:
        log("no new topics to generate today (queue exhausted or all exist)")
        sys.exit(0)
    auto_publish = os.environ.get("AUTO_PUBLISH","false").lower() == "true"
    for topic in topics:
        try:
            body = generate(topic, sorted(real_slugs)[:40])
            md = assemble(topic, body)
            validate(md)
            rev = review(md, topic, sorted(real_slugs)[:40])
            (CONTENT_DIR / f"{topic['slug']}.md").write_text(md)
            (REVIEW_DIR / f"{topic['slug']}.review.md").write_text("# Review: "+topic['slug']+"\n\n"+rev)
            log(f"generated + reviewed: {topic['slug']}")
        except Exception as e:
            log(f"FAILED {topic['slug']}: {e}")
            continue
    if TOKEN_USAGE:
        total = sum(p + c for _, p, c in TOKEN_USAGE)
        log(f"token usage total = {total} ({len(TOKEN_USAGE)} calls)")
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
