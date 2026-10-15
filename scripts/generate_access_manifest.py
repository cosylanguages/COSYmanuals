#!/usr/bin/env python3
"""
generate_access_manifest.py

Produces MANUALS_ACCESS_MANIFEST.json classifying every PDF under manuals/*/print/
and every manual HTML file over 15KB (15360 bytes) as 'free-intended', 'paid-intended',
or 'needs founder decision'.

Follows shared taxonomy: language (ISO 639-1) -> level (CEFR) -> topic -> unit.
"""

import os
import glob
import json

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUALS_DIR = os.path.join(REPO_ROOT, "manuals")
OUTPUT_PATH = os.path.join(REPO_ROOT, "MANUALS_ACCESS_MANIFEST.json")

def parse_entry(path_rel, size_bytes, is_pdf=False):
    parts = path_rel.split("/")

    if path_rel == "manuals/founder-portal.html":
        return {
            "path": path_rel,
            "file_type": "html",
            "size_bytes": size_bytes,
            "language": "all",
            "level": None,
            "topic": "founder-portal",
            "unit": None,
            "classification": "needs founder decision",
            "reason": "Administrative founder portal page restricted to founder role"
        }

    lang = parts[1]

    if is_pdf:
        return {
            "path": path_rel,
            "file_type": "pdf",
            "size_bytes": size_bytes,
            "language": lang,
            "level": "A0-A1",
            "topic": "print_grammar_manual",
            "unit": None,
            "classification": "free-intended",
            "reason": "A0-A1 printable reference booklet for foundational starter level"
        }

    # HTML files
    subject_or_track = parts[2]

    level = None
    topic = None
    unit = None

    for i in range(3, len(parts)):
        pt_u = parts[i].upper()
        if pt_u in ["A0", "A1", "A2", "B1", "B2", "C1", "C2", "A0-A1"]:
            level = pt_u
            if i + 1 < len(parts):
                if parts[i+1] == "topics" and i + 2 < len(parts):
                    topic = parts[i+2].replace(".html", "")
                else:
                    topic = parts[i+1].replace(".html", "")
            break

    if not level and subject_or_track in ["a1", "a2", "b1", "b2", "c1", "c2"]:
        level = subject_or_track.upper()
        subject_or_track = parts[2]

    if not topic:
        filename = parts[-1].replace(".html", "")
        if filename not in ["grammar", "vocabulary", "communication", "index"]:
            topic = filename
        else:
            topic = subject_or_track

    # Classification logic:
    # 1. A0/A1 starter level course materials -> free-intended
    # 2. Specialized tracks (professional, exam, relocation) -> paid-intended
    # 3. Intermediate and Advanced levels (A2, B1, B2, C1, C2) -> paid-intended
    if level in ["A0", "A1", "A0-A1"]:
        classification = "free-intended"
        reason = "A0/A1 starter level course material provided freely as introductory/foundation tier"
    elif subject_or_track in ["professional", "exam", "relocation"]:
        classification = "paid-intended"
        reason = f"Specialized commercial track ({subject_or_track}) reserved for contracted/paid students"
    elif level in ["B1", "B2", "C1", "C2"]:
        classification = "paid-intended"
        reason = f"Intermediate/Advanced level ({level}) content designated for contracted/paid students"
    elif level == "A2":
        classification = "paid-intended"
        reason = "A2 elementary level content beyond free A0/A1 starter tier"
    else:
        classification = "needs founder decision"
        reason = "Unclear level or track structure needing founder determination"

    return {
        "path": path_rel,
        "file_type": "html",
        "size_bytes": size_bytes,
        "language": lang,
        "level": level,
        "topic": topic,
        "unit": unit,
        "classification": classification,
        "reason": reason
    }

def main():
    # 1. PDFs under manuals/*/print/
    pdf_glob_1 = glob.glob(os.path.join(MANUALS_DIR, "*/print/*.pdf"))
    pdf_glob_2 = glob.glob(os.path.join(MANUALS_DIR, "*/print/**/*.pdf"), recursive=True)
    pdf_files = sorted(list(set(pdf_glob_1 + pdf_glob_2)))

    # 2. HTMLs over 15KB (15360 bytes)
    html_files = []
    for root, dirs, files in os.walk(MANUALS_DIR):
        for f in files:
            if f.endswith(".html"):
                full_path = os.path.join(root, f)
                size = os.path.getsize(full_path)
                if size > 15360: # strictly over 15KB
                    rel_path = os.path.relpath(full_path, REPO_ROOT)
                    html_files.append((rel_path, size))

    html_files.sort(key=lambda x: x[0])

    manifest_entries = []
    for pdf_path in pdf_files:
        rel_path = os.path.relpath(pdf_path, REPO_ROOT)
        size = os.path.getsize(pdf_path)
        manifest_entries.append(parse_entry(rel_path, size, is_pdf=True))

    for html_rel, size in html_files:
        manifest_entries.append(parse_entry(html_rel, size, is_pdf=False))

    manifest_entries.sort(key=lambda x: x["path"])

    output_data = {
        "manifest_version": "1.0.0",
        "total_entries": len(manifest_entries),
        "summary": {
            "pdf_count": len(pdf_files),
            "html_over_15kb_count": len(html_files),
            "free_intended": sum(1 for e in manifest_entries if e["classification"] == "free-intended"),
            "paid_intended": sum(1 for e in manifest_entries if e["classification"] == "paid-intended"),
            "needs_founder_decision": sum(1 for e in manifest_entries if e["classification"] == "needs founder decision")
        },
        "entries": manifest_entries
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {OUTPUT_PATH} with {len(manifest_entries)} classified entries.")

if __name__ == "__main__":
    main()
