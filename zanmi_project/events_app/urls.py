from django.urls import path, include
from .views import event_detail, join_event, manage_participation, notifications_view, featured_event, landing, stripe_webhook, stripe_success
from django.shortcuts import redirect



def home_redirect(request):
    return redirect("featured_event")  # Remplace 1 par l’ID de ton "main event"


urlpatterns = [
    path('', landing, name='landing'),  # Page d'accueil
    path("notifications/", notifications_view, name="notifications"),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path("events/<int:event_id>/join/", join_event, name="join_event"),
    path("events/<int:event_id>/manage/", manage_participation, name="manage_participation"),
    path('featured_event/', featured_event, name='featured_event'),
    path("stripe_webhook/", stripe_webhook, name="stripe_webhook"),
    path("stripe_success/", stripe_success, name="stripe_success"),
    path("stripe_cancel/", stripe_cancel, name="stripe_cancel"),

]
