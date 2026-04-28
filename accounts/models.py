from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


# ================= LOCATION MODELS =================

class County(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Constituency(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.county.name})"


class Ward(models.Model):
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.constituency.name})"


class PollingStation(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} ({self.ward.name})"


# ================= USER MODEL =================

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

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='volunteer')
    phone = models.CharField(max_length=20, blank=True, null=True)

    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True)
    polling_station = models.ForeignKey(PollingStation, on_delete=models.SET_NULL, null=True, blank=True)

    profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, blank=True, null=True)
    other_profession = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username


# ================= EVENT MODEL =================

class Event(models.Model):

    APPROVAL_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()

    image = models.ImageField(upload_to='events/', blank=True, null=True)

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending'
    )

    created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="created_events",
    null=True,
    blank=True
)
    

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="joined_events"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_closed(self):
        return self.date < timezone.now().date()

    def __str__(self):
        return self.title

# ================= Donation =================

class Donation(models.Model):

    DONATION_TYPE = (
        ('money', 'Money'),
        ('food', 'Food'),
        ('clothes', 'Clothes'),
        ('books', 'Books'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.donation_type}"



# ================= NOTIFICATIONS =================

class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message