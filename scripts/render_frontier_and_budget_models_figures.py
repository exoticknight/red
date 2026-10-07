"""Render the figures for the budget-model article in Chinese and English.

Run from the repository root: python scripts/render_frontier_and_budget_models_figures.py
Writes methodology/assets/frontier-and-budget-models-{cost,relay,quota}.{zh,en}.{svg,png}.
Requires ImageMagick (`magick`) and Microsoft YaHei, like render_methodology_figures.py.
"""

from pathlib import Path
from html import escape
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "methodology" / "assets"
BLUE, RED, GRAY, BRAND = "#1F6FA3", "#AD2432", "#C9CED2", "#C1121F"
INK, MUTED, SOFT, BODY = "#182831", "#60717D", "#788087", "#30383c"

# Usage totals from the author's usage statistics; replacements use each model's
# average price over the same period (cache reads included).
PREMIUM = 450.54
MIXED_DAILY = 34.2
DAILY_AS = {"astra": 2129, "opus5": 1023, "sol": 921}

TEXT = {
    "zh": {
        "tag": "高模开局，低模接手",
        "footer_brand": "Research · Evolve · Document",
        "cost_title": "不一味用贵模型，换成搭配着用，比全用顶级模型省下 81%",
        "cost_desc": "同一个多月约 19 亿 token 的开发，按 API 均价估算。日常也用 GPT-6 Astra 约 2580 美元，也用 Claude Opus 5 约 1474，也用 GPT-5.6 Sol 约 1371；高低模搭配实际约 485 美元，分别省下 81%、67%、65%。",
        "cost_h1": "不一味用贵模型，换成搭配着用",
        "cost_h2": "比全用顶级模型，省下 81%",
        "cost_sub": "同一个多月、约 19 亿 token 的开发，按 API 均价估算",
        "cost_legend": ["高价模型实际用量 $451（开局、重大功能、审查，四根相同）", "日常 14.3 亿 token 也用贵模型（估算）", "日常换成便宜模型（实际）"],
        "cost_daily_too": "日常也用它", "cost_mixed": "搭配使用", "cost_actual": "实际", "cost_save": "换成搭配 省 {}",
        "cost_notes": ["数据：作者用量统计，主要来自 7 个 DSH 相关项目。实际为订阅制，费用为 API 等价估算；", "换算按各模型同期实际均价（含缓存），只看量级。"],
        "relay_title": "交接靠文档，不靠会话",
        "relay_desc": "贵模型负责决定、编排和审查，便宜模型负责执行；两者都从项目里的 R、E、D 读起，也写回这里，彼此不直接交接。",
        "relay_sub": "贵模型、便宜模型都从同一份 R、E、D 读起，也写回这里",
        "relay_premium": ("贵模型", "开局讨论 · 重大功能 · 代码审查"),
        "relay_budget": ("便宜模型", "日常开发 · 维护 · 查问题"),
        "relay_docs": "项目里的文档",
        "relay_rows": ["还在调查的：问题和证据", "正在推进的：范围、验收、不做的事", "已经定下来的：目标、接口、规则"],
        "relay_read": "读", "relay_write": "写回", "relay_side": ["不靠", "会话", "交接"],
        "relay_notes": ["换模型、换会话、换工具，都从这份文档接着干。"],
        "quota_title": "同样一个 Plus 套餐，Luna 能多发约 70 倍消息",
        "quota_desc": "Codex 官方估算，Plus 套餐每五小时本地消息数：GPT-6 Astra 5 到 45 条，GPT-6 Luna 350 到 3000 条。",
        "quota_h1": "同样一个 Plus 套餐", "quota_h2": "Luna 能多发约 70 倍",
        "quota_sub": "Codex 官方估算：每五小时能发的本地消息数",
        "quota_count": "{:,} 条", "quota_range": "区间 {:,}–{:,}", "quota_tiers": ("顶级", "便宜"),
        "quota_notes": ["来源：OpenAI Codex 定价页（learn.chatgpt.com/docs/pricing）。柱高取区间上限；", "官方说明这是估算，不是固定上限，另可能有每周限额。"],
    },
    "en": {
        "tag": "Frontier to start, budget to carry on ·",
        "footer_brand": "Research · Evolve · Document",
        "cost_title": "Mixing models costs 81% less than running everything on a frontier model",
        "cost_desc": "About 1.94 billion tokens over a month, priced at average API rates. Daily work on GPT-6 Astra as well would total about $2,580, on Claude Opus 5 about $1,474, on GPT-5.6 Sol about $1,371; the actual mix cost about $485, saving 81%, 67% and 65%.",
        "cost_h1": "Don't run everything on frontier models",
        "cost_h2": "Mix them: 81% cheaper",
        "cost_sub": "About 1.94B tokens over a month, at average API prices",
        "cost_legend": ["Premium models, actual: $451 (kickoff, major features, review; same in all four)", "Daily 1.43B tokens on the same model too (estimate)", "Daily work on budget models (actual)"],
        "cost_daily_too": "daily work too", "cost_mixed": "Mixed", "cost_actual": "actual", "cost_save": "saves {}",
        "cost_notes": ["Data: author's usage, mostly from 7 DSH-related projects. Plans are subscriptions;", "costs are API-equivalent estimates at each model's average price (cache included)."],
        "relay_title": "Hand off through docs, not chats",
        "relay_desc": "The premium model decides, orchestrates and reviews; the budget model executes. Both read from and write back to the project's R, E and D, never handing off through a chat.",
        "relay_sub": "Both models read from, and write back to, the same R, E and D",
        "relay_premium": ("Premium model", "Kickoff · Major features · Code review"),
        "relay_budget": ("Budget model", "Daily development · Maintenance · Debugging"),
        "relay_docs": "Project documents",
        "relay_rows": ["Still under investigation: questions, evidence", "In progress: scope, acceptance, what's out", "Settled: goals, interfaces, rules"],
        "relay_read": "read", "relay_write": "write back", "relay_side": ["no", "chat", "handoff"],
        "relay_notes": ["Switch models, sessions or tools, and pick up from the same documents."],
        "quota_title": "On the same Plus plan, Luna sends about 70 times more messages",
        "quota_desc": "Codex estimates of local messages per five hours on Plus: GPT-6 Astra 5 to 45, GPT-6 Luna 350 to 3,000.",
        "quota_h1": "Same Plus plan", "quota_h2": "Luna sends ~70× more",
        "quota_sub": "Codex estimate: local messages per five hours",
        "quota_count": "{:,}", "quota_range": "range {:,}–{:,}", "quota_tiers": ("frontier", "budget"),
        "quota_notes": ["Source: learn.chatgpt.com/docs/pricing. Bars show the upper bound.", "OpenAI calls these estimates, not fixed limits; weekly limits may apply."],
    },
}


