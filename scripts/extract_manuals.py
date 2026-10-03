#!/usr/bin/env python3
"""
COSYmanuals Extraction Pipeline
-------------------------------
Extracts COSYplatform curriculum JSON datasets from `curriculums/<lang>/<course_type>/<level>.json`
and produces derived Markdown manuals & rich HTML manual pages under:
  manuals/<lang>/<course_type>/<level>/
    ├── grammar.md & grammar.html
    ├── vocabulary.md & vocabulary.html
    ├── communication.md & communication.html
    ├── README.md
    └── index.html
"""

import json
import html
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)

def parse_teacher_notes(text):
    if not isinstance(text, str) or not text.strip():
        return {'code': None, 'cando': None, 'pronunciation': [], 'leftover': ''}

    code = None
    cando = None
    pronunciation = []
    leftover_lines = []

    lines = text.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if line.startswith('code:'):
            val = line[len('code:'):].strip().strip('"\'')
            code = val
            i += 1
            continue

        if line.startswith('cando:'):
            val = line[len('cando:'):].strip().strip('"\'')
            cando = val
            i += 1
            continue

        if line.startswith('pronunciation:'):
            p_text = line[len('pronunciation:'):].strip()
            j_str = p_text
            j_parsed = None
            j_end_idx = i
            for j in range(i, len(lines)):
                if j > i:
                    j_str += '\n' + lines[j].strip()
                try:
                    candidate = j_str.strip()
                    if (candidate.startswith('"') and candidate.endswith('"')) or (candidate.startswith("'") and candidate.endswith("'")):
                        candidate = candidate[1:-1]
                    j_parsed = json.loads(candidate)
                    j_end_idx = j
                    break
                except Exception:
                    pass

            if j_parsed is not None:
                if isinstance(j_parsed, list):
                    pronunciation = j_parsed
                elif isinstance(j_parsed, dict):
                    pronunciation = [j_parsed]
                i = j_end_idx + 1
                continue
            else:
                logging.warning(f"Failed to parse pronunciation JSON in teacher_notes: {p_text}")
                leftover_lines.append(line)
                i += 1
                continue

        leftover_lines.append(line)
        i += 1

    leftover = '\n'.join(leftover_lines).strip()
    return {
        'code': code,
        'cando': cando,
        'pronunciation': pronunciation,
        'leftover': leftover
    }

def render_teacher_notes_html(notes):
    parts = []
    if notes.get('cando'):
        parts.append(f'<div class="lesson-cando">🎯 <strong>I can:</strong> {html.escape(notes["cando"])}</div>')

    pron = notes.get('pronunciation') or []
    if pron:
        pron_items = []
        for item in pron:
            if not isinstance(item, dict): continue
            item_html = []
            point = item.get('point')
            if point:
                item_html.append(f'<div class="lesson-pronunciation-point">🗣️ {html.escape(str(point))}</div>')
            explain = item.get('explain')
            if explain:
                item_html.append(f'<div class="lesson-pronunciation-explain">{html.escape(str(explain))}</div>')

            examples = item.get('examples') or []
            minimal_pairs = item.get('minimalPairs') or []
            alphabet = item.get('alphabet') or []

            ex_pills = []
            for ex in examples:
                if isinstance(ex, dict):
                    word = ex.get('word') or ex.get('pattern') or ''
                    ipa = ex.get('ipa') or ''
                    ex_pills.append(f'<span class="lesson-pronunciation-example"><strong>{html.escape(str(word))}</strong> {html.escape(str(ipa))}</span>')
            for mp in minimal_pairs:
                if isinstance(mp, dict):
                    w1, p1 = mp.get('w1', ''), mp.get('p1', '')
                    w2, p2 = mp.get('w2', ''), mp.get('p2', '')
                    ex_pills.append(f'<span class="lesson-pronunciation-example">{html.escape(str(w1))} {html.escape(str(p1))} ↔ {html.escape(str(w2))} {html.escape(str(p2))}</span>')
            for ab in alphabet:
                if isinstance(ab, dict):
                    l, ipa = ab.get('l', ''), ab.get('ipa', '')
                    ex_pills.append(f'<span class="lesson-pronunciation-example"><strong>{html.escape(str(l))}</strong> {html.escape(str(ipa))}</span>')

            if ex_pills:
                item_html.append(f'<div class="lesson-pronunciation-examples">{" ".join(ex_pills)}</div>')

            tip = item.get('tip') or item.get('extension')
            if tip:
                item_html.append(f'<div class="lesson-pronunciation-explain"><em>💡 {html.escape(str(tip))}</em></div>')

            pron_items.append(f'<div class="lesson-pronunciation-item">{"".join(item_html)}</div>')

        parts.append(f'<div class="lesson-pronunciation">{"".join(pron_items)}</div>')

    if notes.get('leftover'):
        parts.append(f'<div class="lesson-notes-extra">{html.escape(notes["leftover"])}</div>')

    return "\n".join(parts)

