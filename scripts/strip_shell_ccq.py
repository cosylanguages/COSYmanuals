"""Remove the shell's leftover quiz from English topic pages and set the level in the eyebrow.

Pages built before en_topic_build dropped the shell head kept the sample page's own quiz, the one
headed "Mandative & Formulaic Subjunctive", between the header and <main>. That block is boilerplate
about a different grammar point, so it goes. The eyebrow is corrected at the same time, since builds
made before the level was parameterised say B2 on every shelf.

    python3 scripts/strip_shell_ccq.py [--write]
"""
import argparse
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STALE = 'Mandative & Formulaic Subjunctive'


def repair(page, level):
    if '</header>' in page and '<main ' in page:
        start = page.index('</header>') + len('</header>')
        end = page.index('<main ')
        if STALE in page[start:end]:
            page = page[:start] + '\n' + page[end:]
    page = re.sub(r'<span class="eyebrow">Level [A-C][12] Grammar</span>',
                  f'<span class="eyebrow">Level {level.upper()} Grammar</span>', page)
    page = re.sub(r'(<main[^>]*data-level=")[^"]*(")', rf'\g<1>{level.upper()}\g<2>', page, count=1)
    return page


def main(write=False):
    changed = 0
    stale = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'manuals/en/grammar/*/topics/*.html'))):
        level = path.split(os.sep)[-3]
        page = open(path, encoding='utf-8').read()
        new = repair(page, level)
        if new != page:
            changed += 1
            if STALE in page:
                stale += 1
            if write:
                open(path, 'w', encoding='utf-8').write(new)
    print(f'pages changed: {changed} ({stale} carried the stale quiz)')
    if not write:
        print('dry run, pass --write')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    main(ap.parse_args().write)