def t(x, y, s, size, color=INK, bold=False, anchor="middle"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>'


def logo(x, y, k=1.0):
    # Three ascending tiles from the RED wordmark.
    return "".join(
        f'<rect x="{x+i*8*k:.1f}" y="{y+(2-i)*6*k:.1f}" width="{6*k:.1f}" height="{(10+i*6)*k:.1f}" rx="{1.6*k:.1f}" fill="{BRAND}" opacity="{op}"/>'
        for i, op in enumerate([.35, .65, 1])
    )


def open_svg(w, h, title, desc, tx):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
        f'<rect width="{w}" height="{h}" fill="#FFFFFF"/><g font-family="Microsoft YaHei">',
        logo(40, 34, 0.9),
        f'<text x="76" y="52" font-size="18" font-weight="700" text-anchor="start"><tspan fill="{MUTED}">{escape(tx["tag"])}  with </tspan><tspan fill="{BRAND}">RED</tspan></text>',
    ]


def close_svg(o, w, h, notes, tx):
    for i, n in enumerate(notes):
        o.append(t(40, h - 104 - 24 * (len(notes) - 1 - i), n, 15, SOFT, False, "start"))
    o.append(f'<rect x="0" y="{h-76}" width="{w}" height="76" fill="#FFFAF7"/><line x1="0" y1="{h-76}" x2="{w}" y2="{h-76}" stroke="#E8DDD7" stroke-width="2"/>')
    o.append(logo(40, h - 52, 1.4))
    o.append(t(84, h - 29, "RED", 24, BRAND, True, "start"))
    o.append(t(140, h - 30, tx["footer_brand"], 15, MUTED, False, "start"))
    o.append(t(w - 40, h - 30, "github.com/exoticknight/red", 16, BODY, True, "end"))
    o.append('</g></svg>')
    return "".join(o)


