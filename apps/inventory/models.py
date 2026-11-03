from django.db import models

class BloodGroup(models.TextChoices):
    A_POS = 'A+', 'A Positive'
    A_NEG = 'A-', 'A Negative'
    B_POS = 'B+', 'B Positive'
    B_NEG = 'B-', 'B Negative'
    AB_POS = 'AB+', 'AB Positive'
    AB_NEG = 'AB-', 'AB Negative'
    O_POS = 'O+', 'O Positive'
    O_NEG = 'O-', 'O Negative'

class BloodComponent(models.TextChoices):
    PRBC = 'PRBC', 'Packed Red Blood Cells'
    FFP = 'FFP', 'Fresh Frozen Plasma'
    PLATELETS = 'PLATELETS', 'Platelets'
    WHOLE = 'WHOLE', 'Whole Blood'

class UnitStatus(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    RESERVED = 'RESERVED', 'Reserved'
    IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
    USED = 'USED', 'Used'
    EXPIRED = 'EXPIRED', 'Expired'

class BloodUnit(models.Model):
    unit_number = models.CharField(max_length=100, unique=True, db_index=True)
    blood_bank = models.ForeignKey('blood_banks.BloodBank', on_delete=models.CASCADE, related_name='units')
    blood_group = models.CharField(max_length=4, choices=BloodGroup.choices, db_index=True)
    component_type = models.CharField(max_length=20, choices=BloodComponent.choices, db_index=True)
    volume_ml = models.IntegerField(default=450)
    collected_at = models.DateTimeField()
    expiry_date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=UnitStatus.choices, default=UnitStatus.AVAILABLE, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['blood_bank', 'blood_group', 'component_type', 'status', 'expiry_date'], name='idx_fefo_lookup'),
        ]