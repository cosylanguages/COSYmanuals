#!/usr/bin/env python3
"""
Fix Existing CSS Links Script for COSYmanuals
--------------------------------------------
Rewrites only the href of local stylesheet links pointing to shared/styles/ or shared/css/
to the correct relative path computed with os.path.relpath from the HTML file's directory
to repo-root/shared/styles/ (or repo-root/shared/css/).

Leaves every other byte of the file unchanged.
"""

import os
import re

def fix_css_links():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dirs_to_fix = ['manuals', 'marathons']

    html_files = []
    for d in dirs_to_fix:
        target_dir = os.path.join(repo_root, d)
        if os.path.exists(target_dir):
            for root, _, files in os.walk(target_dir):
                for f in files:
                    if f.endswith('.html'):
                        html_files.append(os.path.join(root, f))

    html_files.sort()

    total_files_modified = 0
    total_links_rewritten = 0

    pattern = re.compile(
        r'(<link\s+[^>]*?href=["\'])([^"\']*?shared/(styles|css)/[^"\']+)(["\'][^>]*?>)',
        re.IGNORECASE
    )

    for filepath in html_files:
        file_dir = os.path.dirname(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        file_links_rewritten = 0

        def replace_href(match):
            nonlocal file_links_rewritten
            prefix = match.group(1)
            old_href = match.group(2)
            subfolder = match.group(3)

            css_filename = old_href.split(f'shared/{subfolder}/')[-1]

            target_shared_dir = os.path.join(repo_root, 'shared', subfolder)
            target_css_path = os.path.join(target_shared_dir, css_filename)

            new_rel_dir = os.path.relpath(target_shared_dir, file_dir).replace('\\', '/')
            new_href = f"{new_rel_dir}/{css_filename}"

            if old_href != new_href:
                file_links_rewritten += 1
                return f"{prefix}{new_href}{suffix if (suffix := match.group(4)) else ''}"
            return match.group(0)

        new_content = pattern.sub(replace_href, content)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            total_files_modified += 1
            total_links_rewritten += file_links_rewritten

    print(f"Done fixing CSS links.")
    print(f"Files modified: {total_files_modified}")
    print(f"Links rewritten: {total_links_rewritten}")

if __name__ == '__main__':
    fix_css_links()
