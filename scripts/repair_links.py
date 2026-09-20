#!/usr/bin/env python3
"""
scripts/repair_links.py - Helper script to analyze and repair pre-existing broken links in manuals/.

Rules applied in order:
2a. Wrong depth: target exists if one `../` is added or removed.
2b. Missing index: verify index landing pages.
2c. Suffix match: target matches exactly one file in the same language ending with the last two path segments.
2d. Untouched: recorded for docs/migration/LINKS_NEEDING_EDITOR.md.
"""

import json
import os
import re
import sys
import urllib.parse
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_broken_pairs():
    cmd = [sys.executable, os.path.join(REPO_ROOT, 'scripts', 'cosy_manuals_migrate.py'), 'verify', '--json-out', '/tmp/broken.json']
    subprocess.run(cmd, capture_output=True, cwd=REPO_ROOT)
    with open('/tmp/broken.json', encoding='utf-8') as f:
        return json.load(f)

def find_repo_files():
    repo_files = set()
    for root, _, files in os.walk(os.path.join(REPO_ROOT, 'manuals')):
        for file in files:
            rel = os.path.relpath(os.path.join(root, file), REPO_ROOT).replace(os.sep, '/')
            repo_files.add(rel)
    return repo_files

def repair_links():
    pairs = get_broken_pairs()
    repo_files = find_repo_files()

    iso_files = {}
    for f in repo_files:
        parts = f.split('/')
        if len(parts) > 1 and parts[0] == 'manuals':
            iso = parts[1]
            iso_files.setdefault(iso, []).append(f)

    rule_a_repairs = {} # src_file -> list of (old_target, new_target)
    rule_d_items = []   # list of (src_file, target)

    for src_file, target in pairs:
        u = urllib.parse.urlsplit(target)
        path = u.path
        qf = (('?' + u.query) if u.query else '') + (('#' + u.fragment) if u.fragment else '')
        src_dir = os.path.dirname(src_file)

        # Check 2a: Wrong depth
        add_path = '../' + path
        resolved_add = os.path.normpath(os.path.join(src_dir, add_path)).replace(os.sep, '/')
        exists_add = resolved_add in repo_files or os.path.exists(os.path.join(REPO_ROOT, resolved_add)) or os.path.exists(os.path.join(REPO_ROOT, resolved_add, 'index.html'))

        rem_path = path[3:] if path.startswith('../') else (path[2:] if path.startswith('./') else None)
        exists_rem = False
        if rem_path:
            resolved_rem = os.path.normpath(os.path.join(src_dir, rem_path)).replace(os.sep, '/')
            exists_rem = resolved_rem in repo_files or os.path.exists(os.path.join(REPO_ROOT, resolved_rem)) or os.path.exists(os.path.join(REPO_ROOT, resolved_rem, 'index.html'))

        if exists_add:
            rule_a_repairs.setdefault(src_file, []).append((target, add_path + qf))
            continue
        elif exists_rem:
            rule_a_repairs.setdefault(src_file, []).append((target, rem_path + qf))
            continue

        # Check 2b: Missing index
        norm_path = os.path.normpath(os.path.join(src_dir, path)).replace(os.sep, '/')
        parts = norm_path.split('/')
        is_missing_idx = False
        if (len(parts) == 3 and parts[0] == 'manuals' and parts[2] == 'index.html') or \
           (len(parts) == 4 and parts[0] == 'manuals' and parts[3] == 'index.html'):
            is_missing_idx = True

        if is_missing_idx:
            # Not found because missing or invalid
            pass

        # Check 2c: Suffix match
        segs = [s for s in path.split('/') if s and s != '.']
        iso = src_file.split('/')[1] if len(src_file.split('/')) > 1 else None
        lang_files = iso_files.get(iso, [])

        matched_c = []
        if len(segs) >= 2:
            suffix = '/' + '/'.join(segs[-2:])
            matched_c = [f for f in lang_files if f.endswith(suffix)]

        if len(matched_c) == 1:
            new_rel = os.path.relpath(matched_c[0], src_dir).replace(os.sep, '/')
            rule_a_repairs.setdefault(src_file, []).append((target, new_rel + qf))
            continue

        # Rule 2d: Untouched
        rule_d_items.append((src_file, target))

    # Apply Rule 2a repairs to files
    fixed_count = 0
    for src_file, replacements in rule_a_repairs.items():
        file_path = os.path.join(REPO_ROOT, src_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        for old_t, new_t in replacements:
            # Replace exactly attribute href="old_t" or src="old_t"
            pattern = re.compile(r'(\b(?:href|src)\s*=\s*)(["\'])' + re.escape(old_t) + r'\2')
            new_content = pattern.sub(r'\1\2' + new_t + r'\2', new_content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            fixed_count += len(replacements)

    print(f"Applied {fixed_count} link repairs across {len(rule_a_repairs)} files.")
    print(f"Remaining untouched links: {len(rule_d_items)}")

if __name__ == '__main__':
    repair_links()
