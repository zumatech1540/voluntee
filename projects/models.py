from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# =========================
# PROJECT MODEL
# =========================
class Project(models.Model):

    STATUS = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=100)

    leader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects_led"
    )

    status = models.CharField(max_length=20, choices=STATUS, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# PROJECT UPDATES
# =========================
class ProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to='updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project.title


# =========================
# GALLERY
# =========================
class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption