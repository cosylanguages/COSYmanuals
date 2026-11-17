> **Recovered document.** The copy in `docs/from-cosylanguages/` had all whitespace
> stripped by a lossy copy, leaving a single unreadable line. Line structure and 62% of
> word spacing were restored automatically against the current editions of this standard
> (see `COSYstudio/scripts/repair-stripped-markdown.py`). The section from "CELTA
> Lesson-Stage Alignment" onward is unique to this draft, so its spacing could not be
> recovered and still needs a manual pass.

# COSYlanguages Grammar Standard v1.0, v2.0 & v3.0 (Russian Revision)

This document defines the strict, unified standards for all digital and print grammar materials across COSYlanguages. Every lesson, manual, reference page, and printable sheet must adhere 100% to this specification.

---

## 1. The Core Principles

### Principle 1: The Four Standard Questions
Regardless of language or level, every grammar pagelesson must answer the following four questions to provide predictable structure for both students and teachers:
- **What is it?** (Clear identification)
- **When do I use it?** (Context & usage scenario)
- **How do I build it?** (Structure & formulas)
- **What mistakes do beginners make?** (Real-life learner pitfalls)

### Principle 2: Standardized Page Rhythm (Phase 2 & 3 Standard)
Every grammar page must follow an identical visual and logical rhythm to create familiarity for the learner. The standard rhythm sequence is:

1. **Vocabulary Theme:** Natural thematic anchor (e.g., *Family*, *Food*, *Travel*).
2. **Grammar Title:** Large, clear, never clever.
3. **One-Line Summary:** Exactly one sentence summarizing the core rule.
4. **Why is this important?Why learners struggle:** Highlighting importance & difficulty.
5. **Main Visual (DiagramFlow):** Replacing long paragraphs with CSS diagrams.
6. **Colour Example:** Standard color-coded examples.
7. **Guided Observation (👀 Notice):** A single inductive question for pattern discovery.
8. **🧠 Think like [Language]:** Explaining the systematic logic of the language.
9. **🇷🇺 Why does Russian do this?🧩 Russian Pattern (Language Signature boxes):** Systemic reasons & recurring patterns.
10. **⚠ Common Mistakes:** Stacked `❌` (Incorrect) and `✅` (Correct) patterns.
11. **💡 Memory Trick:** Visually-anchored, story-based memory trigger.
12. **🔗 Connects to...:** Sequential learning journey links.
13. **📍 Can you already use this?:** A communication-focused self-evaluation checklist.
14. **🎉 Progress Celebration:** Highlighting unlocked real-world skills.

---

## 2. Priority Upgrades & Editorial Style (Phase 2 & 3)

### Priority 1: Give Languages Personality ("Think like...")
Don't just explain mechanical rules; explain **why** the language functions as a system. Use the `"🧠 Think like [Language]"` box to teach system logic:
- *English:* Focus on word order and auxiliary verbs as structural builders.
- *Russian:* Focus on cases, aspect (complete vs incomplete actions), stability vs stress shift, and softhard endings.

### Priority 2: Diagrams Over Paragraphs (The COSY Rule)
If a concept can be illustrated visually, never write it in text.
- *Example (Russian Case Map Flow):* Instead of raw listings, show:
  `WHO?` (Nom.) ➔ `owns?` (Gen.) ➔ `to?` (Dat.) ➔ `see?` (Acc.) ➔ `with?` (Instr.) ➔ `about?` (Prep.)

### Priority 3: Endings as Families
Grouping endings helps learners recognize patterns.
- *Example (Feminine family):* `-а` and `-я` are part of the feminine family and behave similarly.
- *Example (Adjective family):* `-ый` and `-ой` belong to the same adjective pattern.

### Priority 4: Progressive Exceptions
Never overwhelm beginners with Exceptions immediately. Introduce the dominant pattern first, build structural confidence, and only then introduce exceptions as separate or secondary notes.

### Priority 5: Recognition Before Production
Encourage passive pattern identification before demanding productive conjugation or declension. Use guided observations (e.g., *"Can you spot which word is in the Genitive case?"*).

### Priority 6: Signature "🧩 Russian Pattern" Box
A visual highlighting component that links seemingly new structures back to familiar base patterns:
- *Example:* Showing how the stem `чита-` stays fully stable across `читаю`, `читаешь`, `читает` while only endings change.

### Priority 7: "🇷🇺 Why does Russian do this?" Box
Provides linguistic rationale to make features that seem arbitrary to adults highly sensible and memorable (e.g., *Why six cases? Because they make word order flexible and tenses highly compact!*).

### Priority 8: Progress Celebrations (🎉 You can now...)
End major milestones by celebrating exactly what skills have been unlocked (e.g. *"🎉 You can now introduce yourself, describe family, and identify daily items!"*).

---

## 3. Standard Visual Color Language & Approved Icons

| Element
| Color
| Semantic Class
| Variable |
|:

---

|:

---

|:

---

|:

---

|

| **Subject**
| Blue
| `.key-subject``.key-blue`
| `var(--grammar-subject)` |

| **Verb**
| Green
| `.key-verb``.key-green`
| `var(--grammar-verb)` |

