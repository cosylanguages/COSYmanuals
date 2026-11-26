#!/usr/bin/env python3
"""Build the print-only QR block (.gv-qr) for a practice link. Inline SVG, no network, no JS.
   python3 scripts/make_qr_block.py --url URL --text "Practice this topic" --alt "QR code: practice this topic"
Needs: pip install segno. Words (text, alt) must be in the page's own language."""
import argparse, html, re, segno

def qr_block(url, text, alt):
    svg = segno.make(url, error="m", micro=False).svg_inline(scale=4, border=1, dark="#000", light="#fff", omitsize=True)
    svg = re.sub(r"^<svg ", '<svg role="img" aria-label="%s" ' % html.escape(alt, quote=True), svg, count=1)
    short = re.sub(r"^https?://", "", url)
    return ('<aside class="gv-qr" aria-label="%s">%s<p>%s<span class="gv-url">%s</span></p></aside>'
            % (html.escape(text, quote=True), svg, html.escape(text), html.escape(short)))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True); ap.add_argument("--text", required=True); ap.add_argument("--alt", required=True)
    a = ap.parse_args(); print(qr_block(a.url, a.text, a.alt))
