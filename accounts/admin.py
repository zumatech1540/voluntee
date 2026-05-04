from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import (
    County,
    Constituency,
    Ward,
    PollingStation,
    Event,
    Donation,
    Voter
)

User = get_user_model()


# ================= USER ADMIN =================
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):

    model = User

    list_display = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "role",
        "volunteer_role",
        "volunteer_status",
        "activity_score",
        "ward",
        "polling_station",
    )

    list_filter = (
        "role",
        "volunteer_role",
        "volunteer_status",
        "county",
        "constituency",
        "ward",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    ordering = ("-id",)

    fieldsets = BaseUserAdmin.fieldsets + (

        ("Campaign Role", {
            "fields": (
                "role",
                "volunteer_role",
                "volunteer_status",
            )
        }),

        ("Performance Tracking", {
            "fields": (
                "activity_score",
                "events_attended",
            )
        }),

        ("Location Assignment", {
            "fields": (
                "county",
                "constituency",
                "ward",
                "polling_station",
            )
        }),

        ("Additional Info", {
            "fields": (
                "phone",
                "profession",
                "other_profession",
            )
        }),
    )


# ================= VOTER ADMIN =================
@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "phone",
        "ward",
        "polling_station",
        "support_status",
        "added_by",
        "created_at",
    )

    list_filter = (
        "support_status",
        "ward",
        "polling_station",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
    )

    ordering = ("-created_at",)


# ================= LOCATION ADMIN =================
admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(Ward)
admin.site.register(PollingStation)


# ================= DONATION ADMIN =================
@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "email",
        "donation_type",
        "amount",
        "created_at",
    )

    search_fields = (
        "name",
        "phone",
        "email",
    )

    list_filter = (
        "donation_type",
        "created_at",
    )


# ================= EVENT ADMIN =================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "location",
        "date",
        "approval_status",
        "created_by",
    )

    list_filter = (
        "approval_status",
        "date",
    )

    search_fields = (
        "title",
        "location",
    )

    ordering = ("-date",)