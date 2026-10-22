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
