from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CareCircle, Membership


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
    # Find a circle this user belongs to (just their first one, for now).
    membership = Membership.objects.filter(user=request.user).first()

    # Not in any circle yet? Send them to create one.
    if membership is None:
        return redirect("/circles/new/")

    circle = membership.circle
    context = {
        "circle": circle,
        "my_role": membership.role,
    }
    return render(request, "circles/dashboard.html", context)
