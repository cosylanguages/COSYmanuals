# Read-Only Repository Audit Report: COSYmanuals

**Audit Execution Date:** October 14, 2026
**Auditor Agent:** Jules
**Scope:** Repository structure, branches/PRs, content taxonomy, paid/restricted assets, ecosystem overlaps, legacy `COSYworld` references, cross-repo dependencies, dead weight, and deployment & access control architecture.

---

## 1. Branches and Open Pull Requests

Total remote branches inspected: **66** (including `main`).

| Branch Name | Last Commit Date | Commit Hash | What it adds that is not on `main` |
|---|---|---|---|
| `main` | 2026-10-06 | `82bc9594` | Base branch / canonical main repository state. |
| `add-en-a1-comm-apologies-and-gratitude-8551755434252486168` | 2026-09-30 | `95edbe0c` | Adds 19 files not on main (`curriculums/english/.gitkeep`, `curriculums/english/beginner-a1/.gitkeep`, etc.). |
| `apply-lang-accent-en-ru-fr-8259422333027986432` | 2026-10-01 | `ebfd40ed` | No new files added vs `main` (modifies 4,099 files, deletes 18). |
| `apply-lang-accent-fr-en-14292508421650572819` | 2026-10-01 | `4eec7e96` | No new files added vs `main` (modifies 4,099 files, deletes 18). |
| `apply-lang-accents-batch2-2218997174840287273` | 2026-10-03 | `4c8dcdcb` | No new files added vs `main` (modifies 3,966 files, deletes 16). |
| `apply-ru-lang-accent-5759557420698129108` | 2026-10-02 | `e3e5b3ee` | Adds 12 screenshot report files (`reports/screenshots/*.png`). |
| `audit-french-grammar-manuals-1778469127075904903` | 2026-09-21 | `d2c7707e` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `audit-language-name-curriculums-17443003468706227681` | 2026-09-28 | `132be0fc` | No new files added vs `main` (modifies 4,214 files, deletes 29). |
| `design-system-accent-alignment-11229439525800191219` | 2026-10-03 | `0373dfd7` | No new files added vs `main` (modifies 3,966 files, deletes 16). |
| `docs/reconcile-readme-cosyplatform-4391613171178178732` | 2026-09-24 | `3ecf3fc4` | No new files added vs `main` (modifies 3,569 files, deletes 1,170). |
| `feat/a0-a1-confusing-grammar-guide-7158795291083510464` | 2026-10-05 | `8aaef053` | No new files added vs `main` (modifies 3,008 files, deletes 8). |
| `feat/a0-a1-general-lesson-spec-2595713322348264915` | 2026-09-22 | `3cceea84` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `feat/b1-visual-dictionary-curriculum-4876863232450797015` | 2026-09-24 | `1f29aaeb` | No new files added vs `main` (modifies 3,535 files, deletes 1,212). |
| `feat/confusing-english-grammar-guides-3522519158972421097` | 2026-10-05 | `e7e59b20` | No new files added vs `main` (modifies 3,008 files, deletes 8). |
| `feat/english-a0-a1-grammar-manuals-audit-4896033743790190066` | 2026-09-13 | `6b9bc1aa` | Adds 25 files not on main (`manuals/en/grammar/a1/GRAMMAR_STANDARD.md`, etc.). |
| `feat/extend-en-conjunctions-when-if-although-5272241828038665272` | 2026-09-30 | `cf25dc88` | No new files added vs `main` (modifies 4,214 files, deletes 27). |
| `feat/land-reference-grammar-data-and-schemas-7298878101049554896` | 2026-09-25 | `8649841f` | No new files added vs `main` (modifies 3,569 files, deletes 1,070). |
| `feat/migrate-communication-standard-10482245797481990771` | 2026-09-25 | `5b1842eb` | No new files added vs `main` (modifies 3,647 files, deletes 983). |
| `feat/port-level-pronunciation-bootcamps-10918973394931257861` | 2026-09-14 | `1f335349` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `feat/shared-print-system-6883227026734462704` | 2026-09-13 | `037b51e0` | Adds 19 files not on main (`shared/templates/print-button.html`, etc.). |
| `feature/french-grammar-14days-lessons-13603338923220854362` | 2026-09-13 | `d7677464` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `fix-broken-css-links-2831118951463442708` | 2026-09-30 | `473f761a` | No new files added vs `main` (modifies 4,241 files, deletes 27). |
| `fix-css-link-offenders-4411771907462125041` | 2026-09-30 | `f0445d31` | No new files added vs `main` (modifies 4,239 files, deletes 24). |
| `fix-remove-dead-lang-accents-css-links-4588118741859230342` | 2026-09-14 | `96a12089` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `fix-shared-styles-modular-css-11968202493890670508` | 2026-09-14 | `94e50889` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `fix/clean-raw-teacher-notes-12802745646435414040` | 2026-09-30 | `b49910d5` | No new files added vs `main` (modifies 4,119 files, deletes 20). |
| `fix/repair-preexisting-links-6575915550906857093` | 2026-09-20 | `e5a07dd3` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `fix/second-audit-tatar-and-links-4032870838767234791` | 2026-09-22 | `5fdfca2b` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `fix/teacher-notes-raw-dumps-7729732180732278169` | 2026-09-30 | `de8335e4` | No new files added vs `main` (modifies 4,205 files, deletes 23). |
| `jules-10293000481321690779-101f5ba6` | 2026-10-04 | `cffcff0d` | No new files added vs `main` (modifies 3,017 files, deletes 16). |
| `jules-11214764287698782945-606fe8de` | 2026-09-24 | `19c46d17` | No new files added vs `main` (modifies 4,751 files, deletes 1,212). |
| `jules-13574964946507860771-d4d3f996` | 2026-10-01 | `0f344642` | No new files added vs `main` (modifies 4,117 files, deletes 18). |
| `jules-17088724284958396683-3e3cf855` | 2026-09-12 | `82883824` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-17876971421613622494-f62585e4` | 2026-09-13 | `1cc9f952` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-227971416779705453-e8fd9ecb` | 2026-09-27 | `b83ad886` | Adds 1 new file: `reports/cosylanguages_migration_verification_report.md`. |
| `jules-3057949907245082309-4e262da8` | 2026-10-06 | `defc94c5` | No new files added vs `main` (modifies 2,381 files). |
| `jules-3780021495370891495-f9446956` | 2026-09-13 | `c601c4a9` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-3861525349960092638-0412acab` | 2026-09-10 | `582ccf6a` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-4617815207798914690-f414f2a0` | 2026-09-26 | `55b41eee` | No new files added vs `main` (modifies 4,333 files, deletes 171). |
| `jules-624739837117712781-4a88edc2` | 2026-09-14 | `575e71a5` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-8899994338648531259-5d5341e0` | 2026-10-02 | `4a5e79f5` | Adds 12 screenshot report files (`reports/screenshots/*.png`). |
| `jules-manuals-reorganize-small-elements-12624585773230320660` | 2026-09-11 | `5e572cdb` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-manuals-reorganize-small-elements-12624585773230320660-14963955529536729471` | 2026-09-12 | `e67b6caf` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules-ru-grammar-marathon-14-days-4170849778252270443` | 2026-09-13 | `afa41424` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `jules/extract-manuals-pipeline-audit-16911503648729161129` | 2026-09-25 | `c1b6f218` | No new files added vs `main` (modifies 4,348 files, deletes 183). |
| `jules/p05-a1-coverage-audit-12475192889329601621` | 2026-09-22 | `9d4a1335` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `manuals-reorganize-small-elements-8556050655510902087` | 2026-09-12 | `dfb37167` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `manuals-stage3-migration-docs-print-poc-9159619997767497421` | 2026-09-12 | `04dc32dc` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate-manuals-stage-1-11589919513671823098` | 2026-09-11 | `909a94a8` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate-topics-to-supabase-storage-11978739519723668603` | 2026-09-26 | `dab04958` | Adds 1 file: `shared/js/auth-guard.js`. |
| `migrate/archive-generators-docs-18287071725109376203` | 2026-09-20 | `6e2f27b0` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/en-16281519456721860534` | 2026-09-20 | `1ea3d40c` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/es-it-pt-tt-el-5663909621289066549` | 2026-09-20 | `dd960431` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/fr-c1-c2-comm-vocab-14468947717169629859` | 2026-09-20 | `ff3ab65e` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/fr-grammar-a1-a2-17985454859164775501` | 2026-09-20 | `cd2f83fe` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/fr-grammar-b1-b2-12729961272672922870` | 2026-09-20 | `f7f65bf3` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/indexes-and-residuals-16318955080678997871` | 2026-09-20 | `cd69b930` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `migrate/ru-17959825550058054281` | 2026-09-20 | `1565fc81` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `refactor/deduplicate-curriculums-12520653334090934371` | 2026-09-28 | `ea42886c` | No new files added vs `main` (modifies 4,243 files, deletes 29). |
| `revert-12-visual-genome-layer-10419773072805946972` | 2026-09-12 | `e9113a93` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `setup-cosymanuals-private-repo-9998405495562769675` | 2026-09-10 | `f4b78e15` | Adds 2,073 files not on main (`curriculums/armenian/*`, `curriculums/bashkir/*`, etc.). |
| `setup-cosymanuals-structure-and-extraction-15964812614897886470` | 2026-09-25 | `1bbcd398` | Adds 1 file: `AUDIT.md` (legacy iteration). |
| `shared-accent-system-15247117750048568672` | 2026-10-03 | `1e63d2ad` | No new files added vs `main` (modifies 3,982 files, deletes 16). |
| `sync-en-general-a1-curriculum-16758529372366061025` | 2026-09-13 | `c20701d6` | Adds 19 files not on main (`curriculums/english/.gitkeep`, etc.). |
| `verify-cosylanguages-manuals-migration-14281874233190915850` | 2026-09-28 | `40831b35` | No new files added vs `main` (modifies 4,326 files, deletes 29). |
| `visual-genome-layer-10419773072805946972` | 2026-09-12 | `ce12e1b1` | Adds 26 files not on main (`_engine/buzzer-button.js`, `_engine/components.css`, etc.). |

---

## 2. Full Folder Tree to Depth 3

Root directory contains 5,442 total files across 12 top-level subdirectories.

- `.` (depth 0): Root repository folder (~5,442 files total, 5 files directly: `CANON_SOURCE_OF_TRUTH.md`, `CONTENT_ARCHITECTURE.md`, `README.md`, `index.html`, `.gitignore`).
  - `.github/` (depth 1): GitHub CI/CD workflows and actions (~6 files total, 6 files directly).
    - `.github/workflows/` (depth 2): Automated workflow files (`link-check.yml`, etc.) (~6 files total).
  - `config/` (depth 1): Access control and roster configuration files (~1 file total, 1 file directly: `roster.example.json`).
  - `catalog/` (depth 1): Public catalog manifest metadata for gated manual browsing (~128 files total, 1 file directly: `manifest.json`).
    - `catalog/manifest.json` (depth 2): Master index of manual IDs, titles, levels, and languages.
    - `catalog/*.json` (depth 2): Individual manual metadata descriptors for Supabase authorization (~127 files).
  - `curriculums/` (depth 1): Single-source course curriculum JSON datasets (~128 files total, 1 file directly: `README.md`).
    - `curriculums/_schema/` (depth 2): JSON schema specifications for curriculum datasets (~2 files total).
    - `curriculums/ba/` (depth 2): Bashkir curriculum datasets (~2 files total, general course A1/C1).
    - `curriculums/br/` (depth 2): Breton curriculum datasets (~2 files total, general course A1/C1).
    - `curriculums/cv/` (depth 2): Chuvash curriculum datasets (~2 files total, general course A1/C1).
    - `curriculums/de/` (depth 2): German curriculum datasets (~2 files total, general course A1/C1).
    - `curriculums/el/` (depth 2): Greek curriculum datasets (~2 files total, general course A1).
    - `curriculums/en/` (depth 2): English curriculum datasets (~35 files total).
      - `curriculums/en/general/` (depth 3): General English courses A1-C2 (~13 files total).
      - `curriculums/en/spoken/` (depth 3): Spoken English courses A1-C2 (~6 files total).
      - `curriculums/en/travelling/` (depth 3): Travel English courses A1-B1 (~3 files total).
      - `curriculums/en/professional/` (depth 3): Business English courses B1-C2 (~5 files total).
      - `curriculums/en/relocation/` (depth 3): Relocation English courses A2-C1 (~4 files total).
      - `curriculums/en/exam/` (depth 3): Exam preparation English courses B1-C2 (~4 files total).
    - `curriculums/es/` (depth 2): Spanish curriculum datasets (~2 files total, general A1/C1).
    - `curriculums/fr/` (depth 2): French curriculum datasets (~21 files total across general, spoken, travelling, professional).
    - `curriculums/hy/` (depth 2): Armenian curriculum datasets (~2 files total, general A1/C1).
    - `curriculums/it/` (depth 2): Italian curriculum datasets (~1 file total, general A1).
    - `curriculums/ka/` (depth 2): Georgian curriculum datasets (~2 files total, general A1/C1).
    - `curriculums/pt/` (depth 2): Portuguese curriculum datasets (~2 files total, general A1/C1).
    - `curriculums/ru/` (depth 2): Russian curriculum datasets (~21 files total across general, spoken, travelling, professional).
    - `curriculums/tt/` (depth 2): Tatar curriculum datasets (~2 files total, general A1/C1).
  - `data/` (depth 1): Shared reference data, courses, and linguistic datasets (~105 files total).
    - `data/courses/` (depth 2): Course taxonomy definitions (~1 file directly: `courses.json`).
    - `data/grammar/` (depth 2): Grammatical confusion guides and reference grammar data (~104 files total, 5 confusion JSON files directly).
      - `data/grammar/reference/` (depth 3): Extended syntax, morphology, phonology, and CCQ reference files for `en`, `fr`, `it`, `ru`, `el` (~99 files total).
  - `docs/` (depth 1): Technical documentation, architecture guides, and migration audit logs (~35 files total, 6 files directly).
    - `docs/from-cosylanguages/` (depth 2): Legacy specs, schemas, and templates archived from COSYlanguages (~24 files total).
      - `docs/from-cosylanguages/manuals/` (depth 3): Archived manual standard guidelines (~9 files total).
    - `docs/migration/` (depth 2): Migration status trackers, crosswalks, and link-check baselines (~5 files total).
  - `manuals/` (depth 1): Multi-language CEFR HTML/Markdown textbook manuals and topic lessons (~4,646 files total, 5 files directly: `_TEMPLATE.md`, `founder-portal.html`, `index.html`, `manual-viewer.html`, `manuals.json`).
    - `manuals/ba/` (depth 2): Bashkir manuals (~84 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/br/` (depth 2): Breton manuals (~87 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/cv/` (depth 2): Chuvash manuals (~70 files total: `grammar`, `vocabulary`, `print`, `teacher-access.html`).
    - `manuals/de/` (depth 2): German manuals (~111 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/el/` (depth 2): Greek manuals (~233 files total: `grammar`, `vocabulary`, `general`, `communication`, `exam`, `print`, `teacher-access.html`).
    - `manuals/en/` (depth 2): English manuals (~1,046 files total: `grammar`, `vocabulary`, `communication`, `general`, `spoken`, `travelling`, `professional`, `relocation`, `exam`, `print`, `teacher-access.html`).
    - `manuals/es/` (depth 2): Spanish manuals (~118 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/fr/` (depth 2): French manuals (~1,565 files total: `grammar`, `vocabulary`, `communication`, `general`, `spoken`, `travelling`, `professional`, `print`, `teacher-access.html`).
    - `manuals/hy/` (depth 2): Armenian manuals (~85 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/it/` (depth 2): Italian manuals (~220 files total: `grammar`, `vocabulary`, `communication`, `general`, `print`, `teacher-access.html`).
    - `manuals/ka/` (depth 2): Georgian manuals (~84 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/pt/` (depth 2): Portuguese manuals (~116 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
    - `manuals/ru/` (depth 2): Russian manuals (~721 files total: `grammar`, `vocabulary`, `communication`, `general`, `spoken`, `travelling`, `professional`, `print`, `teacher-access.html`).
    - `manuals/tt/` (depth 2): Tatar manuals (~101 files total: `grammar`, `vocabulary`, `general`, `print`, `teacher-access.html`).
  - `marathons/` (depth 1): Intensive learning marathon hubs and daily lesson tracks (~352 files total, 1 file directly: `README.md`).
    - `marathons/grammar-intensive-14-days/` (depth 2): 14-Day Grammar Confusions marathon (~50 files total: `en/`, `fr/`, `ru/` daily lessons).
    - `marathons/pronunciation-bootcamp/` (depth 2): French Pronunciation Bootcamp (~16 files total).
    - `marathons/pronunciation-bootcamp-el/` (depth 2): Greek Pronunciation Bootcamp (~8 files total).
    - `marathons/pronunciation-bootcamp-en/` (depth 2): English Pronunciation Bootcamp (~15 files total).
    - `marathons/pronunciation-bootcamp-ru/` (depth 2): Russian Pronunciation Bootcamp (~15 files total).
    - `marathons/speaking-marathon-30-days/` (depth 2): 30-Day Speak & Think Marathon (~246 files total: `a0-a2/`, `b1-b2/` daily lessons).
    - `marathons/vocabulary-marathon-500-words/` (depth 2): 500-Word Vocabulary Marathon (~1 file total).
  - `reports/` (depth 1): Verification reports, audit documents, and Playwright screenshots (~3 files total, 3 files directly).
  - `schemas/` (depth 1): Reusable JSON schemas (~1 file directly: `ccq.schema.json`).
  - `scripts/` (depth 1): Python and Node.js build, extraction, migration, and verification tools (~21 files total, 20 files directly).
  - `shared/` (depth 1): Shared CSS stylesheets, JavaScript SSO/CMS drivers, and HTML templates (~20 files total).
    - `shared/css/` & `shared/styles/` (depth 2): Design tokens and modular stylesheets (~13 files total).
    - `shared/js/` (depth 2): Client-side SSO and Founder Visual CMS scripts (`auth-sso.js`, `cms-editor.js`, `auth-guard.js`) (~3 files total).
    - `shared/templates/` (depth 2): Reusable HTML/Markdown templates (~4 files total).
  - `student-workbooks/` (depth 1): Interactive student workbook datasets, worksheets, and answer keys (~14 files total).
    - `student-workbooks/data/` (depth 2): Student workbook JSON datasets (~10 files total).
      - `student-workbooks/data/workbooks/` (depth 3): Per-language A1 workbook JSON datasets for `de`, `el`, `en`, `es`, `fr`, `it`, `pt`, `ru` (~8 files total).
  - `teacher-guides/` (depth 1): Teacher pedagogical guides, lesson plans, and assessment tools (~6 files total).
    - `teacher-guides/assessment-tools/` (depth 2): Assessment rubrics and guides (~1 file total).
    - `teacher-guides/lesson-plans/` (depth 2): Reusable lesson plan templates (~2 files total).
    - `teacher-guides/game-based-learning/` (depth 2): Gamified teaching methodology guides (~1 file total).
  - `templates/` (depth 1): Legacy HTML page templates (~12 files total).
  - `tools/` (depth 1): Legacy manual generation tooling archived for reference (~52 files total).
    - `tools/legacy-generators/` (depth 2): Archived generation scripts (~52 files total).

---

## 3. Languages Covered (ISO 639-1) and CEFR Levels Covered per Content Type

The repository covers **14 ISO language codes**: `ba` (Bashkir), `br` (Breton), `cv` (Chuvash), `de` (German), `el` (Greek), `en` (English), `es` (Spanish), `fr` (French), `hy` (Armenian), `it` (Italian), `ka` (Georgian), `pt` (Portuguese), `ru` (Russian), `tt` (Tatar).

| Content Type | Covered ISO Languages | CEFR Levels Covered |
|---|---|---|
| **Curriculums (`curriculums/`)** | `ba`, `br`, `de`, `el`, `en`, `es`, `fr`, `hy`, `it`, `ka`, `pt`, `ru`, `tt` | **A1, A2, B1, B2, C1, C2** (General, Spoken, Travel, Business, Relocation, Exam). |
| **Manuals & Textbooks (`manuals/`)** | All 14 languages (`ba`, `br`, `cv`, `de`, `el`, `en`, `es`, `fr`, `hy`, `it`, `ka`, `pt`, `ru`, `tt`) | **A1, A2, B1, B2, C1, C2** (Grammar, Vocabulary, Communication, Skill Tracks). |
| **Marathons (`marathons/`)** | `en`, `fr`, `ru`, `el`, `es`, `it` | **A0, A1, A2, B1, B2** (14-Day Grammar, 30-Day Speak & Think, Pronunciation Bootcamps). |
| **Reference Grammar (`data/grammar/reference/`)** | `en`, `fr`, `it`, `ru`, `el` | **A1, A2, B1, B2, C1, C2** (Syntax, Morphology, Phonology, CCQs). |
| **Grammar Confusions (`data/grammar/`)** | `en`, `fr`, `ru`, `it`, `el` | **A1, A2, B1, B2, C1, C2** (`confusions_*.json`). |
| **Student Workbooks (`student-workbooks/`)** | `de`, `el`, `en`, `es`, `fr`, `it`, `pt`, `ru` | **A1** (`a1.json` per language). |
| **Teacher Guides (`teacher-guides/`)** | Universal / English | **A1-C2** (General lesson planning and gamification). |

---

## 4. Content Intended to Be PAID or Restricted Served Publicly

The following assets contain course material, teacher notes, answer keys, or administrative access portals that are currently served publicly via GitHub Pages or static repository routes without server-side authentication:

1. **Teacher Access Portals (14 ISO Languages):**
   - `manuals/ba/teacher-access.html`
   - `manuals/br/teacher-access.html`
   - `manuals/cv/teacher-access.html`
   - `manuals/de/teacher-access.html`
   - `manuals/el/teacher-access.html`
   - `manuals/en/teacher-access.html`
   - `manuals/es/teacher-access.html`
   - `manuals/fr/teacher-access.html`
   - `manuals/hy/teacher-access.html`
   - `manuals/it/teacher-access.html`
   - `manuals/ka/teacher-access.html`
   - `manuals/pt/teacher-access.html`
   - `manuals/ru/teacher-access.html`
   - `manuals/tt/teacher-access.html`

2. **Founder & CMS Administration Portal:**
   - `manuals/founder-portal.html`

3. **Student Workbook Datasets and Answer Keys:**
   - `student-workbooks/data/workbook_data.js`
   - `student-workbooks/data/workbooks/de/a1.json`
   - `student-workbooks/data/workbooks/el/a1.json`
   - `student-workbooks/data/workbooks/en/a1.json`
   - `student-workbooks/data/workbooks/es/a1.json`
   - `student-workbooks/data/workbooks/fr/a1.json`
   - `student-workbooks/data/workbooks/it/a1.json`
   - `student-workbooks/data/workbooks/pt/a1.json`
   - `student-workbooks/data/workbooks/ru/a1.json`

4. **Teacher Pedagogical Guides & Lesson Plans:**
   - `teacher-guides/index.html`
   - `teacher-guides/lesson-plans/lesson-plan-template.md`
   - `teacher-guides/game-based-learning/`

5. **Full Curriculum JSON Specifications (Intended as Single Source for Paid COSYplatform Courses):**
   - `curriculums/en/general/*.json`
   - `curriculums/fr/general/*.json`
   - `curriculums/ru/general/*.json`
   - `curriculums/de/general/*.json`
   - `curriculums/es/general/*.json`
   - `curriculums/it/general/*.json`
   - `curriculums/pt/general/*.json`
   - `curriculums/el/general/*.json`
   - `curriculums/ba/general/*.json`
   - `curriculums/br/general/*.json`
   - `curriculums/cv/general/*.json`
   - `curriculums/hy/general/*.json`
   - `curriculums/ka/general/*.json`
   - `curriculums/tt/general/*.json`

---

## 5. Content Overlapping or Duplicating Other COSY Repositories

The content in this repository overlaps with canonical databases in **COSYdata** (vocabulary), **COSYtools** (grammar/verb conjugation), **COSYplatform** (paid interactive courses), and **COSYlanguages** (public site).

| Overlapping Asset Path | File Count | Fingerprint (Newest Commit Date) | Primary Canonical Repository |
|---|---|---|---|
| `curriculums/` (All JSON course structures) | 128 files | 2026-09-28 (`ea42886c`) | **COSYplatform** (Paid interactive course runner) |
| `data/grammar/confusions_*.json` | 5 files | 2026-10-05 (`8aaef053`) | **COSYtools** / **COSYdata** (Grammar Reference API) |
| `data/grammar/reference/` | 99 files | 2026-09-25 (`8649841f`) | **COSYtools** (Linguistic Reference Data) |
| `student-workbooks/data/workbooks/` | 8 files | 2026-09-10 (`f4b78e15`) | **COSYplatform** (Interactive Student Exercises) |
| `manuals/` (Rendered HTML manual pages) | 4,646 files | 2026-10-06 (`defc94c5`) | **COSYmanuals** (Private Gated Storage) / **COSYlanguages** (Public Landing Pages) |
| `marathons/` (30-Day & 14-Day Marathons) | 352 files | 2026-10-06 (`82bc9594`) | **COSYplatform** / **COSYevents** (Interactive Bootcamps) |

---

## 6. Every Reference to COSYworld Across Codebase and Branches

Per ecosystem direction, **COSYworld is being discontinued**.

- **On `main` branch:** **0 references found** (All references to `COSYworld` have been completely removed from `main`).

- **On Remote Branches (Legacy / Unmerged PR Branches):**
  A total of **46 references** remain on 2 historical unmerged branches:

### Branch 1: `origin/sync-en-general-a1-curriculum-16758529372366061025` (23 references)
1. `CANON_SOURCE_OF_TRUTH.md:3` - `COSYworld` in ecosystem list.
2. `CANON_SOURCE_OF_TRUTH.md:16` - `COSYworld` in mirror list.
3. `CANON_SOURCE_OF_TRUTH.md:57` - `COSYworld` in docs list.
4. `README.md:90` - `[COSYworld](https://cosylanguages.github.io/COSYworld/)` outbound link.
5. `curriculums/english/intermediate-b1/index.html:57` - `https://cosylanguages.github.io/COSYworld/` button href.
6. `curriculums/english/intermediate-b1/index.html:185` - `https://cosylanguages.github.io/COSYworld/` footer href.
7. `curriculums/english/intermediate-b1/unit-1.html:67` - `COSYworld` text mention.
8. `curriculums/english/intermediate-b1/unit-1.html:70` - `https://cosylanguages.github.io/COSYworld/` button href.
9. `curriculums/english/intermediate-b1/unit-1.html:111` - `https://cosylanguages.github.io/COSYworld/` footer href.
10. `docs/PLATFORM_CONTENT_OVERLAP.md:56` - `COSYworld` methodology mention.
11. `marathons/speaking-marathon-30-days/index.html:177` - `https://cosylanguages.github.io/COSYworld/` footer href.
12. `shared/templates/curriculum-template.html:55` - `https://cosylanguages.github.io/COSYworld/` button href.
13. `shared/templates/curriculum-template.html:103` - `https://cosylanguages.github.io/COSYworld/` footer href.
14. `shared/templates/marathon-template.html:107` - `https://cosylanguages.github.io/COSYworld/` footer href.
15. `shared/templates/unit-template.html:108` - `https://cosylanguages.github.io/COSYworld/` footer href.
16. `teacher-guides/index.html:42` - `https://cosylanguages.github.io/COSYworld/` link.
17. `teacher-guides/index.html:122` - `COSYworld` homework assignment text.
18. `teacher-guides/index.html:134` - `https://cosylanguages.github.io/COSYworld/` footer href.
19. `teacher-guides/lesson-plans/lesson-plan-template.md:17` - `COSYworld` quest mention.
20. `teacher-guides/lesson-plans/lesson-plan-template.md:71` - `COSYworld` quest mention.
21. `teacher-guides/lesson-plans/lesson-plan-template.md:73` - `COSYworld` quest mention.
22. `teacher-guides/lesson-plans/lesson-plan-template.md:129` - `COSYworld` quest mention.
23. `templates/curriculum-template.html:55` - `https://cosylanguages.github.io/COSYworld/` button href.

### Branch 2: `origin/visual-genome-layer-10419773072805946972` (23 references)
1. `README.md:88` - `[COSYworld](https://cosylanguages.github.io/COSYworld/)` outbound link.
2. `curriculums/english/intermediate-b1/index.html:57` - `https://cosylanguages.github.io/COSYworld/` button href.
3. `curriculums/english/intermediate-b1/index.html:185` - `https://cosylanguages.github.io/COSYworld/` footer href.
4. `curriculums/english/intermediate-b1/unit-1.html:67` - `COSYworld` text mention.
5. `curriculums/english/intermediate-b1/unit-1.html:70` - `https://cosylanguages.github.io/COSYworld/` button href.
6. `curriculums/english/intermediate-b1/unit-1.html:111` - `https://cosylanguages.github.io/COSYworld/` footer href.
7. `docs/PLATFORM_CONTENT_OVERLAP.md:56` - `COSYworld` methodology mention.
8. `marathons/speaking-marathon-30-days/index.html:177` - `https://cosylanguages.github.io/COSYworld/` footer href.
9. `shared/templates/curriculum-template.html:55` - `https://cosylanguages.github.io/COSYworld/` button href.
10. `shared/templates/curriculum-template.html:103` - `https://cosylanguages.github.io/COSYworld/` footer href.
11. `shared/templates/marathon-template.html:107` - `https://cosylanguages.github.io/COSYworld/` footer href.
12. `shared/templates/unit-template.html:108` - `https://cosylanguages.github.io/COSYworld/` footer href.
13. `teacher-guides/index.html:42` - `https://cosylanguages.github.io/COSYworld/` link.
14. `teacher-guides/index.html:122` - `COSYworld` homework assignment text.
15. `teacher-guides/index.html:134` - `https://cosylanguages.github.io/COSYworld/` footer href.
16. `teacher-guides/lesson-plans/lesson-plan-template.md:17` - `COSYworld` quest mention.
17. `teacher-guides/lesson-plans/lesson-plan-template.md:71` - `COSYworld` quest mention.
18. `teacher-guides/lesson-plans/lesson-plan-template.md:73` - `COSYworld` quest mention.
19. `teacher-guides/lesson-plans/lesson-plan-template.md:129` - `COSYworld` quest mention.
20. `templates/curriculum-template.html:55` - `https://cosylanguages.github.io/COSYworld/` button href.
21. `templates/curriculum-template.html:103` - `https://cosylanguages.github.io/COSYworld/` footer href.
22. `templates/marathon-template.html:107` - `https://cosylanguages.github.io/COSYworld/` footer href.
23. `templates/unit-template.html:108` - `https://cosylanguages.github.io/COSYworld/` footer href.

---

## 7. Every Dependency on Another COSY Repository

Total cross-repo dependency references on `main`: **5,217 instances**.

### Key System Dependencies (Entry Points, Specs, & Scripts)
1. **`index.html` (Catalog Hub & Viewer Entry Point):**
   - Line 10: `<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.1"></script>` (Supabase JS SDK dependency).
   - Line 11: `<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>` (Marked renderer dependency).
   - Line 12: `<script src="shared/js/auth-sso.js"></script>` (SSO session restoration script).
   - Line 13: `<script src="shared/js/cms-editor.js"></script>` (Founder Visual CMS editor script).
   - Line 129: `<a href="https://cosylanguages.github.io/COSYlanguages/" target="_blank" class="btn">COSYlanguages Hub</a>` (Outbound public hub link).
   - Line 250: `const SUPABASE_URL = window.ENV_SUPABASE_URL || "https://your-supabase-project.supabase.co";` (Supabase backend endpoint).
   - Line 260: `const LOGIN_BASE_URL = "https://cosylanguages.github.io/COSYlanguages/login.html";` (Auth redirect target).

2. **`shared/js/auth-sso.js` (Ecosystem SSO Driver):**
   - Line 2: Ecosystem Single Sign-On documentation header.
   - Line 15: `const supabaseUrl = window.ENV_SUPABASE_URL || window.SUPABASE_URL || "https://your-supabase-project.supabase.co";`

3. **`shared/js/cms-editor.js` (Visual CMS Driver):**
   - Line 2: Visual CMS editor documentation header.
   - Line 16: `const supabaseUrl = window.ENV_SUPABASE_URL || window.SUPABASE_URL || "https://your-supabase-project.supabase.co";`

4. **`manuals/founder-portal.html` (Founder Dashboard):**
   - Line 12: `<script src="../shared/js/auth-sso.js"></script>` (SSO Driver).

5. **`docs/CURRENT_PRIORITIES.md`:**
   - Line 29: `<a href="https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}" target="_blank" rel="noopener">` (COSYplatform interactive lesson outbound pattern).

6. **`README.md`:**
   - Line 14: `https://cosylanguages.github.io/COSYlanguages/login.html?redirect=<manual-id>`
   - Line 23: `SUPABASE_URL=https://your-supabase-project.supabase.co`
   - Line 116: `[COSYplatform](https://cosyplatform.com)`

7. **5,180+ Topic & Manual Pages:**
   - Outbound lesson callouts: `https://cosyplatform.com/courses/{iso}/{level}/{topic-slug}`.
   - Outbound header navigation: `https://cosylanguages.github.io/COSYlanguages/`.

---

## 8. Dead Weight

The following committed files, logs, generated reports, screenshots, one-off migration scripts, and stale documentation should be pruned to clean up repository clutter:

1. **Committed Screenshots & Playwright Artifacts:**
   - `reports/screenshots/cv_desktop.png`
   - `reports/screenshots/cv_mobile.png`
   - `reports/screenshots/el_desktop.png`
   - `reports/screenshots/el_mobile.png`
   - `reports/screenshots/en_desktop.png`
   - `reports/screenshots/en_mobile.png`
   - `reports/screenshots/fr_desktop.png`
   - `reports/screenshots/fr_mobile.png`
   - `reports/screenshots/it_desktop.png`
   - `reports/screenshots/it_mobile.png`
   - `reports/screenshots/ru_desktop.png`
   - `reports/screenshots/ru_mobile.png`

2. **One-Off Migration Reports & Audit Logs:**
   - `reports/cosylanguages_migration_verification_report.md`
   - `docs/migration/LINKS_NEEDING_EDITOR.md`
   - `docs/migration/known_broken_links.json`
   - `student-workbooks/data/UNMAPPED.md`

3. **Legacy Maintenance & Migration Scripts:**
   - `scripts/activate_lang_themes.py`
   - `scripts/apply_lang_accent.py`
   - `scripts/map_accent_tokens.py`
   - `scripts/cosy_manuals_migrate.py`

4. **Archived Legacy Tooling & Specs:**
   - `tools/legacy-generators/` (52 archived legacy Python scripts and template generators).
   - `docs/from-cosylanguages/` (24 archived spec files from previous site generation framework).

---

## 9. Deployment Architecture and Access Control Audit

### Deployment Architecture
- **Public Front-End Serving:** The repository is served statically via **GitHub Pages** or direct web host at the root `index.html`.
- **Static Assets:** All HTML manual pages (`manuals/*/*/*/*.html`), marathons (`marathons/*`), student workbooks, and teacher access pages are statically readable over HTTPS.
- **Dynamic Content Viewer:** Root `index.html` and `manuals/manual-viewer.html` use client-side JavaScript (`@supabase/supabase-js`) to fetch gated manual Markdown body text from Supabase database table `manual_content`.

### Access Control Architecture & Security Gaps
1. **Supabase Row-Level Security (RLS):**
   - Full manual body text is intended to be protected by Supabase RLS policies. Unauthenticated users browsing `index.html` are redirected to `https://cosylanguages.github.io/COSYlanguages/login.html?redirect=<manual-id>`.
   - **Gating Flaw:** The underlying static HTML manual pages (`manuals/en/grammar/a1/*.html`, `manuals/fr/grammar/b1/*.html`, etc.) are committed directly to Git and deployed publicly via GitHub Pages. Anyone with the direct URL can view complete manual pages without authenticating through Supabase.

2. **Teacher & Founder Access Portals:**
   - Teacher portals (`manuals/*/teacher-access.html`) and the Founder portal (`manuals/founder-portal.html`) rely on client-side role validation in `shared/js/auth-sso.js` and `shared/js/cms-editor.js`.
   - **Gating Flaw:** Because these HTML pages are static, client-side role checks can be bypassed by viewing page source or disabling JavaScript, exposing links to teacher notes, lesson keys, and CMS edit actions.

3. **Recommendations for Production Hardening:**
   - Prune full HTML manual content from public static hosting and rely exclusively on Supabase RLS gated fetching via `index.html` / `manual-viewer.html`.
   - Move teacher guides, student workbook answer keys, and teacher portals behind server-side authenticated routes in COSYplatform.
