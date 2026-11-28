"""Resolve the last internal links: repeated path runs, language-named gateways, mixed-script slugs."""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ascii_slug(name):
    return re.sub(r'[^A-Za-z0-9._-]', '', name)


def repo_files():
    out = []
    for root, _, files in os.walk(os.path.join(ROOT, 'manuals')):
        for f in files:
            if f.endswith('.html'):
                out.append(os.path.relpath(os.path.join(root, f), ROOT).replace(os.sep, '/'))
    return out


FILES = repo_files()


def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def repair(target):
    cur = target
    for _ in range(3):
        collapsed = re.sub(r'((?:[^/]+/)+?)\1', r'\1', cur)
        if collapsed == cur:
            break
        cur = collapsed
        if exists(cur):
            return cur
    base = cur.split('/')[-1]
    key = ascii_slug(base).lower()
    hits = [f for f in FILES if ascii_slug(os.path.basename(f)).lower() == key]
    if len(hits) == 1:
        return hits[0]
    if 'gateway' in base or base in ('english-a0-a1.html',):
        return None
    return None


def main():
    fixed = 0
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
            if not new or not exists(new):
                continue
            new_rel = os.path.relpath(os.path.join(ROOT, new), os.path.join(ROOT, rel_dir))
            out = out.replace(f'href="{href}"', f'href="{new_rel}"')
            fixed += 1
        if out != html:
            open(path, 'w', encoding='utf-8').write(out)
    print('fixed', fixed)


if __name__ == '__main__':
    main()
