# COSYmanuals Readiness & Architecture Audit Report

**Date:** September 2025
**Auditor:** COSYmanuals Automated Audit Engine
**Status:** Readiness Review & Structural Audit

---

## Executive Summary

`COSYmanuals` is intended to serve as the third principal repository in the COSY ecosystem, providing offline/online language lesson manuals (grammar, vocabulary, communication) derived directly from `COSYplatform` curriculum datasets. This audit evaluates the current repository state across **Structural/Logic** organization, **Extraction Pipeline Readiness**, **Access Control Mechanisms**, and **Visual/CSS/UX** presentation.

---

## 1. Structural & Logic Review

### 1.1 Directory Layout Consistency
- **Expected Layout:** `manuals/<language>/<course-type>/<level>/` matching COSYplatform track naming (`general`, `spoken`, `professional`, `travelling`, `relocation`, `exam-prep`).
- **Current Layout Observation:**
  - Standard curriculum datasets exist under `curriculums/<lang>/<course_type>/<level>.json` (e.g. `curriculums/en/general/A1.json`, `curriculums/en/spoken/A1.json`).
  - Standalone manuals in `manuals/` follow a legacy layout (`manuals/<lang>/<type>/<level>/`, e.g., `manuals/en/grammar/a1/`, `manuals/en/vocabulary/a1/`, `manuals/en/communication/a1/`).
- **Finding:** A migration/derivation pipeline is required to extract COSYplatform JSON curriculums into plain, versionable Markdown documents following the `manuals/<language>/<course-type>/<level>/` schema.

### 1.2 Extraction Pipeline
- **Finding:** No automated extraction script (e.g., `scripts/extract_manuals.py`) is currently checked into the repository root to convert COSYplatform curriculum JSON files (`curriculums/`) into derived Markdown manual documents (`grammar.md`, `vocabulary.md`, `communication.md`).
- **Risk Analysis:** Without defensive field parsing, missing optional fields (such as `teacher_notes`, `growingTask`, or `ageAdaptation`) in COSYplatform lesson JSON files could cause script exceptions or unformatted output.

### 1.3 Access Control & Privacy
- **GitHub Permission Limitations:** GitHub repositories do not support path-based read ACLs on a single private repository. Any teacher added as a read collaborator to a single private repository can technically view all language directories.
- **Architectural Options for Founder Decision:**
  - **Option (a) Single Private Repository:** Founder manually manages collaborator access and relies on direct link distribution.
  - **Option (b) Language-Scoped Repositories:** Split manuals into language repos (`COSYmanuals-en`, `COSYmanuals-fr`), granting teachers read access strictly to their assigned language repository.
- **Roster & Data Collection:** Access checks must remain zero-data-harvesting, storing only GitHub usernames or opaque student IDs mapped to assigned language levels.

---

## 2. Visual / CSS & UX/UI Review

### 2.1 HTML & PDF Print Styles (`manuals/en/print/print.css`)
- **Print Optimization:** The repository includes a print stylesheet (`manuals/en/print/print.css`) with `@page { size: A4 portrait; margin: 20mm 15mm; }` margins, serif typography (`Georgia`), font-size reset (`11pt`), and explicit page break rules (`page-break-after: avoid` for headers, `page-break-inside: avoid` for boxes and tables).
- **Teacher/Student Offline Block:** Includes a dashed `.print-teacher-notes` area for offline paper annotations.
- **Navigation Hiding:** Web elements (`#cosy-nav`, `.sd-sticky-header`, practice buttons, quizzes) are cleanly hidden under `@media print`.

### 2.2 Raw Markdown Rendering Gap
- **Finding:** Plain Markdown files (`.md`) lack an in-browser rendering engine in the repository unless served via GitHub Pages or built into HTML. Raw Markdown viewing in GitHub UI is functional for diffing but less ideal for student reading during live lessons.

---

## 3. Recommended Next Steps

1. **Implement `scripts/extract_manuals.py`**: Build defensive extraction logic that reads `curriculums/<lang>/<course_type>/<level>.json` and outputs diffable `grammar.md`, `vocabulary.md`, and `communication.md` under `manuals/<language>/<course-type>/<level>/`.
2. **Standardize Roster & Access Control**: Check in `config/roster.example.json` and document Option (a) vs Option (b) trade-offs in `docs/ACCESS_CONTROL.md` and `README.md`.
3. **Purge Legacy Ecosystem References**: Ensure zero references to discontinued external modules remain.
