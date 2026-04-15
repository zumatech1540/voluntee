from django.contrib.auth.models import AbstractUser
from django.db import models


# COUNTY
class County(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# CONSTITUENCY
class Constituency(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.county.name})"


# WARD
class Ward(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.constituency.name})"


# POLLING STATION
class PollingStation(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} ({self.ward.name})"


# USER
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

    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    constituency = models.ForeignKey(
        Constituency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

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