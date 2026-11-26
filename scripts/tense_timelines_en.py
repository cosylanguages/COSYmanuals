"""English tense-timeline profiles.

Each profile describes the visual timeline for one tense/aspect concept. Labels are
English only (the manual is monolingual). `ccq` is optional: when present it is used
only if the page has no concept-check panel of its own.
"""

def span(frm, to, tone, label=None, below=True):
    return dict(type="span", frm=frm, to=to, tone=tone, label=label, below=below)


def point(at, tone, label, below=True):
    return dict(type="point", at=at, tone=tone, label=label, below=below)


def now(at, label="Now"):
    return dict(type="now", at=at, label=label)


# Reusable CCQ sets (used only when a page has no existing CCQ panel).
CCQ = {
    "present_simple": [
        dict(q="Does this describe a habit or routine?",
             options=["Yes, it happens regularly", "No, it happens only once", "No, it is happening right now"],
             correct=0, explain="Present simple describes habits, routines and facts."),
        dict(q="Is the action happening at this exact moment?",
             options=["Yes, right now", "No, it is a regular activity", "No, it is in the future"],
             correct=1, explain="Present simple does not mean 'right now'; that is present continuous."),
    ],
    "present_continuous": [
        dict(q="Is the action happening around now?",
             options=["Yes, it is in progress", "No, it is a finished past action", "No, it is a permanent fact"],
             correct=0, explain="Present continuous describes an action in progress around now."),
        dict(q="Is the situation permanent?",
             options=["Yes, forever", "No, it is temporary", "No, it is in the past"],
             correct=1, explain="Present continuous often describes temporary situations."),
    ],
    "past_simple": [
        dict(q="Is the action finished?",
             options=["Yes, it is finished", "No, it is still happening", "No, it is in the future"],
             correct=0, explain="Past simple describes a finished action in the past."),
        dict(q="Do we know when it happened?",
             options=["Yes, a past time is stated or understood", "No, the time is not important", "Yes, it is happening now"],
             correct=0, explain="Past simple usually goes with a finished past time."),
    ],
    "past_continuous": [
        dict(q="Was the action in progress at a past moment?",
             options=["Yes, it was in progress", "No, it was finished before", "No, it is happening now"],
             correct=0, explain="Past continuous describes an action in progress at a past moment."),
        dict(q="Does it often set the scene for another action?",
             options=["Yes, a longer background action", "No, a single finished action", "No, a future plan"],
             correct=0, explain="Past continuous often sets the background for a shorter past action."),
    ],
    "present_perfect": [
        dict(q="Does the action connect the past to now?",
             options=["Yes, there is a connection to now", "No, it is completely finished in the past", "No, it is only in the future"],
             correct=0, explain="Present perfect connects a past action to the present."),
        dict(q="Is the exact past time important?",
             options=["Yes, we must say when", "No, the result or experience matters more", "Yes, it is always 'yesterday'"],
             correct=1, explain="Present perfect does not focus on a finished past time."),
    ],
    "present_perfect_continuous": [
        dict(q="Did the action start in the past and continue to now?",
             options=["Yes, it continues up to now", "No, it finished before now", "No, it starts in the future"],
             correct=0, explain="Present perfect continuous describes an action continuing up to now."),
        dict(q="Does it focus on the activity or on a finished result?",
             options=["On the activity and its duration", "On a completed result", "On a future plan"],
             correct=0, explain="Present perfect continuous focuses on the activity and how long it lasts."),
    ],
    "past_perfect": [
        dict(q="Did the action happen before another past action?",
             options=["Yes, it happened earlier", "No, it happened later", "No, it happens now"],
             correct=0, explain="Past perfect describes the earlier of two past actions."),
        dict(q="Is there a second past action for reference?",
             options=["Yes, another past action is the reference point", "No, there is no other action", "Yes, a future action"],
             correct=0, explain="Past perfect needs a later past reference point."),
    ],
    "past_perfect_continuous": [
        dict(q="Did the action continue up to a past moment?",
             options=["Yes, up to a moment in the past", "No, up to now", "No, from a future moment"],
             correct=0, explain="Past perfect continuous describes duration up to a past point."),
        dict(q="Was it still in progress before another past action?",
             options=["Yes, it was ongoing before it", "No, it was finished long before", "No, it is happening now"],
             correct=0, explain="It stresses the ongoing nature before a later past action."),
    ],
    "going_to": [
        dict(q="Was the plan made before now?",
             options=["Yes, the decision already exists", "No, it is decided at this moment", "No, it is a past habit"],
             correct=0, explain="Going to often expresses a plan decided before the moment of speaking."),
        dict(q="Does it point to the future?",
             options=["Yes, it is about the future", "No, it is about the past", "No, it is about a routine"],
             correct=0, explain="Going to points forward to a future action or result."),
    ],
    "will": [
        dict(q="Is the decision made at the moment of speaking?",
             options=["Yes, decided now", "No, planned long before", "No, a finished past action"],
             correct=0, explain="Will often expresses a decision made at the moment of speaking."),
        dict(q="Does it point to the future?",
             options=["Yes, it is about the future", "No, it is about the past", "No, it is a past habit"],
             correct=0, explain="Will points forward to the future."),
    ],
    "have_got": [
        dict(q="Does it describe possession now?",
             options=["Yes, possession at the present time", "No, possession in the past", "No, a future plan"],
             correct=0, explain="Have got describes possession or states now."),
        dict(q="Is the state still true now?",
             options=["Yes, it is true now", "No, it was true only in the past", "No, it will be true only in the future"],
             correct=0, explain="Have got describes a present state."),
    ],
    "ability_present": [
        dict(q="Does it describe a general ability now?",
             options=["Yes, a general ability", "No, a single finished action", "No, a future plan"],
             correct=0, explain="Can describes general ability or possibility now."),
    ],
    "ability_past": [
        dict(q="Does it describe a general ability in the past?",
             options=["Yes, a past ability", "No, an ability now", "No, a future ability"],
             correct=0, explain="Could describes general ability in the past."),
    ],
    "future_continuous": [
        dict(q="Will the action be in progress at a future time?",
             options=["Yes, in progress at that future time", "No, finished before it", "No, happening now"],
             correct=0, explain="Future continuous describes an action in progress at a future moment."),
    ],
    "future_perfect": [
        dict(q="Will the action be completed before a future time?",
             options=["Yes, completed before that time", "No, still in progress at that time", "No, happening now"],
             correct=0, explain="Future perfect describes completion before a future point."),
    ],
    "future_in_past": [
        dict(q="Is the future seen from a point in the past?",
             options=["Yes, a future event seen from the past", "No, a future event seen from now", "No, a past habit"],
             correct=0, explain="Future in the past describes a future event from a past viewpoint."),
    ],
    "used_to": [
        dict(q="Does it describe a repeated past habit or state?",
             options=["Yes, a past habit or state", "No, a present habit", "No, a future plan"],
             correct=0, explain="Used to describes past habits and states that are no longer true."),
    ],
    "present_simple_vs_continuous": [
        dict(q="Which sentence describes a routine?",
             options=["I work every day", "I am working now", "I worked yesterday"],
             correct=0, explain="Present simple describes routines; present continuous describes actions now."),
        dict(q="Which sentence describes an action in progress now?",
             options=["I work every day", "I am working now", "I worked yesterday"],
             correct=1, explain="Present continuous describes an action in progress now."),
    ],
    "past_simple_vs_continuous": [
        dict(q="Which sentence sets the background scene?",
             options=["I was walking home", "I saw a friend", "I see a friend"],
             correct=0, explain="Past continuous sets the background; past simple reports the event."),
        dict(q="Which sentence reports a single finished event?",
             options=["I was walking home", "I saw a friend", "I see a friend"],
             correct=1, explain="Past simple reports a single finished event."),
    ],
    "present_perfect_vs_past_simple": [
        dict(q="Which sentence connects a past action to now?",
             options=["I have lost my keys", "I lost my keys yesterday", "I lose my keys every day"],
             correct=0, explain="Present perfect connects the past to now; past simple states a finished time."),
        dict(q="Which sentence gives a finished past time?",
             options=["I have lost my keys", "I lost my keys yesterday", "I lose my keys every day"],
             correct=1, explain="Past simple is used with a finished past time."),
    ],
    "will_vs_going_to": [
        dict(q="Which sentence is a plan made before now?",
             options=["I am going to visit Rome", "I will visit Rome", "I visited Rome"],
             correct=0, explain="Going to expresses a plan made before speaking."),
        dict(q="Which sentence is a decision made now?",
             options=["I am going to visit Rome", "I will visit Rome", "I visited Rome"],
             correct=1, explain="Will expresses a decision made at the moment of speaking."),
    ],
    "future_forms": [
        dict(q="Do these forms all point to the future?",
             options=["Yes, they express future time", "No, they are all past", "No, they are all present habits"],
             correct=0, explain="The future forms express future time in different ways."),
    ],
    "tense_system": [
        dict(q="Does the timeline show past, present and future?",
             options=["Yes, all three times", "No, only the past", "No, only the future"],
             correct=0, explain="The tense system maps actions across past, present and future."),
    ],
    "narrative": [
        dict(q="Does the narrative use more than one past tense?",
             options=["Yes, to order and describe past events", "No, only the present", "No, only the future"],
             correct=0, explain="Narrative tenses combine past forms to tell a story."),
    ],
}


