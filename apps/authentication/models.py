from django.contrib.auth.models import AbstractUser
from django.db import models

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STAFF = 'STAFF', 'Blood Bank Staff'
    HOSPITAL = 'HOSPITAL', 'Hospital Representative'
    RIDER = 'RIDER', 'Dispatch Rider'

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STAFF)
    phone = models.CharField(max_length=20, blank=True, null=True)