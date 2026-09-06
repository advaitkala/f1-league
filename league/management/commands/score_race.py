from league.models import Race, Driver, Result
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from django.utils import timezone
from league.scoring import calc_score
from django.db import transaction

class Command(BaseCommand):
    def handle(self, *args, **options):
        race = Race.objects.filter(date_end__lt=timezone.now()).order_by("-date_end").first()
        
        if race.results_fetched is False:
            self.stdout.write("Results not synced yet.")
            return 
        
        result = Result.objects.filter(race=race).order_by("position")[:3]
        if len(result) < 3:
            self.stdout.write("Fewer than three finishers.")
            return    
        
        actuals = []
        for r in result:
            actuals.append(r.driver)
            
        with transaction.atomic(): # stops crashes if an error occurs. Prevents other prediction scores to not be made
            for prediction in race.prediction_set.all():
                picks = [prediction.p1, prediction.p2, prediction.p3]
                prediction.final_score = calc_score(picks, actuals)
                prediction.save()
                self.stdout.write(f"{prediction.user}: {prediction.final_score}")

        
            
        
            
                