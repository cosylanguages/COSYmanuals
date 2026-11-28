#!/usr/bin/env python3
"""Fill a grammar topic page from a spec, keeping the shell intact.

Reconstructed after /tmp was cleared. The markup is reproduced from the pages
already committed under manuals/fr/grammar/b1 and b2.
"""
import html
import json
import os
import re

ROOT = "/workspace/COSYmanuals/manuals/fr/grammar"
LET = "abcdefgh"


def esc(t):
    return html.escape(t, quote=False)


def quiz_attrs(items):
    return json.dumps([{"correct": i["correct"]} for i in items], ensure_ascii=False)


def key_line(items):
    return " ".join(f"{n}\u00b7{LET[i['correct']]}" for n, i in enumerate(items, 1))


def quiz_block(items, heading, cls="ccq-panel", htag="h3"):
    rows = []
    for n, it in enumerate(items, 1):
        opts = "\n".join(f"      <button type=\"button\" class=\"qopt\">{esc(o)}</button>" for o in it["options"])
        rows.append(f"""  <div class="qitem">
    <div class="qtext">{n}. {esc(it['question'])}</div>
    <div class="qopts">
{opts}
    </div>
    <div class="qexplain">{esc(it['explain'])}</div>
  </div>""")
    body = "\n".join(rows)
    return f"""<div class="{cls}" data-quiz='{quiz_attrs(items)}'><div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(items)}</span><span class="pk-ans">&#10003; {key_line(items)}</span></div>
  <div class="quiz-head">
    <{htag}>{heading}</{htag}>
    <span class="quiz-score">Score\u00a0: 0 / {len(items)}</span>
  </div>
{body}
</div>"""


def practice_block(items):
    rows = []
    for it in items:
        opts = "\n".join(f"     <button type=\"button\" class=\"qopt\">{esc(o)}</button>" for o in it["options"])
        rows.append(f""" <div class="qitem">
   <div class="qtext">{esc(it['question'])}</div>
   <div class="qopts">
{opts}
   </div>
   <div class="qexplain">{esc(it['explain'])}</div>
 </div>""")
    body = "\n".join(rows)
    return f"""<div class="quiz-panel" data-quiz='{quiz_attrs(items)}'><div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(items)}</span><span class="pk-ans">&#10003; {key_line(items)}</span></div>
 <div class="quiz-head"><h2>Exercice de contrôle</h2><span class="quiz-score">Score\u00a0: 0 / {len(items)}</span></div>
{body}
 <p class="celebration-msg" style="margin-top:16px; font-weight:700; color:#1c8f56;">\U0001f389 Progress Celebration : Vous avez complété ce sujet de grammaire !</p>
 <button type="button" class="quiz-reset">Réinitialiser le quiz</button>
</div>"""


def vary(spec):
    """Spread the correct answers across the options so the key is not all a."""
    items = []
    for n, it in enumerate(spec["quiz"]):
        opts, c = it["options"], it["correct"]
        target = n % len(opts)
        shift = (c - target) % len(opts)
        items.append(dict(question=it["question"], options=opts[shift:] + opts[:shift],
                          correct=target, explain=it["explain"]))
    spec["quiz"] = items
    spec["key"] = key_line(items)
    return spec


