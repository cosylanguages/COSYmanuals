#!/usr/bin/env python3
"""Add a timeline and a concept-check block to tense pages.

Every tense/aspect grammar page gets one `gv-timeline` figure placed immediately
before the page's concept-check block, so the CCQs sit directly below the timeline.
Labels come from the page's own language (the manuals are monolingual).

When a page has no concept-check block of its own, the first questions from that
page's existing practice quiz are reused as the concept check. That keeps the new
block in the page language without inventing translations.

  python3 scripts/add_tense_timelines.py --lang en          # dry run
  python3 scripts/add_tense_timelines.py --lang en --apply  # write files
"""
import argparse
import html
import json
import os
import re
import sys

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))

from tense_timelines_en import (
    CCQ as EN_CCQ,
    EN_SLUG_TO_PROFILE,
    PROFILES as EN_PROFILES,
)
from tense_timelines_fr_ru import (
    FR_PROFILES,
    FR_SLUG_TO_PROFILE,
    RU_PROFILES,
    RU_SLUG_TO_PROFILE,
)
from tense_timelines_minor import (
    BA_PROFILES, BA_SLUG_TO_PROFILE,
    BR_PROFILES, BR_SLUG_TO_PROFILE,
    CV_PROFILES, CV_SLUG_TO_PROFILE,
    HY_PROFILES, HY_SLUG_TO_PROFILE,
    KA_PROFILES, KA_SLUG_TO_PROFILE,
    TT_PROFILES, TT_SLUG_TO_PROFILE,
)
from tense_timelines_other import (
    DE_PROFILES, DE_SLUG_TO_PROFILE,
    EL_PROFILES, EL_SLUG_TO_PROFILE,
    ES_PROFILES, ES_SLUG_TO_PROFILE,
    IT_PROFILES, IT_SLUG_TO_PROFILE,
    PT_PROFILES, PT_SLUG_TO_PROFILE,
)

REGISTRY = "data/grammar-points.json"
LANG_CODE = "en"
CCQ_HEADING = {
    "en": "Concept check",
    "fr": "Vérification du concept",
    "ru": "Проверка понимания",
    "de": "Konzeptprüfung",
    "es": "Comprobación del concepto",
    "it": "Verifica del concetto",
    "pt": "Verificação do conceito",
    "el": "Έλεγχος κατανόησης",
    "tt": "Аңлауны тикшерү",
    "ba": "Аңлауҙы тикшереү",
    "cv": "Ăнланусене тĕрĕслени",
    "br": "Gwiriañ ar meizad",
    "hy": "Հասկացության ստուգում",
    "ka": "ცნების შემოწმება",
}
SCORE_LABEL = {
    "en": "Score", "fr": "Score", "ru": "Счёт", "de": "Punktzahl",
    "es": "Puntuación", "it": "Punteggio", "pt": "Pontuação", "el": "Σκορ",
    "tt": "Балл", "ba": "Балл", "cv": "Балл", "br": "Poentoù",
    "hy": "Միավոր", "ka": "ქულა",
}
RESET_TEXT = {
    "en": "Reset quiz", "fr": "Réinitialiser", "ru": "Сбросить",
    "de": "Zurücksetzen", "es": "Reiniciar", "it": "Ripristina",
    "pt": "Reiniciar", "el": "Επαναφορά",
    "tt": "Яңадан башлау", "ba": "Яңынан башлау", "cv": "Тепрен çĕнет",
    "br": "Adlakaat", "hy": "Վերսկսել", "ka": "განახლება",
}
DEFAULT_CAPS = {
    "en": ("past", "future"),
    "fr": ("passé", "futur"),
    "ru": ("прошлое", "будущее"),
    "de": ("Vergangenheit", "Zukunft"),
    "es": ("pasado", "futuro"),
    "it": ("passato", "futuro"),
    "pt": ("passado", "futuro"),
    "el": ("παρελθόν", "μέλλον"),
    "tt": ("үткән", "киләчәк"),
    "ba": ("үткән", "киләсәк"),
    "cv": ("иртнĕ", "пулаяс"),
    "br": ("tremenet", "dazont"),
    "hy": ("անցյալ", "ապառնի"),
    "ka": ("წარსული", "მომავალი"),
}

