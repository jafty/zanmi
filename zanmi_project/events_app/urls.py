from django.urls import path, include
from .views import event_detail

urlpatterns = [
    path('events/<int:event_id>/', event_detail, name='event_detail'),
]
