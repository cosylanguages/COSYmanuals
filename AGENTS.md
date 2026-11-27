# COSYmanuals — repository notes

## Layout
- `manuals/<lang>/grammar/<level>/topics/*.html` — one grammar topic per file, 202 topics per level.
- `scripts/build_catalog.py` — regenerates `catalog/pages.json` (columns + rows). Run after any file change.
- `catalog/pages.json` — `{"columns": [...], "rows": [[...]]}`; `lang`, `kind`, `path` are the useful columns.

## Conventions
- Every topic page follows one shape: examples, rule, two comprehension checks (CCQ), formation table,
  register note, "why it matters", native-usage note, pronunciation, three inflected forms, two frequent
  mistakes, two internal links, three objectives, one final question.
- Boilerplate pages contain the literal string `Voici un exemple clair`. It is the reliable detector for
  unwritten topics.

## Checks worth running after a batch
```bash
python3 scripts/build_catalog.py
python3 - <<'EOF'
import glob, os, re
bad = [(f, h) for f in glob.glob('manuals/**/*.html', recursive=True)
       for h in re.findall(r'href="([^"#:]+\.html)"', open(f, encoding='utf-8', errors='replace').read())
       if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f), h)))]
print('broken links:', len(bad), bad[:5])
EOF
```

## Cross-level links
A link from an A1 page to an A2 page must be written `../../a2/topics/<slug>.html`, not bare `<slug>.html`.
Seven such links were repaired during the A1 completion; check new pages for the same mistake.

## Status (last update)
- French A1: 202/202 written. French A2: 202/202 written.
- French B1: 82 of 246 written; every grammar page linked from units 1 to 8 of the B1 course is now real content.
- French B2 200, C1 129, C2 121 still boilerplate.
- German, Spanish, Italian, Portuguese, Russian, Greek A1 and A2: all written.
- English A1 to C2: all written; it is the reference for tone and page shape.
