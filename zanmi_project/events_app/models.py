# events_app/models.py
from django.db import models
from django.conf import settings

class EventDB(models.Model):
    start_datetime = models.DateTimeField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    time = models.CharField(max_length=6, blank=True, null=True)
    activity_type = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True, default='event_images/default.jpg')

    def __str__(self):
        return f"Event by {self.organizer.username} on {self.start_datetime}"
