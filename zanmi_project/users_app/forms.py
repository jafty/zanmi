from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfileDB
from django import forms


class UsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


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
    perfect_outing_description = forms.CharField(
        required=False,
        label="Describe your perfect outing",
        widget=forms.Textarea(attrs={"rows": 3})
    )
    music_preference = forms.CharField(
        required=False,
        label="What kind of music do you enjoy?"
    )
    fun_fact = forms.CharField(
        required=False,
        label="A fun or unexpected fact about you",
        widget=forms.Textarea(attrs={"rows": 2})
    )
    group_size_preference = forms.CharField(required=False, label="Preferred group size")
    dietary_restrictions = forms.CharField(required=False, label="Dietary restrictions")


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # Add new consent fields
    privacy_policy_consent = forms.BooleanField(
        label="I agree to the Privacy Policy",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input me-2'})
    )
    terms_of_service_consent = forms.BooleanField(
        label="I agree to the Terms of Service",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input me-2'})
    )
    event_invitation_consent = forms.BooleanField(
        label="I would like to receive email invitations to events",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input me-2'})
    )

    class Meta:
        model = User
        # Include username, email, password, and password2 in Meta.fields
        fields = ("username", "email", "password1", "password2") # Use 'password' and 'password2'


    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used.")
        return email


class CertificationSelfieForm(forms.ModelForm):
    class Meta:
        model = UserProfileDB
        fields = ['certification_selfie']