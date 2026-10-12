from django.urls import path

from .views import (
    home,
    food_detail,
    saved_foods,
)


urlpatterns = [
    path(
        "",
        home,
        name="home",
    ),

    path(
        "food/<str:food_id>/",
        food_detail,
        name="food_detail",
    ),

    path(
        "saved/",
        saved_foods,
        name="saved_foods",
    ),
]