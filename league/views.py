from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Race, Prediction
from .forms import PredictionForm


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


@login_required
def predict(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    existing = Prediction.objects.filter(user=request.user, race=race).first()

    if timezone.now() >= race.lock_time:
        return render(request, "prediction/locked.html", {"race": race})

    if request.method == "POST":
        form = PredictionForm(request.POST, race=race, instance=existing)
        if form.is_valid():
            prediction = form.save(commit=False)
            prediction.user = request.user
            prediction.race = race
            prediction.save()
            return redirect("my_prediction", race_id=race.id)
    else:
        form = PredictionForm(race=race, instance=existing)

    return render(request, "prediction/predict.html", {"form": form, "race": race})


class RaceView(generic.ListView):
    template_name = "prediction/race_list.html"
    context_object_name = "all_races_list"
    
    def get_queryset(self):
        return Race.objects.all().order_by("date_start")
    
@login_required
def my_prediction(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    prediction = Prediction.objects.filter(user=request.user, race=race).first()
    return render(request, "prediction/my_prediction.html", {"prediction": prediction, "race": race})