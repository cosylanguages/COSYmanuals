# COSYmanuals Content Architecture

This document defines the content architecture, taxonomy, schema relationships, and data organization across `COSYmanuals`.

---

## 1. Overview & Single-Source Authority

`COSYmanuals` serves as the primary content authority for all language manuals, CEFR-aligned grammar topics, vocabulary guides, pronunciation bootcamps, and grammatical confusion datasets across the COSY ecosystem.

The ecosystem separates concerns as follows:
- **`COSYmanuals`**: Static HTML manuals, printable booklets, grammar standards, CCQ guidelines, and structured reference datasets (`data/grammar/`).
- **`COSYplatform`**: Interactive course engines, learner progress tracking, and runtime exercise delivery (linking back to `COSYmanuals` topics via canonical URLs).

---

## 2. Directory Structure & Taxonomy

### Language Taxonomy (ISO 639-1)
All content is organized under standardized ISO 639-1 language codes across 14 supported languages:
`ba`, `br`, `cv`, `de`, `el`, `en`, `es`, `fr`, `hy`, `it`, `ka`, `pt`, `ru`, `tt`.

### Standardized Path Hierarchy
```
COSYmanuals/
├── CONTENT_ARCHITECTURE.md
├── index.html                             # Master Directory landing page
├── manuals/                               # Master Manuals Directory
│   ├── <lang>/                            # Root directory per language (e.g. en, fr, it, el, ru)
│   │   ├── index.html                     # Language entrypoint hub
│   │   ├── grammar/                       # Grammar section
│   │   │   ├── index.html                 # Grammar master index
│   │   │   ├── <level>/                   # CEFR level (a1, a2, b1, b2, c1, c2)
│   │   │   │   ├── index.html             # Level index
│   │   │   │   ├── part-1.html ...        # Part overview pages
│   │   │   │   └── topics/                # Individual topic HTML files
│   │   │   │       └── <topic-slug>.html
│   │   └── vocabulary/                    # Vocabulary section
│   │       └── <level>/
│   └── index.html                         # Master Manuals Registry
├── data/
│   ├── courses/
│   │   └── courses.json                   # Central course registry mapping
│   └── grammar/                           # Grammatical reference data
│       ├── confusions_en.json             # A vs B confusion guides
│       ├── confusions_fr.json
│       ├── confusions_it.json
│       ├── confusions_el.json
│       └── confusions_ru.json
└── shared/                                # Shared visual tokens, styles, and templates
    ├── styles/                            # Base, tokens, components, layout CSS
    └── templates/                         # Reusable HTML snippets (print buttons, etc.)
```

---

## 3. CEFR Manual HTML Staging (CELTA Inductive Standard)

All topic HTML pages under `manuals/<lang>/grammar/<level>/topics/` follow the strict 4-question, inductive CELTA discovery structure defined in `manuals/en/grammar/a1/GRAMMAR_STANDARD.md` (v3.0), and communication pages follow the standard defined in `manuals/en/communication/a1/COMMUNICATION_STANDARD.md`:

1. **Vocabulary / Thematic Anchor**: Communicative context.
2. **Situational Context Examples**: Character-driven example sentences.
3. **Guided Observation (👀 Notice)**: Inductive noticing question.
4. **Concept Check (🧠 Concept check / CCQs)**: Concept checking questions with answers.
5. **Main Rule & Formula (Table / Diagram)**: Formal rule summary.
6. **🧠 Think Like [Language]**: Systemic logic explanation.
7. **⚠ Common Mistakes**: Incorrect (`❌`) vs Correct (`✅`) interactive cards (`.mflip`).
8. **💡 Memory Trick**: Mnemonic memory trigger.
9. **🔗 Connects to...**: Sequential learning journey links.
10. **🎯 Self-Assessment Checklist**: Interactive progress checklist (`.checklist`).
11. **🎉 Diagnostic Quiz**: Interactive practice widget (`.quiz-panel`).

---

## 4. Machine-Readable Grammar Data Layer

In addition to user-facing HTML pages, `COSYmanuals` maintains structured JSON datasets under `data/grammar/`:

### 4.1 Grammatical Confusions Datasets (`confusions_<lang>.json`)
Provides canonical "A vs B" contrast data across CEFR levels (`a0_a2`, `b1_b2`):
- `id`: Unique slug (e.g., `because-vs-so`, `c-e-vs-ci-sono`).
- `level`: Target CEFR level (e.g., `A0-A1`, `A2`, `B1`).
- `point`: Concise contrast title.
- `core_difference`: High-level summary of distinction.
- `usage_a` / `usage_b` / `usage_c`: Contextual rules for each option.
- `examples`: Illustrative sentence pairs.
- `quick_logic`: Decision-tree rule of thumb.
- `common_mistakes`: Frequently observed learner errors with corrections.
- `memory_trick`: Visual or story-based memory trigger.

---

## 5. Relative Navigation & Asset Resolution

Topic HTML files located under `manuals/<lang>/<type>/<level>/topics/` are four levels deep relative to `manuals/<lang>/` and must observe relative asset pathing:
- **Shared CSS Tokens**: `../../../../shared/styles/tokens.css`
- **Shared CSS Base**: `../../../../shared/styles/base.css`
- **Shared CSS Components**: `../../../../shared/styles/components.css`
- **Shared CSS Layout**: `../../../../shared/styles/layout.css`
- **Level Local Assets**: `../assets/style.css` and `../assets/app.js`
- **Language Hub Root**: `../../../index.html`
