#!/usr/bin/env python3
"""Generate assets/portrait.svg: a halftone "node face" built from vector dots.

Usage:
    python scripts/make_portrait.py PATH_TO_PHOTO [-o assets/portrait.svg]

The photo is read from the path you pass and is never copied or embedded. The
output holds only generated <circle> elements, so no pixel data of the photo is
stored in the repository. The generator is deterministic (fixed random seed).

Animation (pure CSS, works when GitHub renders the SVG as an image):
  1. dots fly in from scattered positions and assemble the face (~2.5 s)
  2. a soft diagonal light wave sweeps across, brightening dots in bands (loop)
"""
import argparse
import math
import random
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

SEED = 2024
# Crop box in source pixels (left, top, right, bottom): head and shoulders.
CROP = (66, 40, 250, 240)
COLS = 116
W = 800            # viewBox width
PAD = 40
N_GROUPS = 10      # animated groups for the assembly (keep this small: it is the per-frame cost)
WAVE_PERIOD = 7.0  # seconds
WAVE_START = 2.8   # seconds, after the assembly
ACCENT = "#7dd3fc"
GAMMA = 1.2
FLOOR = 0.42       # every foreground cell keeps at least this share of the max radius
DIM_BELOW = 0.30   # darker cells (hair, hoodie) are drawn at reduced opacity


def load_mask_and_tone(path):
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img).astype(np.float32)

    # Background: near-white pixels connected to the image border.
    dist = np.sqrt(((255.0 - arr) ** 2).sum(axis=2))
    near_white = dist < 40
    lab, _ = ndimage.label(near_white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    border.discard(0)
    bg = np.isin(lab, list(border))
    fg = ~bg
    fg = ndimage.binary_opening(fg, iterations=1)
    fg = ndimage.binary_fill_holes(fg)
    fg = ndimage.binary_erosion(fg, iterations=1)  # drop light anti-aliased fringe
    # keep the largest component only
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = lab == (1 + int(np.argmax(sizes)))

    # Tone: weight red a little more so skin reads brighter than the olive hoodie.
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    gray = 0.50 * r + 0.38 * g + 0.12 * b
    # Neutral fill outside the subject so the white backdrop does not halo the edges.
    gray = np.where(fg, gray, gray[fg].mean() * 0.8)
    return img, gray, fg


def prepare(path):
    img, gray, fg = load_mask_and_tone(path)
    l, t, r, b = CROP
    gray_im = Image.fromarray(np.clip(gray, 0, 255).astype(np.uint8)).crop(CROP)
    fg_im = Image.fromarray((fg * 255).astype(np.uint8)).crop(CROP)

    cw, ch = r - l, b - t
    rows = int(round(COLS * ch / cw))
    up = 4
    gray_im = gray_im.resize((COLS * up, rows * up), Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=6, percent=120, threshold=2))
    fg_im = fg_im.resize((COLS * up, rows * up), Image.LANCZOS)

    # Local contrast (CLAHE) so skin keeps mid-tones and eyes, brows, nose and mouth separate.
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_im = Image.fromarray(clahe.apply(np.asarray(gray_im)))
    g = np.asarray(gray_im).astype(np.float32)
    m = np.asarray(fg_im).astype(np.float32) / 255.0
    # Block average per cell.
    g = g.reshape(rows, up, COLS, up).mean(axis=(1, 3))
    m = m.reshape(rows, up, COLS, up).mean(axis=(1, 3))
    return g, m, rows


def tone_map(g, m):
    inside = m > 0.5
    vals = g[inside]
    lo, hi = np.percentile(vals, 2), np.percentile(vals, 98)
    t = np.clip((g - lo) / (hi - lo), 0, 1)
    # A little extra local detail, then a gamma that pulls skin down into mid-tones.
    blur = ndimage.gaussian_filter(t, 4)
    t = np.clip(t + 0.6 * (t - blur), 0, 1)
    return t ** GAMMA


