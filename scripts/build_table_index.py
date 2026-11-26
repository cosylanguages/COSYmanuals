#!/usr/bin/env python3
"""Build canonical table_index entries for the conjugation/case rollout.

The index stays the single source of table IDs. This script adds entries from
a curated rollout list; it preserves hand-written entries and verifies each
lemma/tense/case against the live COSYtools JSON before writing.

Usage:
  python3 scripts/build_table_index.py            # dry run
  python3 scripts/build_table_index.py --apply    # write
  python3 scripts/build_table_index.py --lang fr  # one language
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "grammar" / "table_index.json"
TOOLS = "https://cosylanguages.github.io/COSYtools/tools/"

sys.path.insert(0, str(ROOT / "scripts"))
from embed_grammar_tables import fetch_json  # noqa: E402

VERB_SOURCES = {
    "fr": {
        "source_url": TOOLS + "fr/conjugeur/",
        "data_url": TOOLS + "fr/conjugeur/data/verbs.json",
        "source_label": "Source :",
        "split_pronoun": True,
        "rows": None,
        "columns": [
            {"key": "person", "header": "personne"},
            {"key": "form", "header": "forme"},
        ],
        "labels": {"indicatif_present": "présent de l'indicatif"},
        "lemmas": {
            "être": ["indicatif_present"],
            "avoir": ["indicatif_present"],
            "aller": ["indicatif_present"],
            "faire": ["indicatif_present"],
            "parler": ["indicatif_present"],
        },
    },
    "es": {
        "source_url": TOOLS + "es/conjugeur/",
        "data_url": TOOLS + "es/conjugeur/data/verbs.json",
        "source_label": "Fuente:",
        "split_pronoun": False,
        "rows": ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas"],
        "columns": [
            {"key": "person", "header": "persona"},
            {"key": "form", "header": "forma"},
        ],
        "labels": {"presente": "presente de indicativo"},
        "lemmas": {
            "hablar": ["presente"],
            "ser": ["presente"],
            "estar": ["presente"],
        },
    },
    "it": {
        "source_url": TOOLS + "it/coniugatore/",
        "data_url": TOOLS + "it/coniugatore/data/verbs.json",
        "source_label": "Fonte:",
        "split_pronoun": False,
        "rows": ["io", "tu", "lui/lei", "noi", "voi", "loro"],
        "columns": [
            {"key": "person", "header": "persona"},
            {"key": "form", "header": "forma"},
        ],
        "labels": {"pres": "presente indicativo"},
        "lemmas": {
            "parlare": ["pres"],
            "essere": ["pres"],
            "avere": ["pres"],
        },
    },
    "pt": {
        "source_url": TOOLS + "pt/conjugeur/",
        "data_url": TOOLS + "pt/conjugeur/data/verbs.json",
        "source_label": "Fonte:",
        "split_pronoun": False,
        "rows": ["eu", "tu", "ele/ela", "nós", "vós", "eles/elas"],
        "columns": [
            {"key": "person", "header": "pessoa"},
            {"key": "form", "header": "forma"},
        ],
        "labels": {"presente": "presente do indicativo"},
        "lemmas": {
            "falar": ["presente"],
            "ser": ["presente"],
            "estar": ["presente"],
        },
    },
    "de": {
        "source_url": TOOLS + "de/konjugation/",
        "data_url": TOOLS + "de/konjugation/data/verbs.json",
        "source_label": "Quelle:",
        "split_pronoun": True,
        "rows": None,
        "columns": [
            {"key": "person", "header": "Person"},
            {"key": "form", "header": "Form"},
        ],
        "labels": {"präsens": "Präsens"},
        "lemmas": {
            "lernen": ["präsens"],
            "sein": ["präsens"],
            "haben": ["präsens"],
        },
    },
    "ru": {
        "source_url": TOOLS + "ru/spryazhenie/",
        "data_url": TOOLS + "ru/spryazhenie/data/verbs.json",
        "source_label": "Источник:",
        "split_pronoun": True,
        "rows": None,
        "columns": [
            {"key": "person", "header": "лицо"},
            {"key": "form", "header": "форма"},
        ],
        "labels": {
            "pres": "настоящее время",
            "past": "прошедшее время",
            "fut": "будущее время",
        },
        "lemmas": {
            "читать": ["pres"],
            "говорить": ["pres"],
            "быть": ["past", "fut"],
            "хотеть": ["pres"],
            "мочь": ["pres"],
        },
    },
    "el": {
        "source_url": TOOLS + "el/klisi-rimaton/",
        "data_url": TOOLS + "el/klisi-rimaton/data/verbs.json",
        "source_label": "Πηγή:",
        "split_pronoun": False,
        "rows": ["εγώ", "εσύ", "αυτός/αυτή", "εμείς", "εσείς", "αυτοί/αυτές"],
        "columns": [
            {"key": "person", "header": "πρόσωπο"},
            {"key": "form", "header": "τύπος"},
        ],
        "labels": {"pres": "ενεστώτας"},
        "lemmas": {"είμαι": ["pres"]},
    },
}

CASE_SOURCES = {
    "ru": {
        "source_url": TOOLS + "ru/rod-padezhi/",
        "data_url": TOOLS + "ru/rod-padezhi/data/nouns.json",
        "source_label": "Источник:",
        "caption": "падежи",
        "label_header": "падеж",
        "columns": [
            {"key": "singular", "header": "единственное число"},
            {"key": "plural", "header": "множественное число"},
        ],
        "row_labels": [
            ("nom", "Именительный"),
            ("gen", "Родительный"),
            ("dat", "Дательный"),
            ("acc", "Винительный"),
            ("ins", "Творительный"),
            ("pre", "Предложный"),
        ],
        "lemmas": ["дом"],
    },
}


def verb_entry(lang: str, cfg: dict, lemma: str, tense: str, forms: list) -> dict:
    render = {
        "kind": "list",
        "split_pronoun": cfg["split_pronoun"],
        "columns": cfg["columns"],
    }
    if cfg["rows"]:
        if len(cfg["rows"]) != len(forms):
            raise ValueError(
                f"{lang}:{lemma}:{tense}: {len(cfg['rows'])} row labels for {len(forms)} forms"
            )
        render["rows"] = cfg["rows"]
    return {
        "source": "cosytools",
        "source_url": cfg["source_url"],
        "data_url": cfg["data_url"],
        "path": [lemma, "tenses", tense],
        "lang": lang,
        "pos": "verb",
        "lemma": lemma,
        "feature": tense,
        "caption": f"{lemma} · {cfg['labels'][tense]}",
        "source_label": cfg["source_label"],
        "render": render,
    }


def case_entry(lang: str, cfg: dict, lemma: str) -> dict:
    rows = []
    for key, label in cfg["row_labels"]:
        rows.append(
            {
                "case": label,
                "singular": f"{key}_sing",
                "plural": f"{key}_plur",
            }
        )
    return {
        "source": "cosytools",
        "source_url": cfg["source_url"],
        "data_url": cfg["data_url"],
        "path": [lemma, "cases"],
        "lang": lang,
        "pos": "noun",
        "lemma": lemma,
        "feature": "cases",
        "caption": f"{lemma} · {cfg['caption']}",
        "source_label": cfg["source_label"],
        "render": {
            "kind": "dict",
            "label_key": "case",
            "label_header": cfg["label_header"],
            "columns": cfg["columns"],
            "rows": rows,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--lang", help="only one language, e.g. fr")
    args = parser.parse_args()

    existing = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    tables = existing.get("tables", {})
    generated: dict[str, dict] = {}
    errors = 0

    for lang, cfg in VERB_SOURCES.items():
        if args.lang and args.lang != lang:
            continue
        data = fetch_json(cfg["data_url"])
        for lemma, tenses in cfg["lemmas"].items():
            entry = data.get(lemma)
            if not isinstance(entry, dict):
                print(f"ERROR {lang}: missing lemma {lemma}", file=sys.stderr)
                errors += 1
                continue
            for tense in tenses:
                forms = entry.get("tenses", {}).get(tense)
                if not isinstance(forms, list):
                    print(f"ERROR {lang}:{lemma}: missing tense {tense}", file=sys.stderr)
                    errors += 1
                    continue
                try:
                    table_id = f"{lang}:verb:{lemma}:{tense}"
                    generated[table_id] = verb_entry(lang, cfg, lemma, tense, forms)
                except ValueError as exc:
                    print(f"ERROR {exc}", file=sys.stderr)
                    errors += 1

    for lang, cfg in CASE_SOURCES.items():
        if args.lang and args.lang != lang:
            continue
        data = fetch_json(cfg["data_url"])
        for lemma in cfg["lemmas"]:
            entry = data.get(lemma)
            cases = entry.get("cases") if isinstance(entry, dict) else None
            if not isinstance(cases, dict):
                print(f"ERROR {lang}: missing noun {lemma}", file=sys.stderr)
                errors += 1
                continue
            missing = [f"{key}_sing" for key, _ in cfg["row_labels"] if f"{key}_sing" not in cases]
            missing += [f"{key}_plur" for key, _ in cfg["row_labels"] if f"{key}_plur" not in cases]
            if missing:
                print(f"ERROR {lang}:{lemma}: missing cases {missing}", file=sys.stderr)
                errors += 1
                continue
            generated[f"{lang}:noun:{lemma}:cases"] = case_entry(lang, cfg, lemma)

    added = [table_id for table_id in generated if table_id not in tables]
    updated = [
        table_id for table_id in generated if table_id in tables and tables[table_id] != generated[table_id]
    ]
    for table_id in added:
        print(f"{'ADD' if args.apply else 'WOULD ADD'} {table_id}")
    for table_id in updated:
        print(f"{'UPDATE' if args.apply else 'WOULD UPDATE'} {table_id}")

    if args.apply and (added or updated):
        merged = dict(tables)
        merged.update(generated)
        INDEX_PATH.write_text(
            json.dumps({"version": existing.get("version", 1), "tables": merged}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )

    print(
        f"{len(generated)} table(s); {len(added)} {'added' if args.apply else 'would add'}; "
        f"{len(updated)} {'updated' if args.apply else 'would update'}; {errors} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
