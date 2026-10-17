#!/usr/bin/env python3
"""Convert legacy hand-made timelines (div.timeline-wrap > div.timeline > .pt/.pt-label/...)
to the shared gv-timeline component. Only the timeline blocks are rewritten; every other byte
of a page is left alone. Labels are copied verbatim (so each page stays in its own language).

  python3 scripts/convert_timelines.py            # dry run, prints a report
  python3 scripts/convert_timelines.py --apply    # rewrite files in place
Idempotent: converted pages no longer match. Review the diff, then run check_visuals.py."""
import colorsys, html, os, re, sys

BLOCK = re.compile(r'<div class="timeline-wrap"(?:\s+style="[^"]*")?>\s*<div class="timeline">(.*?)</div></div>', re.S)
ITEM = re.compile(r'<div class="([^"]+)"(?:\s+style="([^"]*)")?>(.*?)</div>', re.S)
CAP = re.compile(r'<span class="endcap (left|right)">(.*?)</span>', re.S)
# tone reference hues (degrees): a blue, b pink/red, c green/teal, d amber, e purple
TONES = {"a": 226, "b": 330, "c": 172, "d": 33, "e": 260}
FIX_ENT = re.compile(r"&amp;(rarr|larr|harr|mdash|ndash|hellip|nbsp|#\d+|#x[0-9a-fA-F]+);")

def num(style, prop):
    m = re.search(rf"(?:^|[;\s]){prop}\s*:\s*([\d.]+)%", style or ""); return float(m.group(1)) if m else None
def color(style, prop):
    m = re.search(rf"{prop}\s*:\s*#([0-9a-fA-F]{{6}}|[0-9a-fA-F]{{3}})", style or "")
    if not m: return None
    h = m.group(1); h = "".join(c * 2 for c in h) if len(h) == 3 else h
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
def tone(rgb, fill=False):
    if rgb is None: return None
    h, s, v = colorsys.rgb_to_hsv(*rgb)
    if s < (.05 if fill else .15) or v < .25: return None   # near-black / grey: default ink (fills are pale, so lower cut-off)
    hue = h * 360
    return min(TONES, key=lambda t: min(abs(hue - TONES[t]), 360 - abs(hue - TONES[t])))
def fmt(x): return f"{x:g}%"

