from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('volunteer', 'Volunteer'),
        ('leader', 'Leader'),
    )

    PROFESSION_CHOICES = (
        ('farmer', 'Farmer'),
        ('teacher', 'Teacher'),
        ('business', 'Business'),
        ('student', 'Student'),
        ('other', 'Other'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='volunteer'
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    ward = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    polling_station = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    profession = models.CharField(
        max_length=20,
        choices=PROFESSION_CHOICES,
        blank=True,
        null=True
    )

    other_profession = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"