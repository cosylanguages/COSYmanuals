# Representative manual quality review

Review date: 2026-10-22

Scope: representative public HTML pages in the English A0–A1 grammar tree and French A0–A1 grammar tree. This is a focused sample, not a complete language or curriculum audit.

## English A0–A1: Part 1, “The Building Blocks of English”

Reviewed: `manuals/en/grammar/a1/topics/part-1-building-blocks.html` and its linked index.

### Strengths
- Clear topic grouping and an explicit learning-outcome banner.
- Examples cover practical beginner tasks such as spelling names, reading prices, telling time, and recognizing abbreviations.
- Includes common mistakes, a self-check checklist, a short quiz, and next-topic navigation.
- Main navigation has an accessible label; native buttons and checkbox inputs are used for interactions.
- The shared stylesheet includes print-specific rules that remove some screen-only navigation and reveal answer explanations.

### Issues to address
1. **Quiz relevance:** the opening comprehension-check questions were generic and did not assess the page's actual learning outcomes. They have been replaced with concrete capitalization and abbreviation questions.
2. **Scope overload:** one A0–A1 page covers alphabetization, spelling, phonology, connected speech, suffix pronunciation, numbers, money, dates, time, and fractions. Split into shorter learning units or clearly mark optional/reference sections.
3. **Pronunciation variation:** several IPA examples assume a particular accent (for example, vowel values in “car”, “hope”, and “teacher”). Label the reference accent and provide a note that pronunciation varies by variety of English.
4. **Overgeneralized rule:** the “Magic-E” description reads as universal. Present it as a useful spelling pattern with exceptions (for example, “have”, “give”, and “love”) rather than a rule without exceptions.
5. **Objective alignment:** the outcome promises accurate use of dates, prices, pronunciation, and fractions, but the opening quiz only sampled two small areas. Add short, specific practice tasks for the remaining outcomes.
6. **Accessibility verification:** inspect all quiz JavaScript for keyboard operation, focus visibility, answer announcement, and score updates. A visual review alone cannot confirm that dynamic feedback is announced to assistive technology.
7. **Print behavior:** print CSS reveals quiz explanations and hides some navigation, but headings may force a page break before every H1. Test real print/PDF output to avoid unnecessary blank pages and verify tables/examples do not split badly.

## French A0–A1: grammar index and noun-gender lesson

Reviewed: `manuals/fr/grammar/a1/index.html`, `domaine-1.html`, and `topics/genre-des-noms-1.html`.

### Strengths
- French language metadata is correctly declared with `lang="fr"`.
- The index organizes the content into named domains and gives learners a sentence-building interaction.
- The domain overview links to a continuous, printable version, which is a useful alternative to topic-by-topic navigation.
- The reviewed lesson shell explains that the full text is protected and gives a login action plus a route back to the index.

### Limits and issues to address
1. **Gated body not reviewable in Git:** the sampled noun-gender page is a protected-content shell, not the actual lesson body. Grammar accuracy, exercise quality, answer keys, and pedagogical sequencing must be reviewed by an authorized reviewer using a staging/test account; do not copy protected body text into Git or a public PR.
2. **Navigation path check:** the index uses a relative hub link and multiple domain links. The new local-link checker should verify these paths against the built/static repository, while noting that it cannot validate authentication redirects or remote URLs.
3. **Interaction accessibility:** test the sentence builder with keyboard only, screen readers, and touch. Ensure chosen words and the final sentence are exposed as text and do not rely on color alone.
4. **Content claims:** the index advertises 62 pages and specific feature counts. Verify these figures against the actual published/staging content and keep them synchronized as lessons change.
5. **Print alternative:** retain the continuous-reading version, but test page breaks, heading repetition, link visibility, and answer disclosure in a browser-generated PDF.

## Shared acceptance checklist before scaling

- Learning outcomes are observable and matched to practice.
- Each rule has accurate, natural examples and an exception/variation note where needed.
- Exercises assess the content taught and provide actionable feedback.
- Navigation has descriptive link text, a logical heading structure, and keyboard-visible focus.
- HTML declares the correct language; images and interactive controls have accessible names/alternatives.
- Color contrast and reflow pass a real browser-based accessibility check.
- Print/PDF output is readable, avoids clipped content, and does not rely on hover or color.
- A proficient speaker/teacher reviews language accuracy before a manual is marked approved.

