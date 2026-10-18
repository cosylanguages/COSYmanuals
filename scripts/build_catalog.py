#!/usr/bin/env python3
"""Build the page catalog: one row per HTML page under manuals/.
  python3 scripts/build_catalog.py           # (re)write catalog/pages.json, summary.json, COVERAGE.md
  python3 scripts/build_catalog.py --check   # exit 1 if the committed catalog is out of date (for CI)

Columns (catalog/pages.json): path lang track module level kind status title bytes visuals tables quiz
lang_ok leaks access
  kind    topic | unit | track-manual | hub | print | teacher-access
  status  real | locked-stub | redirect
          locked-stub = body is the 'Protected Ecosystem Content' placeholder (the lesson text is stored outside git)
          redirect    = tiny page that only forwards to another page
  lang_ok  <html lang> equals the language folder        leaks  known English template strings still on the page
  access   classification from MANUALS_ACCESS_MANIFEST.json (null when the page is not listed there)
Deterministic output (sorted), so diffs show real changes only."""
import collections, html, importlib.util, json, os, re, sys

LEVELS = ["a0", "a1", "a2", "b1", "b2", "c1", "c2"]; MODS = ["grammar", "vocabulary", "communication"]
TRACKS = ["general", "spoken", "professional", "travelling", "exam", "relocation"]
COLS = ["path", "lang", "track", "module", "level", "kind", "status", "title", "bytes", "visuals", "tables", "quiz", "lang_ok", "leaks", "access"]
OUT = "catalog"

spec = importlib.util.spec_from_file_location("localize_ui", os.path.join(os.path.dirname(os.path.abspath(__file__)), "localize_ui.py"))
lu = importlib.util.module_from_spec(spec); spec.loader.exec_module(lu)

def classify(parts):
    """parts = path segments after manuals/<lang>/ -> (track, module, level, kind)"""
    name = parts[-1]; dirs = parts[:-1]; track = module = level = None
    for x in dirs:
        if x in TRACKS: track = x
        elif x in MODS: module = x
        elif x in LEVELS: level = x
    if dirs and dirs[0] == "print": return None, None, None, "print"
    if name == "teacher-access.html": return None, None, None, "teacher-access"
    if name == "index.html" or name.startswith("index-"): return track, module, level, "hub"
    if track and level: return track, name[:-5] if name[:-5] in MODS else None, level, "track-manual"
    if module and level and "topics" in dirs: return None, module, level, "topic"
    if module and level: return None, module, level, "unit"
    return track, module, level, "hub"

