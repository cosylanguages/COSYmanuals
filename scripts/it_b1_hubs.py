"""Add the new Italian B1 topics to the part hubs and create part 4.

Each entry is inserted once; running the script twice changes nothing.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'manuals/it/grammar/b1')

NEW = {
    'part-1.html': [
        ('congiuntivo-passato', 'Il Congiuntivo Passato'),
        ('futuro-anteriore', 'Il Futuro Anteriore'),
        ('condizionale-passato', 'Il Condizionale Passato'),
    ],
    'part-2.html': [
        ('si-impersonale-e-passivante', 'Il Si Impersonale e Passivante'),
    ],
    'part-3.html': [
        ('pronomi-combinati', 'I Pronomi Combinati'),
        ('verbi-pronominali', 'I Verbi Pronominali'),
    ],
}

PART4 = [('comparativi-e-superlativi-irregolari', 'Comparativi e Superlativi Irregolari'),
         ('avverbi-in-mente', 'Gli Avverbi in -mente'),
         ('aggettivi-e-pronomi-indefiniti', 'Aggettivi e Pronomi Indefiniti')]


def add_items(path, items):
    page = open(path, encoding='utf-8').read()
    rows = ''.join(f'    <li><a href="topics/{slug}.html">{title}</a></li>\n'
                   for slug, title in items if f'topics/{slug}.html' not in page)
    if not rows:
        return False
    page = page.replace('</ul>', rows + '  </ul>', 1)
    open(path, 'w', encoding='utf-8').write(page)
    return True


def build_part4():
    tpl = open(os.path.join(BASE, 'part-3.html'), encoding='utf-8').read()
    rows = ''.join(f'    <li><a href="topics/{slug}.html">{title}</a></li>\n' for slug, title in PART4)
    page = re.sub(r'<title>.*?</title>', '<title>Parte 4: Comparazione, Avverbi e Indefiniti · Grammatica Italiana B1</title>', tpl, count=1, flags=re.S)
    page = re.sub(r'<h1>.*?</h1>', '<h1>Parte 4 · Comparazione, Avverbi e Indefiniti</h1>', page, count=1, flags=re.S)
    page = re.sub(r'<p class="subtitle">.*?</p>',
                  '<p class="subtitle">Forme irregolari di comparazione, avverbi di modo e quantità indefinite</p>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<ul>.*?</ul>', f'<ul>\n{rows}  </ul>', page, count=1, flags=re.S)
    open(os.path.join(BASE, 'part-4.html'), 'w', encoding='utf-8').write(page)


def add_nav():
    link = '      <a class="sd-jump-link" href="../part-4.html">Parte 4</a>\n'
    targets = glob.glob(os.path.join(BASE, 'topics/*.html')) + glob.glob(os.path.join(BASE, 'part-*.html')) + [os.path.join(BASE, 'index.html')]
    for path in targets:
        page = open(path, encoding='utf-8').read()
        if 'part-4.html' in page:
            continue
        if '../part-3.html' in page:
            page = page.replace('      <a class="sd-jump-link" href="../part-3.html">Parte 3</a>\n',
                                '      <a class="sd-jump-link" href="../part-3.html">Parte 3</a>\n' + link, 1)
        elif 'href="part-3.html"' in page:
            page = page.replace('      <a class="sd-jump-link" href="part-3.html">Parte 3</a>\n',
                                '      <a class="sd-jump-link" href="part-3.html">Parte 3</a>\n'
                                '      <a class="sd-jump-link" href="part-4.html">Parte 4</a>\n', 1)
        else:
            continue
        open(path, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    for name, items in NEW.items():
        print(name, 'updated' if add_items(os.path.join(BASE, name), items) else 'already complete')
    build_part4()
    add_nav()
    print('part-4 built, nav links added')
