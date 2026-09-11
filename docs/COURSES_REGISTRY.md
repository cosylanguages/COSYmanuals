# Courses Registry Documentation

The courses registry (`data/courses/courses.json`) serves as the central directory of all active course tracks, industry verticals, and language availability across COSYlanguages curriculums.

---

## 📂 Registry Architecture

`data/courses/courses.json` contains two primary arrays:

1. **`course_types`**: List of curriculum course types (e.g., `general`, `spoken`, `exam`, `travelling`, `professional`, `relocation`).
   - For tracks with domain-specific sub-tracks (such as `professional`), a `verticals` array lists available industry verticals (e.g., `it`, `marketing`, `career`).
2. **`languages`**: Language entries keyed by ISO 639-1 code (e.g., `en`, `fr`, `es`).
   - `course_types_available`: Array of active course type IDs for that language.
   - `levels_available`: Map of `course_type` ID to an array of existing CEFR levels (e.g., `["A1", "A2", "B1", "B2", "C1", "C2"]`).

---

## ➕ How to Add a New Course Type

When adding a brand-new course type across curriculums, follow the 5-step procedure outlined in `curriculums/_schema/README.md`:

1. **Update Schema README:** Add the new course type description to `curriculums/_schema/README.md`.
2. **Register in Registry:** Add the course type object (`id`, `label`, `description`) to the `course_types` array in `data/courses/courses.json`.
3. **Update Schema Enum:** Add the new course type string to the `course_type` enum in `curriculums/_schema/curriculum.schema.json`.
4. **Create Directory Structure:** Create the course folder under each active language directory (e.g., `curriculums/{iso}/{new_course_type}/`).
5. **Create Course Page:** Create matching course page or level JSON files under `curriculums/{iso}/{new_course_type}/{LEVEL}.json`.

---

## 🏢 How to Add a New Industry Vertical (Professional Track)

To add a new industry-specific vertical under the `professional` course track (as described in `curriculums/en/professional/VERTICALS.md`):

1. **Author Unit Content:** Author a unit object (typically 4 lessons) inside the appropriate level file (e.g., `curriculums/en/professional/B1.json`).
2. **Set Vertical Tag:** Set `"vertical": "<id>"` on the unit object (e.g., `"vertical": "finance"`).
3. **Register Vertical:** Add the new vertical object (`{ "id": "<id>", "label": "Display Name" }`) to the `verticals` array under the `professional` course type in `data/courses/courses.json`.
4. **Update Processing Tools:** Extend any outcome generator or reporting scripts (e.g., `scripts/build_cefr_outcomes.py`) if vertical-specific outcome tables are required.
