# French Curriculum Reconciliation & Audit Report

**Date:** September 11, 2026
**Target Directories & Files:**
- `curriculums/french/` (Legacy language-name folder structure)
- `curriculums/fr/` (Canonical ISO-JSON structure)

---

## 1. Executive Summary

An audit of the legacy language-name folder `curriculums/french/` was conducted to evaluate whether any unit content exists that needs reconciliation with the canonical ISO-JSON curriculum structure in `curriculums/fr/`.

`curriculums/french/` contains six level subdirectories (`beginner-a1`, `elementary-a2`, `intermediate-b1`, `upper-intermediate-b2`, `advanced-c1`, `professor-c2`), all of which contain only `.gitkeep` files. No HTML unit files, lesson plans, or text content exist in the `french/` tree.

Conversely, `curriculums/fr/` contains fully populated, schema-validated JSON curriculum files across four course tracks (`general`, `spoken`, `travelling`, `professional`) covering CEFR levels A1 through C2.

**Final Recommendation:** Option **(b) Archive `curriculums/french/` as superseded** by `curriculums/fr/`.

---

## 2. Comparison Matrix

| Feature / Dimension | Legacy `curriculums/french/` | Canonical `curriculums/fr/` (ISO-JSON) | Comparison & Alignment Notes |
|---|---|---|---|
| **Directory Architecture** | Folder per level slug (`beginner-a1`, `intermediate-b1`, etc.) | ISO language code + course track (`fr/general/`, `fr/spoken/`, etc.) | ISO-JSON structure supports multi-track courses. |
| **Real Content Count** | 0 content files (only `.gitkeep` files) | Multiple populated `.json` files | Legacy structure is entirely empty. |
| **CEFR Levels Covered** | None (empty folders) | A1, A2, B1, B2, C1, C2 fully populated | ISO-JSON provides complete active level coverage. |
| **Course Tracks** | Unspecified | General, Spoken, Travelling, Professional | ISO-JSON covers multiple tracks. |
| **Schema Validation** | None | Validated against `curriculum.schema.json` | ISO-JSON integrates with repo validation tooling. |

---

## 3. Detailed Comparison & Pedagogical Evaluation

### 3.1 Content Analysis of `curriculums/french/`
- Directory tree:
  - `curriculums/french/.gitkeep`
  - `curriculums/french/beginner-a1/.gitkeep`
  - `curriculums/french/elementary-a2/.gitkeep`
  - `curriculums/french/intermediate-b1/.gitkeep`
  - `curriculums/french/upper-intermediate-b2/.gitkeep`
  - `curriculums/french/advanced-c1/.gitkeep`
  - `curriculums/french/professor-c2/.gitkeep`
- No `.html`, `.json`, `.js`, or `.md` content files exist in any of these folders.

### 3.2 Comparison with ISO-JSON (`curriculums/fr/`)
- `curriculums/fr/` holds complete, schema-compliant JSON files:
  - `fr/general/`: `A1.json`, `A2.json`, `B1.json`, `B2.json`, `C1.json`, `C2.json`
  - `fr/spoken/`: `A1.json` through `C2.json`
  - `fr/travelling/`: `A1.json`, `A2.json`, `B1.json`
  - `fr/professional/`: `B1.json`, `B2.json`, `C1.json`, `C2.json`
- All lessons contain rich metadata, grammar structures, target vocabulary lists, duration, and teacher notes.

---

## 4. Recommendation & Action Proposal

**Recommendation:** **(b) Archive `curriculums/french/` as superseded.**

### Rationale:
1. The `curriculums/french/` folder contains no unique or real content.
2. The canonical ISO-JSON structure `curriculums/fr/` is fully populated, standardized, and validated against the repository curriculum schema.

---

## 5. File Status & Integrity Confirmation

- **`curriculums/french/`**: Left **UNTOUCHED** (audit only).
- **`curriculums/fr/`**: Left **UNTOUCHED**.
- **`curriculums/_archive/french_RECONCILIATION.md`**: Created for review.
