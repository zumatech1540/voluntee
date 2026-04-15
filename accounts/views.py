from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import User
from projects.models import Project


# HOME PAGE
def home_page(request):
    projects = Project.objects.all().order_by('-id')[:6]
    return render(request, "home.html", {"projects": projects})


# REGISTER
def register_view(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        role = request.POST.get("role")
        ward = request.POST.get("ward")
        polling_station = request.POST.get("polling_station")

        profession = request.POST.get("profession")
        other_profession = request.POST.get("other_profession")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # PASSWORD CHECK
        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        # USER EXISTS CHECK
        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {
                "error": "You already registered. Please login."
            })

        # CREATE USER
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            ward=ward,
            polling_station=polling_station,
            profession=profession,
            other_profession=other_profession
        )

        login(request, user)
        return redirect('home')

    return render(request, "register.html")


# LOGIN
def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {
            "error": "Wrong email or password"
        })

    return render(request, "login.html")


# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("login")


# DASHBOARD
@login_required
def dashboard(request):

    projects = Project.objects.all()

    return render(request, "dashboard.html", {
        "projects": projects
    })


# VOLUNTEERS PAGE
def volunteers_page(request):

    volunteers = User.objects.filter(role='volunteer')

    return render(request, "volunteers.html", {
        "volunteers": volunteers
    })