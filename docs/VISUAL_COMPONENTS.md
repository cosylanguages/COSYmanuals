# Grammar visual components (`gv-*`)

Source: `shared/styles/visuals.css` · Gallery/test fixture: `shared/visuals/gallery.html` · Lint: `python3 scripts/check_visuals.py`

## Rules (non-negotiable)
1. **Monolingual.** The CSS contains no words. Every label, edge, caption and cap is written in the page's own language. Never add `content:"..."` text (the linter fails on it).
2. **Colour is never the only cue.** Roles differ by underline style (solid, dashed, dotted, double, wavy), so grayscale print still works.
3. **Same role = same colour everywhere.** `gv-r1` is always the subject in the formula *and* in the examples; do not re-assign roles page by page.
4. **No JS.** Works offline, in print and behind any gate.
5. Scrollable parts (timeline, paradigm) carry `tabindex="0"` + a name. Decorative parts carry `aria-hidden`.

## Which component for which grammar point
| Need | Use |
|---|---|
| Tenses, aspect, "since/for", sequence of events | **Timeline** |
| Sentence pattern, word order, auxiliary + participle | **Formula** + colour-coded examples |
| "Which form do I choose?" (auxiliary, article, case, aspect) | **Tree** |
| Two forms often confused (être/avoir, a/an, perfective/imperfective) | **Contrast** |
| Case roles: who does what to whom | **Case map** (`gv-case-map`); the full case table is embedded by ID or looked up in COSYtools |
| Conjugation / declension tables | **Embedded paradigm** by COSYtools table ID (`gv-paradigm` + `data-table-id`); hand-author only small teaching patterns |
| Any other word's forms | **Lookup card** (`gv-lookup`): link to the language's COSYtools tool |
| First thing on every page: guess, then see the pattern | **Opening** (`gv-open`) |
| A practice exercise that exists in COSYpractice | **QR block** (`gv-qr`), print only |

## Snippets
**Formula + examples** (roles `gv-r1` to `gv-r5`)
```html
<div class="gv gv-formula" role="group" aria-label="...">
  <span class="gv-slot gv-r1">...</span><span class="gv-op">+</span><span class="gv-slot gv-r2">...</span>
</div>
<ul class="gv-examples"><li><span class="gv-r1">...</span> <span class="gv-r2">...</span></li></ul>
```
**Timeline**: positions are percentages of the axis. `gv-below` puts a label under the line. Tones: `gv-tone-past|present|future|a..e`. `gv-open-start|end` for "continues".
```html
<figure class="gv gv-timeline" tabindex="0" role="region" aria-labelledby="id">
  <ol class="gv-axis">
    <li class="gv-span gv-tone-past gv-open-start" style="--from:8%;--to:60%"><span class="gv-label">...</span></li>
    <li class="gv-point gv-tone-past gv-below" style="--at:20%"><span class="gv-label">...</span></li>
    <li class="gv-now" style="--at:60%"><span class="gv-label">...</span></li>
  </ol>
  <div class="gv-caps"><span>...</span><span>...</span></div>
  <figcaption id="id">...</figcaption>
</figure>
```
**Tree**: nested `ul`; `gv-q` = question, `gv-leaf` = answer, `gv-edge` = branch label.
```html
<figure class="gv gv-tree" aria-labelledby="id"><ul><li><span class="gv-node gv-q">?</span>
  <ul><li><span class="gv-edge">..</span><span class="gv-node gv-leaf gv-tone-a">..</span></li></ul></li></ul>
  <figcaption id="id">...</figcaption></figure>
```
**Contrast**: exactly two `gv-side`, one `gv-vs aria-hidden="true"` (the "≠" is drawn by CSS).
**Case map**: one row of role chips; the case label sits under the word. Use `gv-tone-a..d` for the tint (not `gv-r1..r4`, which adds an underline to the whole card). Arrows are decorative.
```html
<figure class="gv gv-case-map" lang="ru" aria-labelledby="id">
  <div class="gv-case-row">
    <span class="gv-case-role gv-tone-a"><b>брат</b><small>именительный · кто?</small></span>
    <span class="gv-case-arrow" aria-hidden="true">→</span>
    <span class="gv-case-role gv-tone-b"><b>даёт</b><small>глагол</small></span>
    <span class="gv-case-arrow" aria-hidden="true">→</span>
    <span class="gv-case-role gv-tone-c"><b>книгу</b><small>винительный · что?</small></span>
  </div>
  <figcaption id="id">Кто? → что делает? → что?</figcaption>
</figure>
```
**Paradigm** (inside manuals the page keeps its own table look: `class="table-wrap gv gv-paradigm"`; standalone `gv-paradigm` brings its own): wrap the table in `.gv-paradigm` (`tabindex="0" role="region" aria-label`), `<caption>`, `<th scope>`; `<span class="gv-stem">` + `<span class="gv-end">` (empty `gv-end` shows ∅); `gv-irr` marks irregular forms.

