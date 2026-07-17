from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import CareCircle, Membership, SeniorProfile, LogEntry, CareNote, Medication, DoseLog
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth import get_user_model
User = get_user_model()

METRICS = {
    "sleep":     {"label": "Sleep",     "unit": "hours", "icon": "😴"},
    "hydration": {"label": "Hydration", "unit": "cups",  "icon": "💧"},
    "weight":    {"label": "Weight",    "unit": "lbs",   "icon": "🩺"},
}

@login_required #Requires that the user is logged in
def create_circle(request):
    if request.method == "POST": #Sends data to the server
        name = request.POST["name"]

        # Create the circle, owned by whoever is logged in
        circle = CareCircle.objects.create(name=name, owner=request.user)

        # Make the creator the first member, with the Owner role
        Membership.objects.create(user=request.user, circle=circle, role="owner")

        return redirect("/dashboard/")

    return render(request, "circles/create_circle.html")

@login_required
def dashboard(request):
    # Find a circle this user belongs to (just their first one).
    membership = Membership.objects.filter(user=request.user).first()

    # Not in any circle yet? Send them to create one.
    if membership is None:
        return redirect("/circles/new/")

    circle = membership.circle

    # Which trackers to pin on the dashboard (stays fixed even as METRICS grows)
    DASHBOARD_METRICS = ["sleep", "hydration", "weight"]

    # Latest reading for each of those → the snapshot tiles
    snapshot = []
    for key in DASHBOARD_METRICS:
        cfg = METRICS[key]
        latest = LogEntry.objects.filter(circle=circle, metric=key).first()
        snapshot.append({
            "key": key,
            "icon": cfg["icon"],
            "label": cfg["label"],
            "unit": cfg["unit"],
            "value": latest.value if latest else None,
            "has_value": latest is not None,
        })

    # Newest few entries across all trackers → recent activity
    recent = []
    for e in LogEntry.objects.filter(circle=circle)[:6]:
        cfg = METRICS.get(e.metric, {})
        recent.append({
            "icon": cfg.get("icon", "•"),
            "label": cfg.get("label", e.metric),
            "value": e.value,
            "unit": cfg.get("unit", ""),
            "by": e.logged_by.email if e.logged_by else "Someone",
            "at": e.logged_at,
        })

    context = {
        "circle": circle,
        "my_role": membership.role,
        "senior": SeniorProfile.objects.filter(circle=circle).first(),
        "members": circle.memberships.all(),
        "snapshot": snapshot,
        "recent": recent,
    }
    return render(request, "circles/dashboard.html", context)                             
    


@login_required
def tracker(request, metric):
    # Is this a real tracker? Look it up in our config.
    config = METRICS.get(metric)
    if config is None:
        raise Http404("Unknown tracker")

    # Same "find the user's circle" as the dashboard.
    membership = Membership.objects.filter(user=request.user).first()
    if membership is None:
        return redirect("/circles/new/")
    circle = membership.circle

    # If they submitted the form, save a new entry.
    if request.method == "POST":

        # Delete an entry?
        if request.POST.get("action") == "delete":
            LogEntry.objects.filter(
                id=request.POST.get("entry_id"),
                circle=circle,          # scope to this circle...
                metric=metric,          # ...and this metric, for safety
            ).delete()
            return redirect(f"/track/{metric}/")
        

        # Use the date/time the user picked; fall back to now if it's blank.
        when = parse_datetime(request.POST.get("logged_at", ""))
        if when is None:
            when = timezone.now()
        elif timezone.is_naive(when):
            when = timezone.make_aware(when)

        LogEntry.objects.create(
            circle=circle,
            metric=metric,
            value=float(request.POST["value"]),
            note=request.POST.get("note", ""),
            logged_by=request.user,
            logged_at=when,          
        )
        return redirect(f"/track/{metric}/")

    # Otherwise, show the form + history for this metric.
    entries = LogEntry.objects.filter(circle=circle, metric=metric)
    chart_entries = entries.order_by("logged_at")
    labels = [e.logged_at.strftime("%b %d") for e in chart_entries]
    values = [e.value for e in chart_entries]
    context = {
        "circle": circle,
        "metric": metric,
        "config": config,
        "entries": entries,
        "labels": labels,
        "values": values,
    }
    return render(request, "circles/tracker.html", context)

