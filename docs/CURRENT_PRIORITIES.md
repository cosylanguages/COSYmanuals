# COSYmanuals Prioritized Action List & Operational Roadmap

> **Document Status**: Canonical Prioritized Punch-List
> **Last Updated**: March 2025
> **Context & Privacy Note**: COSYmanuals is intentionally private and direct-link accessible only. Do not add public navigation links or reference this document/repo from public navigation.

---

## Executive Summary

This document synthesizes and prioritizes the active open items across `manuals/AUDIT.md`, `student-workbooks/data/UNMAPPED.md`, `docs/MANUALS_MIGRATION_STATUS.md`, and `docs/PLATFORM_CONTENT_OVERLAP.md`. It transforms raw audit findings into a structured, actionable punch-list for curriculum developers, engineers, and content managers.

---

## 🔴 P0: Immediate / High-Priority Operational Blockers

### 1. Stage 3 Migration Completion & COSYlanguages Cleanup Flagging (DUP-001)
- **Status**: Migration complete in COSYmanuals; cleanup pending in COSYlanguages.
- **Action**: All 14 ISO language manuals (`ba`, `br`, `cv`, `de`, `el`, `en`, `es`, `fr`, `hy`, `it`, `ka`, `pt`, `ru`, `tt`) have been ingested and structured under `manuals/<iso>/{grammar,vocabulary}/<level>/` in COSYmanuals.
- **Flagged Cleanup Items for COSYlanguages**: Flag legacy duplicate folders (`COSYlanguages/manuals/*`, `COSYlanguages/reference-grammar/*`, `COSYlanguages/grammar/*`) for deletion in COSYlanguages' own post-migration cleanup task.

### 2. Standardized COSYplatform Callout Banners Rollout
- **Status**: In Progress across migrated topic pages.
- **Action**: Insert standardized outbound CTA callout banners on every explanatory topic HTML page:
  ```html
  <div class="box platform-link">
    <strong>📖 Full Interactive Lesson:</strong>
    Practice this topic on COSYplatform:
    <a href="https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}" target="_blank" rel="noopener">Open Lesson on COSYplatform →</a>
  </div>
  ```
- **Tracking**: Add `<!-- TODO: Verify COSYplatform lesson availability for ... -->` comments for units with pending platform lesson renderers.

### 3. Single-Sourcing Curriculum & Marathon Engines
- **Status**: Reconciliation Defined (`docs/PLATFORM_CONTENT_OVERLAP.md`).
- **Action**:
  - **Curriculums**: Retain canonical JSON datasets (`curriculums/{iso}/{course_type}/{LEVEL}.json`) in COSYplatform as primary store. Deprecate legacy interactive unit prototypes (`curriculums/english/intermediate-b1/unit-1.html`) in COSYmanuals in favor of outbound platform links.
  - **Marathons**: Single-source interactive marathon JS engines (`speaking-marathon-30-days`, `pronunciation-bootcamp`) in COSYplatform. Refactor marathon pages in COSYmanuals into printable syllabus booklets linking to COSYplatform.

---

## 🟡 P1: High-Value Enhancements & Tool Integrations

### 4. COSYtools Standalone Reference Engine Cross-Links
- **Status**: Audit Recommendation (`manuals/AUDIT.md`).
- **Action**: Link manual grammar and verb topic pages directly to standalone `COSYtools` reference engines via prominent callout banners:
  - French Verb Conjugator (`fr-conjugeur`) ➔ `manuals/fr/grammar/a2/topics/passe-compose-avoir-etre.html`
  - Italian Preposition/Reggenza Engine (`it-reggenza`) ➔ `manuals/it/grammar/a2/topics/`
  - English Verb Prepositions (`en-verb-prep`) ➔ `manuals/en/grammar/b1/topics/`
  - Greek Declension & Conjugation Engine (`el-klisi-rimaton`) ➔ `manuals/el/grammar/a1/topics/`

### 5. Print CSS & Offline Adaptation Rollout
- **Status**: English Proof-of-Concept Complete (`manuals/en/print/`); 13 languages pending.
- **Action**: Deploy `manuals/<lang>/print/print.css` and dedicated print index hubs across all remaining 13 target languages (`fr`, `it`, `es`, `pt`, `de`, `ru`, `el`, `tt`, `ba`, `br`, `cv`, `hy`, `ka`). Ensure `@media print` rules hide interactive JS widgets, quiz panels, and topbars while enforcing clean A4 page breaks.

### 6. Skyeng-Style Pedagogy Refinements
- **Status**: Audit Finding (`manuals/AUDIT.md`).
- **Action**: Re-structure introductory sections on high-traffic topic pages to prioritize visual scannability and example-first presentation:
  - **English A1 (`to-be.html`)**: Lead immediately with 2–3 visual color-coded examples (*"I am a teacher. She is happy."*) and formula box `[Subject + am/is/are]`, cutting ~100 words of preamble prose.
  - **French A2 (`passe-compose-avoir-etre.html`)**: Convert 14-verb list into a 2-column visual grid showing contrast pairs (*"Elle est arrivée (état)"* vs *"Elle a mangé (action)"*).
  - **Russian A1 (`to-be.html`)**: Lead with a side-by-side comparison card (*English: "I am a student" ➔ Russian: "Я студент" [No verb!]*), reducing zero-copula preamble prose by 80%.

---

## 🟢 P2: Content Expansion & Regional Maintenance

### 7. Content Depth Expansion for Regional & Minority Languages
- **Status**: Core Framework Available; Topic Count Expansion Needed.
- **Action**: Expand topic coverage for regional and minority language manuals (`ba`, `br`, `cv`, `hy`, `ka`, `ru`, `el`), which currently feature ~8–9 topics per level, bringing them closer to the depth of English, French, Italian, Spanish, and Tatar manuals.

### 8. German (`de/`) Topic Module Authoring
- **Status**: Root Index / Redirect Stub Created.
- **Action**: Author structured A1–A2 German grammar and vocabulary topic modules under `manuals/de/grammar/a1/` and `manuals/de/vocabulary/a1/`.

### 9. Student Workbook Mapping Maintenance
- **Status**: Clean / 0 Unmapped Topics (`student-workbooks/data/UNMAPPED.md`).
- **Action**: Maintain 100% topic mapping validity when adding new workbook topics or running `node scripts/normalize-workbooks.js`. Ensure all workbook entries specify valid `lang` and `level` fields.
