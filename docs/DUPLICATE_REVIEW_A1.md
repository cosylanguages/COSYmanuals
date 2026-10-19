# Duplicate / overlap review: English A1 and Russian A1 grammar

Evidence from the catalog and the link graph. **Executed:** the 14 retirements (`scripts/retire_pages.py`) and the Russian tier links (`scripts/link_ru_tiers.py`).

## Headline

- **English: 11 orphaned older pages** (`en-*` generation: no headings, no hub link, 0-1 inbound) beside maintained twins. Retire 10 now, 1 after a teacher check, keep and link the `en` index.
- **Russian: not duplication, a broken two-tier structure.** 51 detail pages are never linked from their overview pages. Fix with cross-links, do not delete.
- **Russian true duplicates: 3** older English-titled pages (`ru-be`, `ru-nouns-gender`, `ru-pronouns`) + the orphan `ru` index; **1 real orphan lesson** (`narechiya-mesta-i-napravleniya`).

## Recommendation table

| lang | page | twin(s) | recommendation | evidence |
|---|---|---|---|---|
| en | `en-articles` | articles | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 12KB, 9 headings, 2 inbound, 1 visuals |
| en | `en-be` | to-be | **RETIRE (redirect to twin)** | 10KB, 0 headings, 1 inbound | twin: 11KB, 9 headings, 7 inbound, 0 visuals |
| en | `en-future-going-to` | going-to | **RETIRE (redirect to twin)** | 4KB, 0 headings, 0 inbound | twin: 9KB, 6 headings, 2 inbound, 1 visuals |
| en | `en-have` | have-got | **RETIRE (redirect to twin)** | 4KB, 0 headings, 0 inbound | twin: 9KB, 7 headings, 2 inbound, 1 visuals |
| en | `en-past-simple` | past-simple-be+past-simple-regular+past-simple-irregular | **RETIRE (redirect to twin)** | 4KB, 0 headings, 0 inbound | twin: 9KB, 7 headings, 3 inbound, 1 visuals + 9KB, 7 headings, 2 inbound, 1 visuals + 9KB, 8 headings, 3 inbound, 1 visuals |
| en | `en-plurals` | plurals-regular+plurals-irregular | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 10KB, 6 headings, 4 inbound, 0 visuals + 11KB, 8 headings, 2 inbound, 0 visuals |
| en | `en-present-simple` | present-simple | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 10KB, 9 headings, 8 inbound, 1 visuals |
| en | `en-pronouns` | pronouns | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 10KB, 8 headings, 4 inbound, 0 visuals |
| en | `en-there-is` | there-is-are+there-was-were | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 10KB, 8 headings, 3 inbound, 0 visuals + 10KB, 7 headings, 2 inbound, 1 visuals |
| en | `en-word-order` | word-order | **RETIRE (redirect to twin)** | 10KB, 0 headings, 0 inbound | twin: 10KB, 8 headings, 2 inbound, 0 visuals |
| en | `en-possessives` | pronouns+possessive-s | **RETIRE after a teacher confirms** | 5KB, 0 headings, 0 inbound | twin: 10KB, 8 headings, 4 inbound, 0 visuals + 9KB, 8 headings, 3 inbound, 0 visuals |
| en | `en` | · | **KEEP and link from the hub** | 7KB, 0 headings, 0 inbound |
| ru | `ru-be` | to-be | **RETIRE (redirect to twin)** | 14KB, 0 headings, 0 inbound | twin: 13KB, 7 headings, 2 inbound, 1 visuals |
| ru | `ru-nouns-gender` | noun-gender | **RETIRE (redirect to twin)** | 13KB, 0 headings, 0 inbound | twin: 10KB, 6 headings, 3 inbound, 0 visuals |
| ru | `ru-pronouns` | lichnye-mestoimeniya-padezhi+lichnye-mestoimeniya-i-nulevaya-svyazka | **RETIRE (redirect to twin)** | 11KB, 0 headings, 0 inbound | twin: 7KB, 4 headings, 3 inbound, 0 visuals + 13KB, 8 headings, 1 inbound, 0 visuals |
| ru | `ru` | · | **KEEP and link from the hub** | 5KB, 0 headings, 0 inbound |
| ru | `narechiya-mesta-i-napravleniya` | predlogi-mesta | **KEEP and LINK** | 13KB, 8 headings, 0 inbound | twin: 6KB, 4 headings, 3 inbound, 1 visuals |
| ru | `(51 long detail pages)` | (their 30 short overview pages) | **KEEP BOTH tiers, ADD cross-links** | tier structure |

## How to retire safely

Replace each retired page with a tiny redirect shell (the repo already uses one: meta refresh + canonical + script). External or bookmarked links keep working, the catalog marks them `redirect`, and nothing is lost. During the migration the redirect shells are the only thing that needs to move.

## What I did not check

- Other levels (A0, A2-C2) and other languages. The same patterns probably exist (older `*-*` generations; unlinked tiers).
- Whether a teacher considers any older page's *exercises* better than the twin's. All have a quiz either way; text overlap is low because the twins were written independently.

## Open items found while doing this
- **15 Russian detail pages have no confident overview** and were left unlinked: `dni-nedeli-i-mesyatsy`, `kolichestvennye-chislitelnye-1-100`, `konstruktsii-skuchno-veselo-interesno`, `konstruktsiya-menya-zovut`, `konstruktsiya-u-menya-est`, `osobye-glagoly-zhit-pisat-pit`, `otNegative-mestoimeniya-nikto-nishto`, `rod-imyen-sushchestvitelnykh`, `ukazatelnye-mestoimeniya-etot-eta-eto-eti`, `vezhlivye-prosby-i-poveleniya`, `vremya-i-chasy`, `vvodnye-slova-kazhetsya-po-moemu` (the rest of the 15 are standalone pages: `noun-gender`, `to-be`, `part-1-building-blocks`). A teacher can say which overview each belongs to; add the pair to `EXTRA` in `scripts/link_ru_tiers.py`.
- **Slug typo:** `otNegative-mestoimeniya-nikto-nishto` looks like a bad transliteration of "отрицательные". Renaming needs a redirect from the old name.
- The English and Russian reference indexes (`en.html`, `ru.html`, `data/grammar/reference/...`) still list the retired pages; the redirects keep those links working. Pointing them at the twins is a later tidy-up.
