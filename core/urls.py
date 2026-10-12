
from django.urls import path

from .views import (
    home,
    food_detail,
    saved_foods,
    about,
)

urlpatterns = [
    path("", home, name="home"),
    path("food/<int:food_id>/", food_detail, name="food_detail"),
    path("saved/", saved_foods, name="saved_foods"),
    path("about/", about, name="about"),
]
