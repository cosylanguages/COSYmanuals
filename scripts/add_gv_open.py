#!/usr/bin/env python3
"""Insert the gv-open opening (a theme chip, a few gap lines, the formula) before the outcome banner of
English A1 and A2 grammar pages. Content lives in PAGES below, written for A1: short lines, one vocabulary theme per page.
Idempotent. `--check` lists pages in PAGES that lack the opening.
  python3 scripts/add_gv_open.py [--check]"""
import html, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

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

PAGES_A2 = {
 "past-continuous": _p("Yesterday evening", "What were they doing?",
   [("I", "was", "cooking at seven.", ""), ("You", "were", "watching TV.", ""),
    ("Anna", "was", "reading a book.", ""), ("They", "were", "playing football.", "")],
   [("I &middot; he &middot; she &middot; it", "WAS + verb-ing"), ("you &middot; we &middot; they", "WERE + verb-ing")], "past continuous: was or were plus verb-ing"),
 "past-simple-vs-past-continuous": _p("A busy morning", "Long action or short action?",
   [("While I", "was walking", "to work, it started to rain.", "(walk)"), ("I", "met", "my friend while I was shopping.", "(meet)"),
    ("When the phone rang, Anna", "was cooking", ".", "(cook)"), ("Tom", "saw", "an accident when he was driving.", "(see)")],
   [("long action", "WAS &middot; WERE + verb-ing"), ("short action", "past simple")], "past continuous for the long action, past simple for the short action"),
 "present-perfect-form-use": _p("Life experience", "What have they done?",
   [("I", "have", "visited Rome.", ""), ("Anna", "has", "tried sushi.", ""),
    ("We", "have", "seen that film.", ""), ("Tom", "has", "met a famous actor.", "")],
   [("I &middot; you &middot; we &middot; they", "HAVE + participle"), ("he &middot; she &middot; it", "HAS + participle")], "present perfect: have or has plus past participle"),
 "present-perfect-ever-never-for-since": _p("Life experience", "Ever, never, for or since?",
   [("Have you", "ever", "been to Spain?", ""), ("I have", "never", "eaten snails.", ""),
    ("I have lived here", "for", "five years.", ""), ("She has worked here", "since", "2020.", "")],
   [("a question", "EVER"), ("not once", "NEVER"), ("5 years", "FOR"), ("2020", "SINCE")], "ever, never, for a period, since a starting point"),
 "present-perfect-just-already-yet": _p("Today's to-do list", "Just, already or yet?",
   [("I have", "just", "made coffee. (a minute ago)", ""), ("She has", "already", "cleaned the kitchen. (done)", ""),
    ("Have you finished", "yet", "? (question)", ""), ("He hasn't called", "yet", ". (not done)", "")],
   [("a moment ago", "JUST"), ("done, early", "ALREADY"), ("not done &middot; ?", "YET")], "just, already and yet with the present perfect"),
 "present-perfect-vs-past-simple": _p("News and finished times", "Present perfect or past simple?",
   [("I", "have", "lost my keys. (now: no keys)", ""), ("I", "lost", "my keys yesterday.", "(lose)"),
    ("Anna", "has", "just arrived.", ""), ("We", "went", "to Paris in 2019.", "(go)")],
   [("no time, or until now", "HAVE + participle"), ("finished time: yesterday, 2019", "past simple")], "present perfect for news, past simple for a finished time"),
 "zero-conditional": _p("Cooking and weather", "What always happens?",
   [("If you heat ice, it", "melts", ".", "(melt)"), ("If it rains, the grass", "gets", "wet.", "(get)"),
    ("If I am tired, I", "go", "to bed early.", "(go)"), ("Water", "boils", "if you heat it to 100 degrees.", "(boil)")],
   [("IF + present simple", "present simple")], "zero conditional: if plus present simple, present simple"),
 "first-conditional": _p("Plans and weather", "What will happen?",
   [("If it rains, we", "will", "stay at home.", ""), ("If you study, you", "will", "pass the test.", ""),
    ("If I am late, I", "will", "call you.", ""), ("She", "won't", "come if she is ill.", "")],
   [("IF + present simple", "WILL + verb")], "first conditional: if plus present simple, will plus verb"),
 "second-conditional": _p("Dreams", "What would you do?",
   [("If I had a million euros, I", "would", "travel the world.", ""), ("If I were rich, I", "would", "buy a house.", ""),
    ("If she", "had", "more time, she would read more.", "(have)"), ("If we lived in Paris, we", "would", "eat croissants.", "")],
   [("IF + past simple", "WOULD + verb")], "second conditional: if plus past simple, would plus verb"),
 "should-shouldnt": _p("Health advice", "Good idea or bad idea?",
   [("You", "should", "drink more water.", ""), ("You", "shouldn't", "eat too much sugar.", ""),
    ("He", "should", "see a doctor.", ""), ("We", "shouldn't", "stay up late.", "")],
   [("a good idea", "SHOULD + verb"), ("a bad idea", "SHOULDN'T + verb")], "should and shouldn't give advice"),
 "have-to-must-mustnt": _p("Rules", "Must, mustn't or have to?",
   [("You", "must", "wear a seatbelt. (rule)", ""), ("You", "mustn't", "use your phone here. (forbidden)", ""),
    ("I", "have", "to get up at six. (need)", ""), ("He", "doesn't", "have to wear a uniform. (not necessary)", "")],
   [("rule &middot; need", "MUST &middot; HAVE TO"), ("forbidden", "MUSTN'T"), ("not necessary", "DON'T HAVE TO")], "must and have to for rules, mustn't for forbidden, don't have to for not necessary"),
 "used-to": _p("When I was a child", "What did you use to do?",
   [("I", "used", "to play outside every day.", ""), ("We", "used", "to live in a small village.", ""),
    ("She", "didn't", "use to like vegetables.", ""), ("Did you", "use", "to have a pet?", "")],
   [("a past habit, not now", "USED TO + verb"), ("question &middot; negative", "DID &middot; DIDN'T + USE TO")], "used to for past habits"),
 "will-vs-going-to": _p("Plans and offers", "Will or going to?",
   [("I", "am", "going to visit my aunt tomorrow. (plan)", ""), ("The phone is ringing. I", "will", "answer it. (sudden decision)", ""),
    ("Look at the clouds! It", "is", "going to rain. (I can see it)", ""), ("I think she", "will", "like the gift. (opinion)", "")],
   [("plan &middot; evidence", "GOING TO"), ("sudden decision &middot; opinion", "WILL")], "going to for plans and evidence, will for sudden decisions and opinions"),
 "present-continuous-for-future": _p("My diary", "What are your plans?",
   [("I", "am", "meeting Anna tomorrow.", ""), ("We", "are", "flying to Rome on Friday.", ""),
    ("Tom", "is", "starting a new job next week.", ""), ("They", "are", "having a party on Saturday.", "")],
   [("a fixed plan + a time", "AM &middot; IS &middot; ARE + verb-ing")], "present continuous for fixed future plans"),
 "too-and-enough": _p("Shopping for clothes", "Too or enough?",
   [("The coat is", "too", "big for me.", ""), ("The shoes are not big", "enough", ".", ""),
    ("The jacket is", "too", "expensive.", ""), ("I haven't got", "enough", "money.", "")],
   [("more than needed", "TOO + adjective"), ("after an adjective", "adjective + ENOUGH"), ("before a noun", "ENOUGH + noun")], "too before an adjective, enough after an adjective or before a noun"),
 "much-many-little-few": _p("In the fridge", "How much is left?",
   [("There is", "little", "milk left.", ""), ("There are", "few", "eggs left.", ""),
    ("There isn't", "much", "bread.", ""), ("There aren't", "many", "apples.", "")],
   [("you can count: eggs", "FEW &middot; MANY"), ("you cannot count: milk", "LITTLE &middot; MUCH")], "few and many with countable nouns, little and much with uncountable nouns"),
 "question-forms": _p("An interview", "What do you ask?",
   [("", "Where", "do you live?", ""), ("", "What", "did you do yesterday?", ""),
    ("", "Who", "is your best friend?", ""), ("", "How", "often do you go to the gym?", "")],
   [("where &middot; what &middot; who", "+ DO &middot; DOES &middot; DID + subject + verb")], "question words with do, does or did"),
 "how-questions": _p("Getting to know you", "Which how?",
   [("", "How old", "are you?", ""), ("", "How long", "is the film?", ""),
    ("", "How far", "is the station?", ""), ("", "How often", "do you swim?", "")],
   [("age", "HOW OLD"), ("time", "HOW LONG"), ("distance", "HOW FAR"), ("frequency", "HOW OFTEN")], "how questions"),
 "do-vs-make": _p("At home", "Do or make?",
   [("I", "do", "my homework every day.", ""), ("Anna", "makes", "dinner.", ""),
    ("We", "do", "the washing-up.", ""), ("Tom", "makes", "a lot of noise.", "")],
   [("tasks &middot; jobs", "DO"), ("create &middot; produce", "MAKE")], "do for tasks, make for creating"),
 "indefinite-pronouns": _p("At a party", "Who or what?",
   [("", "Everyone", "is happy.", ""), ("", "Someone", "is at the door.", ""),
    ("There is", "nothing", "to eat.", ""), ("I don't know", "anybody", "here.", "")],
   [("all", "EVERYONE"), ("some", "SOMEONE"), ("none", "NO ONE"), ("any: &#10007; &middot; ?", "ANYONE")], "everyone, someone, no one, anyone"),
 "may-might": _p("Maybe at the weekend", "What might happen?",
   [("I", "might", "go to the cinema.", ""), ("It", "may", "rain tomorrow.", ""),
    ("She", "might", "not come.", ""), ("We", "may", "visit Paris.", "")],
   [("maybe", "MAY &middot; MIGHT + verb")], "may and might for possibility"),
 "prepositions-of-movement": _p("In the city", "Which way?",
   [("Walk", "across", "the bridge.", ""), ("Go", "along", "the river.", ""),
    ("The bus goes", "through", "the tunnel.", ""), ("Turn", "into", "Oak Street.", "")],
   [("side to side", "ACROSS"), ("in a line", "ALONG"), ("in and out", "THROUGH"), ("to the inside", "INTO")], "prepositions of movement"),
 "present-and-past-simple-passive": _p("Famous things", "Is, was or were?",
   [("The Eiffel Tower", "is", "visited by millions.", ""), ("Bread", "is", "made from flour.", ""),
    ("The book", "was", "written in 1990.", ""), ("These shoes", "were", "made in Italy.", "")],
   [("now", "AM &middot; IS &middot; ARE + participle"), ("past", "WAS &middot; WERE + participle")], "passive: be plus past participle"),
}
from gv_open_data_b import B1, B2, C1, C2
import gv_open_curriculum as _cur
for _lv, _d, _o in (("a1", PAGES, _cur.A1), ("a2", PAGES_A2, _cur.A2), ("b1", B1, _cur.B1), ("b2", B2, _cur.B2)):
    for _slug, _ov in _o.items():
        _base = _d[_slug]
        _d[_slug] = dict(_base, lesson=_ov["lesson"], theme=_ov["theme"], title=_ov["q"] + " Think of the word, then ",
                         lines=_ov["lines"], formula=((_ov["label"] or _base["formula"][0]), (_ov["formula"] or _base["formula"][1])))
