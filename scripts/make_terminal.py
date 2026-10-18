#!/usr/bin/env python3
"""Generate assets/terminal.svg: a terminal boot header that types itself out.

Usage:
    python scripts/make_terminal.py

Pure SVG + CSS. Each line is revealed by a cover rectangle that shrinks in
steps (a typing effect), then a cursor blinks at the end. Plays once and holds.
"""
from pathlib import Path
from xml.sax.saxutils import escape

W = 600
LH = 24                      # line height
CH = 8.4                     # char width at 14px monospace
X0 = 26
Y0 = 84
BG, FG, DIM = "#0d1117", "#d7dee8", "#6b7a8c"
ACCENT, VIOLET, GREEN, AMBER = "#7dd3fc", "#a78bfa", "#86efac", "#fbbf24"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

# (kind, content, start_seconds, duration_seconds)
# kinds: cmd (prompt + typed command), out (typed output, accent), plain (typed output),
#        kv (key, value), blank, cursor
LINES = [
    ("cmd", "whoami", 0.4, 0.6),
    ("name", "Adiel A Daniel", 1.2, 0.7),
    ("blank",),
    ("cmd", "cat role.txt", 2.2, 0.8),
    ("plain", "AI/ML engineer in the making", 3.2, 0.7),
    ("plain", "B.Tech CSE (AI & ML), Christ University '27", 3.7, 0.9),
    ("blank",),
    ("cmd", "neofetch", 4.8, 0.6),
    ("host", "adiel@github", 5.5, 0.4),
    ("rule", "------------", 5.7, 0.3),
    ("kv", "focus", "agentic AI, multimodal ML, RAG", 5.9, 0.7),
    ("kv", "stack", "Python, FastAPI, PyTorch, LangGraph", 6.2, 0.8),
    ("kv", "since", "coding since Jul 2024", 6.5, 0.7),
    ("kv", "based", "Bangalore, India", 6.8, 0.6),
    ("kv", "status", "open to AI/ML, GenAI and data roles", 7.1, 0.9),
    ("palette", 7.6, 0.3),
    ("blank",),
    ("prompt", 8.2),
]


def main():
    out = []
    css = [
        f"text{{font-family:{MONO};font-size:14px}}",
        "@keyframes show{from{opacity:0}to{opacity:1}}",
        "@keyframes cv{to{transform:scaleX(0)}}",
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}",
        ".l{animation:show .01s steps(1) both}",
        ".cover{transform-box:fill-box;transform-origin:right center;animation-fill-mode:both}",
        ".cur{animation:blink 1.1s steps(1) infinite}",
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.cover{display:none}}",
    ]
    body = []
    y = Y0
    for ln in LINES:
        kind = ln[0]
        if kind == "blank":
            y += LH // 2 + 2
            continue
        if kind == "prompt":
            start = ln[1]
            body.append(f'<g class="l" style="animation-delay:{start}s">'
                        f'<text x="{X0}" y="{y}" fill="{GREEN}">$</text>'
                        f'<rect class="cur" x="{X0+16}" y="{y-12}" width="9" height="16" fill="{ACCENT}"/></g>')
            y += LH
            continue
        if kind == "palette":
            start, dur = ln[1], ln[2]
            sw = []
            for i, c in enumerate([ACCENT, VIOLET, GREEN, AMBER, FG, DIM]):
                sw.append(f'<rect x="{X0 + 78*0 + i*22}" y="{y-12}" width="18" height="14" rx="3" fill="{c}"/>')
            body.append(f'<g class="l" style="animation-delay:{start}s">{"".join(sw)}</g>')
            y += LH
            continue
        if kind == "cmd":
            _, text, start, dur = ln
            x_text = X0 + 2 * CH
            w = len(text) * CH + 2
            cover = (f'<rect class="cover" x="{x_text-1:.0f}" y="{y-14}" width="{w+4:.0f}" height="20" fill="{BG}" '
                     f'style="animation-name:cv;animation-duration:{dur}s;animation-delay:{start}s;'
                     f'animation-timing-function:steps({len(text)},end)"/>')
            body.append(f'<g class="l" style="animation-delay:{start}s">'
                        f'<text x="{X0}" y="{y}" fill="{GREEN}">$</text>'
                        f'<text x="{x_text:.0f}" y="{y}" fill="{FG}">{escape(text)}</text>{cover}</g>')
            y += LH
            continue
        # output kinds
        if kind == "kv":
            _, key, val, start, dur = ln
            full = key.ljust(8) + val
            text_svg = (f'<text x="{X0}" y="{y}" xml:space="preserve"><tspan fill="{VIOLET}" font-weight="700">{escape(key.ljust(8))}</tspan>'
                        f'<tspan fill="{FG}">{escape(val)}</tspan></text>')
        else:
            _, text, start, dur = ln
            full = text
            color = {"name": ACCENT, "host": ACCENT, "rule": DIM, "plain": FG}[kind]
            weight = ' font-weight="700"' if kind in ("name", "host") else ""
            size = ' font-size="16"' if kind == "name" else ""
            text_svg = f'<text x="{X0}" y="{y}" fill="{color}"{weight}{size}>{escape(text)}</text>'
        w = len(full) * CH * (1.15 if kind == "name" else 1) + 6
        n = max(1, len(full))
        cover = (f'<rect class="cover" x="{X0-2}" y="{y-16}" width="{w:.0f}" height="24" fill="{BG}" '
                 f'style="animation-name:cv;animation-duration:{dur}s;animation-delay:{start}s;'
                 f'animation-timing-function:steps({n},end)"/>')
        body.append(f'<g class="l" style="animation-delay:{start}s">{text_svg}{cover}</g>')
        y += LH
    H = y + 22

    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
               f'aria-label="Terminal: whoami prints Adiel A Daniel, AI/ML engineer in the making, based in Bangalore, India">')
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
    print(f"wrote {dest}: {len(svg.encode('utf-8'))/1024:.1f} KB")


if __name__ == "__main__":
    main()
