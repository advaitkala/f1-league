from django import forms
from .models import Prediction, Driver, Race
from django.utils import timezone

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['p1', 'p2', 'p3']
        
        
    def __init__(self,*args, race=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.race = race
        
        entered = Driver.objects.filter(raceentry__race=race)
        for name in self.fields:
            self.fields[name].queryset = entered
            
    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("p1")
        p2 = cleaned_data.get("p2")
        p3 = cleaned_data.get("p3")
        if p1 and p2 and p3:
            if len({p1, p2, p3}) < 3:
                raise forms.ValidationError("Pick three different drivers.")
        if timezone.now() >= self.race.lock_time:
            raise forms.ValidationError("Predictions cannot be sent in")
        return cleaned_data 
                
                   
    
