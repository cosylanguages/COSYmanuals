#!/usr/bin/env python3
"""Retire superseded pages by replacing them with a redirect shell (same template as the existing
'Page Moved' pages). External links and bookmarks keep working; the catalog marks them `redirect`.
The shell text is English; run scripts/localize_ui.py afterwards to translate it.
  python3 scripts/retire_pages.py            # dry run
  python3 scripts/retire_pages.py --apply
Idempotent. Mapping = reviewed list in docs/DUPLICATE_REVIEW_A1.md."""
import html, os, re, sys

BASE = "manuals/{l}/grammar/a1/topics/"
RETIRE = {  # (lang, old slug) -> twin slug
    ("en", "en-articles"): "articles", ("en", "en-be"): "to-be", ("en", "en-future-going-to"): "going-to", ("en", "en-have"): "have-got",
    ("en", "en-past-simple"): "past-simple-regular", ("en", "en-plurals"): "plurals-regular", ("en", "en-possessives"): "pronouns",
    ("en", "en-present-simple"): "present-simple", ("en", "en-pronouns"): "pronouns", ("en", "en-there-is"): "there-is-are",
    ("en", "en-word-order"): "word-order",
    ("ru", "ru-be"): "to-be", ("ru", "ru-nouns-gender"): "noun-gender", ("ru", "ru-pronouns"): "lichnye-mestoimeniya-padezhi",
}
SHELL = """<!doctype html>
<html lang="{lang}" data-lang-theme="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Redirecting &middot; COSYlanguages</title>
<link rel="canonical" href="{to}">
<meta http-equiv="refresh" content="0; url={to}">
<script>window.location.replace("{to}");</script>
<style>
  body {{ margin:0; padding:0; background-color:#fdfcf8; color:#2a2a2a; font-family:'Nunito','Segoe UI',system-ui,sans-serif; display:flex; align-items:center; justify-content:center; min-height:100vh; text-align:center; }}
  .card {{ background:#ffffff; border:1px solid rgba(74,107,80,0.15); border-radius:18px; padding:32px; max-width:480px; box-shadow:0 6px 28px rgba(46,74,51,0.08); }}
  h1 {{ font-size:20px; margin:0 0 12px; color:#375742; }}
  p {{ font-size:15px; margin:0 0 20px; color:#4a4a4a; }}
  a {{ color:#416b49; font-weight:700; text-decoration:underline; }}
</style>
<link rel="stylesheet" href="../../../../../shared/styles/lang-accents.css">
</head>
<body>
<main>
<div class="card">
  <h1>Page Moved</h1>
  <p>This page has moved to a new location. If you are not redirected automatically, please follow the link below.</p>
  <p><a href="{to}">{label}</a></p>
</div>
</main>
</body>
</html>
"""

def title_of(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    h = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    t = h.group(1) if h else (re.search(r"<title>(.*?)</title>", s, re.S).group(1).split("&middot;")[0])
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t)).strip()

def main():
    apply = "--apply" in sys.argv; n = 0
    for (lang, old), twin in RETIRE.items():
        po, pt = BASE.format(l=lang) + old + ".html", BASE.format(l=lang) + twin + ".html"
        if not os.path.exists(pt): print("MISSING TWIN", pt); sys.exit(1)
        if not os.path.exists(po): continue
        if "http-equiv=\"refresh\"" in open(po, encoding="utf-8", errors="replace").read(): continue     # already retired
        n += 1
        print(f"{'retire' if apply else 'would retire'}: {po} -> {twin}.html")
        if apply: open(po, "w", encoding="utf-8").write(SHELL.format(lang=lang, to=twin + ".html", label=html.escape(title_of(pt), quote=False)))
    print(f"{n} page(s) {'retired' if apply else 'to retire'}")

if __name__ == "__main__": main()
