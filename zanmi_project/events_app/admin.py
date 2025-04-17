from django.contrib import admin
from .models import EventDB, ParticipationDB

@admin.register(EventDB)
class EventAdmin(admin.ModelAdmin):
    list_display = ('start_datetime', 'organizer', 'price')

@admin.register(ParticipationDB)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'message')
