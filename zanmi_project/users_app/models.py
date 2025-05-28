from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User as DjangoAuthUser


# Create your models here.
class UserProfileDB(models.Model):
    # Typically, you'd relate it to Django's built-in `User`
    user = models.OneToOneField(
        DjangoAuthUser, on_delete=models.CASCADE, related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True, default='avatars/default.jpg'
    )
    description = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    languages_spoken = models.TextField(blank=True, null=True)
    centers_of_interest = models.TextField(blank=True, null=True)
    event_expectations = models.TextField(blank=True, null=True)
    group_size_preference = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    is_certified = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=now)
    perfect_outing_description = models.TextField(blank=True, null=True)
    music_preference = models.CharField(max_length=100, blank=True, null=True)
    fun_fact = models.TextField(blank=True, null=True)
    # Fields for Privacy Policy Consent
    privacy_policy_consent = models.BooleanField(default=False)
    privacy_policy_consent_date = models.DateTimeField(null=True, blank=True)
    privacy_policy_consent_text = models.TextField(blank=True, null=True) 

    # Fields for Terms of Service Consent
    terms_of_service_consent = models.BooleanField(default=False)
    terms_of_service_consent_date = models.DateTimeField(null=True, blank=True)
    terms_of_service_consent_text = models.TextField(blank=True, null=True) 

    # Fields for Event Invitation Email Consent
    event_invitation_consent = models.BooleanField(default=False)
    event_invitation_consent_date = models.DateTimeField(null=True, blank=True)
    event_invitation_consent_text = models.TextField(blank=True, null=True)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)