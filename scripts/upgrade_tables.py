#!/usr/bin/env python3
"""Upgrade grammar tables.
 Tier 1 (every table): <th scope>, and every .table-wrap becomes a focusable, named scroll region
        (aria-label = nearest heading above, else the column headers; marked data-gv-autolabel).
 Tier 2 (only clear regular verb paradigms): gv-paradigm component with the stem and the ending of
        each form split (<span class="gv-stem">/<span class="gv-end">). A column is split only if ALL its
        forms are single plain words sharing a stem of >= 3 letters that is >= 55% of the shortest form.
        Irregular verbs (no shared stem) are NEVER marked automatically; they are listed for review.
Labels and words are copied verbatim, so every page stays in its own language.
  python3 scripts/upgrade_tables.py            # dry run + report
  python3 scripts/upgrade_tables.py --apply    # rewrite files
Idempotent."""
import html, os, re, sys, unicodedata

PAIR = re.compile(r'(?P<wrap><div class="table-wrap"(?P<wattr>[^>]*)>\s*)?(?P<table><table\b(?P<tattr>[^>]*)>(?P<body>.*?)</table>)(?P<wend>\s*</div>)?', re.S)
ROW = re.compile(r'<tr\b[^>]*>(.*?)</tr>', re.S)
CELL = re.compile(r'<(t[hd])\b([^>]*)>(.*?)</\1>', re.S)
HEAD = re.compile(r'<h[1-4]\b[^>]*>(.*?)</h[1-4]>', re.S)
PRON = re.compile(r"^(i|you|he|she|it|we|they|je|j[’']|tu|il|elle|on|nous|vous|ils|elles|я|ты|он|она|оно|мы|вы|они|ich|du|er|sie|es|wir|ihr|io|lui|lei|noi|voi|loro|yo|él|ella|ellos|nosotros|vosotros|eu|ele|ela|nós|vós|eles|elas|você|vocês)\b", re.I)

# Regular verb endings per language (no stress marks). A column is split ONLY if every ending is in this set,
# so irregular verbs, invariant participles and non-verbs (possessives, pronouns) are never touched.
ENDINGS = {
 "fr": "e es s t ons ez ent ais ait ions iez aient ai as a ont",
 "de": "e st t en n est et",
 "es": "o as a amos áis an es e emos éis en imos ís",
 "it": "o i a e iamo ate ete ite ano ono",
 "pt": "o as a amos am es e emos em imos ei aste ou aram i este eu eram iste iu iram",
 "ru": "у ю ешь ёшь ет ёт ем ём ете ёте ут ют ишь ит им ите ат ят",
}
def norm_end(e): return "".join(c for c in e.lower() if not unicodedata.combining(c)).replace("́", "")

def text(x): return html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
def attr(s): return html.escape(s, quote=True)
def graphemes(s):
    out = []
    for ch in s:
        if out and unicodedata.combining(ch): out[-1] += ch
        else: out.append(ch)
    return out

def scope_ths(body):
    rows = ROW.findall(body); first_is_header = bool(rows) and "<th" in rows[0] and "<td" not in rows[0]
    state = {"r": 0}
    def row_fix(m):
        r = state["r"]; state["r"] += 1; inner = m.group(1); idx = {"c": 0}
        def cell_fix(c):
            tag, a, content = c.groups(); i = idx["c"]; idx["c"] += 1
            if tag != "th" or "scope=" in a: return c.group(0)
            sc = "colgroup" if "colspan" in a else ("col" if (r == 0 and first_is_header) or i > 0 else "row")
            if r == 0 and first_is_header: sc = "colgroup" if "colspan" in a else "col"
            return f'<th{a} scope="{sc}">{content}</th>'
        return m.group(0).replace(inner, CELL.sub(cell_fix, inner), 1)
    return ROW.sub(row_fix, body)

