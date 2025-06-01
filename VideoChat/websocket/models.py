

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, unique=True, null=True)
    display_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.URLField(blank=True)

    def __str__(self):
        return self.username
