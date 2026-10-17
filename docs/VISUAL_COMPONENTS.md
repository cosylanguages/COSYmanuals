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
| Conjugation / declension tables | **Paradigm** (stem vs ending, irregular forms) |

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
**Paradigm**: wrap the table in `.gv-paradigm` (`tabindex="0" role="region" aria-label`), `<caption>`, `<th scope>`; `<span class="gv-stem">` + `<span class="gv-end">` (empty `gv-end` shows ∅); `gv-irr` marks irregular forms.

## Limits to know
- Timeline labels are placed by hand. The linter warns when two labels on the same side are too close; fix with `gv-below` or by moving them.
- On phones the timeline scrolls sideways inside its own box (the page never overflows).
- Positions use inline `style="--at:..."`. If you later add a strict CSP without `unsafe-inline`, switch to generated classes.
- Languages are all left-to-right today. The timeline assumes LTR.

## Rollout order (suggested)
1. Wire in (below) and run the linter. 2. English A1 `to-be`, `have-got`, `simple-vs-continuous` (existing hand-made timelines become `gv-timeline`). 3. French passé composé (tree + contrast). 4. Paradigm tables for every conjugated verb page. 5. Other languages by level.

## Wiring
Add as the **first line** of `shared/styles/components.css` (3,880 of 4,039 pages already load it, so no page edits are needed):
`@import url("visuals.css");`
