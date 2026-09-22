# COSYmanuals Migration Status & Stage 3 Completion Report

> **Document Purpose**: Technical status report documenting the complete migration of manual booklets into the standardized ISO taxonomy under `manuals/` in COSYmanuals (Updated September 2026).

---

## Executive Summary

**COSYmanuals** is dedicated exclusively to **MANUAL BOOKLETS** (grammar, vocabulary, and communication reference booklets for contracted students and teachers) in two primary formats:
1. **Digital Manuals**: Explanatory reference hubs linking out to COSYplatform lessons rather than duplicating interactive platform exercises.
2. **Print / Offline Manuals**: Formatted for print or offline reference (no interactive JS widgets, print-optimized CSS, page-break management).

Access to COSYmanuals is strictly link-only and never exposed via public website navigation.

---

## Stage 3 Final Audit Report (September 2026)

The following audit table reflects the updated audit state against the source `COSYlanguages` repository:

```text
iso  type          lvl source real pages  missing in COSYmanuals
ba   grammar       a1                 29                       0
ba   grammar       a2                  4                       0
ba   vocabulary    a1                 15                       0
ba   vocabulary    a2                  4                       0
br   grammar       a1                 20                       0
br   grammar       a2                  4                       0
br   vocabulary    a1                 26                       0
br   vocabulary    a2                  4                       0
cv   grammar       a1                 31                       0
cv   grammar       a2                  4                       0
cv   vocabulary    a1                 15                       0
cv   vocabulary    a2                  4                       0
de   grammar       a1                 27                       0
de   vocabulary    a1                 32                       0
el   grammar       a1                 62                       0
el   vocabulary    a1                 30                       0
en   communication a1                 22                       0
en   communication a2                 21                       0
en   communication b1                 60                       0
en   communication b2                 21                       0
en   communication c1                 21                       0
en   communication c2                 16                       0
en   grammar       a1                 66                       0
en   grammar       a2                 56                       0
en   grammar       b1                 60                       0
en   grammar       b2                 50                       0
en   grammar       c1                 28                       0
en   grammar       c2                 22                       0
en   vocabulary    a1                 96                       0
en   vocabulary    a2                 35                       0
en   vocabulary    b1                 43                       0
en   vocabulary    b2                 33                       0
en   vocabulary    c1                 36                       0
en   vocabulary    c2                 19                       0
es   grammar       a1                 27                       0
es   grammar       a2                 14                       0
es   vocabulary    a1                 32                       0
es   vocabulary    a2                  7                       0
fr   communication a1                 22                       0
fr   communication a2                 21                       0
fr   communication b1                 21                       0
fr   communication b2                 21                       0
fr   communication c1                 21                       0
fr   communication c2                 21                       0
fr   grammar       a1                210                       0
fr   grammar       a2                206                       0
fr   grammar       b1                247                       0
fr   grammar       b2                203                       0
fr   grammar       c1                130                       0
fr   grammar       c2                122                       0
fr   vocabulary    a1                 78                       0
fr   vocabulary    a2                  8                       0
fr   vocabulary    b1                  7                       0
fr   vocabulary    b2                  6                       0
fr   vocabulary    c1                  5                       0
fr   vocabulary    c2                  6                       0
hy   grammar       a1                 30                       0
hy   grammar       a2                  4                       0
hy   vocabulary    a1                 15                       0
hy   vocabulary    a2                  4                       0
it   grammar       a1                 34                       0
it   grammar       a2                 14                       0
it   vocabulary    a1                 32                       0
it   vocabulary    a2                  7                       0
ka   grammar       a1                 29                       0
ka   grammar       a2                  4                       0
ka   vocabulary    a1                 15                       0
ka   vocabulary    a2                  4                       0
pt   grammar       a1                 27                       0
pt   grammar       a2                 14                       0
pt   vocabulary    a1                 32                       0
pt   vocabulary    a2                  7                       0
ru   communication a1                 22                       0
ru   communication a2                 21                       0
ru   communication b1                 21                       0
ru   communication b2                 21                       0
ru   communication c1                 22                       0
ru   communication c2                 22                       0
ru   grammar       a1                127                       0
ru   grammar       a2                 46                       0
ru   grammar       b1                 46                       0
ru   grammar       b2                 35                       0
ru   grammar       c1                 29                       0
ru   grammar       c2                 21                       0
ru   vocabulary    a1                 46                       0
ru   vocabulary    a2                  8                       0
ru   vocabulary    b1                  7                       0
ru   vocabulary    b2                  6                       0
ru   vocabulary    c1                  5                       0
ru   vocabulary    c2                  5                       0
tt   grammar       a1                 29                       0
tt   grammar       a2                  4                       0
tt   vocabulary    a1                 32                       0
tt   vocabulary    a2                  4                       0
ALL                                 3302                       0
```

---

## Second Audit Gaps & Remediation (September 2026)

A second audit conducted in September 2026 identified remaining gaps that were missed during the initial March 2025 pass:
1. **Tatar Non-Standard Directory Layout**: The entire Tatar A1 manual was stored in `COSYlanguages` under `manuals/tt/{grammar,vocabulary}/topics/*.html` and `bulek-N.html` rather than inside an explicit `a1/` subfolder. COSYmanuals previously contained redirect stubs under `manuals/tt/{grammar,vocabulary}/a1/` pointing to non-existent relative targets. The migration script was updated to classify these non-standard layout files as A1 topics and migrate all 59 real Tatar A1 pages and replacing the stubs.
2. **Git Quoted Non-ASCII File Names**: 3 topic pages with non-ASCII characters (`pretérito-perfecto.html`, `micherioù-ha-labour.html`, `beajoù-ha-treuzdougen.html`) were omitted in the initial audit because Git quoted octal-escaped paths by default (`core.quotePath=true`). Updating the migration script invocation with `-c core.quotePath=false` exposed these pages, which were then fully migrated.
3. **Redirect Stubs & Relinking**: 60 redirect stubs pointing to invalid targets and relative links pointing out to legacy COSYlanguages root paths were repaired using `cosy_manuals_migrate.py verify --fix-stubs` and `--relink`.

---

## Migration Steps & Pull Requests Overview

1. **Content Migration PRs**:
   - Ingested all 3,302 real manual topic pages across 14 ISO languages into standard directory structures (`manuals/<iso>/{grammar,vocabulary,communication}/<level>/`).
   - Rewrote relative resource and style links to point to `shared/styles/`.
2. **Index Pages, Residual Link Repairs & PDFs PR (`migrate/indexes-and-residuals`)**:
   - Ingested source landing/index pages via `migrate --indexes`.
   - Generated missing language/type index pages via `make-indexes`.
   - Repaired relative links automatically (`verify --fix`, `--fix-stubs`, `--relink`) and hand-repaired residual links.
   - Copied legacy grammar manual PDFs (`el`, `en`, `it`, `ru`) into `manuals/<iso>/print/`.
   - Logged unresolvable links requiring content decision in `docs/migration/LINKS_NEEDING_EDITOR.md`.

---

## ℹ️ Scope Clarification: Reference Grammar & Curriculum Files

> **Important Ecosystem Note**:
> The `reference-grammar/` and `curriculum/` directories in `COSYlanguages` were **NOT** part of the manual booklet migration. They contain dynamic JSON schemas and reference data actively consumed at runtime by application engines in `COSYlanguages`. They remain live in `COSYlanguages` and should **NOT** be deleted during manual cleanup tasks.