def cost(tx):
    w, h, base, maxh, top = 720, 1090, 800, 400, 2580
    o = open_svg(w, h, tx["cost_title"], tx["cost_desc"], tx)
    o += [t(40, 104, tx["cost_h1"], 30, INK, True, "start"), t(40, 162, tx["cost_h2"], 44, RED, True, "start"),
          t(40, 204, tx["cost_sub"], 18, MUTED, False, "start")]
    for i, (c, label) in enumerate(zip([BLUE, GRAY, RED], tx["cost_legend"])):
        y = 250 + i * 30
        o.append(f'<rect x="40" y="{y-14}" width="18" height="18" rx="3" fill="{c}"/>')
        o.append(t(68, y, label, 16, BODY, False, "start"))
    bars = [("GPT-6 Astra", tx["cost_daily_too"], DAILY_AS["astra"], GRAY, "$2,580", "81%"),
            ("Claude Opus 5", tx["cost_daily_too"], DAILY_AS["opus5"], GRAY, "$1,474", "67%"),
            ("GPT-5.6 Sol", tx["cost_daily_too"], DAILY_AS["sol"], GRAY, "$1,371", "65%"),
            (tx["cost_mixed"], tx["cost_actual"], MIXED_DAILY, RED, "$485", None)]
    for cx, (name, sub, daily, c, total, save) in zip([120, 280, 440, 600], bars):
        y = base
        for v, col in [(PREMIUM, BLUE), (daily, c)]:
            hh = max(6, maxh * v / top)
            y -= hh
            o.append(f'<rect x="{cx-55}" y="{y:.1f}" width="110" height="{hh:.1f}" fill="{col}" stroke="#FFFFFF" stroke-width="2"/>')
        o.append(t(cx, y - 14, total, 28, RED if c == RED else INK, True))
        o.append(t(cx, base + 36, name, 18, RED if c == RED else "#26333D", True))
        o.append(t(cx, base + 62, sub, 15, MUTED))
        if save:
            o.append(t(cx, base + 92, tx["cost_save"].format(save), 17, RED, True))
    o.append(f'<line x1="40" y1="{base}" x2="{w-40}" y2="{base}" stroke="#9AA3A9" stroke-width="2"/>')
    return close_svg(o, w, h, tx["cost_notes"], tx)


