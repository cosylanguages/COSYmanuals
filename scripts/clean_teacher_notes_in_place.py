#!/usr/bin/env python3
"""
COSYmanuals In-Place Teacher Notes Cleaner
------------------------------------------
Scans all .html and .md files under manuals/, finds raw teacher_notes
monospace <div> tags (HTML) or ```text ... ``` blocks (Markdown) containing
'code:' or 'pronunciation:', parses them via parse_teacher_notes(),
and replaces ONLY those blocks with cleanly rendered HTML / Markdown.

Idempotent: running twice results in 0 file changes.
Logs and skips any block that fails to parse.
"""

import html
import re
import sys
from pathlib import Path

# Ensure scripts directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_manuals import parse_teacher_notes, render_teacher_notes_html, render_teacher_notes_md


def process_html_file(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    matches = list(re.finditer(
        r"<div\s+style=['\"][^'\"]*font-family:\s*monospace[^'\"]*['\"][^>]*>(.*?)</div>",
        content,
        re.DOTALL | re.IGNORECASE
    ))
    if not matches:
        return False, []

    skipped = []
    replacements = []

    for m in matches:
        raw_inner = m.group(1)
        unescaped = html.unescape(raw_inner)
        if 'code:' not in unescaped and 'pronunciation:' not in unescaped:
            continue

        try:
            notes = parse_teacher_notes(unescaped)
            rendered = render_teacher_notes_html(notes)
            if not rendered:
                skipped.append((str(filepath), "Rendered empty HTML", raw_inner))
                continue
            replacements.append((m.start(), m.end(), rendered))
        except Exception as e:
            skipped.append((str(filepath), str(e), raw_inner))

    if not replacements:
        return False, skipped

    new_content = content
    for start, end, rep in sorted(replacements, key=lambda x: x[0], reverse=True):
        new_content = new_content[:start] + rep + new_content[end:]

    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return True, skipped

    return False, skipped


def process_md_file(filepath):
    content = filepath.read_text(encoding='utf-8', errors='ignore')
    matches = list(re.finditer(
        r"```text\n(.*?)\n```",
        content,
        re.DOTALL
    ))
    if not matches:
        return False, []

    skipped = []
    replacements = []

    for m in matches:
        inner = m.group(1)
        if 'code:' not in inner and 'pronunciation:' not in inner:
            continue

        try:
            notes = parse_teacher_notes(inner)
            rendered = render_teacher_notes_md(notes)
            if not rendered:
                skipped.append((str(filepath), "Rendered empty MD", inner))
                continue
            replacements.append((m.start(), m.end(), rendered))
        except Exception as e:
            skipped.append((str(filepath), str(e), inner))

    if not replacements:
        return False, skipped

    new_content = content
    for start, end, rep in sorted(replacements, key=lambda x: x[0], reverse=True):
        new_content = new_content[:start] + rep + new_content[end:]

    if new_content != content:
        filepath.write_text(new_content, encoding='utf-8')
        return True, skipped

    return False, skipped


def main():
    manuals_dir = Path("manuals")
    if not manuals_dir.exists():
        print("Error: manuals directory not found.")
        sys.exit(1)

    html_files = sorted(list(manuals_dir.glob("**/*.html")))
    md_files = sorted(list(manuals_dir.glob("**/*.md")))

    modified_html = 0
    modified_md = 0
    all_skipped = []

    for html_file in html_files:
        changed, skipped = process_html_file(html_file)
        if changed:
            modified_html += 1
        all_skipped.extend(skipped)

    for md_file in md_files:
        changed, skipped = process_md_file(md_file)
        if changed:
            modified_md += 1
        all_skipped.extend(skipped)

    print(f"Cleaned {modified_html} HTML files and {modified_md} MD files.")

    if all_skipped:
        print(f"\n⚠️  Skipped {len(all_skipped)} blocks that failed to parse or render:")
        for file_path, reason, raw_block in all_skipped:
            print(f"  - {file_path}: {reason}\n    Block snippet: {repr(raw_block[:100])}")
    else:
        print("All matching blocks successfully parsed and cleaned.")


if __name__ == "__main__":
    main()