def render_teacher_notes_md(notes):
    lines = []
    if notes.get('code'):
        lines.append(f'- **Lesson Code:** `{notes["code"]}`')
    if notes.get('cando'):
        lines.append(f'- **Goal (Can-Do):** {notes["cando"]}')

    pron = notes.get('pronunciation') or []
    if pron:
        lines.append('- **Pronunciation Focus:**')
        for item in pron:
            if not isinstance(item, dict): continue
            point = item.get('point') or ''
            explain = item.get('explain') or ''
            if point and explain:
                lines.append(f'  - **{point}**: {explain}')
            elif point:
                lines.append(f'  - **{point}**')
            elif explain:
                lines.append(f'  - {explain}')

            examples = item.get('examples') or []
            minimal_pairs = item.get('minimalPairs') or []
            alphabet = item.get('alphabet') or []

            ex_strs = []
            for ex in examples:
                if isinstance(ex, dict):
                    word = ex.get('word') or ex.get('pattern') or ''
                    ipa = ex.get('ipa') or ''
                    if word and ipa:
                        ex_strs.append(f'`{word}` {ipa}')
                    elif word:
                        ex_strs.append(f'`{word}`')
            for mp in minimal_pairs:
                if isinstance(mp, dict):
                    w1, p1 = mp.get('w1', ''), mp.get('p1', '')
                    w2, p2 = mp.get('w2', ''), mp.get('p2', '')
                    ex_strs.append(f'`{w1}` {p1} ↔ `{w2}` {p2}')
            for ab in alphabet:
                if isinstance(ab, dict):
                    l, ipa = ab.get('l', ''), ab.get('ipa', '')
                    ex_strs.append(f'`{l}` {ipa}')

            if ex_strs:
                lines.append(f'    - *Examples:* {", ".join(ex_strs)}')

            tip = item.get('tip') or item.get('extension')
            if tip:
                lines.append(f'    - *Note:* {tip}')

    if notes.get('leftover'):
        lines.append('- **Notes:**')
        for lo_line in notes['leftover'].splitlines():
            if lo_line.strip():
                lines.append(f'  - {lo_line.strip()}')

    return '\n'.join(lines)


def generate_grammar_manual(curriculum_data):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en")
    course_type = str(curriculum_data.get("course_type") or "general")
    level = str(curriculum_data.get("level") or "A1")
    units = curriculum_data.get("units")
    if not isinstance(units, list):
        units = []

    lines = []
    lines.append(f"# {lang.upper()} Grammar Manual — {course_type.title()} ({level.upper()})")
    lines.append("")
    lines.append("> **Derived Manual Document**: Extracted automatically from COSYplatform curriculum source dataset. Do not hand-edit directly.")
    lines.append("")

    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_num = unit.get("unit", "")
        unit_title = str(unit.get("title") or "")
        lines.append(f"## Unit {unit_num}: {unit_title}")
        lines.append("")

        lessons = unit.get("lessons")
        if not isinstance(lessons, list):
            lessons = []

        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            les_num = lesson.get("lesson", "")
            les_title = str(lesson.get("title") or "")
            grammar_list = lesson.get("grammar")
            if not isinstance(grammar_list, list):
                grammar_list = []

            lines.append(f"### Lesson {les_num}: {les_title}")
            lines.append("")
            if grammar_list:
                lines.append("**Grammar Focus Points:**")
                for item in grammar_list:
                    if item:
                        lines.append(f"- {item}")
                lines.append("")

            teacher_notes = lesson.get("teacher_notes")
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                rendered_notes = render_teacher_notes_md(notes)
                if rendered_notes:
                    lines.append("**Teaching Notes & Rules:**")
                    lines.append(rendered_notes)
                    lines.append("")

    return "\n".join(lines)


