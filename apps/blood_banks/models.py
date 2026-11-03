from django.contrib.gis.db import models as gis_models
from django.db import models

class BloodBank(models.Model):
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.license_number})"

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    location = gis_models.PointField(srid=4326, spatial_index=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name