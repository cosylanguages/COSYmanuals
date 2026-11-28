#!/usr/bin/env python3
"""Fill an English grammar topic page from a spec, keeping the shell intact.

The shell (head, navigation, footer, scripts) is copied from a committed
English page; only <title>, the description and everything inside <main> are
rewritten. English pages label their sections in English, so this mirrors
fr_topic_build.py with English headings and an English guided-discovery opener.
"""
import html
import re

ROOT = "manuals/en/grammar"
SHELL = "manuals/en/grammar/b2/topics/mandative-subjunctive.html"
LET = "abcdefgh"


def esc(t):
    return html.escape(t, quote=False)


def quiz_attrs(items):
    import json
    return json.dumps([{"correct": i["correct"]} for i in items], ensure_ascii=False)


def key_line(items):
    return " ".join(f"{n}\u00b7{LET[i['correct']]}" for n, i in enumerate(items, 1))


def spread(spec):
    """Spread the correct answers across the option positions."""
    items = []
    for n, it in enumerate(spec["quiz"]):
        opts, c = it["options"], it["correct"]
        target = n % len(opts)
        shift = (c - target) % len(opts)
        items.append(dict(question=it["question"], options=opts[shift:] + opts[:shift],
                          correct=target, explain=it["explain"]))
    spec["quiz"] = items
    return spec


def quiz_block(items, heading, panel="ccq-panel", htag="h3", reset=False):
    rows = []
    for n, it in enumerate(items, 1):
        opts = "\n".join(f'      <button type="button" class="qopt">{esc(o)}</button>' for o in it["options"])
        rows.append(f"""  <div class="qitem">
    <div class="qtext">{n}. {esc(it['question'])}</div>
    <div class="qopts">
{opts}
    </div>
    <div class="qexplain">{esc(it['explain'])}</div>
  </div>""")
    tail = (' <p class="celebration-msg" style="margin-top:16px; font-weight:700; color:#1c8f56;">'
            '\U0001f389 Progress celebration: you have completed this grammar topic!</p>\n'
            ' <button type="button" class="quiz-reset">Reset the quiz</button>\n') if reset else ''
    return f"""<div class="{panel}" data-quiz='{quiz_attrs(items)}'><div class="print-key" aria-hidden="true"><span class="pk-score">&#9998; ___ / {len(items)}</span><span class="pk-ans">&#10003; {key_line(items)}</span></div>
  <div class="quiz-head">
    <{htag}>{heading}</{htag}>
    <span class="quiz-score">Score\u00a0: 0 / {len(items)}</span>
  </div>
{chr(10).join(rows)}
{tail}</div>"""


def opener(spec, slug):
    lines = "\n".join(
        f'    <li><span class="gv-r1">{esc(before)}</span> <details class="gv-gap"><summary>'
        f'<span class="gv-sr">gap</span></summary><span class="gv-r2">{esc(gap)}</span></details>'
        f'{esc(after)}</li>' for before, gap, after in spec["open_lines"])
    left, right = spec["formula"]
    return f"""<section class="gv gv-open" aria-labelledby="open-{slug}">
  <span class="gv-theme">{esc(spec['open_theme'])}</span>
  <h2 class="gv-title" id="open-{slug}">{esc(spec['open_title'])} <span class="gv-screen">tap the line.</span><span class="gv-print">write it on the line.</span></h2>
  <ol class="gv-lines">
{lines}
  </ol>
  <div class="gv gv-formula" role="group" aria-label="{esc(spec['open_theme'])}">
    <span class="gv-pair"><span class="gv-slot gv-r1">{esc(left)}</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">{esc(right)}</span></span>
  </div>
</section>"""


def body(spec, slug):
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
   <p><span class="key-error key-red">❌ Wrong:</span> {esc(w)}</p>
   <p><span class="key-verb key-green">✅ Right:</span> {esc(r)}</p>
 </div>""" for w, r in spec["mistakes"])
    links = " · ".join(f'<a href="{esc(h)}">{esc(t)}</a>' for t, h in spec["links"])
    checks = "\n".join(f' <label class="check-item"><input type="checkbox"><span>{esc(c)}</span></label>'
                       for c in spec["checklist"])
    return f"""{opener(spec, slug)}

<div class="page-head">
 <span class="eyebrow">Level B2 Grammar</span>
 <h1>{title}</h1>
 <p class="subtitle">{esc(spec['subtitle'])}</p>
 <hr class="rule">
</div>

