#!/usr/bin/env python3
"""Insert gv-paradigm placeholders for the pages in data/grammar/table_pages.json.

The placeholder is intentionally minimal: the embed script owns the rendered
table, provenance, and hashes. This script is idempotent because it skips any
table ID that already appears on the page.

Usage:
  python3 scripts/add_table_placeholders.py            # dry run
  python3 scripts/add_table_placeholders.py --apply    # write
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "data" / "grammar" / "table_pages.json"
PLACEHOLDER = '<div class="gv gv-paradigm" data-table-id="{table_id}" data-source="cosytools"></div>'

ANCHORS = (
    "<!-- gv-lookup:start",
    '<div class="mistakes"',
    '<section class="mistakes"',
    '<div class="checklist"',
    '<div class="pager"',
    "</main>",
)


def insert_before_anchor(text: str, block: str) -> str | None:
    for anchor in ANCHORS:
        position = text.find(anchor)
        if position == -1:
            continue
        line_start = text.rfind("\n", 0, position) + 1
        return text[:line_start] + block + "\n" + text[line_start:]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    errors = 0

    for page in config.get("pages", []):
        path = ROOT / page["path"]
        if not path.exists():
            print(f"ERROR missing {page['path']}")
            errors += 1
            continue
        text = path.read_text(encoding="utf-8")
        table_ids = page.get("table_ids", [])
        if not isinstance(table_ids, list) or not table_ids:
            print(f"ERROR no table_ids for {page['path']}")
            errors += 1
            continue

        missing = [table_id for table_id in table_ids if f'data-table-id="{table_id}"' not in text]
        if not missing:
            print(f"SKIP {page['path']} (all present)")
            continue

        partial = len(missing) != len(table_ids)
        parts = []
        if page.get("intro") and not partial:
            parts.append(page["intro"])
        for table_id in missing:
            parts.append(PLACEHOLDER.format(table_id=table_id))
        block = "\n".join(parts)

        updated = insert_before_anchor(text, block)
        if updated is None:
            print(f"ERROR no anchor in {page['path']}")
            errors += 1
            continue

        if args.apply:
            path.write_text(updated, encoding="utf-8")
            print(f"INSERT {page['path']} :: {', '.join(missing)}")
        else:
            print(f"WOULD INSERT {page['path']} :: {', '.join(missing)}")

    print(f"{len(config.get('pages', []))} page(s); {errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
