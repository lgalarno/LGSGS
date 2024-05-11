from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    country = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return self.username