def build(path, out):
    g, m, rows = prepare(path)
    t = tone_map(g, m)

    inner = W - 2 * PAD
    cell = inner / COLS
    H = int(round(rows * cell + 2 * PAD))
    rng = random.Random(SEED)

    # Soft fade toward the bottom so the shoulders melt into the card.
    fade_start = 0.86
    ys = np.arange(rows) / (rows - 1)
    fade = np.where(ys > fade_start, 1 - np.clip((ys - fade_start) / (1 - fade_start), 0, 1) ** 1.5 * 0.85, 1.0)

    # Tone the hoodie down a little so the face stays the brightest part.
    body = 1 - 0.34 * np.clip((ys - 0.52) / 0.2, 0, 1)
    xs = np.abs(np.arange(COLS) / (COLS - 1) - 0.5) * 2
    xfade = 1 - np.clip((xs - 0.72) / 0.28, 0, 1) ** 1.4 * 0.9
    groups = {}
    count = 0
    for j in range(rows):
        for i in range(COLS):
            if m[j, i] < 0.5:
                continue
            tv = t[j, i] * body[j]
            r = cell * 0.5 * (FLOOR + (1 - FLOOR) * tv) * fade[j] * xfade[i]
            if r < 0.8:
                continue
            dim = tv < DIM_BELOW
            x = PAD + (i + 0.5) * cell
            y = PAD + (j + 0.5) * cell
            k = rng.randrange(N_GROUPS)
            groups.setdefault(k, []).append((round(x), round(y), round(r, 1), dim))
            count += 1

    # Scatter vectors per class (units in viewBox px).
    scat = []
    for k in range(N_GROUPS):
        ang = rng.uniform(0, 2 * math.pi)
        dist = rng.uniform(260, 620)
        scat.append((round(math.cos(ang) * dist), round(math.sin(ang) * dist)))

    keys = sorted(groups)
    css = []
    css.append("svg{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace}")
    # Assembly: one transform animation per group (a few dozen elements in total).
    css.append(".f{animation:fly 1.8s cubic-bezier(.16,.84,.24,1) both}")
    for k, (dx, dy) in enumerate(scat):
        css.append(f".s{k}{{--x:{dx}px;--y:{dy}px;animation-delay:{k * 0.08:.2f}s}}")
    css.append("@keyframes fly{from{transform:translate(var(--x),var(--y));opacity:0}"
               "55%{opacity:1}to{transform:translate(0,0);opacity:1}}")
    # Wave: a single gradient band slides across; the masked dots are static.
    css.append(f".band{{animation:sweep {WAVE_PERIOD}s ease-in-out {WAVE_START}s infinite both}}")
    css.append("@keyframes sweep{0%{transform:translateX(-640px)}72%,100%{transform:translateX(640px)}}")
    css.append(".tag{fill:#6b7a8c;font-size:15px;letter-spacing:.08em}")
    css.append("@media (prefers-reduced-motion:reduce){.f,.band{animation:none!important}.band{display:none}}")

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
                 f'width="{W}" height="{H}" role="img" aria-label="Halftone dot portrait of Adiel A Daniel">')
    parts.append("<title>Adiel A Daniel, halftone node portrait</title>")
    parts.append("<style>" + "".join(css) + "</style>")
    parts.append('<defs><radialGradient id="glow" cx="50%" cy="42%" r="65%">'
                 '<stop offset="0" stop-color="#16202c"/><stop offset="1" stop-color="#0b0f14"/>'
                 '</radialGradient>'
                 f'<linearGradient id="band" x1="0" x2="1" y1="0" y2="0">'
                 f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/>'
                 f'<stop offset=".38" stop-color="{ACCENT}" stop-opacity=".9"/>'
                 '<stop offset=".5" stop-color="#ffffff"/>'
                 f'<stop offset=".62" stop-color="{ACCENT}" stop-opacity=".9"/>'
                 f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>')
    # Every dot is written once, inside static groups in <defs>.
    for n, key in enumerate(keys):
        parts.append(f'<g id="g{n}">')
        for x, y, r, dim in groups[key]:
            fo = ' fill-opacity=".72"' if dim else ""
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r}"{fo}/>')
        parts.append("</g>")
    parts.append(f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><g fill="#fff">'
                 + "".join(f'<use href="#g{n}" xlink:href="#g{n}"/>' for n in range(len(keys)))
                 + "</g></mask></defs>")
    parts.append(f'<rect width="{W}" height="{H}" rx="28" fill="url(#glow)"/>')
    parts.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="27" fill="none" stroke="#2a3441" stroke-width="2"/>')
    # Visible dots: animated <use> per group (assembly only).
    parts.append('<g fill="#e6ebf2">')
    for n, k in enumerate(keys):
        parts.append(f'<use class="f s{k}" href="#g{n}" xlink:href="#g{n}"/>')
    parts.append("</g>")
    # Highlight: one moving band, clipped to the dots by the mask.
    parts.append(f'<g mask="url(#m)"><g transform="translate({W/2:.0f} {H/2:.0f}) rotate(34)">'
                 '<rect class="band" x="-190" y="-1100" width="380" height="2200" fill="url(#band)"/></g></g>')
    parts.append(f'<circle cx="{PAD - 4}" cy="{H - 26}" r="5" fill="{ACCENT}"/>')
    parts.append(f'<text class="tag" x="{PAD + 12}" y="{H - 21}">node map // {count} points</text>')
    parts.append("</svg>")
    svg = "\n".join(parts) + "\n"
    Path(out).write_text(svg, encoding="utf-8", newline="\n")
    return count, len(svg.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", help="path to the source photo (stays outside the repo)")
    ap.add_argument("-o", "--out", default=str(Path(__file__).resolve().parent.parent / "assets" / "portrait.svg"))
    a = ap.parse_args()
    if not Path(a.photo).is_file():
        sys.exit(f"photo not found: {a.photo}")
    n, size = build(a.photo, a.out)
    print(f"wrote {a.out}: {n} dots, {size/1024:.0f} KB")


if __name__ == "__main__":
    main()
