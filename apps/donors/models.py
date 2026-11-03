from django.db import models
from django.conf import settings

class Donor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=4)
    is_available = models.BooleanField(default=True)