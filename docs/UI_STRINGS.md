# UI strings (monolingual pages)

Every non-English page must contain only its own language. Repeated interface text (labels, buttons, hub descriptions) lives in **`shared/i18n/ui-strings.json`**.

- `python3 scripts/localize_ui.py --audit`: which English template strings remain, per language
- `python3 scripts/localize_ui.py`: dry run; `--apply` rewrites pages
- The script replaces only whole text nodes that exactly match a known English string, never lesson content, and never touches tags, attributes, scripts or styles. It also sets `<html lang>` on pages that have no known English left.

## Adding a language
Add its code to `"apply"` and a translation under each string (`"ba": "..."`). Languages without translations are left in English on purpose; they are listed by `--audit`. **Needs a native speaker:** ba, br, cv, hy, ka, tt.

## Register
Follows the existing pages: formal address in de (Sie), es (usted), pt (você), fr (vous), ru (Вы); informal in it (tu).

## Known gaps
- Variable-part strings (course titles, "Lesson N:", "Unit N:", hub headings) are handled by `patterns` in the JSON: a regex with named groups plus a per-language template (`{lg}`, `{lvl}`, `{n}`, `{rest}`) and optional word maps (`mod`, `track`).
- Headings that repeated their own prefix ("Unit 0: Unidad 0: …") are collapsed to one. The same duplicate exists in 30 English headings (not touched here).
- The locked-stub text ("Log In to Access Content", ...) is English in non-English folders (1,106 pages) and mentions the storage back end; wait for the decision on where gated lessons live before localizing it.

## Lesson notes (`lesson-notes-extra`)
Some pages printed serialized notes as visible text (`task: "..." speaking_focus: "..."`, `hw: "..."`, ...).
`python3 scripts/format_notes.py` (`--apply`) turns them into a labelled list (`<dl class="gv-notes">`); labels live in
`notes_labels` in `shared/i18n/ui-strings.json`. Values are copied verbatim. Blocks holding only `lessons_count` (internal
metadata) are removed. Languages without translated labels (ba br cv hy ka tt) get English labels marked `lang="en"`.
`scripts/check_raw_dumps.py` now fails if a raw dump comes back.
