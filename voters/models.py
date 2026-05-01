from django.db import models
from django.conf import settings
from accounts.models import Ward, PollingStation


class Voter(models.Model):

    SUPPORT_CHOICES = [
        ("strong", "Strong Supporter"),
        ("undecided", "Undecided"),
        ("opponent", "Opponent"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)

    ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    polling_station = models.ForeignKey(
        PollingStation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    support_level = models.CharField(
        max_length=20,
        choices=SUPPORT_CHOICES,
        default="undecided"
    )

    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"