from django.db import models
from django.contrib.gis.db import models as gis_models

class DemandStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    FULFILLED = 'FULFILLED', 'Fulfilled'
    CANCELLED = 'CANCELLED', 'Cancelled'

class BloodDemand(models.Model):
    hospital = models.ForeignKey('blood_banks.Hospital', on_delete=models.CASCADE, related_name='demands')
    blood_group = models.CharField(max_length=4)
    component_type = models.CharField(max_length=20)
    units_requested = models.PositiveIntegerField()
    units_allocated = models.PositiveIntegerField(default=0)
    destination_location = gis_models.PointField(srid=4326)
    status = models.CharField(max_length=20, choices=DemandStatus.choices, default=DemandStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)