PROFILES = {
    "present-simple": dict(
        aria="habits, routines and facts around now",
        items=[span(8, 92, "present", "every day · always"), now(50)],
        ccq="present_simple",
    ),
    "present-continuous": dict(
        aria="an action in progress now",
        items=[span(38, 62, "present", "now · at the moment"), now(50)],
        ccq="present_continuous",
    ),
    "present-simple-vs-continuous": dict(
        aria="a routine compared with an action in progress now",
        items=[point(22, "past", "I work every day"), span(45, 58, "present", "I am working now"), now(50)],
        ccq="present_simple_vs_continuous",
    ),
    "past-simple": dict(
        aria="a finished action before now",
        items=[point(32, "past", "finished · yesterday"), now(82)],
        ccq="past_simple",
    ),
    "past-simple-be": dict(
        aria="was and were describe a finished past state",
        items=[point(32, "past", "was / were"), now(82)],
        ccq="past_simple",
    ),
    "there-was-were": dict(
        aria="there was in the past, there is now, there will be in the future",
        items=[point(20, "past", "there was"), now(50), point(80, "future", "there will be")],
        ccq="past_simple",
    ),
    "going-to": dict(
        aria="a plan made before now and directed at the future",
        items=[now(22), point(72, "future", "plan before now → future")],
        ccq="going_to",
    ),
    "will": dict(
        aria="a decision made now and directed at the future",
        items=[now(22), point(72, "future", "decision now → future")],
        ccq="will",
    ),
    "will-vs-going-to": dict(
        aria="a plan made earlier compared with a decision made now",
        items=[now(20), point(62, "future", "going to · planned earlier"), point(82, "future", "will · decided now", below=False)],
        ccq="will_vs_going_to",
    ),
    "have-got": dict(
        aria="possession or a state that is true now",
        items=[span(18, 50, "present", "have got · true now"), now(50)],
        ccq="have_got",
    ),
    "ability-present": dict(
        aria="general ability now",
        items=[now(50), point(50, "present", "can · general ability")],
        ccq="ability_present",
    ),
    "ability-past": dict(
        aria="general ability in the past",
        items=[point(30, "past", "could · past ability"), now(82)],
        ccq="ability_past",
    ),
    "tense-system": dict(
        aria="the full tense system: past, present and future",
        items=[span(6, 36, "past", "past"), span(42, 58, "present", "present"), span(64, 94, "future", "future"), now(50)],
        ccq="tense_system",
    ),
    "past-continuous": dict(
        aria="an action in progress at a past moment",
        items=[span(18, 52, "past", "was doing · in progress"), point(62, "past", "then"), now(85)],
        ccq="past_continuous",
    ),
    "present-perfect": dict(
        aria="a past action connected to now",
        items=[span(16, 82, "present", "past → now"), now(82)],
        ccq="present_perfect",
    ),
    "present-perfect-just-already-yet": dict(
        aria="an action completed just before now, or not completed yet",
        items=[point(70, "present", "just / already"), now(82)],
        ccq="present_perfect",
    ),
    "present-perfect-vs-past-simple": dict(
        aria="a finished past action compared with a past action connected to now",
        items=[point(28, "past", "finished · yesterday"), span(58, 82, "present", "result now"), now(82)],
        ccq="present_perfect_vs_past_simple",
    ),
    "present-continuous-for-future": dict(
        aria="a future arrangement fixed around now",
        items=[now(25), span(58, 82, "future", "arrangement"), point(82, "future", "future", below=False)],
        ccq="present_continuous",
    ),
    "past-simple-vs-past-continuous": dict(
        aria="a background action interrupted by a single past event",
        items=[span(18, 55, "past", "was doing · background"), point(62, "past", "did · event"), now(85)],
        ccq="past_simple_vs_continuous",
    ),
    "verb-tenses-review": dict(
        aria="the full tense system: past, present and future",
        items=[span(6, 36, "past", "past"), span(42, 58, "present", "present"), span(64, 94, "future", "future"), now(50)],
        ccq="tense_system",
    ),
    "used-to": dict(
        aria="a repeated past habit or state that is no longer true",
        items=[span(15, 62, "past", "used to · past habit"), now(85)],
        ccq="used_to",
    ),
    "future-time-clauses": dict(
        aria="a future time clause and the future action that follows it",
        items=[now(20), point(55, "future", "when / as soon as"), point(82, "future", "future action")],
        ccq="future_forms",
    ),
    "past-perfect": dict(
        aria="an earlier past action before a later past action",
        items=[point(26, "past", "had left · earlier"), point(62, "past", "arrived · later"), now(88)],
        ccq="past_perfect",
    ),
    "future-continuous": dict(
        aria="an action in progress at a future time",
        items=[now(22), span(56, 84, "future", "in progress then")],
        ccq="future_continuous",
    ),
    "future-perfect": dict(
        aria="an action completed before a future time",
        items=[now(22), span(56, 82, "future", "completed by then"), point(86, "future", "future deadline", below=False)],
        ccq="future_perfect",
    ),
    "future-forms": dict(
        aria="the main ways to express future time",
        items=[now(20), point(48, "future", "present continuous · arrangement"), point(68, "future", "going to · plan", below=False), point(86, "future", "will · decision")],
        ccq="future_forms",
    ),
    "narrative-tenses": dict(
        aria="past tenses working together to tell a story",
        items=[span(10, 40, "past", "had done · earlier"), span(40, 66, "past", "was doing · background", below=False), point(66, "past", "did · event"), now(88)],
        ccq="narrative",
    ),
    "past-perfect-continuous": dict(
        aria="an action continuing up to a past moment",
        items=[span(14, 58, "past", "had been doing"), point(66, "past", "then"), now(88)],
        ccq="past_perfect_continuous",
    ),
    "present-perfect-simple-vs-continuous": dict(
        aria="a completed result compared with an activity continuing to now",
        items=[point(58, "present", "have done · result", below=False), span(28, 82, "present", "have been doing · duration"), now(82)],
        ccq="present_perfect_continuous",
    ),
    "passive-continuous-perfect": dict(
        aria="passive forms across continuous and perfect tenses",
        items=[span(16, 58, "present", "has been done"), span(58, 82, "future", "will have been done"), now(82)],
        ccq="tense_system",
    ),
    "present-past-simple-passive": dict(
        aria="passive forms in the present and past",
        items=[span(8, 48, "present", "present simple passive", below=True), point(34, "past", "past simple passive", below=False), now(82, "now")],
    ),
    "passive-simple-future": dict(
        aria="passive forms in simple and future tenses",
        items=[span(16, 45, "past", "was done"), span(45, 65, "present", "is done"), span(65, 90, "future", "will be done")],
        ccq="tense_system",
    ),
    "used-to-vs-would": dict(
        aria="past habits with used to and would",
        items=[span(12, 60, "past", "used to / would · past habit"), now(85)],
        ccq="used_to",
    ),
    "future-in-the-past": dict(
        aria="a future event seen from a point in the past",
        items=[point(40, "past", "said · past viewpoint"), point(78, "future", "would happen · future then")],
        ccq="future_in_past",
    ),
}


