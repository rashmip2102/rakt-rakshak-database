from django.db import transaction
from django.utils import timezone
from apps.inventory.models import BloodUnit, UnitStatus
from apps.dispatch.models import DispatchOrder, DispatchUnitReservation

@transaction.atomic
def reserve_fefo_inventory(demand_id, blood_bank_id, blood_group, component_type, quantity):
    """
    Executes optimistic-concurrency-safe inventory allocation using FEFO ordering 
    and SELECT ... FOR UPDATE SKIP LOCKED.
    """
    units = list(
        BloodUnit.objects.select_for_update(skip_locked=True)
        .filter(
            blood_bank_id=blood_bank_id,
            blood_group=blood_group,
            component_type=component_type,
            status=UnitStatus.AVAILABLE,
            expiry_date__gt=timezone.now()
        )
        .order_by('expiry_date')[:quantity]
    )

    if len(units) < quantity:
        raise ValueError(f"Concurrency lock: Requested {quantity} units, but only {len(units)} available for allocation.")

    dispatch_order = DispatchOrder.objects.create(
        demand_id=demand_id,
        source_blood_bank_id=blood_bank_id,
        cold_chain_box_id=f"BOX-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    )

    reservations = []
    for unit in units:
        unit.status = UnitStatus.RESERVED
        unit.save(update_fields=['status'])
        reservations.append(
            DispatchUnitReservation(dispatch_order=dispatch_order, blood_unit=unit)
        )

    DispatchUnitReservation.objects.bulk_create(reservations)
    return dispatch_order