# users_app/urls.py
from django.urls import path
from .views import profile_edit, db_profile, complete_social_signup, post_login_redirect, submit_certification_selfie

urlpatterns = [
    path("profile/", db_profile, name="profile"),  # self
    path('profile/edit/', profile_edit, name='profile_edit'),
    path("profile/<str:username>/", db_profile, name="profile_by_username"),  # public
    path('complete-signup/', complete_social_signup, name='complete_social_signup'),
    path('post-login-redirect/', post_login_redirect, name='post_login_redirect'),
    path("verify-profile/", submit_certification_selfie, name="verify_profile"),



]
