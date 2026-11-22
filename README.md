# COSYmanuals

**COSYmanuals** is an open (public) repository and website holding grammar, vocabulary, communication manuals, teacher guides, and offline print booklets for students and teachers of COSYlanguages.

---

## 🔒 Security & Privacy Rules

> **Status (decision 2026-11-16): all manuals are open for now.** The repository and its GitHub Pages site are public and every manual page is readable without login. Nothing is paid yet. Do not put anything here that must stay private (answer keys, teacher notes, personal data, secrets).
>
> The gating tools below (`manual_to_record.py`, `load_records_to_supabase.js`, `publish_to_supabase.js`, the `manual_content` table) are kept for a possible future paid tier. They are not in use. If paid manuals are introduced later, the text already in this repository's git history stays public, so only new, never-published content can be protected this way.

- **Public Catalog (`catalog/`):** Contains public metadata JSON files (`title`, `language`, `level`, `short_description`).
- **Gated Content Storage (Supabase):** Full manual body text is stored exclusively in Supabase under the `manual_content` table with Row Level Security (RLS) policies.
- **Local Drafts (`drafts/`):** Local Markdown draft files are strictly gitignored (`drafts/` in `.gitignore`) and published directly to Supabase via `scripts/publish_to_supabase.js`.
- **Authentication:** Unauthenticated users browsing the public catalog are redirected to `https://cosylanguages.github.io/COSYlanguages/login.html?redirect=<manual-id>`. Authenticated users fetch content live from Supabase.

---

## 🚀 Publishing Manual Content to Supabase

1. Create or edit local Markdown drafts inside `drafts/` (e.g., `drafts/en-b1-grammar.md`).
2. Ensure you have a local `.env` file containing:
   ```env
   SUPABASE_URL=https://your-supabase-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
3. Validate the catalog and run automated tests:
   ```bash
   node scripts/validate-catalog.mjs
   node --test
   node scripts/check-internal-links.mjs manuals
   ```
4. Run the publisher in dry-run mode first. It validates draft filenames, content, and catalog metadata without network requests or credentials:
   ```bash
   node scripts/publish_to_supabase.js --dry-run
   ```
5. Only after reviewing the dry-run output, publish from a trusted local environment with the required Supabase credentials:
   ```bash
   node scripts/publish_to_supabase.js
   ```
6. Review `SECURITY_REVIEW.md` before any production database changes. The SQL schema is not a substitute for auditing all deployed grants and RLS policies.

---

## 📂 Directory Structure

```text
/catalog/                  # Public metadata JSON per manual (no body text)
  manifest.json
  en-b1-grammar.json
  fr-a2-vocabulary.json
  ...
/curriculums/              # Course curriculums & CEFR level structures
  _schema/                 # JSON Schema validation definitions
  {iso}/                   # Language folders (e.g. en, fr, ru, de, es, it, el, pt, hy, ka, ba, br, tt)
    {track}/               # Course tracks (general, spoken, exam, professional, travelling, relocation)
      {LEVEL}.json         # CEFR level curriculum datasets (A1.json, A2.json, B1.json, etc.)
/drafts/                   # GITIGNORED local Markdown draft manuals
/manuals/                  # Rendered HTML manual pages, topic guides, and offline booklets
  {iso}/                   # Language manual trees (e.g. manuals/en/, manuals/fr/)
    {module}/              # Learning modules (grammar, vocabulary, communication)
      {level}/             # CEFR level manuals and topic pages
    print/                 # Offline A4 print reference booklets