## Opening (`gv-open`): the first thing on every grammar page
Three beats, all in the page's own language, using only words the learner has met: **look** (people or objects, a vocabulary-theme chip), **fill** (gap lines, each revealed with a native `<details>`; no JavaScript), **see it** (a `gv-formula` that shows the pattern in the same role colours). See `shared/visuals/gallery.html` and `manuals/en/grammar/a1/topics/to-be.html`.
```html
<section class="gv gv-open" aria-labelledby="id">
  <span class="gv-theme">Meeting people</span>
  <h2 class="gv-title" id="id">... <span class="gv-screen">tap the line.</span><span class="gv-print">write it on the line.</span></h2>
  <ul class="gv-people"><li><span class="gv-av" aria-hidden="true">T</span><span>Tanya · student</span></li></ul>
  <ol class="gv-lines"><li><span class="gv-r1">I</span> <details class="gv-gap"><summary><span class="gv-sr">gap</span></summary><span class="gv-r2">am</span></details> Tanya.</li></ol>
  <div class="gv gv-formula" role="group" aria-label="..."><span class="gv-pair"><span class="gv-slot gv-r1">I</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">AM</span></span></div>
</section>
```
- **Vocabulary theme.** Every grammar point gets the theme its use naturally lives in, and every example comes from it. Frequency adverbs: daily routine. To be: meeting people. Prepositions of place: home and rooms. Past simple: yesterday and weekends. Name it in the `gv-theme` chip so teachers and learners see it.
- **People are neutral.** `gv-av` avatars use a neutral colour, because role colours mean subject / verb / object everywhere.
- **Level shape.** A0-A1: named people, 3-4 gap lines. A2: two small sets side by side. B1: sentence pairs with different meaning. B2+: a short text, find the pattern. The component is the same; only the content changes.
- **Print.** `<details>` prints closed: each gap becomes a blank line to write on, and the answers are in the formula that follows. Use `gv-screen` / `gv-print` for wording that only fits one medium ("tap" / "write").
- Lint (`check_visuals.py`): needs a labelled section, a non-empty `gv-theme`, at least two gap lines, a `gv-sr` label on every gap, one answer element per gap, and a formula.

## Canonical tables by COSYtools ID
COSYdata owns the data. COSYtools is the lookup engine. The manual is the explanation layer. If a page needs a specific conjugation, declension or case table, do not type it by hand: add a placeholder and let the build script fill it from the canonical source.

```html
<div class="gv gv-paradigm" data-table-id="fr:verb:parler:indicatif_present" data-source="cosytools"></div>
```

Use any stable key as the table ID. The examples use `<lang>:<pos>:<lemma>:<feature>` because the COSYtools JSON is keyed by lemma; a COSYdata object ID works the same way.

Register the table in `data/grammar/table_index.json`:

```json
{
  "source_url": "https://cosylanguages.github.io/COSYtools/tools/fr/conjugeur/",
  "data_url": "https://cosylanguages.github.io/COSYtools/tools/fr/conjugeur/data/verbs.json",
  "path": ["parler", "tenses", "indicatif_present"],
  "caption": "parler · présent de l'indicatif",
  "render": {
    "kind": "list",
    "split_pronoun": true,
    "columns": [
      {"key": "person", "header": "personne"},
      {"key": "form", "header": "forme"}
    ]
  }
}
```

Run:

```bash
python3 scripts/embed_grammar_tables.py            # dry run
python3 scripts/embed_grammar_tables.py --apply    # write
python3 scripts/embed_grammar_tables.py --id fr:verb:parler:indicatif_present --apply
```

The script fetches the canonical JSON, renders a static `gv-paradigm` table with `<caption>`, `scope`, and a visible `Source: COSYtools` link, and records `data-source-url` + `data-source-hash`. Re-running is idempotent; when the source data changes, the hash changes and the block is regenerated. The build needs network access to COSYtools; the generated HTML is static, so the manual itself works offline.

- Do not edit inside `<!-- gv-table:start ... -->` / `<!-- gv-table:end -->`. Edit the index entry or the page framing instead.
- The visible link goes to the COSYtools tool page, not the raw JSON.
- The table is static, so it prints; the source link stays visible.
- If the table ID cannot be resolved, the script leaves the placeholder unchanged and the linter reports it. Keep the surrounding explanation useful.
- Lint (`check_visuals.py`): `gv-paradigm[data-table-id]` needs a known ID, `data-source="cosytools"`, a COSYtools `data-source-url`, a 16-character `data-source-hash`, a rendered `<table>`, and a `.gv-source` link.
- Lint: a `gv-case-map` needs an accessible name, at least two `.gv-case-role` items, a `<b>` word and `<small>` case label in each role, and `aria-hidden="true"` on arrows.