def generate_grammar_html(curriculum_data, out_dir=None):
    if not isinstance(curriculum_data, dict): curriculum_data = {}
    lang = str(curriculum_data.get("language") or "en").lower()
    lang_upper = lang.upper()
    course_type = str(curriculum_data.get("course_type") or "general").title()
    level = str(curriculum_data.get("level") or "A1").lower()
    level_upper = level.upper()
    units = curriculum_data.get("units") or []

    if out_dir is None:
        out_dir = os.path.join("manuals", lang, course_type.lower(), level)

    rel_styles = os.path.relpath("shared/styles", out_dir).replace("\\", "/")

    unit_blocks = []
    for unit in units:
        if not isinstance(unit, dict): continue
        unit_num = unit.get("unit", "")
        unit_title = html.escape(str(unit.get("title") or ""))

        lesson_blocks = []
        for lesson in (unit.get("lessons") or []):
            if not isinstance(lesson, dict): continue
            les_num = lesson.get("lesson", "")
            les_title = html.escape(str(lesson.get("title") or ""))
            grammar_list = lesson.get("grammar") or []

            grammar_html = ""
            if grammar_list:
                items_html = "".join([f"<li>{html.escape(str(g))}</li>" for q in grammar_list for g in ([q] if isinstance(q, str) else []) if g])
                if items_html:
                    grammar_html = f"<div style='margin-bottom:12px;'><strong>Grammar Focus Points:</strong><ul style='margin:6px 0 0 20px;'>{items_html}</ul></div>"

            teacher_notes = lesson.get("teacher_notes")
            notes_html = ""
            code_badge = ""
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                if notes.get("code"):
                    code_badge = f' <span class="lesson-code-badge">{html.escape(notes["code"])}</span>'
                notes_html = render_teacher_notes_html(notes)

            lesson_blocks.append(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:14px;">
              <h4 style="margin:0 0 10px; color:#0f172a; font-size:1.1rem;">Lesson {les_num}: {les_title}{code_badge}</h4>
              {grammar_html}
              {notes_html}
            </div>
            """)

        unit_blocks.append(f"""
        <section style="margin-bottom:32px;">
          <h2 style="color:#1c8f56; border-bottom:2px solid #cbd5e1; padding-bottom:6px; font-size:1.5rem;">Unit {unit_num}: {unit_title}</h2>
          {"".join(lesson_blocks)}
        </section>
        """)

    textbook_link = f"../../grammar/{level}/index.html"
    textbook_btn = ""
    if os.path.exists(f"manuals/{lang}/grammar/{level}/index.html"):
        textbook_btn = f'<a href="{textbook_link}" style="background:#1c8f56; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">📚 Open Full Level Textbook & Topic Lessons →</a>'

    return f"""<!DOCTYPE html>
<html lang="en" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_upper} Grammar Manual — {course_type} ({level_upper})</title>
<link rel="stylesheet" href="{rel_styles}/lang-accents.css">
<link rel="stylesheet" href="{rel_styles}/tokens.css">
<link rel="stylesheet" href="{rel_styles}/base.css">
<link rel="stylesheet" href="{rel_styles}/components.css">
<link rel="stylesheet" href="{rel_styles}/layout.css">
</head>
<body>

<main class="container" style="max-width:840px; margin:2.5rem auto; padding:0 1.25rem;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:10px;">
    <a href="index.html" style="color:#1c8f56; text-decoration:none; font-weight:700;">&larr; Back to Student Course Hub</a>
    <a href="grammar.md" style="color:#64748b; text-decoration:none; font-size:0.88rem;">📄 Download Markdown Version</a>
  </div>

  <div class="page-head" style="margin-bottom:2rem;">
    <span class="eyebrow" style="background:#1c8f56; color:#ffffff; font-size:0.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;">
      📖 COSYmanuals · Grammar Reference
    </span>
    <h1 style="font-size:2.2rem; color:#0f172a; margin:0.25rem 0 0.5rem; font-weight:700;">
      {lang_upper} Grammar Manual — {course_type} ({level_upper})
    </h1>
    <p style="font-size:1.05rem; color:#475569; margin:0 0 12px;">
      Complete interactive grammar rules, structural formulas, and teaching notes.
    </p>
    {textbook_btn}
  </div>

  {"".join(unit_blocks)}

  <footer style="text-align:center; color:#94a3b8; font-size:0.85rem; border-top:1px solid #e2e8f0; padding-top:16px; margin-top:32px;">
    &copy; COSYmanuals. Derived Interactive Grammar Textbook.
  </footer>
</main>

