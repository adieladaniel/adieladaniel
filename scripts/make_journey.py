#!/usr/bin/env python3
"""Generate assets/journey.svg: a `git log --graph` style timeline.

Usage:
    python scripts/make_journey.py            (reads scripts/journey.yml)

Needs PyYAML (pip install pyyaml). Output is pure SVG with CSS animation only.

Animation: the command is typed, then the commit graph draws itself top to
bottom, each commit popping in with its hash, date and message. It holds for a
long pause, fades out and loops.
"""
import hashlib
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

HERE = Path(__file__).resolve().parent
W = 960
RH = 36            # row height
Y0 = 128           # y of first commit
LANE_X0 = 40
LANE_DX = 34
HASH_X, DATE_X, MSG_X = 188, 262, 366
CYCLE = 22.0       # seconds for one loop
T_ROWS = 3.0       # first row appears
STEP = 0.44        # delay between rows
BG = "#0d1117"
DIM = "#6b7a8c"
FG = "#d7dee8"
ACCENT = "#7dd3fc"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"


def hash_id(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:7]


def pct(seconds):
    return round(seconds / CYCLE * 100, 3)


def main():
    data = yaml.safe_load((HERE / "journey.yml").read_text(encoding="utf-8"))
    lanes = data["lanes"]
    commits = data["commits"]
    lane_idx = {l["name"]: i for i, l in enumerate(lanes)}
    n = len(commits)
    head = next(i for i, c in enumerate(commits) if c.get("head"))
    height = Y0 + (n - 1) * RH + 74

    def lx(name):
        return LANE_X0 + lane_idx[name] * LANE_DX

    def ly(i):
        return Y0 + i * RH

    def row_time(k):
        return T_ROWS + k * STEP

    # ---- line pieces, one per lane per row gap -------------------------------
    pieces = []  # (row_key, d, color, dashed)
    for lane in lanes:
        name = lane["name"]
        x = lx(name)
        if name == "main":
            for g in range(n - 1):
                pieces.append((g + 1, f"M{x} {ly(g)}V{ly(g+1)}", lane["color"], g >= head))
            continue
        f, m = lane["fork_from"], lane["merge_into"]
        for g in range(f, m):
            xm = lx("main")
            if g == f:
                d = f"M{xm} {ly(g)}C{xm} {ly(g)+RH*0.6:.0f} {x} {ly(g+1)-RH*0.6:.0f} {x} {ly(g+1)}"
            elif g == m - 1:
                d = f"M{x} {ly(g)}C{x} {ly(g)+RH*0.6:.0f} {xm} {ly(g+1)-RH*0.6:.0f} {xm} {ly(g+1)}"
            else:
                d = f"M{x} {ly(g)}V{ly(g+1)}"
            pieces.append((g + 1, d, lane["color"], g >= head))

    # ---- css ------------------------------------------------------------------
    css = []
    css.append(f"text{{font-family:{MONO}}}")
    css.append(f".h{{fill:{DIM};font-size:12.5px}}.d{{font-size:12.5px}}.m{{fill:{FG};font-size:14px}}")
    css.append(".row{animation-duration:%ss;animation-iteration-count:infinite;animation-timing-function:ease-out;animation-fill-mode:both}" % CYCLE)
    css.append(".ln{fill:none;stroke-width:2.4;stroke-linecap:round;animation-duration:%ss;animation-iteration-count:infinite;animation-timing-function:ease-in-out;animation-fill-mode:both}" % CYCLE)
    css.append(".dash{stroke-dasharray:3 6}")
    css.append(".nd{transform-box:fill-box;transform-origin:center;animation-duration:%ss;animation-iteration-count:infinite;animation-fill-mode:both}" % CYCLE)
    for k in range(n + 1):
        s = row_time(k)
        a, b = pct(s), pct(s + 0.38)
        css.append(f"@keyframes r{k}{{0%,{a}%{{opacity:0;transform:translateX(-10px)}}{b}%{{opacity:1;transform:none}}"
                   f"96%{{opacity:1}}98.5%,100%{{opacity:0}}}}")
        a2, b2, c2 = pct(s), pct(s + 0.22), pct(s + 0.5)
        css.append(f"@keyframes p{k}{{0%,{a2}%{{transform:scale(0)}}{b2}%{{transform:scale(1.6)}}{c2}%{{transform:scale(1)}}"
                   f"98.5%{{transform:scale(1)}}100%{{transform:scale(0)}}}}")
        ls = s - 0.3
        a3, b3 = pct(ls), pct(ls + 0.42)
        css.append(f"@keyframes l{k}{{0%,{a3}%{{stroke-dashoffset:1;opacity:1}}{b3}%{{stroke-dashoffset:0}}"
                   f"96%{{opacity:1}}98.5%{{opacity:0;stroke-dashoffset:0}}100%{{stroke-dashoffset:1;opacity:0}}}}")
        css.append(f"@keyframes f{k}{{0%,{a}%{{opacity:0}}{b}%{{opacity:.7}}96%{{opacity:.7}}98.5%,100%{{opacity:0}}}}")
        css.append(f".r{k}{{animation-name:r{k}}}.f{k}{{animation-name:f{k}}}.p{k}{{animation-name:p{k}}}.l{k}{{animation-name:l{k}}}")
    # typing of the command: a cover rectangle slides away in steps
    cmd = data["command"]
    ch = 8.4
    cmd_w = round(len(cmd) * ch + 4)
    steps = len(cmd)
    t0, t1 = 0.6, 2.4
    css.append(f"@keyframes ty{{0%,{pct(t0)}%{{transform:translateX(0)}}{pct(t1)}%,100%{{transform:translateX({cmd_w}px)}}}}")
    css.append(f".cover{{animation:ty {CYCLE}s steps({steps},end) infinite}}")
    css.append("@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}")
    css.append(".cur{animation:blink 1.1s steps(1) infinite}")
    css.append("@keyframes ring{0%{transform:scale(1);opacity:.7}100%{transform:scale(2.6);opacity:0}}")
    css.append(".pulse{transform-box:fill-box;transform-origin:center;animation:ring 2s ease-out infinite}")
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}.cover,.pulse{display:none}}")

    # ---- svg ------------------------------------------------------------------
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" '
             f'role="img" aria-label="Adiel A Daniel career timeline drawn as a git commit graph">')
    o.append("<title>Adiel A Daniel, journey as a git log graph</title>")
    o.append("<style>" + "".join(css) + "</style>")
    o.append(f'<rect width="{W}" height="{height}" rx="14" fill="{BG}"/>')
    o.append(f'<rect x=".75" y=".75" width="{W-1.5}" height="{height-1.5}" rx="13.5" fill="none" stroke="#2a3441" stroke-width="1.5"/>')
    # title bar
    o.append(f'<path d="M0 14a14 14 0 0 1 14-14H{W-14}a14 14 0 0 1 14 14V42H0Z" fill="#161b22"/>')
    o.append('<line x1="0" y1="42" x2="%d" y2="42" stroke="#2a3441"/>' % W)
    for cx, col in ((24, "#ff5f57"), (46, "#febc2e"), (68, "#28c840")):
        o.append(f'<circle cx="{cx}" cy="21" r="6" fill="{col}" opacity=".85"/>')
    o.append(f'<text x="{W/2}" y="26" text-anchor="middle" font-size="13" fill="{DIM}">{escape(data["title"])}</text>')
    # legend
    lx0 = W - 20
    for lane in reversed(lanes):
        label = lane["name"]
        tw = len(label) * 7.4
        lx0 -= tw
        o.append(f'<text x="{lx0:.0f}" y="26" font-size="12" fill="{lane["color"]}">{label}</text>')
        lx0 -= 12
        o.append(f'<circle cx="{lx0+2:.0f}" cy="21.5" r="4" fill="{lane["color"]}"/>')
        lx0 -= 18
    # command line
    o.append(f'<text x="24" y="80" font-size="14" fill="#86efac">adiel@github</text>')
    o.append(f'<text x="125" y="80" font-size="14" fill="{DIM}">:~$</text>')
    cx = 158
    o.append(f'<text x="{cx}" y="80" font-size="14" fill="{FG}" xml:space="preserve">{escape(cmd)}</text>')
    o.append(f'<rect class="cover" x="{cx-1}" y="64" width="{cmd_w+8}" height="22" fill="{BG}"/>')

    # line pieces
    for k, d, color, dashed in pieces:
        if dashed:
            o.append(f'<path class="ln dash f{k}" d="{d}" stroke="{color}"/>')
        else:
            o.append(f'<path class="ln l{k}" d="{d}" pathLength="1" stroke-dasharray="1" stroke="{color}"/>')
    # rows
    for i, c in enumerate(commits):
        lane = lanes[lane_idx[c["lane"]]]
        color = lane["color"]
        x, y = lx(c["lane"]), ly(i)
        future = c.get("future", False)
        o.append(f'<g class="row r{i}">')
        if future:
            o.append(f'<circle class="nd p{i}" cx="{x}" cy="{y}" r="6" fill="{BG}" stroke="{color}" stroke-width="2" stroke-dasharray="3 2.5"/>')
        else:
            o.append(f'<circle class="nd p{i}" cx="{x}" cy="{y}" r="6.2" fill="{color}" stroke="{BG}" stroke-width="2.5"/>')
        if c.get("head"):
            o.append(f'<circle class="pulse" cx="{x}" cy="{y}" r="7" fill="none" stroke="{color}" stroke-width="2"/>')
        op = ' opacity=".6"' if future else ""
        hid = hash_id(c["msg"] + c["date"])
        style = ' font-style="italic"' if future else ""
        o.append(f'<text class="h" x="{HASH_X}" y="{y+4.5}"{op}>{hid}</text>')
        o.append(f'<text class="d" x="{DATE_X}" y="{y+4.5}" fill="{color}"{op}>{escape(c["date"])}</text>')
        o.append(f'<text class="m" x="{MSG_X}" y="{y+4.5}"{op}{style}>{escape(c["msg"])}</text>')
        if c.get("head"):
            mx = MSG_X + len(c["msg"]) * 8.4 + 16
            o.append(f'<rect x="{mx:.0f}" y="{y-10}" width="112" height="20" rx="10" fill="#0f2a3a" stroke="{ACCENT}" stroke-width="1"/>')
            o.append(f'<text x="{mx+56:.0f}" y="{y+4}" font-size="12" fill="{ACCENT}" text-anchor="middle">HEAD -&gt; main</text>')
        o.append("</g>")
    # final prompt
    yp = ly(n - 1) + 50
    o.append(f'<g class="row r{n}"><text x="24" y="{yp}" font-size="14" fill="#86efac">adiel@github</text>'
             f'<text x="125" y="{yp}" font-size="14" fill="{DIM}">:~$</text>'
             f'<rect class="cur" x="160" y="{yp-12}" width="9" height="16" fill="{ACCENT}"/></g>')
    o.append("</svg>")
    svg = "\n".join(o) + "\n"
    out = HERE.parent / "assets" / "journey.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {out}: {len(svg.encode('utf-8'))/1024:.1f} KB, {n} commits")


if __name__ == "__main__":
    sys.exit(main())
