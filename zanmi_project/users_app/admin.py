from django.contrib import admin
from .models import UserProfileDB

@admin.register(UserProfileDB)
class EventAdmin(admin.ModelAdmin):
    list_display = ('user', 'description')

