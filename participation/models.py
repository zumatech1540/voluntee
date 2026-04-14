from django.db import models
from django.conf import settings
from projects.models import Project

User = settings.AUTH_USER_MODEL


class Participation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -> {self.project}"