LEVELS = (("a1", PAGES), ("a2", PAGES_A2), ("b1", B1), ("b2", B2), ("c1", C1), ("c2", C2))

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
        out.append('    <li>%s<details class="gv-gap"><summary><span class="gv-sr">gap</span></summary><span class="gv-r2">%s</span></details>%s%s%s</li>'
                   % (s, E(ans, quote=False), "" if tail[:1] in ".?,!" else " ", tail, (" " + E(hint)) if hint else ""))
    out.append("  </ol>")
    label, pairs = d["formula"]
    out.append('  <div class="gv gv-formula" role="group" aria-label="%s">' % E(label))
    for l, r in pairs:
        out.append('    <span class="gv-pair"><span class="gv-slot gv-r1">%s</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">%s</span></span>' % (l, r))
    out.append("  </div>\n</section>\n")
    return "\n".join(out)

def main():
    check = "--check" in sys.argv; lacking = 0
    for lvl, pages in LEVELS:
        for slug, d in pages.items():
            p = Path("manuals/en/grammar/%s/topics/%s.html" % (lvl, slug)); t = p.read_text(encoding="utf8")
            if "gv-open" in t:
                if "--rebuild" not in sys.argv: continue
                t = re.sub(r'<section class="gv gv-open".*?</section>\n\n?', "", t, count=1, flags=re.S)
            lacking += 1
            if check: print("lacks opening:", lvl, slug); continue
            i = t.index('<div class="box outcome-banner"')
            p.write_text(t[:i] + build(lvl + "-" + slug, d) + "\n" + t[i:], encoding="utf8")
    print(("check: %d pages lack the opening" if check else "added %d openings") % lacking)
    return 1 if check and lacking else 0

if __name__ == "__main__":
    sys.exit(main())
