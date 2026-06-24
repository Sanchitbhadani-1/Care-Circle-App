from django.shortcuts import render


def home(request):
    return render(request, "accounts/home.html")


def signup(request):
    return render(request, "accounts/signup.html")