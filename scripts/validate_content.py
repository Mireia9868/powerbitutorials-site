#!/usr/bin/env python3
"""
文章 frontmatter 校验 —— 发布前拦住会让 Astro 构建失败的稿件。

为什么需要：云端 publish.yml 生成文章后直接 commit/push，真正构建在 Cloudflare。
如果 frontmatter 与 src/content/config.ts 的 schema 不符（字段名错、enum 越界、
日期格式非法），Astro 构建会失败 → 整个站点停更（比不发布更糟）。本脚本在
push 之前先验，失败就中止并告警。

2026-10 增加「质量闸门」：AdSense 以 Low value content 拒绝了本站，判定要点是
substantial unique value / ongoing curation / genuine user interest。工程校验
拦不住「能构建但没价值」的稿子，所以新增一组 quality 检查：

  - description 长度（SERP 只显示 ~155 字符，超了会被截成半句）
  - FAQ 数量（模板要求 ≥3，但线上只有 25/75 达标 → 说明从来没校验过）
  - 权威引用（0 外链 = 没有核实痕迹，是 low value 最直接的证据）
  - 正文字数下限

默认只报不拦（存量 75 篇多数不达标，直接拦会让 CI 全红）；
发布新稿时用 --quality-gate 让它们变成硬失败。

用法：
  python scripts/validate_content.py                     # 校验全部文章
  python scripts/validate_content.py <file.md> [...]     # 只校验指定文件
  python scripts/validate_content.py --changed           # 只校验 git 改动的 .md
  python scripts/validate_content.py --strict            # 质量提示也算失败（404 内链等）
  python scripts/validate_content.py --quality-gate      # 质量项（引用/FAQ/描述）算失败

退出码：0 = 可发布（可能有质量提示）；1 = 有会让构建失败的问题
"""
import sys, re, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG = REPO_ROOT / "src" / "content" / "config.ts"
CONTENT_DIR = REPO_ROOT / "src" / "content" / "tutorials"
PUBLIC_DIR = REPO_ROOT / "public"

REQUIRED = ["title", "description", "pubDate", "category", "difficulty"]
KNOWN_FIELDS = {"title", "description", "pubDate", "updatedDate", "category",
                "difficulty", "tags", "author", "heroImage", "draft", "featured"}
DIFFICULTY_ENUM = {"Beginner", "Intermediate", "Advanced"}

# ---- 质量闸门阈值（AdSense Low value content 整改）----
DESC_MAX = 155          # Google SERP 显示宽度
FAQ_MIN = 3             # 模板要求 ≥3 组 Q/A
CITATION_MIN = 1        # 至少 1 条权威外链
WORDS_MIN = 600         # 低于此值基本没有实质内容
AUTHORITATIVE_DOMAINS = (
    "learn.microsoft.com",
    "docs.microsoft.com",
    "support.microsoft.com",
    "community.fabric.microsoft.com",
    "sqlbi.com",
    "dax.guides",
    "powerquery.how",
)

# 正文图片引用：Astro/vite 会把「非绝对路径」的 src 当模块去 import。
# 一次 ![Figure 1: ...](placeholder) 就能让整站构建失败（2026-09-29 实际发生）。
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
CITE_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
FAQ_RE = re.compile(r"^###\s+Q[:：]", re.M)
WORD_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9'\-]*\b")


def parse_schema():
    """从 config.ts 里读出 category 枚举，避免两处硬编码不同步。"""
    txt = CONFIG.read_text(encoding="utf-8")
    m = re.search(r"category:\s*z\.enum\(\[(.*?)\]", txt, re.S)
    if not m:
        print("[!] 无法从 config.ts 解析 category 枚举，跳过该项校验")
        return None
    return set(re.findall(r"[\"']([^\"']+)[\"']", m.group(1)))


def split_frontmatter(path):
    txt = path.read_text(encoding="utf-8")
    if not txt.startswith("---"):
        return None, txt
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return None, txt
    return parts[1], parts[2]


def count_citations(body):
    """统计指向权威域的引用条数（去重）。"""
    seen = set()
    for m in CITE_RE.finditer(body):
        url = m.group(1)
        for d in AUTHORITATIVE_DOMAINS:
            if f"//{d}/" in url or url.startswith(f"https://{d}") or url.startswith(f"http://{d}"):
                seen.add(url)
                break
    return len(seen)


