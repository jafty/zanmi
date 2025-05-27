# events_app/models.py
from django.db import models
from django.conf import settings

class EventDB(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_datetime = models.DateTimeField()
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    time = models.CharField(max_length=6, blank=True, null=True)
    activity_type = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return f"Event by {self.organizer.username} on {self.start_datetime}"


class ParticipationDB(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey('EventDB', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')])
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ('user', 'event')


class NotificationDB(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_notifications")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_notifications", null=True, blank=True)
    message = models.TextField()
    event = models.ForeignKey(EventDB, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class AnnouncementDB(models.Model):
    event = models.ForeignKey(EventDB, on_delete=models.CASCADE)
    content = models.TextField()
    is_host_message = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

