#!/usr/bin/env python3
"""Link the two tiers of the Russian A1 grammar: each short overview page gets a 'Подробнее' box pointing to
its detail pages, and each detail page gets a 'Краткий обзор' box pointing back to its overview.
Mapping: detail slug starts with '<overview>-' (strict), plus the reviewed EXTRA pairs below.
Pairs that are not obvious are NOT linked (listed by --report). Idempotent (data-tier marker).
  python3 scripts/link_ru_tiers.py            # dry run + report
  python3 scripts/link_ru_tiers.py --apply"""
import collections, html, os, re, sys

B = "manuals/ru/grammar/a1/topics/"
EXTRA = {  # overview -> [detail slugs]   (reviewed by name, see docs/DUPLICATE_REVIEW_A1.md)
    "osobyy-glagol-khotet": ["glagol-khotet", "glagoly-moch-i-umet"],
    "lyubit-nravitsya": ["konstruktsiya-nravitsya-lyubit"],
    "mozhno-nelzya-nuzhno": ["konstruktsii-mozhno-nelzya-nuzhno"],
    "prilagatelnye": ["soglasovanie-prilagatelnykh"],
    "lichnye-mestoimeniya-padezhi": ["lichnye-mestoimeniya-i-nulevaya-svyazka"],
    "udarenie-i-reduktsiya-glasnykh": ["reduktsiya-glasnykh"],
    "predlogi-mesta": ["narechiya-mesta-i-napravleniya"],
}
OV_KEY, DET_KEY = "Обрати внимание", "Связь с другими темами"
OV_LABEL, DET_LABEL = "📚 Подробнее", "📚 Краткий обзор"

def read(slug): return open(B + slug + ".html", encoding="utf-8").read()
def title(slug):
    t = re.search(r"<h1[^>]*>(.*?)</h1>", read(slug), re.S).group(1)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()

def insert_after_box(path, key, box):
    s = open(path, encoding="utf-8").read()
    if "data-tier=" in s: return False
    if s.count(key) < 1: return None
    i = s.index(key); e = s.index("</div>", i) + 6
    open(path, "w", encoding="utf-8").write(s[:e] + "\n" + box + s[e:]); return True

def main():
    apply = "--apply" in sys.argv
    slugs = sorted(f[:-5] for f in os.listdir(B) if f.endswith(".html"))
    real = {s: os.path.getsize(B + s + ".html") for s in slugs if "http-equiv=\"refresh\"" not in read(s) and not s.startswith(("ru-", "ru."))}
    short = {s for s, n in real.items() if n < 8000}; long_ = {s for s, n in real.items() if n >= 8000}
    pairs = collections.defaultdict(list)
    for o in sorted(short):
        for d in sorted(long_):
            if d.startswith(o + "-"): pairs[o].append(d)
    for o, ds in EXTRA.items():
        for d in ds:
            if o in real and d in real and d not in pairs[o]: pairs[o].append(d)
    back = {d: o for o, ds in pairs.items() for d in ds}
    done_o = done_d = 0; skipped = []
    for o, ds in sorted(pairs.items()):
        links = " · ".join(f'<a href="{d}.html">{html.escape(title(d), quote=False)}</a>' for d in ds)
        box = f'<div class="box connect" data-tier="overview"><h3>{OV_LABEL}</h3><p>{links}</p></div>'
        if apply:
            r = insert_after_box(B + o + ".html", OV_KEY, box)
            if r is None: skipped.append(o)
            done_o += bool(r)
        else: done_o += 1
    for d, o in sorted(back.items()):
        box = f'<div class="box connect" data-tier="detail"><h3>{DET_LABEL}</h3><p><a href="{o}.html">{html.escape(title(o), quote=False)}</a></p></div>'
        if apply:
            r = insert_after_box(B + d + ".html", DET_KEY, box)
            if r is None: skipped.append(d)
            done_d += bool(r)
        else: done_d += 1
    unlinked = sorted(long_ - set(back))
    print(f"overview pages {'linked' if apply else 'to link'}: {done_o} | detail pages {'linked' if apply else 'to link'}: {done_d} of {len(long_)}")
    print("detail pages with no confident overview (left unlinked):", unlinked)
    if skipped: print("skipped (anchor text not found):", skipped)

if __name__ == "__main__": main()
