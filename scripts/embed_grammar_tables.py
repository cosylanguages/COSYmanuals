#!/usr/bin/env python3
"""Embed canonical COSYtools tables into gv-paradigm blocks by table ID.

The page owns only the placeholder and the pedagogical framing. The table
itself is fetched from COSYtools at build time and rendered as static HTML, so
the manual keeps working offline and in print.

Usage:
  python3 scripts/embed_grammar_tables.py                  # dry run, all manuals
  python3 scripts/embed_grammar_tables.py --apply          # write
  python3 scripts/embed_grammar_tables.py --lang fr        # one language
  python3 scripts/embed_grammar_tables.py --id fr:verb:parler:indicatif_present
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "grammar" / "table_index.json"
COSYTOOLS_HOST = "https://cosylanguages.github.io/COSYtools/"

_cache: dict[str, object] = {}


def fail(message: str) -> None:
    print(f"ERROR {message}", file=sys.stderr)


def load_index() -> dict[str, dict]:
    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    tables = data.get("tables")
    if not isinstance(tables, dict):
        raise SystemExit(f"{INDEX_PATH} has no 'tables' object")
    for table_id, entry in tables.items():
        for key in ("source_url", "data_url", "path", "caption", "render"):
            if key not in entry:
                raise SystemExit(f"{table_id}: missing '{key}'")
        if not entry["source_url"].startswith(COSYTOOLS_HOST):
            raise SystemExit(f"{table_id}: source_url must point at COSYtools")
        if not entry["data_url"].startswith(COSYTOOLS_HOST):
            raise SystemExit(f"{table_id}: data_url must point at COSYtools")
        if not isinstance(entry["path"], list) or not entry["path"]:
            raise SystemExit(f"{table_id}: path must be a non-empty list")
        if entry["render"].get("kind") not in ("list", "dict"):
            raise SystemExit(f"{table_id}: render.kind must be 'list' or 'dict'")
    return tables


def fetch_json(url: str):
    if url in _cache:
        return _cache[url]
    request = urllib.request.Request(
        url, headers={"User-Agent": "COSYmanuals table embed/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.load(response)
    _cache[url] = value
    return value


def resolve_path(value, path: list[str]):
    current = value
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(" / ".join(path))
        current = current[key]
    return current


def escape(value) -> str:
    return html.escape(str(value), quote=True)


def render_table(entry: dict, data) -> str:
    render = entry["render"]
    kind = render["kind"]
    caption = escape(entry["caption"])
    lines = ["<table>", f"<caption>{caption}</caption>"]

    if kind == "list":
        columns = render["columns"]
        lines.append(
            "<thead><tr>"
            + "".join(f'<th scope="col">{escape(c["header"])}</th>' for c in columns)
            + "</tr></thead>"
        )
        lines.append("<tbody>")
        rows = render.get("rows")
        if rows is not None and (not isinstance(rows, list) or len(rows) != len(data)):
            raise ValueError("render.rows must be a list with one label per form")
        for index, item in enumerate(data):
            if render.get("split_pronoun") and isinstance(item, str) and " " in item.strip():
                person, form = item.strip().split(" ", 1)
            else:
                person, form = (rows[index] if rows else ""), item
            lines.append(
                "<tr>"
                f'<th scope="row">{escape(person)}</th>'
                f"<td>{escape(form)}</td>"
                "</tr>"
            )
        lines.append("</tbody>")
    else:
        label_key = render["label_key"]
        columns = render["columns"]
        label_header = render.get("label_header", "")
        lines.append(
            "<thead><tr>"
            f'<th scope="col">{escape(label_header)}</th>'
            + "".join(f'<th scope="col">{escape(c["header"])}</th>' for c in columns)
            + "</tr></thead>"
        )
        lines.append("<tbody>")
        for row in render["rows"]:
            label = row.get(label_key, "")
            cells = []
            for column in columns:
                source_key = row.get(column["key"], column["key"])
                cell = data.get(source_key, "") if isinstance(data, dict) else ""
                cells.append(f"<td>{escape(cell)}</td>")
            lines.append(
                "<tr>"
                f'<th scope="row">{escape(label)}</th>'
                + "".join(cells)
                + "</tr>"
            )
        lines.append("</tbody>")

    lines.append("</table>")
    return "\n".join(lines)


def render_hash(entry: dict, data) -> str:
    payload = {"data": data, "entry": entry}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(raw).hexdigest()[:16]


def render_block(table_id: str, entry: dict, table_html: str, value_hash: str) -> str:
    caption = escape(entry["caption"])
    source_url = escape(entry["source_url"])
    source_label = escape(entry.get("source_label", "Source:"))
    source = escape(entry.get("source", "cosytools"))
    return (
        f'<div class="gv gv-paradigm" tabindex="0" role="region" aria-label="{caption}" '
        f'data-table-id="{escape(table_id)}" data-source="{source}" '
        f'data-source-url="{source_url}" data-source-hash="{value_hash}">\n'
        f"<!-- gv-table:start {escape(table_id)} {value_hash} -->\n"
        f"{table_html}\n"
        f'<p class="gv-source">{source_label} '
        f'<a href="{source_url}" target="_blank" rel="noopener">COSYtools</a></p>\n'
        "<!-- gv-table:end -->\n"
        "</div>"
    )


def process_one(text: str, table_id: str, entry: dict) -> tuple[str, bool, str]:
    pattern = re.compile(
        r'<div\b(?P<attrs>[^>]*\bdata-table-id="'
        + re.escape(table_id)
        + r'"[^>]*)>(?P<inner>.*?)</div>',
        re.S,
    )
    match = pattern.search(text)
    if not match:
        return text, False, "placeholder not found"

    try:
        source = fetch_json(entry["data_url"])
        data = resolve_path(source, entry["path"])
    except Exception as exc:  # network, JSON, or missing key
        return text, False, f"could not resolve table: {exc}"

    value_hash = render_hash(entry, data)
    old_hash = re.search(r'data-source-hash="([^"]+)"', match.group("attrs"))
    if old_hash and old_hash.group(1) == value_hash and "<table" in match.group("inner"):
        return text, False, "unchanged"

    table_html = render_table(entry, data)
    block = render_block(table_id, entry, table_html, value_hash)
    return text[: match.start()] + block + text[match.end():], True, "updated"


def iter_pages(lang: str | None):
    base = ROOT / "manuals" / lang / "grammar" if lang else ROOT / "manuals"
    if not base.exists():
        return
    yield from sorted(base.rglob("*.html"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes")
    parser.add_argument("--lang", help="only one language, e.g. fr")
    parser.add_argument("--id", dest="table_id", help="only one table ID")
    parser.add_argument("--limit", type=int, help="stop after N changed pages")
    args = parser.parse_args()

    tables = load_index()
    scanned = changed = unchanged = errors = 0

    for path in iter_pages(args.lang):
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        ids = sorted(set(re.findall(r'data-table-id="([^"]+)"', text)))
        if args.table_id:
            ids = [table_id for table_id in ids if table_id == args.table_id]
        if not ids:
            continue
        scanned += 1
        for table_id in ids:
            entry = tables.get(table_id)
            if not entry:
                fail(f"{path.relative_to(ROOT)}: unknown data-table-id {table_id}")
                errors += 1
                continue
            new_text, did_change, status = process_one(text, table_id, entry)
            if did_change:
                text = new_text
                changed += 1
                print(f"{'UPDATE' if args.apply else 'WOULD UPDATE'} {path.relative_to(ROOT)} :: {table_id}")
                if args.apply:
                    path.write_text(text, encoding="utf-8", errors="surrogateescape")
            else:
                unchanged += 1
                if status != "unchanged":
                    print(f"SKIP {path.relative_to(ROOT)} :: {table_id} :: {status}")

        if args.limit and changed >= args.limit:
            break

    print(
        f"{scanned} page(s) with table placeholders; "
        f"{changed} {'updated' if args.apply else 'would update'}; "
        f"{unchanged} unchanged; {errors} error(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
