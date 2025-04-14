from django.contrib import admin
from django.urls import include, path

from .models import EventDB

@admin.register(EventDB)
class EventAdmin(admin.ModelAdmin):
    list_display = ('start_datetime', 'organizer', 'price')
