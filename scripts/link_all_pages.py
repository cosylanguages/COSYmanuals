"""Append every unlinked topic page of a grammar level to that level's index.

The shelves grew faster than their hubs: French A1 has 202 pages and its index reaches 62 of them, English A1
reaches 20 of 81, Russian A1 63 of 115. This appends the missing pages to the level index in one alphabetical
list, so no page is reachable only by URL.

    python3 scripts/link_all_pages.py [--check]
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADINGS = {
    'fr': 'Toutes les pages de ce niveau',
    'en': 'All pages at this level',
    'ru': 'Все страницы этого уровня',
    'el': 'Όλες οι σελίδες αυτού του επιπέδου',
    'it': 'Tutte le pagine di questo livello',
}


def title_of(path):
    html = open(path, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if not m:
        return os.path.basename(path)[:-5]
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.group(1))).strip()


def level_dirs():
    for lang_dir in sorted(glob.glob(os.path.join(ROOT, 'manuals/*/grammar/*'))):
        lang = lang_dir.split('/')[-3]
        if glob.glob(os.path.join(lang_dir, 'topics/*.html')):
            yield lang, lang_dir


def main():
    check = '--check' in sys.argv
    touched = []
    for lang, lvl_dir in level_dirs():
        index = os.path.join(lvl_dir, 'index.html')
        if not os.path.exists(index):
            continue
        html = open(index, encoding='utf-8').read()
        linked = set(re.findall(r'topics/([A-Za-z0-9_-]+)\.html', html))
        missing = []
        for path in glob.glob(os.path.join(lvl_dir, 'topics/*.html')):
            slug = os.path.basename(path)[:-5]
            if slug not in linked:
                missing.append((title_of(path), slug))
        if not missing:
            continue
        if check:
            print(f'{lang} {os.path.basename(lvl_dir)}: {len(missing)} pages unreachable')
            touched.append((lang, lvl_dir, len(missing)))
            continue
        missing.sort(key=lambda t: t[0].casefold())
        items = ''.join(f'      <li><a href="topics/{s}.html">{t}</a></li>\n' for t, s in missing)
        block = (f'  <section class="all-pages">\n'
                 f'    <h2>{HEADINGS.get(lang, "All pages")}</h2>\n'
                 f'    <ul class="all-pages-list">\n{items}    </ul>\n'
                 f'  </section>\n')
        if '</main>' in html:
            html = html.replace('</main>', block + '</main>', 1)
        else:
            html = html.replace('</body>', block + '</body>', 1)
        open(index, 'w', encoding='utf-8').write(html)
        touched.append((lang, lvl_dir, len(missing)))
    for lang, lvl_dir, n in touched:
        print(f'{lang} {os.path.basename(lvl_dir)}: {n} pages added to the index')


if __name__ == '__main__':
    main()
