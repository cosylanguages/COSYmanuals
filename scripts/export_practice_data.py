#!/usr/bin/env python3
"""Export the grammar-reference files that the PUBLIC practice site needs (phonology + CCQ) from this private repo.
The source of truth stays here; COSYpractice keeps a copy in its own deploy (data/grammar-reference/) and loads it from there,
because a private repo cannot serve raw files.
  python3 scripts/export_practice_data.py --out ../COSYpractice/data/grammar-reference
Copies data/grammar/reference/<lang>/{phonology,ccq}/*.json (valid JSON only) to <out>/<lang>/<type>/<file>.json and writes
<out>/manifest.json (file list + sha256). Idempotent: files no longer in the source are removed from <out>.
  --check   exit 1 if <out> differs from the source (use in CI of the consuming repo)"""
import argparse, hashlib, json, os, shutil, sys

TYPES = ("phonology", "ccq")
ap = argparse.ArgumentParser(); ap.add_argument("--src", default="."); ap.add_argument("--out", required=True); ap.add_argument("--check", action="store_true")
a = ap.parse_args()
ref = os.path.join(a.src, "data", "grammar", "reference")
files = {}
for lang in sorted(os.listdir(ref)):
    for t in TYPES:
        d = os.path.join(ref, lang, t)
        if not os.path.isdir(d): continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"): continue
            p = os.path.join(d, f); raw = open(p, "rb").read()
            try: json.loads(raw)
            except ValueError as e: sys.exit(f"invalid JSON: {p}: {e}")
            files[f"{lang}/{t}/{f}"] = raw
manifest = json.dumps({"source": "COSYmanuals data/grammar/reference", "count": len(files),
                       "files": {k: hashlib.sha256(v).hexdigest() for k, v in files.items()}}, indent=1, sort_keys=True) + "\n"
want = {**files, "manifest.json": manifest.encode()}
have = {}
if os.path.isdir(a.out):
    for d, _, fs in os.walk(a.out):
        for f in fs: have[os.path.relpath(os.path.join(d, f), a.out).replace(os.sep, "/")] = open(os.path.join(d, f), "rb").read()
if a.check:
    diff = sorted(k for k in set(want) | set(have) if want.get(k) != have.get(k))
    print("practice data up to date" if not diff else f"practice data differs ({len(diff)}): {diff[:5]}"); sys.exit(1 if diff else 0)
for k in set(have) - set(want): os.remove(os.path.join(a.out, k))
for k, v in want.items():
    p = os.path.join(a.out, k); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(v)
print(f"exported {len(files)} files to {a.out}")
