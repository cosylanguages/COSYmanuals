# Greek Curriculum Reconciliation & Audit Report

**Date:** September 11, 2026
**Target Directories & Files:**
- `curriculums/greek/` (Legacy language-name folder structure)
- `curriculums/el/` (Canonical ISO-JSON structure)

---

## 1. Executive Summary

An audit of the legacy language-name folder `curriculums/greek/` was conducted to evaluate whether any unit content exists that needs reconciliation with the canonical ISO-JSON curriculum structure in `curriculums/el/`.

`curriculums/greek/` contains only a `.gitkeep` file. No level subdirectories, HTML unit files, lesson plans, or text content exist in the `greek/` tree.

Conversely, `curriculums/el/` contains schema-validated JSON curriculum dataset files (such as `el/general/A1.json`).

**Final Recommendation:** Option **(b) Archive `curriculums/greek/` as superseded** by `curriculums/el/`.

---

## 2. Comparison Matrix

| Feature / Dimension | Legacy `curriculums/greek/` | Canonical `curriculums/el/` (ISO-JSON) | Comparison & Alignment Notes |
|---|---|---|---|
| **Directory Architecture** | Flat legacy folder `curriculums/greek/` | ISO language code + course track (`el/general/`) | ISO-JSON structure supports multi-track courses. |
| **Real Content Count** | 0 content files (only `.gitkeep`) | Validated JSON files (`A1.json`) | Legacy structure is entirely empty. |
| **CEFR Levels Covered** | None | Active CEFR level datasets in `el/general/` | ISO-JSON provides active level coverage. |
| **Schema Validation** | None | Validated against `curriculum.schema.json` | ISO-JSON integrates with repo validation tooling. |

---

## 3. Detailed Comparison & Pedagogical Evaluation

### 3.1 Content Analysis of `curriculums/greek/`
- Directory tree:
  - `curriculums/greek/.gitkeep`
- No `.html`, `.json`, `.js`, or `.md` content files exist in `curriculums/greek/`.

### 3.2 Comparison with ISO-JSON (`curriculums/el/`)
- `curriculums/el/` holds schema-compliant JSON files (e.g., `el/general/A1.json`) containing rich metadata, grammar structures, target vocabulary lists, duration, and teacher notes.

---

## 4. Recommendation & Action Proposal

**Recommendation:** **(b) Archive `curriculums/greek/` as superseded.**

### Rationale:
1. The `curriculums/greek/` folder contains no unique or real content.
2. The canonical ISO-JSON structure `curriculums/el/` is standardized and validated against the repository curriculum schema.

---

## 5. File Status & Integrity Confirmation

- **`curriculums/greek/`**: Left **UNTOUCHED** (audit only).
- **`curriculums/el/`**: Left **UNTOUCHED**.
- **`curriculums/_archive/greek_RECONCILIATION.md`**: Created for review.
