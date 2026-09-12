# COSYmanuals Migration Status & Stage 3 Execution Plan

> **Document Purpose**: Technical status report and roadmap for Stage 3 of the COSY ecosystem migration — migrating manual content into the standardized ISO taxonomy under `manuals/`.

---

## Executive Summary

**COSYmanuals** is dedicated exclusively to **MANUAL BOOKLETS** (grammar, vocabulary, and communication reference booklets for contracted students and teachers) in two primary formats:
1. **Digital Manuals**: Explanatory reference hubs linking out to COSYplatform lessons rather than duplicating interactive platform exercises.
2. **Print / Offline Manuals**: Formatted for print or offline reference (no interactive JS widgets, print-optimized CSS, page-break management).

Access to COSYmanuals is strictly link-only and never exposed via public website navigation.

---

## Current Repository Inventory & Audit Summary

Based on `manuals/AUDIT.md` and `manuals/MIGRATION_PLAN.md`:

### Total Scope
- **Languages Covered (14 ISO codes)**: `en` (English), `fr` (French), `it` (Italian), `es` (Spanish), `pt` (Portuguese), `de` (German), `ru` (Russian), `el` (Greek), `tt` (Tatar), `ba` (Bashkir), `br` (Breton), `cv` (Chuvash), `hy` (Armenian), `ka` (Georgian).
- **File Inventory**: Over 900 topic pages, index portals, shared assets, and template files.

### Standardized Target Structure
All manuals follow the strict 4-level deep directory convention:
```
manuals/
├── <iso_lang_code>/
│   ├── index.html
│   ├── {grammar,vocabulary,communication}/
│   │   └── <level>/             # e.g., a1, a2, b1, b2, c1, c2
│   │       ├── index.html
│   │       ├── part-1.html ... part-N.html
│   │       ├── appendix.html
│   │       ├── assets/
│   │       │   ├── app.js
│   │       │   └── style.css
│   │       └── topics/
│   │           └── <topic-slug>.html
│   └── print/
│       ├── print.css
│       └── index.html
```

---

## Stage 3 Requirements: The Content Move

Stage 3 represents the actual physical migration and restructuring of manual content from legacy flat folders (such as `grammaire-francaise/`, `elliniki-grammatiki/`, `vocabulary-a2/`, `english-a0-a1.html`) into the ISO structure above.

### Key Requirements & Action Items for Stage 3:

1. **Legacy Folder Restructuring**:
   - Move legacy flat folders into their canonical paths:
     - `grammaire-francaise/` ➔ `manuals/fr/grammar/`
     - `elliniki-grammatiki/` ➔ `manuals/el/grammar/`
     - `vocabulary-a2/` ➔ `manuals/en/vocabulary/a2/`
     - Flat root redirects (e.g., `english-a0-a1.html`) ➔ `manuals/en/index-a0-a1.html`
   - Complete inventory mapping per language code as specified in `manuals/MIGRATION_PLAN.md`.

2. **Link & Relative Path Remediation**:
   - Update 2,408 internal link references across 594 files affected by path movements.
   - Standardize relative asset paths from topic pages to root CSS/JS (`../../../../css/tokens.css`, `../../../../css/base.css`, etc.).

3. **Single-Sourcing & COSYplatform Linking**:
   - Remove redundant tables and long-form lesson explanations that duplicate COSYplatform interactive lessons.
   - Replace duplicated content with standardized reference callouts:
     ```html
     <div class="box platform-link">
       <strong>📖 Full Interactive Lesson:</strong>
       See this unit's complete lesson on <a href="https://cosyplatform.com/courses/en/a1/lesson-slug">COSYplatform</a>.
     </div>
     ```
   - Insert `<!-- TODO: Verify COSYplatform lesson availability for ... -->` comments for lessons whose COSYplatform equivalent is pending confirmation.

4. **Print / Offline Adaptation Rollout**:
   - Deploy `manuals/<lang>/print/print.css` and dedicated print index pages for all 14 supported languages, following the English proof-of-concept pattern (`manuals/en/print/`).
   - Hide interactive JS elements (`.quiz-panel`, `.ccq-panel`, `.checklist`, score badges) during `@media print`.

5. **Structural Standardization & CELTA Blueprinting**:
   - Enforce the 14-step CELTA manual blueprint (defined in `manuals/_TEMPLATE.md`) across all migrated topic pages.

---

## Migration Status Table

| Language | ISO | Digital Manual Index | Grammar Topic Pages | Vocabulary Topic Pages | Print CSS / Offline PoC | Platform Linking Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| English | `en` | ✅ Ready (`manuals/en/`) | ✅ A1–C2 | ✅ A1–C2 | ✅ PoC Created (`manuals/en/print/`) | 🔄 In Progress |
| French | `fr` | ✅ Ready (`manuals/fr/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Italian | `it` | ✅ Ready (`manuals/it/`) | ✅ A1–A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Spanish | `es` | ✅ Ready (`manuals/es/`) | ✅ A1–A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Portuguese | `pt` | ✅ Ready (`manuals/pt/`) | ✅ A1–A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| German | `de` | ✅ Ready (`manuals/de/`) | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Russian | `ru` | ✅ Ready (`manuals/ru/`) | ✅ A1 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Greek | `el` | ✅ Ready (`manuals/el/`) | ✅ A1 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Tatar | `tt` | ✅ Ready (`manuals/tt/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Bashkir | `ba` | ✅ Ready (`manuals/ba/`) | ✅ A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Breton | `br` | ✅ Ready (`manuals/br/`) | ✅ A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Chuvash | `cv` | ✅ Ready (`manuals/cv/`) | ✅ A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Armenian | `hy` | ✅ Ready (`manuals/hy/`) | ✅ A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
| Georgian | `ka` | ✅ Ready (`manuals/ka/`) | ✅ A2 | ✅ A2 | ⏳ Pending Stage 3 | ⏳ Pending Stage 3 |
