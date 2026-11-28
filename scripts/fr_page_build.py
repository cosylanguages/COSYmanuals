import html
import os


def esc(x):
    return html.escape(x, quote=False)


def page(level, slug, s):
    up = '../../../../../'
    head = f"""<!DOCTYPE html>
<html lang="fr" data-lang-theme="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(s['title'])} &middot; Grammaire Fran&ccedil;aise {level.upper()} &middot; COSYlanguages</title>
<meta name="description" content="{esc(s['subtitle'])}">
<link rel="stylesheet" href="{up}shared/styles/lang-accents.css">
<link rel="stylesheet" href="{up}shared/styles/tokens.css">
<link rel="stylesheet" href="{up}shared/styles/base.css">
<link rel="stylesheet" href="{up}shared/styles/components.css">
<link rel="stylesheet" href="{up}shared/styles/layout.css">
<link rel="stylesheet" href="../assets/style.css">
<link rel="stylesheet" href="{up}shared/styles/manual-look.css">
<link rel="stylesheet" href="https://cosylanguages.github.io/COSYlanguages/css/ecosystem-strip.css">
</head>
<body>
<div data-ecosystem-strip data-self="manuals"></div>

<nav id="cosy-nav" aria-label="Navigation principale"></nav>

<header class="sd-sticky-header">
  <div class="sd-header-inner">
    <nav class="sd-jump-links" aria-label="Navigation dans la page">
      <a class="sd-jump-link" href="../index.html">&larr; Manuel {level.upper()}</a>
      <a class="sd-jump-link" href="#contexte">Contexte</a>
      <a class="sd-jump-link" href="#ccq">Compr&eacute;hension</a>
      <a class="sd-jump-link" href="#regle">R&egrave;gle &amp; Forme</a>
      <a class="sd-jump-link" href="#pratique">Exercice</a>
    </nav>
  </div>
</header>

<main data-level="{level.upper()}" class="container" id="fr-{level}-{slug}" data-grammar-point="fr-{level}-{slug}">
<div class="page-head">
 <span class="eyebrow">Grammaire Fran&ccedil;aise {level.upper()}</span>
 <h1>{esc(s['title'])}</h1>
 <p class="subtitle">{esc(s['subtitle'])}</p>
 <hr class="rule">
</div>

<div class="box outcome-banner" style="background:rgba(28,143,86,0.08); border-left:4px solid var(--role-verb, #1c8f56); padding:12px 16px; margin-bottom:20px; border-radius:4px;">
  <strong>&#127919; Objectif de communication :</strong> {esc(s['outcome'])}
</div>
"""

    ex = '\n'.join(
        f'  <li><span class="key-subject key-blue">Exemple {i+1} :</span> <span class="key-verb key-green"><b>{esc(a)}</b></span> &mdash; {esc(b)}</li>'
        for i, (a, b) in enumerate(s['examples']))

    quiz_json = '[' + ', '.join('{"correct": %d}' % q[2] for q in s['quiz']) + ']'
    quiz_items = []
    for i, (q, opts, correct, explain) in enumerate(s['quiz']):
        buttons = ''.join(f'<button class="qopt">{esc(o)}</button>' for o in opts)
        quiz_items.append(
            f'  <div class="qitem">\n'
            f'    <div class="qtext">{i+1}. {esc(q)}</div>\n'
            f'    <div class="qopts">{buttons}</div>\n'
            f'    <div class="qexplain">{esc(explain)}</div>\n'
            f'  </div>')
    quiz = '\n'.join(quiz_items)
    keys = ' '.join(f'{i+1}&middot;{"abcdef"[q[2]]}' for i, q in enumerate(s['quiz']))

    th = ''.join(f'<th scope="col">{esc(h)}</th>' for h in s['headers'])
    rows = '\n'.join(
        '      <tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r) + '</tr>' for r in s['rows'])

    mistakes = []
    for wrong, right, why in s['mistakes']:
        mistakes.append(f"""<div class="mflip">
  <div class="wrong-line"><span class="x">&#10060;</span><span class="wrong-text">{esc(wrong)}</span></div>
  <span class="hint">{esc(why)}</span>
  <div class="right-line"><span class="c">&#9989;</span><span>{esc(right)}</span></div>
</div>""")
    mistakes = '\n'.join(mistakes)

    checklist = ''.join(
        f'<label class="check-item"><input type="checkbox"><span>{esc(c)}</span></label>'
        for c in s['checklist'])

    more = '\n'.join(f'<li>{esc(m)}</li>' for m in s['more'])

    prevnext = ''
    if s.get('prev') or s.get('next'):
        parts = []
        if s.get('prev'):
            parts.append(f'<a class="prev" href="{esc(s["prev"][1])}"><span class="dir">&larr; Pr&eacute;c&eacute;dent</span><span class="ttl">{esc(s["prev"][0])}</span></a>')
        if s.get('next'):
            parts.append(f'<a class="next" href="{esc(s["next"][1])}"><span class="dir">Suivant &rarr;</span><span class="ttl">{esc(s["next"][0])}</span></a>')
        prevnext = '<div class="pager">' + ''.join(parts) + '</div>'

    tail = f"""
<section id="contexte" class="examples" style="margin-bottom:20px;">
 <span class="label">Exemples en contexte</span>
 <ul>
{ex}
 </ul>
</section>

<div class="box mint" style="margin-bottom:20px;">
  <h3>&#128064; Qu&rsquo;observez-vous ?</h3>
  <p>{esc(s['observe'])}</p>
</div>

<section id="ccq">
<div class="ccq-panel" data-quiz='{quiz_json}'><div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(s['quiz'])}</span><span class="pk-ans">&#10003; {keys}</span></div>
  <div class="quiz-head">
    <h3>&#128161; V&eacute;rifiez votre compr&eacute;hension (CCQ)</h3>
    <span class="quiz-score">Score&nbsp;: 0 / {len(s['quiz'])}</span>
  </div>
{quiz}
  <button class="quiz-reset">R&eacute;initialiser</button>
</div>
</section>

<section id="regle" style="margin-top:20px;">
<div class="table-wrap" tabindex="0" role="region" aria-label="{esc(s['title'])} &mdash; forme, r&ocirc;le et exemple" data-gv-autolabel><table>
    <thead>
      <tr>
{th}
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
</table></div>

<div class="box rule-box" style="margin-top:16px;">
  <p><strong>R&egrave;gle :</strong> {esc(s['rule'])}</p>
</div>

<div class="box why">
  <h3>&#9733; Pourquoi &ccedil;a compte</h3>
  <p>{esc(s['why'])}</p>
</div>

<div class="box native">
  <h3>&#128173; Pensez comme un natif</h3>
  <p>{esc(s['native'])}</p>
</div>

<div class="see-hear">
  <div class="col"><span class="lbl">Ce que vous voyez</span><span class="txt">{esc(s['see'])}</span></div>
  <div class="col"><span class="lbl">Ce que vous entendez</span><span class="txt">{esc(s['hear'])}</span></div>
</div>
</section>

<section id="pratique" style="margin-top:24px;">
<h2>&#9997;&#65039; Exercice</h2>
<div class="box mint">
  <h3>Autres exemples</h3>
  <ul>
{more}
  </ul>
</div>

<div class="mistakes">
  <div class="m-title">&#9888;&#65039; Erreurs fr&eacute;quentes</div>
{mistakes}
</div>

<div class="checklist" data-key="{slug}">
  <h3>&#127919; Est-ce que je sais d&eacute;j&agrave; faire &ccedil;a&nbsp;?</h3>
  {checklist}
  <div class="check-progress"></div>
</div>
</section>

{prevnext}
</main>
<footer class="site">
  <div class="container">
    <div>COSYlanguages &middot; Manuel de grammaire fran&ccedil;aise &middot; &eacute;dition web interactive</div>
    <div><a href="https://cosylanguages.github.io/COSYlanguages/index.html">&larr; Retour &agrave; cosylanguages.github.io</a></div>
  </div>
</footer>
<script src="../assets/app.js"></script>
<script src="https://cosylanguages.github.io/COSYlanguages/js/ecosystem-strip.js" defer></script>
</body>
</html>
"""
    return head + tail


def write(level, slug, s, root='/workspace/COSYmanuals'):
    path = os.path.join(root, 'manuals', 'fr', 'grammar', level, 'topics', slug + '.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page(level, slug, s))
    return path
