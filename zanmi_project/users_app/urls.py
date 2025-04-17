# users_app/urls.py
from django.urls import path
from .views import profile_edit, profile

urlpatterns = [
    path("profile/", profile, name="profile"),  # self
    path('profile/edit/', profile_edit, name='profile_edit'),
    path("profile/<str:username>/", profile, name="profile_by_username"),  # public

]
