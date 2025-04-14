from django import forms

class ParticipationForm(forms.Form):
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Say hi to the host! Let them know why you’d like to join.',
            'rows': 3,
            'class': 'form-control'
        }),
        label="Message (optional)"
    )