</body>
</html>
"""


def generate_vocabulary_manual(curriculum_data):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en")
    course_type = str(curriculum_data.get("course_type") or "general")
    level = str(curriculum_data.get("level") or "A1")
    units = curriculum_data.get("units")
    if not isinstance(units, list):
        units = []

    lines = []
    lines.append(f"# {lang.upper()} Vocabulary Manual — {course_type.title()} ({level.upper()})")
    lines.append("")
    lines.append("> **Derived Manual Document**: Extracted automatically from COSYplatform curriculum source dataset. Do not hand-edit directly.")
    lines.append("")

    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_num = unit.get("unit", "")
        unit_title = str(unit.get("title") or "")
        lines.append(f"## Unit {unit_num}: {unit_title}")
        lines.append("")

        lessons = unit.get("lessons")
        if not isinstance(lessons, list):
            lessons = []

        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            les_num = lesson.get("lesson", "")
            les_title = str(lesson.get("title") or "")
            vocab_list = lesson.get("vocabulary")
            if not isinstance(vocab_list, list):
                vocab_list = []

            lines.append(f"### Lesson {les_num}: {les_title}")
            lines.append("")
            if vocab_list:
                lines.append("**Target Vocabulary:**")
                for item in vocab_list:
                    if item:
                        lines.append(f"- `{item}`")
                lines.append("")

            teacher_notes = lesson.get("teacher_notes")
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                rendered_notes = render_teacher_notes_md(notes)
                if rendered_notes:
                    lines.append("**Teaching Notes & Rules:**")
                    lines.append(rendered_notes)
                    lines.append("")

    return "\n".join(lines)


def generate_vocabulary_html(curriculum_data, out_dir=None):
    if not isinstance(curriculum_data, dict): curriculum_data = {}
    lang = str(curriculum_data.get("language") or "en").lower()
    lang_upper = lang.upper()
    course_type = str(curriculum_data.get("course_type") or "general").title()
    level = str(curriculum_data.get("level") or "A1").lower()
    level_upper = level.upper()
    units = curriculum_data.get("units") or []

    if out_dir is None:
        out_dir = os.path.join("manuals", lang, course_type.lower(), level)

    rel_styles = os.path.relpath("shared/styles", out_dir).replace("\\", "/")

    unit_blocks = []
    for unit in units:
        if not isinstance(unit, dict): continue
        unit_num = unit.get("unit", "")
        unit_title = html.escape(str(unit.get("title") or ""))

        lesson_blocks = []
        for lesson in (unit.get("lessons") or []):
            if not isinstance(lesson, dict): continue
            les_num = lesson.get("lesson", "")
            les_title = html.escape(str(lesson.get("title") or ""))
            vocab_list = lesson.get("vocabulary") or []

            vocab_html = ""
            if vocab_list:
                pills = "".join([f"<span style='background:#f1f5f9; color:#0f172a; padding:4px 10px; border-radius:16px; font-family:monospace; font-weight:600; font-size:0.9rem;'>{html.escape(str(v))}</span> " for v in vocab_list if v])
                if pills:
                    vocab_html = f"<div style='display:flex; flex-wrap:wrap; gap:8px; margin-top:8px;'>{pills}</div>"

            teacher_notes = lesson.get("teacher_notes")
            notes_html = ""
            code_badge = ""
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                if notes.get("code"):
                    code_badge = f' <span class="lesson-code-badge">{html.escape(notes["code"])}</span>'
                notes_html = render_teacher_notes_html(notes)

            lesson_blocks.append(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:14px;">
              <h4 style="margin:0 0 8px; color:#0f172a; font-size:1.1rem;">Lesson {les_num}: {les_title}{code_badge}</h4>
              {vocab_html}
              {notes_html}
            </div>
            """)

        unit_blocks.append(f"""
        <section style="margin-bottom:32px;">
          <h2 style="color:#2563eb; border-bottom:2px solid #cbd5e1; padding-bottom:6px; font-size:1.5rem;">Unit {unit_num}: {unit_title}</h2>
          {"".join(lesson_blocks)}
        </section>
        """)

    textbook_link = f"../../vocabulary/{level}/index.html"
    textbook_btn = ""
    if os.path.exists(f"manuals/{lang}/vocabulary/{level}/index.html"):
        textbook_btn = f'<a href="{textbook_link}" style="background:#2563eb; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">📚 Open Full Level Vocabulary Textbook & Topic Lessons →</a>'

    return f"""<!DOCTYPE html>
<html lang="en" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_upper} Vocabulary Manual — {course_type} ({level_upper})</title>
<link rel="stylesheet" href="{rel_styles}/lang-accents.css">
<link rel="stylesheet" href="{rel_styles}/tokens.css">
<link rel="stylesheet" href="{rel_styles}/base.css">
<link rel="stylesheet" href="{rel_styles}/components.css">
<link rel="stylesheet" href="{rel_styles}/layout.css">
</head>
<body>

<main class="container" style="max-width:840px; margin:2.5rem auto; padding:0 1.25rem;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:10px;">
    <a href="index.html" style="color:#2563eb; text-decoration:none; font-weight:700;">&larr; Back to Student Course Hub</a>
    <a href="vocabulary.md" style="color:#64748b; text-decoration:none; font-size:0.88rem;">📄 Download Markdown Version</a>
  </div>

  <div class="page-head" style="margin-bottom:2rem;">
    <span class="eyebrow" style="background:#2563eb; color:#ffffff; font-size:0.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;">
      🗂️ COSYmanuals · Vocabulary Manual
    </span>
    <h1 style="font-size:2.2rem; color:#0f172a; margin:0.25rem 0 0.5rem; font-weight:700;">
      {lang_upper} Vocabulary Manual — {course_type} ({level_upper})
    </h1>
    <p style="font-size:1.05rem; color:#475569; margin:0 0 12px;">
      Structured thematic word lists, target expressions, and key phrases.
    </p>
    {textbook_btn}
  </div>

  {"".join(unit_blocks)}

  <footer style="text-align:center; color:#94a3b8; font-size:0.85rem; border-top:1px solid #e2e8f0; padding-top:16px; margin-top:32px;">
    &copy; COSYmanuals. Derived Interactive Vocabulary Manual.
  </footer>
</main>

</body>
</html>
"""


