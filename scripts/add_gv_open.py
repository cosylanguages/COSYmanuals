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

def _p(theme, q, lines, formula, label, people=()):
    return dict(theme=theme, title=q + " Think of the word, then ", people=list(people), lines=lines, formula=(label, formula))

PAGES.update({
 "adjectives": _p("Describing things", "What is it like?",
   [("The tea is hot. The ice is", "cold", ".", ""), ("Tom is big. The cat is", "small", ".", ""),
    ("My car is old. Your car is", "new", ".", ""), ("Anna is happy. Tom is", "sad", ".", "")],
   [("a &middot; the", "ADJECTIVE + noun"), ("is &middot; are", "ADJECTIVE")], "adjective before a noun or after is and are"),
 "adverbs-manner": _p("How we do things", "How do they do it?",
   [("Anna sings", "beautifully", ".", "(beautiful)"), ("Tom drives", "slowly", ".", "(slow)"),
    ("I speak", "quietly", ".", "(quiet)"), ("James plays", "well", ".", "(good)")],
   [("slow", "SLOWLY"), ("good", "WELL")], "adverbs of manner: adjective plus ly, good becomes well"),
 "all-both-none": _p("My class", "How many?",
   [("", "All", "the students are here. (10 of 10)", ""), ("", "Both", "teachers are kind. (2 of 2)", ""),
    ("", "None", "of us are late. (0 of 10)", ""), ("", "All", "my friends like music. (100%)", "")],
   [("100%", "ALL"), ("2 of 2", "BOTH"), ("0", "NONE")], "all for everyone, both for two, none for nobody"),
 "comparative-adjectives": _p("Animals", "Which one is more?",
   [("A mouse is", "smaller", "than a cat.", "(small)"), ("A horse is", "faster", "than a dog.", "(fast)"),
    ("A cat is", "more", "beautiful than a fish.", "(beautiful)"), ("A lion is", "bigger", "than a cat.", "(big)")],
   [("short adjective", "+ ER than"), ("long adjective", "MORE + adjective + than")], "comparatives: short adjectives take er, long adjectives take more"),
 "countable-uncountable": _p("In the kitchen", "Is or are?",
   [("There", "is", "some milk.", ""), ("There", "are", "some eggs.", ""),
    ("There", "is", "some rice.", ""), ("There", "are", "some apples.", "")],
   [("you can count: egg, apple", "ARE + some"), ("you cannot count: milk, rice", "IS + some")], "countable nouns take are, uncountable nouns take is"),
 "demonstratives": _p("At the market", "Near or far?",
   [("", "This", "apple is red. (near, one)", ""), ("", "That", "apple is green. (far, one)", ""),
    ("", "These", "oranges are sweet. (near, two)", ""), ("", "Those", "bananas are yellow. (far, two)", "")],
   [("near", "THIS &middot; THESE"), ("far", "THAT &middot; THOSE")], "this and these are near, that and those are far"),
 "going-to": _p("Weekend plans", "What are they going to do?",
   [("I", "am", "going to visit my aunt.", ""), ("You", "are", "going to cook.", ""),
    ("Tom", "is", "going to play football.", ""), ("We", "are", "going to watch a film.", "")],
   [("I", "AM going to"), ("you &middot; we &middot; they", "ARE going to"), ("he &middot; she &middot; it", "IS going to")], "going to: am, are or is, then going to and a verb"),
 "how-much-cost": _p("Shopping", "How much or how many?",
   [("", "How much", "is the bread? &mdash; Two euros.", ""), ("", "How many", "apples do you want? &mdash; Six.", ""),
    ("", "How much", "milk do you need? &mdash; A litre.", ""), ("", "How many", "eggs? &mdash; Ten.", "")],
   [("you can count: apples", "HOW MANY"), ("price, or you cannot count: milk", "HOW MUCH")], "how many for countable things, how much for price and uncountable things"),
 "id-like": _p("In a caf&eacute;".replace("&eacute;", "é"), "What would they like?",
   [("I", "would", "like a tea, please.", ""), ("Anna", "would", "like a sandwich.", ""),
    ("", "Would", "you like some water?", ""), ("We", "would", "like the menu, please.", "")],
   [("I &middot; you &middot; he &middot; she &middot; we &middot; they", "WOULD like"), ("short form", "'D like")], "would like is the polite way to ask for something"),
 "like-love-hate": _p("Food I like", "How much do you like it?",
   [("I", "love", "pizza. &#9829;&#9829;", ""), ("I", "like", "rice. &#9829;", ""),
    ("I", "don't like", "fish. &#10007;", ""), ("I", "hate", "onions. &#10007;&#10007;", "")],
   [("&#9829;&#9829;", "LOVE"), ("&#9829;", "LIKE"), ("&#10007;", "DON'T LIKE"), ("&#10007;&#10007;", "HATE")], "scale from love to hate"),
 "much-many": _p("At the party", "Much or many?",
   [("I haven't got", "much", "time.", ""), ("She hasn't got", "many", "friends here.", ""),
    ("There aren't", "many", "chairs.", ""), ("There isn't", "much", "food.", "")],
   [("you can count: friends, chairs", "MANY"), ("you cannot count: time, food", "MUCH")], "many for countable nouns, much for uncountable nouns"),
 "numbers-dates": _p("Birthdays", "Which number?",
   [("My birthday is on the", "fifth", "of May.", "(5th)"), ("Tom is", "twelve", "years old.", "(12)"),
    ("The party is on the", "twentieth", "of July.", "(20th)"), ("Anna is", "ten", "today.", "(10)")],
   [("5", "FIVE"), ("5th", "FIFTH"), ("12", "TWELVE"), ("12th", "TWELFTH")], "numbers and dates: five and fifth, twelve and twelfth"),
 "past-simple-be": _p("Yesterday", "Was or were?",
   [("I", "was", "at home.", ""), ("You", "were", "at school.", ""),
    ("Anna", "was", "at work.", ""), ("We", "were", "in the park.", "")],
   [("I &middot; he &middot; she &middot; it", "WAS"), ("you &middot; we &middot; they", "WERE")], "past of be: was and were"),
 "past-simple-regular": _p("Last weekend", "What did they do?",
   [("I", "watched", "a film.", "(watch)"), ("Anna", "cooked", "dinner.", "(cook)"),
    ("We", "played", "football.", "(play)"), ("They", "visited", "Paris.", "(visit)")],
   [("watch", "WATCHED"), ("like", "LIKED")], "regular past: add ed, or d after e"),
 "past-simple-irregular": _p("Yesterday morning", "What did they do?",
   [("I", "went", "to school.", "(go)"), ("Anna", "ate", "an apple.", "(eat)"),
    ("Tom", "drank", "coffee.", "(drink)"), ("We", "saw", "a film.", "(see)")],
   [("go", "WENT"), ("eat", "ATE"), ("drink", "DRANK"), ("see", "SAW")], "irregular past forms have to be learned"),
 "plurals-regular": _p("In my bag", "How many?",
   [("one book &rarr; two", "books", "", ""), ("one pen &rarr; two", "pens", "", ""),
    ("one box &rarr; two", "boxes", "", ""), ("one city &rarr; two", "cities", "", "")],
   [("book", "BOOKS"), ("box", "BOXES"), ("city", "CITIES")], "regular plurals: s, es, and y becomes ies"),
 "plurals-irregular": _p("People and animals", "What is the plural?",
   [("one man &rarr; two", "men", "", ""), ("one child &rarr; two", "children", "", ""),
    ("one foot &rarr; two", "feet", "", ""), ("one mouse &rarr; two", "mice", "", "")],
   [("man", "MEN"), ("woman", "WOMEN"), ("child", "CHILDREN"), ("foot", "FEET")], "irregular plurals change the word"),
 "possessive-s": _p("Whose is it?", "Whose is it?",
   [("This is", "Anna's", "bag.", "(Anna)"), ("That is", "Tom's", "car.", "(Tom)"),
    ("These are", "my parents'", "keys.", "(my parents)"), ("It is the", "dog's", "ball.", "(the dog)")],
   [("one owner", "+ 'S"), ("owners ending in s", "+ '")], "possessive s: apostrophe s after one owner"),
 "prepositions-place": _p("My room", "Where is it?",
   [("The book is", "on", "the table.", ""), ("The cat is", "under", "the bed.", ""),
    ("The lamp is", "next to", "the bed.", ""), ("The keys are", "in", "the bag.", "")],
   [("on top", "ON"), ("inside", "IN"), ("below", "UNDER"), ("beside", "NEXT TO")], "prepositions of place"),
 "prepositions-time": _p("My week", "At, on or in?",
   [("I get up", "at", "seven.", ""), ("I have English", "on", "Monday.", ""),
    ("My birthday is", "in", "June.", ""), ("My party is", "on", "5 May.", "")],
   [("clock time", "AT"), ("days &middot; dates", "ON"), ("months &middot; seasons", "IN")], "at for clock times, on for days, in for months"),
 "present-continuous": _p("Right now", "What are they doing now?",
   [("I", "am", "reading.", ""), ("You", "are", "eating.", ""),
    ("Anna", "is", "cooking.", ""), ("They", "are", "playing.", "")],
   [("I", "AM + verb-ing"), ("you &middot; we &middot; they", "ARE + verb-ing"), ("he &middot; she &middot; it", "IS + verb-ing")], "present continuous: am, are or is plus verb-ing"),
 "question-words": _p("Meeting people", "What do you ask?",
   [("", "What", "is your name? &mdash; Tanya.", ""), ("", "Where", "are you from? &mdash; France.", ""),
    ("", "How old", "are you? &mdash; Twenty.", ""), ("", "Who", "is that? &mdash; My brother.", "")],
   [("thing", "WHAT"), ("place", "WHERE"), ("person", "WHO"), ("age", "HOW OLD")], "question words"),
 "some-vs-any": _p("In the fridge", "Some or any?",
   [("There is", "some", "milk. &#10003;", ""), ("There aren't", "any", "eggs. &#10007;", ""),
    ("Is there", "any", "cheese? ?", ""), ("There are", "some", "apples. &#10003;", "")],
   [("&#10003;", "SOME"), ("&#10007; &middot; ?", "ANY")], "some in positive sentences, any in negatives and questions"),
 "superlative-adjectives": _p("Animals", "Which is the most?",
   [("The elephant is", "the biggest", "animal.", "(big)"), ("The cheetah is", "the fastest", "animal.", "(fast)"),
    ("The mouse is", "the smallest", "animal here.", "(small)"), ("The dog is", "the most", "friendly animal.", "(friendly)")],
   [("short adjective", "THE + -EST"), ("long adjective", "THE MOST + adjective")], "superlatives: the est, or the most"),
 "telling-time": _p("My day", "What time is it?",
   [("It is", "seven", "o'clock.", "(7:00)"), ("It is", "half", "past eight.", "(8:30)"),
    ("It is", "quarter", "past nine.", "(9:15)"), ("It is", "quarter", "to ten.", "(9:45)")],
   [(":00", "O'CLOCK"), (":15", "QUARTER PAST"), (":30", "HALF PAST"), (":45", "QUARTER TO")], "telling the time"),
 "there-was-were": _p("Last night at home", "Was or were?",
   [("There", "was", "a cake.", ""), ("There", "were", "two cats.", ""),
    ("There", "was", "no milk.", ""), ("There", "were", "three books.", "")],
   [("1 thing", "THERE WAS"), ("2 or more", "THERE WERE")], "there was for one, there were for more"),
 "will": _p("Tomorrow", "What will happen?",
   [("I", "will", "call you.", ""), ("Anna", "will", "be at school.", ""),
    ("It", "will", "rain.", ""), ("We", "won't", "be late.", "")],
   [("every person", "WILL + verb"), ("&#10007;", "WON'T + verb")], "will and won't plus the base verb"),
 "articles": _p("In my bag", "A, an or the?",
   [("I have", "a", "dog.", ""), ("I have", "an", "egg.", ""),
    ("Look! This is", "the", "book from Anna.", ""), ("She has", "a", "red pen.", "")],
   [("consonant sound", "A"), ("vowel sound", "AN"), ("a known thing", "THE")], "a before consonant sounds, an before vowel sounds, the for known things"),
})

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
        out.append('    <span class="gv-pair"><span class="gv-slot gv-r1">%s</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">%s</span></span>' % (l, r))
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
