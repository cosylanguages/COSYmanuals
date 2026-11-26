#!/usr/bin/env python3
"""Add a print-only QR (.gv-qr) after the practice banner of English grammar pages, pointing to the
same COSYpractice link as the banner. Idempotent. English only: the QR caption is page-language text.
   python3 scripts/add_page_qr.py manuals/en/grammar   |   --check"""
import re, sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).parent))

BASE = "https://cosylanguages.github.io/COSYpractice/"
BANNER = re.compile(r'<div class="box practice-cta-banner".*?<a href="(\.\./\.\./\.\./\.\./\.\./practice/|https://cosylanguages\.github\.io/(?:COSYlanguages/practice|COSYpractice)/)([^"]+)"[^>]*>.*?</a>\s*</div>\n', re.S)

def process(p, check):
    s = p.read_text(encoding="utf8")
    if "practice-cta-banner" not in s: return None
    if 'class="gv-qr"' in s: return False
    m = BANNER.search(s)
    if not m: return None
    if check: return True
    pre = m.group(1)
    from make_qr_block import qr_block  # needs segno; only when writing
    url = (BASE if pre.startswith("..") else pre) + html.unescape(m.group(2))
    title = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    name = html.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else "this topic"
    blk = qr_block(url, "Practice this topic", "QR code: practice " + name) + "\n"
    p.write_text(s[:m.end()] + blk + s[m.end():], encoding="utf8")
    return True

if __name__ == "__main__":
    check = "--check" in sys.argv
    root = pathlib.Path([a for a in sys.argv[1:] if not a.startswith("--")][0])
    need = done = 0
    for p in sorted(root.rglob("topics/*.html")):
        r = process(p, check)
        if r is True: need += 1
        elif r is False: done += 1
    print(("check: %d lacking a QR, %d have one" if check else "added %d, %d already had one") % (need, done))
    sys.exit(1 if check and need else 0)
