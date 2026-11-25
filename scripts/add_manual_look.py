#!/usr/bin/env python3
"""Link shared/styles/manual-look.css on every manual page, after the page's own stylesheet.

The look is one shared file (paper, Fraunces headlines, masthead, callouts, formula tiles, tap-to-flip
mistakes). It must load LAST, so the link goes after the last <link rel="stylesheet"> that is local
(not the ecosystem-strip stylesheet on another host). The relative path is computed from the page's depth.
Idempotent. Everything else in a file stays byte-identical.

  python3 scripts/add_manual_look.py [--check] [root ...]     (default root: manuals)
"""
import argparse, os, re, sys
from pathlib import Path

LINK = re.compile(r'<link\b[^>]*\brel="stylesheet"[^>]*>', re.I)

def process(path: Path, text: str):
    if "manual-look.css" in text:
        return text, False
    links = [m for m in LINK.finditer(text) if 'href="http' not in m.group(0)]
    if not links:
        return text, False
    rel = os.path.relpath("shared/styles/manual-look.css", path.parent).replace(os.sep, "/")
    m = links[-1]
    return text[:m.end()] + '\n<link rel="stylesheet" href="%s">' % rel + text[m.end():], True

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("roots", nargs="*", default=["manuals"]); ap.add_argument("--check", action="store_true")
    a = ap.parse_args(); n = total = nolink = 0
    for root in a.roots:
        for f in sorted(Path(root).rglob("*.html")):
            t = f.read_text(encoding="utf-8")
            if "/print/" in str(f).replace(os.sep, "/"):   # booklets are built from the pages
                continue
            if "<main" not in t:           # booklets and fragments without a page shell are skipped
                continue
            total += 1
            new, ch = process(f, t)
            if ch:
                n += 1
                if a.check: print("missing manual-look link:", f)
                else: f.write_text(new, encoding="utf-8")
            elif "manual-look.css" not in t:
                nolink += 1
    print("%s: %d pages, %d %s, %d without any local stylesheet" % ("check" if a.check else "done", total, n, "lacking the link" if a.check else "updated", nolink))
    return 1 if (a.check and n) else 0

if __name__ == "__main__":
    sys.exit(main())
