from __future__ import annotations

from collections import Counter
from typing import Any

from accounts.models import RecommendationHistory, SavedFood


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Normalize text for preference comparison.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


# ============================================================
# USER PREFERENCE PROFILE
# ============================================================

def get_user_preference_profile(user) -> dict:
    """
    Build a lightweight preference profile from:

    - Saved Foods
    - Recommendation History

    This function only collects preference signals.
    It does not change recommendation scores yet.
    """

    profile = {
        "saved_count": 0,
        "history_count": 0,

        "food_types": Counter(),
        "cuisines": Counter(),
        "categories": Counter(),
        "diet_types": Counter(),

        "recommended_food_ids": Counter(),
        "saved_food_ids": Counter(),

        "moods": Counter(),
        "hunger_levels": Counter(),
    }

    if not user or not getattr(
        user,
        "is_authenticated",
        False,
    ):
        return profile

    # ========================================================
    # SAVED FOODS
    # ========================================================

    saved_foods = (
        SavedFood.objects
        .filter(user=user)
        .select_related("food")
    )

    for saved_item in saved_foods:

        food = saved_item.food

        profile["saved_count"] += 1

        profile["saved_food_ids"][
            str(food.food_id)
        ] += 1

        food_type = normalize_text(
            food.food_type
        )

        cuisine = normalize_text(
            food.cuisine
        )

        category = normalize_text(
            food.category
        )

        diet_type = normalize_text(
            food.diet_type
        )

        if food_type:
            profile["food_types"][food_type] += 1

        if cuisine:
            profile["cuisines"][cuisine] += 1

        if category:
            profile["categories"][category] += 1

        if diet_type:
            profile["diet_types"][diet_type] += 1

    # ========================================================
    # RECOMMENDATION HISTORY
    # ========================================================

    history_items = (
        RecommendationHistory.objects
        .filter(user=user)
        .order_by("-created_at")[:20]
    )

    for history in history_items:

        profile["history_count"] += 1

        mood = normalize_text(
            history.mood
        )

        hunger = normalize_text(
            history.hunger
        )

        if mood:
            profile["moods"][mood] += 1

        if hunger:
            profile["hunger_levels"][hunger] += 1

        results = (
            history.results
            if isinstance(
                history.results,
                list,
            )
            else []
        )

        for result in results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            food_id = result.get(
                "food_id"
            )

            if food_id:
                profile[
                    "recommended_food_ids"
                ][str(food_id)] += 1

    return profile

# ============================================================
# PERSONALIZATION SCORE
# ============================================================

def calculate_personalization_score(
    food,
    profile: dict,
) -> float:
    """
    Calculate a small personalization signal.

    This does NOT replace the main recommendation score.

    Signals:
        - Previously saved exact food
        - Preferred food type
        - Preferred cuisine
        - Preferred category
        - Preferred diet type

    Returns:
        0 to 100
    """

    if not profile:
        return 0.0

    food_id = str(
        getattr(
            food,
            "food_id",
            "",
        )
    ).strip()

    food_type = normalize_text(
        getattr(
            food,
            "food_type",
            "",
        )
    )

    cuisine = normalize_text(
        getattr(
            food,
            "cuisine",
            "",
        )
    )

    category = normalize_text(
        getattr(
            food,
            "category",
            "",
        )
    )

    diet_type = normalize_text(
        getattr(
            food,
            "diet_type",
            "",
        )
    )

    score = 0.0

    # ========================================================
    # EXACT SAVED FOOD
    # ========================================================

    if food_id in profile.get(
        "saved_food_ids",
        {},
    ):

        score += 40.0

    # ========================================================
    # FOOD TYPE
    # ========================================================

    food_type_counts = profile.get(
        "food_types",
        {},
    )

    if food_type in food_type_counts:

        count = food_type_counts[
            food_type
        ]

        score += min(
            20.0,
            count * 5.0,
        )

    # ========================================================
    # CUISINE
    # ========================================================

    cuisine_counts = profile.get(
        "cuisines",
        {},
    )

    if cuisine in cuisine_counts:

        count = cuisine_counts[
            cuisine
        ]

        score += min(
            20.0,
            count * 5.0,
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    category_counts = profile.get(
        "categories",
        {},
    )

    if category in category_counts:

        count = category_counts[
            category
        ]

        score += min(
            10.0,
            count * 2.5,
        )

    # ========================================================
    # DIET TYPE
    # ========================================================

    diet_counts = profile.get(
        "diet_types",
        {},
    )

    if diet_type in diet_counts:

        count = diet_counts[
            diet_type
        ]

        score += min(
            10.0,
            count * 2.5,
        )

    return round(
        min(
            100.0,
            score,
        ),
        2,
    )