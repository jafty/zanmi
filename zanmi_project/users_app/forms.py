from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class UserProfileForm(forms.Form):
    avatar = forms.ImageField(required=False, label="Profile picture")
    birth_date = forms.DateField(
        required=False,
        label="Date of birth",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    city = forms.CharField(required=False, label="City")
    country = forms.CharField(required=False, label="Country")
    languages_spoken = forms.CharField(required=False, label="Languages spoken")
    description = forms.CharField(
        required=False,
        label="Short introduction",
        widget=forms.Textarea(attrs={"rows": 3})
    )
    centers_of_interest = forms.CharField(required=False, label="What are you interested in?")

    event_expectations = forms.CharField(
        required=False,
        label="What do you hope to get from these events?",
        widget=forms.Textarea(attrs={"rows": 3})
    )
    activity_preferences = forms.CharField(
        required=False,
        label="Preferred activities",
        widget=forms.Textarea(attrs={"rows": 3})
    )
    group_size_preference = forms.CharField(required=False, label="Preferred group size")
    dietary_restrictions = forms.CharField(required=False, label="Dietary restrictions")


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used.")
        return email