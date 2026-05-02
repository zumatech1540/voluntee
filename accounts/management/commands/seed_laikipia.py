from django.core.management.base import BaseCommand
from accounts.models import County, Constituency, Ward, PollingStation


class Command(BaseCommand):
    help = "Seed Laikipia County location data"

    def handle(self, *args, **kwargs):

        # ================= COUNTY =================
        county, _ = County.objects.get_or_create(name="Laikipia")

        # ================= CONSTITUENCIES =================
        east, _ = Constituency.objects.get_or_create(name="Laikipia East", county=county)
        north, _ = Constituency.objects.get_or_create(name="Laikipia North", county=county)
        west, _ = Constituency.objects.get_or_create(name="Laikipia West", county=county)

        # ================= EAST WARDS =================
        nanyuki, _ = Ward.objects.get_or_create(name="Nanyuki", constituency=east)
        tigithi, _ = Ward.objects.get_or_create(name="Tigithi", constituency=east)
        thome, _ = Ward.objects.get_or_create(name="Thome", constituency=east)

        # ================= NORTH WARDS =================
        doldol, _ = Ward.objects.get_or_create(name="Doldol", constituency=north)
        mairungi, _ = Ward.objects.get_or_create(name="Mairungi", constituency=north)
        sosian, _ = Ward.objects.get_or_create(name="Sosian", constituency=north)

        # ================= WEST WARDS =================
        rumuruti, _ = Ward.objects.get_or_create(name="Rumuruti", constituency=west)
        sipili, _ = Ward.objects.get_or_create(name="Sipili", constituency=west)
        sabukia, _ = Ward.objects.get_or_create(name="Sabukia", constituency=west)

        # ================= POLLING STATIONS =================

        # EAST
        PollingStation.objects.get_or_create(name="Nanyuki Primary School", ward=nanyuki)
        PollingStation.objects.get_or_create(name="Nanyuki Secondary School", ward=nanyuki)
        PollingStation.objects.get_or_create(name="Likii Market Center", ward=nanyuki)

        PollingStation.objects.get_or_create(name="Tigithi Market", ward=tigithi)
        PollingStation.objects.get_or_create(name="Kiamariga Centre", ward=tigithi)

        PollingStation.objects.get_or_create(name="Thome Community Hall", ward=thome)

        # NORTH
        PollingStation.objects.get_or_create(name="Doldol Town Hall", ward=doldol)
        PollingStation.objects.get_or_create(name="Olmoran Center", ward=doldol)

        PollingStation.objects.get_or_create(name="Mairungi Primary", ward=mairungi)
        PollingStation.objects.get_or_create(name="Sosian Ranch Gate", ward=sosian)

        # WEST
        PollingStation.objects.get_or_create(name="Rumuruti Market", ward=rumuruti)
        PollingStation.objects.get_or_create(name="Rumuruti Stadium", ward=rumuruti)

        PollingStation.objects.get_or_create(name="Sipili Market Center", ward=sipili)
        PollingStation.objects.get_or_create(name="Sabukia Trading Center", ward=sabukia)

        self.stdout.write(self.style.SUCCESS("✅ Laikipia location data seeded successfully!"))