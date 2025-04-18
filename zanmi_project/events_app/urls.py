from django.urls import path, include
from .views import event_detail, join_event, manage_participation, notifications_view, featured_event
from django.shortcuts import redirect



def home_redirect(request):
    return redirect("featured_event")  # Remplace 1 par l’ID de ton "main event"


urlpatterns = [
    path('', home_redirect, name="home"),
    path("notifications/", notifications_view, name="notifications"),
    path('events/<int:event_id>/', event_detail, name='event_detail'),
    path("events/<int:event_id>/join/", join_event, name="join_event"),
    path("events/<int:event_id>/manage/", manage_participation, name="manage_participation"),
    path('featured_event/', featured_event, name='featured_event'),

]