def check_file(path, cat_enum):
    """返回 (errors, warnings, quality)，errors 空 = 可发布。

    errors   = 会让 Astro 构建失败 → 必须拦（否则整站停更）
    warnings = 不影响构建、但影响 SEO 质量 → 只报，可用 --strict 升级为拦
    quality  = AdSense 判定「低价值」的相关项 → 只报，可用 --quality-gate 升级为拦
    """
    errs, warns, quals = [], [], []
    fm, body = split_frontmatter(path)
    if fm is None:
        return ["缺少 frontmatter（文件未以 --- 开头 / 未闭合）"], [], []

    keys = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if m:
            keys[m.group(1)] = m.group(2).strip()

    for f in REQUIRED:
        if f not in keys or keys[f] in ("", "''", '""'):
            errs.append(f"必填字段缺失或为空：{f}")

    for k in keys:
        if k not in KNOWN_FIELDS and k != "slug":  # slug 有专门提示，不重复报
            errs.append(f"未知字段 `{k}`（schema 里没有 → Astro 构建会报错）")

    cat = keys.get("category", "").strip().strip('"').strip("'")
    if cat and cat_enum and cat not in cat_enum:
        errs.append(f"category `{cat}` 不在枚举内 {sorted(cat_enum)}")

    dif = keys.get("difficulty", "").strip().strip('"').strip("'")
    if dif and dif not in DIFFICULTY_ENUM:
        errs.append(f"difficulty `{dif}` 不在枚举内 {sorted(DIFFICULTY_ENUM)}")

    pub = keys.get("pubDate", "").strip().strip('"').strip("'")
    if pub and not re.match(r"^\d{4}-\d{2}-\d{2}", pub):
        errs.append(f"pubDate 格式应为 YYYY-MM-DD，实际 `{pub}`")

    # slug = 文件名，不允许再写 slug 字段（schema 无此字段）
    if "slug" in keys:
        errs.append("frontmatter 含 `slug` 字段，但 schema 未定义（slug 由文件名决定）")

    # 正文至少要有点内容，防空稿上线
    if len(body.strip()) < 400:
        warns.append(f"正文过短（{len(body.strip())} 字符），疑似生成失败")

    # ---------------- 质量闸门 ----------------
    desc = keys.get("description", "").strip().strip('"').strip("'")
    if len(desc) > DESC_MAX:
        quals.append(
            f"description {len(desc)} 字符 > {DESC_MAX}：SERP 会截成半句，损失 CTR"
        )

    faq = len(FAQ_RE.findall(body))
    if faq < FAQ_MIN:
        quals.append(f"FAQ 只有 {faq} 组（要求 ≥{FAQ_MIN}）—— 模板要求，读者也确实会问")

    cites = count_citations(body)
    if cites < CITATION_MIN:
        quals.append(
            "没有任何权威外链（learn.microsoft.com / sqlbi.com）："
            "零引用 = 无法核对，是 low value 最直接的证据"
        )

    words = len(WORD_RE.findall(body))
    if words < WORDS_MIN:
        quals.append(f"正文 {words} 词 < {WORDS_MIN}：不足以解决一个具体问题")

    # 图片引用必须能被静态构建解析，否则 Rollup 报
    # `failed to resolve import "..."` → 整个站点停止部署（比不发布更糟）→ 属 errors
    seen_img = set()
    for m in IMG_RE.finditer(body):
        src = m.group(1)
        if src in seen_img:
            continue
        seen_img.add(src)
        if src.startswith(("http://", "https://", "data:")):
            continue
        if src.startswith("/"):
            if not (PUBLIC_DIR / src.lstrip("/")).exists():
                errs.append(f"图片路径不存在：{src}（public/ 下未找到该文件）")
            continue
        if src == "placeholder":
            errs.append("正文含占位图引用 ![...](placeholder) —— "
                        "Astro 会把它当模块 import，构建直接失败")
        else:
            errs.append(f"图片用了相对路径 `{src}` —— vite 会当模块解析导致构建失败；"
                        f"请改用 /images/... 绝对路径或删除该行")

    # 内链必须指向真实存在的 slug，避免 404（不影响构建，故为 warning）
    dead = set()
    for m in re.finditer(r"\]\(/tutorials/([a-z0-9\-]+)/?\)", body):
        slug = m.group(1)
        if slug in dead:
            continue
        if not (CONTENT_DIR / f"{slug}.md").exists():
            dead.add(slug)
            warns.append(f"404 内链：/tutorials/{slug}/ （无此文章）")

    return errs, warns, quals


def changed_files():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                         cwd=REPO_ROOT, capture_output=True, text=True).stdout
    out += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                          cwd=REPO_ROOT, capture_output=True, text=True).stdout
    return [REPO_ROOT / p for p in out.split()
            if p.endswith(".md") and p.startswith("src/content/tutorials/")]


def main():
    quality_gate = "--quality-gate" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--strict", "--quality-gate")]
    strict = "--strict" in sys.argv
    cat_enum = parse_schema()

    if not args:
        files = sorted(CONTENT_DIR.glob("*.md"))
    elif args == ["--changed"]:
        files = changed_files()
        if not files:
            print("[i] 无改动的文章，跳过校验")
            return 0
    else:
        files = [Path(a) for a in args if Path(a).is_file()]

    bad = warn_only = qual_only = 0
    quality_hits = 0
    for f in files:
        errs, warns, quals = check_file(f, cat_enum)
        if errs:
            bad += 1
            print(f"[✗] {f.name}")
            for e in errs:
                print(f"      - {e}")
            for w in warns + quals:
                print(f"      ~ {w}")
        elif warns or quals:
            warn_only += 1
            label = "质量提示" if (warns or not quals) else "质量提示"
            print(f"[!] {f.name}（可发布，{label}）")
            for w in warns:
                print(f"      ~ {w}")
            for q in quals:
                print(f"      · {q}")
        else:
            qual_only += 1
        quality_hits += len(quals)

    print(f"\n校验 {len(files)} 篇：构建阻断 {bad}，有质量提示 {warn_only}，"
          f"完全干净 {qual_only}")
    if quality_hits:
        print(f"质量项命中 {quality_hits} 条（AdSense Low value content 相关）。")
    if bad:
        print("→ 不合格稿件不要 commit：Astro 构建会失败，整个站点会停更。")
        return 1
    if strict and warn_only:
        print("→ --strict 模式下质量提示也视为失败。")
        return 1
    if quality_gate and quality_hits:
        print("→ --quality-gate 模式：质量项未达标，阻塞发布。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
