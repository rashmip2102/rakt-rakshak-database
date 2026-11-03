from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.matching.models import BloodDemand, DemandStatus
from apps.blood_banks.models import Hospital
from django.contrib.gis.geos import Point
from .services import reserve_fefo_inventory

class ReserveInventoryAPIView(APIView):
    def post(self, request):
        blood_bank_id = request.data.get('blood_bank_id')
        blood_group = request.data.get('blood_group', 'A+')
        component_type = request.data.get('component_type', 'PRBC')
        quantity = int(request.data.get('quantity', 1))

        hospital = Hospital.objects.first()
        if not hospital:
            return Response({"error": "No hospital available"}, status=status.HTTP_400_BAD_REQUEST)

        demand = BloodDemand.objects.create(
            hospital=hospital,
            blood_group=blood_group,
            component_type=component_type,
            units_requested=quantity,
            destination_location=hospital.location
        )

        try:
            dispatch_order = reserve_fefo_inventory(
                demand_id=demand.id,
                blood_bank_id=blood_bank_id,
                blood_group=blood_group,
                component_type=component_type,
                quantity=quantity
            )
            return Response({
                "message": "FEFO inventory reserved successfully",
                "dispatch_order_id": dispatch_order.id,
                "cold_chain_box_id": dispatch_order.cold_chain_box_id,
                "status": dispatch_order.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)