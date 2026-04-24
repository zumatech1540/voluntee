from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import openpyxl

from django.contrib.auth import get_user_model
User = get_user_model()

from projects.models import Project


# ================= HOME =================
def home_page(request):
    projects = Project.objects.all().order_by('-id')[:6]

    return render(request, "home.html", {
        "projects": projects
    })


# ================= REGISTER =================
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

        # VALIDATION
        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {
                "error": "User already exists"
            })

        # CREATE USER
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        # SAVE EXTRA FIELDS
        user.phone = phone
        user.role = role if role else "volunteer"
        user.ward = ward
        user.polling_station = polling_station
        user.profession = profession
        user.other_profession = other_profession
        user.save()

        login(request, user)
        return redirect("home")

    return render(request, "register.html")


# ================= LOGIN =================
def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # ADMIN / LEADER ROUTING
            if user.is_staff or user.is_superuser or user.role == "leader":
                return redirect("dashboard")

            return redirect("home")

        return render(request, "login.html", {
            "error": "Invalid email or password"
        })

    return render(request, "login.html")


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= DASHBOARD =================
@login_required
def dashboard(request):

    projects = Project.objects.all()

    return render(request, "dashboard.html", {
        "projects": projects
    })


# ================= VOLUNTEERS =================
def volunteers_page(request):

    volunteers = User.objects.filter(role='volunteer')

    return render(request, "volunteers.html", {
        "volunteers": volunteers
    })


# ================= DOWNLOAD USERS (EXCEL) =================
@login_required
def download_users_excel(request):

    # only leader or admin
    if not (request.user.role == "leader" or request.user.is_staff):
        return redirect("dashboard")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"

    # HEADER
    ws.append([
        "First Name",
        "Last Name",
        "Email",
        "Phone",
        "Role",
        "Ward",
        "Polling Station",
        "Profession"
    ])

    # DATA
    users = User.objects.all()

    for user in users:

        ws.append([
            user.first_name,
            user.last_name,
            user.email,
            getattr(user, "phone", ""),
            getattr(user, "role", ""),
            str(getattr(user, "ward", "")),
            str(getattr(user, "polling_station", "")),
            getattr(user, "profession", "")
        ])

    # RESPONSE
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="users.xlsx"'

    wb.save(response)

    return response


# ================= CASCADING DROPDOWNS =================
def load_constituencies(request):

    county = request.GET.get('county')

    data = {
        "Laikipia": [
            "Laikipia East",
            "Laikipia North",
            "Laikipia West"
        ]
    }

    return JsonResponse({
        "constituencies": data.get(county, [])
    })


def load_polling(request):

    constituency = request.GET.get('constituency')

    data = {
        "Laikipia East": ["Nanyuki", "Ngobit", "Tigithi", "Thingithu"],
        "Laikipia North": ["Doldol", "Segera", "Ol Moran", "Rumuruti"],
        "Laikipia West": ["Rumuruti", "Githiga", "Salama", "Kinamba"]
    }

    return JsonResponse({
        "polling": data.get(constituency, [])
    })