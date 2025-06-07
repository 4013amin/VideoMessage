from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class Users_Save(models.Model):
    username = models.CharField(max_length=200)
    phone = models.IntegerField()
    email = models.EmailField()
    
    def __str__(self):
        return self.username
