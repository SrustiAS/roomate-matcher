from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .compatibility import calculate_compatibility
from .forms import PreferenceForm
from .models import Preference, RoommateRequest

User = get_user_model()


# --- Questionnaire --------------------------------------------------------
@login_required
def questionnaire(request):
    instance = getattr(request.user, "preferences", None)
    if request.method == "POST":
        form = PreferenceForm(request.POST, instance=instance)
        if form.is_valid():
            pref = form.save(commit=False)
            pref.user = request.user
            pref.save()
            messages.success(request, "Preferences saved! Here are your matches.")
            return redirect("find_roommate")
    else:
        form = PreferenceForm(instance=instance)
    return render(request, "matching/questionnaire.html", {"form": form})


# --- Helpers --------------------------------------------------------------
def _candidate_prefs(me):
    """Every other eligible user who has completed the questionnaire."""
    return (
        Preference.objects.select_related("user")
        .exclude(user=me)
        .exclude(user__is_blocked=True)
        .exclude(user__is_active=False)
    )


def _relationship(me, other):
    """Return the request status between me and other, if any."""
    req = RoommateRequest.objects.filter(
        Q(sender=me, receiver=other) | Q(sender=other, receiver=me)
    ).first()
    if not req:
        return None, None
    direction = "outgoing" if req.sender_id == me.id else "incoming"
    return req, direction


# --- Find roommate + filters ---------------------------------------------
@login_required
def find_roommate(request):
    me = request.user
    if not hasattr(me, "preferences"):
        messages.info(request, "Complete the questionnaire first.")
        return redirect("questionnaire")

    my_pref = me.preferences
    results = []
    for other_pref in _candidate_prefs(me):
        data = calculate_compatibility(my_pref, other_pref)
        req, direction = _relationship(me, other_pref.user)
        results.append({
            "user": other_pref.user,
            "pref": other_pref,
            "score": data["compatibility_score"],
            "reasons": data["matching_reasons"][:4],
            "request": req,
            "direction": direction,
        })

    # --- Filters (GET params) ---
    g = request.GET
    def keep(r):
        u, p = r["user"], r["pref"]
        if g.get("min_score") and r["score"] < int(g["min_score"]):
            return False
        if g.get("floor") not in (None, "", "any") and str(u.preferred_floor) != g["floor"]:
            return False
        if g.get("year") and str(u.year) != g["year"]:
            return False
        if g.get("branch") and g["branch"].lower() not in (u.branch or "").lower():
            return False
        if g.get("sleep_type") and p.sleep_type != g["sleep_type"]:
            return False
        if g.get("noise") and p.noise_preference != g["noise"]:
            return False
        if g.get("cleanliness") and p.cleanliness != g["cleanliness"]:
            return False
        if g.get("min_age") and (not u.age or u.age < int(g["min_age"])):
            return False
        if g.get("max_age") and (not u.age or u.age > int(g["max_age"])):
            return False
        return True

    results = [r for r in results if keep(r)]
    results.sort(key=lambda r: r["score"], reverse=True)

    return render(request, "matching/find.html", {
        "results": results,
        "filters": g,
        "floor_choices": User.FLOOR_CHOICES,
        "year_choices": User.YEAR_CHOICES,
    })


# --- Match detail (the "why") --------------------------------------------
@login_required
def match_detail(request, user_id):
    me = request.user
    other = get_object_or_404(User, pk=user_id)
    if other == me or not hasattr(me, "preferences") or not hasattr(other, "preferences"):
        raise Http404("Match not available.")

    data = calculate_compatibility(me.preferences, other.preferences)
    req, direction = _relationship(me, other)

    # Contact is revealed only after a mutual (accepted) match.
    contact_unlocked = bool(req and req.status == "accepted")

    label_map = {
        "sleep": "Sleep Schedule", "light": "Light Preference", "study": "Study Behaviour",
        "noise": "Noise Preference", "cleanliness": "Cleanliness", "floor": "Floor Preference",
        "age": "Age Compatibility", "year": "Year / Academic", "social": "Social Behaviour",
        "visitor": "Visitor Preference",
    }
    breakdown = [
        {"label": label_map[k], "score": v}
        for k, v in data["category_scores"].items()
    ]

    return render(request, "matching/match_detail.html", {
        "other": other,
        "pref": other.preferences,
        "data": data,
        "breakdown": breakdown,
        "request_obj": req,
        "direction": direction,
        "contact_unlocked": contact_unlocked,
    })


# --- Request system -------------------------------------------------------
@login_required
def send_request(request, user_id):
    me = request.user
    other = get_object_or_404(User, pk=user_id)
    if other == me:
        messages.error(request, "You can't send a request to yourself.")
        return redirect("find_roommate")

    existing, _ = _relationship(me, other)
    if existing and existing.status in ("pending", "accepted"):
        messages.info(request, "There's already an active request with this student.")
    else:
        RoommateRequest.objects.update_or_create(
            sender=me, receiver=other,
            defaults={"status": "pending"},
        )
        messages.success(request, f"Request sent to {other.full_name or other.username}.")
    return redirect("match_detail", user_id=other.id)


@login_required
def respond_request(request, request_id, action):
    me = request.user
    req = get_object_or_404(RoommateRequest, pk=request_id)
    if req.receiver_id != me.id:
        raise Http404()
    if action == "accept":
        req.status = "accepted"
        messages.success(request, "Request accepted! Contact options are now unlocked.")
    elif action == "reject":
        req.status = "rejected"
        messages.info(request, "Request rejected.")
    else:
        raise Http404()
    req.save()
    return redirect("requests")


@login_required
def cancel_request(request, request_id):
    me = request.user
    req = get_object_or_404(RoommateRequest, pk=request_id, sender=me)
    req.status = "cancelled"
    req.save()
    messages.info(request, "Request cancelled.")
    return redirect("requests")


@login_required
def requests_view(request):
    me = request.user
    received = RoommateRequest.objects.filter(receiver=me, status="pending").select_related("sender")
    sent = RoommateRequest.objects.filter(sender=me).select_related("receiver")
    accepted = RoommateRequest.objects.filter(
        Q(sender=me) | Q(receiver=me), status="accepted"
    ).select_related("sender", "receiver")
    return render(request, "matching/requests.html", {
        "received": received, "sent": sent, "accepted": accepted,
    })


# --- Dashboard ------------------------------------------------------------
@login_required
def dashboard(request):
    me = request.user
    top_matches = []
    if hasattr(me, "preferences"):
        my_pref = me.preferences
        scored = []
        for other_pref in _candidate_prefs(me):
            data = calculate_compatibility(my_pref, other_pref)
            scored.append({
                "user": other_pref.user, "pref": other_pref,
                "score": data["compatibility_score"],
                "reasons": data["matching_reasons"][:3],
            })
        scored.sort(key=lambda r: r["score"], reverse=True)
        top_matches = scored[:6]

    pending_count = RoommateRequest.objects.filter(receiver=me, status="pending").count()
    return render(request, "matching/dashboard.html", {
        "top_matches": top_matches,
        "pending_count": pending_count,
        "has_prefs": hasattr(me, "preferences"),
    })
