#!/usr/bin/env python3
"""Insert the gv-open opening (a theme chip, a few gap lines, the formula) before the outcome banner of
English A1 grammar pages. Content lives in PAGES below, written for A1: short lines, one vocabulary theme per page.
Idempotent. `--check` lists pages in PAGES that lack the opening.
  python3 scripts/add_gv_open.py [--check]"""
import html, re, sys
from pathlib import Path

E = html.escape
# line = (subject, answer, tail, hint)  ->  <subject> [gap=answer] <tail> <hint>
# subject may be "" (then the line starts with the gap). role: class of the answer (r2 verb, r3 noun/other)
PAGES = {
 "present-simple": dict(theme="Daily routine", title="What do they do every day? Think of the verb, then ",
   people=[("A", "Anna · nurse"), ("T", "Tom · driver")],
   lines=[("I", "wake", "up at seven.", "(wake)"), ("You", "eat", "breakfast.", "(eat)"),
          ("Anna", "takes", "the bus.", "(take)"), ("Tom", "works", "in a shop.", "(work)")],
   formula=("present simple: verb for I you we they, verb plus s for he she it",
     [("I &middot; you &middot; we &middot; they", "VERB"), ("he &middot; she &middot; it", "VERB + S")])),
 "adverbs-frequency": dict(theme="Daily actions", title="How often? Think of the word, then ",
   people=[], lines=[("I", "always", "drink coffee in the morning.", "(100%)"), ("I", "usually", "walk to work.", "(80%)"),
          ("I", "sometimes", "watch TV.", "(50%)"), ("I", "never", "eat breakfast late.", "(0%)")],
   formula=("frequency scale: always 100 percent, usually, sometimes, never 0 percent",
     [("100%", "ALWAYS"), ("80%", "USUALLY"), ("50%", "SOMETIMES"), ("0%", "NEVER")])),
 "have-got": dict(theme="My family", title="Who has got what? Think of the verb, then ",
   people=[("M", "Mia · 12"), ("J", "James · dad")],
   lines=[("I", "have", "got a sister.", ""), ("You", "have", "got a brother.", ""),
          ("Mia", "has", "got two dogs.", ""), ("We", "have", "got a big house.", "")],
   formula=("have got: have for I you we they, has for he she it",
     [("I &middot; you &middot; we &middot; they", "HAVE got"), ("he &middot; she &middot; it", "HAS got")])),
 "can-cant": dict(theme="Things I can do", title="Can or can't? Think of the word, then ",
   people=[("T", "Tanya"), ("J", "James")],
   lines=[("Tanya", "can", "swim. &#10003;", ""), ("James", "can't", "dance. &#10007;", ""),
          ("I", "can", "cook pasta. &#10003;", ""), ("We", "can't", "fly. &#10007;", "")],
   formula=("can and can't plus the base verb, the same for every person",
     [("I &middot; you &middot; he &middot; she &middot; we &middot; they", "CAN + verb"), ("&#10007;", "CAN'T + verb")])),
 "there-is-are": dict(theme="My room", title="What is in the room? Think of the word, then ",
   people=[], lines=[("There", "is", "a bed.", ""), ("There", "are", "two chairs.", ""),
          ("There", "is", "a lamp.", ""), ("There", "are", "three books.", "")],
   formula=("there is for one thing, there are for two or more",
     [("1 thing", "THERE IS"), ("2 or more", "THERE ARE")])),
 "possessive-adjectives": dict(theme="My things, your things", title="Whose is it? Think of the word, then ",
   people=[], lines=[("I &rarr;", "my", "bag", ""), ("you &rarr;", "your", "book", ""),
          ("she &rarr;", "her", "pen", ""), ("we &rarr;", "our", "teacher", "")],
   formula=("possessive adjectives: I my, you your, he his, she her, we our, they their",
     [("I", "MY"), ("you", "YOUR"), ("he", "HIS"), ("she", "HER"), ("we", "OUR"), ("they", "THEIR")])),
 "imperatives": dict(theme="In the classroom", title="What does the teacher say? Think of the word, then ",
   people=[], lines=[("", "Open", "your book.", ""), ("", "Sit", "down, please.", ""),
          ("", "Don't", "talk, please.", ""), ("", "Listen", "to me.", "")],
   formula=("imperative: the base verb; add do not for a negative",
     [("&#10003;", "VERB!"), ("&#10007;", "DON'T + verb!")])),
}

def build(slug, d):
    gid = "open-" + slug
    out = ['<section class="gv gv-open" aria-labelledby="%s">' % gid,
           '  <span class="gv-theme">%s</span>' % E(d["theme"]),
           '  <h2 class="gv-title" id="%s">%s<span class="gv-screen">tap the line.</span><span class="gv-print">write it on the line.</span></h2>' % (gid, E(d["title"], quote=False))]
    if d["people"]:
        out.append('  <ul class="gv-people" aria-label="People">')
        for a, t in d["people"]:
            out.append('    <li><span class="gv-av" aria-hidden="true">%s</span><span>%s</span></li>' % (a, E(t)))
        out.append("  </ul>")
    out.append('  <ol class="gv-lines">')
    for subj, ans, tail, hint in d["lines"]:
        s = ('<span class="gv-r1">%s</span> ' % subj) if subj else ""
        out.append('    <li>%s<details class="gv-gap"><summary><span class="gv-sr">gap</span></summary><span class="gv-r2">%s</span></details> %s%s</li>'
                   % (s, E(ans, quote=False), tail, (" " + E(hint)) if hint else ""))
    out.append("  </ol>")
    label, pairs = d["formula"]
    out.append('  <div class="gv gv-formula" role="group" aria-label="%s">' % E(label))
    for l, r in pairs:
        out.append('    <span class="gv-pair"><span class="gv-slot gv-r1">%s</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">%s</span></span>' % (l, E(r, quote=False)))
    out.append("  </div>\n</section>\n")
    return "\n".join(out)

def main():
    check = "--check" in sys.argv; lacking = 0
    for slug, d in PAGES.items():
        p = Path("manuals/en/grammar/a1/topics/%s.html" % slug); t = p.read_text(encoding="utf8")
        if "gv-open" in t: continue
        lacking += 1
        if check: print("lacks opening:", slug); continue
        i = t.index('<div class="box outcome-banner"')
        p.write_text(t[:i] + build(slug, d) + "\n" + t[i:], encoding="utf8")
    print(("check: %d pages lack the opening" if check else "added %d openings") % lacking)
    return 1 if check and lacking else 0

if __name__ == "__main__":
    sys.exit(main())
