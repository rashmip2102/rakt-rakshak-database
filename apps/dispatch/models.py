from django.db import models

class DispatchStatus(models.TextChoices):
    PREPARING = 'PREPARING', 'Preparing'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    DELIVERED = 'DELIVERED', 'Delivered'
    FAILED = 'FAILED', 'Failed'

class DispatchOrder(models.Model):
    demand = models.ForeignKey('matching.BloodDemand', on_delete=models.CASCADE, related_name='dispatches')
    source_blood_bank = models.ForeignKey('blood_banks.BloodBank', on_delete=models.CASCADE)
    cold_chain_box_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=DispatchStatus.choices, default=DispatchStatus.PREPARING)
    created_at = models.DateTimeField(auto_now_add=True)

class DispatchUnitReservation(models.Model):
    dispatch_order = models.ForeignKey(DispatchOrder, on_delete=models.CASCADE, related_name='reservations')
    blood_unit = models.OneToOneField('inventory.BloodUnit', on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)
    