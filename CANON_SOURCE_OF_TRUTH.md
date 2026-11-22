# Ecosystem Canon Source of Truth Policy

This document establishes the official synchronization policy and authority hierarchy for canonical datasets within the COSY ecosystem (**COSYlanguages**, **COSYgames**, **COSYtools**, **COSYmanuals**).

---

## 1. Governance & Single Source of Truth Declarations

To prevent data divergence, duplicate maintenance, and drift across ecosystem repositories:

1. **Vocabulary Canon Authority**:
   - `vocabulary/_canonical/en/A0-A1_master.json` in **COSYlanguages** is the **sole writable master copy** of the A0-A1 English vocabulary canon for the entire COSY ecosystem.
2. **Curriculum Canon Authority**:
   - `curriculums/<lang>/<track>/<LEVEL>.json` (e.g., `curriculums/en/general/A1.json`) in **COSYplatform** is the **sole writable master copy** of curriculum data for the entire COSY ecosystem, validated by `curriculums/_schema/curriculum.schema.json`.
   - The files under `curriculums/` in this repository are pointers to those files, not copies. (This section previously named COSYlanguages as the master; COSYlanguages holds no curriculum data.)
3. **Read-Only Mirror Requirement**:
   - Any other repository or application within the COSY ecosystem (**COSYgames**, **COSYtools**, **COSYmanuals**) holding a copy or subset of these datasets MUST treat its local copy as a **read-only mirror** and label it as such.
4. **Change Management Protocol**:
   - Downstream repositories must **NEVER** edit local mirror copies directly.
   - Any proposed addition, removal, definition change, or spelling correction must be submitted to **COSYlanguages** via a GitHub Issue or Pull Request referencing the specific `word` / `word_id` or `lesson` / `unit` number.
   - Once merged in **COSYlanguages**, mirror repositories should update their read-only copies directly from this repository.

---

## 2. Drift Detection Utility Usage

A standalone checker tool is provided in `scripts/check-canon-drift.mjs` to detect and audit drift between local mirror files and the canonical files in `COSYlanguages`.

### Running the Checker

```bash
# Audit a vocabulary mirror against vocabulary/_canonical/en/A0-A1_master.json
node scripts/check-canon-drift.mjs path/to/mirror_A0-A1_master.json

# Audit a curriculum mirror against curriculum/en/general/A1.json
node scripts/check-canon-drift.mjs path/to/mirror_A1.json
```

### Options & Auto-Detection
- **Automatic Schema Detection**: The script automatically detects whether the input file is a **Vocabulary Canon** dataset or a **Curriculum** dataset.
- **Explicit Canon Target**: You can optionally pass `--canon <path_to_canon_file>` to override the canonical target file.

### Output Format
The checker outputs report blocks detailing:
- **Added Elsewhere**: Words or lessons present in the mirror but missing from the local canon source of truth.
- **Missing Elsewhere**: Words or lessons present in the local canon source of truth but missing from the mirror.
- **Field Modifications**: Mismatched POS, definitions, topics, or lesson titles between mirror and canon.

---

## 3. Propagation Notes for Sub-Repository READMEs

The following companion note must be added manually to the READMEs of downstream repositories.

### Repositories to Update:
- `COSYgames` (`README.md`)
- `COSYtools` (`README.md`)
- `COSYmanuals` (`README.md`)

### Snippet to Copy:

```markdown
> ⚠️ **Read-Only Mirror Notice**:
> The vocabulary dataset (`A0-A1_master.json`) in this repository is a **read-only mirror**. Curriculum files (`A1.json` - `C2.json`) are pointers to [COSYplatform](https://github.com/cosylanguages/COSYplatform), where the canonical curricula live.
> 
> **Do not edit these dataset files directly in this repository.** Proposed changes (word additions, definition edits, lesson adjustments) must be submitted as an Issue or PR to the repository that owns the data ([COSYplatform](https://github.com/cosylanguages/COSYplatform) for curricula) referencing the specific word or lesson ID. See `CANON_SOURCE_OF_TRUTH.md` in `COSYlanguages` for details.
```
