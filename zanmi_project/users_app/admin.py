from django.contrib import admin
from .models import UserProfileDB


@admin.register(UserProfileDB)
class UserProfileDBAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_certified', 'has_certification_selfie']
    list_filter = ['is_certified' ]
    search_fields = ['user__username']
    ordering = ['-certification_selfie', '-created_at']

    def has_certification_selfie(self, obj):
        return bool(obj.certification_selfie)
    has_certification_selfie.boolean = True  # Affiche une icône ✔️/❌ dans l’admin
    has_certification_selfie.short_description = "Selfie fourni"
