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

    # ================= VOLUNTEER MANAGEMENT =================
    VOLUNTEER_ROLE_CHOICES = [
        ("mobilizer", "Mobilizer"),
        ("ward_coordinator", "Ward Coordinator"),
        ("polling_agent", "Polling Agent"),
        ("data_collector", "Data Collector"),
        ("observer", "Observer"),
    ]

    volunteer_role = models.CharField(
        max_length=50,
        choices=VOLUNTEER_ROLE_CHOICES,
        blank=True,
        null=True
    )

    VOLUNTEER_STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("suspended", "Suspended"),
    ]

    volunteer_status = models.CharField(
        max_length=20,
        choices=VOLUNTEER_STATUS,
        default="active"
    )

    activity_score = models.IntegerField(default=0)
    events_attended = models.IntegerField(default=0)

    # ================= 🔥 FIX ADDED (ROLE SAFETY) =================

    @property
    def safe_role(self):
        """
        Always return valid role (prevents crashes)
        """
        return self.role or "volunteer"

    def save(self, *args, **kwargs):
        """
        Force default role if missing (prevents bad DB values)
        """
        if not self.role:
            self.role = "volunteer"
        super().save(*args, **kwargs)

    # ================= STRING =================
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

# ================= Attendance =================
class Attendance(models.Model):

    ROLE_TYPE = (
        ("volunteer", "Volunteer"),
        ("voter", "Voter"),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    voter = models.ForeignKey(
        "Voter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    role_type = models.CharField(max_length=20, choices=ROLE_TYPE)

    status = models.CharField(max_length=20, default="present")

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ PUT IT HERE 👇
    def clean(self):
        if not self.user and not self.voter:
            raise ValidationError("Either user or voter must be set")

        if self.user and self.voter:
            raise ValidationError("Cannot assign both user and voter")

    def __str__(self):
        return f"{self.event.title} - {self.role_type}"

# ================= VOTER DATABASE =================

class Voter(models.Model):

    SUPPORT_STATUS = (
        ("supporter", "Supporter"),
        ("undecided", "Undecided"),
        ("opponent", "Opponent"),
    )

    GENDER = (
        ("male", "Male"),
        ("female", "Female"),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    gender = models.CharField(max_length=10, choices=GENDER, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voters_county"
    )

    constituency = models.ForeignKey(
        Constituency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voters_constituency"
    )

    ward = models.ForeignKey(
        Ward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voters_ward"
    )

    polling_station = models.ForeignKey(
        PollingStation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voters_station"
    )

    support_status = models.CharField(
        max_length=20,
        choices=SUPPORT_STATUS,
        default="undecided"
    )

    notes = models.TextField(blank=True, null=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="voters_added"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ================= TASK MODEL =================

class Task(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Assigned volunteer
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_assigned'
    )

    # Leader who created the task
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks_created'
    )

    # Optional: link task to a specific event
    event = models.ForeignKey(
        'Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Task status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Priority level
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Deadline
    due_date = models.DateField(null=True, blank=True)

    # Notes or feedback after completion
    feedback = models.TextField(blank=True, null=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} → {self.assigned_to}"

        
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
# ================= ContactMessage =================
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)