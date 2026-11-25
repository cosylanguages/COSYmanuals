#!/usr/bin/env python3
"""Stamp a print-only answer key and score line into every quiz / concept-check panel.

A printed page has nothing to tap. Each `.quiz-panel` / `.ccq-panel` carries its answers in
`data-quiz='[{"correct": 1}, ...]'`; this inserts, right after the panel's opening tag:

  <div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / 3</span><span class="pk-ans">&#10003; 1&middot;b 2&middot;c 3&middot;b</span></div>

Only letters, numbers and symbols, so it needs no translation in any language. Hidden on screen
(components.css); on paper it is the score line and the upside-down answer key.
Idempotent: panels that already have a key are skipped. Everything else in a file stays byte-identical.

  python3 scripts/add_print_key.py [--check] [root ...]     (default root: manuals)
  --check  change nothing; exit 1 if any panel lacks a key (used by tests/print-exercises.test.mjs)
"""
import argparse, json, re, sys
from pathlib import Path

TAG = re.compile(r"""<(?:div|section)\b(?:[^>"']|"[^"]*"|'[^']*')*>""")   # quote-aware: values may contain ">"
IS_PANEL = re.compile(r'\bclass="[^"]*\b(?:quiz-panel|ccq-panel)\b')
DATA = re.compile(r"""data-quiz=(?:'([^']*)'|"([^"]*)")""")
KEY = 'class="print-key"'

def key_html(items):
    letters = []
    for i, it in enumerate(items, 1):
        c = it.get("correct") if isinstance(it, dict) else None
        if not isinstance(c, int) or not 0 <= c < 26:
            return None
        letters.append("%d&middot;%s" % (i, chr(97 + c)))
    return ('<div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / %d</span>'
            '<span class="pk-ans">&#10003; %s</span></div>' % (len(items), " ".join(letters)))

def process(text):
    out, pos, n_new, n_missing = [], 0, 0, 0
    for m in TAG.finditer(text):
        tag = m.group(0)
        if not IS_PANEL.search(tag):
            continue
        d = DATA.search(tag)
        if not d:
            continue
        try:
            items = json.loads((d.group(1) or d.group(2)).replace("&quot;", '"'))
        except ValueError:
            continue
        after = text[m.end():m.end() + 80]
        if KEY in after:
            continue
        k = key_html(items)
        if k is None:
            continue
        n_missing += 1
        out.append(text[pos:m.end()]); out.append(k); pos = m.end(); n_new += 1
    out.append(text[pos:])
    return "".join(out), n_new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=["manuals"]); ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    files = changed = panels = 0
    for root in a.roots:
        for f in sorted(Path(root).rglob("*.html")):
            t = f.read_text(encoding="utf-8")
            if "data-quiz" not in t:
                continue
            files += 1
            new, n = process(t)
            if n:
                changed += 1; panels += n
                if a.check:
                    print("missing print key:", f)
                else:
                    f.write_text(new, encoding="utf-8")
    print("%s: %d files with quizzes, %d %s, %d panels" % ("check" if a.check else "done", files, changed,
          "lacking a key" if a.check else "updated", panels))
    return 1 if (a.check and changed) else 0

if __name__ == "__main__":
    sys.exit(main())
