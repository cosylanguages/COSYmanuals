#!/usr/bin/env python3
"""Add or refresh the gv-lookup CTA card on configured grammar pages.

The card points to the language's COSYtools tool. It is static HTML: the
visible URL makes it useful in print, and no JavaScript or network is needed
on the manual page.

Usage:
  python3 scripts/add_lookup_cards.py            # dry run
  python3 scripts/add_lookup_cards.py --apply    # write
  python3 scripts/add_lookup_cards.py --lang fr  # one language
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "grammar" / "lookup_pages.json"
BASE = "https://cosylanguages.github.io/COSYtools/"
START = "<!-- gv-lookup:start -->"
END = "<!-- gv-lookup:end -->"
ANCHORS = ['<div class="mistakes"', '<div class="checklist"', '<div class="pager"', "</main>"]

TOOLS = {
    "en": {
        "principal-parts": "tools/en/irregular-verbs/",
        "government": "tools/en/verb-prep/",
    },
    "fr": {
        "conjugation": "tools/fr/conjugeur/",
        "government": "tools/fr/regime/",
        "gender": "tools/fr/genre/",
    },
    "ru": {
        "cases": "tools/ru/rod-padezhi/",
        "conjugation": "tools/ru/spryazhenie/",
    },
    "de": {
        "conjugation": "tools/de/konjugation/",
        "government": "tools/de/praepositionen/",
        "gender": "tools/de/genus/",
    },
    "es": {
        "conjugation": "tools/es/conjugeur/",
        "gender": "tools/es/genre/",
    },
    "it": {
        "conjugation": "tools/it/coniugatore/",
        "government": "tools/it/reggenza/",
        "gender": "tools/it/genere/",
    },
    "pt": {
        "conjugation": "tools/pt/conjugeur/",
        "gender": "tools/pt/genre/",
    },
    "el": {
        "cases": "tools/el/genos-ptoseis/",
        "conjugation": "tools/el/klisi-rimaton/",
    },
}

LABELS = {
    "en": {
        "aria": "Look up forms in COSYtools",
        "link": "Open COSYtools →",
        "cases": "See all cases of any noun.",
        "conjugation": "Conjugate any verb.",
        "principal-parts": "Check irregular verb forms.",
        "government": "Check verb + preposition patterns.",
        "gender": "Check noun gender.",
    },
    "fr": {
        "aria": "Consulter les formes dans COSYtools",
        "link": "Ouvrir COSYtools →",
        "cases": "Voir tous les cas d'un nom.",
        "conjugation": "Conjuguez n'importe quel verbe.",
        "principal-parts": "Vérifiez les formes irrégulières.",
        "government": "Vérifiez les verbes et leurs prépositions.",
        "gender": "Vérifiez le genre d'un nom.",
    },
    "ru": {
        "aria": "Посмотреть формы в COSYtools",
        "link": "Открыть COSYtools →",
        "cases": "Посмотрите все падежи любого существительного.",
        "conjugation": "Проспрягайте любой глагол.",
        "principal-parts": "Проверьте формы неправильных глаголов.",
        "government": "Проверьте управление глаголов и предлоги.",
        "gender": "Проверьте род существительного.",
    },
    "de": {
        "aria": "Formen in COSYtools nachschlagen",
        "link": "COSYtools öffnen →",
        "cases": "Alle Fälle eines Nomens ansehen.",
        "conjugation": "Jedes Verb konjugieren.",
        "principal-parts": "Unregelmäßige Verbformen prüfen.",
        "government": "Verben und ihre Präpositionen prüfen.",
        "gender": "Das Genus eines Nomens prüfen.",
    },
    "es": {
        "aria": "Consultar formas en COSYtools",
        "link": "Abrir COSYtools →",
        "cases": "Consulta todos los casos de un sustantivo.",
        "conjugation": "Conjuga cualquier verbo.",
        "principal-parts": "Consulta las formas irregulares.",
        "government": "Comprueba verbos y preposiciones.",
        "gender": "Comprueba el género de un sustantivo.",
    },
    "it": {
        "aria": "Consultare le forme in COSYtools",
        "link": "Apri COSYtools →",
        "cases": "Controlla tutti i casi di un nome.",
        "conjugation": "Coniuga qualsiasi verbo.",
        "principal-parts": "Controlla le forme irregolari.",
        "government": "Controlla verbi e preposizioni.",
        "gender": "Controlla il genere di un nome.",
    },
    "pt": {
        "aria": "Consultar formas no COSYtools",
        "link": "Abrir COSYtools →",
        "cases": "Consulte todos os casos de um substantivo.",
        "conjugation": "Conjugue qualquer verbo.",
        "principal-parts": "Consulte as formas irregulares.",
        "government": "Verifique verbos e preposições.",
        "gender": "Verifique o género de um substantivo.",
    },
    "el": {
        "aria": "Αναζήτηση τύπων στο COSYtools",
        "link": "Άνοιγμα COSYtools →",
        "cases": "Δείτε όλες τις πτώσεις οποιουδήποτε ουσιαστικού.",
        "conjugation": "Κλίνετε οποιοδήποτε ρήμα.",
        "principal-parts": "Ελέγξτε τους ανώμαλους τύπους.",
        "government": "Ελέγξτε τα ρήματα και τις προθέσεις.",
        "gender": "Ελέγξτε το γένος ενός ουσιαστικού.",
    },
}


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def card_html(lang: str, lookup: str) -> str:
    url = BASE + TOOLS[lang][lookup]
    labels = LABELS[lang]
    return (
        f"{START}\n"
        f'<aside class="gv gv-lookup" data-lookup="{escape(lookup)}" data-lang="{escape(lang)}" '
        f'aria-label="{escape(labels["aria"])}">\n'
        f'  <span class="gv-lookup-kicker">COSYtools</span>\n'
        f'  <p class="gv-lookup-text">{escape(labels[lookup])}</p>\n'
        f'  <span class="gv-lookup-action"><a class="gv-lookup-link" href="{escape(url)}" '
        f'target="_blank" rel="noopener">{escape(labels["link"])}</a>'
        f'<span class="gv-lookup-url">{escape(url.replace("https://", ""))}</span></span>\n'
        f"</aside>\n"
        f"{END}"
    )


def insert_card(text: str, card: str) -> tuple[str, str]:
    if START in text and END in text:
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        new_text = pattern.sub(card, text, count=1)
        return new_text, "unchanged" if new_text == text else "updated"

    positions = [(text.find(anchor), anchor) for anchor in ANCHORS if text.find(anchor) != -1]
    if not positions:
        return text, "no anchor"
    position, _ = min(positions)
    return text[:position] + card + "\n\n" + text[position:], "inserted"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--lang", help="only one language, e.g. fr")
    parser.add_argument("--path", help="only one page path")
    parser.add_argument("--limit", type=int, help="stop after N changed pages")
    args = parser.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    pages = config.get("pages", [])
    scanned = changed = unchanged = errors = 0

    for page in pages:
        lang = page.get("lang")
        lookup = page.get("lookup")
        path_value = page.get("path")
        if not lang or not lookup or not path_value:
            print(f"ERROR invalid config entry: {page}", file=sys.stderr)
            errors += 1
            continue
        if args.lang and args.lang != lang:
            continue
        if args.path and args.path != path_value:
            continue
        if lang not in TOOLS or lookup not in TOOLS[lang]:
            print(f"ERROR {lang}: no COSYtools target for '{lookup}'", file=sys.stderr)
            errors += 1
            continue
        if lang not in LABELS or lookup not in LABELS[lang]:
            print(f"ERROR {lang}: no labels for '{lookup}'", file=sys.stderr)
            errors += 1
            continue

        path = ROOT / path_value
        if not path.exists():
            print(f"ERROR missing page {path_value}", file=sys.stderr)
            errors += 1
            continue
        if f"/{lang}/" not in f"/{path_value}":
            print(f"ERROR {path_value}: lang '{lang}' does not match the path", file=sys.stderr)
            errors += 1
            continue

        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        card = card_html(lang, lookup)
        new_text, status = insert_card(text, card)
        scanned += 1
        if status in ("inserted", "updated") and new_text != text:
            changed += 1
            print(f"{'APPLY' if args.apply else 'WOULD APPLY'} {path_value} :: {lang}:{lookup} :: {status}")
            if args.apply:
                path.write_text(new_text, encoding="utf-8", errors="surrogateescape")
        elif status == "unchanged":
            unchanged += 1
        else:
            errors += 1
            print(f"ERROR {path_value}: {status}", file=sys.stderr)
        if args.limit and changed >= args.limit:
            break

    print(
        f"{scanned} page(s); {changed} {'changed' if args.apply else 'would change'}; "
        f"{unchanged} unchanged; {errors} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
