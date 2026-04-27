from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import PollingStation, Ward
import openpyxl
import urllib.parse

from .models import (
    County, Constituency, Ward,
    PollingStation, Event
)

from projects.models import Project


# ================= HOME =================
def home_page(request):
    projects = Project.objects.all().order_by('-id')[:6]

    return render(request, "home.html", {
        "projects": projects
    })


def about_page(request):
    return render(request, "about.html")


def volunteers_page(request):
    volunteers = User.objects.filter(role="volunteer")

    return render(request, "volunteers.html", {
        "volunteers": volunteers
    })


def gallery_page(request):
    return render(request, "gallery.html")


def blogs_page(request):
    return render(request, "blogs.html")


def contact_page(request):
    return render(request, "contact.html")


# ================= REGISTER =================
def register_view(request):

    county = County.objects.filter(name__icontains="Laikipia").first()
    constituencies = Constituency.objects.filter(county=county)

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")

        constituency_id = request.POST.get("constituency")
        ward_id = request.POST.get("ward")
        polling_station_id = request.POST.get("polling_station")

        profession = request.POST.get("profession")
        other_profession = request.POST.get("other_profession")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match",
                "constituencies": constituencies
            })

        if User.objects.filter(username=email).exists():
            return render(request, "register.html", {
                "error": "User already exists",
                "constituencies": constituencies
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        user.phone = phone
        user.role = role
        user.county = county
        user.constituency_id = constituency_id or None
        user.ward_id = ward_id or None
        user.polling_station_id = polling_station_id or None
        user.profession = profession
        user.other_profession = other_profession

        user.save()

        login(request, user)

        if user.role == "leader":
            return redirect("dashboard")

        return redirect("home")

    return render(request, "register.html", {
        "constituencies": constituencies
    })


# ================= LOGIN =================
def login_view(request):

    if request.method == "POST":

        email_or_username = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email_or_username, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")

            if user.role == "leader":
                return redirect("dashboard")

            return redirect("home")

        return render(request, "login.html", {
            "error": "Wrong email/username or password"
        })

    return render(request, "login.html")


# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= HELPERS =================
def is_leader(user):
    return user.is_authenticated and user.role == "leader"


def is_admin(user):
    return user.is_authenticated and user.is_superuser


# ================= DASHBOARD =================
@login_required
def dashboard(request):

    if request.user.role != "leader" and not request.user.is_superuser:
        return redirect("home")

    projects = Project.objects.all().order_by('-id')
    events = Event.objects.all().order_by('-created_at')
    members = User.objects.all().order_by('-id')

    notifications = [
        "Welcome to the dashboard",
        "System running successfully",
        "You can create events below"
    ]

    return render(request, "dashboard.html", {
        "projects": projects,
        "events": events,
        "members": members,
        "notifications": notifications
    })


# ================= ADMIN DASHBOARD =================
@login_required
def dashboard(request):

    # ONLY leaders
    if request.user.role != "leader" and not request.user.is_superuser:
        return redirect("home")

    # 🔥 FIX: leaders only see THEIR OWN created events
    if request.user.is_superuser:
        events = Event.objects.all().order_by('-id')
    else:
        events = Event.objects.filter(created_by=request.user).order_by('-id')

    members = User.objects.all().order_by('-id') if request.user.is_superuser else User.objects.filter(id=request.user.id)

    notifications = [
        "Welcome to your dashboard",
        "Manage your events efficiently",
        "System running smoothly"
    ]

    return render(request, "dashboard.html", {
        "events": events,
        "members": members,
        "notifications": notifications
    })

# ================= admin_dashboard =================
@login_required
def admin_dashboard(request):

    # ONLY SUPERUSER CAN ACCESS
    if not request.user.is_superuser:
        return redirect("home")

    events = Event.objects.all().order_by('-id')
    members = User.objects.all().order_by('-id')

    stats = {
        "total_events": events.count(),
        "total_members": members.count(),
        "pending_events": events.filter(approval_status="pending").count(),
        "approved_events": events.filter(approval_status="approved").count(),
    }

    return render(request, "admin_dashboard.html", {
        "events": events,
        "members": members,
        "stats": stats
    })

# ================= EVENTS =================
def events_page(request):

    if request.user.is_superuser:
        events = Event.objects.all()

    elif request.user.is_authenticated and request.user.role == "leader":
        events = Event.objects.filter(created_by=request.user)

    else:
        events = Event.objects.filter(approval_status="approved")

    return render(request, "events.html", {"events": events})


# ================= CREATE EVENT =================


@login_required
def create_event(request):

    if request.user.role != "leader":
        return redirect("events")

    if request.method == "POST":

        date = request.POST.get("date")

        # 🔥 VALIDATION FIX
        if not date:
            return render(request, "create_event.html", {
                "error": "Please select a valid date"
            })

        Event.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            date=date,
            image=request.FILES.get("image"),
            created_by=request.user,
            approval_status="pending"
        )

        return redirect("events")

    return render(request, "create_event.html")


# ================= EVENT DETAILS =================
@login_required
def event_detail(request, id):

    event = get_object_or_404(Event, id=id)
    joined = request.user in event.attendees.all()

    return render(request, "event_detail.html", {
        "event": event,
        "joined": joined
    })


@login_required
def join_event(request, id):

    event = get_object_or_404(Event, id=id)

    if request.user not in event.attendees.all():
        event.attendees.add(request.user)

    return redirect("event_detail", id=id)


@login_required
def leave_event(request, id):

    event = get_object_or_404(Event, id=id)

    if request.user in event.attendees.all():
        event.attendees.remove(request.user)

    return redirect("event_detail", id=id)


# ================= EDIT EVENT =================
@login_required
def edit_event(request, id):

    event = get_object_or_404(Event, id=id)

    if request.user != event.created_by and not request.user.is_superuser:
        return redirect("events")

    if request.method == "POST":

        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        event.location = request.POST.get("location")
        event.date = request.POST.get("date")

        if request.FILES.get("image"):
            event.image = request.FILES.get("image")

        event.approval_status = "pending"
        event.save()

        return redirect("events")

    return render(request, "edit_event.html", {"event": event})


# ================= APPROVE EVENT =================
@login_required
def approve_event(request, id):

    if not request.user.is_superuser:
        return redirect("events")

    event = get_object_or_404(Event, id=id)
    event.approval_status = "approved"
    event.save()

    return redirect("events")


# ================= REJECT EVENT =================
@login_required
def reject_event(request, id):

    if not request.user.is_superuser:
        return redirect("events")

    event = get_object_or_404(Event, id=id)
    event.approval_status = "rejected"
    event.save()

    return redirect("events")


# ================= DELETE EVENT =================
@login_required
def delete_event(request, id):

    if not request.user.is_superuser:
        return redirect("events")

    event = get_object_or_404(Event, id=id)
    event.delete()

    return redirect("events")


# ================= ADMIN REVIEW =================
@login_required
def admin_events_review(request):

    if not request.user.is_superuser:
        return redirect("home")

    events = Event.objects.filter(approval_status="pending")

    return render(request, "admin_events.html", {
        "events": events
    })


# ================= EXPORT ATTENDEES =================
@login_required
def export_attendees(request, id):

    event = get_object_or_404(Event, id=id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendees"

    ws.append(["First Name", "Last Name", "Phone", "Email"])

    for user in event.attendees.all():
        ws.append([
            user.first_name,
            user.last_name,
            user.phone,
            user.email
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename={event.title}.xlsx'

    wb.save(response)
    return response
# ================= admin_volunteer_details =================
@login_required
def admin_volunteer_details(request, station_id):
    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    users = User.objects.filter(polling_station_id=station_id)

    return JsonResponse([
        {
            "name": u.first_name + " " + u.last_name,
            "phone": u.phone,
            "email": u.email
        }
        for u in users
    ], safe=False)

# ================= DOWNLOAD USERS =================
@login_required
def download_users_excel(request):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"

    ws.append(["First Name", "Last Name", "Email", "Phone", "Role"])

    for user in User.objects.all():
        ws.append([
            user.first_name,
            user.last_name,
            user.email,
            user.phone,
            user.role
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = "attachment; filename=users.xlsx"

    wb.save(response)
    return response


# ================= volunteer_map_data =================

def volunteer_map_data(request):

    stations = PollingStation.objects.all()

    data = []

    for s in stations:

        volunteers = User.objects.filter(polling_station=s)

        data.append({
            "id": s.id,
            "name": s.name,
            "lat": s.latitude,
            "lng": s.longitude,
            "count": volunteers.count(),

            # ❌ REMOVE PHONE NUMBERS (SECURITY FIX)
            "volunteers": [
                {
                    "name": v.first_name + " " + v.last_name
                }
                for v in volunteers
            ]
        })

    return JsonResponse(data, safe=False)

# ================= volunteer_map_api =================


def volunteer_map_api(request):

    stations = PollingStation.objects.filter(
        ward__constituency__county__name__icontains="Laikipia"
    )

    data = []

    for s in stations:
        volunteers = s.volunteer_set.all()

        data.append({
            "name": s.name,
            "lat": s.latitude,
            "lng": s.longitude,
            "count": volunteers.count(),
            "volunteers": [
                {"name": v.first_name + " " + v.last_name}
                for v in volunteers
            ]
        })

    return JsonResponse(data, safe=False)


# ================= WHATSAPP =================
@login_required
def whatsapp_attendees(request, id):

    event = get_object_or_404(Event, id=id)

    if request.user != event.created_by and not request.user.is_superuser:
        return redirect("events")

    message = f"Hello, reminder for event: {event.title} at {event.location} on {event.date}"
    text = urllib.parse.quote(message)

    return redirect(f"https://wa.me/?text={text}")


# ================= AJAX =================
def load_wards(request):

    constituency_id = request.GET.get('constituency')

    if not constituency_id or not constituency_id.isdigit():
        return JsonResponse([], safe=False)

    wards = Ward.objects.filter(constituency_id=constituency_id)
    return JsonResponse(list(wards.values('id', 'name')), safe=False)


def load_polling(request):

    ward_id = request.GET.get('ward')

    if not ward_id or not ward_id.isdigit():
        return JsonResponse([], safe=False)

    polling = PollingStation.objects.filter(ward_id=ward_id)
    return JsonResponse(list(polling.values('id', 'name')), safe=False)