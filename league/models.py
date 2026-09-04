from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

# Create your models here.

class Driver(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200)
    name_acronym = models.CharField(max_length=4)
    driver_number = models.IntegerField()
    driver_team = models.CharField(max_length=200)
    headshot_url = models.URLField()
    team_colour = models.CharField(max_length=20)
    
    def __str__(self):
        return self.full_name
    
class Race(models.Model):
    country_name = models.CharField(max_length=200)
    circuit_name = models.CharField(max_length=200)
    flag_url = models.URLField()
    session_key = models.IntegerField()
    meeting_key = models.IntegerField()
    circuit_short_name = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    is_cancelled = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    results_fetched = models.BooleanField(default=False)
    
    @property
    def lock_time(self):
        return self.date_start - timedelta(hours=2)

    def __str__(self):
        return f"{self.circuit_short_name}, {self.date_start.year}"
        
class Result(models.Model):
    meeting_key = models.ForeignKey(Race, on_delete=models.CASCADE)
    driver_name = models.ForeignKey(Driver, on_delete=models.PROTECT)
    position = models.IntegerField()
    dnf = models.BooleanField(default=False)
    dns = models.BooleanField(default=False)
    dsq = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    p1 = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="p1_picks")
    p2 = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="p2_picks")
    p3 = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="p3_picks")
    final_score = models.IntegerField(null=True)
    submission_datetime = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "race"], name="one_prediction_per_race")
        ]
    
    
    