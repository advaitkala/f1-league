import httpx
from league.models import Race, Driver, RaceEntry
from django.core.management.base import BaseCommand
from datetime import datetime
from django.utils import timezone


class Command(BaseCommand):
    def handle(self, *args, **options):
        with httpx.Client(timeout=30) as client:            
            params = {"year": 2026, "session_name":'Race'}
            response = client.get("https://api.openf1.org/v1/sessions", params=params)
            
            if response.status_code == 401:
                self.stdout.write("Live session in progress, skipping.")
                return

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
            self.stdout.write(self.style.SUCCESS("Races synced."))
                
                
            next_race = Race.objects.filter(date_start__gt=timezone.now()).order_by("date_start").first()
            
            if next_race is None:
                self.stdout.write("No upcoming race.")
                return
            
            params = {"meeting_key": next_race.meeting_key, "session_name":'Practice 2'}
            response = client.get("https://api.openf1.org/v1/sessions", params=params)
            
            sessions = response.json()
            if not sessions:
                params = {"meeting_key": next_race.meeting_key, "session_name":'Sprint'}
                response = client.get("https://api.openf1.org/v1/sessions", params=params)
                sessions = response.json()
            
            if not sessions:
                self.stdout.write("No lineup session found.")
                
            fp2_session_key = response.json()[0]["session_key"]
            
            response = client.get("https://api.openf1.org/v1/drivers", params = {'session_key': fp2_session_key})
            
            for data in response.json():
                driver, _ = Driver.objects.update_or_create(
                    driver_number = data["driver_number"],
                    defaults = {
                        "first_name": data["first_name"],
                        "last_name": data["last_name"],
                        "full_name": data['full_name'],
                        "name_acronym": data["name_acronym"],
                        "headshot_url": data.get('headshot_url')
                    }
                )
                
                RaceEntry.objects.update_or_create(
                    race=next_race,
                    driver = driver,
                    defaults = {
                        "driver_team":data["team_name"],
                        "team_colour":data["team_colour"]
                    }
                )