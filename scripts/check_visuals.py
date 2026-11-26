#!/usr/bin/env python3
"""Lint the gv-* grammar visual components. Run from repo root.
   python3 scripts/check_visuals.py [path ...]   (default: manuals shared/visuals)
Needs: pip install beautifulsoup4
Checks: palette contrast (WCAG AA), no words in visuals.css, and for every page using gv-*:
accessible names, scroll regions focusable, timeline numbers valid, label collisions,
known role/tone classes only."""
import json, os, re, sys
from bs4 import BeautifulSoup

CSS = "shared/styles/visuals.css"
ROLES = {f"gv-r{i}" for i in range(1, 6)}
TONES = {f"gv-tone-{t}" for t in ("a", "b", "c", "d", "e", "past", "present", "future")}
TABLE_IDS = set()
try:
    TABLE_IDS = set(json.load(open("data/grammar/table_index.json", encoding="utf-8"))["tables"])
except Exception:
    pass
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
        if re.search(r"[A-Za-z\u00C0-\u024F\u0370-\u03FF\u0400-\u04FF]", re.sub(r"\\[0-9a-fA-F]{1,6}", "", m.group(1))):   # ignore CSS escapes like \00a0
            err(CSS, f'content:"{m.group(1)}" contains words; text must come from the page')

def pct(style, var):
    m = re.search(rf"--{var}\s*:\s*([\d.]+)%", style or ""); return float(m.group(1)) if m else None

def check_page(path):
    soup = BeautifulSoup(open(path, errors="ignore").read(), "html.parser")
    noscope = [t for t in soup.select("table th") if not t.get("scope")]
    if noscope: err(path, f"{len(noscope)} table header cell(s) without scope (run scripts/upgrade_tables.py)")
    for w in soup.select("div.table-wrap"):
        if w.get("role") != "region" or not w.get("aria-label") or w.get("tabindex") != "0":
            err(path, "table-wrap must be a named, focusable region (run scripts/upgrade_tables.py)"); break
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
    for f in soup.select("figure.gv-case-map"):
        if not (f.get("aria-label") or f.get("aria-labelledby") or f.find("figcaption")):
            err(path, "case map has no accessible name (figcaption/aria-label)")
        roles = f.select(".gv-case-role")
        if len(roles) < 2: err(path, "case map needs at least two .gv-case-role items")
        for role in roles:
            word = role.find("b")
            label = role.find("small")
            if not word or not word.get_text(strip=True): err(path, "case map role needs a <b> word")
            if not label or not label.get_text(strip=True): err(path, "case map role needs a <small> case label")
        for arrow in f.select(".gv-case-arrow"):
            if arrow.get("aria-hidden") != "true": err(path, "case map arrows must have aria-hidden=\"true\"")
    for f in soup.select(".gv-paradigm"):
        if f.get("tabindex") != "0" or not f.get("aria-label"): err(path, "paradigm needs tabindex=\"0\" and aria-label")
        if not f.find("caption"): err(path, "paradigm table needs a <caption>")
        if [t for t in f.select("th") if not t.get("scope")]: err(path, "paradigm <th> without scope")
    for f in soup.select(".gv-paradigm[data-table-id]"):
        table_id = f.get("data-table-id")
        if TABLE_IDS and table_id not in TABLE_IDS: err(path, f"unknown data-table-id {table_id}")
        if f.get("data-source") != "cosytools": err(path, "embedded table must declare data-source=\"cosytools\"")
        source_url = f.get("data-source-url", "")
        if not source_url.startswith("https://cosylanguages.github.io/COSYtools/"):
            err(path, "embedded table source-url must point at COSYtools")
        if not re.fullmatch(r"[0-9a-f]{16}", f.get("data-source-hash", "")):
            err(path, "embedded table needs a 16-character data-source-hash")
        if not f.find("table"): err(path, "embedded table is not rendered (run scripts/embed_grammar_tables.py)")
        source = f.select_one(".gv-source a")
        if not source or source.get("href") != source_url:
            err(path, "embedded table needs a .gv-source link to its COSYtools source")
    for f in soup.select(".gv-open"):
        if not (f.get("aria-label") or f.get("aria-labelledby")): err(path, "opening needs aria-labelledby or aria-label")
        if not f.select_one(".gv-theme") or not f.select_one(".gv-theme").get_text(strip=True): err(path, "opening needs a .gv-theme (vocabulary theme) with text")
        if len(f.select(".gv-lines > li")) < 2: err(path, "opening needs at least 2 gap lines")
        for d in f.select("details.gv-gap"):
            sm = d.find("summary")
            if not sm or not sm.select_one(".gv-sr") or not sm.select_one(".gv-sr").get_text(strip=True): err(path, "gap <summary> needs a .gv-sr label")
            if len(d.find_all(True, recursive=False)) != 2: err(path, "gap <details> must hold one <summary> and one answer element")
        if not f.select_one(".gv-formula"): err(path, "opening should end with the formula that reveals the pattern")
    for f in soup.select(".gv-qr"):
        sv = f.find("svg")
        if not sv or sv.get("role") != "img" or not sv.get("aria-label"): err(path, "QR needs an <svg role=\"img\" aria-label>")
        u = f.select_one(".gv-url")
        if not u or not u.get_text(strip=True): err(path, "QR needs a visible .gv-url (printed address)")
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
