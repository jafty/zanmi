from django.contrib import admin
from .models import EventDB, ParticipationDB, NotificationDB, AnnouncementDB

@admin.register(EventDB)
class EventAdmin(admin.ModelAdmin):
    list_display = ('start_datetime', 'organizer', 'price')


@admin.register(ParticipationDB)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'message')


@admin.register(NotificationDB)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'event', 'message')

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('event', 'is_host_message', 'created_at')
    list_filter = ('is_host_message',)
    search_fields = ('content',)