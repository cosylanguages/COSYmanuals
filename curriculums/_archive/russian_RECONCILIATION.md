# Russian Curriculum Reconciliation & Audit Report

**Date:** September 11, 2026
**Target Directories & Files:**
- `curriculums/russian/` (Legacy language-name folder structure)
- `curriculums/ru/` (Canonical ISO-JSON structure)

---

## 1. Executive Summary

An audit of the legacy language-name folder `curriculums/russian/` was conducted to evaluate whether any unit content exists that needs reconciliation with the canonical ISO-JSON curriculum structure in `curriculums/ru/`.

`curriculums/russian/` contains only a `.gitkeep` file. No level subdirectories, HTML unit files, lesson plans, or text content exist in the `russian/` tree.

Conversely, `curriculums/ru/` contains fully populated, schema-validated JSON curriculum files across four course tracks (`general`, `spoken`, `travelling`, `professional`) covering CEFR levels A1 through C2.

**Final Recommendation:** Option **(b) Archive `curriculums/russian/` as superseded** by `curriculums/ru/`.

---

## 2. Comparison Matrix

| Feature / Dimension | Legacy `curriculums/russian/` | Canonical `curriculums/ru/` (ISO-JSON) | Comparison & Alignment Notes |
|---|---|---|---|
| **Directory Architecture** | Flat legacy folder `curriculums/russian/` | ISO language code + course track (`ru/general/`, `ru/spoken/`, etc.) | ISO-JSON structure supports multi-track courses. |
| **Real Content Count** | 0 content files (only `.gitkeep`) | Multiple populated `.json` files | Legacy structure is entirely empty. |
| **CEFR Levels Covered** | None | A1, A2, B1, B2, C1, C2 fully populated | ISO-JSON provides complete active level coverage. |
| **Course Tracks** | Unspecified | General, Spoken, Travelling, Professional | ISO-JSON covers multiple tracks. |
| **Schema Validation** | None | Validated against `curriculum.schema.json` | ISO-JSON integrates with repo validation tooling. |

---

## 3. Detailed Comparison & Pedagogical Evaluation

### 3.1 Content Analysis of `curriculums/russian/`
- Directory tree:
  - `curriculums/russian/.gitkeep`
- No `.html`, `.json`, `.js`, or `.md` content files exist in `curriculums/russian/`.

### 3.2 Comparison with ISO-JSON (`curriculums/ru/`)
- `curriculums/ru/` holds complete, schema-compliant JSON files:
  - `ru/general/`: `A1.json`, `A2.json`, `B1.json`, `B2.json`, `C1.json`, `C2.json`
  - `ru/spoken/`: `A1.json` through `C2.json`
  - `ru/travelling/`: `A1.json`, `A2.json`, `B1.json`
  - `ru/professional/`: `B1.json`, `B2.json`, `C1.json`, `C2.json`
- All lessons contain rich metadata, grammar structures, target vocabulary lists, duration, and teacher notes.

---

## 4. Recommendation & Action Proposal

**Recommendation:** **(b) Archive `curriculums/russian/` as superseded.**

### Rationale:
1. The `curriculums/russian/` folder contains no unique or real content.
2. The canonical ISO-JSON structure `curriculums/ru/` is fully populated, standardized, and validated against the repository curriculum schema.

---

## 5. File Status & Integrity Confirmation

- **`curriculums/russian/`**: Left **UNTOUCHED** (audit only).
- **`curriculums/ru/`**: Left **UNTOUCHED**.
- **`curriculums/_archive/russian_RECONCILIATION.md`**: Created for review.
