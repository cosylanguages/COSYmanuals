"""German, Spanish, Italian, Portuguese and Greek tense-timeline profiles."""

from tense_timelines_en import span, point, now


DE_PROFILES = {
    "de-present": dict(
        aria="Gewohnheit und Fakten um die Gegenwart",
        items=[span(8, 92, "present", "Gewohnheit · jeden Tag"), now(50, "jetzt")],
    ),
    "de-perfect": dict(
        aria="abgeschlossene Handlung in der Vergangenheit",
        items=[point(32, "past", "Perfekt · abgeschlossen"), now(82, "jetzt")],
        ccq=[
            dict(q="Ist die Handlung abgeschlossen?", options=["Ja, abgeschlossen", "Nein, sie läuft noch", "Nein, sie ist zukünftig"], correct=0, explain="Das Perfekt beschreibt eine abgeschlossene Handlung."),
            dict(q="Liegt die Handlung in der Vergangenheit?", options=["Ja, in der Vergangenheit", "Nein, jetzt", "Nein, in der Zukunft"], correct=0, explain="Das Perfekt bezieht sich auf die Vergangenheit."),
        ],
    ),
    "de-praeteritum": dict(
        aria="abgeschlossene Handlung in der Vergangenheit",
        items=[point(32, "past", "Präteritum · abgeschlossen"), now(82, "jetzt")],
        ccq=[
            dict(q="Ist die Handlung abgeschlossen?", options=["Ja, abgeschlossen", "Nein, sie läuft noch", "Nein, sie ist zukünftig"], correct=0, explain="Das Präteritum beschreibt eine abgeschlossene Handlung."),
            dict(q="Liegt die Handlung in der Vergangenheit?", options=["Ja, in der Vergangenheit", "Nein, jetzt", "Nein, in der Zukunft"], correct=0, explain="Das Präteritum bezieht sich auf die Vergangenheit."),
        ],
    ),
}


ES_PROFILES = {
    "es-present": dict(
        aria="hábito y hechos alrededor del presente",
        items=[span(8, 92, "present", "hábito · todos los días"), now(50, "ahora")],
        ccq=[
            dict(q="¿La frase describe un hábito o una acción única?", options=["Un hábito o rutina", "Una acción única", "Una acción futura"], correct=0, explain="El presente describe hábitos, rutinas y hechos."),
            dict(q="¿La acción ocurre ahora?", options=["Sí, regularmente", "No, ya terminó", "No, es futura"], correct=0, explain="El presente no significa una acción terminada."),
        ],
    ),
    "es-perfect": dict(
        aria="acción terminada en el pasado",
        items=[point(32, "past", "perfecto · terminado"), now(82, "ahora")],
    ),
    "es-indefinido": dict(
        aria="acción terminada en un momento pasado",
        items=[point(32, "past", "indefinido · terminado"), now(82, "ahora")],
    ),
    "es-imperfect": dict(
        aria="acción en curso o hábito en el pasado",
        items=[span(15, 62, "past", "imperfecto · en curso / hábito"), now(85, "ahora")],
    ),
    "es-perfect-vs-indefinido": dict(
        aria="el imperfecto describe el escenario y el indefinido cuenta el acontecimiento",
        items=[span(18, 55, "past", "imperfecto · escenario", below=False), point(62, "past", "indefinido · acontecimiento"), now(85, "ahora")],
    ),
    "es-future": dict(
        aria="acción situada en el futuro",
        items=[now(22, "ahora"), point(72, "future", "futuro · acción futura")],
    ),
}


IT_PROFILES = {
    "it-present": dict(
        aria="abitudine e fatti intorno al presente",
        items=[span(8, 92, "present", "abitudine · ogni giorno"), now(50, "adesso")],
    ),
    "it-passato": dict(
        aria="azione terminata nel passato",
        items=[point(32, "past", "passato prossimo · finito"), now(82, "adesso")],
    ),
    "it-imperfetto": dict(
        aria="azione in corso o abitudine nel passato",
        items=[span(15, 62, "past", "imperfetto · in corso / abitudine"), now(85, "adesso")],
    ),
    "it-passato-vs-imperfetto": dict(
        aria="l'imperfetto descrive lo sfondo e il passato prossimo racconta l'avvenimento",
        items=[span(18, 55, "past", "imperfetto · sfondo", below=False), point(62, "past", "passato prossimo · avvenimento"), now(85, "adesso")],
    ),
    "it-future": dict(
        aria="azione situata nel futuro",
        items=[now(22, "adesso"), point(72, "future", "futuro · azione futura")],
    ),
    "it-trappassato": dict(
        aria="azione anteriore a un'altra azione passata",
        items=[point(26, "past", "trapassato · prima"), point(62, "past", "passato prossimo · dopo"), now(88, "adesso")],
    ),
}


PT_PROFILES = {
    "pt-present": dict(
        aria="hábito e factos em torno do presente",
        items=[span(8, 92, "present", "hábito · todos os dias"), now(50, "agora")],
    ),
    "pt-perfeito": dict(
        aria="ação terminada no passado",
        items=[point(32, "past", "perfeito · terminado"), now(82, "agora")],
    ),
    "pt-imperfeito": dict(
        aria="ação em curso ou hábito no passado",
        items=[span(15, 62, "past", "imperfeito · em curso / hábito"), now(85, "agora")],
    ),
    "pt-perfeito-vs-imperfeito": dict(
        aria="o imperfeito descreve o cenário e o perfeito conta o acontecimento",
        items=[span(18, 55, "past", "imperfeito · cenário", below=False), point(62, "past", "perfeito · acontecimento"), now(85, "agora")],
    ),
    "pt-future": dict(
        aria="ação situada no futuro",
        items=[now(22, "agora"), point(72, "future", "futuro · ação futura")],
    ),
}


