# events_app/forms.py

from django import forms
from .models import ParticipationDB

class ParticipationForm(forms.ModelForm):
    class Meta:
        model = ParticipationDB
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Write a message for the host..."
            }),
        }
        labels = {
            "message": "Your message to the host"
        }
