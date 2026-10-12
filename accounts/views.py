from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from foods.models import Food

from .models import (
    SavedFood,
    RecommendationHistory,
    UserPreference,
)
from .forms import RegisterForm

# ============================================================
# REGISTER
# ============================================================


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")

    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )

# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
            )

            next_url = request.GET.get(
                "next"
            )

            if next_url:
                return redirect(next_url)

            return redirect("/")

    else:

        form = AuthenticationForm()

    return render(
        request,
        "registration/login.html",
        {
            "form": form,
        },
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect("/")


# ============================================================
# PROFILE
# ============================================================

@login_required
def profile_view(request):

    saved_food_count = (
        SavedFood.objects
        .filter(
            user=request.user,
        )
        .count()
    )

    recommendation_history_count = (
        RecommendationHistory.objects
        .filter(
            user=request.user,
        )
        .count()
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": request.user,
            "saved_food_count": saved_food_count,
            "recommendation_history_count": (
                recommendation_history_count
            ),
        },
    )


# ============================================================
# RECOMMENDATION HISTORY PAGE
# ============================================================

@login_required
def history_view(request):

    history = (
        RecommendationHistory.objects
        .filter(
            user=request.user,
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "accounts/history.html",
        {
            "history": history,
        },
    )


# ============================================================
# RECOMMENDATION HISTORY API
# ============================================================

@login_required
@require_GET
def history_api(request):

    history_items = (
        RecommendationHistory.objects
        .filter(
            user=request.user,
        )
        .order_by("-created_at")
    )

    results = []

    for item in history_items:

        results.append(
            {
                "id": item.id,

                "mood": item.mood,

                "hunger": item.hunger,

                "budget": item.budget,

                "food_type": item.food_type,

                "diet_type": item.diet_type,

                "results": item.results,

                "created_at": (
                    item.created_at.isoformat()
                ),
            }
        )

    return JsonResponse(
        {
            "success": True,

            "count": len(results),

            "history": results,
        }
    )


# ============================================================
# CLEAR RECOMMENDATION HISTORY
# ============================================================

@login_required
@require_POST
def clear_history_api(request):

    deleted_count, _ = (
        RecommendationHistory.objects
        .filter(
            user=request.user,
        )
        .delete()
    )

    return JsonResponse(
        {
            "success": True,

            "deleted": deleted_count,

            "message": (
                "Recommendation history cleared."
            ),
        }
    )


# ============================================================
# SAVED FOODS API
# ============================================================

@login_required
@require_GET
def saved_foods_api(request):

    saved_foods = (
        SavedFood.objects
        .filter(
            user=request.user,
        )
        .select_related("food")
        .order_by("-created_at")
    )

    results = []

    for saved in saved_foods:

        food = saved.food

        results.append(
            {
                "food_id": food.food_id,

                "name": food.food_name,

                "food_type": food.food_type,

                "cuisine": food.cuisine,

                "category": food.category,

                "diet_type": food.diet_type,

                "description": food.description,

                "image_url": food.image_url,

                "price": {
                    "min_inr": food.price_min_inr,
                    "max_inr": food.price_max_inr,
                    "avg_inr": food.price_avg_inr,
                },

                "nutrition": {
                    "calories": (
                        food.calories_per_serving
                    ),

                    "protein_g": (
                        food.protein_g
                    ),

                    "carbs_g": (
                        food.carbs_g
                    ),

                    "fat_g": (
                        food.fat_g
                    ),

                    "fiber_g": (
                        food.fiber_g
                    ),
                },

                "saved_at": (
                    saved.created_at.isoformat()
                ),
            }
        )

    return JsonResponse(
        {
            "success": True,

            "count": len(results),

            "foods": results,
        }
    )


# ============================================================
# SAVE FOOD
# ============================================================

@login_required
@require_POST
def save_food_api(request, food_id):

    try:

        food = Food.objects.get(
            food_id=food_id,
        )

    except Food.DoesNotExist:

        return JsonResponse(
            {
                "success": False,

                "message": "Food not found.",
            },
            status=404,
        )

    saved_food, created = (
        SavedFood.objects.get_or_create(
            user=request.user,
            food=food,
        )
    )

    return JsonResponse(
        {
            "success": True,

            "saved": True,

            "created": created,

            "food_id": food.food_id,
        }
    )


# ============================================================
# REMOVE SAVED FOOD
# ============================================================

@login_required
@require_POST
def remove_saved_food_api(
    request,
    food_id,
):

    deleted, _ = (
        SavedFood.objects
        .filter(
            user=request.user,
            food_id=food_id,
        )
        .delete()
    )

    return JsonResponse(
        {
            "success": True,

            "saved": False,

            "deleted": deleted > 0,

            "food_id": food_id,
        }
    )


# ============================================================
# CHECK SAVED STATUS
# ============================================================

@login_required
@require_GET
def saved_food_status_api(
    request,
    food_id,
):

    saved = (
        SavedFood.objects
        .filter(
            user=request.user,
            food_id=food_id,
        )
        .exists()
    )

    return JsonResponse(
        {
            "success": True,

            "saved": saved,

            "food_id": food_id,
        }
    )

# USER PREFERENCES API
@login_required
@require_GET
def preferences_api(request):
    """
    Return the authenticated user's saved food preferences.
    """

    preferences, _ = UserPreference.objects.get_or_create(
        user=request.user
    )

    return JsonResponse({
        "success": True,
        "preferences": {
            "preferred_food_type": preferences.preferred_food_type,
            "preferred_diet_type": preferences.preferred_diet_type,
            "preferred_cuisine": preferences.preferred_cuisine,
            "preferred_budget": preferences.preferred_budget,
        },
    })


@login_required
@require_POST
def update_preferences_api(request):
    """
    Update the authenticated user's food preferences.
    """

    preferences, _ = UserPreference.objects.get_or_create(
        user=request.user
    )

    preferences.preferred_food_type = (
        request.POST.get(
            "preferred_food_type",
            ""
        ).strip()
        or None
    )

    preferences.preferred_diet_type = (
        request.POST.get(
            "preferred_diet_type",
            ""
        ).strip()
        or None
    )

    preferences.preferred_cuisine = (
        request.POST.get(
            "preferred_cuisine",
            ""
        ).strip()
        or None
    )

    budget_raw = request.POST.get(
        "preferred_budget",
        ""
    ).strip()

    try:
        preferences.preferred_budget = (
            float(budget_raw)
            if budget_raw
            else None
        )
    except (TypeError, ValueError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid budget.",
            },
            status=400,
        )

    preferences.save()

    return JsonResponse({
        "success": True,
        "message": "Preferences updated successfully.",
        "preferences": {
            "preferred_food_type": preferences.preferred_food_type,
            "preferred_diet_type": preferences.preferred_diet_type,
            "preferred_cuisine": preferences.preferred_cuisine,
            "preferred_budget": preferences.preferred_budget,
        },
    })
# PREFERENCES PAGE
@login_required
def preferences_view(request):
    return render(
        request,
        "accounts/preferences.html",
    )
@login_required
def profile_view(request):

    saved_food_count = (
        SavedFood.objects
        .filter(
            user=request.user,
        )
        .count()
    )

    recommendation_history_count = (
        RecommendationHistory.objects
        .filter(
            user=request.user,
        )
        .count()
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": request.user,
            "saved_food_count": saved_food_count,
            "recommendation_history_count": (
                recommendation_history_count
            ),
        },
    )