LANG = {
    "en": (EN_PROFILES, EN_SLUG_TO_PROFILE),
    "fr": (FR_PROFILES, FR_SLUG_TO_PROFILE),
    "ru": (RU_PROFILES, RU_SLUG_TO_PROFILE),
    "de": (DE_PROFILES, DE_SLUG_TO_PROFILE),
    "es": (ES_PROFILES, ES_SLUG_TO_PROFILE),
    "it": (IT_PROFILES, IT_SLUG_TO_PROFILE),
    "pt": (PT_PROFILES, PT_SLUG_TO_PROFILE),
    "el": (EL_PROFILES, EL_SLUG_TO_PROFILE),
    "tt": (TT_PROFILES, TT_SLUG_TO_PROFILE),
    "ba": (BA_PROFILES, BA_SLUG_TO_PROFILE),
    "cv": (CV_PROFILES, CV_SLUG_TO_PROFILE),
    "br": (BR_PROFILES, BR_SLUG_TO_PROFILE),
    "hy": (HY_PROFILES, HY_SLUG_TO_PROFILE),
    "ka": (KA_PROFILES, KA_SLUG_TO_PROFILE),
}

TIMELINE_RE = re.compile(r'\s*<figure class="gv gv-timeline"[\s\S]*?</figure>')
CCQ_RE = re.compile(r'<div class="ccq-panel"')
TABLE_RE = re.compile(r'<div class="table-wrap\b')
TABLE_ANY_RE = re.compile(r'<table\b')
RULE_RE = re.compile(r'<div class="box rule-box\b')
BOX_WHY_RE = re.compile(r'<div class="box why"')
PAGER_RE = re.compile(r'<div class="pager"')


def esc(value):
    return html.escape(str(value), quote=True)


def render_timeline(profile_id, profile, lang):
    rows = []
    for item in profile["items"]:
        if item["type"] == "span":
            classes = ["gv-span"]
            if item.get("tone"):
                classes.append("gv-tone-" + item["tone"])
            if item.get("below"):
                classes.append("gv-below")
            label = item.get("label") or ""
            label_html = f'<span class="gv-label">{esc(label)}</span>' if label else ""
            hidden = "" if label else ' aria-hidden="true"'
            rows.append(
                f'<li class="{" ".join(classes)}" style="--from:{item["frm"]:g}%;--to:{item["to"]:g}%"{hidden}>{label_html}</li>'
            )
        elif item["type"] == "now":
            label = item.get("label") or ""
            label_html = f'<span class="gv-label">{esc(label)}</span>' if label else ""
            rows.append(f'<li class="gv-now" style="--at:{item["at"]:g}%">{label_html}</li>')
        else:
            classes = ["gv-point"]
            if item.get("tone"):
                classes.append("gv-tone-" + item["tone"])
            if item.get("below"):
                classes.append("gv-below")
            label = item.get("label") or ""
            label_html = f'<span class="gv-label">{esc(label)}</span>' if label else ""
            rows.append(
                f'<li class="{" ".join(classes)}" style="--at:{item["at"]:g}%">{label_html}</li>'
            )
    caps = profile.get("caps", DEFAULT_CAPS.get(lang, ("past", "future")))
    return (
        f'<figure class="gv gv-timeline" tabindex="0" role="region" '
        f'aria-label="{esc(profile["aria"])}" data-gv-autolabel data-tense-timeline="{esc(profile_id)}">'
        f'<ol class="gv-axis">{"".join(rows)}</ol>'
        f'<div class="gv-caps"><span>{esc(caps[0])}</span><span>{esc(caps[1])}</span></div>'
        f"</figure>"
    )


def render_en_ccq(profile_id, ccq_key):
    questions = EN_CCQ[ccq_key]
    data = html.escape(json.dumps([{"correct": q["correct"]} for q in questions], ensure_ascii=False), quote=True)
    letters = "abcdefghij"
    answers = " ".join(f"{i + 1}·{letters[q['correct']]}" for i, q in enumerate(questions))
    items = []
    for i, q in enumerate(questions):
        opts = "".join(
            f'<button type="button" class="qopt">{esc(opt)}</button>' for opt in q["options"]
        )
        items.append(
            f'<div class="qitem"><div class="qtext">{i + 1}. {esc(q["q"])}</div>'
            f'<div class="qopts">{opts}</div>'
            f'<div class="qexplain">{esc(q["explain"])}</div></div>'
        )
    return (
        f'<div class="ccq-panel" data-quiz="{data}" data-tense-ccq="{esc(profile_id)}">'
        f'<div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(questions)}</span>'
        f'<span class="pk-ans">&#10003; {answers}</span></div>'
        f'<div class="quiz-head"><h3>🧠 Concept check</h3>'
        f'<span class="quiz-score">Score: 0 / {len(questions)}</span></div>'
        f'{"".join(items)}</div>'
    )


