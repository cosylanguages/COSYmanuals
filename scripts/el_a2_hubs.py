"""Link every Greek A2 topic page from a part hub and add the functional part."""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'manuals/el/grammar/a2')

PARTS = {
    1: ['aoristos-paratatikos'],
    2: ['mellochrons-exakolouthitikos-stigmiaiou', 'syntomos-mellontas', 'schedia-kai-yposcheseis',
        'provlepseis', 'ypotaktiki-egklisi', 'protaseis-kai-symvoules', 'odigies', 'diapragmatefsi'],
    3: ['syxronoi-sygkritikoi-vathmoi', 'adynatoi-typoi-antonymion', 'plagies-erotiseis',
        'pathetiki-foni', 'ypothetikoi-logoi', 'anaforikes-protaseis-pou', 'plagiakos-logos'],
    4: ['klitika-antikeimena', 'klitika-kai-prostaktiki', 'epirrimata-apo-epitheta'],
    5: ['angelies-ergasias', 'viografiko', 'synentefxi', 'dexiotites', 'epaggelmatiki-epikoinonia',
        'ston-giatro', 'farmakeio', 'dimosies-ypiresies', 'ilefonikes-synennoiseis', 'typologies-evgeneias',
        'stegasi-enoikio', 'geitonia', 'agores-kai-epistrofes', 'kathimerina-provlimata',
        'mesa-enimerosis', 'tainies-kai-vivlia', 'mousiki-kai-paradoseis', 'giortes-kai-ethima',
        'parousiasi', 'synthesi'],
}

PART5 = dict(
    title='Μέρος 5 · Γραμματική σε χρήση',
    subtitle='Εργασία, υγεία, υπηρεσίες, στέγαση, πολιτισμός',
    page_title='Μέρος 5: Γραμματική σε χρήση · Γραμματική Ελληνικών Α2',
)


def title_of(slug):
    html = open(os.path.join(BASE, 'topics', slug + '.html'), encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.group(1))).strip() if m else slug


def card(slug):
    return f'    <li><a href="topics/{slug}.html">{title_of(slug)}</a></li>\n'


def ensure_part5():
    path = os.path.join(BASE, 'part-5.html')
    if os.path.exists(path):
        return
    html = open(os.path.join(BASE, 'part-1.html'), encoding='utf-8').read()
    html = html.replace('<title>Μέρος 1: Παρελθοντικοί Χρόνοι & Διάρκεια · Γραμματική Ελληνικών Α2</title>',
                        f'<title>{PART5["page_title"]}</title>')
    html = html.replace('<h1>Μέρος 1 · Παρελθοντικοί Χρόνοι & Διάρκεια</h1>', f'<h1>{PART5["title"]}</h1>')
    html = html.replace('<p class="subtitle">Παρατατικός, Αόριστος και Παρακείμενος</p>',
                        f'<p class="subtitle">{PART5["subtitle"]}</p>')
    html = re.sub(r'  <ul>.*?</ul>\n', '  <ul>\n  </ul>\n', html, flags=re.S)
    open(path, 'w', encoding='utf-8').write(html)


def main():
    ensure_part5()
    for num, slugs in PARTS.items():
        path = os.path.join(BASE, f'part-{num}.html')
        html = open(path, encoding='utf-8').read()
        linked = set(re.findall(r'href="topics/([a-z0-9-]+)\.html"', html))
        add = ''.join(card(s) for s in slugs if s not in linked)
        if add:
            html = html.replace('  </ul>\n', add + '  </ul>\n', 1)
            open(path, 'w', encoding='utf-8').write(html)
    index = os.path.join(BASE, 'index.html')
    html = open(index, encoding='utf-8').read()
    if 'part-5.html' not in html:
        html = html.replace('      <a class="sd-jump-link" href="part-4.html">Μέρος 4</a>\n',
                            '      <a class="sd-jump-link" href="part-4.html">Μέρος 4</a>\n'
                            '      <a class="sd-jump-link" href="part-5.html">Μέρος 5</a>\n')
        html = html.replace('  </div>\n</main>',
                            ('    <a class="part-card" href="part-5.html"><div style="height:4px;background:#7c3aed;'
                             'border-radius:2px;margin-bottom:12px;"></div><h2>Μέρος 5 · Γραμματική σε χρήση</h2>'
                             '<p>Εργασία, υγεία, υπηρεσίες, στέγαση, πολιτισμός.</p><span style="font-size:12px;'
                             'font-weight:700;color:var(--blue-700);">20 κεφάλαια →</span></a>\n  </div>\n</main>'), 1)
        open(index, 'w', encoding='utf-8').write(html)


if __name__ == '__main__':
    main()
