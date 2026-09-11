# English Curriculum Reconciliation & Audit Report

**Date:** September 11, 2026
**Target Directories & Files:**
- `curriculums/english/` (Legacy language-name folder structure)
- `curriculums/english/intermediate-b1/index.html` & `unit-1.html` (Legacy HTML manual pages)
- `curriculums/en/general/B1.json` (Canonical ISO-JSON B1 dataset)
- `curriculums/en/general/A2.json` (Canonical ISO-JSON A2 dataset)

---

## 1. Executive Summary

An audit of the legacy language-name folder `curriculums/english/` was conducted to evaluate its contents against the canonical ISO-JSON curriculum structure in `curriculums/en/`.

`curriculums/english/` contains five empty level subdirectories (`beginner-a1`, `elementary-a2`, `upper-intermediate-b2`, `advanced-c1`, `professor-c2`) holding only `.gitkeep` files. The only subdirectory with real content is `english/intermediate-b1/`, which contains `index.html` (a 12-unit syllabus overview where Units 2–12 are locked placeholders) and `unit-1.html` (Unit 1: Life Stories & Past Memories).

A comparative analysis shows that `curriculums/en/general/B1.json` provides a far more complete, schema-validated, 10-unit / 20-lesson B1 curriculum. Furthermore, the single implemented HTML lesson in `unit-1.html` ("Past Simple vs. Past Continuous") is calibrated to CEFR A2 level in the ISO-JSON system (`curriculums/en/general/A2.json`, Lesson `EN-A2-001`).

**Final Recommendation:** Option **(b) Archive `curriculums/english/` as superseded** by `curriculums/en/`. Optionally, extract specific vocabulary items from `unit-1.html` (`Nostalgia`, `Reminisce`) into the ISO-JSON datasets during a future content pass.

---

## 2. Comparison Matrix

| Feature / Dimension | Legacy `curriculums/english/` (HTML) | Canonical `curriculums/en/` (ISO-JSON) | Comparison & Alignment Notes |
|---|---|---|---|
| **Directory Architecture** | Folder per level slug (`beginner-a1`, `intermediate-b1`, etc.) | ISO language code + course track (`en/general/`, `en/spoken/`, etc.) | ISO-JSON structure supports multi-track courses (general, spoken, exam, professional, travelling, relocation). |
| **Level Coverage** | 6 level folders, 5 completely empty (`.gitkeep` only) | 6 CEFR levels (A1–C2) fully populated across multiple tracks | ISO-JSON structure provides 100% active level coverage. |
| **Unit Count (B1)** | 12 units defined in `index.html` (11 locked placeholders) | 10 thematic units in `en/general/B1.json` | ISO-JSON has 10 complete units; HTML has only 1 working unit. |
| **Lesson Count (B1)** | 1 implemented lesson page (`unit-1.html`) | 20 fully populated 60–90 min lessons | ISO-JSON contains 20 schema-validated lessons. |
| **Grammar Calibration** | Unit 1 teaches **Past Simple vs. Past Continuous** | B1 starts at **Present Perfect Continuous**; Past Simple/Continuous is in **A2 (`A2.json`)** | HTML Unit 1 grammar is CEFR A2 level, already captured in `en/general/A2.json` (`EN-A2-001`). |
| **Vocabulary Items** | 4 items in Unit 1 (`Nostalgia`, `Milestone`, `Upbringing`, `Reminisce`) | 200+ B1 target words (10 per lesson) across `B1.json` | `Milestone` and `Upbringing` exist in `A2.json`. `Nostalgia` and `Reminisce` are uncaptured B1 items. |
| **Metadata & Tooling** | Static HTML markup with external links | Rich JSON validated against `curriculum.schema.json` (IPA, can-do, recycled grammar) | ISO-JSON integrates directly with automated test suites and schema validation. |

---

## 3. Detailed Comparison & Pedagogical Evaluation

