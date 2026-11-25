#!/usr/bin/env python3
"""Put data-level="A1".."C2" on the <main> of every manual topic page, from its folder
(manuals/<lang>/<kind>/<level>/...). manual-look.css reads it for the CEFR stamp and the level's accent colour.

Only pages with a .page-head get it (topic pages), not hubs or indexes. Idempotent; everything else stays byte-identical.

  python3 scripts/add_level_stamp.py [--check] [root ...]     (default root: manuals)
"""
import argparse, re, sys
from pathlib import Path

MAIN = re.compile(r"<main\b(?![^>]*\bdata-level=)", re.I)
LEVEL = re.compile(r"^manuals/[^/]+/(?:grammar|vocabulary|communication|general)/(a1|a2|b1|b2|c1|c2)/")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("roots", nargs="*", default=["manuals"]); ap.add_argument("--check", action="store_true")
    a = ap.parse_args(); pages = changed = 0
    for root in a.roots:
        for f in sorted(Path(root).rglob("*.html")):
            rel = str(f).replace("\\", "/")
            m = LEVEL.match(rel)
            if not m or "/print/" in rel:
                continue
            t = f.read_text(encoding="utf-8")
            if 'class="page-head"' not in t or "<main" not in t:
                continue
            pages += 1
            new, n = MAIN.subn('<main data-level="%s"' % m.group(1).upper(), t, count=1)
            if n:
                changed += 1
                if a.check: print("missing data-level:", f)
                else: f.write_text(new, encoding="utf-8")
    print("%s: %d topic pages, %d %s" % ("check" if a.check else "done", pages, changed, "lacking data-level" if a.check else "updated"))
    return 1 if (a.check and changed) else 0

if __name__ == "__main__":
    sys.exit(main())
