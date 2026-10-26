#!/usr/bin/env python3
"""
把过长的 meta description 压到 SERP 可完整显示的宽度。

背景：Google 在搜索结果里显示约 155–160 字符，超出部分被截掉。
本站 52/87 条描述超过 160（最长 324），等于把后半句白白浪费。
根因是 generate_article.py 里把上限写成了 190（已修为 150）。

这里只做「压缩」，不重写语义：优先保留第一句；第一句仍然超长时，
在词边界截断并补句号。压缩后的文案建议再人工过一遍，
尤其是 GSC 里有曝光的页面 —— 描述直接影响 CTR。

用法：
  python scripts/fix_descriptions.py --dry-run
  python scripts/fix_descriptions.py
"""
import re
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "src" / "content" / "tutorials"
MAX = 155
MIN = 90  # 压缩后太短就没信息量，宁可保留原样让人工改


def squeeze(desc):
    """返回压缩后的描述；无法安全压缩时返回 None。"""
    desc = desc.strip()
    if len(desc) <= MAX:
        return None

    # 1) 第一句够短就直接用第一句
    m = re.match(r"^(.{50,}?[.!?])(\s|$)", desc)
    if m and MIN <= len(m.group(1)) <= MAX:
        return m.group(1).strip()

    # 2) 在词边界截断
    cut = desc[:MAX]
    if " " not in cut:
        return None
    cut = cut[: cut.rfind(" ")].rstrip(" ,;:-")
    if cut and cut[-1] not in ".!?":
        cut += "."
    return cut if len(cut) >= MIN else None


def main():
    dry = "--dry-run" in sys.argv
    changed = skipped = 0
    for p in sorted(CONTENT.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r'^description:\s*"(.*)"\s*$', text, re.M)
        if not m:
            continue
        old = m.group(1)
        new = squeeze(old)
        if new is None:
            if len(old) > MAX:
                skipped += 1
                print(f"[skip] {p.stem}: {len(old)} 字符，未能安全压缩")
            continue
        changed += 1
        print(f"[{len(old)}→{len(new)}] {p.stem}")
        print(f"    - {old}")
        print(f"    + {new}")
        if not dry:
            text = text.replace(m.group(0), f'description: "{new}"', 1)
            p.write_text(text, encoding="utf-8")
    print(f"\n压缩 {changed} 条，跳过 {skipped} 条{'（dry-run，未落盘）' if dry else ''}")


if __name__ == "__main__":
    main()
