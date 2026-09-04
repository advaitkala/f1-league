import httpx
from league.models import Race, Driver, Result, Prediction
from django.core.management.base import BaseCommand
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        with httpx.Client() as client:            
            params = {"year": 2026, "session_name":'Race'}
            response = client.get("https://api.openf1.org/v1/sessions", params=params)
            
            if response.status_code == 401:
                raise Exception("Live F1 Session ongoing. Please retry 30 minutes after end of session")

            for data in response.json():
                Race.objects.update_or_create(
                    session_key = data["session_key"], 
                    defaults={
                        "country_name": data["country_name"],
                        "circuit_short_name": data["circuit_short_name"],
                        "location": data["location"],
                        "is_cancelled": data["is_cancelled"],
                        "meeting_key": data["meeting_key"],
                        "date_start": datetime.fromisoformat(data["date_start"]),
                        "date_end": datetime.fromisoformat(data["date_end"])
                        
                    }
                )