def render_profile_ccq(profile_id, questions, lang):
    data = html.escape(json.dumps([{"correct": q["correct"]} for q in questions], ensure_ascii=False), quote=True)
    letters = "abcdefghij"
    answers = " ".join(f"{i + 1}·{letters[q['correct']]}" for i, q in enumerate(questions))
    items = []
    for i, q in enumerate(questions):
        opts = "".join(
            f'<button type="button" class="qopt">{esc(opt)}</button>' for opt in q["options"]
        )
        items.append(
            f'<div class="qitem"><div class="qtext">{i + 1}. {esc(q["q"])}</div>'
            f'<div class="qopts">{opts}</div>'
            f'<div class="qexplain">{esc(q["explain"])}</div></div>'
        )
    panel_class = "ccq-panel" if lang == "en" else "quiz-panel"
    heading = CCQ_HEADING.get(lang, "Concept check")
    score_label = SCORE_LABEL.get(lang, "Score")
    reset = RESET_TEXT.get(lang, "Reset quiz")
    return (
        f'<div class="{panel_class}" data-quiz="{data}" data-tense-ccq="{esc(profile_id)}">'
        f'<div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(questions)}</span>'
        f'<span class="pk-ans">&#10003; {answers}</span></div>'
        f'<div class="quiz-head"><h2>{esc(heading)}</h2>'
        f'<span class="quiz-score">{esc(score_label)}: 0 / {len(questions)}</span></div>'
        f'{"".join(items)}'
        f'<button type="button" class="quiz-reset">{esc(reset)}</button></div>'
    )


def render_quiz_ccq(text, profile_id):
    """Reuse the first questions of the page's own practice quiz as a CCQ block."""
    soup = BeautifulSoup(text, "html.parser")
    panel = soup.select_one("div.quiz-panel[data-quiz]")
    if panel is None:
        return None
    try:
        data = json.loads(panel.get("data-quiz", "[]"))
    except (TypeError, ValueError):
        return None
    qitems = panel.select(".qitem")
    count = min(2, len(qitems), len(data))
    if count == 0:
        return None
    data = data[:count]
    heading = panel.select_one(".quiz-head h2, .quiz-head h3")
    heading_text = CCQ_HEADING.get(LANG_CODE, heading.get_text(strip=True) if heading else "CCQ")
    reset = panel.select_one(".quiz-reset")
    reset_text = reset.get_text(strip=True) if reset else "Reset"
    letters = "abcdefghij"
    answers = " ".join(
        f"{i + 1}·{letters[item.get('correct', 0)]}" for i, item in enumerate(data)
    )
    return (
        f'<div class="quiz-panel" data-quiz="{html.escape(json.dumps(data, ensure_ascii=False), quote=True)}" data-tense-ccq="{esc(profile_id)}">'
        f'<div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {count}</span>'
        f'<span class="pk-ans">&#10003; {answers}</span></div>'
        f'<div class="quiz-head"><h2>{esc(heading_text)}</h2>'
        f'<span class="quiz-score">{esc(SCORE_LABEL.get(LANG_CODE, "Score"))}: 0 / {count}</span></div>'
        f'{"".join(str(qitems[i]) for i in range(count))}'
        f'<button type="button" class="quiz-reset">{esc(reset_text)}</button></div>'
    )


def in_canonical_table(text, pos):
    """True when pos sits inside a canonical gv-paradigm wrapper."""
    start = text.rfind("<div", 0, pos)
    if start == -1:
        return False
    tag = text[start:text.find(">", start) + 1]
    return "data-table-id=" in tag or "gv-paradigm" in tag


def find_anchor(text):
    main = re.search(r'<main\b', text)
    main_start = main.start() if main else 0

    # Keep the timeline directly above the concept-check block when one exists.
    for pattern, kind in (
        (r'<section[^>]*\bid="ccq"[^>]*>', "section-ccq"),
        (CCQ_RE.pattern, "ccq"),
    ):
        for m in re.finditer(pattern, text):
            if m.start() >= main_start:
                return m.start(), kind

    matches = []
    canonical_wrapper = None
    for regex, kind in ((TABLE_RE, "table"), (TABLE_ANY_RE, "table"), (RULE_RE, "rule"), (BOX_WHY_RE, "rule"), (PAGER_RE, "pager")):
        for m in regex.finditer(text):
            if m.start() < main_start:
                continue
            if kind == "table" and in_canonical_table(text, m.start()):
                if canonical_wrapper is None:
                    canonical_wrapper = text.rfind("<div", main_start, m.start())
                continue
            matches.append((m.start(), kind))
            break
    if matches:
        return min(matches)
    if canonical_wrapper is not None:
        return canonical_wrapper, "table"
    return None, None


