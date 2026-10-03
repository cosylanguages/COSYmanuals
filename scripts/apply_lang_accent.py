#!/usr/bin/env python3
"""
apply_lang_accent.py
--------------------
Connects language manual pages and CSS files to the shared accent system for specified languages.

Usage:
    python3 scripts/apply_lang_accent.py --langs cv,ba

Actions:
  a) In manuals/<lang>/**/assets/style.css:
     Updates :root declarations for --teal-050, -100, -500, -600, -700, -800, -900 to
     var(--accent-050, #<old_hex>) ... var(--accent-900, #<old_hex>). Leaves all other variables untouched.
     If a file's :root does not match / contain --teal declarations, lists it in the summary.
  b) In manuals/<lang>/**/*.html:
     Adds data-lang-theme="<lang>" to <html> without modifying existing lang="..." attribute.
     Adds <link rel="stylesheet" href="..."> for shared/styles/lang-accents.css before the first stylesheet link.
"""

import argparse
import os
import re
import sys


TEAL_VARS = ['--teal-050', '--teal-100', '--teal-500', '--teal-600', '--teal-700', '--teal-800', '--teal-900']


def process_css_file(filepath):
    """Processes a style.css file to map --teal-* vars to var(--accent-*, old_hex)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file has --teal- definitions
    has_teal = any(var in content for var in TEAL_VARS)
    if not has_teal:
        return False, False, "No --teal-* declarations in file"

    updated = False
    new_content = content

    for var in TEAL_VARS:
        accent_token = var.replace('--teal-', '--accent-')
        # Regex to match line: `--teal-600:#0f766e;` or `--teal-600: #0f766e;`
        # and replace value with `var(--accent-600, #0f766e);`
        pattern = re.compile(rf'({re.escape(var)}\s*:\s*)(?!var\(--accent-)(#[0-9a-fA-F]{{3,6}})(\s*;)')
        def repl(m):
            nonlocal updated
            updated = True
            prefix = m.group(1)
            hex_val = m.group(2)
            suffix = m.group(3)
            return f"{prefix}var({accent_token}, {hex_val}){suffix}"

        new_content = pattern.sub(repl, new_content)

    if updated and new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True, True, "Updated --teal-* variables to var(--accent-*, fallback_hex)"

    if has_teal and not updated:
        return True, False, "Already up to date"

    return False, False, "Skipped"


def process_html_file(filepath, lang, repo_root):
    """Processes an HTML file to add data-lang-theme attribute and lang-accents.css link."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    updated = False
    new_content = content

    # 1. Add data-lang-theme="<lang>" to <html> tag if not present
    if 'data-lang-theme=' not in new_content:
        # Match <html ...> and add data-lang-theme="<lang>"
        html_tag_pattern = re.compile(r'(<html\b[^>]*)(>)', re.IGNORECASE)
        m_html = html_tag_pattern.search(new_content)
        if m_html:
            start_tag = m_html.group(1)
            end_bracket = m_html.group(2)
            new_tag = f'{start_tag} data-lang-theme="{lang}"{end_bracket}'
            new_content = html_tag_pattern.sub(new_tag, new_content, count=1)
            updated = True

    # 2. Add <link rel="stylesheet" href="..."> for lang-accents.css if not present
    if 'lang-accents.css' not in new_content:
        rel_accents = os.path.relpath(
            os.path.join(repo_root, 'shared', 'styles', 'lang-accents.css'),
            os.path.dirname(filepath)
        ).replace('\\', '/')

        link_tag = f'<link rel="stylesheet" href="{rel_accents}">'

        # Insert before first <link rel="stylesheet" ...>
        first_link_m = re.search(r'(<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>)', new_content, re.IGNORECASE)
        if first_link_m:
            pos = first_link_m.start()
            new_content = new_content[:pos] + link_tag + '\n' + new_content[pos:]
            updated = True
        else:
            # Fallback: insert before </head>
            head_close_m = re.search(r'</head>', new_content, re.IGNORECASE)
            if head_close_m:
                pos = head_close_m.start()
                new_content = new_content[:pos] + link_tag + '\n' + new_content[pos:]
                updated = True

    if updated and new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True

    return False


def process_language(lang, repo_root):
    """Processes all CSS and HTML files under manuals/<lang>/."""
    lang_dir = os.path.join(repo_root, 'manuals', lang)
    if not os.path.exists(lang_dir):
        print(f"Directory manuals/{lang}/ does not exist! Skipping.")
        return

    print(f"==================================================")
    print(f"Processing Language: {lang.upper()} (manuals/{lang}/)")
    print(f"==================================================")

    css_files = []
    html_files = []

    for root, _, files in os.walk(lang_dir):
        for f in files:
            p = os.path.join(root, f)
            if f == 'style.css':
                css_files.append(p)
            elif f.endswith('.html'):
                html_files.append(p)

    css_updated = 0
    css_no_teal = []

    for css_path in sorted(css_files):
        rel_path = os.path.relpath(css_path, repo_root).replace('\\', '/')
        has_teal, modified, msg = process_css_file(css_path)
        if modified:
            css_updated += 1
            print(f"  [CSS Updated] {rel_path}")
        elif not has_teal:
            css_no_teal.append(rel_path)

    if css_no_teal:
        print(f"  [CSS Summary Note] {len(css_no_teal)} CSS file(s) did not contain --teal-* declarations:")
        for p in css_no_teal:
            print(f"    - {p}")

    html_updated = 0
    for html_path in sorted(html_files):
        rel_path = os.path.relpath(html_path, repo_root).replace('\\', '/')
        if process_html_file(html_path, lang, repo_root):
            html_updated += 1

    print(f"  Summary for '{lang}':")
    print(f"    - Total CSS files checked : {len(css_files)}")
    print(f"    - CSS files updated       : {css_updated}")
    print(f"    - Total HTML files checked: {len(html_files)}")
    print(f"    - HTML files updated      : {html_updated}\n")


def main():
    parser = argparse.ArgumentParser(description="Connect pages and CSS to shared accent system.")
    parser.add_argument('--langs', required=True, help="Comma-separated language ISO codes (e.g., cv,ba)")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    langs = [l.strip().lower() for l in args.langs.split(',') if l.strip()]

    for lang in langs:
        process_language(lang, repo_root)


if __name__ == '__main__':
    main()
