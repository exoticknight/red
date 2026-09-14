"""Author RED publication SVG drawings and export PNGs with ImageMagick.

Run from the repository: python scripts/render_methodology_figures.py
Requires ImageMagick with an SVG renderer and Microsoft YaHei (or supply
--font with an installed font covering both Chinese and Latin characters).
SVG is explicit drawing content; ImageMagick handles image rendering.
"""

from pathlib import Path
from html import escape
import argparse
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "methodology" / "assets"
COLORS = ["#276078", "#9A5718", "#AD2432"]
FILLS = ["#EEF5F8", "#FCF4EA", "#FBEEF0"]


def text(x, y, lines, size=24, color="#26333D", bold=False):
    weight = "700" if bold else "400"
    return "".join(
        f'<text x="{x}" y="{y+i*(size+12)}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">{escape(line)}</text>'
        for i, line in enumerate(lines)
    )


def box(x, y, w, h, heading, lines, state=0, size=24):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
        f'fill="{FILLS[state]}" stroke="{COLORS[state]}" stroke-width="2"/>'
        + text(x+24, y+48, [heading], 30, COLORS[state], True)
        + text(x+24, y+92, lines, size)
    )


def arrow(points):
    # Explicit arrowhead keeps the drawing portable across SVG renderers.
    x, y = points[-1]
    px, py = points[-2]
    if y > py:
        tip = [(x-7, y-12), (x+7, y-12), (x, y)]
    elif y < py:
        tip = [(x-7, y+12), (x+7, y+12), (x, y)]
    elif x > px:
        tip = [(x-12, y-7), (x-12, y+7), (x, y)]
    else:
        tip = [(x+12, y-7), (x+12, y+7), (x, y)]
    path = " ".join(f"{a},{b}" for a, b in points)
    triangle = " ".join(f"{a},{b}" for a, b in tip)
    return (f'<polyline points="{path}" fill="none" stroke="#60717D" '
            f'stroke-width="3"/><polygon points="{triangle}" fill="#60717D"/>')


def save(name, width, height, title, desc, body, font):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>'
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>'
        f'<g font-family="{escape(font, quote=True)}">'
        + text(40, 46, ["RED  /  RESEARCH · EVOLVE · DOCUMENT"], 16, "#60717D", True)
        + text(40, 100, [title], 34, "#182831", True)
        + body + '</g></svg>\n'
    )
    path = OUT / f"{name}.svg"
    path.write_text(svg, encoding="utf-8")
    subprocess.run([
        "magick", "-density", "144", "-background", "white", str(path),
        "-alpha", "remove", "-alpha", "off", str(path.with_suffix(".png")),
    ], check=True)
    print(path.relative_to(ROOT))


def states(lang, font, mobile=False):
    zh = lang == "zh"
    headings = ["R · Research", "E · Evolve", "D · Document"]
    lines = ([
        ["处理未知", "问题、证据与假设", "说明已知与调查边界"],
        ["推进变化", "方案、实现与验证", "在获准范围内持续工作"],
        ["维护共识", "目标、接口与规则", "形成后续工作的基线"],
    ] if zh else [
        ["Address unknowns", "Questions and evidence", "Identify assumptions"],
        ["Develop changes", "Design, implement, verify", "Work within authorization"],
        ["Maintain agreements", "Goals, interfaces, rules", "A baseline for future work"],
    ])
    title = "01  三种知识状态" if zh else "01  Three knowledge states"
    body = ""
    for i in range(3):
        x, y, w, h = (40, 150+i*260, 640, 230) if mobile else (40+i*380, 160, 360, 240)
        body += box(x, y, w, h, headings[i], lines[i], i, 30 if mobile else 23)
    note = (["状态说明协作用途。", "证据可信度需要单独判断。"] if zh else
            ["States describe how content is used.", "Evidence quality requires a separate judgment."])
    body += text(40, 970 if mobile else 464, note, 28 if mobile else 24)
    save("red-states."+("wechat" if mobile else lang), 720 if mobile else 1200,
         1070 if mobile else 570, title, " ".join(sum(lines, [])+note), body, font)


