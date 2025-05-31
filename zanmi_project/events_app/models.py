# events_app/models.py
from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

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

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.endswith(".webp"):
            self.image = self.compress_and_convert_image(self.image)
        super().save(*args, **kwargs)

    def compress_and_convert_image(self, uploaded_image, max_width=1600, quality=80):
        img = Image.open(uploaded_image)
        img = img.convert("RGB")  # pour éviter les problèmes avec les PNGs

        if img.width > max_width:
            ratio = max_width / float(img.width)
            height = int((float(img.height) * float(ratio)))
            img = img.resize((max_width, height), Image.ANTIALIAS)

        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=quality, optimize=True)
        new_filename = uploaded_image.name.rsplit(".", 1)[0] + ".webp"
        return ContentFile(buffer.getvalue(), name=new_filename)


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

