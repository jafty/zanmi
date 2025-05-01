# users_app/urls.py
from django.urls import path
from .views import profile_edit, profile, complete_social_signup, post_login_redirect

urlpatterns = [
    path("profile/", profile, name="profile"),  # self
    path('profile/edit/', profile_edit, name='profile_edit'),
    path("profile/<str:username>/", profile, name="profile_by_username"),  # public
    path('complete-signup/', complete_social_signup, name='complete_social_signup'),
    path('post-login-redirect/', post_login_redirect, name='post_login_redirect'),


]
