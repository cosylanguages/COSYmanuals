# Italian Curriculum Reconciliation & Audit Report

**Date:** September 11, 2026
**Target Directories & Files:**
- `curriculums/italian/` (Legacy language-name folder structure)
- `curriculums/it/` (Canonical ISO-JSON structure)

---

## 1. Executive Summary

An audit of the legacy language-name folder `curriculums/italian/` was conducted to evaluate whether any unit content exists that needs reconciliation with the canonical ISO-JSON curriculum structure in `curriculums/it/`.

`curriculums/italian/` contains only a `.gitkeep` file. No level subdirectories, HTML unit files, lesson plans, or text content exist in the `italian/` tree.

Conversely, `curriculums/it/` contains schema-validated JSON curriculum dataset files (such as `it/general/A1.json`).

**Final Recommendation:** Option **(b) Archive `curriculums/italian/` as superseded** by `curriculums/it/`.

---

## 2. Comparison Matrix

| Feature / Dimension | Legacy `curriculums/italian/` | Canonical `curriculums/it/` (ISO-JSON) | Comparison & Alignment Notes |
|---|---|---|---|
| **Directory Architecture** | Flat legacy folder `curriculums/italian/` | ISO language code + course track (`it/general/`) | ISO-JSON structure supports multi-track courses. |
| **Real Content Count** | 0 content files (only `.gitkeep`) | Validated JSON files (`A1.json`) | Legacy structure is entirely empty. |
| **CEFR Levels Covered** | None | Active CEFR level datasets in `it/general/` | ISO-JSON provides active level coverage. |
| **Schema Validation** | None | Validated against `curriculum.schema.json` | ISO-JSON integrates with repo validation tooling. |

---

## 3. Detailed Comparison & Pedagogical Evaluation

### 3.1 Content Analysis of `curriculums/italian/`
- Directory tree:
  - `curriculums/italian/.gitkeep`
- No `.html`, `.json`, `.js`, or `.md` content files exist in `curriculums/italian/`.

### 3.2 Comparison with ISO-JSON (`curriculums/it/`)
- `curriculums/it/` holds schema-compliant JSON files (e.g., `it/general/A1.json`) containing rich metadata, grammar structures, target vocabulary lists, duration, and teacher notes.

---

## 4. Recommendation & Action Proposal

**Recommendation:** **(b) Archive `curriculums/italian/` as superseded.**

### Rationale:
1. The `curriculums/italian/` folder contains no unique or real content.
2. The canonical ISO-JSON structure `curriculums/it/` is standardized and validated against the repository curriculum schema.

---

## 5. File Status & Integrity Confirmation

- **`curriculums/italian/`**: Left **UNTOUCHED** (audit only).
- **`curriculums/it/`**: Left **UNTOUCHED**.
- **`curriculums/_archive/italian_RECONCILIATION.md`**: Created for review.
