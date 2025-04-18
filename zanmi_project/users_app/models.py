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
    activity_preferences = models.TextField(blank=True, null=True)
    group_size_preference = models.CharField(max_length=100, blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    is_certified = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)