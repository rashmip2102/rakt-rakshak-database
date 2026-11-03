from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from apps.blood_banks.models import BloodBank
from apps.inventory.models import BloodUnit, UnitStatus

COMPATIBILITY_MAP = {
    'O-': ['O-'],
    'O+': ['O-', 'O+'],
    'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
}

class SpatialMatchAPIView(APIView):
    def get(self, request):
        try:
            lat = float(request.query_params.get('lat', 28.6315))
            lon = float(request.query_params.get('lon', 77.2167))
            req_group = request.query_params.get('blood_group', 'A+')
            component = request.query_params.get('component_type', 'PRBC')
            radius_km = float(request.query_params.get('radius_km', 30))
        except ValueError:
            return Response({"error": "Invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)

        target_point = Point(lon, lat, srid=4326)
        compatible_groups = COMPATIBILITY_MAP.get(req_group, [req_group])

        # PostGIS ST_Distance calculation
        nearby_banks = BloodBank.objects.filter(
            is_active=True,
            location__distance_lte=(target_point, D(km=radius_km))
        ).annotate(
            distance=Distance('location', target_point)
        ).order_by('distance')

        results = []
        for bank in nearby_banks:
            matching_units = BloodUnit.objects.filter(
                blood_bank=bank,
                blood_group__in=compatible_groups,
                component_type=component,
                status=UnitStatus.AVAILABLE
            ).order_by('expiry_date') # FEFO Priority

            if matching_units.exists():
                results.append({
                    "blood_bank_id": bank.id,
                    "blood_bank_name": bank.name,
                    "address": bank.address,
                    "distance_km": round(bank.distance.km, 2),
                    "available_count": matching_units.count(),
                    "next_expiring_unit": matching_units.first().expiry_date,
                })

        return Response({"matches": results})