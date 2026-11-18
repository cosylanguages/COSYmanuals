#!/usr/bin/env python3
"""
Add full-manual download controls to print hubs
-----------------------------------------------
Every ``manuals/<lang>/print/index.html`` gets a small offline control bar
(below its ``.page-head``) linking to the full booklet and its downloadable
PDF, plus a print button. Idempotent: re-running does not duplicate the bar.

    python3 scripts/add_print_downloads.py
    python3 scripts/add_print_downloads.py --check
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "booklet-actions"

BAR = """<div class="booklet-actions no-print" role="group" aria-label="Offline options">
  <a class="print-btn" href="full.html">📖 Open full booklet</a>
  <a class="print-btn" href="full.pdf" download>⬇️ Download full PDF</a>
  <button type="button" class="print-btn" onclick="window.print()">🖨️ Print this page</button>
</div>
"""

PAGE_HEAD_RE = re.compile(r'(</div>\s*)(?=\s*<div class="box|\s*<section|\s*</main>)', re.IGNORECASE)


def inject(text: str) -> tuple[str, bool]:
    if MARKER in text:
        return text, False
    # Insert right after the first .page-head block (which ends with <hr class="rule"> ... </div>).
    m = re.search(r'(<div class="page-head">[\s\S]*?</div>)', text)
    if not m:
        return text, False
    insert_at = m.end()
    return text[:insert_at] + "\n" + BAR + text[insert_at:], True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    pages = sorted(ROOT.glob("manuals/*/print/index.html"))
    changed = 0
    missing = []
    for path in pages:
        text = path.read_text(encoding="utf-8")
        if args.check:
            if MARKER not in text:
                missing.append(str(path.relative_to(ROOT)))
            continue
        new_text, did = inject(text)
        if did:
            path.write_text(new_text, encoding="utf-8")
            changed += 1

    if args.check:
        if missing:
            print(f"{len(missing)} print hubs lack download controls:", file=sys.stderr)
            for rel in missing:
                print(f"  {rel}", file=sys.stderr)
            return 1
        print(f"OK: all {len(pages)} print hubs have download controls")
        return 0

    print(f"Updated {changed} of {len(pages)} print hubs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