def example(lang, font, mobile=False):
    zh = lang == "zh"
    headings = (["R · 下游依赖调查", "E · 可选格式改动", "D · 已接受的规则"] if zh else
                ["R · Dependencies", "E · Optional format", "D · Accepted rule"])
    lines = ([
        ["谁在读取导出文件？", "哪些解析器依赖原格式？", "注明未覆盖的消费者"],
        ["获准增加显式选项", "保留默认导出行为", "验证默认路径与新路径"],
        ["默认：YYYY-MM-DD", "显式选择：本地格式", "记录区域来源与示例"],
    ] if zh else [
        ["Who reads the exports?", "Which parsers depend", "on the existing format?", "Record coverage limits"],
        ["Authorized: add an option", "Preserve default behavior", "Verify both output paths"],
        ["Default: YYYY-MM-DD", "Explicit local-format option", "Define locale and examples"],
    ])
    title = "03  CSV 日期导出案例" if zh else "03  A CSV date-export example"
    if mobile:
        title = "02  从建议到现行规则"
    body = ""
    for i in range(3):
        x, y, w, h = (40, 150+i*260, 640, 230) if mobile else (40+i*380, 160, 360, 280)
        body += box(x, y, w, h, headings[i], lines[i], i, 30 if mobile else 22)
    note = (["研究结果 → 授权推进 → E", "验证结果 → 接受结果 → D"] if zh else
            ["Research findings → authorization → E", "Verified results → acceptance → D"])
    body += text(40, 970 if mobile else 500, note, 28 if mobile else 24)
    save("red-example."+("wechat" if mobile else lang), 720 if mobile else 1200,
         1080 if mobile else 610, title, " ".join(sum(lines, [])+note), body, font)


def transitions(lang, font):
    zh = lang == "zh"
    title = "02  从当前基线到新的共识" if zh else "02  From the current baseline to a new agreement"
    labels = ([
        ("当前 D + 实现证据", ["读取相关规则，检查代码、测试与运行结果"]),
        ("R · 存在关键未知", ["调查可能改变决定的问题", "提交发现、风险与建议范围"]),
        ("明确且已获授权的改动", ["目标与边界清楚", "可以直接进入 E"]),
        ("确认点 1 · 授权推进", ["人或项目授权的决策来源确认范围"]),
        ("E · 设计、实现、验证与修改", ["在获准范围内持续工作", "提交验证证据与拟更新的 D 内容"]),
        ("确认点 2 · 接受具体结果", ["人或项目授权的决策来源审查并接受"]),
        ("同步 D · 形成新的基线", ["只同步被接受的范围，并核对实现"]),
    ] if zh else [
        ("Current D + implementation evidence", ["Read relevant rules; inspect code, tests, and runtime results"]),
        ("R · Critical unknowns", ["Investigate decision-relevant questions", "Present findings, risks, and scope"]),
        ("Clear, authorized change", ["Goals and boundaries are clear", "Direct entry to E is available"]),
        ("Checkpoint 1 · Authorize scope", ["A person or authorized decision source decides"]),
        ("E · Design, implement, verify, revise", ["Continue within the authorized scope", "Present evidence and proposed D changes"]),
        ("Checkpoint 2 · Accept the result", ["A person or authorized decision source reviews and accepts"]),
        ("Synchronize D · Establish a new baseline", ["Update only the accepted scope and check implementation"]),
    ])
    body = box(128, 145, 1032, 125, *labels[0], 2)
    body += arrow([(380, 270), (380, 325)])
    body += arrow([(900, 270), (900, 325)])
    body += box(128, 325, 560, 160, *labels[1], 0, 22)
    body += box(740, 325, 420, 160, *labels[2], 1, 22)
    body += arrow([(400, 485), (400, 530)])
    body += box(128, 530, 680, 125, *labels[3], 0, 23)
    body += arrow([(400, 655), (400, 705)])
    body += arrow([(960, 485), (960, 705)])
    body += box(128, 705, 1032, 160, *labels[4], 1)
    body += arrow([(650, 865), (650, 915)])
    body += box(128, 915, 1032, 125, *labels[5], 1)
    body += arrow([(650, 1040), (650, 1090)])
    body += box(128, 1090, 1032, 125, *labels[6], 2)
    body += arrow([(128, 1150), (65, 1150), (65, 405), (128, 405)])
    note = (["回流：D 与实现证据冲突时，返回 R 调查。", "拒绝：D 不变。部分接受：仅同步被接受的范围。"] if zh else
            ["Return path: conflicts between D and implementation go to R.",
             "Rejection leaves D unchanged. Partial acceptance updates only that scope."])
    body += text(128, 1268, note, 24)
    save(f"red-transitions.{lang}", 1200, 1350, title,
         " ".join(h+". "+" ".join(ls) for h, ls in labels)+" "+" ".join(note), body, font)



def wechat_transitions(font):
    template = ROOT / "scripts" / "assets" / "red-transitions.wechat.svg"
    svg = template.read_text(encoding="utf-8").replace(
        "Microsoft YaHei, Segoe UI, sans-serif",
        escape(font, quote=True) + ", Segoe UI, sans-serif",
    )
    path = OUT / "red-transitions.wechat.svg"
    path.write_text(svg, encoding="utf-8")
    subprocess.run([
        "magick", "-background", "#fffaf7", str(path),
        "-alpha", "remove", "-alpha", "off", str(path.with_suffix(".png")),
    ], check=True)
    print(path.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", default="Microsoft YaHei")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for lang in ("zh", "en"):
        states(lang, args.font)
        transitions(lang, args.font)
        example(lang, args.font)
    states("zh", args.font, mobile=True)
    example("zh", args.font, mobile=True)
    wechat_transitions(args.font)


if __name__ == "__main__":
    main()