<div class="box outcome-banner" style="background:rgba(28,143,86,0.08); border-left:4px solid var(--role-verb, #1c8f56); padding:12px 16px; margin-bottom:20px; border-radius:4px;">
  <strong>🎯 What you can communicate after this page:</strong> {esc(spec['objective'])}
</div>

<section id="contexte" class="examples" style="margin-bottom:20px;">
 <span class="label">Examples in context</span>
 <ul>
{ex}
 </ul>
</section>

<div class="box mint" style="margin-bottom:20px;">
  <h3>👀 What do you observe?</h3>
  <p>{esc(spec['observe'])}</p>
</div>

<section id="ccq">
{quiz_block(spec['ccq'], '💡 Check your understanding')}
</section>

<section id="regle" style="margin-top:20px;">
<div class="table-wrap" tabindex="0" role="region" aria-label="{title} — form, role and example"><table>
    <thead>
      <tr>
        <th scope="col">Element / structure</th>
        <th scope="col">Role in English</th>
        <th scope="col">Application example</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table></div>
<div class="box rule-box" style="margin-top:15px;">
  <p><strong>Formula / rule:</strong> {esc(spec['rule'])}</p>
</div>
</section>

<div class="box why" style="margin-top:20px;">
 <h3>★ Why it matters</h3>
 <p>{esc(spec['why'])}</p>
</div>

<div class="box native" style="margin-top:20px;">
 <h3>💭 Think like a native speaker</h3>
 <p>{esc(spec['native'])}</p>
</div>

<div class="pron-callout" style="margin-top:20px;">
 <h3>🗣️ Pronunciation note</h3>
 <p>{esc(spec['pron'])}</p>
</div>

<div class="examples" style="margin-top:20px;">
 <span class="label">Additional example bank</span>
 <ul>
{bank}
 </ul>
</div>

<div class="mistakes" style="margin-top:20px;">
 <div class="m-title">⚠️ Common mistakes to avoid</div>
{mistakes}
</div>

<div class="box connect" style="margin-top:20px;">
 <h3>🔗 Connects to what you already know</h3>
 <p>{links}</p>
</div>

<div class="checklist" data-key="{key_line(spec['quiz'])}" style="margin-top:20px;">
 <h3>🎯 Can you already use this?</h3>
{checks}
 <div class="check-progress"></div>
</div>

<section id="pratique" style="margin-top:20px;">
{quiz_block(spec['quiz'], 'Quick check', panel='quiz-panel', htag='h2', reset=True)}
</section>
"""


def prune_nav(fragment, level):
    """Drop navigation links whose target does not exist for this level."""
    import os

    def keep(m):
        target = os.path.normpath(os.path.join(ROOT, level, m.group(1)))
        return m.group(0) if os.path.exists(target) else ""

    fragment = re.sub(r'\s*<a class="sd-jump-link[^"]*" href="\.\./([^"]+)">[^<]*</a>', keep, fragment)
    return re.sub(r"<nav[^>]*>\s*</nav>\n?", "", fragment)


def build(level, slug, spec):
    src = open(SHELL, encoding="utf-8").read()
    head_end = src.index("<main ")
    tail_start = src.index("</main>")
    head, tail = src[:head_end], src[tail_start:]
    main_open = src[head_end:src.index(">", head_end) + 1]
    gid = f"en-{level}-{slug}"
    main_open = re.sub(r'id="[^"]*"', f'id="{gid}"', main_open, count=1)
    main_open = re.sub(r'data-grammar-point="[^"]*"', f'data-grammar-point="{gid}"', main_open, count=1)
    title = spec["title"]
    head = re.sub(r"<title>.*?</title>",
                  f"<title>{esc(title)} · English Grammar {level.upper()} · COSYlanguages</title>",
                  head, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="Complete English grammar guide to {esc(title)} at level {level.upper()}. Rule, examples, CCQs and interactive practice.">',
                  head, count=1)
    out = prune_nav(head, level) + main_open + "\n" + body(spec, slug) + "\n" + tail
    path = f"{ROOT}/{level}/topics/{slug}.html"
    open(path, "w", encoding="utf-8").write(out)
    return path


def spec(title, subtitle, objective, open_theme, open_title, open_lines, formula,
         examples, observe, ccq, table, rule, why, native, pron, bank, mistakes,
         links, checklist, quiz):
    return dict(title=title, subtitle=subtitle, objective=objective,
                open_theme=open_theme, open_title=open_title, open_lines=open_lines,
                formula=formula, examples=examples, observe=observe, ccq=ccq,
                table=table, rule=rule, why=why, native=native, pron=pron, bank=bank,
                mistakes=mistakes, links=links, checklist=checklist, quiz=quiz)
