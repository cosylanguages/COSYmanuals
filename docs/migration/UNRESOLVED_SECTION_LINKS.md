# Unresolved section links

The manuals link to four site sections that are built outside this repository. After the repair passes in
`scripts/repair_links.py`, `scripts/repair_links_gateways.py` and `scripts/repair_links_final.py`, these are the
only internal links left pointing at a page that does not exist.

| Section | Live at | Links |
|---|---|---|
| `comparative` | https://cosylanguages.github.io/COSYlanguages/comparative/index.html | resolved: rewritten to the absolute URL |
| `practice` | not published (404) | 26 |
| `hybrid` | not published (404) | 34 |
| `rosetta-wall` | not published (404) | 34 |

`practice`, `hybrid` and `rosetta-wall` cannot be resolved from this repository and are published nowhere, so the
links stay as they are until those sections exist. Every other internal link in `manuals/` resolves: verified by
scanning `manuals/**/*.html`, excluding the generated `print/` booklets.
