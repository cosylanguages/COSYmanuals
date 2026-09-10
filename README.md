# COSYmanuals

**COSYmanuals** is a private, direct-link accessible repository containing detailed curriculums, marathons, manuals, teacher guides, and student workbooks for contracted students and teachers of COSYlanguages.

---

## 🔒 Access Model & Privacy Notes

- **Link-Only Access:** This repository is intentionally unlinked from public site navigation on the main hub. Access is granted exclusively via direct links shared by COSYlanguages or contracted instructors.
- **Privacy Notice:** The landing page (`/index.html`) serves as an access boundary for uninvited visitors, explaining the direct-link model and pointing to the main contact hub.
- **No Indexing / Public Directory:** Do not link this repository publicly on social media or public navigation menus.

---

## 📂 Directory Structure

```text
/curriculums/
  /english/
    /beginner-a1/
    /elementary-a2/
    /intermediate-b1/
    /upper-intermediate-b2/
    /advanced-c1/
    /professor-c2/
  /french/
  /italian/
  /russian/
  /greek/
/marathons/
  /speaking-marathon-30-days/
  /pronunciation-bootcamp/
    /levels/
    /js/
  /vocabulary-marathon-500-words/
  /grammar-intensive-14-days/
/teacher-guides/
  /lesson-plans/
  /game-based-learning/
  /assessment-tools/
/student-workbooks/
  /data/
  /worksheets/
  /answer-keys/
  /progress-trackers/
/shared/
  /templates/
  /styles/
/templates/
  /curriculum/
  /grammar/
  /vocabulary/
  /communication/
```

---

## 🗺️ Multi-Stage Migration Plan from COSYlanguages

To systematically decouple and migrate all manuals, marathons, and curriculums from `COSYlanguages`, the migration is structured into logical stages:

- **Stage 1 (Completed): Simple & Self-Contained Resources**
  - French Pronunciation Marathon suite (`marathons/pronunciation-bootcamp/`) including levels A0–C2 and engine JS.
  - Core curriculum, grammar, vocabulary, communication, and lesson plan templates (`templates/`, `teacher-guides/lesson-plans/`).
  - Student workbook datasets (`student-workbooks/data/workbook_data.js`).
- **Stage 2 (Completed): Core Language Curriculums**
  - Migration of structured CEFR curriculum schemas and JSON datasets for all supported languages (`curriculum/` from COSYlanguages into `curriculums/`), covering 14 target languages (`en`, `fr`, `de`, `es`, `it`, `el`, `ru`, `pt`, `hy`, `ka`, `tt`, `ba`, `cv`, `br`) across general, spoken, exam, professional, travelling, and relocation course tracks.
- **Stage 3: Language Manuals, Grammar References & Vocabulary Datasets**
  - Full migration of standalone language manuals (`manuals/`), monolingual grammar references (`grammar/`), and thematic vocabulary datasets (`vocabulary/`).

---

## 🧭 How to Navigate Manuals

1. **Curriculums:** Navigate to a specific language and level index page (e.g., `/curriculums/english/intermediate-b1/index.html`) to view course overview, prerequisites, unit breakdown, and progress tracking.
2. **Units:** Each unit page (e.g., `unit-1.html`) provides unit objectives, key vocabulary, grammar points, speaking exercises, practice activities, homework assignments, and self-assessment checklists.
3. **Marathons:** Access intensive challenge courses (e.g., `/marathons/speaking-marathon-30-days/index.html`) for daily schedules, streak trackers, leaderboards, and completion certificates.
4. **Teacher Guides:** Access pedagogical strategies, lesson plan architecture, assessment rubrics, and online/offline best practices at `/teacher-guides/index.html`.

---

## 🔗 COSY Ecosystem Integration & Practice Links

All manuals integrate directly with other COSY ecosystem repositories. Every page includes practice resource links that open in new tabs (`target="_blank"`):

- 🎮 **[COSYgames](https://cosylanguages.github.io/COSYgames/):** Vocabulary challenges, grammar quizzes, and interactive games.
- 🛠️ **[COSYtools](https://cosylanguages.github.io/COSYtools/):** Dictionary lookups, verb conjugation tables, and phonetic guides.
- 🌍 **[COSYworld](https://cosylanguages.github.io/COSYworld/):** Contextual roleplays and immersive scenarios.
- 🏠 **[COSYlanguages](https://cosylanguages.github.io/COSYlanguages/):** Main hub and contact point.

---

## 🧑‍🏫 Integration Guide for Teachers

- **Flipped Classroom:** Assign unit reading and COSYtools vocabulary lookups prior to live sessions.
- **In-Class Application:** Use speaking prompts and COSYgames multiplayer mode during live lessons.
- **Progress Tracking:** Encourage students to complete self-assessment checklists at the end of each unit.

---

## 📩 Requesting New Content

Contracted teachers and curriculum designers can request new units, marathons, or language tracks by contacting the COSYlanguages administrator or submitting a content request issue in the private repository management queue.

---

*© COSYlanguages. Private and confidential resource.*