| **Object**
| Orange
| `.key-object``.key-orange`
| `var(--grammar-object)` |

| **Ending**
| Purple
| `.key-ending``.key-purple`
| `var(--grammar-ending)` |

| **Adjective**
| Yellow
| `.key-adjective``.key-yellow`
| `var(--grammar-adjective)` |

| **Error**
| Red
| `.key-error``.key-red`
| `var(--grammar-error)` |

| **Optional**
| Grey
| `.key-optional``.key-grey`
| `var(--grammar-optional)` |

### Approved Icon Set:
- `⚠` Common mistakeWhy this is difficult
- `💡` Memory trick
- `👀` NoticeGuided observation
- `🧠` Think like a native speakerThink like English
- `🔗` Connects to...
- `✓` Correct
- `✗` Incorrect
- `🌍` Regional variation
- `⭐` Important rule
- `🧩` Language Pattern (Signature)
- `🇷🇺` Language RationalWhy does Russian do this?
- `🎉` Progress Celebration

---

## 4.

CELTALesson
- StageAlignment(Phase4Standard)The14-steppagerhythm(Section1,Principle2)is the**authoring**rhythm—ittellsawriterhowtolayoutatopicpage.

TheCELTAlesson-stagemodelisthe**pedagogical**rhythm—ittellsa teacherhowtoru nthelesson.

Theyarecomplementary,notcompeting.

Everytopicpageshouldbe**stageable**:its14authoringstepsmustmapcleanlyontothe6CELTAstagessothe samepageservesbothself-studyreadersandclassroomteachers.

### The6CELTAStages
1. **Lead-inContext**—engageschema,introducethetargetiteminarealcontext.
2. **MeaningCheck(CCQs)**—verifyunderstandingofmeaningwithconcept checkingquestions(yesnoorshortfactual),nevertranslation.
3. **Form**—structuralformulas,tables,conjugationpatterns("Thinklikeanativespeaker").
4. **Pronunciation**—stress,weakforms,liaison,intonation.
5. **Controlled→FreerPractice**—accuracy-firstdrillsmovingtowardfluency.
6. **Production&Feedback**—communicativeuse+delayederrorcorrection.

### Howthe14StepsMapontothe6Stages
|CELTAStage
|Authoringsteps(Section1)
||:

---

|:

---

|
|
1. Lead-inContext
|1VocabularyTheme,2GrammarTitle,3One
- LineSummary,4Whyitmatters,5MainVisual,6ColourExample
|
|
2. MeaningCheck(CCQs)
|7GuidedObservation(👀Notice)
|
|
3. Form
|8Thinklike[Language],9LanguageSignatureWhydoes[Language]dothis?
|
|
4. Pronunciation
|(addapronunciationnoteblockwhererelevant—see`manuals_TEMPLATE.md`Stage4)
|
|
5. Controlled→FreerPractice
|10CommonMistakes(❌✅),11MemoryTrick,12Connectsto...(IncludeICQswhenpracticeactivitymechanicsarenon-obvious,e.g.pairwork,timedtasks,role-play)
|
|
6. Production&Feedback
|13Canyoualreadyusethis?,14ProgressCelebration|

### CanonicalImplementation
- **Human-facingHTML**:everytopicpagein`manuals{lang}grammar{level}topics*.html`followsthe6-stagemarkupblueprintin`manuals_TEMPLATE.md`,whichbakesinastandardized`💡Checkyourunderstanding(CCQs)`block(Stage2).
- **Machine-readableJSON**:everylessonunitisstructuredas`schemalesson-stage.schema.json`dataunder`reference-grammar{lang}lessons*.json`.

The`meaningCheck`arrayholdsinlineCCQobjects(`schemaccq.schema.json`),and`controlledPractice``freerPractice``production`linkouttotheCOSYecosystem(`COSYtools`,`COSYgames`,`COSYevents`,``).
- **Validation**:`scriptsvalidate-schema.js`validatesalllivelesson-stageandCCQdatafiles;`scriptsbuild_unified_index.py`cross-referencestheminto`dataindex{lang}_index.json`.

### GrowingTaskMonologue&DialoguePolicies
- **PolicyA(Review&ExamScope)**:Reviewandexamlessons(identifiedbylessontitlecontaining"review"or"exam",ortype`"srev"``"exam"`)neverreceivea`growingTask`entry.
- **PolicyB(Self-PortraitMonologueThread)**:`growingTask.selfPortrait`isoptional.

Include`selfPortrait`onlywhenanatural,coherentfirst-personmonologuesentencecanbeconstructedusingtargetlanguageitemslearneduptothatlesson.

Forfunctionalconversationallessons(greetings,politenessformulas,phoneopeners),omit`selfPortrait`andprovide`growingTask.dialogue`only.

### AuthoringRuleWhenaddingoreditingatopic,satisfy**both**rhythms:laythepageoutusingthe14authoringsteps,andmakesureeachofthe6CELTAstagesisexplicitlypresentandlabelled.

The6-stagestructureisthecontracta teachercanrelyon;the14stepsarehowyoufillitinbeautifully.