def relay(tx):
    w, h = 720, 1040
    o = open_svg(w, h, tx["relay_title"], tx["relay_desc"], tx)
    o += [t(40, 110, tx["relay_title"], 34, INK, True, "start"), t(40, 152, tx["relay_sub"], 18, MUTED, False, "start")]

    def model_box(y, c, fill, names):
        return [f'<rect x="120" y="{y}" width="480" height="110" rx="14" fill="{fill}" stroke="{c}" stroke-width="2"/>',
                t(360, y + 48, names[0], 28, c, True), t(360, y + 84, names[1], 18, BODY)]

    o += model_box(196, BLUE, "#EEF4F9", tx["relay_premium"])
    dy = 402
    o.append(f'<rect x="80" y="{dy}" width="560" height="262" rx="16" fill="#FFFAF7" stroke="#E8DDD7" stroke-width="2"/>')
    o.append(logo(108, dy + 24, 1.3))
    o.append(t(152, dy + 46, tx["relay_docs"], 22, INK, True, "start"))
    for i, (k, v, op) in enumerate(zip("RED", tx["relay_rows"], [.5, .75, 1])):
        y = dy + 78 + i * 58
        o.append(f'<rect x="108" y="{y}" width="504" height="46" rx="8" fill="#FFFFFF" stroke="#E8DDD7"/>')
        o.append(f'<rect x="108" y="{y}" width="46" height="46" rx="8" fill="{BRAND}" opacity="{op}"/>')
        o.append(t(131, y + 31, k, 22, "#FFFFFF", True))
        o.append(t(172, y + 30, v, 18, BODY, False, "start"))
    o += model_box(730, RED, "#FBEEF0", tx["relay_budget"])

    def arrows(y1, y2, c):
        s = []
        for x, up in [(300, False), (420, True)]:
            a, b = (y2, y1) if up else (y1, y2)
            s.append(f'<line x1="{x}" y1="{a}" x2="{x}" y2="{b-10 if b > a else b+10}" stroke="{c}" stroke-width="3"/>')
            d = -1 if b > a else 1
            s.append(f'<path d="M{x-8} {b+d*12} L{x} {b} L{x+8} {b+d*12} Z" fill="{c}"/>')
        s.append(t(292, (y1 + y2) / 2 + 6, tx["relay_read"], 17, c, True, "end"))
        s.append(t(428, (y1 + y2) / 2 + 6, tx["relay_write"], 17, c, True, "start"))
        return s

    o += arrows(306, 402, BLUE)
    o += arrows(664, 730, RED)
    o.append('<path d="M620 251 C 700 251, 700 785, 620 785" fill="none" stroke="#9AA3A9" stroke-width="2" stroke-dasharray="7 6"/>')
    o.append(f'<circle cx="680" cy="518" r="15" fill="#FFFFFF" stroke="#9AA3A9" stroke-width="2"/><path d="M670 508 L690 528 M690 508 L670 528" stroke="{RED}" stroke-width="3"/>')
    o.append('<rect x="652" y="542" width="56" height="66" fill="#FFFFFF"/>')
    for i, word in enumerate(tx["relay_side"]):
        o.append(t(680, 560 + i * 20, word, 15, MUTED))
    return close_svg(o, w, h, tx["relay_notes"], tx)


def quota(tx):
    w, h, base, maxh = 720, 920, 660, 300
    o = open_svg(w, h, tx["quota_title"], tx["quota_desc"], tx)
    o += [t(40, 110, tx["quota_h1"], 32, INK, True, "start"), t(40, 168, tx["quota_h2"], 48, RED, True, "start"),
          t(40, 210, tx["quota_sub"], 18, MUTED, False, "start")]
    for cx, name, tier, lo, hi, c in [(200, "GPT-6 Astra", tx["quota_tiers"][0], 5, 45, GRAY), (520, "GPT-6 Luna", tx["quota_tiers"][1], 350, 3000, RED)]:
        bh = max(8, maxh * hi / 3000)
        o.append(f'<rect x="{cx-95}" y="{base-bh}" width="190" height="{bh}" rx="6" fill="{c}"/>')
        o.append(t(cx, base - bh - 50, tx["quota_count"].format(hi), 44, RED if c == RED else INK, True))
        o.append(t(cx, base - bh - 18, tx["quota_range"].format(lo, hi), 16, MUTED))
        o.append(t(cx, base + 40, name, 22, RED if c == RED else "#26333D", True))
        o.append(t(cx, base + 68, tier, 16, MUTED))
    o.append(f'<line x1="40" y1="{base}" x2="{w-40}" y2="{base}" stroke="#9AA3A9" stroke-width="2"/>')
    return close_svg(o, w, h, tx["quota_notes"], tx)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for lang, tx in TEXT.items():
        for name, draw in [("cost", cost), ("relay", relay), ("quota", quota)]:
            svg = OUT / f"frontier-and-budget-models-{name}.{lang}.svg"
            svg.write_text(draw(tx), encoding="utf-8")
            subprocess.run(["magick", "-density", "192", str(svg), "-resize", "1440x", str(svg.with_suffix(".png"))], check=True)
            print(f"Wrote {svg.relative_to(ROOT)} and PNG")


if __name__ == "__main__":
    main()
