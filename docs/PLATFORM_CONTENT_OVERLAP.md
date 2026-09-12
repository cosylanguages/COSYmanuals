# COSYplatform vs. COSYmanuals Content Overlap & Structural Recommendations

> **Document Purpose**: Analysis of content overlap between `COSYmanuals` (`curriculums/`, `marathons/`, `teacher-guides/`, `student-workbooks/`) and `COSYplatform` (canonical interactive learning hub), with architectural recommendations and human decision items.

---

## Executive Summary & Architectural Scope

**COSYmanuals** is designed specifically for **MANUAL BOOKLETS** (reference booklets for contracted students and teachers) in two formats:
- **Digital Manuals**: Structural reference hubs linking to COSYplatform interactive lessons rather than hosting duplicate lessons.
- **Print / Offline Manuals**: Formatted for offline/printed reference (no interactive JS widgets, page-break friendly).

Currently, `COSYmanuals` hosts four legacy/non-manual folders (`curriculums/`, `marathons/`, `teacher-guides/`, `student-workbooks/`). This document details the overlap with COSYplatform, flags exact and near-duplicate content, and proposes single-sourcing guidelines.

---

## Detailed Directory-by-Directory Overlap Analysis

### 1. `curriculums/`
- **Current Inventory in COSYmanuals**:
  - `curriculums/{iso}/{course_type}/{LEVEL}.json` (e.g., `en/general/A1.json`, `fr/spoken/B2.json`, `ru/general/A1.json`) - 75 canonical JSON curriculum datasets validated against `curriculums/_schema/curriculum.schema.json`.
  - `curriculums/english/intermediate-b1/unit-1.html`, `index.html` - HTML lesson unit prototypes duplicating COSYplatform lesson views.
  - `curriculums/en/general/*_VISUAL_DICTIONARY_MASTER_CURRICULUM.md` - Master curriculum markdown specs.
- **COSYplatform Sibling Listing**:
  - `COSYplatform/curriculums/` hosts exact duplicate schema JSONs and lesson engine parsers.
- **Overlap Flag**:
  - **EXACT DUPLICATE**: All `curriculums/{iso}/*.json` files match COSYplatform curriculum schemas.
  - **NEAR-DUPLICATE**: `curriculums/english/intermediate-b1/unit-1.html` is an interactive unit view that duplicates COSYplatform's lesson renderer.
- **Recommendation**:
  - Canonical curriculum JSON files belong in **COSYplatform** (the primary data store for interactive learning).
  - COSYmanuals should either consume published platform JSONs or link directly to COSYplatform lesson pages rather than maintaining duplicate JSON/HTML files.

---

### 2. `marathons/`
- **Current Inventory in COSYmanuals**:
  - `marathons/speaking-marathon-30-days/index.html` (30-day intensive speaking challenge UI).
  - `marathons/pronunciation-bootcamp/levels/*.html` (A0–C2 interactive audio pronunciation drills with `fr-marathon-engine.js`).
  - `marathons/grammar-intensive-14-days/` & `marathons/vocabulary-marathon-500-words/`.
- **COSYplatform Sibling Listing**:
  - `COSYplatform/marathons/` hosts identical interactive marathon engines and level dashboards.
- **Overlap Flag**:
  - **EXACT DUPLICATE**: `pronunciation-bootcamp/levels/*.html` and `speaking-marathon-30-days/index.html` contain interactive JS quiz/speech widgets designed for direct student learning.
- **Recommendation**:
  - Marathons belong in **COSYplatform** exclusively.
  - COSYmanuals should only contain a syllabus booklet page linking to COSYplatform:
    > "Access your 30-Day Speaking Marathon on [COSYplatform](https://cosyplatform.com/marathons/speaking-30-days)."

---