def body(spec, level, slug):
    title = esc(spec["title"])
    ex = "\n".join(
        f'  <li><span class="key-subject key-blue">{esc(k)}</span> <span class="key-verb key-green">'
        f'<b>{esc(v)}</b></span> — {esc(n)}</li>' for k, v, n in spec["examples"])
    rows = "\n".join(
        f"""      <tr>
        <td><strong>{esc(a)}</strong></td>
        <td>{esc(b)}</td>
        <td>{esc(c)}</td>
      </tr>""" for a, b, c in spec["table"])
    bank = "\n".join(
        f'  <li><span class="key-subject key-blue">{esc(k)}</span> {esc(v)}</li>' for k, v in spec["bank"])
    mistakes = "\n".join(
        f""" <div class="mflip" style="background:#fff3f3; border-left:4px solid #e53e3e; padding:12px; margin-top:8px; border-radius:4px;">
   <p><span class="key-error key-red">❌ Erreur :</span> {esc(w)}</p>
   <p><span class="key-verb key-green">✅ Correct :</span> {esc(r)}</p>
 </div>""" for w, r in spec["mistakes"])
    links = " · ".join(f'<a href="{esc(h)}">{esc(t)}</a>' for t, h in spec["links"])
    checks = "\n".join(f' <label class="check-item"><input type="checkbox"><span>{esc(c)}</span></label>'
                       for c in spec["checklist"])
    key = key_line(spec["quiz"])
    return f"""<div class="page-head">
 <span class="eyebrow">Grammaire Française {level.upper()}</span>
 <h1>{title}</h1>
 <p class="subtitle">{esc(spec['subtitle'])}</p>
 <hr class="rule">
</div>

<div class="box outcome-banner" style="background:rgba(28,143,86,0.08); border-left:4px solid var(--role-verb, #1c8f56); padding:12px 16px; margin-bottom:20px; border-radius:4px;">
  <strong>\U0001f3af Objectif de communication :</strong> {esc(spec['objective'])}
</div>

<section id="contexte" class="examples" style="margin-bottom:20px;">
 <span class="label">Exemples en contexte</span>
 <ul>
{ex}
 </ul>
</section>

<div class="box mint" style="margin-bottom:20px;">
  <h3>\U0001f440 Qu'observez-vous ?</h3>
  <p>{esc(spec['observe'])}</p>
</div>

<section id="ccq">
{quiz_block(spec['ccq'], '\U0001f4a1 Vérifiez votre compréhension (CCQ)')}
</section>

<section id="regle" style="margin-top:20px;">
<div class="table-wrap" tabindex="0" role="region" aria-label="{title} — forme, rôle et exemple" data-gv-autolabel><table>
    <thead>
      <tr>
        <th scope="col">Élément / Structure</th>
        <th scope="col">Rôle en français</th>
        <th scope="col">Exemple d'application</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table></div>
<div class="box rule-box" style="margin-top:15px;">
  <p><strong>Formule / Règle :</strong> {esc(spec['rule'])}</p>
</div>
</section>

<div class="box why" style="margin-top:20px;">
 <h3>★ Pourquoi c'est important</h3>
 <p>{esc(spec['why'])}</p>
</div>

<div class="box native" style="margin-top:20px;">
 <h3>\U0001f4ad Pensez comme un francophone</h3>
 <p>{esc(spec['native'])}</p>
</div>

<div class="pron-callout" style="margin-top:20px;">
 <h3>\U0001f5e3\ufe0f Note de prononciation</h3>
 <p>{esc(spec['pron'])}</p>
</div>

<div class="examples" style="margin-top:20px;">
 <span class="label">Banque d'exemples complémentaires</span>
 <ul>
{bank}
 </ul>
</div>

<div class="mistakes" style="margin-top:20px;">
 <div class="m-title">⚠️ Erreurs fréquentes à éviter</div>
{mistakes}
</div>

<div class="box connect" style="margin-top:20px;">
 <h3>\U0001f517 En lien avec ce que vous savez déjà</h3>
 <p>{links}</p>
</div>

<div class="checklist" data-key="{key}" style="margin-top:20px;">
 <h3>\U0001f3af Pouvez-vous déjà l'utiliser ?</h3>
{checks}
 <div class="check-progress"></div>
</div>

<section id="pratique" style="margin-top:20px;">
{practice_block(spec['quiz'])}
</section>
"""


def build(lang, level, slug, spec):
    path = os.path.join(ROOT, level, "topics", slug + ".html")
    src = open(path, encoding="utf-8").read()
    head_end = src.index("<main ")
    tail_start = src.index("</main>")
    head, tail = src[:head_end], src[tail_start:]
    main_open = src[head_end:src.index(">", head_end) + 1]
    gid = f"{lang}-{level}-{slug}"
    main_open = re.sub(r'id="[^"]*"', f'id="{gid}"', main_open, count=1)
    main_open = re.sub(r'data-grammar-point="[^"]*"', f'data-grammar-point="{gid}"', main_open, count=1)

    title = spec["title"]
    head = re.sub(r"<title>.*?</title>",
                  f"<title>{esc(title)} · Grammaire Française {level.upper()} · COSYlanguages</title>",
                  head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="Guide complet de grammaire française sur {esc(title)} pour le niveau {level.upper()}. Règle, exemples, CCQs et exercices interactifs.">',
                  head, count=1)
    out = head + main_open + "\n" + body(spec, level, slug) + "\n" + tail
    open(path, "w", encoding="utf-8").write(out)
    return path


def spec(title, subtitle, objective, examples, observe, ccq, table, rule, why,
         native, pron, bank, mistakes, links, checklist, key, quiz):
    return dict(title=title, subtitle=subtitle, objective=objective, examples=examples,
                observe=observe, ccq=ccq, table=table, rule=rule, why=why, native=native,
                pron=pron, bank=bank, mistakes=mistakes, links=links, checklist=checklist,
                key=key, quiz=quiz)
