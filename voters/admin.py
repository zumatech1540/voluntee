from django.contrib import admin
from .models import Voter


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "ward",
        "polling_station",
        "support_level",
        "created_by",
        "created_at"
    )

    list_filter = ("support_level", "ward")
    search_fields = ("name", "phone")