from __future__ import annotations

from typing import Any

from foods.models import Food


# ============================================================
# SAFE HELPERS
# ============================================================


def safe_float(
    value: Any,
    default: float | None = None,
) -> float | None:
    """
    Safely convert a value to float.
    """

    if value is None:
        return default

    try:

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return default

            value = value.replace("₹", "")
            value = value.replace(",", "")

        return float(value)

    except (TypeError, ValueError):
        return default


def normalize_text(value: Any) -> str:
    """
    Normalize text for comparison.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def get_field(
    food: Food,
    field: str,
    default: Any = None,
) -> Any:
    """
    Safely read a Food model field.
    """

    try:
        return getattr(
            food,
            field,
            default,
        )

    except Exception:
        return default


# ============================================================
# PRICE
# ============================================================


def get_food_price(
    food: Food,
) -> float | None:
    """
    Get the best available average food price.
    """

    average = safe_float(
        get_field(
            food,
            "price_avg_inr",
        )
    )

    if average is not None:
        return average

    minimum = safe_float(
        get_field(
            food,
            "price_min_inr",
        )
    )

    maximum = safe_float(
        get_field(
            food,
            "price_max_inr",
        )
    )

    if (
        minimum is not None
        and maximum is not None
    ):
        return (
            minimum + maximum
        ) / 2

    if minimum is not None:
        return minimum

    if maximum is not None:
        return maximum

    return None


# ============================================================
# NUMERIC SIMILARITY
# ============================================================


def numeric_similarity(
    value_a: float | None,
    value_b: float | None,
    tolerance: float,
) -> float:
    """
    Return similarity between two numeric values.

    100 = almost identical
    0   = very different
    """

    if (
        value_a is None
        or value_b is None
    ):
        return 0.0

    if tolerance <= 0:
        return 0.0

    difference = abs(
        value_a - value_b
    )

    score = (
        100
        - (
            difference
            / tolerance
            * 100
        )
    )

    return max(
        0.0,
        min(
            100.0,
            score,
        ),
    )


# ============================================================
# FOOD SIMILARITY
# ============================================================


def calculate_food_similarity(
    source_food: Food,
    candidate_food: Food,
) -> float:
    """
    Calculate similarity between two foods.

    Similarity is based on:

    - Food type
    - Cuisine
    - Category
    - Dietary type
    - Price
    - Calories
    - Protein
    """

    # --------------------------------------------------------
    # SAME FOOD
    # --------------------------------------------------------

    source_id = str(
        get_field(
            source_food,
            "food_id",
            "",
        )
    ).strip()

    candidate_id = str(
        get_field(
            candidate_food,
            "food_id",
            "",
        )
    ).strip()

    if (
        source_id
        and candidate_id
        and source_id == candidate_id
    ):
        return -1.0

    # --------------------------------------------------------
    # TEXT FEATURES
    # --------------------------------------------------------

    source_food_type = normalize_text(
        get_field(
            source_food,
            "food_type",
        )
    )

    candidate_food_type = normalize_text(
        get_field(
            candidate_food,
            "food_type",
        )
    )

    source_cuisine = normalize_text(
        get_field(
            source_food,
            "cuisine",
        )
    )

    candidate_cuisine = normalize_text(
        get_field(
            candidate_food,
            "cuisine",
        )
    )

    source_category = normalize_text(
        get_field(
            source_food,
            "category",
        )
    )

    candidate_category = normalize_text(
        get_field(
            candidate_food,
            "category",
        )
    )

    source_diet = normalize_text(
        get_field(
            source_food,
            "diet_type",
        )
    )

    candidate_diet = normalize_text(
        get_field(
            candidate_food,
            "diet_type",
        )
    )

    # --------------------------------------------------------
    # INDIVIDUAL FEATURE SCORES
    # --------------------------------------------------------

    food_type_score = (
        100.0
        if (
            source_food_type
            and candidate_food_type
            and source_food_type
            == candidate_food_type
        )
        else 0.0
    )

    cuisine_score = (
        100.0
        if (
            source_cuisine
            and candidate_cuisine
            and source_cuisine
            == candidate_cuisine
        )
        else 0.0
    )

    category_score = (
        100.0
        if (
            source_category
            and candidate_category
            and source_category
            == candidate_category
        )
        else 0.0
    )

    diet_score = (
        100.0
        if (
            source_diet
            and candidate_diet
            and source_diet
            == candidate_diet
        )
        else 0.0
    )

    # --------------------------------------------------------
    # PRICE SIMILARITY
    # --------------------------------------------------------

    source_price = get_food_price(
        source_food
    )

    candidate_price = get_food_price(
        candidate_food
    )

    if (
        source_price is not None
        and candidate_price is not None
    ):

        price_tolerance = max(
            50.0,
            source_price * 0.75,
        )

        price_score = numeric_similarity(
            source_price,
            candidate_price,
            price_tolerance,
        )

    else:

        price_score = 0.0

    # --------------------------------------------------------
    # CALORIE SIMILARITY
    # --------------------------------------------------------

    source_calories = safe_float(
        get_field(
            source_food,
            "calories_per_serving",
        )
    )

    candidate_calories = safe_float(
        get_field(
            candidate_food,
            "calories_per_serving",
        )
    )

    calorie_score = numeric_similarity(
        source_calories,
        candidate_calories,
        500.0,
    )

    # --------------------------------------------------------
    # PROTEIN SIMILARITY
    # --------------------------------------------------------

    source_protein = safe_float(
        get_field(
            source_food,
            "protein_g",
        )
    )

    candidate_protein = safe_float(
        get_field(
            candidate_food,
            "protein_g",
        )
    )

    protein_score = numeric_similarity(
        source_protein,
        candidate_protein,
        30.0,
    )

    # ========================================================
    # FINAL WEIGHTED SCORE
    # ========================================================

    score = (
        food_type_score * 0.20
        + cuisine_score * 0.20
        + category_score * 0.20
        + diet_score * 0.15
        + price_score * 0.10
        + calorie_score * 0.10
        + protein_score * 0.05
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                score,
            ),
        ),
        2,
    )


# ============================================================
# GET SIMILAR FOODS
# ============================================================


def get_similar_foods(
    food_id: str,
    limit: int = 6,
) -> list[dict]:
    """
    Return the most similar foods for a given food ID.
    """

    # --------------------------------------------------------
    # LIMIT
    # --------------------------------------------------------

    try:
        limit = int(limit)

    except (
        TypeError,
        ValueError,
    ):
        limit = 6

    limit = max(
        1,
        min(
            limit,
            12,
        ),
    )

    # --------------------------------------------------------
    # SOURCE FOOD
    # --------------------------------------------------------

    try:

        source_food = Food.objects.get(
            food_id=food_id
        )

    except Food.DoesNotExist:

        return []

    # --------------------------------------------------------
    # LOAD CANDIDATES
    # --------------------------------------------------------

    candidates = Food.objects.exclude(
        food_id=food_id
    )

    # --------------------------------------------------------
    # CALCULATE SIMILARITY
    # --------------------------------------------------------

    scored_foods = []
    seen_names = set()

    for candidate in candidates:

        similarity = calculate_food_similarity(
            source_food=source_food,
            candidate_food=candidate,
        )

        if similarity < 0:
            continue


        # ========================================================
        # PREVENT DUPLICATE FOOD NAMES
        # ========================================================

        candidate_name = normalize_text(
            get_field(
                candidate,
                "food_name",
                "",
            )
        )

        if candidate_name:

            if candidate_name in seen_names:
                continue

            seen_names.add(
                candidate_name
            )


        scored_foods.append(
            {
                "food": candidate,
                "similarity": similarity,
            }
        )


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    scored_foods.sort(
        key=lambda item: (
            item["similarity"],
            get_food_price(
                item["food"]
            )
            or 0,
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # RETURN TOP RESULTS
    # --------------------------------------------------------

    return scored_foods[:limit]