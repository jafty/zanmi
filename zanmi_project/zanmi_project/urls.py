from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users_app.views import register_view
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('events_app.urls')),
    path("admin/", admin.site.urls),
    path('allauth/', include('allauth.urls')),  # Allauth handles login/logout etc.
    path("register/", register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users_app/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('users/', include('users_app.urls')),
    path('cgv/', TemplateView.as_view(template_name="static/cgv.html"), name='cgv'),
    path('cgu/', TemplateView.as_view(template_name="static/cgu.html"), name='cgu'),
    path('mentions-legales/', TemplateView.as_view(template_name="static/legal_mentions.html"), name='mentions_legales'),
    path('confidentialite/', TemplateView.as_view(template_name="static/confidentialite.html"), name='confidentialite'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
