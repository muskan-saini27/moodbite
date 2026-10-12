from __future__ import annotations

from typing import Any
from collections import Counter

from foods.models import Food

from accounts.models import RecommendationHistory, SavedFood, UserInteraction



# ============================================================

# SAFE HELPERS

# ============================================================



def safe_float(

    value: Any,

    default: float | None = None,

) -> float | None:

    """Safely convert a value to float."""



    if value is None:

        return default



    try:

        if isinstance(value, str):

            value = value.strip()



            if not value:

                return default



            value = value.replace("₹", "")

            value = value.replace(",", "")

            value = value.strip()



        return float(value)



    except (TypeError, ValueError):

        return default





def safe_int(

    value: Any,

    default: int | None = None,

) -> int | None:

    """Safely convert a value to integer."""

    number = safe_float(value)

    if number is None:

        return default

    return int(number)

def normalize_text(value: Any) -> str:

    """Normalize text for comparisons."""

    if value is None:

        return ""

    return str(value).strip().lower()

def get_field(

    food: Food,

    field: str,

    default: Any = None,

) -> Any:

    """Safely get a Food model field."""

    try:

        return getattr(

            food,

            field,

            default,

        )

    except Exception:

        return default

def get_score(

    food: Food,

    field: str,

) -> float:

    """

    Get a score field and normalize it

    to the 0–100 range.

    """
    value = safe_float(

        get_field(

            food,

            field,

        )

    )



    if value is None:

        return 0.0



    return max(

        0.0,

        min(

            100.0,

            value,

        ),

    )

# ============================================================

# MOOD TARGETS

# ============================================================



MOOD_TARGETS = {



    "happy": {

        "comfort": 70,

        "energy": 70,

        "indulgence": 60,

        "freshness": 55,

        "adventure": 55,

        "spice": 50,

    },



    "sad": {

        "comfort": 90,

        "energy": 45,

        "indulgence": 75,

        "freshness": 40,

        "adventure": 35,

        "spice": 50,

    },



    "stressed": {

        "comfort": 85,

        "energy": 45,

        "indulgence": 70,

        "freshness": 55,

        "adventure": 30,

        "spice": 35,

    },



    "tired": {

        "comfort": 75,

        "energy": 80,

        "indulgence": 55,

        "freshness": 45,

        "adventure": 30,

        "spice": 45,

    },



    "energetic": {

        "comfort": 45,

        "energy": 90,

        "indulgence": 40,

        "freshness": 75,

        "adventure": 65,

        "spice": 55,

    },



    "excited": {

        "comfort": 45,

        "energy": 85,

        "indulgence": 60,

        "freshness": 65,

        "adventure": 85,

        "spice": 65,

    },



    "calm": {

        "comfort": 75,

        "energy": 45,

        "indulgence": 40,

        "freshness": 75,

        "adventure": 35,

        "spice": 30,

    },



    "bored": {

        "comfort": 45,

        "energy": 70,

        "indulgence": 65,

        "freshness": 55,

        "adventure": 90,

        "spice": 70,

    },

}





# ============================================================

# HUNGER TARGETS

# ============================================================



HUNGER_TARGETS = {



    "just a little": {

        "satiety": 30,

        "energy": 35,

    },



    "little": {

        "satiety": 30,

        "energy": 35,

    },



    "low": {

        "satiety": 30,

        "energy": 35,

    },



    "moderately hungry": {

        "satiety": 55,

        "energy": 55,

    },



    "moderate": {

        "satiety": 55,

        "energy": 55,

    },



    "hungry": {

        "satiety": 75,

        "energy": 70,

    },



    "very hungry": {

        "satiety": 95,

        "energy": 85,

    },



    "very_hungry": {

        "satiety": 95,

        "energy": 85,

    },

}





# ============================================================

# PRICE

# ============================================================



def get_food_price(

    food: Food,

) -> float | None:

    """

    Get the best available food price.



    Priority:



    1. price_avg_inr

    2. midpoint of min/max

    3. price_min_inr

    4. price_max_inr

    """



    avg_price = safe_float(

        get_field(

            food,

            "price_avg_inr",

        )

    )



    if avg_price is not None:

        return avg_price



    min_price = safe_float(

        get_field(

            food,

            "price_min_inr",

        )

    )



    max_price = safe_float(

        get_field(

            food,

            "price_max_inr",

        )

    )



    if (

        min_price is not None

        and max_price is not None

    ):

        return (

            min_price + max_price

        ) / 2



    if min_price is not None:

        return min_price



    if max_price is not None:

        return max_price



    return None





