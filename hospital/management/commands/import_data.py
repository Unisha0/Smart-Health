import pandas as pd
from django.core.management.base import BaseCommand
from hospital.models import Hospitaldb  # Correct import here

class Command(BaseCommand):
    help = "Import hospitals from Excel file"

    def handle(self, *args, **kwargs):
        file_path = "D:\\project\\shea_project_1.xlsx"  # Update path

        df = pd.read_excel(file_path, header=0)  # Ensure correct header
        df.columns = df.columns.str.strip()  # Remove extra spaces

        print("Columns in Excel:", df.columns)  # Debugging step

        for _, row in df.iterrows():
            hospital, created = Hospitaldb.objects.get_or_create(
                name=row["NAME"],
                defaults={
                    "speciality": row["SPECIALITY"],
                    "contact": row["CONTACT"],
                    "address": row["ADDRESS"],
                    "latitude": row["LATITUDE"],
                    "longitude": row["LONGITUDE"],
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added {hospital.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Skipped {hospital.name} (already exists)"))
