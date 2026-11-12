# A0–A1 General Language Course: Lesson Authoring Specification

> **Document Status**: Canonical Authoring Specification
> **Course Scope**: A0–A1 General Language Course (Target Languages: `en`, `fr`, `it`, `ru`, `el`)
> **Target Audience**: Content authors, pedagogical engineers, and curriculum maintainers

---

## 1. Overview & Purpose

This document establishes the locked lesson specification for all A0–A1 General Language course materials across the COSY ecosystem. To maintain quality and pedagogical consistency across all target languages, every authored lesson must strictly adhere to the 10-point pedagogical framework, standard section ordering, native language adaptation rules, and file organization standards detailed below.

---

## 2. The 10-Point Pedagogical Framework

Every A0–A1 General lesson must satisfy all 10 criteria:

1. **Communication Goal ("I Can..." Outcome)**
   - Every lesson must state an explicit, action-oriented communicative goal using CEFR "I can..." statement format (e.g., *"I can introduce myself and exchange basic personal contact information"*).

2. **Vocabulary Requirements**
   - **Active Core Items**: 10–20 single lexical items or primary terms.
   - **Essential Chunks / Collocations**: 5–10 multi-word functional phrases or fixed collocations (not bare words).
   - **Functional Grouping**: Vocabulary tables must include a designated column explaining the communicative function or usage context for each item.

3. **Grammar Framework & Practice Stages**
   - **Communicative Framing**: Exactly one main grammar point framed around its communicative function, never as an abstract or isolated rule.
   - **Required Practice Types**: Must include all four practice modalities:
     1. *Controlled exercises* (e.g., gap fills, choice selection)
     2. *Substitution drills* (e.g., pattern-swapping exercises)
     3. *Question-answer practice* (e.g., targeted pair exchanges)
     4. *Personalised production* (e.g., meaningful self-expression tasks)

4. **Vocabulary Practice Progression**
   - Exercises must strictly follow a 5-step cognitive progression:
     `Recognition` &rarr; `Pronunciation` &rarr; `Matching / Classification` &rarr; `Controlled Production` &rarr; `Personalised Use`

5. **Four Skills Balance**
   - Every lesson must target all four language skills according to a strict distribution:
     - **Speaking**: ~70%
     - **Listening**: ~10%
     - **Reading**: ~10%
     - **Writing**: ~10%

6. **Three Duration Versions (Building Structure)**
   - Every lesson must provide three timestamped duration flows where each longer version builds directly upon the previous:
     - **60 minutes**: Core essential flow (Foundational input, controlled practice, primary production).
     - **90 minutes**: Standard expanded flow (Includes 60-min flow + extra fluency drills and deeper practice).
     - **120 minutes**: Comprehensive extended flow (Includes 90-min flow + extended roleplays, project work, and detailed feedback).

7. **Two Delivery Adaptations**
   - Every lesson must specify explicit adaptations for both delivery contexts:
     - **Individual (1-on-1)**: Focuses on teacher-student interaction, self-monitoring, and tailored pacing.
     - **Group (Classroom / Peer)**: Focuses on pairwork, group mingling, peer feedback, and dynamic interaction.

8. **Explicit Recycling System**
   - **Recycling from Previous Lesson**: Explicitly lists items/structures brought forward from the prior lesson.
   - **Recycling into Next Lesson**: Explicitly identifies target items/structures being prepared for reuse in the upcoming lesson.

9. **Realistic Scope & Domain Rules**
   - **Strict Domain Separation**: Never combine unrelated numeric or functional domains into a single lesson (e.g., do NOT combine numbers + dates + prices + phone numbers in one lesson).
   - Unrelated domains must be split into a logical sequential series (e.g., Lesson A: Cardinal Numbers & Phone Numbers &rarr; Lesson B: Dates & Calendar &rarr; Lesson C: Prices & Currency).

10. **Standardized 14-Section Order**
    - All lesson files must strictly follow the mandatory 14-section layout defined in Section 3 of this specification.

---

## 3. Standard 14-Section Lesson Order

Every authored lesson Markdown file must follow this exact section layout in order:

1. **Level**: CEFR Level (e.g., `A0–A1`)
2. **Duration Options**: Overview of available timeframes (`60 min / 90 min / 120 min`)
3. **Lesson Type**: Course categorization (e.g., `General Language - Core Communication`)
4. **Communication Goal**: "I can..." statement
5. **Recycling from Previous Lesson**: Reused vocabulary and structures
6. **Vocabulary**: Table with Core Items, Essential Chunks, IPA/Pronunciation, and Functional Context
7. **Pronunciation Focus**: Phonetic features, sentence stress, or intonation patterns
8. **Grammar Focus**: Communicative Rule + Structural System + 4 Practice Modal Subsections
9. **Lesson Flow (60 / 90 / 120 min)**: Timestamped stage-by-stage agenda
10. **Individual Adaptation**: Guidelines for 1-on-1 instruction
11. **Group Adaptation**: Guidelines for group/pairwork instruction
12. **Homework**: Consolidated assignment tasks
13. **Recycling into Next Lesson**: Items targeted for future reinforcement
14. **Teacher Notes & Common Pitfalls**: Diagnostic guidance and anticipated learner errors

---

## 4. Native Authoring & Multilingual Guidelines

### 4.1 Native Authoring vs. Machine Translation
Lessons across all target languages (`en`, `fr`, `it`, `ru`, `el`) **must be authored natively**, not translated word-for-word from English.
- **Cultural Realism**: Cultural references, names, cities, currencies, and real-world scenarios must reflect the target language's natural context (e.g., Paris/Euros for French, Rome/Euros for Italian, Moscow/Rubles for Russian, Athens/Euros for Greek).
- **Equivalence**: The **Communication Goal**, **Grammar Level**, and **Skills Ratio (~70/10/10/10)** must remain equivalent across all language versions to ensure a 1:1 cross-language curriculum mapping.

### 4.2 Language-Specific Grammar Realities

Authors must adapt the grammar presentation to match the authentic structure of each target language:

- **Russian (`ru`)**:
  - **Zero Copula**: The present tense of "to be" (*быть*) is typically omitted in basic nominative/identifying sentences (e.g., *"Я Анна"* / *"Это стол"*). Lesson 1 grammar for Russian must focus on non-copular naming structures rather than forcing an English-shaped copula explanation.
  - **Gender & Case Agreement**: Gender agreement (Masculine, Feminine, Neuter) and case forms must be introduced explicitly in lessons covering nationalities, professions, and possessives.

- **French (`fr`)**:
  - **Gender Agreement**: Adjectives and articles must explicitly show masculine and feminine agreements (e.g., *étudiant / étudiante*, *nationalité*).
  - **Elision & Binding**: Phonetic liaison and elision (e.g., *c'est*, *je m'appelle*) must be highlighted in pronunciation sections.

- **Italian (`it`)**:
  - **Gender & Number Agreement**: Adjectives and nouns must explicitly present masculine/feminine singular and plural endings (e.g., *italiano / italiana / italiani / italiane*).
  - **Subject Pronoun Omission**: Italian is a pro-drop language; natural usage omits subject pronouns (*"Sono Mario"* vs *"Io sono Mario"*), which must be highlighted.

- **Greek (`el`)**:
  - **Definite Articles & Gender**: Greek requires explicit handling of gendered articles (*ο, η, το*) and case inflection (Nominative/Accusative) even at A1.
  - **Pro-Drop Structure**: Greek naturally omits subject pronouns (*"Είμαι ο Γιώργος"*).

---

## 5. File Structure & Folder Conventions

Lessons are authored as Markdown documents (`.md`) placed within language-specific ISO subdirectories:

```text
lessons/
├── en/
│   └── a0-a1/
│       ├── lesson-01.md
│       ├── lesson-02.md
│       └── ...
├── fr/
│   └── a0-a1/
│       ├── lesson-01.md
│       └── ...
├── it/
│   └── a0-a1/
│       ├── lesson-01.md
│       └── ...
├── ru/
│   └── a0-a1/
│       ├── lesson-01.md
│       └── ...
└── el/
    └── a0-a1/
        ├── lesson-01.md
        └── ...
```

### Conventions Summary:
- **Path Pattern**: `lessons/{iso}/a0-a1/lesson-{XX}.md`
- **ISO Language Codes**: Standard 2-letter codes (`en`, `fr`, `it`, `ru`, `el`).
- **File Format**: Clean Markdown (`.md`).
- **Crosswalk Mapping**: Every `lesson-{XX}.md` maps 1:1 with the corresponding unit in `docs/a0-a1-unit-crosswalk.md`.