def remove_generated_ccq(text):
    """Remove previously generated CCQ blocks, matching nested divs correctly."""
    while True:
        m = re.search(r'<div class="(?:ccq|quiz)-panel"[^>]*data-tense-ccq="[^"]*"[^>]*>', text)
        if not m:
            return text
        start = m.start()
        pos = m.end()
        depth = 1
        tag = re.compile(r"<(/?)div\b[^>]*>", re.I)
        end = len(text)
        while depth and pos < len(text):
            t = tag.search(text, pos)
            if not t:
                break
            depth += -1 if t.group(1) else 1
            pos = t.end()
            if depth == 0:
                end = pos
        text = text[:start] + text[end:]


def extract_first_ccq(text):
    """Move a hand-authored CCQ panel so it sits directly below the timeline."""
    m = re.search(r'<div class="ccq-panel"(?![^>]*data-tense-ccq)[^>]*>', text)
    if not m:
        return None, text
    start = m.start()
    pos = m.end()
    depth = 1
    tag = re.compile(r"<(/?)div\b[^>]*>", re.I)
    end = len(text)
    while depth and pos < len(text):
        t = tag.search(text, pos)
        if not t:
            break
        depth += -1 if t.group(1) else 1
        pos = t.end()
        if depth == 0:
            end = pos
    return text[start:end], text[:start] + text[end:]


def process(path, profile_id, profile, lang, apply):
    source = open(path, encoding="utf-8", errors="surrogateescape").read()
    original = source

    source = remove_generated_ccq(source)
    source = TIMELINE_RE.sub("", source)
    if lang == "fr":
        source = source.replace(
            "<h3>💡 Check your understanding (CCQs)</h3>",
            "<h3>💡 Vérifiez votre compréhension (CCQ)</h3>",
        ).replace(
            "<h3>💡 Check your understanding</h3>",
            "<h3>💡 Vérifiez votre compréhension (CCQ)</h3>",
        )

    anchor, kind = find_anchor(source)
    if anchor is None:
        return "no anchor", source, original

    block = render_timeline(profile_id, profile, lang)
    if kind not in ("ccq", "section-ccq"):
        existing, stripped = extract_first_ccq(source)
        if existing:
            source = stripped
            anchor, kind = find_anchor(source)
            if anchor is None:
                return "no anchor", source, original
            ccq = existing
        elif profile.get("ccq"):
            if isinstance(profile["ccq"], str):
                ccq = render_en_ccq(profile_id, profile["ccq"])
            else:
                ccq = render_profile_ccq(profile_id, profile["ccq"], lang)
        else:
            ccq = render_quiz_ccq(source, profile_id)
        if ccq:
            block += "\n" + ccq
    block += "\n"

    new = source[:anchor] + block + source[anchor:]
    changed = new != original
    if apply and changed:
        open(path, "w", encoding="utf-8", errors="surrogateescape").write(new)
    return ("updated" if changed else "unchanged"), new, original


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="en")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", default=None, help="only this slug")
    args = parser.parse_args()

    if args.lang not in LANG:
        sys.exit(f"unsupported language: {args.lang}")

    global LANG_CODE
    LANG_CODE = args.lang
    profiles, slug_map = LANG[args.lang]
    registry = json.load(open(REGISTRY, encoding="utf-8"))["points"]
    targets = [
        p for p in registry
        if p["lang"] == args.lang and p["slug"] in slug_map
        and "/print/" not in p["path"] and not p["path"].endswith("-complet.html")
        and (args.limit is None or p["slug"] == args.limit)
    ]
    seen = set()
    for p in targets:
        if p["path"] in seen:
            continue
        seen.add(p["path"])
        profile_id = slug_map[p["slug"]]
        status, _, _ = process(p["path"], profile_id, profiles[profile_id], args.lang, args.apply)
        print(f"{status:10} {p['path']}  ->  {profile_id}")
    print(f"\n{len(seen)} page(s) {'updated' if args.apply else 'examined (dry run)'}")


if __name__ == "__main__":
    main()
