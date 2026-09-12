# COSYmanuals Migration Status & Stage 3 Completion Plan

> **Document Purpose**: Technical status report and roadmap for Stage 3 of the COSY ecosystem migration — documenting the completion of manual content migration into the standardized ISO taxonomy under `manuals/` and flagging legacy copies in COSYlanguages for deletion.

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
- **File Inventory**: Over 900 topic pages, index portals, shared assets, and template files completely reorganized under `manuals/`.

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

## Stage 3 Completion Status: Content Move Executed

Stage 3 content migration is **✅ CONFIRMED COMPLETE** within COSYmanuals. All remaining standalone language manuals, monolingual grammar references, and thematic vocabulary datasets previously residing in COSYlanguages flat/legacy directories have been migrated and consolidated into `COSYmanuals/manuals/<iso>/{grammar,vocabulary}/<level>/`.

> **Physical Repository Verification Note**:
> All topic pages and section indices across all 14 supported ISO languages (`ba`, `br`, `cv`, `de`, `el`, `en`, `es`, `fr`, `hy`, `it`, `ka`, `pt`, `ru`, `tt`) are physically present in `COSYmanuals` under `manuals/<iso>/{grammar,vocabulary,communication}/<level>/`. With all source materials ingested and structured here, COSYmanuals has completed Stage 3 migration, and COSYlanguages can safely proceed with its own cleanup task (DUP-001) to remove its duplicate copies.

### Key Executed Action Items:

1. **Legacy Folder Restructuring**:
   - Legacy flat folders and monolingual references have been migrated into canonical ISO directory paths:
     - `grammaire-francaise/` ➔ `manuals/fr/grammar/a1/`
     - `lexique-francais/` ➔ `manuals/fr/vocabulary/a1/`
     - `elliniki-grammatiki/` ➔ `manuals/el/grammar/a1/`
     - `leksilogio-ellinikon/` ➔ `manuals/el/vocabulary/a1/`
     - `grammatika-russkogo-yazyka/` ➔ `manuals/ru/grammar/a1/`
     - `leksika-russkogo-yazyka/` ➔ `manuals/ru/vocabulary/a1/`
     - `deutsche-grammatik/` ➔ `manuals/de/grammar/a1/`
     - `tatar-teli-grammatikasy/` & `tatar-teli-leksikasy/` ➔ `manuals/tt/{grammar,vocabulary}/a1/`
     - Flat root redirects (e.g., `english-a0-a1.html`) ➔ `manuals/en/index-a0-a1.html`

2. **Link & Relative Path Remediation**:
   - Internal link references and relative asset paths (`../../../../css/...`, `assets/app.js`, `assets/style.css`) across all topic pages have been updated to respect the 4-level deep directory standard.

3. **Single-Sourcing & Platform Callout Banners**:
   - Outbound COSYplatform CTA banners (`https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}`) integrated into digital manual hubs.

---

## Migration Status Table

| Language | ISO | Digital Manual Index | Grammar Topic Pages | Vocabulary Topic Pages | Print CSS / Offline PoC | Platform Linking Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| English | `en` | ✅ Ready (`manuals/en/`) | ✅ A1–C2 | ✅ A1–C2 | ✅ PoC Created (`manuals/en/print/`) | 🔄 In Progress |
| French | `fr` | ✅ Ready (`manuals/fr/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Italian | `it` | ✅ Ready (`manuals/it/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Spanish | `es` | ✅ Ready (`manuals/es/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Portuguese | `pt` | ✅ Ready (`manuals/pt/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| German | `de` | ✅ Ready (`manuals/de/`) | ✅ A1 | ✅ A1 | ⏳ Pending Rollout | 🔄 In Progress |
| Russian | `ru` | ✅ Ready (`manuals/ru/`) | ✅ A1 | ✅ A1 | ⏳ Pending Rollout | 🔄 In Progress |
| Greek | `el` | ✅ Ready (`manuals/el/`) | ✅ A1 | ✅ A1 | ⏳ Pending Rollout | 🔄 In Progress |
| Tatar | `tt` | ✅ Ready (`manuals/tt/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Bashkir | `ba` | ✅ Ready (`manuals/ba/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Breton | `br` | ✅ Ready (`manuals/br/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Chuvash | `cv` | ✅ Ready (`manuals/cv/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Armenian | `hy` | ✅ Ready (`manuals/hy/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |
| Georgian | `ka` | ✅ Ready (`manuals/ka/`) | ✅ A1–A2 | ✅ A1–A2 | ⏳ Pending Rollout | 🔄 In Progress |

---

## 🗑️ Flagged Post-Migration Cleanup Task for COSYlanguages (DUP-001)

Per finding **DUP-001** ("Duplicate Manual & Reference Content Across Ecosystem"), content ingestion into `COSYmanuals` is complete. The following legacy paths in `COSYlanguages` are now flagged for deletion by the `COSYlanguages` repository maintainers as part of that repo's own cleanup task:

1. **`COSYlanguages/manuals/`**: Delete all legacy flat/duplicated manuals folders in `COSYlanguages` now that `COSYmanuals` serves as the sole canonical host.
2. **`COSYlanguages/reference-grammar/`**: Delete monolingual reference grammar JSONs and HTML views.
3. **`COSYlanguages/grammar/`**: Delete legacy standalone grammar folders.

> **Constraint Enforcement Notice**: No content inside `COSYlanguages` was modified or deleted during this migration task. COSYlanguages maintainers will execute the deletion using the flagged path manifest above once Stage 3 sign-off is confirmed.
