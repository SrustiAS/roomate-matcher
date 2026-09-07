"""
Roommate compatibility engine.

Pure, dependency-free scoring so it is easy to unit-test and easy to extend.
Every category returns a 0-100 sub-score; the final score is the
weighted average. The output is fully explainable: no black-box number.

Public API:
    calculate_compatibility(pref_a, pref_b) -> dict
        {
            "compatibility_score": int,        # 0-100
            "category_scores": {name: int},    # 0-100 per category
            "matching_reasons": [str],         # human-readable "why you match"
            "potential_conflicts": [str],      # human-readable "possible differences"
        }

`pref_a` / `pref_b` are matching.models.Preference instances (each has `.user`).
To add a new factor later: add a scorer, register it in WEIGHTS, done.
"""
from datetime import datetime, timedelta

# --- Weights (must sum to 100) -------------------------------------------
WEIGHTS = {
    "sleep": 20,
    "light": 15,
    "study": 15,
    "noise": 10,
    "cleanliness": 10,
    "floor": 10,
    "age": 5,
    "year": 5,
    "social": 5,
    "visitor": 5,
}
assert sum(WEIGHTS.values()) == 100, "Weights must sum to 100"


# --- Helpers --------------------------------------------------------------
def _minutes(t):
    return t.hour * 60 + t.minute


def _circular_diff(a_min, b_min):
    """Smallest difference between two clock times, in minutes (0-720)."""
    d = abs(a_min - b_min) % (24 * 60)
    return min(d, 24 * 60 - d)


def _ordinal_score(a, b, scale, step):
    """Score two ordinal choices: identical = 100, each step apart drops `step`."""
    try:
        diff = abs(scale.index(a) - scale.index(b))
    except ValueError:
        return 50
    return max(0, 100 - diff * step)


# --- Category scorers -----------------------------------------------------
def score_sleep(a, b):
    # 60% chronotype match + 40% clock proximity of sleep/wake times.
    type_score = 100 if a.sleep_type == b.sleep_type else 30

    sleep_gap = _circular_diff(_minutes(a.sleep_time), _minutes(b.sleep_time))
    wake_gap = _circular_diff(_minutes(a.wake_time), _minutes(b.wake_time))
    avg_gap = (sleep_gap + wake_gap) / 2
    # 0 min apart -> 100, 120+ min apart -> 0
    time_score = max(0, 100 - (avg_gap / 120) * 100)

    return round(type_score * 0.6 + time_score * 0.4)


def score_light(a, b):
    scale = ["off", "dim", "dont_mind", "on_study"]
    return _ordinal_score(a.light_preference, b.light_preference, scale, 30)


def score_study(a, b):
    if a.study_habit == b.study_habit:
        return 100
    time_based = {"late_night", "early_morning"}
    place_based = {"room", "library", "occasional"}
    a_h, b_h = a.study_habit, b.study_habit
    # Opposite study clocks are the biggest clash.
    if {a_h, b_h} == {"late_night", "early_morning"}:
        return 25
    if a_h in time_based and b_h in time_based:
        return 70
    if a_h in place_based and b_h in place_based:
        return 65
    return 50


def score_noise(a, b):
    scale = ["quiet", "moderate", "dont_mind"]
    return _ordinal_score(a.noise_preference, b.noise_preference, scale, 50)


def score_cleanliness(a, b):
    scale = ["very", "moderate", "relaxed"]
    return _ordinal_score(a.cleanliness, b.cleanliness, scale, 40)


def score_floor(a, b):
    fa, fb = a.user.preferred_floor, b.user.preferred_floor
    if fa is None or fb is None:
        return 50
    ANY = -1
    if fa == ANY or fb == ANY:
        return 80
    if fa == fb:
        return 100
    if abs(fa - fb) == 1:
        return 55
    return 20


def score_age(a, b):
    aa, ab = a.user.age, b.user.age
    if not aa or not ab:
        return 60
    d = abs(aa - ab)
    return {0: 100, 1: 100, 2: 80, 3: 55}.get(d, 30)


