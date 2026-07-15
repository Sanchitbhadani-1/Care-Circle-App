from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import User
from django.contrib.auth import authenticate, login, logout

#Load home page
def home(request):
    return render(request, "accounts/home.html")

#Logic behind signing upo
def signup(request): 

    #Sends data pack to server if user is trying to signup
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        # Checks that email is not already taken
        if User.objects.filter(email=email).exists():
            return render(request, "accounts/signup.html",
                          {"error": "That email is already registered."})

        # Create the account 
        user = User.objects.create_user(email=email, password=password)

        # Log the new user in right away
        login(request, user)

        # Send them straight to create their first circle
        return redirect("/circles/new/")

    # If its not a post but instead just a visit, show the empty form.
    return render(request, "accounts/signup.html")


def login_view(request):
    
    #Takes user login info and sends to server
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        #Checks if user's login info matches with info in database
        user = authenticate(request, username=email, password=password)

        #Decide what to do if it finds a match or not
        if user is not None:
            login(request, user)
            return redirect("/dashboard/")
        else:
            return render(request, "accounts/login.html",
                          {"error": "Wrong email or password."})

    #Loads up the page
    return render(request, "accounts/login.html")

#If user logs out, redirect them to home page
def logout_view(request):
    logout(request)
    return redirect("/")