EN_SLUG_TO_PROFILE = {
    "present-simple": "present-simple",
    "present-continuous": "present-continuous",
    "simple-vs-continuous": "present-simple-vs-continuous",
    "present-simple-vs-present-continuous": "present-simple-vs-continuous",
    "past-simple-regular": "past-simple",
    "past-simple-irregular": "past-simple",
    "past-simple-be": "past-simple-be",
    "past-simple-review": "past-simple",
    "there-was-were": "there-was-were",
    "going-to": "going-to",
    "will": "will",
    "will-vs-going-to": "will-vs-going-to",
    "have-got": "have-got",
    "can-cant": "ability-present",
    "could-couldnt": "ability-past",
    "part-10-tense-system": "tense-system",
    "past-continuous": "past-continuous",
    "present-perfect-form-use": "present-perfect",
    "present-perfect-ever-never-for-since": "present-perfect",
    "present-perfect-just-already-yet": "present-perfect-just-already-yet",
    "present-perfect-vs-past-simple": "present-perfect-vs-past-simple",
    "past-simple-vs-present-perfect": "present-perfect-vs-past-simple",
    "present-continuous-for-future": "present-continuous-for-future",
    "past-simple-vs-past-continuous": "past-simple-vs-past-continuous",
    "review-of-verb-tenses": "verb-tenses-review",
    "used-to": "used-to",
    "future-time-clauses": "future-time-clauses",
    "past-perfect": "past-perfect",
    "future-continuous": "future-continuous",
    "future-perfect": "future-perfect",
    "future-forms-review": "future-forms",
    "narrative-tenses": "narrative-tenses",
    "past-perfect-continuous": "past-perfect-continuous",
    "present-perfect-simple-vs-continuous": "present-perfect-simple-vs-continuous",
    "present-and-past-simple-passive": "present-past-simple-passive",
    "passive-continuous-and-perfect-tenses": "passive-continuous-perfect",
    "passive-simple-and-future-tenses": "passive-simple-future",
    "wh-questions-in-the-past": "past-simple",
    "used-to-vs-would": "used-to-vs-would",
    "future-in-the-past": "future-in-the-past",
    "other-ways-to-express-future": "future-forms",
    "present-tenses-review": "verb-tenses-review",
    "past-tenses-review": "verb-tenses-review",
    "future-forms-expressing-future-time": "future-forms",
}
