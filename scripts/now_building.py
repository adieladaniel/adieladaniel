#!/usr/bin/env python3
"""Generate assets/now-building.svg from the public GitHub REST API.

Usage:
    python scripts/now_building.py [-o assets/now-building.svg]

Picks the most recently pushed public, non-fork repository of the user (the
profile repository itself is excluded) and draws a small animated card with its
description, language, last push time and latest commit message.

Uses only the standard library. GITHUB_TOKEN is used when set (higher rate
limit); otherwise requests are unauthenticated.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = "adieladaniel"
PROFILE_REPO = "adieladaniel"
CODING_SINCE = dt.date(2024, 7, 1)  # started coding around Jul 2024
API = "https://api.github.com"

W = 860
BG, FG, DIM = "#0d1117", "#d7dee8", "#6b7a8c"
ACCENT, VIOLET, GREEN = "#7dd3fc", "#a78bfa", "#86efac"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Java": "#b07219",
    "HTML": "#e34c26", "CSS": "#563d7c", "C": "#555555", "C++": "#f34b7d",
    "Jupyter Notebook": "#DA5B0B", "Shell": "#89e051",
}


def api_get(path):
    req = urllib.request.Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "adieladaniel-profile-readme",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def relative(then, now):
    secs = max(0, int((now - then).total_seconds()))
    if secs < 90:
        return "just now"
    mins = secs // 60
    if mins < 60:
        return f"{mins} minutes ago"
    hours = mins // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


def clean(text):
    text = re.sub(r"[\x00-\x1f\x7f]", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def truncate(text, limit):
    text = clean(text)
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def wrap(text, width, max_lines):
    words, lines, cur = clean(text).split(" "), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = truncate(lines[-1], width - 3).rstrip(".") + "..."
    return lines


def pick_repo():
    repos = api_get(f"/users/{USER}/repos?type=owner&sort=pushed&direction=desc&per_page=100")
    for repo in repos:
        if repo.get("fork") or repo.get("private") or repo.get("archived"):
            continue
        if repo["name"].lower() == PROFILE_REPO.lower():
            continue
        return repo
    raise SystemExit("no public non-fork repository found")


def latest_commit(repo):
    try:
        commits = api_get(f"/repos/{USER}/{repo['name']}/commits?per_page=1")
        return clean(commits[0]["commit"]["message"].splitlines()[0])
    except (urllib.error.URLError, IndexError, KeyError, ValueError):
        return ""


def render(repo, commit_msg, now):
    pushed = dt.datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    desc_lines = wrap(repo.get("description") or "No description yet.", 92, 2)
    lang = repo.get("language") or "Mixed"
    lang_color = LANG_COLORS.get(lang, VIOLET)
    days = (now.date() - CODING_SINCE).days
    updated = now.date().isoformat()
    when = f"{pushed.day} {pushed.strftime('%b %Y')}"  # absolute date: the card is only rebuilt daily
    commit = truncate(commit_msg, 78) if commit_msg else "no commit message available"

    y_desc = 100
    desc_svg = "".join(
        f'<text x="28" y="{y_desc + i * 21}" font-size="14" fill="{FG}">{escape(line)}</text>'
        for i, line in enumerate(desc_lines)
    )
    meta_y = y_desc + len(desc_lines) * 21 + 12
    h = meta_y + 46
    lang_w = len(lang) * 8.2
    when_x = 50 + lang_w + 28
    commit_y = meta_y + 26
    name = escape(repo["name"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="Currently building {name}">
<title>Currently building: {name}</title>
<style>
text{{font-family:{MONO}}}
@keyframes pulse{{0%{{transform:scale(1);opacity:.8}}100%{{transform:scale(3);opacity:0}}}}
@keyframes sweep{{0%{{transform:translateX(-200px)}}100%{{transform:translateX({W}px)}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:pulse 1.8s ease-out infinite}}
.sweep{{animation:sweep 5s linear infinite}}
.cur{{animation:blink 1.1s steps(1) infinite}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.ring{{display:none}}}}
</style>
<defs>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}" stop-opacity="0"/><stop offset=".5" stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
<clipPath id="card"><rect width="{W}" height="{h}" rx="14"/></clipPath>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{BG}"/>
<rect x=".75" y=".75" width="{W-1.5}" height="{h-1.5}" rx="13.5" fill="none" stroke="#2a3441" stroke-width="1.5"/>
<g clip-path="url(#card)"><rect class="sweep" x="0" y="{h-3}" width="200" height="3" fill="url(#sw)"/></g>
<circle class="ring" cx="34" cy="32" r="5" fill="{GREEN}"/>
<circle cx="34" cy="32" r="5" fill="{GREEN}"/>
<text x="50" y="36" font-size="12.5" fill="{GREEN}" letter-spacing=".12em">LIVE  CURRENTLY BUILDING</text>
<text x="{W-28}" y="36" font-size="12" fill="{DIM}" text-anchor="end">updated {updated}</text>
<text x="28" y="72" font-size="20" font-weight="700" fill="{ACCENT}">{escape(USER)}/{name}</text>
{desc_svg}
<circle cx="35" cy="{meta_y - 4}" r="6" fill="{lang_color}"/>
<text x="50" y="{meta_y}" font-size="13" fill="{FG}">{escape(lang)}</text>
<text x="{when_x:.0f}" y="{meta_y}" font-size="13" fill="{DIM}">last push {escape(when)}</text>
<text x="{W-28}" y="{meta_y}" font-size="13" fill="{VIOLET}" text-anchor="end">coding since Jul 2024: {days} days</text>
<text x="28" y="{commit_y}" font-size="13" fill="{DIM}">latest commit</text>
<text x="132" y="{commit_y}" font-size="13" fill="{FG}">{escape(commit)}</text>
<rect class="cur" x="{132 + len(commit) * 7.8 + 6:.0f}" y="{commit_y - 11}" width="7" height="14" fill="{ACCENT}"/>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(Path(__file__).resolve().parent.parent / "assets" / "now-building.svg"))
    args = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    try:
        repo = pick_repo()
        commit = latest_commit(repo)
    except (urllib.error.URLError, ValueError) as exc:
        print(f"GitHub API request failed: {exc}", file=sys.stderr)
        return 1
    svg = render(repo, commit, now)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {out}: {repo['name']} ({len(svg.encode('utf-8'))/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
