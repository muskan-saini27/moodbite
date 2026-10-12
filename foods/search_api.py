from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Food


def _text(value):
    if value is None:
        return ""

    return str(value).strip()


def _float(value):
    try:
        if value is None or value == "":
            return None

        return float(value)

    except (TypeError, ValueError):
        return None


def _clean_number(value):
    """
    Treat zero nutrition values as missing.

    In our food dataset, 0 can represent unavailable
    nutrition rather than a genuine zero.
    """

    number = _float(value)

    if number is None:
        return None

    if number <= 0:
        return None

    return number


def _normalize_name(name):
    """
    Used only for search-result deduplication.

    Keeps the original food name for display.
    """

    name = _text(name).lower()

    name = " ".join(
        name.split()
    )

    return name


def _serialize_food(food):
    calories = _clean_number(
        food.calories_per_serving
    )

    protein = _clean_number(
        food.protein_g
    )

    carbs = _clean_number(
        food.carbs_g
    )

    fat = _clean_number(
        food.fat_g
    )

    fiber = _clean_number(
        food.fiber_g
    )

    return {
        "food_id": food.food_id,

        "name": food.food_name,

        "food_type": food.food_type,

        "cuisine": food.cuisine,

        "category": food.category,

        "diet_type": food.diet_type,

        "description": food.description,

        "region": food.region,

        "country": food.country,

        "image_url": food.image_url,

        "price": {
            "min_inr": food.price_min_inr,
            "max_inr": food.price_max_inr,
            "avg_inr": food.price_avg_inr,
        },

        "nutrition": {
            "calories": calories,
            "protein_g": protein,
            "carbs_g": carbs,
            "fat_g": fat,
            "fiber_g": fiber,
        },
    }


@require_GET
def food_search_api(request):
    """
    MoodBite food discovery/search API.

    Supported parameters:

        q
        food_type
        diet
        cuisine
        category
        max_price
        min_protein
        max_calories
        limit
    """

    query = _text(
        request.GET.get("q")
    )

    food_type = _text(
        request.GET.get("food_type")
    )

    diet = _text(
        request.GET.get("diet")
    )

    cuisine = _text(
        request.GET.get("cuisine")
    )

    category = _text(
        request.GET.get("category")
    )

    max_price = _float(
        request.GET.get("max_price")
    )

    min_protein = _float(
        request.GET.get("min_protein")
    )

    max_calories = _float(
        request.GET.get("max_calories")
    )

    try:

        limit = int(
            request.GET.get(
                "limit",
                24,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 24

    limit = max(
        1,
        min(
            limit,
            50,
        ),
    )

    foods = Food.objects.all()

    # ========================================================
    # SEARCH
    # ========================================================

    if query:

        foods = foods.filter(
            food_name__icontains=query
        )

    # ========================================================
    # FOOD TYPE
    # ========================================================

    if food_type:

        foods = foods.filter(
            food_type__icontains=food_type
        )

    # ========================================================
    # DIET
    # ========================================================

    if diet:

        diet_normalized = diet.lower()

        if diet_normalized in {
            "vegetarian",
            "veg",
        }:

            foods = foods.filter(
                diet_type__in=[
                    "Vegetarian",
                    "Vegan",
                    "vegetarian",
                    "vegan",
                    "Veg",
                    "veg",
                ]
            )

        elif diet_normalized == "vegan":

            foods = foods.filter(
                diet_type__iexact="Vegan"
            )

        elif diet_normalized in {
            "non-vegetarian",
            "non vegetarian",
            "nonvegetarian",
        }:

            foods = foods.exclude(
                diet_type__in=[
                    "Vegetarian",
                    "Vegan",
                    "vegetarian",
                    "vegan",
                    "Veg",
                    "veg",
                ]
            )

        else:

            foods = foods.filter(
                diet_type__icontains=diet
            )

    # ========================================================
    # CUISINE
    # ========================================================

    if cuisine:

        foods = foods.filter(
            cuisine__icontains=cuisine
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    if category:

        foods = foods.filter(
            category__icontains=category
        )

    # ========================================================
    # PRICE
    # ========================================================

    if max_price is not None:

        foods = foods.filter(
            price_avg_inr__lte=max_price
        )

    # ========================================================
    # PROTEIN
    # ========================================================

    if min_protein is not None:

        foods = foods.filter(
            protein_g__gte=min_protein
        )

    # ========================================================
    # CALORIES
    # ========================================================

    if max_calories is not None:

        foods = foods.filter(
            calories_per_serving__lte=max_calories
        )

    # ========================================================
    # ORDER
    # ========================================================

    foods = foods.order_by(
        "food_name"
    )

    # ========================================================
    # RESULT DEDUPLICATION
    # ========================================================

    results = []

    seen_names = set()

    for food in foods:

        normalized_name = _normalize_name(
            food.food_name
        )

        if not normalized_name:
            continue

        if normalized_name in seen_names:
            continue

        seen_names.add(
            normalized_name
        )

        results.append(
            _serialize_food(food)
        )

        if len(results) >= limit:
            break

    # ========================================================
    # RESPONSE
    # ========================================================

    return JsonResponse(
        {
            "success": True,

            "count": len(results),

            "filters": {
                "q": query,
                "food_type": food_type,
                "diet": diet,
                "cuisine": cuisine,
                "category": category,
                "max_price": max_price,
                "min_protein": min_protein,
                "max_calories": max_calories,
            },

            "results": results,
        }
    )