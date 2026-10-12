from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from foods.models import Food
from .models import (
    SavedFood,
    UserInteraction,
)


# ============================================================
# SAVED FOODS LIST
# ============================================================

@login_required
@require_http_methods(["GET"])
def saved_foods_api(request):

    saved_items = (
        SavedFood.objects
        .filter(user=request.user)
        .select_related("food")
        .order_by("-created_at")
    )

    foods = []

    for item in saved_items:

        food = item.food

        foods.append({
            "food_id": food.food_id,
            "name": food.food_name,
            "food_type": food.food_type,
            "cuisine": food.cuisine,
            "category": food.category,
            "diet_type": food.diet_type,

            "description": food.description,

            "ingredients": food.ingredients,
            "instructions": food.instructions,

            "servings": food.servings,

            "prep_time_min": food.prep_time_min,
            "cook_time_min": food.cook_time_min,
            "total_time_min": food.total_time_min,

            "region": food.region,
            "country": food.country,

            "image_url": food.image_url,
            "image_source": food.image_source,

            "price": {
                "min_inr": food.price_min_inr,
                "max_inr": food.price_max_inr,
                "avg_inr": food.price_avg_inr,
            },

            "nutrition": {
                "calories": food.calories_per_serving,
                "protein_g": food.protein_g,
                "carbs_g": food.carbs_g,
                "fat_g": food.fat_g,
                "fiber_g": food.fiber_g,
                "sugar_g": food.sugar_g,
                "sodium_mg": food.sodium_mg,
            },

            "saved_at": item.created_at.isoformat(),
        })

    return JsonResponse({
        "success": True,
        "count": len(foods),
        "foods": foods,
    })


# ============================================================
# CHECK ONE FOOD
# ============================================================

@login_required
@require_http_methods(["GET"])
def saved_food_check_api(request, food_id):

    exists = SavedFood.objects.filter(
        user=request.user,
        food_id=food_id,
    ).exists()

    return JsonResponse({
        "success": True,
        "saved": exists,
        "food_id": food_id,
    })


# ============================================================
# SAVE ONE FOOD
# ============================================================

@login_required
@require_http_methods(["POST"])
def save_food_api(request, food_id):

    try:
        food = Food.objects.get(
            food_id=food_id
        )

    except Food.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Food not found.",
            },
            status=404,
        )

    saved_food, created = SavedFood.objects.get_or_create(
        user=request.user,
        food=food,
    )
    if created:
        UserInteraction.objects.create(
        user=request.user,
        food=food,
        interaction_type="save",
    )

    return JsonResponse({
        "success": True,
        "saved": True,
        "created": created,
        "food_id": food.food_id,
    })


# ============================================================
# REMOVE ONE FOOD
# ============================================================

@login_required
@require_http_methods(["POST", "DELETE"])
def remove_food_api(request, food_id):

    deleted_count, _ = SavedFood.objects.filter(
        user=request.user,
        food_id=food_id,
    ).delete()
    if deleted_count > 0:
        UserInteraction.objects.create(
            user=request.user,
            food_id=food_id,
            interaction_type="unsave",
    )

    return JsonResponse({
        "success": True,
        "saved": False,
        "removed": deleted_count > 0,
        "food_id": food_id,
    })