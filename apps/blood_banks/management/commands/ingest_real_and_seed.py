import random
import requests
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone

from apps.blood_banks.models import BloodBank, Hospital
from apps.inventory.models import BloodUnit, BloodGroup, BloodComponent, UnitStatus

class Command(BaseCommand):
    help = "Pulls real hospitals from OSM via Overpass API and generates FEFO inventory."

    def handle(self, *args, **options):
        self.stdout.write("Fetching real facilities from OpenStreetMap (Overpass API)...")
        
        # Query hospitals in Delhi NCR bounding box
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = """
        [out:json];
        (
          node["amenity"="hospital"](28.5000, 77.1000, 28.7500, 77.3500);
          way["amenity"="hospital"](28.5000, 77.1000, 28.7500, 77.3500);
        );
        out center 15;
        """
        
        try:
            res = requests.post(overpass_url, data={'data': query}, timeout=25)
            data = res.json()
            elements = data.get('elements', [])
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"OSM fetch failed ({e}). Falling back to seed coordinates."))
            elements = []

        banks = []
        if elements:
            for idx, el in enumerate(elements):
                tags = el.get('tags', {})
                name = tags.get('name') or f"Regional Medical Center #{idx+1}"
                lat = el.get('lat') or el.get('center', {}).get('lat')
                lon = el.get('lon') or el.get('center', {}).get('lon')
                
                if lat and lon:
                    bank, _ = BloodBank.objects.update_or_create(
                        license_number=f"LIC-OSM-{el['id']}",
                        defaults={
                            'name': name,
                            'address': tags.get('addr:full', 'New Delhi, India'),
                            'contact_phone': tags.get('phone', '+911123456789'),
                            'location': Point(float(lon), float(lat), srid=4326),
                            'is_active': True
                        }
                    )
                    banks.append(bank)
        
        # Fallback default banks if OSM query returned empty
        if not banks:
            fallback_coords = [
                ("Central Red Cross Blood Bank", 77.2090, 28.6139),
                ("AIIMS Apex Blood Bank", 77.2100, 28.5672),
                ("Max Super Speciality Storage", 77.2197, 28.5284),
            ]
            for name, lon, lat in fallback_coords:
                bank, _ = BloodBank.objects.update_or_create(
                    license_number=f"LIC-{random.randint(10000, 99999)}",
                    defaults={
                        'name': name,
                        'address': 'New Delhi',
                        'contact_phone': '+919876543210',
                        'location': Point(lon, lat, srid=4326),
                        'is_active': True
                    }
                )
                banks.append(bank)

        # Create receiving Hospital
        hospital, _ = Hospital.objects.update_or_create(
            registration_number="HOSP-TRAUMA-01",
            defaults={
                'name': 'Apex Emergency Trauma Center',
                'address': 'Connaught Place, New Delhi',
                'contact_phone': '+911199998888',
                'location': Point(77.2167, 28.6315, srid=4326),
            }
        )

        self.stdout.write(f"Populated {len(banks)} Blood Banks and 1 Hospital.")

        # Seed FEFO Blood Units
        self.stdout.write("Generating FEFO inventory batches with variable shelf-lives...")
        BloodUnit.objects.all().delete()
        
        units = []
        for bank in banks:
            for _ in range(25):
                group = random.choice(list(BloodGroup))
                component = random.choice(list(BloodComponent))
                days_to_expire = random.randint(1, 30) # Random expiry for FEFO ordering testing
                
                collected_at = timezone.now() - timedelta(days=random.randint(1, 15))
                expiry_date = timezone.now() + timedelta(days=days_to_expire)

                units.append(BloodUnit(
                    unit_number=f"BAG-{random.randint(1000000, 9999999)}",
                    blood_bank=bank,
                    blood_group=group,
                    component_type=component,
                    volume_ml=450,
                    collected_at=collected_at,
                    expiry_date=expiry_date,
                    status=UnitStatus.AVAILABLE
                ))
                
        BloodUnit.objects.bulk_create(units)
        self.stdout.write(self.style.SUCCESS(f"Successfully generated {len(units)} FEFO blood units!"))