def main():
    access = {}
    if os.path.exists("MANUALS_ACCESS_MANIFEST.json"):
        for e in json.load(open("MANUALS_ACCESS_MANIFEST.json", encoding="utf-8"))["entries"]: access[e["path"]] = e.get("classification")
    rows = []
    for d, _, fs in os.walk("manuals"):
        for f in fs:
            if not f.endswith(".html"): continue
            p = os.path.join(d, f).replace(os.sep, "/"); segs = p.split("/")[1:]
            lang = segs[0] if len(segs[0]) == 2 and segs[0].isalpha() and len(segs) > 1 else None
            parts = segs[1:] if lang else segs
            track, module, level, kind = classify(parts)
            s = open(p, encoding="utf-8", errors="replace").read()
            stub = "Protected Ecosystem Content" in s
            t = re.search(r"<title>(.*?)</title>", s, re.S); title = re.sub(r"\s+", " ", html.unescape(t.group(1))).strip() if t else ""
            hl = re.search(r'<html[^>]*\blang="([^"]*)"', s[:4000])
            redirect = bool(re.search(r'<meta[^>]+http-equiv=["\']refresh', s, re.I))
            rows.append([p, lang, track, module, level, kind, "locked-stub" if stub else "redirect" if redirect else "real", title, len(s.encode("utf-8", "replace")),
                         len(re.findall(r'class="[^"]*\bgv-(?:timeline|paradigm|tree|contrast|formula)\b', s)),
                         s.count("<table"), int("quiz" in s.lower()),
                         int(bool(lang) and bool(hl) and hl.group(1) == lang),
                         len(lu.remaining_english(s, lang)) if lang and lang != "en" else 0,
                         access.get(p)])
    rows.sort(key=lambda r: r[0])
    pages = json.dumps({"columns": COLS, "rows": rows}, ensure_ascii=False, separators=(",", ":")) + "\n"

    # ---- summary
    langs = sorted({r[1] for r in rows if r[1]}); C = lambda *a: collections.Counter(a)
    per = {}
    for l in langs:
        rs = [r for r in rows if r[1] == l]
        per[l] = {"pages": len(rs),
                  "topic_real": sum(1 for r in rs if r[5] == "topic" and r[6] == "real"), "topic_stub": sum(1 for r in rs if r[5] == "topic" and r[6] == "locked-stub"),
                  "unit": sum(1 for r in rs if r[5] == "unit"), "track_manual": sum(1 for r in rs if r[5] == "track-manual"),
                  "hub": sum(1 for r in rs if r[5] == "hub"), "other_stub": sum(1 for r in rs if r[5] != "topic" and r[6] == "locked-stub"),
                  "visual_pages": sum(1 for r in rs if r[9] > 0), "lang_wrong": sum(1 for r in rs if not r[12]), "english_leak_pages": sum(1 for r in rs if r[13] > 0)}
    cell = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r[5] == "topic": cell[(r[1], r[3], r[4])][0 if r[6] == "real" else 1] += 1
    summary = {"total_pages": len(rows), "by_language": per,
               "topics_by_language_module_level": {f"{l}/{m}/{v}": cell[(l, m, v)] for (l, m, v) in sorted(cell, key=lambda k: tuple(str(x) for x in k))}}
    sj = json.dumps(summary, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

    # ---- human-readable coverage
    md = ["# Content coverage (generated by scripts/build_catalog.py, do not edit)\n",
          f"{len(rows)} HTML pages under `manuals/`: {sum(1 for r in rows if r[6] == 'real')} real (text is in git), {sum(1 for r in rows if r[6] == 'locked-stub')} locked stubs (placeholder page, the text is stored outside git), {sum(1 for r in rows if r[6] == 'redirect')} redirect pages.\n",
          "## By language\n", "| lang | pages | topic pages real | topic pages locked | % locked | unit pages | track manuals | pages with visuals | wrong `lang` | English-template leaks |", "|---|---|---|---|---|---|---|---|---|---|"]
    for l in langs:
        v = per[l]; tp = v["topic_real"] + v["topic_stub"]
        md.append(f"| {l} | {v['pages']} | {v['topic_real']} | {v['topic_stub']} | {100 * v['topic_stub'] // tp if tp else 0}% | {v['unit']} | {v['track_manual']} | {v['visual_pages']} | {v['lang_wrong']} | {v['english_leak_pages']} |")
    for m in MODS:
        md += [f"\n## Topic pages by language and level: {m} (real / locked)\n", "| lang | " + " | ".join(LEVELS) + " |", "|---|" + "---|" * len(LEVELS)]
        for l in langs:
            cs = [cell.get((l, m, v), [0, 0]) for v in LEVELS]
            if any(a or b for a, b in cs): md.append(f"| {l} | " + " | ".join(f"{a} / {b}" if a or b else "·" for a, b in cs) + " |")
    md += ["\n## Track manuals present (language x track: levels)\n", "| lang | " + " | ".join(TRACKS) + " |", "|---|" + "---|" * len(TRACKS)]
    for l in langs:
        cs = []
        for t in TRACKS:
            lv = sorted({r[4] for r in rows if r[1] == l and r[5] == "track-manual" and r[2] == t}, key=LEVELS.index)
            cs.append(", ".join(x.upper() for x in lv) or "·")
        md.append(f"| {l} | " + " | ".join(cs) + " |")
    md.append("")
    coverage = "\n".join(md)

    files = {"pages.json": pages, "summary.json": sj, "COVERAGE.md": coverage}
    if "--check" in sys.argv:
        stale = [n for n, c in files.items() if not os.path.exists(f"{OUT}/{n}") or open(f"{OUT}/{n}", encoding="utf-8").read() != c]
        if stale: print("catalog out of date:", ", ".join(stale), "-> run python3 scripts/build_catalog.py"); sys.exit(1)
        print(f"catalog up to date ({len(rows)} pages)"); return
    os.makedirs(OUT, exist_ok=True)
    for n, c in files.items(): open(f"{OUT}/{n}", "w", encoding="utf-8").write(c)
    unk = [r[0] for r in rows if r[1] is None and r[5] not in ("hub", "teacher-access", "print")]
    print(f"{len(rows)} pages -> {OUT}/pages.json ({len(pages) // 1024} KB), summary.json, COVERAGE.md")
    print("kinds:", dict(collections.Counter(r[5] for r in rows).most_common()), "| status:", dict(collections.Counter(r[6] for r in rows)))
    if unk: print("unclassified without language:", unk[:5])

if __name__ == "__main__": main()
