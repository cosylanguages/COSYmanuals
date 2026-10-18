# Page catalog

`catalog/pages.json`, `catalog/summary.json` and `catalog/COVERAGE.md` are **generated**: do not edit them.

- `python3 scripts/build_catalog.py`: rebuild after adding, moving or editing pages
- `python3 scripts/build_catalog.py --check`: exits 1 if the committed catalog is stale (use it in CI)
- `catalog/index.html`: filterable browser (language, level, module, track, kind, status, search); filters are kept in the URL, so a filtered view can be shared. Open it through a web server (it loads `pages.json`).

Columns of `pages.json`: `path lang track module level kind status title bytes visuals tables quiz lang_ok leaks access`

| field | meaning |
|---|---|
| kind | `topic`, `unit`, `track-manual`, `hub`, `print`, `teacher-access` |
| status | `real` (text is in git), `locked-stub` (placeholder, text stored outside git), `redirect` |
| lang_ok | `<html lang>` equals the language folder |
| leaks | known English template strings still on the page |
| visuals | number of `gv-*` components on the page |
| access | classification from `MANUALS_ACCESS_MANIFEST.json` (null if the page is not listed there) |

The older sample files in `catalog/` (`manifest.json`, `*-grammar.json`, ...) are a 5-entry sketch and are not used by the generated catalog.
