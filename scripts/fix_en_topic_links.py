"""Repoint the hand-built English A1 pages at targets that exist.

The early A1 pages were copied from the old static site, so their language tabs point at
`../fr/fr.html` and their morphology and syntax links at `morphology/en-be.html`, neither of which
exists inside a level folder. Each broken link is rewritten to the page that does exist, and links
that already resolve are left alone.

    python3 scripts/fix_en_topic_links.py [--write]
"""
import argparse
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ('en', 'fr', 'it', 'ru', 'el', 'es', 'de', 'pt')


def resolve(page_dir, href):
    return os.path.exists(os.path.normpath(os.path.join(page_dir, href)))


def repair(page, page_dir):
    def fix(m):
        href = m.group(1)
        if href.startswith(('http', 'mailto', '#', '../../../../')) or resolve(page_dir, href):
            return m.group(0)
        lang_tab = re.fullmatch(r'\.\./(%s)/\1\.html' % '|'.join(LANGS), href)
        if lang_tab:
            new = f'../../../{lang_tab.group(1)}/index.html'
            return f'href="{new}"' if resolve(page_dir, new) else m.group(0)
        old_site = re.fullmatch(r'\.\./\.\./manuals/english-a0-a1\.html', href)
        if old_site:
            return 'href="../../../index-a0-a1.html"'
        flat = re.fullmatch(r'(morphology|syntax)/([\w-]+\.html)', href)
        if flat and resolve(page_dir, flat.group(2)):
            return f'href="{flat.group(2)}"'
        return m.group(0)

    return re.sub(r'href="([^"#]+\.html)"', fix, page)


def main(write=False):
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'manuals/en/grammar/*/topics/*.html'))):
        page = open(path, encoding='utf-8').read()
        new = repair(page, os.path.dirname(path))
        if new != page:
            changed += 1
            if write:
                open(path, 'w', encoding='utf-8').write(new)
    print(f'pages changed: {changed}')
    if not write:
        print('dry run, pass --write')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    main(ap.parse_args().write)
