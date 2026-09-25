#!/usr/bin/env python3
"""
COSYmanuals Extraction Pipeline
-------------------------------
Extracts COSYplatform curriculum JSON datasets from `curriculums/<lang>/<course_type>/<level>.json`
and produces derived, plain, versionable Markdown manual documents & student index HTML under:
  manuals/<lang>/<course_type>/<level>/
    ├── grammar.md
    ├── vocabulary.md
    ├── communication.md
    ├── README.md
    └── index.html
"""

import json
import os
import sys
from pathlib import Path

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
                lines.append("**Teaching Notes & Rules:**")
                lines.append("```text")
                lines.append(teacher_notes.strip())
                lines.append("```")
                lines.append("")

    return "\n".join(lines)


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

    return "\n".join(lines)


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
    lines.append("- 📖 [`grammar.md`](./grammar.md) - Grammar rules, explanations, and structures.")
    lines.append("- 🗂️ [`vocabulary.md`](./vocabulary.md) - Thematic vocabulary lists and key phrases.")
    lines.append("- 💬 [`communication.md`](./communication.md) - Communicative tasks, dialogues, and adaptations.")
    lines.append("")
    lines.append("---")
    lines.append("*Generated automatically by `scripts/extract_manuals.py` from COSYplatform curriculum files.*")
    return "\n".join(lines)


def generate_student_index(curriculum_data):
    if not isinstance(curriculum_data, dict):
        curriculum_data = {}

    lang = str(curriculum_data.get("language") or "en").upper()
    course_type = str(curriculum_data.get("course_type") or "general").title()
    level = str(curriculum_data.get("level") or "A1").upper()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lang} {course_type} Manual ({level}) · Student Portal</title>
<link rel="stylesheet" href="../../../shared/styles/tokens.css">
<link rel="stylesheet" href="../../../shared/styles/base.css">
<link rel="stylesheet" href="../../../shared/styles/components.css">
<link rel="stylesheet" href="../../../shared/styles/layout.css">
</head>
<body>

<main class="container" style="max-width:760px; margin:2.5rem auto; padding:0 1.25rem;">
  <div class="page-head" style="margin-bottom:1.5rem;">
    <span class="eyebrow" style="background:#e2e8f0; font-size:0.85rem; padding:4px 10px; border-radius:4px; font-weight:700; display:inline-block; margin-bottom:8px;">
      🎓 Student Course Manuals · {lang}
    </span>
    <h1 style="font-size:2.2rem; color:#1e293b; margin:0.25rem 0 0.5rem; font-weight:700;">
      {lang} {course_type} Course ({level})
    </h1>
    <p style="font-size:1.05rem; color:#475569; margin:0;">
      Welcome to your course manual directory. Below you can access your 3 core study manuals for this level.
    </p>
  </div>

  <div class="box outcome-banner" style="background:#f4fbf7; border-left:4px solid #1c8f56; padding:14px 18px; margin-bottom:24px; border-radius:6px;">
    <strong>🎯 Student Direct Access:</strong> Keep this link saved for your live lessons and homework. Your teacher will assign specific sections from these manuals.
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:32px;">
    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #1c8f56;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">📖 Grammar</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Grammar rules, sentence formulas, and structural explanations.</p>
      <a href="grammar.md" style="display:inline-block; background:#1c8f56; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Grammar Manual →</a>
    </div>

    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #2563eb;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">🗂️ Vocabulary</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Thematic word lists, key phrases, and target expressions.</p>
      <a href="vocabulary.md" style="display:inline-block; background:#2563eb; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Vocabulary Manual →</a>
    </div>

    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:18px; border-top:4px solid #4f46e5;">
      <h3 style="margin-top:0; color:#1e293b; font-size:1.2rem;">💬 Communication</h3>
      <p style="font-size:0.9rem; color:#64748b; margin-bottom:14px;">Dialogues, speaking tasks, and interactive prompts.</p>
      <a href="communication.md" style="display:inline-block; background:#4f46e5; color:#ffffff; font-weight:700; padding:8px 14px; border-radius:6px; text-decoration:none; font-size:0.9rem;">Open Communication Manual →</a>
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

    # Write Grammar Manual
    grammar_content = generate_grammar_manual(data)
    with open(out_dir / "grammar.md", "w", encoding="utf-8") as f:
        f.write(grammar_content)

    # Write Vocabulary Manual
    vocab_content = generate_vocabulary_manual(data)
    with open(out_dir / "vocabulary.md", "w", encoding="utf-8") as f:
        f.write(vocab_content)

    # Write Communication Manual
    comm_content = generate_communication_manual(data)
    with open(out_dir / "communication.md", "w", encoding="utf-8") as f:
        f.write(comm_content)

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
