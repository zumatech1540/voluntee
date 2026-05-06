from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Sum
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from accounts.utils.permissions import admin_required, leader_required, volunteer_required
from datetime import date, timedelta

import openpyxl
import urllib.parse


from .models import (
    User, Task, TaskComment, PasswordResetOTP, SMSLog,
    County, Constituency, Ward, PollingStation,
    Event, Donation, Voter, Attendance
)
# ================= HOME =================



def home_page(request):
    return render(request, "home.html")

def about_page(request):
    return render(request, "about.html")


def volunteers_page(request):
    volunteers = User.objects.filter(role="volunteer")

    return render(request, "volunteers.html", {
        "volunteers": volunteers
    })


def gallery_page(request):
    return render(request, "gallery.html")


def donation_page(request):
    return render(request, "donation.html")


def blogs_page(request):
    return render(request, "blogs.html")


def contact_page(request):
    return render(request, "contact.html")

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == "admin")


def is_leader(user):
    return user.is_authenticated and user.role == "leader"


def is_volunteer(user):
    return user.is_authenticated and user.role == "volunteer"

def manage_users(request):

    wards = Ward.objects.all()
    
# ================= REGISTER =================


def register_view(request):

    county = County.objects.filter(name__icontains="Laikipia").first()
    constituencies = Constituency.objects.filter(county=county) if county else Constituency.objects.none()

    if request.method == "POST":

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        constituency_id = request.POST.get("constituency")
        ward_id = request.POST.get("ward")
        polling_station_id = request.POST.get("polling_station")

        profession = request.POST.get("profession")
        other_profession = request.POST.get("other_profession")

        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # ================= VALIDATION =================
        if not email or not password1:
            messages.error(request, "Email and password are required")
            return redirect("register")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect("register")

        # ================= CREATE USER =================
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )

        # ================= SYSTEM-ENFORCED ROLE =================
        user.role = "volunteer"   # ALWAYS DEFAULT

        # ================= PROFILE DATA =================
        user.phone = phone
        user.county = county

        if constituency_id and constituency_id.isdigit():
            user.constituency_id = int(constituency_id)

        if ward_id and ward_id.isdigit():
            user.ward_id = int(ward_id)

        if polling_station_id and polling_station_id.isdigit():
            user.polling_station_id = int(polling_station_id)

        user.profession = profession
        user.other_profession = other_profession

        user.save()

        login(request, user)

        # ================= REDIRECT =================
        return redirect("home")   # 🔥 FIXED (not home)

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
                user_obj = get_user_model().objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except:
                user = None

        if user:

            login(request, user)

            # ================= ROLE ROUTING FIX =================

            if user.is_superuser:
                return redirect("admin_dashboard")

            elif user.role == "leader":
                return redirect("leader_dashboard")

            else:
                return redirect("home")  # 🔥 IMPORTANT FIX

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# ================= dashboard_redirect =================


@login_required
def dashboard_redirect(request):

    user = request.user
    role = getattr(user, "role", "volunteer")

    if user.is_superuser or role == "admin":
        return redirect("admin_dashboard")

    elif role == "leader":
        return redirect("leader_dashboard")

    else:
        return redirect("volunteer_dashboard")

# ================= home =================
def home(request):

    tasks = []

    if request.user.is_authenticated:
        tasks = Task.objects.filter(assigned_to=request.user)

    return render(request, "home.html", {
        "tasks": tasks
    })
# ================= volunteer_home =================


@login_required
def heat_map(request):

    # 🔒 access control
    if not (request.user.role == "leader" or request.user.is_superuser):
        return redirect("home")

    wards = Ward.objects.all()

    data = []

    for w in wards:

        voters = Voter.objects.filter(ward=w)

        total = voters.count()
        supporters = voters.filter(support_status="supporter").count()
        undecided = voters.filter(support_status="undecided").count()
        opponents = voters.filter(support_status="opponent").count()

        # status logic (matches your UI colors)
        if supporters > opponents and supporters > undecided:
            status = "strong"
        elif undecided > supporters and undecided > opponents:
            status = "undecided"
        else:
            status = "weak"

        data.append({
            "ward": w.name,
            "total": total,
            "supporters": supporters,
            "undecided": undecided,
            "opponents": opponents,
            "status": status
        })

    return render(request, "heatmap.html", {
        "data": data
    })
    
