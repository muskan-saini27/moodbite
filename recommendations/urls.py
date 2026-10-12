from django.urls import path

from .views import (
    recommendation_api,
    food_detail_api,
)

from foods.search_api import (
    food_search_api,
)


urlpatterns = [

    path(
        "recommendations/",
        recommendation_api,
        name="recommendation-api",
    ),

    path(
        "foods/search/",
        food_search_api,
        name="food-search-api",
    ),

    path(
        "foods/<str:food_id>/",
        food_detail_api,
        name="food-detail-api",
    ),
]