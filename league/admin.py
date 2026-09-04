from django.contrib import admin
from .models import Race, Driver, Result, Prediction
# Register your models here.
admin.site.register(Race)
admin.site.register(Driver)
admin.site.register(Result)
admin.site.register(Prediction)