@login_required
def edit_senior(request):
    membership = Membership.objects.filter(user=request.user).first()
    if membership is None:
        return redirect("/circles/new/")
    circle = membership.circle

    # The circle's senior, or None if not created yet.
    senior = SeniorProfile.objects.filter(circle=circle).first()

    if request.method == "POST":
        name = request.POST["name"]
        dob = request.POST.get("date_of_birth") or None
        relationship = request.POST.get("relationship", "")
        allergies = request.POST.get("allergies", "")
        about = request.POST.get("about", "")

        if senior is None:
            # First time → create the profile.
            SeniorProfile.objects.create(
                circle=circle, name=name, date_of_birth=dob,
                relationship=relationship, allergies=allergies, about=about,
            )
        else:
            # Already exists - update the fields and save.
            senior.name = name
            senior.date_of_birth = dob
            senior.relationship = relationship
            senior.allergies = allergies
            senior.about = about
            senior.save()

        return redirect("/dashboard/")

    return render(request, "circles/edit_senior.html", {
        "circle": circle,
        "senior": senior,
    })

@login_required
def members(request):
    membership = Membership.objects.filter(user=request.user).first()
    if membership is None:
        return redirect("/circles/new/")
    circle = membership.circle
    is_owner = (membership.role == "owner")     # the permission flag

    error = ""

    # Only the owner may add or remove people.
    if request.method == "POST" and is_owner:
        action = request.POST.get("action")

        if action == "add":
            email = request.POST.get("email", "").strip().lower()
            person = User.objects.filter(email=email).first()

            if person is None:
                error = "No account found with that email — ask them to sign up first."
            elif Membership.objects.filter(user=person, circle=circle).exists():
                error = "That person is already in this circle."
            else:
                # Join as family by default; the owner can mark them a caregiver.
                role = request.POST.get("role", "family")
                if role not in ("caregiver", "family"):
                    role = "family"          # ignore anything sketchy (e.g. "owner")
                Membership.objects.create(user=person, circle=circle, role=role)
                return redirect("/members/")

        elif action == "remove":
            Membership.objects.filter(
                id=request.POST.get("membership_id"),
                circle=circle,
            ).exclude(role="owner").delete()      # never remove the owner
            return redirect("/members/")

    context = {
        "circle": circle,
        "members": circle.memberships.all(),
        "is_owner": is_owner,
        "error": error,
    }
    return render(request, "circles/members.html", context)


@login_required
def care_notes(request):
    membership = Membership.objects.filter(user=request.user).first()
    if membership is None:
        return redirect("/circles/new/")
    circle = membership.circle

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:                     # ignore empty submissions
            CareNote.objects.create(circle=circle, body=body, author=request.user)
        return redirect("/notes/")

    notes = circle.notes.all()  # reverse accessor from related_name="notes"
    return render(request, "circles/care_notes.html", {"circle": circle, "notes": notes})


@login_required
def medications(request):
    membership = Membership.objects.filter(user=request.user).first()
    if membership is None:
        return redirect("/circles/new/")
    circle = membership.circle

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            name = request.POST.get("name", "").strip()
            if name:                                  # ignore blank names
                Medication.objects.create(
                    circle=circle,
                    name=name,
                    dosage=request.POST.get("dosage", ""),
                    instructions=request.POST.get("instructions", ""),
                )

        elif action == "dose":
            med = Medication.objects.filter(
                id=request.POST.get("medication_id"),
                circle=circle,                        # scope to this circle for safety
            ).first()
            if med:
                amount = request.POST.get("amount_given", "").strip() or med.dosage

                when = parse_datetime(request.POST.get("given_at", ""))
                if when is None:
                    when = timezone.now()
                elif timezone.is_naive(when):
                    when = timezone.make_aware(when)

                DoseLog.objects.create(medication=med, given_by=request.user, amount_given=amount, given_at=when)

        elif action == "delete_dose":
            DoseLog.objects.filter(
                id=request.POST.get("dose_id"),
                medication__circle=circle,   # dose → its medication → the circle
            ).delete()
            return redirect("/medications/")
        return redirect("/medications/")

    meds = circle.medications.filter(is_active=True)  # only active meds
    return render(request, "circles/medications.html", {
        "circle": circle,
        "medications": meds,
    })