# ================= volunteer_home =================
@login_required
def voter_list(request):

    if not (request.user.role == "leader" or request.user.is_superuser):
        return redirect("home")

    voters = Voter.objects.all()
# ================= volunteer_home =================
@login_required
def volunteer_home(request):

    if not is_volunteer(request.user):
        return redirect("home")

    tasks = Task.objects.filter(assigned_to=request.user)

    return render(request, "volunteer_home.html", {"tasks": tasks})

# ================= complete_task =================
def complete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.status = "completed"
    task.save()
    return redirect("volunteer_home")

# ================= LOGOUT =================
def logout_view(request):
    logout(request)
    return redirect("login")


# ================= HELPERS =================
def is_leader(user):
    return user.is_authenticated and user.role == "leader"


def is_admin(user):
    return user.is_authenticated and user.is_superuser



# ================= my_tasks=================
def my_tasks(request):
    tasks = Task.objects.filter(user=request.user)

    return render(request, "my_tasks.html", {
        "tasks": tasks
    })
# ================= dashboard =================

@login_required




# ================= LEADER DASHBOARD =================
@login_required
def leader_dashboard(request):

    if not is_leader(request.user): return redirect("home")

    from django.db.models import Count, Q
    from datetime import date
    from .models import Task, Voter, User, Event

    # ================= EVENTS =================
    if request.user.is_superuser:
        events = Event.objects.all().order_by('-id')
    else:
        events = Event.objects.filter(created_by=request.user).order_by('-id')

    total_events = events.count()
    pending_events = events.filter(approval_status="pending").count()
    approved_events = events.filter(approval_status="approved").count()

    # ================= USERS =================
    volunteers = User.objects.filter(role="volunteer")
    leaders = User.objects.filter(role="leader")

    total_volunteers = volunteers.count()
    total_leaders = leaders.count()

    # ================= TASKS =================
    if request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_by=request.user)

    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='pending').count()
    in_progress_tasks = tasks.filter(status='in_progress').count()
    completed_tasks = tasks.filter(status='completed').count()

    overdue_tasks = tasks.filter(
        due_date__lt=date.today()
    ).exclude(status='completed').count()

    # ================= TASK PERFORMANCE =================
    task_performance = (
        Task.objects.exclude(assigned_by=None)
        .values('assigned_by__first_name', 'assigned_by__last_name')
        .annotate(
            total_tasks=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            pending=Count('id', filter=Q(status='pending')),
            in_progress=Count('id', filter=Q(status='in_progress')),
        )
        .order_by('-completed')
    )

    # ================= CHART =================
    task_status_chart = {
        "pending": pending_tasks,
        "in_progress": in_progress_tasks,
        "completed": completed_tasks
    }

    priority_stats = tasks.values('priority').annotate(total=Count('id'))

    # ================= VOTERS =================
    total_voters = Voter.objects.count()
    supporters = Voter.objects.filter(support_status='supporter').count()
    undecided = Voter.objects.filter(support_status='undecided').count()
    opponents = Voter.objects.filter(support_status='opponent').count()

    # ================= WARD ANALYSIS =================
    ward_analysis = (
        Voter.objects.values('ward__name')
        .annotate(
            total=Count('id'),
            supporters=Count('id', filter=Q(support_status='supporter')),
            undecided=Count('id', filter=Q(support_status='undecided')),
            opponents=Count('id', filter=Q(support_status='opponent')),
        )
        .order_by('-supporters')
    )

    notifications = [
        "📊 Leader dashboard active",
        "📌 Monitor task completion rates",
        "⚠ Track overdue tasks",
        "📍 Focus on weak wards",
        "📈 Improve volunteer performance"
    ]

    return render(request, "dashboard.html", {
        "events": events,
        "total_events": total_events,
        "pending_events": pending_events,
        "approved_events": approved_events,

        "total_volunteers": total_volunteers,
        "total_leaders": total_leaders,

        "tasks": tasks,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,

        "task_status_chart": task_status_chart,
        "priority_stats": priority_stats,
        "task_performance": task_performance,

        "total_voters": total_voters,
        "supporters": supporters,
        "undecided": undecided,
        "opponents": opponents,

        "ward_analysis": ward_analysis,
        "notifications": notifications,
    })