No full French gated lesson content was reviewed in this pass; that remains an explicit follow-up rather than an assumed pass.


## Supplemental read-only review: live Supabase French A1 pronunciation content

Reviewed on 2026-10-22 from the connected Supabase project's `public.lesson_content` rows (read-only; no content was changed):
- `fr-pron-a1-01-alphabet` — “L'Alphabet et les sons fondamentaux”
- `fr-pron-a1-02-accent-aigu` — “L'Accent Aigu (É) et le son [e]”
- The A1 French workbook JSON at `student-workbooks/data/workbooks/fr/a1.json`

This is a sample review of database content, not proof that the connected project is staging. The project had no development branches listed, so treat it as potentially production. No database write tests or content edits were performed.

### High-priority accuracy corrections

1. **Separate letter names from grapheme-to-sound examples.** The alphabet lesson lists “C [se] (chat)” and “E [ə] (eau)” in a sequence of letter-name/word examples. The letter names C /se/ and E /ə/ are not the pronunciations of the initial letters in *chat* and *eau*: *chat* begins with /ʃ/ (the digraph **ch**), and *eau* begins with /o/. As written, these pairings teach a false association. Use examples that match the target sound (e.g. C — *ce* for the letter name, and *chat* only in a separate **ch** spelling example; E — *le* for a schwa example, and *eau* under /o/).
2. **Correct the categorical statement about K and W.** The lesson says K and W are “reserved for words of foreign origin.” This is too absolute for a beginner rule; explain that they are less common in inherited French vocabulary and occur especially in loanwords, names, and established exceptions.
3. **Clarify the six-vowel statement.** “Six pure vowels” can conflate written vowel letters (A, E, I, O, U, Y) with phonetic vowel sounds. State explicitly that this is a spelling/alphabet convention, and distinguish it from the French vowel phoneme inventory.
4. **Fix the accent aigu exception field.** The lesson treats omission of accents in uppercase loanwords as an exception. That is not a useful phonetic exception and risks implying that accents should be dropped in capitals. Teach that French accents are retained on capital letters in standard modern French typography; if discussing inconsistent real-world typography, label it as a common error, not a rule.
5. **Qualify the schwa rule.** “E without an accent = [ə]” is an overgeneralization. Use a small set of clear examples and note that schwa realization/deletion varies with word, context, speech rate, and variety.

### Pedagogical structure and usability

- The alphabet lesson's three stages each show a 50-minute duration while the overall lesson also declares a 50-minute default. Reconcile per-stage durations with the stated lesson duration, or label these as suggested durations that can be adjusted.
- The repeated 14-field template creates consistent teacher notes, but it overloads a beginner-facing lesson with abstract fields such as frequency stars, historical etymology, exceptions, and meta labels. Keep the full framework in teacher notes; expose learners first to a small objective, a clear model, guided discrimination, short retrieval practice, and a recap.
- The workbook's English-only exercise prompts (e.g. asking “How do you say ‘Hello’ in French (formal)?”) may be intentional for English-medium instruction, but the interface should clearly state its instructional language and offer French learner-facing directions or accessible language support where appropriate.
- The workbook groups greetings, accents, and numbers 1–10 into one topic. This can work as a first orientation, but needs an explicit learning goal and separate short practice/feedback for each mini-skill.
- Pronunciation examples should include a consistent IPA convention and an audio/listening model where possible; visual mouth-shape cues alone are not enough for phonological contrasts.

### Recommended correction sequence

1. Fix the two misleading alphabet examples and the capital-accent guidance first.
2. Rework the “14 fields” into learner-facing core + expandable teacher notes.
3. Reconcile timing, objective alignment, and exercise feedback.
4. Have a French phonetics/teaching reviewer validate all IPA examples and regional notes.
5. Validate the revised lesson in staging before any publisher action. Keep database content unchanged until a reviewed change set and staging target are confirmed.
