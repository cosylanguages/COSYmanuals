#!/usr/bin/env python3
"""Check that each English opening with a `lesson` really comes from a COSYplatform lesson that teaches its grammar id.
Needs the cosyplatform repo next to this one (../cosyplatform); skips with exit 0 if it is missing.
Also reports, for information, openings whose grammar id no lesson teaches yet.
   python3 scripts/check_open_vocab.py [--platform ../cosyplatform]"""
import glob, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import add_gv_open as G

plat = Path(sys.argv[sys.argv.index("--platform") + 1]) if "--platform" in sys.argv else Path(__file__).resolve().parents[2] / "cosyplatform"
files = sorted(glob.glob(str(plat / "curriculums/en/*/*.json")))
if not files:
    print("cosyplatform curricula not found; skipped"); sys.exit(0)

lessons = {}   # grammar id -> [(title, vocabulary)]
def walk(o):
    if isinstance(o, dict):
        if "grammarIds" in o:
            for g in o["grammarIds"]:
                lessons.setdefault(g, []).append((o.get("title", ""), [w.lower() for w in o.get("vocabulary", [])]))
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
for f in files: walk(json.load(open(f, encoding="utf8")))

bad, nolesson, checked = [], [], 0
for lvl, pages in G.LEVELS:
    for slug, d in pages.items():
        gid = "en-%s-%s" % (lvl, slug)
        if gid not in lessons:
            nolesson.append(gid); continue
        want = d.get("lesson")
        if not want:
            bad.append("%s: no lesson recorded, but lessons teach it: %s" % (gid, "; ".join(t for t, _ in lessons[gid][:3]))); continue
        if not any(want.lower() in t.lower() for t, _ in lessons[gid]):
            bad.append("%s: lesson %r does not teach this grammar id" % (gid, want))
        checked += 1
print("checked %d openings against lessons; %d problem(s); %d openings have no lesson yet (info)" % (checked, len(bad), len(nolesson)))
for b in bad: print("  ERROR", b)
if "--list" in sys.argv:
    for g in nolesson: print("  no lesson:", g)
sys.exit(1 if bad else 0)