# ============================================================

# HARD BUDGET FILTER

# ============================================================



def matches_budget(

    food: Food,

    budget: float | int | str | None,

) -> bool:

    """

    HARD budget ceiling.



    Example:



    Budget ₹100:



        ₹50   -> YES

        ₹80   -> YES

        ₹100  -> YES

        ₹125  -> NO



    Budget ₹1000:



        ₹100  -> YES

        ₹500  -> YES

        ₹800  -> YES

        ₹1000 -> YES

        ₹1100 -> NO

    """



    budget_value = safe_float(

        budget

    )



    if budget_value is None:

        return True



    if budget_value < 0:

        return False



    food_price = get_food_price(

        food

    )



    # If we don't know the price,

    # don't include it when a budget

    # has been explicitly selected.

    if food_price is None:

        return False



    return food_price <= budget_value





# ============================================================

# DIET FILTER

# ============================================================



def matches_diet(

    food: Food,

    requested_diet: str | None,

) -> bool:

    """Match vegetarian, vegan or non-vegetarian."""



    requested = normalize_text(

        requested_diet

    )



    if not requested:

        return True



    actual = normalize_text(

        get_field(

            food,

            "diet_type",

            "",

        )

    )



    if requested in {

        "vegetarian",

        "veg",

    }:



        return actual in {

            "vegetarian",

            "vegan",

            "veg",

        }



    if requested == "vegan":

        return actual == "vegan"



    if requested in {

        "non-vegetarian",

        "non vegetarian",

        "nonvegetarian",

        "non_vegetarian",

        "non-veg",

        "non veg",

    }:



        return actual not in {

            "",

            "vegetarian",

            "vegan",

            "veg",

        }



    return True





# ============================================================

# FOOD TYPE FILTER

# ============================================================



def matches_food_type(

    food: Food,

    requested_food_type: str | None,

) -> bool:

    """Match Indian or International food."""



    requested = normalize_text(

        requested_food_type

    )



    if not requested:

        return True



    actual = normalize_text(

        get_field(

            food,

            "food_type",

            "",

        )

    )



    if not actual:

        return True



    if requested == "indian":

        return "indian" in actual



    if requested == "international":

        return "international" in actual



    return True





# ============================================================

# MOOD SCORE

# ============================================================



def calculate_mood_score(

    food: Food,

    mood: str | None,

) -> float:

    """Calculate how well a food matches the user's mood."""



    mood_name = normalize_text(

        mood

    )



    if not mood_name:

        return 50.0



    target = MOOD_TARGETS.get(

        mood_name

    )



    if target is None:

        return 50.0



    fields = {

        "comfort": "comfort_score",

        "energy": "energy_score",

        "indulgence": "indulgence_score",

        "freshness": "freshness_score",

        "adventure": "adventure_score",

        "spice": "spice_score",

    }



    matches = []



    for target_name, field_name in fields.items():



        actual = get_score(

            food,

            field_name,

        )



        expected = target[

            target_name

        ]



        similarity = (

            100.0

            - abs(

                actual - expected

            )

        )



        similarity = max(

            0.0,

            min(

                100.0,

                similarity,

            ),

        )



        matches.append(

            similarity

        )



    if not matches:

        return 50.0



    return sum(matches) / len(

        matches

    )





# ============================================================

# HUNGER SCORE

# ============================================================



def calculate_hunger_score(

    food: Food,

    hunger: str | None,

) -> float:

    """Calculate how well a food matches hunger level."""



    hunger_name = normalize_text(

        hunger

    )



    if not hunger_name:

        return 50.0



    target = HUNGER_TARGETS.get(

        hunger_name

    )



    if target is None:

        return 50.0



    satiety = get_score(

        food,

        "satiety_score",

    )



    energy = get_score(

        food,

        "energy_score",

    )



    satiety_match = (

        100.0

        - abs(

            satiety

            - target["satiety"]

        )

    )



    energy_match = (

        100.0

        - abs(

            energy

            - target["energy"]

        )

    )



    satiety_match = max(

        0.0,

        min(

            100.0,

            satiety_match,

        ),

    )



    energy_match = max(

        0.0,

        min(

            100.0,

            energy_match,

        ),

    )



    return (

        satiety_match * 0.65

        + energy_match * 0.35

    )





