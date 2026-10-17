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
- Strings with variable parts ("{LANG} Grammar Manual — Spoken (B1)", "Lesson 1:", "Unit 1:") are not covered yet.
- The locked-stub text ("Log In to Access Content", ...) is English in non-English folders (1,106 pages) and mentions the storage back end; wait for the decision on where gated lessons live before localizing it.
- Raw data dumps ("task: ... speaking_focus: ...") appear on some pages; see `scripts/check_raw_dumps.py`.
