#!/usr/bin/env python3
"""Replace English UI template strings on non-English pages with the translations in
shared/i18n/ui-strings.json, and correct <html lang> on pages that end up fully localized.

Safe by design:
  * only whole text nodes that EXACTLY match a known English template string are replaced
    (lesson content is never touched); <script>/<style> blocks are skipped;
  * only languages listed in "apply" are touched; languages without translations keep their English
    (listed by --audit) instead of receiving a guess;
  * idempotent.
  python3 scripts/localize_ui.py             # dry run + report
  python3 scripts/localize_ui.py --apply     # rewrite files
  python3 scripts/localize_ui.py --audit     # remaining English template strings, per language"""
import collections, html, json, os, re, sys

DATA = json.load(open("shared/i18n/ui-strings.json", encoding="utf-8"))
APPLY = set(DATA["apply"]); ROWS = DATA["strings"]; PATS = [(re.compile(p["regex"]), p) for p in DATA["patterns"]]
EN = {re.sub(r"\s+", " ", r["en"]).strip(): r for r in ROWS}
TOKEN = re.compile(r"<(script|style)\b.*?</\1>|(>)([^<>]+)(?=<)", re.S | re.I)
HTML_TAG = re.compile(r"<html\b[^>]*>", re.I)
# "Unidad 0: Unidad 0: Primeros Pasos": the source repeated the heading prefix; keep it once
DUP = re.compile(r"^(?P<w>[^\W\d_]+ \d+[\s\u00a0]*:)\s*(?P=w)\s*")

def norm(t): return re.sub(r"\s+", " ", html.unescape(t)).strip()

def lookup(text, lang):
    """-> (key, translation or None) if text is a known English template string."""
    n = norm(text)
    if n in EN: return EN[n]["id"], EN[n].get(lang)
    for rx, p in PATS:
        m = rx.match(n)
        if not m: continue
        tpl = p["tpl"].get(lang)
        if not tpl: return p["id"], None
        g = m.groupdict()
        for name, table in p.get("maps", {}).items():            # localized words (module, track, ...)
            g[name] = table.get(g[name], {}).get(lang)
            if g[name] is None: return p["id"], None
        if lang == "fr" and g.get("rest", "").startswith(":"): g["rest"] = "\u00a0" + g["rest"]   # French spacing before ':'
        return p["id"], tpl.format(**g)
    return None, None

def process(s, lang, stats, dedupe_only=False):
    def sub(m):
        if m.group(1): return m.group(0)
        raw = m.group(3); n = norm(raw)
        key, tr = (None, None) if dedupe_only else lookup(raw, lang)
        if key and not tr: stats["missing"][key] += 1
        out = tr if (key and tr) else n
        dd = DUP.sub(lambda x: x.group("w") + " ", out, count=1)
        if dd != out: stats["deduped"] += 1
        if dd == n and not (key and tr): return m.group(0)         # nothing to do
        if dd == n: return m.group(0)
        lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
        if key and tr: stats["replaced"][key] += 1
        return ">" + lead + html.escape(dd, quote=False) + trail
    return TOKEN.sub(sub, s)

def remaining_english(s, lang):
    """Known English template strings still on the page (cognates, where the translation equals the English, are fine)."""
    out = []
    for m in TOKEN.finditer(s):
        if not m.group(2): continue
        key, tr = lookup(m.group(3), lang)
        if key and not (tr and norm(tr) == norm(m.group(3))): out.append(norm(m.group(3)))
    return out

def main():
    apply = "--apply" in sys.argv; audit = "--audit" in sys.argv
    changed = 0; langfix = 0; dedup = 0; rep = collections.Counter(); per_lang = collections.Counter()
    left = collections.defaultdict(collections.Counter); pages_left = collections.Counter()
    for d, _, fs in os.walk("manuals"):
        for f in fs:
            if not f.endswith(".html"): continue
            p = os.path.join(d, f); lang = p.split(os.sep)[1]
            if not re.fullmatch(r"[a-z]{2}", lang): continue
            s = open(p, encoding="utf-8", errors="surrogateescape").read()
            stats = {"replaced": collections.Counter(), "missing": collections.Counter(), "deduped": 0}
            if lang == "en":                                       # English: only collapse duplicated heading prefixes
                new = process(s, lang, stats, dedupe_only=True)
                if new != s:
                    changed += 1; per_lang[lang] += 1; dedup += stats["deduped"]
                    if apply: open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
                continue
            new = process(s, lang, stats) if lang in APPLY else s
            rem = remaining_english(new, lang)
            for r in rem: left[lang][r] += 1
            if rem: pages_left[lang] += 1
            else:                                                  # no known English left: declare the right language
                hm = HTML_TAG.search(new)
                if hm and re.search(r'\blang="(?!%s")[^"]*"' % lang, hm.group(0)):
                    new = new.replace(hm.group(0), re.sub(r'\blang="[^"]*"', f'lang="{lang}"', hm.group(0)), 1); langfix += 1
            if new != s:
                changed += 1; per_lang[lang] += 1; rep.update(stats["replaced"]); dedup += stats["deduped"]
                if apply: open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
    if audit:
        print("Remaining English template strings (pages affected / distinct strings):")
        for l in sorted(pages_left, key=lambda x: -pages_left[x]):
            tag = "" if l in APPLY else "  <- no translations yet (needs a native speaker)"
            print(f"  {l}: {pages_left[l]} pages, {len(left[l])} strings{tag}")
        return
    print(f"{changed} page(s) {'updated' if apply else 'would change'}; {sum(rep.values())} strings replaced; {dedup} duplicated heading prefixes collapsed; <html lang> fixed on {langfix} page(s)")
    print("  per language:", dict(per_lang.most_common()))
    still = {l: pages_left[l] for l in pages_left}
    print("  pages still containing known English template strings:", still)

if __name__ == "__main__":
    main()
