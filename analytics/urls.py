from django.urls import path

from .views import (
    analytics_api,
    analytics_dashboard,
)


urlpatterns = [
    path(
        "",
        analytics_dashboard,
        name="analytics_dashboard",
    ),

    path(
        "api/",
        analytics_api,
        name="analytics_api",
    ),
]