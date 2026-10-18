#!/usr/bin/env python3
"""Turn raw serialized teacher/lesson notes ('task: "..." speaking_focus: "..."') printed inside
<div class="lesson-notes-extra"> into a labelled list (<dl class="gv-notes">), with labels in the page's language.
Blocks that are only internal metadata (lessons_count) are removed. Blocks that are NOT a clean key/value dump
(e.g. normal sentences) are never touched. Values are copied verbatim.
Languages without translated labels (ba br cv hy ka tt) get English labels marked lang="en" (honest, readable,
and flagged in docs/UI_STRINGS.md). Idempotent.
  python3 scripts/format_notes.py            # dry run
  python3 scripts/format_notes.py --apply"""
import collections, html, json, os, re, sys

DATA = json.load(open("shared/i18n/ui-strings.json", encoding="utf-8"))
LABELS = DATA["notes_labels"]; DROP = set(DATA["notes_drop_if_only"]); APPLY = set(DATA["apply"])
BLK = re.compile(r'<div class="lesson-notes-extra">(.*?)</div>', re.S)
PAIR = re.compile(r'\s*([a-z_]+):\s*("(?:[^"\\]|\\.)*"|-?\d+(?:\.\d+)?)\s*')

def parse(t):
    out, pos = [], 0
    while pos < len(t):
        m = PAIR.match(t, pos)
        if not m: return None
        out.append((m.group(1), m.group(2))); pos = m.end()
    return out or None

def value(v):
    if v.startswith('"'): return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return v

def render(pairs, lang):
    rows = []
    for k, v in pairs:
        lab = LABELS.get(k)
        if lab is None: return None                               # unknown key: leave the block alone
        txt = lab.get(lang) if lang in APPLY else None
        dt = f"<dt>{html.escape(txt, quote=False)}</dt>" if txt else f'<dt lang="en">{html.escape(lab["en"], quote=False)}</dt>'
        rows.append(f"<div>{dt}<dd>{html.escape(value(v), quote=False)}</dd></div>")
    return '<div class="lesson-notes-extra"><dl class="gv-notes">' + "".join(rows) + "</dl></div>"

def main():
    apply = "--apply" in sys.argv; pages = blocks = dropped = skipped = 0; per = collections.Counter()
    for d, _, fs in os.walk("manuals"):
        for f in sorted(fs):
            if not f.endswith(".html"): continue
            p = os.path.join(d, f); lang = p.split(os.sep)[1]
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            if 'class="lesson-notes-extra"' not in s: continue
            n = [0, 0, 0]
            def sub(m):
                pairs = parse(html.unescape(re.sub(r"\s+", " ", m.group(1))).strip())
                if not pairs: n[2] += 1; return m.group(0)
                if all(k in DROP for k, _ in pairs): n[1] += 1; return ""
                r = render(pairs, lang)
                if r is None: n[2] += 1; return m.group(0)
                n[0] += 1; return r
            new = BLK.sub(sub, s)
            if new != s:
                pages += 1; blocks += n[0]; dropped += n[1]; per[lang] += 1
                if apply: open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
            skipped += n[2]
    print(f"{pages} page(s) {'updated' if apply else 'would change'}: {blocks} notes blocks formatted, {dropped} metadata-only blocks removed, {skipped} non-dump blocks left alone")
    print("  per language:", dict(per.most_common()))

if __name__ == "__main__": main()
