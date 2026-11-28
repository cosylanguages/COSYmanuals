"""Builder for the Italian and Greek grammar shelves.

The English builder slices a finished page to borrow its head, which is how the shell's sample quiz
ended up on 92 pages. This one writes the head from scratch, so every page is self-contained, and it
takes its labels from L10N so the same structure works in both languages.

    from lang_topic_build import build, spec, localise
    print(build('it', 'b1', 'pronomi-combinati', spec(...)))
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

L10N = {
    'it': dict(
        lang='it', title_suffix='Grammatica Italiana', hub='Hub Italiano',
        objective='Obiettivo comunicativo:',
        examples='Esempi in contesto', observe='Cosa osservi?',
        ccq='Verifica la comprensione', element='Elemento / struttura',
        role='Funzione in italiano', example='Esempio',
        rule='Formula / regola:', why='Perché conta',
        native='Pensa come un madrelingua', pron='Nota di pronuncia',
        bank='Altri esempi', mistakes='Errori frequenti',
        wrong='Sbagliato:', right='Corretto:', links='Collegamenti',
        checklist='Sai già usare questa struttura?', practice='Esercizi',
        score='Punteggio', celebrate='Hai completato questo argomento di grammatica!',
        reset='Ripeti il quiz', back='← Torna al manuale'),
    'el': dict(
        lang='el', title_suffix='Ελληνική Γραμματική', hub='Ελληνικά',
        objective='Επικοινωνιακός στόχος:',
        examples='Παραδείγματα σε χρήση', observe='Τι παρατηρείτε;',
        ccq='Έλεγχος κατανόησης', element='Δομή',
        role='Λειτουργία στα ελληνικά', example='Παράδειγμα',
        rule='Κανόνας:', why='Γιατί έχει σημασία',
        native='Σκεφτείτε σαν φυσικός ομιλητής', pron='Σημείωση προφοράς',
        bank='Περισσότερα παραδείγματα', mistakes='Συχνά λάθη',
        wrong='Λάθος:', right='Σωστό:', links='Συνδέσεις',
        checklist='Μπορείτε ήδη να το χρησιμοποιήσετε;', practice='Ασκήσεις',
        score='Βαθμοί', celebrate='Ολοκληρώσατε αυτό το θέμα γραμματικής!',
        reset='Επανάληψη ασκήσεων', back='← Πίσω στο εγχειρίδιο'),
    'ru': dict(
        lang='ru', title_suffix='Грамматика русского языка', hub='Русский язык',
        objective='Коммуникативная цель:',
        examples='Примеры в контексте', observe='Что вы замечаете?',
        ccq='Проверка понимания', element='Структура',
        role='Функция в русском языке', example='Пример',
        rule='Правило:', why='Почему это важно',
        native='Думайте как носитель языка', pron='Замечание о произношении',
        bank='Дополнительные примеры', mistakes='Частые ошибки',
        wrong='Неверно:', right='Верно:', links='Связи с другими темами',
        checklist='Вы уже умеете это использовать?', practice='Упражнения',
        score='Счёт', celebrate='Вы освоили эту тему грамматики!',
        reset='Повторить упражнения', back='← Назад к учебнику'),
}

CSS = ('../../../../../shared/styles/lang-accents.css',
       '../../../../../shared/styles/tokens.css',
       '../../../../../shared/styles/base.css',
       '../../../../../shared/styles/components.css',
       '../../../../../shared/styles/layout.css',
       '../assets/style.css',
       '../../../../../shared/styles/manual-look.css')


def esc(text):
    return html.escape(str(text), quote=False)


def spec(title, subtitle, objective, opener_theme, open_lines, formula, examples,
         observe, ccq, table, rule, why, native, pron, bank, mistakes, links,
         checklist, quiz):
    # An opener is written as (prefix, verb, suffix), but a call may split the sentence differently.
    # Treat the first item as the prefix, the last as the suffix and everything between as the verb,
    # so a two-part sentence ("Vorrei", " un caffè") and a two-verb one both render.
    openers = []
    for line in open_lines:
        line = tuple(line)
        if len(line) == 1:
            openers.append((line[0], '', ''))
        elif len(line) == 2:
            openers.append((line[0], '', line[1]))
        else:
            openers.append((line[0], ''.join(line[1:-1]), line[-1]))
    return dict(title=title, subtitle=subtitle, objective=objective,
                theme=opener_theme, open_lines=openers, formula=formula,
                examples=examples, observe=observe, ccq=ccq, table=table, rule=rule,
                why=why, native=native, pron=pron, bank=bank, mistakes=mistakes,
                links=links, checklist=checklist, quiz=quiz)


def quiz_block(items, heading, t, panel='quiz-panel', reset=False):
    rows = []
    for n, it in enumerate(items, 1):
        buttons = ''.join(f'<button type="button" class="qopt">{esc(o)}</button>'
                          for o in it['options'])
        rows.append(f'''<div class="qitem"><div class="qtext">{n}. {esc(it["question"])}</div>'''
                    f'''<div class="qopts">{buttons}</div>'''
                    f'''<div class="qexplain">{esc(it["explain"])}</div></div>''')
    tail = (f'<p class="celebration-msg">{esc(t["celebrate"])}</p>'
            f'<button type="button" class="quiz-reset">{esc(t["reset"])}</button>') if reset else ''
    key = ' '.join(f'{n}·{"abc"[it["correct"]]}' for n, it in enumerate(items, 1))
    data = '[' + ', '.join('{"correct": %d}' % it['correct'] for it in items) + ']'
    return f'''<div class="{panel}" data-quiz='{data}'>
<div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(items)}</span><span class="pk-ans">&#10003; {key}</span></div>
<div class="quiz-head"><h2>{esc(heading)}</h2><span class="quiz-score">{esc(t["score"])}: 0 / {len(items)}</span></div>
{''.join(rows)}{tail}</div>'''


def page_head(lang, level, slug, t, title, subtitle, jump_links):
    css = '\n'.join(f'<link rel="stylesheet" href="{c}">' for c in CSS)
    jumps = '\n'.join(f'    <a class="sd-jump-link" href="{href}">{esc(label)}</a>'
                      for label, href in jump_links)
    return f'''<!doctype html>
<html lang="{t["lang"]}" data-lang-theme="{t["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(t["title_suffix"])} {level.upper()}</title>
<meta name="description" content="{esc(title)}: {esc(subtitle)}">
{css}
<link rel="stylesheet" href="https://cosylanguages.github.io/COSYlanguages/css/ecosystem-strip.css">
</head>
<body>
<div data-ecosystem-strip data-self="manuals"></div>
<nav id="cosy-nav"></nav>
<header class="sd-sticky-header">
  <div class="sd-header-inner">
    <nav class="sd-jump-links" aria-label="In-page section navigation">
{jumps}
    </nav>
  </div>
</header>
<main data-level="{level.upper()}" class="container" id="{t["lang"]}-{level}-{slug}" data-grammar-point="{t["lang"]}-{level}-{slug}">
'''


def main_sections(s, slug, t):
    openers = '\n'.join(
        f'<li>{esc(a)} <span class="key-verb key-green">{esc(b)}</span>{esc(c)}</li>'
        for a, b, c in s['open_lines'])
    examples = '\n'.join(
        f'<li>{esc(a)} <em>{esc(b)}</em> — {esc(c)}</li>' for a, b, c in s['examples'])
    rows = '\n'.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td>'
                     for a, b, c in s['table'])
    bank = '\n'.join(
        f'<li><strong>{esc(r[0])}</strong> {esc(" — ".join(r[1:]))}</li>' for r in s['bank'])
    mistakes = '\n'.join(
        f'<div class="mflip"><div class="wrong-line">❌ <span class="wrong-text">{esc(w)}</span></div>'
        f'<div class="right-line">✅ <span>{esc(r)}</span></div></div>' for w, r in s['mistakes'])
    links = ' · '.join(f'<a href="{esc(h)}">{esc(n)}</a>' for n, h in s['links'])
    checks = '\n'.join(f'<label class="check-item"><input type="checkbox"><span>{esc(c)}</span></label>'
                       for c in s['checklist'])
    left, right = s['formula']
    return f'''  <div class="page-head">
    <span class="eyebrow">{esc(s["theme"])}</span>
    <h1>{esc(s["title"])}</h1>
    <p class="subtitle">{esc(s["subtitle"])}</p>
    <hr class="rule">
  </div>
  <div class="outcome-banner">🎯 <strong>{esc(t["objective"])}</strong> {esc(s["objective"])}</div>
  <section class="gv gv-open">
    <ul class="gv-lines">{openers}</ul>
    <p class="gv-formula"><span class="gv-rule">{esc(left)}</span> <span class="gv-rule">{esc(right)}</span></p>
  </section>
  <section class="examples"><span class="label">{esc(t["examples"])}</span><ul>{examples}</ul></section>
  <div class="box mint"><h3>👀 {esc(t["observe"])}</h3><p>{esc(s["observe"])}</p></div>
  <section id="ccq">{quiz_block(s["ccq"], t["ccq"], t, panel="ccq-panel")}</section>
  <section id="regola">
    <div class="table-wrap" tabindex="0" role="region" aria-label="{esc(s["title"])}">
      <table><thead><tr><th scope="col">{esc(t["element"])}</th><th scope="col">{esc(t["role"])}</th><th scope="col">{esc(t["example"])}</th></tr></thead>
      <tbody>{rows}</tbody></table>
    </div>
    <div class="box rule-box"><p><strong>{esc(t["rule"])}</strong> {esc(s["rule"])}</p></div>
  </section>
  <div class="box why"><h3>★ {esc(t["why"])}</h3><p>{esc(s["why"])}</p></div>
  <div class="box native"><h3>💭 {esc(t["native"])}</h3><p>{esc(s["native"])}</p></div>
  <div class="pron-callout"><h3>🗣️ {esc(t["pron"])}</h3><p>{esc(s["pron"])}</p></div>
  <div class="examples"><span class="label">{esc(t["bank"])}</span><ul>{bank}</ul></div>
  <div class="mistakes"><div class="m-title">⚠️ {esc(t["mistakes"])}</div>{mistakes}</div>
  <div class="box connect"><h3>🔗 {esc(t["links"])}</h3><p>{links}</p></div>
  <div class="checklist" data-key="{slug}"><h3>🎯 {esc(t["checklist"])}</h3>{checks}<div class="check-progress"></div></div>
  <section id="pratica">{quiz_block(s["quiz"], t["practice"], t, reset=True)}</section>
'''


def build(lang, level, slug, s):
    t = L10N[lang]
    base = os.path.join(ROOT, 'manuals', lang, 'grammar', level)
    jumps = [(t['hub'], '../index.html')]
    for n in (1, 2, 3, 4):
        if os.path.exists(os.path.join(base, f'part-{n}.html')):
            jumps.append((f'{n}', f'../part-{n}.html'))
    out = (page_head(lang, level, slug, t, s['title'], s['subtitle'], jumps)
           + '\n' + main_sections(s, slug, t)
           + f'''  <p class="pager"><a class="prev" href="../index.html">{esc(t["back"])}</a></p>
</main>
<footer class="site"><div class="container"><div>COSYlanguages · {esc(t["title_suffix"])} {level.upper()}</div></div></footer>
<script src="../assets/app.js"></script>
<script src="https://cosylanguages.github.io/COSYlanguages/js/ecosystem-strip.js" defer></script>
</body>
</html>
''')
    path = os.path.join(base, 'topics', f'{slug}.html')
    open(path, 'w', encoding='utf-8').write(out)
    return path
