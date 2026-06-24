from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User


def home(request):
    return render(request, "accounts/home.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Server-side check: is this email already taken?
        if User.objects.filter(email=email).exists():
            return render(request, "accounts/signup.html",
                          {"error": "That email is already registered."})

        # Create the account — the password gets scrambled automatically
        user = User.objects.create_user(email=email, password=password)

        # Log the new user in right away
        login(request, user)

        # Send them to the home page
        return redirect("/")

    # Not a POST? Then it's just a visit (GET) — show the empty form.
    return render(request, "accounts/signup.html")