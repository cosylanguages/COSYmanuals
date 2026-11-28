"""Add the new Greek A2 topics to the part hubs and create part 4."""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'manuals/el/grammar/a2')

NEW = {
    'part-1.html': [('paratatikos-eimai-echo', 'Παρατατικός του «είμαι» και του «έχω»')],
    'part-2.html': [('klitika-kai-prostaktiki', 'Αδύνατοι Τύποι με Προστακτική')],
    'part-3.html': [('anaforikes-protaseis-pou', 'Αναφορικές Προτάσεις με «που»'),
                    ('plagiakos-logos', 'Ο Πλάγιος Λόγος')],
}

PART4 = [('klitika-antikeimena', 'Οι Αδύνατοι Τύποι Αντικειμένου'),
         ('epirrimata-apo-epitheta', 'Επιρρήματα από Επίθετα')]


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
    page = re.sub(r'<title>.*?</title>', '<title>Μέρος 4: Αντωνυμίες και Επιρρήματα · Ελληνικά Α2</title>', tpl, count=1, flags=re.S)
    page = re.sub(r'<h1>.*?</h1>', '<h1>Μέρος 4 · Αντωνυμίες και Επιρρήματα</h1>', page, count=1, flags=re.S)
    page = re.sub(r'<p class="subtitle">.*?</p>',
                  '<p class="subtitle">Αδύνατοι τύποι αντικειμένου και επιρρήματα τρόπου</p>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<ul>.*?</ul>', f'<ul>\n{rows}  </ul>', page, count=1, flags=re.S)
    open(os.path.join(BASE, 'part-4.html'), 'w', encoding='utf-8').write(page)


def add_nav():
    targets = glob.glob(os.path.join(BASE, 'topics/*.html')) + glob.glob(os.path.join(BASE, 'part-*.html')) + [os.path.join(BASE, 'index.html')]
    for path in targets:
        page = open(path, encoding='utf-8').read()
        if 'part-4.html' in page:
            continue
        before = 'href="../part-3.html">Μέρος 3</a>\n'
        after = 'href="part-3.html">Μέρος 3</a>\n'
        if before in page:
            page = page.replace(before, before + '      <a class="sd-jump-link" href="../part-4.html">Μέρος 4</a>\n', 1)
        elif after in page:
            page = page.replace(after, after + '      <a class="sd-jump-link" href="part-4.html">Μέρος 4</a>\n', 1)
        else:
            continue
        open(path, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    for name, items in NEW.items():
        print(name, 'updated' if add_items(os.path.join(BASE, name), items) else 'already complete')
    build_part4()
    add_nav()
    print('part-4 built, nav links added')