EL_PROFILES = {
    "el-present": dict(
        aria="συνήθεια και γεγονότα γύρω από το παρόν",
        items=[span(8, 92, "present", "συνήθεια · κάθε μέρα"), now(50, "τώρα")],
    ),
    "el-aoristos": dict(
        aria="τελειωμένη πράξη στο παρελθόν",
        items=[point(32, "past", "αόριστος · τελειωμένο"), now(82, "τώρα")],
    ),
    "el-paratatikos": dict(
        aria="πράξη σε εξέλιξη ή συνήθεια στο παρελθόν",
        items=[span(15, 62, "past", "παρατατικός · σε εξέλιξη"), now(85, "τώρα")],
    ),
    "el-aoristos-vs-paratatikos": dict(
        aria="ο παρατατικός δείχνει το σκηνικό και ο αόριστος το γεγονός",
        items=[span(18, 55, "past", "παρατατικός · σκηνικό", below=False), point(62, "past", "αόριστος · γεγονός"), now(85, "τώρα")],
        ccq=[
            dict(q="Ο παρατατικός δείχνει το σκηνικό ή το γεγονός;", options=["Το σκηνικό", "Το γεγονός", "Το μέλλον"], correct=0, explain="Ο παρατατικός περιγράφει το σκηνικό και τις συνήθειες."),
            dict(q="Ο αόριστος δείχνει μια τελειωμένη πράξη;", options=["Ναι, τελειωμένη", "Όχι, σε εξέλιξη", "Όχι, στο μέλλον"], correct=0, explain="Ο αόριστος δηλώνει μια τελειωμένη πράξη."),
        ],
    ),
    "el-parakeimenos": dict(
        aria="πράξη που συνδέει το παρελθόν με το τώρα",
        items=[span(16, 82, "present", "παρακείμενος · παρελθόν → τώρα"), now(82, "τώρα")],
    ),
    "el-future": dict(
        aria="πράξη στο μέλλον",
        items=[now(22, "τώρα"), point(72, "future", "μέλλον · θα + ρήμα")],
        ccq=[
            dict(q="Η πράξη γίνεται στο μέλλον;", options=["Ναι, στο μέλλον", "Όχι, στο παρελθόν", "Όχι, τώρα"], correct=0, explain="Ο μέλλοντας δηλώνει πράξη που θα γίνει."),
            dict(q="Το «θα» δείχνει μέλλον;", options=["Ναι", "Όχι", "Μόνο παρελθόν"], correct=0, explain="Το «θα» σχηματίζει τον μέλλοντα."),
        ],
    ),
}


DE_SLUG_TO_PROFILE = {
    "praesens-regelmaessig": "de-present",
    "perfekt": "de-perfect",
    "perfekt-mit-haben-und-sein": "de-perfect",
    "praeteritum-modalverben": "de-praeteritum",
}

ES_SLUG_TO_PROFILE = {
    "presente-indicativo": "es-present",
    "es-presente-reg": "es-present",
    "preterito-perfecto": "es-perfect",
    "pretérito-perfecto": "es-perfect",
    "preterito-indefinido-y-perfecto": "es-perfect-vs-indefinido",
    "preterito-indefinido-vs-perfecto": "es-perfect-vs-indefinido",
    "el-preterito-imperfecto": "es-imperfect",
    "indefinido-vs-imperfecto": "es-perfect-vs-indefinido",
    "el-futuro-simple": "es-future",
}

IT_SLUG_TO_PROFILE = {
    "presente-regolare": "it-present",
    "passato-prossimo": "it-passato",
    "passato-prossimo-essere-avere": "it-passato",
    "limperfetto-indicativo": "it-imperfetto",
    "passato-prossimo-vs-imperfetto": "it-passato-vs-imperfetto",
    "il-futuro-semplice": "it-future",
    "trapassato-prossimo": "it-trappassato",
}

PT_SLUG_TO_PROFILE = {
    "presente-do-indicativo": "pt-present",
    "preterito-perfeito": "pt-perfeito",
    "preterito-perfeito-composto": "pt-perfeito",
    "preterito-imperfeito-do-indicativo": "pt-imperfeito",
    "perfeito-vs-imperfeito": "pt-perfeito-vs-imperfeito",
    "preterito-perfeito-vs-imperfeito": "pt-perfeito-vs-imperfeito",
    "futuro-do-presente-e-ir": "pt-future",
}

EL_SLUG_TO_PROFILE = {
    "enestotas-omada-a": "el-present",
    "enestotas-omada-v": "el-present",
    "aoristos": "el-aoristos",
    "aoristos-kanonika-rimata": "el-aoristos",
    "aoristos-anomala-rimata": "el-aoristos",
    "paratatikos": "el-paratatikos",
    "parelthontikos-tou-eimai": "el-paratatikos",
    "aoristos-paratatikos": "el-aoristos-vs-paratatikos",
    "parakeimenos": "el-parakeimenos",
    "mellontas-tha": "el-future",
    "syntomos-mellontas": "el-future",
    "mellochrons-exakolouthitikos-stigmiaiou": "el-future",
}
