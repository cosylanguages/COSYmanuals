"""Add the new Italian A2 topics to the part cards and create part 4.

Cards carry a title and a one-line gloss, matching the existing grid markup. Running the script twice
changes nothing.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'manuals/it/grammar/a2')

NEW = {
    'part-1.html': [
        ('emozioni-al-passato', 'Le Emozioni al Passato', 'Stati d\'animo, reazioni e verbi pronominali'),
        ('trapassato-prossimo', 'Il Trapassato Prossimo', 'Un fatto anteriore a un altro fatto passato'),
    ],
    'part-2.html': [
        ('il-futuro-semplice', 'Il Futuro Semplice', 'Forme regolari, progetti, promesse'),
        ('il-futuro-irregolare', 'Il Futuro Irregolare', 'Sarò, avrò, andrò, verrò e i modali'),
        ('fare-previsioni', 'Fare Previsioni', 'Futuro di previsione e di supposizione'),
        ('stare-per-e-intenzioni', 'Stare per e le Intenzioni', 'Azione imminente e progetti dichiarati'),
        ('dare-consigli', 'Dare Consigli', 'Dovresti, ti consiglio di, è meglio che'),
        ('esprimere-desideri-e-speranze', 'Esprimere Desideri e Speranze', 'Spero che, magari, vorrei tanto'),
        ('se-presente-futuro', 'Se, Presente e Futuro', 'L\'ipotesi reale del primo tipo'),
        ('periodo-ipotetico-2', 'Il Periodo Ipotetico del Secondo Tipo', 'Se più congiuntivo imperfetto'),
        ('il-condizionale-presente', 'Il Condizionale Presente', 'Cortesia, desideri, notizie non confermate'),
    ],
    'part-3.html': [
        ('pronomi-diretti-e-indiretti', 'Pronomi Diretti e Indiretti', 'Lo vedo, gli parlo, le scrivo'),
        ('pronomi-indiretti', 'I Pronomi Indiretti', 'Mi, ti, gli, le, ci, vi'),
        ('pronomi-combinati', 'I Pronomi Combinati (base)', 'Me lo, te la, glielo, ce ne'),
        ('i-pronomi-ci-e-ne', 'I Pronomi Ci e Ne', 'Luogo, argomento e quantità'),
        ('imperativo-con-pronomi', 'L\'Imperativo con i Pronomi', 'Dammi, fallo, portamelo'),
        ('il-comparativo-e-il-superlativo', 'Il Comparativo e il Superlativo', 'Più di, come, il più, -issimo'),
        ('obbligo-dovere-bisogna', 'Obbligo: Dovere e Bisogna', 'Obbligo personale e impersonale'),
        ('molto-poco-troppo', 'Molto, Poco e Troppo', 'Quantità graduata, accordo e invariabilità'),
        ('l-articolo-partitivo', 'L\'Articolo Partitivo', 'Del, dei, delle: quantità non precisata'),
        ('forma-passiva-base', 'La Forma Passiva', 'Essere e venire più participio'),
    ],
}

PART4 = [('il-tempo-atmosferico', 'Il Tempo Atmosferico', 'Fa caldo, c\'è vento, piove, previsioni')]


def cards(items):
    return ''.join(
        f'<a class="topic-card" href="topics/{slug}.html"><div class="ttl">{title}</div>'
        f'<div class="sub">{sub}</div></a>' for slug, title, sub in items)


def add_cards(path, items):
    page = open(path, encoding='utf-8').read()
    missing = [i for i in items if f'topics/{i[0]}.html' not in page]
    if not missing:
        return False
    page = page.replace('</div>\n</main>', cards(missing) + '</div>\n</main>', 1)
    open(path, 'w', encoding='utf-8').write(page)
    return True


def build_part4():
    tpl = open(os.path.join(BASE, 'part-3.html'), encoding='utf-8').read()
    page = re.sub(r'<title>.*?</title>', '<title>Parte 4: Tempo e Descrizione · Grammatica Italiana A2</title>', tpl, count=1, flags=re.S)
    page = re.sub(r'<h1>.*?</h1>', '<h1>Parte 4 · Tempo e Descrizione</h1>', page, count=1, flags=re.S)
    page = re.sub(r'<p class="subtitle">.*?</p>',
                  '<p class="subtitle">Parlare del tempo atmosferico e descrivere l\'ambiente</p>',
                  page, count=1, flags=re.S)
    page = re.sub(r'<div class="topic-grid">.*?</div>\s*</main>',
                  '<div class="topic-grid">' + cards(PART4) + '</div>\n</main>', page, count=1, flags=re.S)
    open(os.path.join(BASE, 'part-4.html'), 'w', encoding='utf-8').write(page)


def add_nav():
    targets = glob.glob(os.path.join(BASE, 'topics/*.html')) + glob.glob(os.path.join(BASE, 'part-*.html')) + [os.path.join(BASE, 'index.html')]
    for path in targets:
        page = open(path, encoding='utf-8').read()
        if 'part-4.html' in page:
            continue
        before = 'href="../part-3.html">Parte 3</a>\n'
        after = 'href="part-3.html">Parte 3</a>\n'
        if before in page:
            page = page.replace(before, before + '      <a class="sd-jump-link" href="../part-4.html">Parte 4</a>\n', 1)
        elif after in page:
            page = page.replace(after, after + '      <a class="sd-jump-link" href="part-4.html">Parte 4</a>\n', 1)
        else:
            continue
        open(path, 'w', encoding='utf-8').write(page)


if __name__ == '__main__':
    for name, items in NEW.items():
        print(name, 'updated' if add_cards(os.path.join(BASE, name), items) else 'already complete')
    build_part4()
    add_nav()
    print('part-4 built, nav links added')
