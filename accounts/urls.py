from django.urls import path

from . import views

from .saved_api import (
    saved_foods_api,
    saved_food_check_api,
    save_food_api,
    remove_food_api,
)
from .feedback_api import (
    feedback_check_api,
    feedback_api,
    remove_feedback_api,
    feedback_list_api,
)
from .view_tracking_api import (
    record_food_view_api,
)

urlpatterns = [

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "register/",
        views.register_view,
        name="register",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),


    # ========================================================
    # PROFILE
    # ========================================================

    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),


    # ========================================================
    # RECOMMENDATION HISTORY
    # ========================================================

    path(
        "history/",
        views.history_view,
        name="history",
    ),

    path(
        "api/history/",
        views.history_api,
        name="history_api",
    ),

    path(
        "api/history/clear/",
        views.clear_history_api,
        name="clear_history_api",
    ),


    # ========================================================
    # SAVED FOODS
    # ========================================================

    path(
        "api/saved-foods/",
        saved_foods_api,
        name="saved_foods_api",
    ),

    path(
        "api/saved-foods/<str:food_id>/",
        saved_food_check_api,
        name="saved_food_check_api",
    ),

    path(
        "api/saved-foods/<str:food_id>/save/",
        save_food_api,
        name="save_food_api",
    ),

    path(
        "api/saved-foods/<str:food_id>/remove/",
        remove_food_api,
        name="remove_food_api",
    ),

    path(
    "api/preferences/",
    views.preferences_api,
    name="preferences_api",
    ),

    path(
        "api/preferences/update/",
        views.update_preferences_api,
        name="update_preferences_api",
    ),

    path(
    "preferences/",
    views.preferences_view,
    name="preferences",
    ),

        path(
        "api/feedback/",
        feedback_list_api,
        name="feedback_list_api",
    ),

    path(
        "api/feedback/<str:food_id>/",
        feedback_check_api,
        name="feedback_check_api",
    ),

    path(
        "api/feedback/<str:food_id>/save/",
        feedback_api,
        name="feedback_api",
    ),

    path(
        "api/feedback/<str:food_id>/remove/",
        remove_feedback_api,
        name="remove_feedback_api",
    ),

    path(
    "api/food-views/<str:food_id>/",
    record_food_view_api,
    name="record_food_view_api",
    ),
]