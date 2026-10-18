#!/usr/bin/env python3
"""Vendor shields.io badges into assets/badges/ and point README.md at them.

Usage:
    python scripts/vendor_badges.py

What it does
  1. Finds every https://img.shields.io/... image URL in README.md.
  2. Downloads each badge once and saves it as assets/badges/<slug>.svg.
  3. Shields embeds logos as <image href="data:image/svg+xml;base64,...">. GitHub's
     raw file host may block data: URIs, so each embedded logo is decoded and
     inlined as a nested <svg x y width height viewBox> holding the logo paths.
     The saved files contain no <image>, no data: URI, no base64 and no
     external references.
  4. Rewrites the README so each src points at the local file. Every other
     attribute (alt, width, the surrounding <a>) is left untouched.

The URL to slug mapping is stored in assets/badges/manifest.json, so slugs stay
stable and the script is idempotent: with no shields URLs left in the README it
changes nothing. To add a badge, paste its img.shields.io URL into README.md and
run this script again. Standard library only.
"""
import base64
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OUT = ROOT / "assets" / "badges"
MANIFEST = OUT / "manifest.json"
URL_RE = re.compile(r'https://img\.shields\.io/[^"\s)<>]+')
IMAGE_RE = re.compile(r"<image\b([^>]*?)/>|<image\b([^>]*?)></image>", re.S)


def slug_for(url, taken):
    path = url.split("img.shields.io/", 1)[1].split("?", 1)[0]
    if path.startswith("badge/"):
        path = path[len("badge/"):]
    parts = re.split(r"(?<!-)-(?!-)", path)           # "--" is a literal dash in shields paths
    texts = [p for p in parts[:-1] if p] or parts[:1]
    text = " ".join(texts).replace("--", "-").replace("__", "_").replace("_", " ")
    text = urllib.parse.unquote(text)
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if len(slug) > 40:                                  # cut on a word boundary
        slug = slug[:40].rsplit("-", 1)[0]
    slug = slug or "badge"
    base, n = slug, 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    return slug


def fetch(url):
    req = urllib.request.Request(html.unescape(url), headers={"User-Agent": "Mozilla/5.0 (vendor_badges.py)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def attr(text, name):
    m = re.search(r'(?<![\w:-])' + re.escape(name) + r'="([^"]*)"', text)
    return m.group(1) if m else None


def inline_logo(match):
    attrs = match.group(1) or match.group(2) or ""
    href = attr(attrs, "href") or attr(attrs, "xlink:href") or ""
    m = re.match(r"data:image/svg\+xml;base64,(.+)", href, re.S)
    if not m:
        raise ValueError(f"unsupported embedded image: {href[:40]}")
    logo = base64.b64decode(m.group(1)).decode("utf-8")
    root = re.search(r"<svg\b([^>]*)>", logo, re.S)
    inner = logo[root.end():logo.rindex("</svg>")]
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    keep = []
    for name in ("fill", "viewBox", "stroke", "stroke-width", "fill-rule", "clip-rule"):
        v = attr(root.group(1), name)
        if v is not None:
            keep.append(f'{name}="{v}"')
    pos = " ".join(f'{n}="{attr(attrs, n)}"' for n in ("x", "y", "width", "height") if attr(attrs, n) is not None)
    return f"<svg {pos} {' '.join(keep)}>{inner}</svg>"


def vendor(svg):
    out = IMAGE_RE.sub(inline_logo, svg)
    out = out.replace("\r\n", "\n").strip() + "\n"
    for bad in ("<image", "data:", "base64"):
        if bad in out:
            raise ValueError(f"vendored badge still contains {bad!r}")
    if re.search(r'(?:href|src)="https?:', out) or "url(http" in out:
        raise ValueError("vendored badge has an external reference")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    text = README.read_text(encoding="utf-8")
    urls = sorted(set(URL_RE.findall(text)))
    replaced = 0
    for url in urls:
        key = html.unescape(url)
        if key not in manifest:
            manifest[key] = slug_for(key, set(manifest.values()))
        slug = manifest[key]
        target = OUT / f"{slug}.svg"
        if not target.exists():
            target.write_text(vendor(fetch(key)), encoding="utf-8", newline="\n")
            print(f"saved {target.relative_to(ROOT)}")
            time.sleep(0.15)
        replaced += 1
    text = URL_RE.sub(lambda m: f"assets/badges/{manifest[html.unescape(m.group(0))]}.svg", text)
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), indent=2, ensure_ascii=True) + "\n",
                        encoding="utf-8", newline="\n")
    if urls:
        README.write_text(text, encoding="utf-8", newline="\n")
    total = sum(p.stat().st_size for p in OUT.glob("*.svg"))
    print(f"{replaced} shields URL(s) rewritten, {len(list(OUT.glob('*.svg')))} badge files, {total/1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
