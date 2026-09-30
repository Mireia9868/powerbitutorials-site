#!/usr/bin/env python3
"""
文章 frontmatter 校验 —— 发布前拦住会让 Astro 构建失败的稿件。

为什么需要：云端 publish.yml 生成文章后直接 commit/push，真正构建在 Cloudflare。
如果 frontmatter 与 src/content/config.ts 的 schema 不符（字段名错、enum 越界、
日期格式非法），Astro 构建会失败 → 整个站点停更（比不发布更糟）。本脚本在
push 之前先验，失败就中止并告警。

用法：
  python scripts/validate_content.py                     # 校验全部文章
  python scripts/validate_content.py <file.md> [...]     # 只校验指定文件
  python scripts/validate_content.py --changed           # 只校验 git 改动的 .md
  python scripts/validate_content.py --strict            # 质量提示也算失败（404 内链等）

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

# 正文图片引用：Astro/vite 会把「非绝对路径」的 src 当模块去 import。
# 一次 ![Figure 1: ...](placeholder) 就能让整站构建失败（2026-09-29 实际发生）。
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")


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


def check_file(path, cat_enum):
    """返回 (errors, warnings)，errors 空 = 可发布。

    errors   = 会让 Astro 构建失败 → 必须拦（否则整站停更）
    warnings = 不影响构建、但影响质量 → 只报，可用 --strict 升级为拦
    """
    errs, warns = [], []
    fm, body = split_frontmatter(path)
    if fm is None:
        return ["缺少 frontmatter（文件未以 --- 开头 / 未闭合）"], []

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

    return errs, warns


def changed_files():
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                         cwd=REPO_ROOT, capture_output=True, text=True).stdout
    out += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                          cwd=REPO_ROOT, capture_output=True, text=True).stdout
    return [REPO_ROOT / p for p in out.split()
            if p.endswith(".md") and p.startswith("src/content/tutorials/")]


def main():
    args = [a for a in sys.argv[1:] if a != "--strict"]
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

    bad = warn_only = 0
    for f in files:
        errs, warns = check_file(f, cat_enum)
        if errs:
            bad += 1
            print(f"[✗] {f.name}")
            for e in errs:
                print(f"      - {e}")
            for w in warns:
                print(f"      ~ {w}")
        elif warns:
            warn_only += 1
            print(f"[!] {f.name}（可发布，质量提示）")
            for w in warns:
                print(f"      ~ {w}")

    print(f"\n校验 {len(files)} 篇：合格 {len(files) - bad - warn_only}，"
          f"仅质量提示 {warn_only}，构建会被阻断 {bad}")
    if bad:
        print("→ 不合格稿件不要 commit：Astro 构建会失败，整个站点会停更。")
        return 1
    if strict and warn_only:
        print("→ --strict 模式下质量提示也视为失败。")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
