from django.contrib import admin
from django.urls import include, path

from apps.core.views import health_check
from apps.pages.views import home, dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("health/", health_check, name="health"),
    path("dashboard/", dashboard, name="dashboard"),
    path("", home, name="home"),
]
