from django import forms
from aeroraker.models import City


class TaskForm(forms.Form):
    roundtrip = forms.BooleanField(required=False, initial=True)
    origin = forms.ChoiceField(
        choices=[(city.id, city.name) for city in City.objects.all()]
    )
    destination = forms.ChoiceField(
        choices=[(city.id, city.name) for city in City.objects.all()]
    )
    search_date_start = forms.DateField()
    search_date_end = forms.DateField()
