from django.core.management.base import BaseCommand
from accounts.models import County, Constituency, Ward, PollingStation


class Command(BaseCommand):
    help = "Seed Laikipia County data safely (no duplicates)"

    def handle(self, *args, **kwargs):

        # ================= CLEAN DUPLICATES =================
        County.objects.filter(name__icontains="Laikipia").delete()

        # ================= COUNTY =================
        county = County.objects.create(name="Laikipia")

        self.stdout.write(self.style.SUCCESS(f"Created County: {county.name}"))

        # ================= CONSTITUENCIES =================
        constituencies_data = [
            "Laikipia East",
            "Laikipia West",
            "Laikipia North"
        ]

        for c_name in constituencies_data:

            constituency = Constituency.objects.create(
                name=c_name,
                county=county
            )

            self.stdout.write(f"Constituency: {constituency.name}")

            # ================= WARDS =================
            wards_data = [
                "Central Ward",
                "North Ward",
                "South Ward"
            ]

            for w_name in wards_data:

                ward = Ward.objects.create(
                    name=f"{w_name} - {c_name}",
                    constituency=constituency
                )

                self.stdout.write(f"  Ward: {ward.name}")

                # ================= POLLING STATIONS =================
                polling_data = [
                    "Primary School",
                    "Chief Office",
                    "Market Center"
                ]

                for p_name in polling_data:

                    PollingStation.objects.create(
                        name=f"{p_name} - {ward.name}",
                        ward=ward
                    )

                    self.stdout.write(f"    Polling: {p_name}")

        self.stdout.write(self.style.SUCCESS("✔ Laikipia data seeded successfully"))