def generate_communication_manual(curriculum_data):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en")
    course_type = str(curriculum_data.get("course_type") or "general")
    level = str(curriculum_data.get("level") or "A1")
    units = curriculum_data.get("units")
    if not isinstance(units, list):
        units = []

    lines = []
    lines.append(f"# {lang.upper()} Communication & Practice Manual — {course_type.title()} ({level.upper()})")
    lines.append("")
    lines.append("> **Derived Manual Document**: Extracted automatically from COSYplatform curriculum source dataset. Do not hand-edit directly.")
    lines.append("")

    for unit in units:
        if not isinstance(unit, dict):
            continue
        unit_num = unit.get("unit", "")
        unit_title = str(unit.get("title") or "")
        lines.append(f"## Unit {unit_num}: {unit_title}")
        lines.append("")

        lessons = unit.get("lessons")
        if not isinstance(lessons, list):
            lessons = []

        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            les_num = lesson.get("lesson", "")
            les_title = str(lesson.get("title") or "")

            growing_task = lesson.get("growingTask")
            if not isinstance(growing_task, dict):
                growing_task = {}

            age_adaptation = lesson.get("ageAdaptation")
            if not isinstance(age_adaptation, dict):
                age_adaptation = {}

            lines.append(f"### Lesson {les_num}: {les_title}")
            lines.append("")

            self_portrait = growing_task.get("selfPortrait")
            dialogue = growing_task.get("dialogue")

            has_self_portrait = isinstance(self_portrait, str) and bool(self_portrait.strip())
            has_dialogue = isinstance(dialogue, str) and bool(dialogue.strip())

            if has_self_portrait or has_dialogue:
                lines.append("**Communicative Dialogue & Production Tasks:**")
                lines.append("")
                if has_self_portrait:
                    lines.append(f"- **Self-Portrait**: {self_portrait.strip()}")
                if has_dialogue:
                    lines.append("- **Dialogue Practice**:")
                    lines.append("```text")
                    lines.append(dialogue.strip())
                    lines.append("```")
                lines.append("")

            teacher_notes = lesson.get("teacher_notes")
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                rendered_notes = render_teacher_notes_md(notes)
                if rendered_notes:
                    lines.append("**Teaching Notes & Rules:**")
                    lines.append(rendered_notes)
                    lines.append("")

            valid_adaptations = {
                group: adapt.strip()
                for group, adapt in age_adaptation.items()
                if isinstance(adapt, str) and adapt.strip()
            }

            if valid_adaptations:
                lines.append("**Pedagogical Adaptations:**")
                for group, adaptation in valid_adaptations.items():
                    lines.append(f"- **{str(group).title()}**: {adaptation}")
                lines.append("")

    return "\n".join(lines)