# ================= admin_dashboard =================


@login_required
def admin_dashboard(request):

    # ================= SECURITY =================
    if not request.user.is_superuser:
        return redirect("home")

    # ================= CORE DATA =================
    events = Event.objects.all().order_by('-id')
    members = User.objects.all().order_by('-id')
    donations = Donation.objects.all().order_by("-created_at")
    voters = Voter.objects.all()
    attendance = Attendance.objects.all()

    # ================= COUNTS =================
    total_events = events.count()
    total_members = members.count()
    total_voters = voters.count()
    total_attendance = attendance.count()

    total_leaders = members.filter(role="leader").count()
    total_volunteers = members.filter(role="volunteer").count()

    pending_events = events.filter(approval_status="pending").count()
    approved_events = events.filter(approval_status="approved").count()

    total_donations = donations.aggregate(
        total=Sum("amount")
    )["total"] or 0

    # ================= ACTIVITY INSIGHTS =================

    top_volunteers = (
        Voter.objects.values("added_by__first_name", "added_by__last_name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    event_creators = (
        Event.objects.values("created_by__first_name", "created_by__last_name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # ================= SYSTEM HEALTH =================
    system_health = {
        "event_completion_rate": round(
            (approved_events / total_events) * 100, 2
        ) if total_events else 0,

        "volunteer_ratio": round(
            (total_volunteers / total_members) * 100, 2
        ) if total_members else 0,
    }

    # ================= NOTIFICATIONS =================
    notifications = [
        "System running normally",
        "Check pending events",
        "Monitor volunteer activity",
        "Review donations"
    ]

    return render(request, "admin_dashboard.html", {
        # DATA
        "events": events,
        "members": members,
        "donations": donations,

        # COUNTS
        "total_voters": total_voters,
        "total_attendance": total_attendance,
        "total_events": total_events,
        "total_members": total_members,

        "total_leaders": total_leaders,
        "total_volunteers": total_volunteers,

        "pending_events": pending_events,
        "approved_events": approved_events,

        "total_donations": total_donations,

        # INSIGHTS
        "top_volunteers": top_volunteers,
        "event_creators": event_creators,

        # HEALTH
        "system_health": system_health,

        # UI
        "notifications": notifications,
    })

# ================= donate =================

def donate(request):

    if request.method == "POST":

        Donation.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            donation_type=request.POST.get("donation_type"),
            amount=request.POST.get("amount") or None,
            message=request.POST.get("message")
        )

        messages.success(request, "Thank you for your donation!")

        return redirect("donate")

    return render(request, "donate.html")

# ================= EVENTS =================
def events_page(request):

    if request.user.is_superuser:
        events = Event.objects.all().order_by("-id")

    elif request.user.is_authenticated and is_leader(request.user):
        events = Event.objects.filter(created_by=request.user).order_by("-id")

    else:
        events = Event.objects.filter(approval_status="approved").order_by("-id")

    return render(request, "events.html", {"events": events})


# ================= CREATE EVENT =================


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
@login_required
def create_event(request):

    if not (request.user.is_superuser or is_leader(request.user)):
        return redirect("events")

    if request.method == "POST":

        Event.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            location=request.POST.get("location"),
            date=request.POST.get("date"),
            image=request.FILES.get("image"),
            created_by=request.user,
            approval_status="pending"
        )

        messages.success(request, "Event created successfully")
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


from django.views.decorators.http import require_POST
from django.contrib import messages

@login_required
@require_POST
def join_event(request, id):

    try:
        event = get_object_or_404(Event, id=id)

        # check approval
        if event.approval_status != "approved":
            messages.error(request, "Event not open")
            return redirect("events")

        # prevent duplicate
        exists = Attendance.objects.filter(
            event=event,
            user=request.user
        ).exists()

        if not exists:
            Attendance.objects.create(
                event=event,
                user=request.user,
                role_type=getattr(request.user, "role", "volunteer"),  # SAFE FIX
                status="present"
            )
            messages.success(request, "Joined successfully")
        else:
            messages.info(request, "Already joined")

        return redirect("event_detail", id=id)

    except Exception as e:
        print("ERROR:", e)  # 👈 shows real error in terminal
        messages.error(request, "Something went wrong")
        return redirect("events")


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


# ================= contact_page =================


def contact_page(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # BASIC VALIDATION
        if not name or not email or not message:
            messages.error(request, "Please fill all required fields")
            return redirect("contact")

        # 👉 OPTION 1: JUST SHOW SUCCESS (for now)
        # (Later we can save to DB or send email)

        print("NEW CONTACT MESSAGE:")
        print(name, email, subject, message)

        messages.success(request, "Your message has been sent successfully!")

        return redirect("contact")

    return render(request, "contact.html")

# ================= assign_task =================
from django.contrib import messages
from django.utils import timezone
from datetime import date

from django.contrib import messages
@login_required
def assign_task(request):

    if not (request.user.is_superuser or request.user.role == "leader"):
        return redirect("home")

    if request.user.is_superuser:
        volunteers = User.objects.filter(role="volunteer")
    else:
        volunteers = User.objects.filter(role="volunteer")

    events = Event.objects.all()

    if request.method == "POST":

        user_ids = request.POST.getlist("assigned_to")

        if not user_ids:
            messages.error(request, "Select at least one volunteer")
            return redirect("assign_task")

        created_tasks = []

        for uid in user_ids:

            try:
                user = User.objects.get(id=uid)
            except User.DoesNotExist:
                continue

            # create task
            task = Task.objects.create(
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                assigned_to=user,
                assigned_by=request.user,
                event_id=request.POST.get("event") or None,
                priority=request.POST.get("priority"),
                due_date=request.POST.get("due_date") or None,
                status="pending"
            )

            created_tasks.append(task)

        messages.success(request, "Tasks assigned successfully")

        # 👉 redirect to first task chat (SAFE)
        if created_tasks:
            return redirect("task_chat", created_tasks[0].id)

        return redirect("assign_task")

    return render(request, "assign_task.html", {
        "volunteers": volunteers,
        "events": events
    })

# ================= my_tasks =================
@login_required
def my_tasks(request):

    tasks = Task.objects.filter(assigned_to=request.user).order_by("-created_at")

    return render(request, "my_tasks.html", {
        "tasks": tasks
    })

# ================= update_task_status =================
@login_required
def update_task_status(request, id):

    task = get_object_or_404(Task, id=id)

    # only assigned volunteer OR admin
    if request.user != task.assigned_to and not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in ["pending", "in_progress", "completed"]:
            task.status = new_status
            task.save()
            messages.success(request, "Task updated successfully")

    return redirect("my_tasks")

# ================= leader_tasks =================
@login_required
def leader_tasks(request):

    if request.user.role != "leader" and not request.user.is_superuser:
        return redirect("home")

    tasks = Task.objects.filter(assigned_by=request.user).order_by("-created_at")

    return render(request, "leader_tasks.html", {
        "tasks": tasks
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Task

# ================= complete_task =================
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def complete_task(request, id):

    task = get_object_or_404(Task, id=id, assigned_to=request.user)

    if request.method == "POST":
        task.status = "completed"
        task.save()

        messages.success(request, "Task marked as completed ✅")

    return redirect("volunteer_home")

# ================= task_feedback =================


def task_feedback(request, id):

    task = get_object_or_404(Task, id=id)

    # 🔒 Only allowed users
    if request.user not in [task.assigned_to, task.assigned_by] and not request.user.is_superuser:
        messages.error(request, "Not allowed")
        return redirect("dashboard")

    if request.method == "POST":
        feedback = request.POST.get("feedback")

        task.feedback = feedback
        task.feedback_by = request.user
        task.feedback_date = timezone.now()
        task.save()

        messages.success(request, "Feedback submitted successfully ✅")
        return redirect("dashboard")

    return render(request, "task_feedback.html", {"task": task})

# =================task_chat =================


def task_chat(request, id):

    task = get_object_or_404(Task, id=id)

    # 🔒 SECURITY
    if request.user not in [task.assigned_to, task.assigned_by] and not request.user.is_superuser:
        messages.error(request, "Not allowed")
        return redirect("dashboard")

    if request.method == "POST":
        message = request.POST.get("message")

        if message:
            TaskComment.objects.create(
                task=task,
                user=request.user,
                message=message
            )

        return redirect("task_chat", id=task.id)

    comments = task.comments.all().order_by("created_at")

    return render(request, "task_chat.html", {
        "task": task,
        "comments": comments
    })
# ================= leader_charts =================
def leader_charts(request):

    if not (is_leader(request.user) or request.user.is_superuser):
        return redirect("home")

    return render(request, "leader_charts.html")

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

# ================= manage_users =================

@login_required
def manage_users(request):

    if not request.user.is_superuser:
        return redirect("home")

    from django.db.models import Count, Q
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    from .models import Attendance, Voter

    # ================= USERS WITH TASK STATS =================
    users = User.objects.annotate(
        total_tasks=Count('tasks_created'),
        completed_tasks=Count('tasks_created', filter=Q(tasks_created__status='completed')),
        pending_tasks=Count('tasks_created', filter=Q(tasks_created__status='pending')),
        in_progress_tasks=Count('tasks_created', filter=Q(tasks_created__status='in_progress')),
    ).order_by("-id")

    wards = Ward.objects.all()
    stations = PollingStation.objects.all()
    events = Event.objects.all()

    # ================= ADD USER =================
    if request.method == "POST" and request.POST.get("action") == "add_user":

        email = request.POST.get("email")
        first_name = request.POST.get("first_name")

        if not email or not first_name:
            messages.error(request, "Email and First Name are required")
            return redirect("manage_users")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect("manage_users")

        User.objects.create_user(
            username=email,
            email=email,
            password="12345678",
            first_name=first_name,
            last_name=request.POST.get("last_name"),
            role=request.POST.get("role"),
            phone=request.POST.get("phone"),
            ward_id=request.POST.get("ward") or None,
            polling_station_id=request.POST.get("polling_station") or None,
        )

        messages.success(request, "User created successfully")
        return redirect("manage_users")

    # ================= ATTENDANCE =================
    if request.method == "POST" and request.POST.get("action") == "attendance":

        event_id = request.POST.get("event_id")
        voter_name = request.POST.get("voter_name")
        phone = request.POST.get("phone")

        if not event_id:
            messages.error(request, "Please select an event")
            return redirect("manage_users")

        if not voter_name or not phone:
            messages.error(request, "Voter name and phone are required")
            return redirect("manage_users")

        event = get_object_or_404(Event, id=event_id)

        names = voter_name.strip().split(" ", 1)

        voter = Voter.objects.create(
            first_name=names[0],
            last_name=names[1] if len(names) > 1 else "",
            phone=phone.strip(),
            ward=getattr(request.user, "ward", None),
            added_by=request.user
        )

        Attendance.objects.create(
            event=event,
            voter=voter,
            user=request.user,
            role_type="voter"
        )

        messages.success(request, "Attendance recorded successfully")
        return redirect("manage_users")

    return render(request, "manage_users.html", {
        "users": users,
        "wards": wards,
        "stations": stations,
        "events": events
    })

# ================= user_tasks_admin =================
@login_required
def user_tasks_admin(request, user_id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    status = request.GET.get("status")  # filter

    tasks = user.tasks_assigned.all().order_by("-created_at")

    if status in ["pending", "in_progress", "completed"]:
        tasks = tasks.filter(status=status)

    return render(request, "admin_user_tasks.html", {
        "selected_user": user,
        "tasks": tasks,
        "status": status
    })


# ================= delete_user =================
@login_required
def delete_user(request, id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=id)

    if not user.is_superuser:
        user.delete()

    return redirect("manage_users")

# ================= VOLUNTEER ASSIGNMENT =================


@staff_member_required
def volunteer_assignment(request):

    volunteers = User.objects.filter(role="volunteer")

    wards = Ward.objects.all()
    stations = PollingStation.objects.all()

    if request.method == "POST":

        user_id = request.POST.get("user_id")

        volunteer = User.objects.get(id=user_id)

        volunteer.volunteer_role = request.POST.get("volunteer_role")
        volunteer.volunteer_status = request.POST.get("volunteer_status")

        volunteer.ward_id = request.POST.get("ward")
        volunteer.polling_station_id = request.POST.get("polling_station")

        volunteer.activity_score = request.POST.get("activity_score") or 0

        volunteer.save()

        messages.success(request, "Volunteer updated successfully")

        return redirect("volunteer_assignment")

    return render(request, "volunteer_assignment.html", {
        "volunteers": volunteers,
        "wards": wards,
        "stations": stations
    })


#================= assign_task_admin =================
@login_required
def assign_task_admin(request, user_id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":

        due_date = request.POST.get("due_date")

        # prevent past dates
        if due_date and due_date < str(timezone.now().date()):
            messages.error(request, "You cannot assign past dates")
            return redirect("assign_task_admin", user_id=user_id)

        Task.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            assigned_to=user,
            assigned_by=request.user,
            priority=request.POST.get("priority"),
            due_date=due_date if due_date else None
        )

        messages.success(request, "Task assigned successfully")
        return redirect("manage_users")

    return render(request, "admin_assign_task.html", {
        "user": user
    })
    
# ================= VOLUNTEER PERFORMANCE =================
@login_required
def volunteer_performance(request):

    if not request.user.is_superuser:
        return redirect("home")

    volunteers = User.objects.filter(role="volunteer").annotate(
        total_tasks=Count('tasks_assigned')
    ).order_by('-total_tasks')

    return render(request, "volunteer_performance.html", {
        "volunteers": volunteers
    })


# ================= ward_strength =================
@login_required
def ward_strength(request):

    if not request.user.is_superuser:
        return redirect("home")

    wards = Ward.objects.all()

    data = []

    for ward in wards:
        volunteers = User.objects.filter(ward=ward, role="volunteer")

        data.append({
            "ward": ward,
            "total": volunteers.count(),
            "active": volunteers.filter(volunteer_status="active").count(),
        })

    return render(request, "admin/ward_strength.html", {
        "data": data
    })
# ================= polling_strength =================
@login_required
def polling_strength(request):

    stations = PollingStation.objects.all()

    data = []

    for s in stations:
        volunteers = User.objects.filter(polling_station=s)

        data.append({
            "station": s,
            "count": volunteers.count()
        })

    return render(request, "polling_strength.html", {
        "data": data
    })


# ================= REGISTER VOTER =================

@login_required
def register_voter(request):

    wards = Ward.objects.all()
    stations = PollingStation.objects.all()

    if request.method == "POST":

        Voter.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            phone=request.POST.get("phone"),
            gender=request.POST.get("gender"),
            age=request.POST.get("age") or None,
            ward_id=request.POST.get("ward"),
            polling_station_id=request.POST.get("polling_station"),
            support_status=request.POST.get("support_status"),
            notes=request.POST.get("notes"),
            added_by=request.user
        )

        messages.success(request, "Voter registered successfully")
        return redirect("register_voter")

    return render(request, "register_voter.html", {
        "wards": wards,
        "stations": stations
    })

# ================= add_voter =================
@login_required
def add_voter(request):

    wards = Ward.objects.all()
    polling = PollingStation.objects.all()

    if request.method == "POST":

        Voter.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),

            ward_id=request.POST.get("ward"),
            polling_station_id=request.POST.get("polling_station"),

            support_status=request.POST.get("support_status"),
            notes=request.POST.get("notes"),

            added_by=request.user
        )

        return redirect("voter_list")

    return render(request, "add_voter.html", {
        "wards": wards,
        "polling": polling
    })


# ================= voter_list =================
@login_required
def voter_list(request):

    voters = Voter.objects.all().order_by("-created_at")

    ward = request.GET.get("ward")
    polling = request.GET.get("polling")
    support = request.GET.get("support")

    if ward:
        voters = voters.filter(ward_id=ward)

    if polling:
        voters = voters.filter(polling_station_id=polling)

    if support:
        voters = voters.filter(support_status=support)

    wards = Ward.objects.all()
    polling = PollingStation.objects.all()

    return render(request, "voter_list.html", {
        "voters": voters,
        "wards": wards,
        "polling": polling
    })

# ================= make_leader =================
@login_required
def make_leader(request, id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=id)

    user.role = "leader"
    user.save()

    return redirect("manage_users")

# ================= make_volunteer =================
@login_required
def make_volunteer(request, id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=id)

    user.role = "volunteer"
    user.save()

    return redirect("manage_users")


# ================= make_admin =================
@login_required
def make_admin(request, id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=id)

    user.is_superuser = True
    user.is_staff = True
    user.save()

    return redirect("manage_users")

# ================= event_attendance =================
@login_required
def event_attendance(request, id):

    event = get_object_or_404(Event, id=id)

    # ================= FILTER VOTERS BY WARD =================
    if hasattr(request.user, "ward") and request.user.ward:
        voters = Voter.objects.filter(ward=request.user.ward)
    else:
        voters = Voter.objects.all()

    attendances = Attendance.objects.filter(event=event)

    # ================= POST REQUEST =================
    if request.method == "POST":

        voter_id = request.POST.get("voter_id")
        first_name = request.POST.get("first_name")
        phone = request.POST.get("phone")

        # ================= VALIDATION =================
        if not voter_id and not first_name:
            messages.error(request, "Select a voter or enter new voter details")
            return redirect("event_attendance", id=id)

        # ================= EXISTING VOTER =================
        if voter_id:
            voter = get_object_or_404(Voter, id=voter_id)

        # ================= NEW VOTER =================
        else:
            if not first_name or not phone:
                messages.error(request, "First name and phone are required")
                return redirect("event_attendance", id=id)

            voter = Voter.objects.create(
                first_name=first_name.strip(),
                last_name="",
                phone=phone.strip(),
                ward=request.user.ward if hasattr(request.user, "ward") else None,
                added_by=request.user
            )

        # ================= PREVENT DUPLICATE ATTENDANCE =================
        attendance_exists = Attendance.objects.filter(
            event=event,
            voter=voter
        ).exists()

        if attendance_exists:
            messages.warning(request, "Voter already marked present")
            return redirect("event_attendance", id=id)

        Attendance.objects.create(
            event=event,
            voter=voter,
            user=request.user,
            role_type="voter",
            status="present"
        )

        messages.success(request, "Attendance recorded successfully")
        return redirect("event_attendance", id=id)

    return render(request, "attendance.html", {
        "event": event,
        "voters": voters,
        "attendances": attendances
    })

# ================= remove_admin =================
@login_required
def remove_admin(request, id):

    if not request.user.is_superuser:
        return redirect("home")

    user = get_object_or_404(User, id=id)

    # prevent removing yourself
    if user != request.user:
        user.is_superuser = False
        user.is_staff = False
        user.save()

    return redirect("manage_users")
    
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

# ================= whatsapp_voters =================
@login_required
def whatsapp_voters(request):

    voters = Voter.objects.all()

    ward = request.GET.get("ward")
    support = request.GET.get("support")

    if ward:
        voters = voters.filter(ward_id=ward)

    if support:
        voters = voters.filter(support_status=support)

    phones = []

    for v in voters:
        if v.phone:
            phone = v.phone.replace("+", "").replace(" ", "")
            phones.append(phone)

    message = request.GET.get("message")

    if message:
        text = urllib.parse.quote(message)

        # WhatsApp multi message
        numbers = ",".join(phones[:20])  # whatsapp limit
        return redirect(f"https://wa.me/?text={text}")

    wards = Ward.objects.all()

    return render(request, "whatsapp.html", {
        "wards": wards
    })

# ================= sms_broadcast =================


@login_required
def sms_broadcast(request):

    wards = Ward.objects.all()

    if request.method == "POST":

        message = request.POST.get("message")
        target = request.POST.get("target")
        ward_id = request.POST.get("ward")
        phone = request.POST.get("phone")

        clean_numbers = []

        # ================= VALIDATION =================
        if not message:
            return render(request, "sms.html", {
                "wards": wards,
                "error": "Message cannot be empty"
            })

        # ================= SINGLE SMS =================
        if phone:
            p = phone.strip()

            if p.startswith("0"):
                p = "+254" + p[1:]
            elif not p.startswith("+"):
                p = "+254" + p

            clean_numbers.append(p)

        # ================= BULK SMS =================
        else:
            voters = Voter.objects.all()

            if target == "supporters":
                voters = voters.filter(support_status="supporter")

            elif target == "undecided":
                voters = voters.filter(support_status="undecided")

            elif target == "opponents":
                voters = voters.filter(support_status="opponent")

            if ward_id:
                voters = voters.filter(ward_id=ward_id)

            phones = [v.phone for v in voters if v.phone]

            for p in phones:
                if p.startswith("0"):
                    p = "+254" + p[1:]
                elif not p.startswith("+"):
                    p = "+254" + p

                clean_numbers.append(p)

        # ================= REMOVE DUPLICATES =================
        clean_numbers = list(set(clean_numbers))

        # ================= SAFETY CHECK =================
        if not clean_numbers:
            return render(request, "sms.html", {
                "wards": wards,
                "error": "No valid phone numbers found"
            })

        # ================= SEND SMS =================
        results = send_sms(clean_numbers, message)

        # ================= STATUS SUMMARY =================
        sent_count = sum(1 for r in results if r["status"] == "sent")
        failed_count = sum(1 for r in results if r["status"] == "failed")

        # ================= RESPONSE =================
        return render(request, "sms.html", {
            "wards": wards,
            "success": f"✅ Sent: {sent_count} | ❌ Failed: {failed_count}",
            "results": results
        })

    return render(request, "sms.html", {
        "wards": wards
    })

# ================= send_sms =================


def send_sms(phone_numbers, message):

    results = []

    for number in phone_numbers:

        # create initial log
        log = SMSLog.objects.create(
            phone=number,
            message=message,
            status="pending"
        )

        try:
            # 🔥 SIMULATION (replace later with real API)
            print(f"[SMS] Sending to {number}: {message}")

            # mark success
            log.status = "sent"
            log.response = "Message sent successfully"

        except Exception as e:
            log.status = "failed"
            log.response = str(e)

        log.save()

        results.append({
            "phone": number,
            "status": log.status
        })

    return results


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



# ================= request_otp =================



# ================= REQUEST OTP =================
def request_otp(request):

    if request.method == "POST":
        phone = request.POST.get("phone")

        users = User.objects.filter(phone=phone)

        if not users.exists():
            messages.error(request, "Phone not found")
            return redirect("request_otp")

        if users.count() > 1:
            messages.error(request, "Duplicate phone accounts found")
            return redirect("request_otp")

        user = users.first()

        # RESEND LIMIT
        last = PasswordResetOTP.objects.filter(user=user).last()
        if last and (timezone.now() - last.created_at).seconds < 60:
            messages.error(request, "Wait 60 seconds before resending OTP")
            return redirect("request_otp")

        otp = generate_otp()

        obj = PasswordResetOTP(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        obj.set_otp(otp)
        obj.save()

        send_sms([phone], f"Your OTP is {otp}")

        request.session["reset_user"] = user.id

        messages.success(request, "OTP sent successfully")
        return redirect("verify_otp")

    return render(request, "request_otp.html")



# ================= RESET PASSWORD =================
def reset_password(request):

    if not request.session.get("otp_verified"):
        return redirect("request_otp")

    user_id = request.session.get("reset_user")
    user = User.objects.get(id=user_id)

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("reset_password")

        if len(password) < 8:
            messages.error(request, "Password too weak (min 8 chars)")
            return redirect("reset_password")

        user.password = make_password(password)
        user.save()

        # AUTO LOGIN
        login(request, user)

        # CLEAN SESSION
        request.session.flush()

        messages.success(request, "Password reset successful")
        return redirect("home")

    return render(request, "reset_password.html")

# ================= verify_otp =================
def verify_otp(request):

    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("login")

    if request.method == "POST":
        otp = request.POST.get("otp")

        record = PasswordResetOTP.objects.filter(user_id=user_id).last()

        if not record:
            messages.error(request, "No OTP found")
            return redirect("request_otp")

        # ⛔ BLOCK IF TOO MANY ATTEMPTS
        if record.attempts >= 5:
            messages.error(request, "Too many attempts. Request new OTP")
            return redirect("request_otp")

        if not record.is_valid():
            messages.error(request, "OTP expired")
            return redirect("request_otp")

        if record.check_otp(otp):
            record.is_used = True
            record.save()

            request.session['otp_verified'] = True

            return redirect("reset_password")

        else:
            record.attempts += 1
            record.save()

            messages.error(request, f"Invalid OTP ({record.attempts}/5)")

    return render(request, "verify_otp.html")

    
