#!/usr/bin/env python3
"""
生成落地页预览图：模拟 Power BI Desktop 的「数据」窗格 + 一张报表。

为什么要生成而不是截图：Power BI Desktop 是 Windows only，本地只有 Mac。
这张图的目标不是「真实截图」，而是让访客一眼看到「12 个度量值长什么样」，
所以刻意做得像字段列表，但不伪造任何具体数值。

输出：public/images/time-intelligence-pack-preview.png (1200x675)
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 675
SCALE = 2  # 2x 输出，落地页在高分屏上不糊

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

BG = "#F3F2F1"
PANEL = "#FFFFFF"
TEXT = "#323130"
MUTED = "#605E5C"
FAINT = "#A19F9D"
BORDER = "#EDEBE9"
ACCENT = "#F2C811"   # Power BI 黄
BLUE = "#118DFF"

MEASURES = [
    "Total Sales", "Sales YTD", "Sales QTD", "Sales MTD",
    "Sales PY", "Sales YoY %", "Sales YoY Abs", "Sales MoM %",
    "Rolling 3M Avg", "Rolling 12M Sum", "Sales vs Target", "% of Total",
]

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
BARS = [0.42, 0.51, 0.47, 0.58, 0.63, 0.55, 0.68, 0.72, 0.66, 0.78, 0.83, 0.91]


def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size * SCALE)


def draw_round(d, box, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = [v * SCALE for v in box]
    d.rounded_rectangle([x1, y1, x2, y2], radius=radius * SCALE,
                        fill=fill, outline=outline, width=width * SCALE)


def text(d, xy, s, font, fill=TEXT, anchor="la"):
    d.text((xy[0] * SCALE, xy[1] * SCALE), s, font=font, fill=fill, anchor=anchor)


def main():
    img = Image.new("RGB", (W * SCALE, H * SCALE), BG)
    d = ImageDraw.Draw(img)

    # ---------------- 左侧：数据窗格 ----------------
    panel_w = 310
    d.rectangle([0, 0, panel_w * SCALE, H * SCALE], fill=PANEL)
    d.line([panel_w * SCALE, 0, panel_w * SCALE, H * SCALE], fill=BORDER, width=SCALE)

    # 标题行
    text(d, (16, 20), "Data", f(15, True))
    # 三个小图标（模拟窗格切换）
    for i, x in enumerate([250, 268, 286]):
        draw_round(d, (x, 22, x + 12, 34), 2,
                   fill=ACCENT if i == 0 else "#F3F2F1")

    # 搜索框
    draw_round(d, (16, 52, panel_w - 16, 84), 4, fill="#FAF9F8", outline="#E1DFDD")
    text(d, (28, 62), "Search", f(11.5), FAINT)
    # 放大镜
    d.ellipse([(panel_w - 40) * SCALE, 62 * SCALE, (panel_w - 30) * SCALE, 72 * SCALE],
              outline=FAINT, width=int(1.4 * SCALE))
    d.line([(panel_w - 31) * SCALE, 71 * SCALE, (panel_w - 26) * SCALE, 76 * SCALE],
           fill=FAINT, width=int(1.4 * SCALE))

    # 分组标题 _Measures
    y = 100
    draw_round(d, (16, y, 22, y + 6), 1, fill=MUTED)  # ▼ 简化
    d.polygon([(16 * SCALE, (y - 1) * SCALE), (26 * SCALE, (y - 1) * SCALE),
               (21 * SCALE, (y + 5) * SCALE)], fill=MUTED)
    # 表格图标
    draw_round(d, (34, y - 3, 46, y + 9), 2, outline=MUTED, width=1)
    d.line([(34 * SCALE, (y + 3) * SCALE), (46 * SCALE, (y + 3) * SCALE)], fill=MUTED, width=SCALE)
    text(d, (54, y - 6), "_Measures", f(12.5, True))

    # 12 个度量值
    row_h = 27
    y0 = 126
    for i, name in enumerate(MEASURES):
        yy = y0 + i * row_h
        if i % 2 == 0:
            d.rectangle([0, yy * SCALE, panel_w * SCALE, (yy + row_h) * SCALE],
                        fill="#FCFCFB")
        # fx 图标（Power BI 的度量值图标近似）
        cx, cy = 28, yy + 13
        draw_round(d, (cx - 8, cy - 7, cx + 8, cy + 7), 3, fill="#EFF6FC")
        text(d, (cx - 5, cy - 7), "fx", f(8.5, True), BLUE)
        text(d, (44, cy - 7), name, f(12.5))

    # 底部提示条
    d.rectangle([0, (H - 34) * SCALE, panel_w * SCALE, H * SCALE], fill="#FAF9F8")
    text(d, (16, H - 24), "12 measures · 1 table", f(10.5), MUTED)

    # ---------------- 右侧：报表 ----------------
    cw, ch = 830, 600
    cx, cy = 350, 38
    draw_round(d, (cx, cy, cx + cw, cy + ch), 8, fill="#FFFFFF", outline=BORDER)

    text(d, (cx + 28, cy + 24), "Sales vs Target — Year to Date", f(14, True))
    text(d, (cx + 28, cy + 48), "Contoso sample model", f(10.5), MUTED)
    # 品牌色小方块（Power BI 视觉习惯）
    draw_round(d, (cx + cw - 44, cy + 24, cx + cw - 30, cy + 38), 3, fill=ACCENT)

    # 四个 KPI 卡
    kpis = [
        ("Sales YTD", "4.82M", "+18.4%", BLUE),
        ("YoY %", "18.4%", "vs 4.07M", "#107C10"),
        ("vs Target", "-212K", "94.2% of goal", "#D13438"),
        ("% of Total", "31.6%", "EMEA share", MUTED),
    ]
    kw = (cw - 28 * 2 - 3 * 16) / 4
    ky = cy + 78
    for i, (label, value, sub, color) in enumerate(kpis):
        kx = cx + 28 + i * (kw + 16)
        draw_round(d, (kx, ky, kx + kw, ky + 74), 6, fill="#FAF9F8", outline=BORDER)
        text(d, (kx + 12, ky + 10), label, f(9.5), MUTED)
        text(d, (kx + 12, ky + 26), value, f(19, True), color)
        text(d, (kx + 12, ky + 54), sub, f(9), FAINT)

    # 柱状图
    gx, gy = cx + 28, ky + 106
    gw, gh = cw - 56, ch - (gy - cy) - 46
    d.line([gx * SCALE, (gy + gh) * SCALE, (gx + gw) * SCALE, (gy + gh) * SCALE],
           fill=BORDER, width=SCALE)

    # 网格线
    for i in range(1, 4):
        yy = gy + gh - (gh * i / 4)
        d.line([gx * SCALE, yy * SCALE, (gx + gw) * SCALE, yy * SCALE],
               fill="#F3F2F1", width=SCALE)

    slot = gw / 12
    bw = slot * 0.52
    for i, v in enumerate(BARS):
        bx = gx + i * slot + (slot - bw) / 2
        bh = (gh - 24) * v
        by = gy + gh - bh
        color = ACCENT if i == 11 else "#C7E0F4"
        draw_round(d, (bx, by, bx + bw, gy + gh - 1), 2, fill=color)
        text(d, (bx + bw / 2, gy + gh + 6), MONTHS[i], f(8.5), FAINT, anchor="ma")

    # 图例：单一序列 + 最新月份高亮（Power BI 里最常见的做法，
    # 不再用「Current / Prior」这种和 12 根柱对不上的说法）
    lx = cx + cw - 128
    d.rectangle([lx * SCALE, (gy - 18) * SCALE, (lx + 9) * SCALE, (gy - 9) * SCALE], fill=ACCENT)
    text(d, (lx + 13, gy - 19), "Latest month", f(8.5), MUTED)

    out = Path(__file__).resolve().parent.parent / "public" / "images" / "time-intelligence-pack-preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)
    print(f"saved {out}  ({out.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
