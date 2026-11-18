#!/usr/bin/env python3
"""
COSYmanuals Grammar Point ID Assignment
---------------------------------------
Every grammar explanation page owns a stable, citable id of the form
``<lang>-<level>-<slug>`` (e.g. ``en-a1-adjectives``). The id is written onto
the page's ``<main>`` element as both ``id`` (deep-link anchor) and
``data-grammar-point`` (machine hook used by the embed component), and the
whole set is exported to ``data/grammar-points.json``.

The id is derived only from the file path, so it never changes when the title
or body is edited. Later content can reference a grammar point instead of
re-authoring it:

    <div data-grammar-embed="en-a1-adjectives"></div>

Run:
    python3 scripts/assign_grammar_ids.py            # assign + write registry
    python3 scripts/assign_grammar_ids.py --check     # fail if any page lacks an id
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUALS = ROOT / "manuals"
REGISTRY = ROOT / "data" / "grammar-points.json"
INDEX = ROOT / "data" / "grammar-points.index.json"
BASE_URL = "https://cosylanguages.github.io/COSYmanuals/"

TOPIC_GLOB = "*/grammar/*/topics/*.html"
# Most pages wrap the explanation in <main>; a few legacy stubs use a bare
# <div class="container">. Both are treated as the explanation root.
MAIN_RE = re.compile(
    r"<main\b[^>]*>|<div\b[^>]*\bclass=\"[^\"]*\bcontainer\b[^\"]*\"[^>]*>",
    re.IGNORECASE,
)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
SUBTITLE_RE = re.compile(
    r'<p class="subtitle"[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")


def point_id(path: Path) -> str:
    """Derive the stable id from the path: manuals/<lang>/grammar/<level>/topics/<slug>.html."""
    parts = path.relative_to(MANUALS).parts
    lang, _module, level, _topics, filename = parts
    slug = filename[:-5] if filename.endswith(".html") else filename
    return f"{lang}-{level}-{slug}".lower()


def _clean(text: str) -> str:
    return html.unescape(TAG_RE.sub("", text)).strip()


def extract_meta(text: str) -> dict:
    h1 = H1_RE.search(text)
    subtitle = SUBTITLE_RE.search(text)
    title = TITLE_RE.search(text)
    return {
        "title": _clean(h1.group(1)) if h1 else (_clean(title.group(1)) if title else ""),
        "subtitle": _clean(subtitle.group(1)) if subtitle else "",
    }


def inject(text: str, gid: str) -> tuple[str, bool]:
    """Add id + data-grammar-point to the first <main> tag. Returns (text, changed)."""
    match = MAIN_RE.search(text)
    if not match:
        return text, False
    tag = match.group(0)
    if "data-grammar-point" in tag:
        return text, False
    if re.search(r'\bid="', tag):
        new_tag = re.sub(r'\bid="[^"]*"', f'id="{gid}"', tag, count=1)
    else:
        new_tag = tag[:-1].rstrip() + f' id="{gid}">'
    new_tag = new_tag[:-1].rstrip() + f' data-grammar-point="{gid}">'
    return text[: match.start()] + new_tag + text[match.end():], True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify ids, do not write")
    args = parser.parse_args()

    pages = sorted(MANUALS.glob(TOPIC_GLOB))
    if not pages:
        print("No grammar topic pages found", file=sys.stderr)
        return 1

    points = []
    changed = 0
    missing_main = []
    seen = {}

    for path in pages:
        gid = point_id(path)
        if gid in seen:
            print(f"Duplicate id {gid}: {path} and {seen[gid]}", file=sys.stderr)
            return 1
        seen[gid] = path

        text = path.read_text(encoding="utf-8")
        if not MAIN_RE.search(text):
            missing_main.append(str(path.relative_to(ROOT)))
            continue

        if not args.check:
            new_text, did = inject(text, gid)
            if did:
                path.write_text(new_text, encoding="utf-8")
                text = new_text
                changed += 1

        meta = extract_meta(text)
        rel = path.relative_to(ROOT).as_posix()
        points.append(
            {
                "id": gid,
                "lang": gid.split("-", 1)[0],
                "level": path.relative_to(MANUALS).parts[2],
                "slug": path.stem,
                "title": meta["title"],
                "subtitle": meta["subtitle"],
                "path": rel,
                "url": BASE_URL + rel,
            }
        )

    if missing_main:
        print(f"Pages without <main> (skipped): {len(missing_main)}", file=sys.stderr)
        for rel in missing_main[:10]:
            print(f"  {rel}", file=sys.stderr)

    if args.check:
        unstamped = []
        for path in pages:
            text = path.read_text(encoding="utf-8")
            if MAIN_RE.search(text) and "data-grammar-point" not in text:
                unstamped.append(str(path.relative_to(ROOT)))
        if unstamped:
            print(f"{len(unstamped)} grammar pages lack data-grammar-point:", file=sys.stderr)
            for rel in unstamped[:10]:
                print(f"  {rel}", file=sys.stderr)
            return 1
        print(f"OK: all {len(pages)} grammar pages carry a grammar-point id")
        return 0

    points.sort(key=lambda p: p["id"])
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "count": len(points),
                "id_format": "<lang>-<level>-<slug>",
                "points": points,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    # Compact lookup index: id -> path only, for the embed component.
    index = {p["id"]: p["path"] for p in points}
    INDEX.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Stamped {changed} pages, registry has {len(points)} grammar points")
    print(f"Wrote {REGISTRY.relative_to(ROOT)} and {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