def generate_communication_html(curriculum_data, out_dir=None):
    if not isinstance(curriculum_data, dict): curriculum_data = {}
    lang = str(curriculum_data.get("language") or "en").lower()
    lang_upper = lang.upper()
    course_type = str(curriculum_data.get("course_type") or "general").title()
    level = str(curriculum_data.get("level") or "A1").lower()
    level_upper = level.upper()
    units = curriculum_data.get("units") or []

    if out_dir is None:
        out_dir = os.path.join("manuals", lang, course_type.lower(), level)

    rel_styles = os.path.relpath("shared/styles", out_dir).replace("\\", "/")

    unit_blocks = []
    for unit in units:
        if not isinstance(unit, dict): continue
        unit_num = unit.get("unit", "")
        unit_title = html.escape(str(unit.get("title") or ""))

        lesson_blocks = []
        for lesson in (unit.get("lessons") or []):
            if not isinstance(lesson, dict): continue
            les_num = lesson.get("lesson", "")
            les_title = html.escape(str(lesson.get("title") or ""))
            growing_task = lesson.get("growingTask") or {}
            age_adaptation = lesson.get("ageAdaptation") or {}

            self_portrait = growing_task.get("selfPortrait")
            dialogue = growing_task.get("dialogue")

            comm_html = ""
            if (isinstance(self_portrait, str) and self_portrait.strip()) or (isinstance(dialogue, str) and dialogue.strip()):
                parts = []
                if isinstance(self_portrait, str) and self_portrait.strip():
                    parts.append(f"<p style='margin:0 0 8px;'><strong>Self-Portrait Task:</strong> {html.escape(self_portrait.strip())}</p>")
                if isinstance(dialogue, str) and dialogue.strip():
                    parts.append(f"<div style='background:#f8fafc; border-left:3px solid #4f46e5; padding:10px 14px; font-family:monospace; font-size:0.9rem; border-radius:4px;'>{html.escape(dialogue.strip())}</div>")
                comm_html = f"<div style='margin-bottom:10px;'>{''.join(parts)}</div>"

            teacher_notes = lesson.get("teacher_notes")
            notes_html = ""
            code_badge = ""
            if isinstance(teacher_notes, str) and teacher_notes.strip():
                notes = parse_teacher_notes(teacher_notes)
                if notes.get("code"):
                    code_badge = f' <span class="lesson-code-badge">{html.escape(notes["code"])}</span>'
                notes_html = render_teacher_notes_html(notes)

            adapt_html = ""
            valid_adaptations = {g: a.strip() for g, a in age_adaptation.items() if isinstance(a, str) and a.strip()}
            if valid_adaptations:
                adapt_items = "".join([f"<li><strong>{html.escape(str(g)).title()}:</strong> {html.escape(a)}</li>" for g, a in valid_adaptations.items()])
                adapt_html = f"<div style='font-size:0.88rem; color:#475569;'><strong>Age Adaptations:</strong><ul style='margin:4px 0 0 20px;'>{adapt_items}</ul></div>"

            lesson_blocks.append(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:16px; margin-bottom:14px;">
              <h4 style="margin:0 0 10px; color:#0f172a; font-size:1.1rem;">Lesson {les_num}: {les_title}{code_badge}</h4>
              {comm_html}
              {notes_html}
              {adapt_html}
            </div>
            """)

        unit_blocks.append(f"""
        <section style="margin-bottom:32px;">
          <h2 style="color:#4f46e5; border-bottom:2px solid #cbd5e1; padding-bottom:6px; font-size:1.5rem;">Unit {unit_num}: {unit_title}</h2>
          {"".join(lesson_blocks)}
        </section>
        """)

    textbook_link = f"../../communication/{level}/index.html"
    textbook_btn = ""
    if os.path.exists(f"manuals/{lang}/communication/{level}/index.html"):
        textbook_btn = f'<a href="{textbook_link}" style="background:#4f46e5; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">📚 Open Full Level Communication Textbook & Topic Lessons →</a>'

    return f"""<!DOCTYPE html>
<html lang="en" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_upper} Communication Manual — {course_type} ({level_upper})</title>
<link rel="stylesheet" href="{rel_styles}/lang-accents.css">
<link rel="stylesheet" href="{rel_styles}/tokens.css">
<link rel="stylesheet" href="{rel_styles}/base.css">
<link rel="stylesheet" href="{rel_styles}/components.css">
<link rel="stylesheet" href="{rel_styles}/layout.css">
</head>
<body>

<main class="container" style="max-width:840px; margin:2.5rem auto; padding:0 1.25rem;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; flex-wrap:wrap; gap:10px;">
    <a href="index.html" style="color:#4f46e5; text-decoration:none; font-weight:700;">&larr; Back to Student Course Hub</a>
    <a href="communication.md" style="color:#64748b; text-decoration:none; font-size:0.88rem;">📄 Download Markdown Version</a>
  </div>

  <div class="page-head" style="margin-bottom:2rem;">
    <span class="eyebrow" style="background:#4f46e5; color:#ffffff; font-size:0.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;">
      💬 COSYmanuals · Communication & Practice
    </span>
    <h1 style="font-size:2.2rem; color:#0f172a; margin:0.25rem 0 0.5rem; font-weight:700;">
      {lang_upper} Communication Manual — {course_type} ({level_upper})
    </h1>
    <p style="font-size:1.05rem; color:#475569; margin:0 0 12px;">
      Interactive dialogues, production tasks, and pedagogical adaptations.
    </p>
    {textbook_btn}
  </div>

  {"".join(unit_blocks)}

  <footer style="text-align:center; color:#94a3b8; font-size:0.85rem; border-top:1px solid #e2e8f0; padding-top:16px; margin-top:32px;">
    &copy; COSYmanuals. Derived Interactive Communication Manual.
  </footer>
