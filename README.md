# COSYmanuals

**COSYmanuals** is a public catalog and gated learning portal holding grammar, vocabulary, and communication manuals for students and teachers of COSYlanguages.

---

## 🔒 Security & Privacy Rules

> **IMPORTANT:** This repository's git history must **NEVER** contain manual body text, only public catalog metadata and app code.

- **Public Catalog (`catalog/`):** Contains public metadata JSON files (`title`, `language`, `level`, `short_description`).
- **Gated Content Storage (Supabase):** Full manual body text is stored exclusively in Supabase under the `manual_content` table with Row Level Security (RLS) policies.
- **Local Drafts (`drafts/`):** Local Markdown draft files are strictly gitignored (`drafts/` in `.gitignore`) and published directly to Supabase via `scripts/publish_to_supabase.js`.
- **Authentication:** Unauthenticated users browsing the public catalog are redirected to `https://cosylanguages.github.io/COSYlanguages/login.html?redirect=<manual-id>`. Authenticated users fetch content live from Supabase.

---

## 🚀 Publishing Manual Content to Supabase

1. Create or edit local Markdown drafts inside `drafts/` (e.g. `drafts/en-b1-grammar.md`).
2. Ensure you have a local `.env` file containing:
   ```env
   SUPABASE_URL=https://your-supabase-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
3. Run the local publisher script:
   ```bash
   node scripts/publish_to_supabase.js
   ```
4. DB Schema can be updated using `scripts/schema.sql`.

---

## 📂 Directory Structure

```text
/catalog/                  # Public metadata JSON per manual (no body text)
  manifest.json
  en-b1-grammar.json
  fr-a2-vocabulary.json
  ...
/drafts/                   # GITIGNORED local Markdown draft manuals
/scripts/
  publish_to_supabase.js   # Local publisher script for pushing drafts to Supabase
  schema.sql               # Supabase database schema & RLS policies
/curriculums/              # Course curriculums & CEFR level structures
/marathons/                # Interactive bootcamps and marathons
/teacher-guides/           # Pedagogical guides and lesson plans
/shared/                   # Shared CSS styles, tokens, and templates
```

---

## 🔗 COSY Ecosystem Integration

- 🎮 **[COSYgames](https://cosylanguages.github.io/COSYgames/):** Interactive games and quizzes.
- 🛠️ **[COSYtools](https://cosylanguages.github.io/COSYtools/):** Dictionaries, conjugation tables, phonetic guides.
- 🏠 **[COSYlanguages](https://cosylanguages.github.io/COSYlanguages/):** Main platform and authentication hub.

---

*© COSYlanguages. Public Catalog & Secure Manual Repository.*
