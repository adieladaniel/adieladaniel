#!/usr/bin/env python3
"""Generate assets/terminal.svg: a terminal intro that types itself out.

Usage:
    python scripts/make_terminal.py

Pure SVG + CSS, built the same way as journey.svg so it also animates when
GitHub shows it inside an <img> tag: no inline style attributes, no
animation-delay, and every line has its own class and its own @keyframes
written as percentages of one shared infinite cycle. Each line is revealed by a
cover rectangle that shrinks in steps (typing). Everything types in the first
~11 s, holds, fades out and restarts. With prefers-reduced-motion the final
state is shown.
"""
from pathlib import Path
from xml.sax.saxutils import escape

W = 600
LH = 23                      # line height
CH = 8.4                     # char width at 14px monospace
X0 = 26
Y0 = 82
CYCLE = 26.0                 # seconds for one loop
BG, FG, DIM = "#0d1117", "#d7dee8", "#6b7a8c"
ACCENT, VIOLET, GREEN, AMBER = "#7dd3fc", "#a78bfa", "#86efac", "#fbbf24"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# (kind, ...) in display order. Typing times are assigned automatically.
LINES = [
    ("cmd", "whoami"),
    ("name", "Adiel A Daniel"),
    ("blank",),
    ("cmd", "cat about.txt"),
    ("plain", "Final-year B.Tech CSE (AI & ML) at Christ University,"),
    ("plain", "Bangalore ('27). I build AI systems that do real work:"),
    ("plain", "LLM analytics pipelines, browser agents with human"),
    ("plain", "approval gates, and multimodal diagnostic models."),
    ("blank",),
    ("cmd", "neofetch"),
    ("host", "adiel@github"),
    ("rule", "------------"),
    ("kv", "role", "AI/ML engineer in the making"),
    ("kv", "focus", "agentic AI, multimodal ML, RAG"),
    ("kv", "likes", "building agents that do real work,"),
    ("kv", "", "with a human in the loop"),
    ("kv", "now", "MedReasonAI: multimodal diagnosis"),
    ("kv", "stack", "Python, PyTorch, LangGraph, FastAPI"),
    ("kv", "since", "coding since Jul 2024"),
    ("kv", "based", "Bangalore, India, open to relocation"),
    ("kv", "status", "open to AI/ML, GenAI and data roles"),
    ("palette",),
    ("blank",),
    ("prompt",),
]


def pct(seconds):
    return round(seconds / CYCLE * 100, 3)