</main>

</body>
</html>
"""


def generate_readme(curriculum_data):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en")
    course_type = str(curriculum_data.get("course_type") or "general")
    level = str(curriculum_data.get("level") or "A1")

    lines = []
    lines.append(f"# {lang.upper()} {course_type.title()} Manual ({level.upper()})")
    lines.append("")
    lines.append(f"This folder contains derived lesson manuals for **{lang.upper()} - {course_type.title()} - {level.upper()}**.")
    lines.append("")
    lines.append("## Available Manual Documents")
    lines.append("- 📖 [`grammar.html`](./grammar.html) / [`grammar.md`](./grammar.md) - Grammar rules, explanations, and structures.")
    lines.append("- 🗂️ [`vocabulary.html`](./vocabulary.html) / [`vocabulary.md`](./vocabulary.md) - Thematic vocabulary lists and key phrases.")
    lines.append("- 💬 [`communication.html`](./communication.html) / [`communication.md`](./communication.md) - Communicative tasks, dialogues, and adaptations.")
    lines.append("")
    lines.append("---")
    lines.append("*Generated automatically by `scripts/extract_manuals.py` from COSYplatform curriculum files.*")
    return "\n".join(lines)


def generate_student_index(curriculum_data, out_dir=None):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en").lower()
    lang_upper = lang.upper()
    course_type = str(curriculum_data.get("course_type") or "general").title()
    level = str(curriculum_data.get("level") or "a1").lower()
    level_upper = level.upper()

    if out_dir is None:
        out_dir = os.path.join("manuals", lang, course_type.lower(), level)

    rel_styles = os.path.relpath("shared/styles", out_dir).replace("\\", "/")

    # Check for direct textbook links
    grammar_tb = f"../../grammar/{level}/index.html" if os.path.exists(f"manuals/{lang}/grammar/{level}/index.html") else None
    vocab_tb = f"../../vocabulary/{level}/index.html" if os.path.exists(f"manuals/{lang}/vocabulary/{level}/index.html") else None
    comm_tb = f"../../communication/{level}/index.html" if os.path.exists(f"manuals/{lang}/communication/{level}/index.html") else None
    print_hub = f"../../print/index.html" if os.path.exists(f"manuals/{lang}/print/index.html") else None

    tb_links_html = ""
    if grammar_tb or vocab_tb or comm_tb or print_hub:
        extra_btns = []
        if grammar_tb:
          extra_btns.append(f'<a href="{grammar_tb}" style="display:inline-block; background:#1c8f56; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">📘 Open Full Grammar Textbook Hub →</a>')
        if vocab_tb:
          extra_btns.append(f'<a href="{vocab_tb}" style="display:inline-block; background:#2563eb; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">📚 Open Full Vocabulary Textbook Hub →</a>')
        if comm_tb:
          extra_btns.append(f'<a href="{comm_tb}" style="display:inline-block; background:#4f46e5; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">💬 Open Communication Hub →</a>')
        if print_hub:
          extra_btns.append(f'<a href="{print_hub}" style="display:inline-block; background:#0f172a; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">🖨️ Printable A4 Booklet Edition →</a>')

        tb_links_html = f"""
        <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:18px; margin-bottom:28px;">
          <h3 style="margin-top:0; color:#1e293b; font-size:1.15rem;">📚 Full Interactive Level Textbooks & Lesson Pages:</h3>
          <p style="font-size:0.9rem; color:#64748b; margin-bottom:12px;">Access the complete, topic-by-topic interactive textbooks for {lang_upper} {level_upper}:</p>
          <div style="display:flex; flex-wrap:wrap; gap:10px;">
            {"".join(extra_btns)}
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang_upper} {course_type} Manual ({level_upper}) · Student Portal</title>
<link rel="stylesheet" href="{rel_styles}/lang-accents.css">
<link rel="stylesheet" href="{rel_styles}/tokens.css">
<link rel="stylesheet" href="{rel_styles}/base.css">
<link rel="stylesheet" href="{rel_styles}/components.css">
<link rel="stylesheet" href="{rel_styles}/layout.css">
</head>
<body>

