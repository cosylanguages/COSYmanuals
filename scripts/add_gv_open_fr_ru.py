#!/usr/bin/env python3
"""gv-open openings for French and Russian A1 grammar pages, grounded in the repo:
  * the theme chip is the page's own "vocabulary theme" pill (theme-pill),
  * only pages whose grammar id is taught by a lesson in ../cosyplatform/curriculums/<lang>/general/A1.json get an opening
    (the lesson title is recorded in the check output),
  * visuals.css is linked so the components render (these pages did not load it).
The sentences are DRAFTS written for A1 and need a native speaker's review (see the PR).
   python3 scripts/add_gv_open_fr_ru.py [--check]"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAT = ROOT.parent / "cosyplatform"

I18N = {
 "fr": dict(gap="blanc", think="Pensez au mot, puis ", screen="touchez la ligne.", print="écrivez-le sur la ligne.", people="Personnes"),
 "ru": dict(gap="пропуск", think="Подумайте о слове, потом ", screen="нажмите на строку.", print="впишите на строке.", people="Люди"),
}

def L(subj, ans, tail="", hint=""):
    return (subj, ans, tail, hint)

def P(q, lines, formula, label):
    return dict(q=q, lines=lines, formula=formula, label=label)

FR = {
 "avoir": P("Qu'est-ce qu'ils ont ?", [L("J'", "ai", "faim."), L("Tu", "as", "soif."), L("Elle", "a", "froid."), L("Nous", "avons", "chaud.")],
   [("je", "AI"), ("tu", "AS"), ("il &middot; elle", "A"), ("nous", "AVONS"), ("vous", "AVEZ"), ("ils &middot; elles", "ONT")], "le verbe avoir au présent"),
 "adjectifs-possessifs": P("C'est à qui ?", [L("J'ai un frère : c'est", "mon", "frère."), L("Tu as une sœur : c'est", "ta", "sœur."), L("Elle a des parents : ce sont", "ses", "parents."), L("Nous avons une maison : c'est", "notre", "maison.")],
   [("je", "MON &middot; MA &middot; MES"), ("tu", "TON &middot; TA &middot; TES"), ("il &middot; elle", "SON &middot; SA &middot; SES"), ("nous", "NOTRE &middot; NOS")], "adjectifs possessifs"),
 "articles-partitifs": P("Du, de la ou de l' ?", [L("Je mange", "du", "pain."), L("Je bois", "du", "café."), L("Je mange", "de la", "confiture."), L("Je bois", "de l'", "eau.")],
   [("masculin", "DU"), ("féminin", "DE LA"), ("voyelle", "DE L'")], "articles partitifs"),
 "aimer-adorer-detester": P("Quels sont vos goûts ?", [L("J'", "adore", "la musique. &#9829;&#9829;"), L("J'", "aime", "le football. &#9829;"), L("Je", "n'aime pas", "le poisson. &#10007;"), L("Je", "déteste", "les oignons. &#10007;&#10007;")],
   [("&#9829;&#9829;", "ADORER"), ("&#9829;", "AIMER"), ("&#10007;", "NE PAS AIMER"), ("&#10007;&#10007;", "DÉTESTER")], "adorer, aimer, ne pas aimer, détester"),
 "comparatif": P("Plus, moins ou aussi ?", [L("Le train est", "plus", "rapide que le bus."), L("Le vélo est", "moins", "rapide que la voiture."), L("Le métro est", "aussi", "pratique que le bus."), L("L'avion est", "plus", "cher que le train.")],
   [("+", "PLUS ... QUE"), ("&minus;", "MOINS ... QUE"), ("=", "AUSSI ... QUE")], "le comparatif"),
 "heure": P("Quelle heure est-il ?", [L("Il est", "sept", "heures. (7 h 00)"), L("Il est", "midi", ". (12 h 00)"), L("Il est huit heures et", "quart", ". (8 h 15)"), L("Il est neuf heures et", "demie", ". (9 h 30)")],
   [(":00", "... HEURES"), (":15", "ET QUART"), (":30", "ET DEMIE"), (":45", "MOINS LE QUART")], "dire l'heure"),
 "il-y-a": P("Qu'est-ce qu'il y a en ville ?", [L("", "Il y a", "une banque en ville. &#10003;"), L("", "Il y a", "des magasins. &#10003;"), L("", "Il n'y a pas", "de cinéma. &#10007;"), L("Est-ce qu'", "il y a", "une pharmacie ? ?")],
   [("&#10003;", "IL Y A + un &middot; une &middot; des"), ("&#10007;", "IL N'Y A PAS DE + nom")], "il y a"),
 "je-voudrais": P("Qu'est-ce qu'ils voudraient ?", [L("Je", "voudrais", "un café, s'il vous plaît."), L("Il", "voudrait", "un thé."), L("Nous", "voudrions", "deux jus d'orange."), L("Je", "voudrais", "l'addition, s'il vous plaît.")],
   [("je", "VOUDRAIS"), ("il &middot; elle", "VOUDRAIT"), ("nous", "VOUDRIONS")], "je voudrais pour demander poliment"),
 "imperatif": P("Que dit l'entraîneur ?", [L("", "Joue", "au tennis ! (jouer, tu)"), L("", "Courez", "vite ! (courir, vous)"), L("", "Nageons", "ensemble ! (nager, nous)"), L("", "Ne", "cours pas ! (non)")],
   [("tu", "VERBE (sans tu)"), ("nous", "VERBE (sans nous)"), ("vous", "VERBE (sans vous)"), ("non", "NE + verbe + PAS")], "l'impératif"),
 "nombres-jours-mois": P("Quel jour, quel mois ?", [L("Après lundi, c'est", "mardi", "."), L("Avant samedi, c'est", "vendredi", "."), L("Le premier mois de l'année, c'est", "janvier", "."), L("Après juin, c'est", "juillet", ".")],
   [("1", "LUNDI"), ("2", "MARDI"), ("3", "MERCREDI"), ("4", "JEUDI"), ("5", "VENDREDI"), ("6", "SAMEDI"), ("7", "DIMANCHE")], "les jours de la semaine"),
 "pouvoir-vs-savoir": P("Pouvoir ou savoir ?", [L("Je", "sais", "nager. (j'ai appris)"), L("Tu", "peux", "entrer. (c'est permis)"), L("Elle", "sait", "parler français. (elle a appris)"), L("Nous", "pouvons", "venir demain. (c'est possible)")],
   [("une compétence apprise", "SAVOIR + verbe"), ("possibilité &middot; permission", "POUVOIR + verbe")], "pouvoir et savoir"),
 "vouloir-infinitif": P("Que veulent-ils faire ?", [L("Je", "veux", "voyager en Italie."), L("Tu", "veux", "aller à la plage ?"), L("Elle", "veut", "visiter Paris."), L("Nous", "voulons", "dormir tard.")],
   [("je &middot; tu", "VEUX"), ("il &middot; elle", "VEUT"), ("nous", "VOULONS"), ("vous", "VOULEZ"), ("ils &middot; elles", "VEULENT")], "vouloir + infinitif"),
 "passe-compose-avoir": P("Qu'est-ce qu'ils ont fait ?", [L("Hier, j'", "ai", "regardé un film."), L("Tu", "as", "joué au foot."), L("Elle", "a", "mangé une pizza."), L("Nous", "avons", "visité Paris.")],
   [("avoir au présent", "+ participe passé")], "passé composé avec avoir"),
 "mots-interrogatifs": P("Que demande-t-on ?", [L("", "Comment", "vous vous appelez ?"), L("", "Où", "habitez-vous ?"), L("", "Quel", "âge avez-vous ?"), L("", "Quand", "êtes-vous né ?")],
   [("le nom", "COMMENT"), ("le lieu", "OÙ"), ("l'âge", "QUEL ÂGE"), ("le moment", "QUAND")], "les mots interrogatifs"),
 "pluriel-des-noms": P("Quel est le pluriel ?", [L("un chat &rarr; des", "chats", ""), L("un oiseau &rarr; des", "oiseaux", ""), L("un cheval &rarr; des", "chevaux", ""), L("une souris &rarr; des", "souris", "")],
   [("chat", "CHATS"), ("oiseau", "OISEAUX"), ("cheval", "CHEVAUX"), ("souris", "SOURIS")], "le pluriel des noms"),
 "prepositions-lieu-1": P("Où est-ce ?", [L("Le chat est", "sur", "le canapé."), L("Le livre est", "sous", "la table."), L("Le sac est", "dans", "la chambre."), L("La lampe est", "à côté", "du lit.")],
   [("dessus", "SUR"), ("dessous", "SOUS"), ("à l'intérieur", "DANS"), ("près de", "À CÔTÉ DE")], "prépositions de lieu"),
}

RU = {
 "predlogi-mesta": P("Где это?", [L("Книга", "на", "столе."), L("Одежда", "в", "шкафу."), L("Диван", "у", "окна."), L("Ключи", "в", "сумке.")],
   [("внутри", "В + предложный"), ("на поверхности", "НА + предложный"), ("рядом", "У + родительный")], "предлоги места"),
 "prityazhatelnye-mestoimeniya": P("Чей это?", [L("Это я. Это", "мой", "брат."), L("Это ты. Это", "твоя", "сестра."), L("Это она. Это", "её", "мама."), L("Это мы. Это", "наш", "дом.")],
   [("я", "МОЙ &middot; МОЯ &middot; МОЁ &middot; МОИ"), ("ты", "ТВОЙ &middot; ТВОЯ"), ("он &middot; она", "ЕГО &middot; ЕЁ"), ("мы", "НАШ &middot; НАША")], "притяжательные местоимения"),
 "narechiya-chastoty": P("Как часто?", [L("Я", "всегда", "пью кофе утром. (100%)"), L("Я", "обычно", "иду на работу пешком. (80%)"), L("Я", "иногда", "смотрю телевизор. (50%)"), L("Я", "никогда", "не курю. (0%)")],
   [("100%", "ВСЕГДА"), ("80%", "ОБЫЧНО"), ("50%", "ИНОГДА"), ("0%", "НИКОГДА")], "наречия частоты"),
 "lyubit-nravitsya": P("Что вам нравится?", [L("Я", "люблю", "музыку. &#9829;&#9829;"), L("Мне", "нравится", "футбол. &#9829;"), L("Я", "не люблю", "рано вставать. &#10007;"), L("Мне", "не нравится", "дождь. &#10007;&#10007;")],
   [("я", "ЛЮБЛЮ + кого? что?"), ("мне", "НРАВИТСЯ + что?")], "любить и нравиться"),
 "ya-khotel-by-khotite": P("Что они хотят заказать?", [L("Я", "хотел бы", "чай, пожалуйста. (м.)"), L("Мы", "хотели бы", "два кофе."), L("", "Вы", "хотите чай или кофе?"), L("Она", "хотела бы", "сок.")],
   [("я (м.)", "ХОТЕЛ БЫ"), ("я &middot; она (ж.)", "ХОТЕЛА БЫ"), ("мы &middot; они", "ХОТЕЛИ БЫ")], "я хотел бы"),
 "povelitelnoe-naklonenie": P("Что говорят?", [L("", "Открой", "окно, пожалуйста. (открыть)"), L("", "Закрой", "дверь. (закрыть)"), L("", "Помой", "посуду. (помыть)"), L("", "Не", "спи на диване. (нет)")],
   [("ты", "ОТКРОЙ"), ("вы", "ОТКРОЙТЕ"), ("нет", "НЕ ОТКРЫВАЙ")], "повелительное наклонение"),
 "predlozhnyy-padezh": P("Какое окончание?", [L("Я живу в", "городе", ". (город)"), L("Он работает в", "банке", ". (банк)"), L("Мы живём в", "Москве", ". (Москва)"), L("Книга лежит на", "столе", ". (стол)")],
   [("город", "В ГОРОДЕ"), ("банк", "В БАНКЕ"), ("Москва", "В МОСКВЕ"), ("стол", "НА СТОЛЕ")], "предложный падеж"),
 "budushchee-vremya": P("Что будут делать?", [L("Завтра я", "буду", "работать."), L("Ты", "будешь", "дома?"), L("Мы", "будем", "отдыхать."), L("Они", "будут", "учиться.")],
   [("я", "БУДУ"), ("ты", "БУДЕШЬ"), ("он &middot; она", "БУДЕТ"), ("мы", "БУДЕМ"), ("вы", "БУДЕТЕ"), ("они", "БУДУТ")], "будущее время: быть + инфинитив"),
 "prilagatelnye": P("Какой он? Какая она?", [L("Это мой брат. Он", "добрый", "."), L("Это моя сестра. Она", "добрая", "."), L("Это моё имя. Оно", "красивое", "."), L("Это мои друзья. Они", "добрые", ".")],
   [("он", "ДОБРЫЙ"), ("она", "ДОБРАЯ"), ("оно", "ДОБРОЕ"), ("они", "ДОБРЫЕ")], "прилагательные меняют окончание"),
 "mnogo-malo-skolko": P("Сколько?", [L("", "Сколько", "стоит хлеб?"), L("На рынке", "много", "людей."), L("В магазине", "мало", "молока."), L("", "Сколько", "яблок вам нужно?")],
   [("цена", "СКОЛЬКО СТОИТ?"), ("большое количество", "МНОГО"), ("маленькое количество", "МАЛО")], "много, мало, сколько"),
 "voprositelnye-slova": P("О чём спрашивают?", [L("", "Как", "вас зовут?"), L("", "Где", "вы живёте?"), L("", "Кто", "это?"), L("", "Сколько", "вам лет?")],
   [("имя", "КАК"), ("место", "ГДЕ"), ("человек", "КТО"), ("возраст", "СКОЛЬКО ЛЕТ")], "вопросительные слова"),
}
DATA = {"fr": FR, "ru": RU}

E = html.escape
ANCHOR = re.compile(r'(<hr class="rule">\s*</div>\n)')
COMP = re.compile(r'(<link rel="stylesheet" href="((?:\.\./)+)shared/styles/components\.css">\n)')

def lessons_for(lang):
    f = PLAT / "curriculums" / lang / "general" / "A1.json"
    if not f.exists(): return None
    use = {}
    def walk(o):
        if isinstance(o, dict):
            for g in o.get("grammarIds", []): use.setdefault(g, o.get("title", ""))
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(json.load(open(f, encoding="utf8")))
    return use

def pill(t):
    m = re.search(r'theme-pill">.*?</span>(.*?)</div>', t, re.S)
    if not m: return None
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip().split(":")[-1].strip()

def build(lang, slug, d, theme):
    i = I18N[lang]; gid = "open-%s-a1-%s" % (lang, slug)
    out = ['<section class="gv gv-open" aria-labelledby="%s">' % gid,
           '  <span class="gv-theme">%s</span>' % E(theme),
           '  <h2 class="gv-title" id="%s">%s%s<span class="gv-screen">%s</span><span class="gv-print">%s</span></h2>' % (gid, E(d["q"], quote=False), " " + i["think"], i["screen"], i["print"]),
           '  <ol class="gv-lines">']
    for subj, ans, tail, hint in d["lines"]:
        s = ('<span class="gv-r1">%s</span> ' % subj) if subj else ""
        out.append('    <li>%s<details class="gv-gap"><summary><span class="gv-sr">%s</span></summary><span class="gv-r2">%s</span></details>%s%s%s</li>'
                   % (s, i["gap"], E(ans, quote=False), "" if tail[:1] in ".?,!" else " ", tail, (" " + E(hint)) if hint else ""))
    out.append("  </ol>")
    out.append('  <div class="gv gv-formula" role="group" aria-label="%s">' % E(d["label"]))
    for l, r in d["formula"]:
        out.append('    <span class="gv-pair"><span class="gv-slot gv-r1">%s</span><span class="gv-op">&rarr;</span><span class="gv-slot gv-r2">%s</span></span>' % (l, r))
    out.append("  </div>\n</section>\n")
    return "\n".join(out)

def main():
    check = "--check" in sys.argv; need = 0; skipped = []
    for lang, pages in DATA.items():
        use = lessons_for(lang)
        if use is None:
            print(lang, ": cosyplatform curricula not found; skipped"); continue
        for slug, d in pages.items():
            gid = "%s-a1-%s" % (lang, slug)
            p = ROOT / "manuals" / lang / "grammar" / "a1" / "topics" / (slug + ".html")
            t = p.read_text(encoding="utf8")
            if gid not in use: skipped.append(gid); continue
            if "gv-open" in t: continue
            th = pill(t)
            if not th: skipped.append(gid + " (no theme pill)"); continue
            need += 1
            if check: print("lacks opening:", gid, "| lesson:", use[gid], "| theme:", th); continue
            m = ANCHOR.search(t)
            if not m: skipped.append(gid + " (no page-head anchor)"); continue
            t = t[:m.end()] + build(lang, slug, d, th) + "\n" + t[m.end():]
            if "shared/styles/visuals.css" not in t:
                t = COMP.sub(lambda m: m.group(1) + '<link rel="stylesheet" href="%sshared/styles/visuals.css">\n' % m.group(2), t, count=1)
            p.write_text(t, encoding="utf8")
    print(("check: %d openings missing" if check else "added %d openings") % need)
    for s in skipped: print("  skipped:", s)
    return 1 if check and need else 0

if __name__ == "__main__":
    sys.exit(main())