## Lookup card (`gv-lookup`)
Use this when the page explains a pattern but does not embed a specific table: the learner can look up any word in COSYtools. The card is static, prints, and shows the URL so a paper reader can type it.
```html
<aside class="gv gv-lookup" data-lookup="conjugation" data-lang="fr" aria-label="...">
  <span class="gv-lookup-kicker">COSYtools</span>
  <p class="gv-lookup-text">...</p>
  <span class="gv-lookup-action"><a class="gv-lookup-link" href="...">...</a><span class="gv-lookup-url">...</span></span>
</aside>
```
Types: `cases`, `conjugation`, `principal-parts`, `government`, `gender`. The text and link label are in the page language; the URL is the only non-localized string.

Add pages to `data/grammar/lookup_pages.json` and run:
```bash
python3 scripts/add_lookup_cards.py            # dry run
python3 scripts/add_lookup_cards.py --apply    # write
python3 scripts/add_lookup_cards.py --lang fr  # one language
```
The script inserts before the first `.mistakes`, `.checklist`, `.pager`, or `</main>` and is idempotent. It refuses a language/type pair with no COSYtools target or no localized labels. Adding a new language means adding its labels and tool paths to `scripts/add_lookup_cards.py`.

- Lint (`check_visuals.py`): needs `data-lookup` from the known set, `data-lang`, `aria-label`, a non-empty `.gv-lookup-text`, a COSYtools `a.gv-lookup-link` with text, and a visible `.gv-lookup-url`.

## QR block (`gv-qr`): practice from the printed manual
Hidden on screen. In print the page's "Practice this" button is hidden and the QR block (code + visible short address) appears in its place. Generate it with `python3 scripts/make_qr_block.py --url <https URL> --text "<page language>" --alt "<page language>"` (needs `pip install segno`); it is inline SVG, so it needs no network. Link to the live practice site (`https://cosylanguages.github.io/COSYpractice/index.html?lang=..&cat=..&level=..&theme=..`), never to a relative path, so the code works on paper. Check that the `theme` value exists in COSYpractice before printing it on a page.

## Tense timelines (automated authoring)
Tense/aspect pages get a `gv-timeline` plus a CCQ panel directly below it. Do not hand-edit the timeline pages; run the driver:
```bash
python3 scripts/add_tense_timelines.py --lang en           # dry run
python3 scripts/add_tense_timelines.py --lang en --apply   # write
```
Profiles live in `scripts/tense_timelines_en.py`, `tense_timelines_fr_ru.py`, `tense_timelines_other.py` and `tense_timelines_minor.py`. A profile declares the axis items, optional authored `ccq` questions, and a slug map. The driver:
- removes an earlier generated timeline/CCQ, so reruns are idempotent;
- inserts the timeline before the first in-content CCQ, `.table-wrap`, `<table>` or rule box, preferring anchors inside `<main>`;
- keeps an existing hand-authored CCQ and moves it directly below the timeline; otherwise it copies the page's practice-quiz questions or renders the profile's authored CCQ;
- escapes `data-quiz` as an HTML attribute, so apostrophes in questions are safe.

Every inserted CCQ is a `.ccq-panel`/`.quiz-panel` with `data-quiz` and `data-tense-ccq`; the page's existing `app.js` makes it interactive. Pages on the legacy template must also load `tokens.css`, `base.css`, `components.css` and `layout.css`; the driver does not add them automatically.

After a run:
```bash
python3 scripts/check_visuals.py manuals/*/grammar
```

## Limits to know
- Timeline labels are placed by hand. The linter warns when two labels on the same side are too close; fix with `gv-below` or by moving them.
- On phones the timeline scrolls sideways inside its own box (the page never overflows).
- Positions use inline `style="--at:..."`. If you later add a strict CSP without `unsafe-inline`, switch to generated classes.
- Languages are all left-to-right today. The timeline assumes LTR.

## Rollout order (suggested)
1. Wire in (below) and run the linter. 2. English A1 `to-be`, `have-got`, `simple-vs-continuous` (existing hand-made timelines become `gv-timeline`). 3. French passé composé (tree + contrast). 4. Embed canonical COSYtools tables by ID on conjugated verb pages; add case maps to case pages; add lookup cards where a specific table is not embedded. 5. Other languages by level.

## Wiring
Add as the **first line** of `shared/styles/components.css` (3,880 of 4,039 pages already load it, so no page edits are needed):
`@import url("visuals.css");`

## Tables (all pages)
`python3 scripts/upgrade_tables.py` (dry run; `--apply` to write) makes every table accessible (`<th scope>`, `.table-wrap` becomes a named, focusable region) and splits stem/ending ONLY for clearly regular verb paradigms (every ending must be in a per-language regular set). Irregular verbs are never marked automatically; see the review list. `check_visuals.py` fails on any table header without `scope`. For a canonical table, prefer `data-table-id` + `scripts/embed_grammar_tables.py`; `upgrade_tables.py` is for legacy hand-authored tables.
