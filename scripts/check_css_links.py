#!/usr/bin/env python3
"""
CSS Link Checker for COSYmanuals
--------------------------------
Scans all .html files under manuals/ and marathons/, parses local <link rel="stylesheet" href="...">,
resolves the href relative to the HTML file's directory, and checks whether the target file exists.

Prints total files checked, count of offending files, total broken CSS links, and lists the first
20 offending files with details.

Exits with code 1 if any broken stylesheet links are found, or code 0 if all links are valid.
"""

import os
import sys
from html.parser import HTMLParser

class CSSLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.css_links = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'link':
            attr_dict = {k.lower(): v for k, v in attrs if k and v is not None}
            rel = attr_dict.get('rel', '').lower().split()
            if 'stylesheet' in rel:
                href = attr_dict.get('href')
                if href:
                    self.css_links.append(href)

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dirs_to_check = ['manuals', 'marathons']

    html_files = []
    for d in dirs_to_check:
        target_dir = os.path.join(repo_root, d)
        if os.path.exists(target_dir):
            for root, _, files in os.walk(target_dir):
                for f in files:
                    if f.endswith('.html'):
                        rel_path = os.path.relpath(os.path.join(root, f), repo_root)
                        html_files.append(rel_path)

    html_files.sort()

    offending_files = {}
    total_broken_links = 0
    total_files_checked = len(html_files)

    for filepath in html_files:
        full_filepath = os.path.join(repo_root, filepath)
        try:
            with open(full_filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            parser = CSSLinkParser()
            parser.feed(content)

            broken_in_file = []
            for href in parser.css_links:
                if href.startswith(('http://', 'https://', '//', 'data:')):
                    continue
                clean_href = href.split('?')[0].split('#')[0]
                target_path = os.path.normpath(os.path.join(os.path.dirname(full_filepath), clean_href))
                if not os.path.exists(target_path):
                    broken_in_file.append((href, os.path.relpath(target_path, repo_root)))

            if broken_in_file:
                offending_files[filepath] = broken_in_file
                total_broken_links += len(broken_in_file)
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)

    print(f"Checked {total_files_checked} HTML files in manuals/ and marathons/.")
    print(f"Offending files count: {len(offending_files)}")
    print(f"Total broken stylesheet links: {total_broken_links}")

    if offending_files:
        print("\nFirst 20 offending files:")
        for i, (f, links) in enumerate(list(offending_files.items())[:20]):
            print(f"{i+1}. {f}")
            for href, target in links:
                print(f"   -> href=\"{href}\" (resolved target: {target})")
        sys.exit(1)
    else:
        print("\nAll stylesheet links resolved successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