### 3. `teacher-guides/`
- **Current Inventory in COSYmanuals**:
  - `teacher-guides/index.html` (Teacher methodology portal & lesson planning hub).
  - `teacher-guides/lesson-plans/` (30-minute, 45-minute, 60-minute lesson pacing guides).
  - `teacher-guides/assessment-tools/` (CEFR level placement rubrics).
  - `teacher-guides/game-based-learning/` (Methodology for using COSYgames/COSYworld in class).
- **Overlap Flag**:
  - **PARTIAL / USE-CASE OVERLAP**: The methodology and lesson plans serve contracted teachers (fitting COSYmanuals context), but embedded links and exercise prompts duplicate COSYplatform lesson flows.
- **Recommendation**:
  - Retain teacher methodology guides in COSYmanuals as reference booklets, but replace any embedded interactive lesson exercises with COSYplatform lesson links.

---

### 4. `student-workbooks/`
- **Current Inventory in COSYmanuals**:
  - `student-workbooks/data/workbooks/{lang}/{level}.json` (Generated topic workbooks via `scripts/normalize-workbooks.js`).
  - `student-workbooks/worksheets/` & `student-workbooks/answer-keys/` (Printable PDF/HTML worksheets).
  - `student-workbooks/progress-trackers/` (Offline CEFR tracking grids).
- **Overlap Flag**:
  - **PARTIAL OVERLAP**: Workbook datasets overlap with COSYplatform practice items, but printable worksheets/answer keys directly support offline/print manual usage.
- **Recommendation**:
  - Keep printable worksheets and answer keys in COSYmanuals under `student-workbooks/` (or merge under `manuals/<lang>/print/`), while data structures for interactive practice belong in COSYplatform.

---

## 🚩 Flagged "Human Decision Needed" List

Prior to deleting or performing mass moves on existing folders in COSYmanuals, human stakeholders (course directors / founder) must decide on the following 4 structural choices:

1. **Curriculum JSON Single-Sourcing**:
   - *Question*: Should `curriculums/{iso}/.../*.json` be deleted from `COSYmanuals` entirely and hosted exclusively in `COSYplatform`, or should `COSYmanuals` retain read-only copies used strictly for generating printed manual booklets?
   - *Recommendation*: Move to `COSYplatform` single-source repo; import via npm package or web build step if needed by `COSYmanuals`.

2. **Marathons Folder Removal**:
   - *Question*: Should `marathons/` (e.g. `pronunciation-bootcamp/`, `speaking-marathon-30-days/`) be removed from `COSYmanuals` in favor of a single syllabus page linking to `https://cosyplatform.com/marathons/`?
   - *Recommendation*: Yes. Marathons are interactive application features, not manual booklets.

3. **Teacher Guides & Student Workbooks Location**:
   - *Question*: Should `teacher-guides/` and `student-workbooks/` remain top-level directories in `COSYmanuals`, or be refactored into language-specific manual directories (e.g., `manuals/<lang>/teacher-guide/` and `manuals/<lang>/print/workbooks/`)?
   - *Recommendation*: Refactor into `manuals/<lang>/` taxonomy during Stage 3 migration for consistency.

4. **COSYplatform Standard URL Linking Pattern**:
   - *Question*: Confirm the standard URL format for outbound platform links in manual pages:
     `https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}` vs. `https://platform.cosylanguages.com/...`
   - *Recommendation*: Standardize on `https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}`.

---

## Single-Sourcing Linking Guideline

Every manual topic page must follow the rule: **Reference & Explain in Manual, Practice & Interact on Platform**.

```html
<!-- Example Standard Platform Link Callout -->
<div class="box practice-cta-banner" style="background:rgba(28,143,86,0.08); border-left:4px solid #1c8f56; padding:12px 16px; margin-bottom:20px; border-radius:4px;">
  <strong>🎯 Interactive Practice & Full Lesson:</strong>
  Practice this topic on COSYplatform:
  <a href="https://cosyplatform.com/courses/en/a1/to-be" target="_blank" rel="noopener">Open Lesson on COSYplatform →</a>
</div>
```
