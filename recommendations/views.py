from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .services import recommend_foods
from foods.models import Food
from accounts.models import RecommendationHistory

from .similar import get_similar_foods

# ============================================================
# RECOMMENDATION API
# ============================================================

def recommendation_api(request):
    """
    MoodBite Recommendation API.

    Example:
    /api/recommendations/?mood=happy&hunger=hungry&budget=200&diet=vegetarian

    Logged-in users:
        The recommendation session is saved to RecommendationHistory.

    Logged-out users:
        Recommendations still work, but no history is saved.
    """

    # ========================================================
    # GET USER INPUTS
    # ========================================================

    mood = request.GET.get("mood")
    hunger = request.GET.get("hunger")

    # Convert budget from URL string → float
    budget_raw = request.GET.get("budget")

    try:
        budget = float(budget_raw) if budget_raw else None
    except (TypeError, ValueError):
        budget = None

    food_type = request.GET.get("food_type")
    diet_type = request.GET.get("diet")

    # ========================================================
    # RESULT LIMIT
    # ========================================================

    try:
        limit = int(
            request.GET.get("limit", 10)
        )
    except (TypeError, ValueError):
        limit = 10

    # Prevent unreasonable requests
    limit = max(1, min(limit, 50))

    # ========================================================
    # GET RECOMMENDATIONS
    # ========================================================

    results = recommend_foods(
        mood=mood,
        hunger=hunger,
        budget=budget,
        food_type=food_type,
        diet_type=diet_type,
        limit=limit,
        user=request.user,
    )

    # ========================================================
    # BUILD JSON RESPONSE
    # ========================================================

    data = []

    for result in results:

        food = result["food"]

        data.append({
            # -----------------------------------------------
            # BASIC INFORMATION
            # -----------------------------------------------

            "food_id": food.food_id,
            "name": food.food_name,

            "food_type": food.food_type,
            "cuisine": food.cuisine,
            "category": food.category,
            "diet_type": food.diet_type,

            # -----------------------------------------------
            # RECIPE
            # -----------------------------------------------

            "ingredients": food.ingredients,
            "instructions": food.instructions,
            "servings": food.servings,

            "prep_time_min": food.prep_time_min,
            "cook_time_min": food.cook_time_min,
            "total_time_min": food.total_time_min,

            # -----------------------------------------------
            # IMAGE
            # -----------------------------------------------

            "image_url": food.image_url,
            "image_source": food.image_source,

            # -----------------------------------------------
            # NUTRITION
            # -----------------------------------------------

            "nutrition": {
                "calories": food.calories_per_serving,
                "protein_g": food.protein_g,
                "carbs_g": food.carbs_g,
                "fat_g": food.fat_g,
                "fiber_g": food.fiber_g,
                "sugar_g": food.sugar_g,
                "sodium_mg": food.sodium_mg,
            },

            # -----------------------------------------------
            # PRICE
            # -----------------------------------------------

            "price": {
                "min_inr": food.price_min_inr,
                "max_inr": food.price_max_inr,
                "avg_inr": food.price_avg_inr,
            },

            # -----------------------------------------------
            # RECOMMENDATION
            # -----------------------------------------------

            "score": result["score"],

            "breakdown": result.get(
                "breakdown",
                {}
            ),

            "reasons": result.get(
                "reasons",
                []
            ),
        })

    # ========================================================
    # SAVE RECOMMENDATION HISTORY
    #
    # IMPORTANT:
    # Only authenticated users get history records.
    # Logged-out users can still receive recommendations.
    # ========================================================

    if request.user.is_authenticated:

        history_results = []

        for item in data:

            history_results.append({
                "food_id": item["food_id"],
                "name": item["name"],
                "score": item["score"],
                "reasons": item["reasons"],
            })

        RecommendationHistory.objects.create(
            user=request.user,

            mood=mood,
            hunger=hunger,
            budget=budget,
            food_type=food_type,
            diet_type=diet_type,

            results=history_results,
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return JsonResponse({
        "success": True,

        "count": len(data),

        "filters": {
            "mood": mood,
            "hunger": hunger,

            "budget": (
                int(budget)
                if budget is not None
                else None
            ),

            "food_type": food_type,
            "diet": diet_type,
        },

        "results": data,
    })

# ============================================================
# FOOD DETAIL API
# ============================================================

def food_detail_api(request, food_id):
    """
    Return complete information for one food
    along with similar food recommendations.
    """

    food = get_object_or_404(
        Food,
        food_id=food_id,
    )

    # ========================================================
    # GET SIMILAR FOODS
    # ========================================================

    similar_items = get_similar_foods(
        food_id=food_id,
        limit=6,
    )

    similar_foods = []

    for item in similar_items:

        similar_food = item["food"]

        similar_foods.append({
            "food_id": similar_food.food_id,
            "name": similar_food.food_name,

            "food_type": similar_food.food_type,
            "cuisine": similar_food.cuisine,
            "category": similar_food.category,
            "diet_type": similar_food.diet_type,

            "description": similar_food.description,

            "image_url": similar_food.image_url,

            "price": {
                "min_inr": similar_food.price_min_inr,
                "max_inr": similar_food.price_max_inr,
                "avg_inr": similar_food.price_avg_inr,
            },

            "nutrition": {
                "calories": similar_food.calories_per_serving,
                "protein_g": similar_food.protein_g,
                "carbs_g": similar_food.carbs_g,
                "fat_g": similar_food.fat_g,
                "fiber_g": similar_food.fiber_g,
                "sugar_g": similar_food.sugar_g,
                "sodium_mg": similar_food.sodium_mg,
            },

            "similarity": item["similarity"],
        })

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return JsonResponse({
        "success": True,

        "food": {
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

            "image_url": food.image_url,

            "nutrition": {
                "calories": food.calories_per_serving,
                "protein_g": food.protein_g,
                "carbs_g": food.carbs_g,
                "fat_g": food.fat_g,
                "fiber_g": food.fiber_g,
                "sugar_g": food.sugar_g,
                "sodium_mg": food.sodium_mg,
            },

            "price": {
                "min_inr": food.price_min_inr,
                "max_inr": food.price_max_inr,
                "avg_inr": food.price_avg_inr,
            },

            "source": {
                "name": food.recipe_source,
                "url": food.recipe_source_url,
            },
        },

        "similar_foods": similar_foods,
    })