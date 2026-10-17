#!/usr/bin/env python3
"""Lint the gv-* grammar visual components. Run from repo root.
   python3 scripts/check_visuals.py [path ...]   (default: manuals shared/visuals)
Needs: pip install beautifulsoup4
Checks: palette contrast (WCAG AA), no words in visuals.css, and for every page using gv-*:
accessible names, scroll regions focusable, timeline numbers valid, label collisions,
known role/tone classes only."""
import os, re, sys
from bs4 import BeautifulSoup

CSS = "shared/styles/visuals.css"
ROLES = {f"gv-r{i}" for i in range(1, 6)}
TONES = {f"gv-tone-{t}" for t in ("a", "b", "c", "d", "e", "past", "present", "future")}
errors = []
def err(where, msg): errors.append(f"{where}: {msg}")

def lum(h):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + .05) / (lb + .05)

def check_css():
    s = open(CSS).read()
    for n in range(1, 6):
        ink = re.search(rf"--gv-{n}-ink:(#\w+)", s).group(1)
        bg = re.search(rf"--gv-{n}-bg:(#\w+)", s).group(1)
        for name, other in (("its tint", bg), ("white", "#ffffff"), ("cream", "#fdfcf8")):
            if ratio(ink, other) < 4.5:
                err(CSS, f"tone {n}: ink {ink} on {name} is {ratio(ink, other):.2f}:1 (< 4.5)")
    for m in re.finditer(r'content:\s*"([^"]*)"', s):   # monolingual guarantee
        if re.search(r"[A-Za-z\u00C0-\u024F\u0370-\u03FF\u0400-\u04FF]", m.group(1)):
            err(CSS, f'content:"{m.group(1)}" contains words; text must come from the page')

def pct(style, var):
    m = re.search(rf"--{var}\s*:\s*([\d.]+)%", style or ""); return float(m.group(1)) if m else None

def check_page(path):
    soup = BeautifulSoup(open(path, errors="ignore").read(), "html.parser")
    if not soup.select("[class*=gv-]"): return 0
    for el in soup.select("[class*=gv-]"):
        for c in el.get("class", []):
            if re.fullmatch(r"gv-r\d+", c) and c not in ROLES: err(path, f"unknown role class {c}")
            if c.startswith("gv-tone-") and c not in TONES: err(path, f"unknown tone class {c}")
    for f in soup.select("figure.gv-timeline"):
        if not (f.get("aria-label") or f.get("aria-labelledby") or f.find("figcaption")):
            err(path, "timeline has no accessible name (figcaption/aria-label)")
        if f.get("tabindex") != "0": err(path, "timeline is a scroll region: needs tabindex=\"0\"")
        items = []
        for li in f.select(".gv-axis > li"):
            cls = li.get("class", []); st = li.get("style", "")
            lab = li.select_one(".gv-label"); text = lab.get_text(strip=True) if lab else ""
            if li.get("aria-hidden") == "true" and not text: continue      # decorative bar
            if not text: err(path, "timeline item without a .gv-label text")
            if "gv-span" in cls:
                a, b = pct(st, "from"), pct(st, "to")
                if a is None or b is None or not (0 <= a < b <= 100): err(path, f"bad span range {a}..{b} ({text})"); continue
                pos, y0 = (a + b) / 2, 1.6
            else:
                pos = pct(st, "at"); y0 = 2.8 if "gv-now" in cls else 1.3
                if pos is None or not (0 <= pos <= 100): err(path, f"bad --at on '{text}'"); continue
            if not text: continue
            w = min(9.0, .5 * len(text)); lines = max(1, -(-int(.5 * len(text) * 100) // 900))
            items.append(dict(pos=pos, below="gv-below" in cls, w=w, y0=y0, y1=y0 + 1.15 * lines, text=text))
        for i, p in enumerate(items):                    # 2-D overlap: same side, 30rem axis
            for q in items[i + 1:]:
                if p["below"] != q["below"]: continue
                if abs(p["pos"] - q["pos"]) * .30 < (p["w"] + q["w"]) / 2 and p["y0"] < q["y1"] and q["y0"] < p["y1"]:
                    err(path, f"timeline labels may overlap: '{p['text']}' / '{q['text']}' (move one with gv-below)")
    for f in soup.select("figure.gv-tree"):
        if not (f.get("aria-label") or f.get("aria-labelledby") or f.find("figcaption")): err(path, "tree has no accessible name")
        if not f.select("ul ul"): err(path, "tree has no branches")
    for f in soup.select(".gv-contrast"):
        if len(f.select(".gv-side")) != 2: err(path, "contrast needs exactly two .gv-side")
        for v in f.select(".gv-vs"):
            if v.get("aria-hidden") != "true": err(path, ".gv-vs must have aria-hidden=\"true\"")
    for f in soup.select(".gv-paradigm"):
        if f.get("tabindex") != "0" or not f.get("aria-label"): err(path, "paradigm needs tabindex=\"0\" and aria-label")
        if not f.find("caption"): err(path, "paradigm table needs a <caption>")
        if [t for t in f.select("th") if not t.get("scope")]: err(path, "paradigm <th> without scope")
    for f in soup.select(".gv-formula"):
        if f.get("role") != "group" or not f.get("aria-label"): err(path, "formula needs role=\"group\" and aria-label")
    return 1

def main():
    roots = sys.argv[1:] or ["manuals", "shared/visuals"]
    check_css(); used = 0
    for r in roots:
        for d, _, fs in os.walk(r):
            for f in fs:
                if f.endswith(".html"): used += check_page(os.path.join(d, f))
    for e in errors[:100]: print("ERROR", e)
    print(f"{len(errors)} problem(s); {used} page(s) use gv-* components")
    sys.exit(1 if errors else 0)

if __name__ == "__main__":
    main()
