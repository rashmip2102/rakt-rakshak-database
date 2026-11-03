from django.db import models
from django.contrib.gis.db import models as gis_models

class TelemetryLog(models.Model):
    dispatch_order = models.ForeignKey('dispatch.DispatchOrder', on_delete=models.CASCADE, related_name='telemetry')
    current_location = gis_models.PointField(srid=4326)
    temperature_celsius = models.DecimalField(max_digits=5, decimal_places=2)
    is_thermal_breach = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)
    