def score_year(a, b):
    ya, yb = a.user.year, b.user.year
    if not ya or not yb:
        return 60
    d = abs(ya - yb)
    return {0: 100, 1: 75, 2: 50}.get(d, 35)


def score_social(a, b):
    scale = ["very", "moderate", "private"]
    return _ordinal_score(a.social_level, b.social_level, scale, 40)


def score_visitor(a, b):
    scale = ["none", "occasional", "okay"]
    return _ordinal_score(a.visitor_preference, b.visitor_preference, scale, 40)


SCORERS = {
    "sleep": score_sleep,
    "light": score_light,
    "study": score_study,
    "noise": score_noise,
    "cleanliness": score_cleanliness,
    "floor": score_floor,
    "age": score_age,
    "year": score_year,
    "social": score_social,
    "visitor": score_visitor,
}


# --- Reason / conflict text ----------------------------------------------
def _reasons_and_conflicts(a, b, cat_scores):
    reasons, conflicts = [], []

    def label(pref, field):
        return dict(pref._meta.get_field(field).choices).get(getattr(pref, field), "")

    # Sleep
    if a.sleep_type == b.sleep_type:
        reasons.append(f"Both are {a.get_sleep_type_display()}")
    else:
        conflicts.append("Different sleep chronotypes (Night Owl vs Early Bird)")
    if cat_scores["sleep"] >= 80:
        reasons.append("Similar sleeping / waking times")

    # Light
    if a.light_preference == b.light_preference:
        reasons.append(f"Both: {a.get_light_preference_display().lower()}")
    elif cat_scores["light"] < 50:
        conflicts.append(
            f"Light clash: one wants '{a.get_light_preference_display()}', "
            f"other '{b.get_light_preference_display()}'"
        )

    # Study
    if a.study_habit == b.study_habit:
        reasons.append(f"Same study habit: {a.get_study_habit_display().lower()}")
    elif cat_scores["study"] < 50:
        conflicts.append("Study routines differ significantly")

    # Noise
    if cat_scores["noise"] >= 90:
        reasons.append("Same noise tolerance")
    elif cat_scores["noise"] < 50:
        conflicts.append("Different noise tolerance")

    # Cleanliness
    if cat_scores["cleanliness"] >= 90:
        reasons.append("Similar cleanliness standards")
    elif cat_scores["cleanliness"] < 50:
        conflicts.append("Different cleanliness habits")

    # Floor
    if cat_scores["floor"] == 100:
        reasons.append(f"Same preferred floor ({a.user.get_preferred_floor_display()})")
    elif cat_scores["floor"] <= 20:
        conflicts.append("Prefer different floors")

    # Social
    if cat_scores["social"] < 50:
        conflicts.append("Different social energy")

    # Visitor
    if a.visitor_preference == b.visitor_preference:
        reasons.append("Agree on visitors")
    elif cat_scores["visitor"] < 60:
        conflicts.append(
            f"Visitor preference differs: '{a.get_visitor_preference_display()}' "
            f"vs '{b.get_visitor_preference_display()}'"
        )

    return reasons, conflicts


# --- Public API -----------------------------------------------------------
def calculate_compatibility(pref_a, pref_b):
    if pref_a.user_id == pref_b.user_id:
        raise ValueError("Cannot match a user with themselves.")

    category_scores = {}
    weighted_total = 0
    for name, weight in WEIGHTS.items():
        s = int(round(SCORERS[name](pref_a, pref_b)))
        s = max(0, min(100, s))
        category_scores[name] = s
        weighted_total += s * weight

    overall = int(round(weighted_total / 100))
    reasons, conflicts = _reasons_and_conflicts(pref_a, pref_b, category_scores)

    return {
        "compatibility_score": overall,
        "category_scores": category_scores,
        "matching_reasons": reasons,
        "potential_conflicts": conflicts,
    }
