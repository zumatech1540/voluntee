from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import User
from projects.models import Project

# try import location models safely
try:
    from .models import County, Constituency, Ward, PollingStation
except:
    County = None
    Constituency = None
    Ward = None
    PollingStation = None


# HOME PAGE
def home_page(request):
    projects = Project.objects.all().order_by('-id')[:6]
    return render(request, "home.html", {"projects": projects})


# REGISTER
def register_view(request):

    counties = County.objects.all() if County else []

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")

        county_id = request.POST.get("county")
        constituency_id = request.POST.get("constituency")
        ward_id = request.POST.get("ward")
        polling_id = request.POST.get("polling_station")

        profession = request.POST.get("profession")
        other_profession = request.POST.get("other_profession")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # password check
        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match",
                "counties": counties
            })

        # already exists
        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {
                "error": "You already registered. Please login.",
                "counties": counties
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role,
            profession=profession,
            other_profession=other_profession
        )

        login(request, user)
        return redirect('home')

    return render(request, "register.html", {"counties": counties})


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


# VOLUNTEERS
def volunteers_page(request):

    volunteers = User.objects.filter(role='volunteer')

    return render(request, "volunteers.html", {
        "volunteers": volunteers
    })


# AJAX LOADERS (safe)

def load_constituencies(request):
    if not Constituency:
        return JsonResponse([], safe=False)

    county_id = request.GET.get('county')
    data = Constituency.objects.filter(
        county_id=county_id
    ).values('id', 'name')

    return JsonResponse(list(data), safe=False)


def load_wards(request):
    if not Ward:
        return JsonResponse([], safe=False)

    constituency_id = request.GET.get('constituency')
    data = Ward.objects.filter(
        constituency_id=constituency_id
    ).values('id', 'name')

    return JsonResponse(list(data), safe=False)


def load_polling(request):
    if not PollingStation:
        return JsonResponse([], safe=False)

    ward_id = request.GET.get('ward')
    data = PollingStation.objects.filter(
        ward_id=ward_id
    ).values('id', 'name')

    return JsonResponse(list(data), safe=False)