def main():
    t = 0.5                  # running clock (seconds)
    plan = []                # (start, duration) per line, None for blank lines
    for ln in LINES:
        kind = ln[0]
        if kind == "blank":
            t += 0.15
            plan.append(None)
            continue
        if kind == "cmd":
            dur = 0.045 * len(ln[1]) + 0.15
            plan.append((t, dur))
            t += dur + 0.25
        elif kind in ("palette", "prompt"):
            plan.append((t, 0.25))
            t += 0.35
        else:
            text = ln[1] if kind != "kv" else ln[1].ljust(8) + ln[2]
            dur = min(0.55, 0.01 * len(text) + 0.15)
            plan.append((t, dur))
            t += dur + 0.06
    end_time = t

    css = [
        f"text{{font-family:{MONO};font-size:14px}}",
        f".l,.cv{{animation-duration:{CYCLE}s;animation-iteration-count:infinite;animation-fill-mode:both;animation-timing-function:linear}}",
        ".cv{transform-box:fill-box;transform-origin:right center}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
        ".cur{animation:blink 1.1s steps(1) infinite}",
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.cv{display:none}}",
    ]
    body = []
    y = Y0
    for i, (ln, pl) in enumerate(zip(LINES, plan)):
        kind = ln[0]
        if kind == "blank":
            y += LH // 2 + 1
            continue
        start, dur = pl
        a, b = pct(start), pct(start + dur)
        css.append(
            f"@keyframes l{i}{{0%,{a}%{{opacity:0}}{pct(start + 0.01)}%,96%{{opacity:1}}98.5%,100%{{opacity:0}}}}"
            f".l{i}{{animation-name:l{i}}}")
        cover = ""
        n = 1
        if kind == "cmd":
            text = ln[1]
            n = len(text)
            x_text = X0 + 2 * CH
            w = len(text) * CH + 4
            svg_line = (f'<text x="{X0}" y="{y}" fill="{GREEN}">$</text>'
                        f'<text x="{x_text:.0f}" y="{y}" fill="{FG}">{escape(text)}</text>')
            cover = f'<rect class="cv c{i}" x="{x_text-1:.0f}" y="{y-14}" width="{w:.0f}" height="20" fill="{BG}"/>'
        elif kind == "prompt":
            svg_line = (f'<text x="{X0}" y="{y}" fill="{GREEN}">$</text>'
                        f'<rect class="cur" x="{X0+16}" y="{y-12}" width="9" height="16" fill="{ACCENT}"/>')
        elif kind == "palette":
            svg_line = "".join(
                f'<rect x="{X0 + k*22}" y="{y-12}" width="18" height="14" rx="3" fill="{c}"/>'
                for k, c in enumerate([ACCENT, VIOLET, GREEN, AMBER, FG, DIM]))
        else:
            if kind == "kv":
                key, val = ln[1], ln[2]
                full = key.ljust(8) + val
                svg_line = (f'<text x="{X0}" y="{y}" xml:space="preserve">'
                            f'<tspan fill="{VIOLET}" font-weight="700">{escape(key.ljust(8))}</tspan>'
                            f'<tspan fill="{FG}">{escape(val)}</tspan></text>')
            else:
                text = ln[1]
                full = text
                color = {"name": ACCENT, "host": ACCENT, "rule": DIM, "plain": FG}[kind]
                weight = ' font-weight="700"' if kind in ("name", "host") else ""
                size = ' font-size="16"' if kind == "name" else ""
                svg_line = f'<text x="{X0}" y="{y}" fill="{color}"{weight}{size}>{escape(text)}</text>'
            n = max(1, len(full))
            w = len(full) * CH * (1.15 if kind == "name" else 1) + 8
            cover = f'<rect class="cv c{i}" x="{X0-2}" y="{y-16}" width="{w:.0f}" height="24" fill="{BG}"/>'
        if cover:
            css.append(
                f"@keyframes c{i}{{0%,{a}%{{transform:scaleX(1);animation-timing-function:steps({n},end)}}"
                f"{b}%,99.9%{{transform:scaleX(0)}}100%{{transform:scaleX(1)}}}}"
                f".c{i}{{animation-name:c{i}}}")
        body.append(f'<g class="l l{i}">{svg_line}{cover}</g>')
        y += LH
    H = y + 18

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
               f'aria-label="Terminal: whoami prints Adiel A Daniel; about.txt and neofetch describe his work, focus and location">')
    out.append("<title>Adiel A Daniel, terminal intro</title>")
    out.append("<style>" + "".join(css) + "</style>")
    out.append(f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>')
    out.append(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="13.5" fill="none" stroke="#2a3441" stroke-width="1.5"/>')
    out.append(f'<path d="M0 14a14 14 0 0 1 14-14H{W-14}a14 14 0 0 1 14 14V42H0Z" fill="#161b22"/>')
    out.append(f'<line x1="0" y1="42" x2="{W}" y2="42" stroke="#2a3441"/>')
    for cx, col in ((24, "#ff5f57"), (46, "#febc2e"), (68, "#28c840")):
        out.append(f'<circle cx="{cx}" cy="21" r="6" fill="{col}" opacity=".85"/>')
    out.append(f'<text x="{W/2}" y="26" text-anchor="middle" font-size="13" fill="{DIM}">adiel@github: ~</text>')
    out.extend(body)
    out.append("</svg>")
    svg = "\n".join(out) + "\n"
    dest = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {dest}: {len(svg.encode('utf-8'))/1024:.1f} KB, typing done at {end_time:.1f}s of {CYCLE:.0f}s, height {H}")


if __name__ == "__main__":
    main()
