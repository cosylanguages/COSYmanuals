"""Repair gateway and language-switcher links that were never resolved by the depth rules.

Covers three families the main repair pass leaves alone:
 * gateways named after the language ('manuals/english-a0-a1.html', 'manuals/de/deutsch-a2.html');
 * language switchers that repeat the language segment ('de/grammar/a1/en/en.html');
 * morphology links to pages that live in topics/.

Site sections that live in other repositories (practice, comparative, hybrid, rosetta-wall) are left untouched.

    python3 scripts/repair_links_gateways.py [--check]
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GATEWAY = {
    'manuals/english-a0-a1.html': 'manuals/en/index-a0-a1.html',
    'manuals/francaise-a0-a1.html': 'manuals/fr/index-a0-a1.html',
    'manuals/italiano-a0-a1.html': 'manuals/it/index-a0-a1.html',
    'manuals/russkiy-a0-a1.html': 'manuals/ru/index-a0-a1.html',
    'manuals/russkiy-a2.html': 'manuals/ru/index-a2.html',
    'manuals/de/deutsch-a2.html': 'manuals/de/index-a2.html',
    'manuals/el/ellinika-a2.html': 'manuals/el/index-a2.html',
    'manuals/en/vocabulary/english-b1.html': 'manuals/en/vocabulary/b1/index.html',
    'manuals/en/vocabulary/english-b2.html': 'manuals/en/vocabulary/b2/index.html',
    'manuals/en/vocabulary/english-a1.html': 'manuals/en/vocabulary/a1/index.html',
    'manuals/en/vocabulary/english-a2.html': 'manuals/en/vocabulary/a2/index.html',
    'manuals/en/vocabulary/english-c1.html': 'manuals/en/vocabulary/c1/index.html',
    'manuals/en/vocabulary/english-c2.html': 'manuals/en/vocabulary/c2/index.html',
    'manuals/manuals/index.html': 'manuals/index.html',
    'manuals/manuals/english-a0-a1.html': 'manuals/en/index-a0-a1.html',
    'manuals/manuals/francaise-a0-a1.html': 'manuals/fr/index-a0-a1.html',
    'manuals/manuals/italiano-a0-a1.html': 'manuals/it/index-a0-a1.html',
}


def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def repair(target):
    if target in GATEWAY and exists(GATEWAY[target]):
        return GATEWAY[target]
    parts = target.split('/')
    # language switcher: manuals/<lang>/grammar/<lvl>/<x>/<x>.html -> manuals/<x>/index.html
    if len(parts) >= 6 and parts[0] == 'manuals' and parts[2] == 'grammar':
        x = parts[-1][:-5]
        if x == parts[-2] and exists(f'manuals/{x}/index.html'):
            return f'manuals/{x}/index.html'
    # level switcher inside a shelf: manuals/<lang>/grammar/<lvl>/<lang>.html
    if len(parts) == 5 and parts[0] == 'manuals' and parts[2] == 'grammar':
        x = parts[-1][:-5]
        if x == parts[1] and exists(f'manuals/{x}/index.html'):
            return f'manuals/{x}/index.html'
    # morphology page that lives next to the others
    if '/morphology/' in target:
        alt = target.replace('/morphology/', '/')
        if exists(alt):
            return alt
    # language hub referenced as languages/<code>.html
    if '/languages/' in target:
        code = parts[-1][:-5]
        if exists(f'manuals/{code}/index.html'):
            return f'manuals/{code}/index.html'
        return 'manuals/index.html'
    return None


def main():
    check = '--check' in sys.argv
    fixed = left = 0
    for path in glob.glob(os.path.join(ROOT, 'manuals/**/*.html'), recursive=True):
        rel_dir = os.path.dirname(os.path.relpath(path, ROOT))
        html = open(path, encoding='utf-8').read()
        out = html
        for href in set(re.findall(r'href="([^"#:]+\.html)"', html)):
            if href.startswith(('http', 'mailto')):
                continue
            target = os.path.normpath(os.path.join(rel_dir, href))
            if exists(target):
                continue
            new = repair(target)
            if not new:
                left += 1
                continue
            new_rel = os.path.relpath(os.path.join(ROOT, new), os.path.join(ROOT, rel_dir))
            out = out.replace(f'href="{href}"', f'href="{new_rel}"')
            fixed += 1
        if out != html and not check:
            open(path, 'w', encoding='utf-8').write(out)
    print(f'{"would fix" if check else "fixed"} {fixed} links, {left} untouchable')
    if check:
        return
    for path in glob.glob(os.path.join(ROOT, 'manuals/**/*.html'), recursive=True):
        rel_dir = os.path.dirname(os.path.relpath(path, ROOT))
        for href in set(re.findall(r'href="([^"#:]+\.html)"', open(path, encoding='utf-8').read())):
            if href.startswith(('http', 'mailto')):
                continue
            if not exists(os.path.normpath(os.path.join(rel_dir, href))):
                print('  still broken:', os.path.relpath(path, ROOT), '->', href)


if __name__ == '__main__':
    main()