def paradigm(body, report, where, lang):
    """Return new <table> inner HTML or None. Splits only clear regular paradigms."""
    rows = [[(t, a, c) for t, a, c in CELL.findall(r)] for r in ROW.findall(body)]
    if not rows: return None
    hdr = rows[0] if all(t == "th" for t, _, _ in rows[0]) else None
    data = rows[1:] if hdr else rows
    if len(data) < 4 or any(len(r) != len(data[0]) for r in data) or len(data[0]) < 2: return None
    if sum(1 for r in data if PRON.match(text(r[0][2]))) < len(data) * .8: return None
    splits = {}
    for j in range(1, len(data[0])):
        cells = [r[j][2] for r in data]
        if any("<" in c or "&" in c.replace("&#x27;", "") for c in cells): continue
        forms = [text(c) for c in cells]
        if any((" " in f) or (not f) or f.startswith("-") or len(f) > 16 for f in forms): continue
        g = [graphemes(f.lower()) for f in forms]; k = 0
        while all(len(x) > k for x in g) and len({x[k] for x in g}) == 1: k += 1
        short = min(len(x) for x in g)
        ends = {norm_end("".join(x[k:])) for x in g}
        ok_set = set(ENDINGS.get(lang, "").split()) | {""}
        if len({f.lower() for f in forms}) < 2: continue                       # invariant column: nothing to split
        if k >= 3 and k >= .55 * short and ends <= ok_set and ENDINGS.get(lang): splits[j] = k
        elif k >= 3 and ENDINGS.get(lang) and not ends <= ok_set:
            report.append(f"   review (stem found but endings not in the regular set {sorted(ends - ok_set)}): {where} col {j + 1}: {forms}")
        elif len({f.lower() for f in forms}) >= 4 and k < 3:
            report.append(f"   review (no shared stem, maybe irregular): {where} col {j + 1}: {forms}")
    if not splits: return None
    out = []
    if hdr: out.append("<thead><tr>" + "".join(f"<th{a}>{c}</th>" if "scope=" in a else f'<th{a} scope="col">{c}</th>' for t, a, c in hdr) + "</tr></thead>")
    out.append("<tbody>")
    for r in data:
        cells = []
        for j, (t, a, c) in enumerate(r):
            if j == 0: cells.append(f'<td{a} role="rowheader">{c}</td>')   # td keeps each folder\'s own cell styling
            elif j in splits:
                g = graphemes(text(c)); k = splits[j]
                cells.append(f'<td{a}><span class="gv-stem">{html.escape("".join(g[:k]), quote=False)}</span><span class="gv-end">{html.escape("".join(g[k:]), quote=False)}</span></td>')
            else: cells.append(f"<td{a}>{c}</td>")
        out.append("<tr>" + "".join(cells) + "</tr>")
    out.append("</tbody>")
    report.append(f"   split columns {sorted(c + 1 for c in splits)}: {where}")
    return "".join(out)

def process(s, rep, lang):
    stats = {"tables": 0, "wrapped": 0, "paradigm": 0}
    def sub(m):
        stats["tables"] += 1
        wrap, wend, body, tattr = m.group("wrap"), m.group("wend"), m.group("body"), m.group("tattr")
        wattr = m.group("wattr") or ""
        if wrap and wend and ('role="region"' in wattr or "gv-paradigm" in wattr): return m.group(0)   # already done
        pos = m.start(); hs = HEAD.findall(s[:pos]); label = text(hs[-1]) if hs else ""
        rows = ROW.findall(body)
        if not label and rows: label = " / ".join(text(c) for _, _, c in CELL.findall(rows[0]))
        new_body = scope_ths(body)
        if wrap and wend:
            stats["wrapped"] += 1
            p = paradigm(new_body, rep, f"{label[:40]!r}", lang) if "--no-paradigm" not in sys.argv else None
            if p:
                stats["paradigm"] += 1
                return (f'<div class="table-wrap gv gv-paradigm" tabindex="0" role="region" aria-label="{attr(label)}" data-gv-autolabel>'
                        f'<table{tattr}><caption class="gv-sr">{html.escape(label, quote=False)}</caption>{p}</table></div>')
            return (f'<div class="table-wrap"{wattr} tabindex="0" role="region" aria-label="{attr(label)}" data-gv-autolabel>'
                    f'<table{tattr}>{new_body}</table></div>')
        return (wrap or "") + f"<table{tattr}>{new_body}</table>" + (wend or "")
    return PAIR.sub(sub, s), stats

def main():
    apply = "--apply" in sys.argv; tot = {"tables": 0, "wrapped": 0, "paradigm": 0}; pages = 0
    for d, _, fs in os.walk("manuals"):
        for f in sorted(fs):
            if not f.endswith(".html"): continue
            p = os.path.join(d, f); s = open(p, encoding="utf-8", errors="surrogateescape").read()
            if "<table" not in s: continue
            rep = []; new, st = process(s, rep, p.split(os.sep)[1])
            if new != s:
                pages += 1
                for k in tot: tot[k] += st[k]
                if rep: print(p); [print(x) for x in rep]
                if apply: open(p, "w", encoding="utf-8", errors="surrogateescape").write(new)
    print(f"\n{pages} page(s) {'updated' if apply else 'would change'}: {tot['wrapped']} scroll regions named, {tot['paradigm']} paradigm tables split")

if __name__ == "__main__": main()