Y0 = {"point": 1.3, "span": 1.6, "now": 2.8}
def box(r):
    t = html.unescape(re.sub("<[^>]+>", "", r["text"]))
    return min(9.0, .5 * len(t)), Y0[r["kind"]], Y0[r["kind"]] + 1.15 * max(1, -(-int(.5 * len(t) * 100) // 900))
def clash(p, q):
    (w1, a1, b1), (w2, a2, b2) = box(p), box(q)
    return abs(p["pos"] - q["pos"]) * .30 < (w1 + w2) / 2 and a1 < b2 and a2 < b1
def place(rows, warns):
    """Choose above/below per label so labels do not overlap (same model as check_visuals.py)."""
    placed = []
    for kind in ("now", "point", "span"):
        for r in [x for x in rows if x["kind"] == kind and x["text"]]:
            order = [r["below"], not r["below"]] if kind != "now" else [False]
            for side in order:
                r["below"] = side
                if not any(q["below"] == side and clash(r, q) for q in placed): break
            else:
                r["below"] = order[0]
                warns.append(f"label '{html.unescape(re.sub('<[^>]+>', '', r['text']))}' may still overlap another label")
            placed.append(r)

def convert(inner, warns):
    pts, labels, spans, nows, caps = [], [], [], [], {}
    for cls, style, body in ITEM.findall(inner):
        c = cls.split()
        if "<div" in body: warns.append("nested div, skipped block"); return None
        if "pt" == c[0]: pts.append((num(style, "left"), tone(color(style, "background"))))
        elif "pt-label" == c[0]: labels.append((num(style, "left"), tone(color(style, "color")), "below" in c, body.strip()))
        elif "span" == c[0]:
            l, w = num(style, "left"), num(style, "width")
            spans.append([l, l + w, tone(color(style, "background"), fill=True), None, False])
        elif "now-tick" == c[0]: nows.append([num(style, "left"), None])
        elif "now-label" == c[0]:
            for n in nows:
                if n[0] == num(style, "left") and n[1] is None: n[1] = body.strip(); break
            else: nows.append([num(style, "left"), body.strip()])
    for side, text in CAP.findall(inner): caps[side] = text.strip()
    items = []  # (sort_pos, html, aria_text)
    used = set()
    for l, t, below, text in labels:
        ptmatch = next((p for p in pts if p[0] == l and id(p) not in used), None)
        if ptmatch: used.add(id(ptmatch)); items.append((l, "point", t or ptmatch[1], below, text, l)); continue
        sp = next((s for s in spans if s[0] <= (l or 0) <= s[1] and s[3] is None), None)
        if sp: sp[3], sp[4] = text, below; continue
        warns.append(f"label '{re.sub('<[^>]+>', '', text)}' had no dot; rendered as a point"); items.append((l, "point", t, below, text, l))
    for p in pts:
        if id(p) not in used: warns.append("dot without label"); items.append((p[0], "point", p[1], False, "", p[0]))
    rows = []
    for s_ in spans: rows.append(dict(kind="span", pos=(s_[0] + s_[1]) / 2, frm=s_[0], to=s_[1], tone=s_[2], text=s_[3], below=s_[4]))
    for n in nows: rows.append(dict(kind="now", pos=n[0], tone=None, text=n[1], below=False))
    for pos, _, t, below, text, l in items: rows.append(dict(kind="point", pos=pos, tone=t, text=text, below=True))  # legacy look: under the axis
    place(rows, warns)
    rows.sort(key=lambda r: r["pos"] if r["pos"] is not None else 0)
    out_rows = []
    for r in rows:
        lab = f'<span class="gv-label">{r["text"]}</span>' if r["text"] else ""
        tcl = f' gv-tone-{r["tone"]}' if r["tone"] else ""
        bcl = " gv-below" if r["below"] and r["text"] else ""
        if r["kind"] == "span":
            hid = "" if r["text"] else ' aria-hidden="true"'
            out_rows.append((r["pos"], f'<li class="gv-span{tcl}{bcl}" style="--from:{fmt(r["frm"])};--to:{fmt(r["to"])}"{hid}>{lab}</li>', r["text"]))
        elif r["kind"] == "now":
            out_rows.append((r["pos"], f'<li class="gv-now" style="--at:{fmt(r["pos"])}">{lab}</li>', r["text"]))
        else:
            out_rows.append((r["pos"], f'<li class="gv-point{tcl}{bcl}" style="--at:{fmt(r["pos"])}">{lab}</li>', r["text"]))
    rows = out_rows
    aria = " · ".join(html.unescape(re.sub("<[^>]+>", "", r[2])) for r in rows if r[2])
    aria = html.escape(aria, quote=True)
    cap = ""
    if caps: cap = f'<div class="gv-caps"><span>{caps.get("left", "")}</span><span>{caps.get("right", "")}</span></div>'
    return (f'<figure class="gv gv-timeline" tabindex="0" role="region" aria-label="{aria}" data-gv-autolabel>'
            f'<ol class="gv-axis">{"".join(r[1] for r in rows)}</ol>{cap}</figure>')

def main():
    apply = "--apply" in sys.argv
    total = changed = 0
    for d, _, fs in os.walk("manuals"):
        for f in sorted(fs):
            if not f.endswith(".html"): continue
            p = os.path.join(d, f); s = open(p, encoding="utf-8", errors="surrogateescape").read()
            if "timeline-wrap" not in s: continue
            warns = []; n = [0]
            def sub(m):
                r = convert(m.group(1), warns)
                if r is None: return m.group(0)
                n[0] += 1; return FIX_ENT.sub(r"&\1;", r)
            new = BLOCK.sub(sub, s)
            fixed = len(FIX_ENT.findall(s)) - len(FIX_ENT.findall(new))
            if n[0]:
                total += n[0]; changed += 1
                print(f"{p}: {n[0]} timeline(s)" + (f", fixed {fixed} double-encoded entit{'y' if fixed == 1 else 'ies'}" if fixed else ""))
                for w in warns: print("    WARN", w)
                if apply: open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
            left = new.count("timeline-wrap")
            if left: print(f"    NOTE {p}: {left} unconverted legacy block(s) remain")
    print(f"\n{total} timeline(s) on {changed} page(s) " + ("converted" if apply else "would be converted (dry run, use --apply)"))

if __name__ == "__main__":
    main()
