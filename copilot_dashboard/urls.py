from django.urls import path, include

urlpatterns = [
    # All routes are handled by the dashboard app
    path("", include("dashboard.urls")),
]
