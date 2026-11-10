# Manuals Studio

`shared/studio/studio.html` authors one manual topic, checks it against the
topic standard, previews it and exports files. It runs entirely in the browser
and **publishes nothing**.

## Exports
| Button | File | Use |
|---|---|---|
| Full page | `<slug>.html` | Same components as existing topic pages. Public if committed. |
| Protected record | `<lang>_<cefr>_manual_<slug>.json` | Same fields `scripts/manual_to_record.py` writes (`body` = `<main>` content). |
| Public stub | `<slug>.html` | Same "Protected Manual Shell" as `manual_to_record.py` (title is HTML-escaped). |

`tests/test_manual_studio.js` renders a topic, runs `manual_to_record.py` on it
and requires the record and stub to match.

## Not wired yet
Where the protected body is stored is undecided: the repo has three mechanisms
(record loader, Storage migration, direct pages) and they disagree. See the PR
description. Until that is settled the studio only produces files.

`shared/studio/studio-core.js` is a vendored copy shared with the other studios.
