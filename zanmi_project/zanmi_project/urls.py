from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from users_app.views import register_view
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', include('events_app.urls')),
    path("admin/", admin.site.urls),
    path("register/", register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users_app/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('users/', include('users_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
