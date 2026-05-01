from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import User, Event, Donation, Ward


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard_view(request):

    total_users = User.objects.count()
    volunteers = User.objects.filter(role="volunteer").count()
    leaders = User.objects.filter(role="leader").count()

    active_volunteers = User.objects.filter(
        volunteer_status="active"
    ).count()

    events = Event.objects.count()
    donations = Donation.objects.count()

    top_volunteers = User.objects.filter(
        role="volunteer"
    ).order_by("-activity_score")[:5]

    wards = Ward.objects.all()

    return render(request, "admin/campaign_dashboard.html", {
        "total_users": total_users,
        "volunteers": volunteers,
        "leaders": leaders,
        "active_volunteers": active_volunteers,
        "events": events,
        "donations": donations,
        "top_volunteers": top_volunteers,
        "wards": wards,
    })