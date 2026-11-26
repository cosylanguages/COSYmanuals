"""Tatar, Bashkir, Chuvash, Breton, Armenian and Georgian timeline profiles."""

from tense_timelines_en import span, point, now


TT_PROFILES = {
    "tt-present": dict(
        aria="хәзерге заман: гадәти гамәл",
        items=[span(8, 92, "present", "хәзерге заман · гадәт"), now(50, "хәзер")],
    ),
    "tt-past": dict(
        aria="үткән заман: тәмамланган гамәл",
        items=[point(32, "past", "үткән заман · тәмамланган"), now(82, "хәзер")],
    ),
    "tt-future": dict(
        aria="киләчәк заман",
        items=[now(22, "хәзер"), point(72, "future", "киләчәк заман")],
    ),
}


BA_PROFILES = {
    "ba-present": dict(
        aria="хәҙерге заман: ғәҙәти ғәмәл",
        items=[span(8, 92, "present", "хәҙерге заман · ғәҙәт"), now(50, "хәҙер")],
    ),
    "ba-past": dict(
        aria="үткән заман: тамамланған ғәмәл",
        items=[point(32, "past", "үткән заман · тамамланған"), now(82, "хәҙер")],
    ),
    "ba-future": dict(
        aria="киләсәк заман",
        items=[now(22, "хәҙер"), point(72, "future", "киләсәк заман")],
    ),
}


CV_PROFILES = {
    "cv-present": dict(
        aria="хальхи вăхăт: йăлари ĕç",
        items=[span(8, 92, "present", "хальхи вăхăт · йăла"), now(50, "халь")],
    ),
    "cv-past": dict(
        aria="иртнĕ вăхăт: пĕтнĕ ĕç",
        items=[point(32, "past", "иртнĕ вăхăт · пĕтнĕ"), now(82, "халь")],
    ),
    "cv-future": dict(
        aria="пулаяс вăхăт",
        items=[now(22, "халь"), point(72, "future", "пулаяс вăхăт")],
    ),
}


BR_PROFILES = {
    "br-present": dict(
        aria="amzer-vremañ: boaz ha faktou",
        items=[span(8, 92, "present", "amzer-vremañ · boaz"), now(50, "bremañ")],
    ),
    "br-past": dict(
        aria="amzer-dremen: ober echuet",
        items=[point(32, "past", "amzer-dremen · echuet"), now(82, "bremañ")],
    ),
}


HY_PROFILES = {
    "hy-present": dict(
        aria="ներկա ժամանակ: սովորություն",
        items=[span(8, 92, "present", "ներկա ժամանակ · սովորություն"), now(50, "հիմա")],
    ),
    "hy-past": dict(
        aria="անցյալ ժամանակ: ավարտված գործողություն",
        items=[point(32, "past", "անցյալ ժամանակ · ավարտված"), now(82, "հիմա")],
    ),
    "hy-past-imperfect": dict(
        aria="անցյալ անկատար և անցյալ կատարյալ",
        items=[span(15, 55, "past", "անցյալ անկատար · ընթացք", below=False), point(66, "past", "անցյալ կատարյալ · ավարտված"), now(86, "հիմա")],
    ),
    "hy-future": dict(
        aria="ապառնի ժամանակ",
        items=[now(22, "հիմա"), point(72, "future", "ապառնի ժամանակ")],
    ),
}


KA_PROFILES = {
    "ka-tenses": dict(
        aria="ზმნის დროები: წარსული, ახლა და მომავალი",
        items=[span(6, 36, "past", "წარსული"), span(42, 58, "present", "ახლა"), span(64, 94, "future", "მომავალი"), now(50, "ახლა")],
    ),
}


TT_SLUG_TO_PROFILE = {
    "hazierge-zaman": "tt-present",
    "utkan-zaman": "tt-past",
    "kilechak-zaman": "tt-future",
}

BA_SLUG_TO_PROFILE = {
    "hadherge-zaman": "ba-present",
    "utkan-zaman": "ba-past",
    "utken-zamandar": "ba-past",
    "kilechak-zaman": "ba-future",
}

CV_SLUG_TO_PROFILE = {
    "halkhi-vakhat": "cv-present",
    "irtne-vakhat": "cv-past",
    "Iskil-viesleny": "cv-past",
    "pulayas-vakhat": "cv-future",
}

BR_SLUG_TO_PROFILE = {
    "amzer-vreman-simpl": "br-present",
    "ar-verb-bezan": "br-present",
    "ar-verb-kaout": "br-present",
    "amzer-dremen-gevrennek": "br-past",
}

HY_SLUG_TO_PROFILE = {
    "nerka-zhamanak": "hy-present",
    "antsyal-zhamanak": "hy-past",
    "ancyal-katarhyal-yev-ancyal-anhatar": "hy-past-imperfect",
    "aparni-zhamanak": "hy-future",
}

KA_SLUG_TO_PROFILE = {
    "zmna-da-droebrivi-fortmebi": "ka-tenses",
}