<main class="container" style="max-width:800px; margin:2.5rem auto; padding:0 1.25rem;">
  <div class="page-head" style="margin-bottom:1.5rem;">
    <span class="eyebrow" style="background:#e2e8f0; font-size:0.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;">
      🎓 Student Course Manuals · {lang_upper}
    </span>
    <h1 style="font-size:2.2rem; color:#1e293b; margin:0.25rem 0 0.5rem; font-weight:700;">
      {lang_upper} {course_type} Course ({level_upper})
    </h1>
    <p style="font-size:1.05rem; color:#475569; margin:0;">
      Welcome to your course manual directory. Below you can access your core study manuals, topic lesson pages, and print editions for this level.
    </p>
  </div>

  <div class="box outcome-banner" style="background:#f4fbf7; border-left:4px solid #1c8f56; padding:14px 18px; margin-bottom:24px; border-radius:6px;">
    <strong>🎯 Student Direct Access:</strong> Keep this link saved for your live lessons and homework. Your teacher will assign specific sections from these manuals.
  </div>

  {tb_links_html}

  <h3 style="color:#0f172a; margin-bottom:12px; font-size:1.25rem;">📖 Derived Course Manuals ({level_upper}):</h3>
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:32px;">
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #1c8f56;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">📖 Grammar</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Grammar rules, sentence formulas, and structural explanations.</p>
      <a href="grammar.html" style="display:inline-block; background:#1c8f56; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Grammar Manual →</a>
    </div>

    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #2563eb;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">🗂️ Vocabulary</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Thematic word lists, key phrases, and target expressions.</p>
      <a href="vocabulary.html" style="display:inline-block; background:#2563eb; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Vocabulary Manual →</a>
    </div>

    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #4f46e5;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">💬 Communication</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Dialogues, speaking tasks, and interactive prompts.</p>
      <a href="communication.html" style="display:inline-block; background:#4f46e5; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Communication Manual →</a>
    </div>
  </div>

  <footer style="text-align:center; color:#94a3b8; font-size:0.85rem; border-top:1px solid #e2e8f0; padding-top:16px;">
    &copy; COSYmanuals. Direct Student Course Resource.
  </footer>
</main>

</body>
</html>
"""


def process_curriculum_file(filepath):
    path = Path(filepath)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, dict):
        print(f"Skipping {filepath}: Root is not a dict JSON object.")
        return

    lang = data.get("language")
    course_type = data.get("course_type")
    level = data.get("level")

    if not lang or not course_type or not level:
        print(f"Skipping {filepath}: Missing language, course_type, or level metadata.")
        return

    out_dir = Path("manuals") / str(lang) / str(course_type) / str(level).lower()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write Grammar Manual (.md and .html)
    grammar_content = generate_grammar_manual(data)
    with open(out_dir / "grammar.md", "w", encoding="utf-8") as f:
        f.write(grammar_content)

    grammar_html_content = generate_grammar_html(data)
    with open(out_dir / "grammar.html", "w", encoding="utf-8") as f:
        f.write(grammar_html_content)

    # Write Vocabulary Manual (.md and .html)
    vocab_content = generate_vocabulary_manual(data)
    with open(out_dir / "vocabulary.md", "w", encoding="utf-8") as f:
        f.write(vocab_content)

    vocab_html_content = generate_vocabulary_html(data)
    with open(out_dir / "vocabulary.html", "w", encoding="utf-8") as f:
        f.write(vocab_html_content)

    # Write Communication Manual (.md and .html)
    comm_content = generate_communication_manual(data)
    with open(out_dir / "communication.md", "w", encoding="utf-8") as f:
        f.write(comm_content)

    comm_html_content = generate_communication_html(data)
    with open(out_dir / "communication.html", "w", encoding="utf-8") as f:
        f.write(comm_html_content)

    # Write README
    readme_content = generate_readme(data)
    with open(out_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Write Student Index HTML
    student_index_content = generate_student_index(data)
    with open(out_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(student_index_content)

    print(f"Successfully generated manuals in: {out_dir}")


def main():
    curriculum_base = Path("curriculums")
    json_files = list(curriculum_base.glob("**/*.json"))

    # Filter out schema or archive files
    valid_files = [f for f in json_files if "_schema" not in str(f) and "_archive" not in str(f)]

    print(f"Found {len(valid_files)} curriculum JSON files to extract.")
    for file in valid_files:
        try:
            process_curriculum_file(file)
        except Exception as e:
            print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    main()
