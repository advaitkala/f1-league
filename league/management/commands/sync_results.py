import httpx
from league.models import Race, Driver, Result
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from django.utils import timezone

class Command(BaseCommand):
    def handle(self, *args, **options):
        race = Race.objects.filter(date_end__lt=timezone.now()).order_by("-date_end").first()
        if race is None:
            raise CommandError("No previous race") 
               
        with httpx.Client() as client:            
            params = {"session_key": race.session_key }
            response = client.get("https://api.openf1.org/v1/session_result", params=params)
            
            if response.status_code == 401:
                raise CommandError("Live F1 Session ongoing. Please retry 30 minutes after end of session")  
            
            for data in response.json():
                driver = Driver.objects.filter(driver_number=data["driver_number"]).first()
                if driver is None:
                    continue
                if data['position'] is None:
                    continue
                Result.objects.update_or_create(
                    race=race,
                    driver=driver,
                    defaults={
                        "position": data["position"],
                        "dnf": data["dnf"],
                        "dns": data["dns"],
                        "dsq": data["dsq"]
                    }
                )    
                
            race.results_fetched = True
            race.save()
            
                