# ============================================================

# IMPROVED BUDGET SCORE

# ============================================================



def calculate_budget_score(

    food: Food,

    budget: float | int | str | None,

) -> float:

    """

    Calculate budget relevance.



    IMPORTANT:



    This is NOT the hard budget filter.



    matches_budget() handles the hard ceiling.



    This function decides how strongly the price

    should influence ranking.



    --------------------------------------------------------

    Example: budget ₹1000

    --------------------------------------------------------



    ₹50   -> very low relevance

    ₹100  -> low relevance

    ₹300  -> moderate

    ₹500  -> good

    ₹700  -> excellent

    ₹800  -> excellent

    ₹900  -> very good

    ₹1000 -> good



    We intentionally don't force the user to spend

    100% of the budget.



    The sweet spot is around 70–80% of the budget.



    --------------------------------------------------------

    Example: budget ₹100

    --------------------------------------------------------



    ₹50  -> reasonable

    ₹80  -> excellent

    ₹100 -> very good



    This prevents the budget score from behaving

    strangely for small budgets.

    """



    budget_value = safe_float(

        budget

    )



    if budget_value is None:

        return 50.0



    if budget_value <= 0:

        return 0.0



    food_price = get_food_price(

        food

    )



    if food_price is None:

        return 0.0



    # --------------------------------------------------------

    # HARD SAFETY

    # --------------------------------------------------------



    if food_price > budget_value:

        return 0.0



    # --------------------------------------------------------

    # PRICE / BUDGET RATIO

    # --------------------------------------------------------



    ratio = (

        food_price

        / budget_value

    )



    ratio = max(

        0.0,

        min(

            1.0,

            ratio,

        ),

    )



    # --------------------------------------------------------

    # IDEAL BUDGET UTILIZATION

    # --------------------------------------------------------

    #

    # For small budgets, being close to the maximum

    # affordable price makes sense.

    #

    # For larger budgets, we don't want to force

    # spending the entire budget.

    # --------------------------------------------------------



    if budget_value <= 200:

        ideal_ratio = 0.80

    else:

        ideal_ratio = 0.75



    # --------------------------------------------------------

    # DISTANCE FROM IDEAL

    # --------------------------------------------------------



    distance = abs(

        ratio - ideal_ratio

    )



    # 160 controls how strongly cheap foods

    # are penalized.

    score = (

        100.0

        - (

            distance * 160.0

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

# NUTRITION SCORE

# ============================================================



def calculate_nutrition_score(

    food: Food,

) -> float:

    """Calculate general nutrition quality."""



    calories = safe_float(

        get_field(

            food,

            "calories_per_serving",

        )

    )



    protein = safe_float(

        get_field(

            food,

            "protein_g",

        )

    )



    fiber = safe_float(

        get_field(

            food,

            "fiber_g",

        )

    )



    scores = []



    # --------------------------------------------------------

    # CALORIES

    # --------------------------------------------------------



    if calories is not None:



        calorie_score = (

            100.0

            - abs(

                calories - 500

            ) / 5

        )



        calorie_score = max(

            0.0,

            min(

                100.0,

                calorie_score,

            ),

        )



        scores.append(

            calorie_score

        )



    # --------------------------------------------------------

    # PROTEIN

    # --------------------------------------------------------



    if protein is not None:



        protein_score = min(

            100.0,

            max(

                0.0,

                protein * 5,

            ),

        )



        scores.append(

            protein_score

        )



    # --------------------------------------------------------

    # FIBER

    # --------------------------------------------------------



    if fiber is not None:



        fiber_score = min(

            100.0,

            max(

                0.0,

                fiber * 8,

            ),

        )



        scores.append(

            fiber_score

        )



    if not scores:

        return 50.0



    return sum(scores) / len(

        scores

    )





# ============================================================

# QUALITY SCORE

# ============================================================



def calculate_quality_score(

    food: Food,

) -> float:

    """Calculate dataset/content quality."""



    score = 100.0



    image_url = get_field(

        food,

        "image_url",

        "",

    )



    if not image_url:

        score -= 15



    ingredients = get_field(

        food,

        "ingredients",

        "",

    )



    if not ingredients:

        score -= 15



    instructions = get_field(

        food,

        "instructions",

        "",

    )



    if not instructions:

        score -= 15



    if get_food_price(food) is None:

        score -= 15



    nutrition_fields = [

        "calories_per_serving",

        "protein_g",

        "carbs_g",

        "fat_g",

    ]



    missing = 0



    for field in nutrition_fields:



        if safe_float(

            get_field(

                food,

                field,

            )

        ) is None:



            missing += 1



    score -= (

        missing * 5

    )



    return max(

        0.0,

        min(

            100.0,

            score,

        ),

    )





# ============================================================

# FINAL SCORE

# ============================================================



def calculate_score(

    food: Food,

    mood: str | None = None,

    hunger: str | None = None,

    budget: float | int | str | None = None,

):

    """

    Calculate final recommendation score.



    Current weights:



        Mood       30%

        Hunger     25%

        Budget     25%

        Nutrition  10%

        Quality    10%



    Budget is important enough to affect ranking,

    but mood and hunger still have higher combined

    importance.

    """



    mood_score = calculate_mood_score(

        food,

        mood,

    )



    hunger_score = calculate_hunger_score(

        food,

        hunger,

    )



    budget_score = calculate_budget_score(

        food,

        budget,

    )



    nutrition_score = calculate_nutrition_score(

        food

    )



    quality_score = calculate_quality_score(

        food

    )



    # --------------------------------------------------------

    # FINAL WEIGHTED SCORE

    # --------------------------------------------------------



    final_score = (

        mood_score * 0.30

        + hunger_score * 0.25

        + budget_score * 0.25

        + nutrition_score * 0.10

        + quality_score * 0.10

    )



    final_score = max(

        0.0,

        min(

            100.0,

            final_score,

        ),

    )



    breakdown = {

        "mood": round(

            mood_score,

            2,

        ),



        "hunger": round(

            hunger_score,

            2,

        ),



        "budget": round(

            budget_score,

            2,

        ),



        "nutrition": round(

            nutrition_score,

            2,

        ),



        "quality": round(

            quality_score,

            2,

        ),

    }



    return (

        round(

            final_score,

            2,

        ),

        breakdown,

    )





# ============================================================

# EXPLANATIONS

# ============================================================


def build_explanations(
    food: Food,
    mood: str | None = None,
    hunger: str | None = None,
    budget: float | int | str | None = None,
    breakdown: dict | None = None,
    personalization_score: float = 0.0,
):

    """Build human-readable recommendation reasons."""



    reasons = []



    if breakdown is None:

        breakdown = {}



    mood_name = normalize_text(

        mood

    )



    hunger_name = normalize_text(

        hunger

    )



    budget_value = safe_float(

        budget

    )



    # --------------------------------------------------------

    # MOOD

    # --------------------------------------------------------



    if (

        mood_name

        and breakdown.get(

            "mood",

            0,

        ) >= 70

    ):



        pretty_mood = (

            mood_name

            .replace(

                "_",

                " ",

            )

            .title()

        )



        reasons.append(

            f"Strong match for your "

            f"{pretty_mood.lower()} mood"

        )



    # --------------------------------------------------------

    # HUNGER

    # --------------------------------------------------------



    if (

        hunger_name

        and breakdown.get(

            "hunger",

            0,

        ) >= 65

    ):



        pretty_hunger = (

            hunger_name

            .replace(

                "_",

                " ",

            )

            .lower()

        )



        reasons.append(

            f"Good fit for being "

            f"{pretty_hunger}"

        )



    # --------------------------------------------------------

    # BUDGET

    # --------------------------------------------------------



    food_price = get_food_price(

        food

    )



    if (

        budget_value is not None

        and food_price is not None

        and food_price <= budget_value

    ):



        reasons.append(

            f"Fits your "

            f"₹{safe_int(budget_value)} "

            f"budget"

        )



    # --------------------------------------------------------

    # DIET

    # --------------------------------------------------------



    diet = normalize_text(

        get_field(

            food,

            "diet_type",

            "",

        )

    )



    if diet == "vegan":



        reasons.append(

            "Vegan option"

        )



    elif diet in {

        "vegetarian",

        "veg",

    }:



        reasons.append(

            "Vegetarian option"

        )



    elif diet:



        reasons.append(

            "Non-vegetarian option"

        )



    # --------------------------------------------------------

    # PROTEIN

    # --------------------------------------------------------



    protein = safe_float(

        get_field(

            food,

            "protein_g",

        )

    )



    if (

        protein is not None

        and protein >= 15

    ):



        reasons.append(

            "Good protein content"

        )

    # --------------------------------------------------------
    # PERSONALIZATION
    # --------------------------------------------------------

    if personalization_score >= 40:

        reasons.append(
            "Matches your past food preferences"
        )

    elif personalization_score >= 20:

        reasons.append(
            "Similar to foods you often enjoy"
        )

    # --------------------------------------------------------

    # FALLBACK

    # --------------------------------------------------------



    if not reasons:



        reasons.append(

            "Good overall match"

        )



    return reasons[:4]





# ============================================================

# ============================================================
# USER PERSONALIZATION
# ============================================================


def _get_user_personalization_profile(user):
    """Build a lightweight profile from saved foods and history."""

    empty_profile = {
        "saved_food_ids": set(),
        "liked_food_ids": set(),
        "disliked_food_ids": set(),
        "cuisines": Counter(),
        "food_types": Counter(),
        "diet_types": Counter(),
        "categories": Counter(),
        "history_food_ids": Counter(),
    }

    if user is None or not getattr(user, "is_authenticated", False):
        return empty_profile

    try:
        saved_items = (
            SavedFood.objects
            .filter(user=user)
            .select_related("food")
            .order_by("-created_at")[:100]
        )

        for item in saved_items:
            food = item.food
            food_id = str(get_field(food, "food_id", "")).strip()
            cuisine = normalize_text(get_field(food, "cuisine", ""))
            food_type = normalize_text(get_field(food, "food_type", ""))
            diet_type = normalize_text(get_field(food, "diet_type", ""))
            category = normalize_text(get_field(food, "category", ""))

            if food_id:
                empty_profile["saved_food_ids"].add(food_id)
            if cuisine:
                empty_profile["cuisines"][cuisine] += 1
            if food_type:
                empty_profile["food_types"][food_type] += 1
            if diet_type:
                empty_profile["diet_types"][diet_type] += 1
            if category:
                empty_profile["categories"][category] += 1
    except Exception:
        pass

    # Use the most recent like/dislike per food so an older
    # interaction does not override the user's latest feedback.
    try:
        interactions = (
            UserInteraction.objects
            .filter(user=user, interaction_type__in=["like", "dislike"])
            .select_related("food")
            .order_by("-created_at")[:300]
        )
        seen_food_pks = set()

        for interaction in interactions:
            food = interaction.food
            if food is None or food.pk in seen_food_pks:
                continue
            seen_food_pks.add(food.pk)

            food_id = str(get_field(food, "food_id", "")).strip()
            if not food_id:
                continue

            interaction_type = normalize_text(
                get_field(interaction, "interaction_type", "")
            )
            if interaction_type == "like":
                empty_profile["liked_food_ids"].add(food_id)
            elif interaction_type == "dislike":
                empty_profile["disliked_food_ids"].add(food_id)
    except Exception:
        # Feedback is optional; recommendation still works if unavailable.
        pass

    try:
        history_items = (
            RecommendationHistory.objects
            .filter(user=user)
            .order_by("-created_at")[:30]
        )

        for item in history_items:
            for result in item.results or []:
                if isinstance(result, dict):
                    food_id = str(result.get("food_id", "")).strip()
                    if food_id:
                        empty_profile["history_food_ids"][food_id] += 1
    except Exception:
        pass

    return empty_profile


def calculate_personalization_score(food: Food, profile: dict | None = None) -> float:
    """Return a 0-100 personal preference signal without filtering foods."""

    if not profile:
        return 0.0

    food_id = str(get_field(food, "food_id", "")).strip()
    cuisine = normalize_text(get_field(food, "cuisine", ""))
    food_type = normalize_text(get_field(food, "food_type", ""))
    diet_type = normalize_text(get_field(food, "diet_type", ""))
    category = normalize_text(get_field(food, "category", ""))

    signals = []

    if food_id and food_id in profile.get("saved_food_ids", set()):
        signals.append((100.0, 0.45))

    if food_id and food_id in profile.get("liked_food_ids", set()):
        signals.append((100.0, 0.45))

    for value, key, weight in (
        (cuisine, "cuisines", 0.20),
        (food_type, "food_types", 0.10),
        (diet_type, "diet_types", 0.10),
        (category, "categories", 0.05),
    ):
        counts = profile.get(key, Counter())
        if value and counts:
            total = sum(counts.values())
            signals.append(((counts.get(value, 0) / total) * 100.0, weight))

    if not signals:
        return 0.0

    weight_total = sum(weight for _, weight in signals)
    if weight_total <= 0:
        return 0.0

    score = sum(value * weight for value, weight in signals) / weight_total
    return round(max(0.0, min(100.0, score)), 2)

# ============================================================
# RESULT DIVERSITY
# ============================================================


def _normalize_food_name_for_diversity(
    value: Any,
) -> str:
    """
    Normalize food names so duplicate recipe names
    are treated as one recommendation.
    """

    text = normalize_text(
        value
    )

    return " ".join(
        text.split()
    )


def diversify_results(
    results: list[dict],
    limit: int,
) -> list[dict]:
    """
    Return the highest-scoring results without repeating
    the same food ID or normalized food name.
    """

    if not results or limit <= 0:
        return []

    selected = []
    seen_names = set()
    seen_ids = set()

    for item in results:
        food = item.get("food")

        if food is None:
            continue

        food_id = str(
            get_field(food, "food_id", "") or ""
        ).strip().lower()

        name = _normalize_food_name_for_diversity(
            get_field(food, "food_name", "")
        )

        # Skip records with a repeated ID.
        if food_id and food_id in seen_ids:
            continue

        # Skip records with a repeated normalized name.
        if name and name in seen_names:
            continue

        if food_id:
            seen_ids.add(food_id)

        if name:
            seen_names.add(name)

        selected.append(item)

        if len(selected) >= limit:
            break

    return selected

   
# ============================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================


def recommend_foods(
    mood: str | None = None,
    hunger: str | None = None,
    budget: float | int | str | None = None,
    diet_type: str | None = None,
    food_type: str | None = None,
    limit: int = 10,
    user=None,
):
    """
    Main MoodBite recommendation engine.

    Pipeline:

        ALL FOODS
            ↓
        DIET FILTER
            ↓
        FOOD TYPE FILTER
            ↓
        HARD BUDGET FILTER
            ↓
        BASE SCORE
            ↓
        PERSONALIZATION SCORE
            ↓
        PERSONALIZED FINAL SCORE
            ↓
        SORT
            ↓
        TOP RESULTS
    """

    # ========================================================
    # NORMALIZE BUDGET
    # ========================================================

    budget_value = safe_float(
        budget
    )

    # ========================================================
    # NORMALIZE LIMIT
    # ========================================================

    try:

        limit = int(
            limit
        )

    except (
        TypeError,
        ValueError,
    ):

        limit = 10

    limit = max(
        1,
        min(
            limit,
            50,
        ),
    )

    # ========================================================
    # LOAD FOODS
    # ========================================================

    foods = list(
        Food.objects.all()
    )

    # ========================================================
    # DIET FILTER
    # ========================================================

    if diet_type:

        foods = [
            food
            for food in foods
            if matches_diet(
                food,
                diet_type,
            )
        ]

    # ========================================================
    # FOOD TYPE FILTER
    # ========================================================

    if food_type:

        foods = [
            food
            for food in foods
            if matches_food_type(
                food,
                food_type,
            )
        ]

    # ========================================================
    # HARD BUDGET FILTER
    # ========================================================

    if budget_value is not None:

        foods = [
            food
            for food in foods
            if matches_budget(
                food,
                budget_value,
            )
        ]

    # ========================================================
    # USER PERSONALIZATION PROFILE
    # ========================================================

    personalization_profile = (
        _get_user_personalization_profile(
            user
        )
    )

    # ========================================================
    # RESULTS
    # ========================================================

    results = []

    # ========================================================
    # SCORE EACH FOOD
    # ========================================================

    for food in foods:

        # ----------------------------------------------------
        # BASE RECOMMENDATION SCORE
        # ----------------------------------------------------

        base_score, breakdown = calculate_score(
            food=food,
            mood=mood,
            hunger=hunger,
            budget=budget_value,
        )

        # ----------------------------------------------------
        # PERSONALIZATION SCORE
        # ----------------------------------------------------

        personalization_score = (
            calculate_personalization_score(
                food=food,
                profile=personalization_profile,
            )
        )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        final_score = base_score

        if (
            user is not None
            and getattr(
                user,
                "is_authenticated",
                False,
            )
        ):

            # Personalization contributes 5%
            # to the final recommendation score.

            personalization_boost = (
                personalization_score * 0.05
            )

            final_score = (
                base_score
                + personalization_boost
            )

        # Learn directly from explicit feedback. A dislike should outweigh
        # the small positive personalization boost; repeated history should
        # gently diversify results when alternatives are available.
        food_id = str(get_field(food, "food_id", "")).strip()
        feedback_adjustment = 0.0
        if user is not None and getattr(user, "is_authenticated", False):
            if food_id and food_id in personalization_profile.get("disliked_food_ids", set()):
                feedback_adjustment = -12.0
            elif food_id and food_id in personalization_profile.get("liked_food_ids", set()):
                feedback_adjustment = 3.0

            history_count = personalization_profile.get(
                "history_food_ids", Counter()
            ).get(food_id, 0)
            repeat_penalty = min(6.0, history_count * 1.5)
            final_score += feedback_adjustment - repeat_penalty
        else:
            repeat_penalty = 0.0

        # Never allow score above 100 or below 0.

        final_score = max(
            0.0,
            min(
                100.0,
                final_score,
            ),
        )

        # ----------------------------------------------------
        # ADD PERSONALIZATION TO BREAKDOWN
        # ----------------------------------------------------

        breakdown["personalization"] = round(
            personalization_score,
            2,
        )

        # ----------------------------------------------------
        # ADD PERSONALIZATION BOOST
        # ----------------------------------------------------

        if (
            user is not None
            and getattr(
                user,
                "is_authenticated",
                False,
            )
        ):

            breakdown["personalization_boost"] = round(
                personalization_score * 0.05,
                2,
            )

        else:

            breakdown["personalization_boost"] = 0.0

        breakdown["feedback_adjustment"] = round(feedback_adjustment, 2)
        breakdown["repeat_penalty"] = round(repeat_penalty, 2)

        # ----------------------------------------------------
        # BUILD EXPLANATIONS
        # ----------------------------------------------------

        reasons = build_explanations(
            food=food,
            mood=mood,
            hunger=hunger,
            budget=budget_value,
            breakdown=breakdown,
            personalization_score=personalization_score,
        )

        # ----------------------------------------------------
        # PERSONALIZATION REASON
        # ----------------------------------------------------

        if (
            user is not None
            and getattr(
                user,
                "is_authenticated",
                False,
            )
            and personalization_score >= 70
            and len(reasons) < 4
        ):

            reasons.append(
                "Matches your personal food preferences"
            )

        # ----------------------------------------------------
        # APPEND RESULT
        # ----------------------------------------------------

        results.append(
            {
                "food": food,

                "score": round(
                    final_score,
                    2,
                ),

                "breakdown": breakdown,

                "reasons": reasons,
            }
        )

    # ========================================================
    # SORT RESULTS
    # ========================================================

    results.sort(
        key=lambda item: (
            item["score"],

            item["breakdown"].get(
                "personalization",
                0,
            ),

            item["breakdown"].get(
                "budget",
                0,
            ),

            item["breakdown"].get(
                "mood",
                0,
            ),

            item["breakdown"].get(
                "hunger",
                0,
            ),
        ),
        reverse=True,
    )

    # ========================================================
    # APPLY RESULT DIVERSITY
    # ========================================================

    results = diversify_results(
        results=results,
        limit=limit,
    )

    # ========================================================
    # RETURN
    # ========================================================

    return results[:limit]