### 3.1 Content Analysis of `english/intermediate-b1/`
- **`index.html`**: Serves as a course landing page outlining a 12-week (48-hour) B1 Intermediate syllabus. However, Units 2 through 12 are marked as `"Locked"` with non-functional anchor tags (`href="#"`).
- **`unit-1.html`**: Titled *"Unit 1: Life Stories & Past Memories"*. Contains:
  - **Objectives:** Contrast Past Simple vs. Past Continuous; expand life milestone vocabulary; deliver a personal narrative.
  - **Vocabulary:** *Nostalgia*, *Milestone*, *Upbringing*, *Reminisce*.
  - **Grammar Focus:** Past Simple vs. Past Continuous contrast with an example sentence ("I was walking home when I met an old friend").
  - **Exercises:** Warm-up prompt, roleplay activity, mini-game links, homework assignment (150-word journal entry), and self-assessment checklist.

### 3.2 Comparison with ISO-JSON (`en/general/B1.json` & `A2.json`)
1. **CEFR Grammar Level Placement:**
   - In `unit-1.html`, the core grammar structure taught is **Past Simple vs. Past Continuous**.
   - In the ISO-JSON architecture, Past Simple vs. Past Continuous is categorized under **CEFR A2** in `curriculums/en/general/A2.json` (Unit 1, Lesson 1: *"Past Simple vs Past Continuous"*, Code `EN-A2-001`).
   - In `curriculums/en/general/B1.json`, B1 grammar begins at higher intermediate level: Unit 1 covers *Present Perfect Continuous vs Simple* (`EN-B1-001`) and *Modals of Deduction* (`EN-B1-002`). Past narrative tenses appear in Unit 2 as *Past Perfect Simple / Continuous* (`EN-B1-003`).

2. **Vocabulary Overlap & Uncaptured Items:**
   - **Captured in ISO-JSON:** `Milestone` and `Upbringing` are already listed as target vocabulary in `curriculums/en/general/A2.json` (Unit 1 Lessons 1–2).
   - **Uncaptured in ISO-JSON:** `Nostalgia` and `Reminisce` do not appear in `A2.json` or `B1.json`. They represent valid B1 vocabulary items that could be added to `en/general/B1.json` Unit 1 vocabulary.

3. **Curriculum Completeness:**
   - `english/intermediate-b1/` contains only 1 working HTML page out of 12 planned units.
   - `en/general/B1.json` contains 10 complete units, 20 detailed lesson objects with IPA pronunciation notes, can-do statements, recycled grammar links, and teacher instructions.

---

## 4. Recommendation & Action Proposal

**Recommendation:** **(b) Archive `curriculums/english/` as superseded.**

### Rationale:
1. The language-name structure `curriculums/english/` is obsolete and mostly empty (5 of 6 level directories contain only `.gitkeep`).
2. The canonical ISO-JSON structure in `curriculums/en/` is fully populated across 6 CEFR levels (A1–C2) and 6 course tracks, fully validated by `curriculum.schema.json`.
3. The single implemented HTML unit (`english/intermediate-b1/unit-1.html`) covers A2-level grammar already captured in `curriculums/en/general/A2.json`.

### Optional Extraction Plan (For Future Content Pass):
If desired prior to archiving:
- Add `"Nostalgia"` and `"Reminisce"` to the vocabulary array of `curriculums/en/general/B1.json` (Unit 1, Lesson 1) or `A2.json` (Unit 1, Lesson 1).
- No new lesson objects need to be created in JSON, as all grammar topics from `unit-1.html` already exist in the ISO-JSON dataset.

---

## 5. File Status & Integrity Confirmation

- **`curriculums/english/`**: Left **UNTOUCHED** (audit only).
- **`curriculums/en/general/B1.json`**: Left **UNTOUCHED**.
- **`curriculums/en/general/A2.json`**: Left **UNTOUCHED**.
- **`curriculums/_archive/english_RECONCILIATION.md`**: Created for review.
