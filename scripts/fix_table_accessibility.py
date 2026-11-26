#!/usr/bin/env python3
"""Make legacy .table-wrap tables focusable, named regions with scoped headers.

This is the targeted subset of scripts/upgrade_tables.py needed when a page is
otherwise ready but still has an unwrapped legacy table. It preserves the
existing HTML formatting and is idempotent.

Usage:
  python3 scripts/fix_table_accessibility.py manuals/fr/grammar/a1/topics/*.html
  python3 scripts/fix_table_accessibility.py --apply <paths...>
"""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

HEADING = re.compile(r"<h[1-4]\b[^>]*>(.*?)</h[1-4]>", re.S | re.I)
WRAP = re.compile(r'(<div class="table-wrap")([^>]*)>(.*?)</div>', re.S)
NO_SCOPE = re.compile(r"<th(?=[\s>])(?![^>]*\bscope=)")


def label_for(text: str, position: int) -> str:
    headings = list(HEADING.finditer(text[:position]))
    if not headings:
        return "Tableau"
    value = html.unescape(re.sub(r"<[^>]+>", "", headings[-1].group(1))).strip()
    return value or "Tableau"


def table_label(body: str, text: str, position: int) -> str:
    first = re.search(r"<th\b[^>]*>(.*?)</th>", body, re.S | re.I)
    if first:
        value = html.unescape(re.sub(r"<[^>]+>", "", first.group(1))).strip()
        if value:
            return value
    return label_for(text, position)


def fix_wrap(match: re.Match, text: str) -> tuple[str, int]:
    attrs = match.group(2)
    body = match.group(3)
    fixes = 0

    if "tabindex=" not in attrs:
        attrs += ' tabindex="0"'
        fixes += 1
    if "role=" not in attrs:
        attrs += ' role="region"'
        fixes += 1
    label = html.escape(table_label(body, text, match.start()), quote=True)
    if "aria-label=" not in attrs and "aria-labelledby=" not in attrs:
        attrs += f' aria-label="{label}" data-gv-autolabel="1"'
        fixes += 1
    elif 'data-gv-autolabel="1"' in attrs:
        current = re.search(r'aria-label="([^"]*)"', attrs)
        if current and current.group(1) != label:
            attrs = re.sub(r'aria-label="[^"]*"', f'aria-label="{label}"', attrs, count=1)
            fixes += 1

    if "</thead>" in body:
        head, rest = body.split("</thead>", 1)
        head, count = NO_SCOPE.subn('<th scope="col"', head)
        fixes += count
        body = head + "</thead>" + rest
    body, count = NO_SCOPE.subn('<th scope="row"', body)
    fixes += count

    return f"{match.group(1)}{attrs}>{body}</div>", fixes


def process(path: Path, apply: bool) -> int:
    text = path.read_text(encoding="utf-8")
    total = 0

    def replace(match: re.Match) -> str:
        nonlocal total
        updated, fixes = fix_wrap(match, text)
        total += fixes
        return updated

    updated = WRAP.sub(replace, text)
    if apply and updated != text:
        path.write_text(updated, encoding="utf-8")
    print(f"{'FIX' if apply else 'WOULD FIX'} {path} :: {total} change(s)")
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    files = []
    for path in args.paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.html")))
        else:
            files.append(path)

    changes = 0
    for path in files:
        changes += process(path, args.apply)
    print(f"{len(files)} file(s); {changes} change(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
