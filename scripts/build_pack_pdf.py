#!/usr/bin/env python3
"""
把 lead-magnet/README.md 转成排版良好的 PDF。

为什么需要：下载包的人很多是在手机上看落地页，下载后打开 .md 看到的是一堆
星号和竖线。README 是这份包唯一的说明文档，读不下去等于包是坏的。

做法：markdown → docx（python-docx，只处理 README 用到的元素）→ PDF
（LibreOffice Kit）。特意只支持必要子集，不引第三方 markdown 库。

用法：
  python scripts/build_pack_pdf.py
"""
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Inches

REPO = Path(__file__).resolve().parent.parent
SRC = REPO.parent / "lead-magnet" / "README.md"
OUT_DOCX = REPO.parent / "lead-magnet" / "_README.docx"
OUT_PDF = REPO.parent / "lead-magnet" / "README.pdf"

NODE = "/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
CLI = "/Applications/DeepSeek Harness.app/Contents/Resources/app.asar.unpacked/dsh/node_modules/@deepseek-ai/libreoffice-kit/lib/cli.js"


def add_rich(paragraph, text):
    """处理 **bold** 和 `code`，其余原样。"""
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            r = paragraph.add_run(part[2:-2]); r.bold = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = paragraph.add_run(part[1:-1])
            r.font.name = "Menlo"
            r.font.size = Pt(9)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            r = paragraph.add_run(part[1:-1]); r.italic = True
        else:
            paragraph.add_run(part)


def build_docx(md_path, out_path):
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Helvetica"
    style.font.size = Pt(10.5)
    style.paragraph_format.space_after = Pt(7)
    style.paragraph_format.line_spacing = 1.35

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    raw = md_path.read_text(encoding="utf-8").splitlines()

    # markdown 里一个段落可以跨多行（尤其引用块里跨行的行内代码）。
    # 逐行渲染会把一段话拆成好几个段落，这是第一版 PDF 最难看的毛病。
    blocks, buf, kind = [], [], None

    def flush():
        nonlocal buf, kind
        if buf:
            blocks.append((kind, buf))
        buf, kind = [], None

    for line in raw:
        stripped = line.strip()
        if stripped.startswith("```"):
            # flush() 会把 kind 重置为 None，所以必须先记住进来时是不是在代码块里，
            # 否则每个结束 fence 都会被当成开始，代码块一路吞到文末。
            was_code = (kind == "code")
            flush()
            kind = None if was_code else "code"
            continue
        # 代码块必须先判断，且保留原始缩进 —— 放在后面会被当段落收集，
        # 换行就丢了，M 代码会挤成一行。
        if kind == "code":
            buf.append(line)
            continue
        if not stripped:
            flush(); continue
        if stripped.startswith("|"):
            if kind != "table": flush(); kind = "table"
            buf.append(stripped); continue
        if stripped.startswith("#"):
            flush(); blocks.append(("heading", [stripped])); continue
        if stripped.startswith(">"):
            if kind != "quote": flush(); kind = "quote"
            buf.append(stripped.lstrip(">").strip()); continue
        m = re.match(r"^(\d+\.|[-*])\s+", stripped)
        if m:
            flush()
            blocks.append(("li", [stripped]))
            continue
        if kind in ("code", "table", "quote") and buf and kind != "p":
            buf.append(stripped); continue
        if kind != "p":
            flush(); kind = "p"
        buf.append(stripped)
    flush()

    for kind, buf in blocks:
        if kind == "code":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            r = p.add_run("\n".join(buf))
            r.font.name = "Menlo"
            r.font.size = Pt(8.5)
            continue

        if kind == "table":
            rows = [r for r in buf if not re.match(r"^\|[\s:-]+\|", r)]
            if not rows: continue
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            ncols = max(len(r) for r in cells)
            t = doc.add_table(rows=len(cells), cols=ncols)
            t.style = "Light Grid Accent 1"
            for ri, row in enumerate(cells):
                for ci in range(ncols):
                    cell = t.cell(ri, ci); cell.text = ""
                    cp = cell.paragraphs[0]
                    cp.paragraph_format.space_after = Pt(2)
                    add_rich(cp, row[ci] if ci < len(row) else "")
                    for run in cp.runs:
                        run.font.size = Pt(9)
                        if ri == 0: run.bold = True
            doc.add_paragraph()
            continue

        text = " ".join(buf)

        if kind == "heading":
            m = re.match(r"^(#{1,3})\s+(.*)$", text)
            level = len(m.group(1))
            h = doc.add_heading(level=level)
            add_rich(h, m.group(2))
            for run in h.runs:
                run.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
            continue

        if kind == "li":
            m = re.match(r"^(\d+\.|[-*])\s+(.*)$", text)
            style_name = "List Number" if m.group(1)[0].isdigit() else "List Bullet"
            p = doc.add_paragraph(style=style_name)
            add_rich(p, m.group(2))
            continue

        if kind == "quote":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            add_rich(p, text)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            continue

        if set(text) <= {"-", " "}:
            doc.add_paragraph(); continue

        p = doc.add_paragraph()
        add_rich(p, text)
        if text.startswith("*") and text.endswith("*") and not text.startswith("**"):
            for run in p.runs:
                run.italic = True

    doc.save(out_path)
    return out_path


def to_pdf(docx_path, pdf_path):
    if pdf_path.exists():
        pdf_path.unlink()   # LibreOffice Kit 不会覆盖已有文件
    r = subprocess.run(
        [NODE, CLI, "convert", "--input", str(docx_path), "--output", str(pdf_path)],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-800:]); print(r.stderr[-800:])
        return False
    return True


def main():
    if not SRC.exists():
        print(f"[!] 找不到 {SRC}")
        return 1
    build_docx(SRC, OUT_DOCX)
    print(f"docx: {OUT_DOCX}")
    if to_pdf(OUT_DOCX, OUT_PDF):
        print(f"pdf : {OUT_PDF}  ({OUT_PDF.stat().st_size/1024:.0f} KB)")
    else:
        print("[!] PDF 转换失败，docx 保留")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
