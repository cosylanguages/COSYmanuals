#!/usr/bin/env python3
"""
manual_to_record.py

Converts static HTML/MD manual topic pages into structured protected records
(suitable for Supabase `lessons` table insertion with kind='manual') and converts
the original static HTML file into a lightweight public stub.

Usage:
  python3 scripts/manual_to_record.py <filepath> [--out-dir drafts]
  python3 scripts/manual_to_record.py --batch <directory> [--out-json drafts/records.json]
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser

class TopicHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.subtitle = ""
        self.description = ""
        self.eyebrow = ""
        self.in_title = False
        self.in_h1 = False
        self.in_subtitle = False
        self.in_eyebrow = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_dict.get("name") == "description":
            self.description = attrs_dict.get("content", "")
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "p" and attrs_dict.get("class") == "subtitle":
            self.in_subtitle = True
        elif tag == "span" and attrs_dict.get("class") == "eyebrow":
            self.in_eyebrow = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "p":
            self.in_subtitle = False
        elif tag == "span":
            self.in_eyebrow = False

    def handle_data(self, data):
        if self.in_h1 and not self.title:
            self.title += data.strip()
        elif self.in_title and not self.title:
            raw_title = data.split("·")[0].strip()
            if raw_title:
                self.title = raw_title
        elif self.in_subtitle:
            self.subtitle += data.strip()
        elif self.in_eyebrow:
            self.eyebrow += data.strip()


def parse_topic_path(filepath):
    norm_path = os.path.normpath(filepath).replace("\\", "/")
    parts = norm_path.split("/")

    lang = "en"
    cefr = "a1"
    course = "grammar"
    slug = os.path.splitext(os.path.basename(filepath))[0]

    if "manuals" in parts:
        idx = parts.index("manuals")
        if len(parts) > idx + 1:
            lang = parts[idx + 1]
        if len(parts) > idx + 2:
            course = parts[idx + 2]
        if len(parts) > idx + 3:
            cefr = parts[idx + 3]

    return lang, cefr, course, slug


def extract_record_and_stub(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lang, cefr, course, slug = parse_topic_path(filepath)

    parser = TopicHTMLParser()
    parser.feed(content)

    title = parser.title or slug.replace("-", " ").title()
    summary = parser.subtitle or parser.description or f"Protected manual topic: {title}"

    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL | re.IGNORECASE)
    if main_match:
        body = main_match.group(1).strip()
    else:
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        body = body_match.group(1).strip() if body_match else content

    canonical_id = f"{lang}:{cefr}:manual:{slug}"

    record = {
        "id": canonical_id,
        "language": lang,
        "cefr": cefr,
        "kind": "manual",
        "slug": slug,
        "title": title,
        "summary": summary,
        "body": body,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    norm_path = os.path.normpath(filepath).replace("\\", "/")
    depth = len(norm_path.split("/")) - 1
    rel_root = "../" * depth if depth > 0 else "./"

    stub_html = f"""<!DOCTYPE html>
<html lang="{lang}" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Protected Manual Shell · COSYmanuals</title>
<meta name="description" content="{summary}">
<link rel="stylesheet" href="{rel_root}shared/styles/lang-accents.css">
<link rel="stylesheet" href="{rel_root}shared/styles/tokens.css">
<link rel="stylesheet" href="{rel_root}shared/styles/base.css">
<link rel="stylesheet" href="{rel_root}shared/styles/components.css">
<link rel="stylesheet" href="{rel_root}shared/styles/layout.css">
</head>
<body>
<nav id="cosy-nav" aria-label="Navigation principale"></nav>

<main class="container">
<div class="page-head" style="margin-top: 2rem;">
 <span class="eyebrow">{lang.upper()} {cefr.upper()} Manual</span>
 <h1>{title}</h1>
 <p class="subtitle">{summary}</p>
 <hr class="rule">
</div>

<div class="box gated-content-notice" style="background: var(--surface-2, #f8f9fa); border: 2px dashed var(--border-color, #ccc); padding: 2rem; border-radius: 8px; text-align: center; margin: 2rem 0;">
  <div style="font-size: 2.5rem; margin-bottom: 1rem;">🔒</div>
  <h2 style="margin-bottom: 0.5rem; font-size: 1.5rem;">Protected Ecosystem Content</h2>
  <p style="max-width: 600px; margin: 0 auto 1.5rem auto; color: var(--text-muted, #666);">
    Full lesson text, rule guides, answer keys, and teacher materials for <strong>{title}</strong> are protected and hosted in Supabase database tables with Row Level Security.
  </p>
  <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
    <a href="https://cosylanguages.github.io/COSYlanguages/login.html?redirect={canonical_id}" class="btn-primary" style="background: var(--cosy-manuals-accent, #6b202b); color: #fff; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: bold;">Log In to Access Content</a>
    <a href="{rel_root}manuals/{lang}/{course}/{cefr}/index.html" class="btn-secondary" style="border: 1px solid var(--border-color, #ccc); color: var(--text-color, #333); padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none;">Return to {cefr.upper()} Index</a>
  </div>
</div>
</main>

<footer class="cosy-ecosystem-footer-note" style="text-align: center; padding: 2rem 0; color: var(--text-muted, #888); font-size: 0.875rem;">
  Part of the COSY Family · Upstream Curriculum Owner: COSYplatform
</footer>
</body>
</html>
"""
    return record, stub_html


def process_single(filepath, out_dir="drafts", write_stub=True):
    record, stub_html = extract_record_and_stub(filepath)
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, f"{record['id'].replace(':', '_')}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    if write_stub:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(stub_html)

    return record, json_path


def process_batch(directory, out_json_path="drafts/records.json", write_stubs=True):
    records = []
    out_dir = os.path.dirname(out_json_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".html") and file != "index.html" and not file.startswith("domaine"):
                filepath = os.path.join(root, file)
                record, stub_html = extract_record_and_stub(filepath)
                records.append(record)
                if write_stubs:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(stub_html)

    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Processed {len(records)} topic files from {directory}. Exported to {out_json_path}.")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert manual topic pages to protected records & public stubs.")
    parser.add_argument("path", nargs="?", help="Path to single HTML topic file or directory if --batch")
    parser.add_argument("--batch", action="store_true", help="Process all HTML files in directory recursively")
    parser.add_argument("--out-dir", default="drafts", help="Output directory for individual JSON records")
    parser.add_argument("--out-json", default="drafts/records.json", help="Output JSON file path for batch export")
    parser.add_argument("--no-stub", action="store_true", help="Do not overwrite original HTML file with stub")

    args = parser.parse_args()

    if args.batch:
        if not args.path:
            print("Error: Directory path required when using --batch")
            sys.exit(1)
        process_batch(args.path, out_json_path=args.out_json, write_stubs=not args.no_stub)
    else:
        if not args.path:
            print("Error: Filepath required.")
            sys.exit(1)
        rec, jpath = process_single(args.path, out_dir=args.out_dir, write_stub=not args.no_stub)
        print(f"Created record '{rec['id']}' -> {jpath}")
