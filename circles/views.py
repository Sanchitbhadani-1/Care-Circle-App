from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import CareCircle, Membership, SeniorProfile, LogEntry
from django.utils import timezone
from django.utils.dateparse import parse_datetime

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
    context = {
        "circle": circle,
        "my_role": membership.role,
        "senior": SeniorProfile.objects.filter(circle=circle).first(),   
        "members": circle.memberships.all()                             
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