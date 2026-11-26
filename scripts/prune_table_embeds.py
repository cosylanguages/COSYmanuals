#!/usr/bin/env python3
"""Remove duplicated gv-paradigm embeds from pages that already teach the paradigm.

A hand-made table is often richer than a single-lemma canonical table (multiple
verbs, stem/ending splits, negative/interrogative columns). When that table is
already present, a second canonical table is noise. This script removes the
canonical embed and its intro, and drops the page from table_pages.json.

Usage:
  python3 scripts/prune_table_embeds.py            # dry run
  python3 scripts/prune_table_embeds.py --apply    # write
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "data" / "grammar" / "table_pages.json"
INTRO = re.compile(
    r"<p>(?:(?!</p>).)*(?:paradig|парадигм|παράδειγμα)(?:(?!</p>).)*</p>\s*$",
    re.I | re.S,
)

PRUNE = {
    "manuals/es/grammar/a1/topics/presente-indicativo.html": ["es:verb:hablar:presente"],
    "manuals/it/grammar/a1/topics/presente-regolare.html": ["it:verb:parlare:pres"],
    "manuals/pt/grammar/a1/topics/presente-do-indicativo.html": ["pt:verb:falar:presente"],
    "manuals/de/grammar/a1/topics/praesens-regelmaessig.html": ["de:verb:lernen:präsens"],
    "manuals/ru/grammar/a1/topics/budushchee-vremya-spryazhenie.html": ["ru:verb:быть:fut"],
    "manuals/it/grammar/a1/topics/essere-avere.html": ["it:verb:essere:pres", "it:verb:avere:pres"],
    "manuals/el/grammar/a1/topics/to-rima-eimai.html": ["el:verb:είμαι:pres"],
}


def div_end(text: str, start: int) -> int | None:
    depth = 0
    for match in re.finditer(r"<div\b|</div>", text[start:]):
        if match.group(0) == "<div":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start + match.end()
    return None


def remove_embed(text: str, table_id: str) -> tuple[str, bool]:
    pattern = re.compile(
        r'<div class="gv gv-paradigm"[^>]*data-table-id="' + re.escape(table_id) + r'"[^>]*>'
    )
    match = pattern.search(text)
    if not match:
        return text, False
    end = div_end(text, match.start())
    if end is None:
        raise ValueError(f"unbalanced gv-paradigm block for {table_id}")
    text = text[: match.start()] + text[end:]
    text = INTRO.sub("", text[: match.start()]) + text[match.start() :]
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args()

    removed = 0
    for relative, table_ids in PRUNE.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        for table_id in table_ids:
            try:
                text, changed = remove_embed(text, table_id)
            except ValueError as exc:
                print(f"ERROR {relative}: {exc}")
                return 1
            if changed:
                removed += 1
        if args.apply:
            path.write_text(text, encoding="utf-8")
        print(f"{'PRUNE' if args.apply else 'WOULD PRUNE'} {relative} :: {', '.join(table_ids)}")

    if args.apply:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config["pages"] = [page for page in config.get("pages", []) if page["path"] not in PRUNE]
        CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(PRUNE)} page(s); {removed} embed(s) removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