/marathons/                # Interactive bootcamps and marathon syllabus reference hubs
/scripts/                  # Publisher, migration, audit, and verification scripts
/shared/                   # Shared CSS styles, design tokens, and templates
/student-workbooks/        # Student workbook supplementary materials & printable worksheets
/teacher-guides/           # Pedagogical guides and lesson pacing plans
```

---

## 🌐 Supported Languages & Availability

COSYmanuals coordinates with **COSYplatform** across 13 core ISO languages, while providing manual reference and print booklet structures for additional languages in expansion:

### Active Languages in COSYplatform (13)
- 🇬🇧 **English (`en`)** — Full CEFR coverage (`A1`–`C2`) across all tracks.
- 🇫🇷 **French (`fr`)** — Full CEFR coverage (`A1`–`C2`) across all tracks.
- 🇷🇺 **Russian (`ru`)** — Full CEFR coverage (`A1`–`C2`) across all tracks.
- 🇩🇪 **German (`de`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🇪🇸 **Spanish (`es`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🇮🇹 **Italian (`it`)** — `A1` available (`A0`, `A2`, `B1`, `B2`, `C1`, `C2` planned).
- 🇬🇷 **Greek (`el`)** — `A1` available (`A0`, `A2`, `B1`, `B2`, `C1`, `C2` planned).
- 🇵🇹 **Portuguese (`pt`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🇦🇲 **Armenian (`hy`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🇬🇪 **Georgian (`ka`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🏴 **Bashkir (`ba`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🏴 **Breton (`br`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).
- 🏴 **Tatar (`tt`)** — `A1`, `C1` available (`A0`, `A2`, `B1`, `B2`, `C2` planned).

### Planned Languages
- 🏴 **Chuvash (`cv`)** — *Planned, not yet available in COSYplatform.* Manual booklet templates and grammar/vocabulary reference hubs exist in COSYmanuals (`manuals/cv/`) for offline print and future platform onboarding.

---

## 🎓 Course Tracks & Content Categories

To ensure 1:1 synchronization with COSYplatform, COSYmanuals uses standardized course track and content module nomenclature across all curriculums, roadmaps, and manuals:

### Curriculum Course Tracks (`/curriculums/{iso}/{track}/`)
- **`general`** — Standard General CEFR course progression.
- **`spoken`** — Spoken language, conversational skills, and speech practice.
- **`exam`** — CEFR exam preparation (IELTS, DELF, TORFL, Goethe, etc.).
- **`professional`** — Business and career English/French/Russian with domain verticals (`it`, `marketing`, `career`, `finance`).
- **`travelling`** — Situational travel and navigation language.
- **`relocation`** — Expat integration, living abroad, and administrative language.
- **`discussion`** — COSYplatform only: the speaking clubs run in COSYevents, converted into lessons. No COSYmanuals folder and no COSYlanguages course page.
- **`pronunciation`** — Planned as a marathon / course in COSYplatform (curricula exist, not launched yet). Until then, pronunciation guides stay a content module here (see below).

The full list lives in COSYplatform: `curriculums/_schema/course-types.json` (documented in `docs/COURSE_TYPES.md`). On the COSYlanguages site the exam course page is named `exam-preparation.html`; `exam.html` redirects to it.

### Content Tracks & Reference Modules (`/manuals/{iso}/{module}/`)
- **`grammar`** — Structural grammar explanations, CCQ checks, and rule tables.
- **`phrasal-verbs`** — Dedicated phrasal verb and particle usage guides.
- **`vocabulary`** — Topic-based lexical sets and visual dictionary modules.
- **`pronunciation`** — Phonetic diagrams, IPA guides, and accent bootcamps.
- **`introductory`** — Foundation alphabet, phonetics, and pre-A1 starter modules.
- **`communication`** — Manual-only folder (`/manuals/{iso}/communication/`). Not a course type and it has no curriculum.

---

## 📈 CEFR Level Range & Coverage Alignment

- **COSYplatform Live Coverage:** Active live interactive courses run **`A0`–`C1`** for most languages, with **`C2`** active for English (`en`), French (`fr`), and Russian (`ru`). `A0` level modules are designated as planned across languages.
- **COSYmanuals Intentional Scope:** COSYmanuals holds manual reference guides, teacher handbooks, and print booklet layouts (`/manuals/` and `/student-workbooks/`) covering the complete `A0` through `C2` CEFR spectrum. Where COSYmanuals contains reference material for levels not yet live in COSYplatform, outbound links route students to the nearest active level hub with coming-soon badges.

---

## 🔗 COSY Ecosystem Integration

- 🚀 **[COSYplatform](https://cosyplatform.com):** Interactive teaching & learning platform, canonical curriculum authority, and live lesson player.
- 📊 **[COSYdata](https://cosylanguages.github.io/COSYdata/):** Central vocabulary dictionary, phonetics engine, and static linguistic datasets.
- 🎮 **[COSYgames](https://cosylanguages.github.io/COSYgames/):** Interactive games and learning quizzes.
- 🛠️ **[COSYtools](https://cosylanguages.github.io/COSYtools/):** Dictionaries, conjugation tables, and phonetic guides.
- 🏠 **[COSYlanguages](https://cosylanguages.github.io/COSYlanguages/):** Main platform catalog and authentication hub.

> ⚠️ **Read-Only Mirror Notice**:
> The curriculum files in `/curriculums/` are pointers to COSYplatform, where the canonical curricula live (`curriculums/<lang>/<track>/<LEVEL>.json`). The vocabulary dataset (`A0-A1_master.json`) is a **read-only mirror**.
>
> **Do not edit these dataset files directly in this repository.** Proposed changes (word additions, definition edits, lesson adjustments) must be submitted as an Issue or PR to the canonical source repository. See `CANON_SOURCE_OF_TRUTH.md` for details.

---

*© COSYlanguages. Public Catalog & Secure Manual Repository.*
