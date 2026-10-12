import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from foods.models import Food

from .models import (
    RecommendationFeedback,
    RecommendationHistory,
    UserInteraction,
)


# ============================================================
# HELPERS
# ============================================================


def _get_json_body(request):
    """
    Safely read JSON request body.

    Returns:
        dict
    """

    try:
        if not request.body:
            return {}

        data = json.loads(
            request.body.decode("utf-8")
        )

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):
        pass

    return {}


def _serialize_feedback(feedback):
    """
    Convert RecommendationFeedback into JSON-safe data.
    """

    if feedback is None:
        return {
            "feedback": None,
            "food_id": None,
            "created_at": None,
            "updated_at": None,
        }

    return {
        "feedback": feedback.feedback,
        "food_id": feedback.food.food_id,
        "created_at": feedback.created_at.isoformat(),
        "updated_at": feedback.updated_at.isoformat(),
    }


# ============================================================
# GET CURRENT FEEDBACK
# ============================================================


@login_required
@require_http_methods(["GET"])
def feedback_check_api(request, food_id):
    """
    Return the current user's feedback for one food.

    Example:

        GET
        /accounts/api/feedback/IND_ARCH_03368/
    """

    feedback = (
        RecommendationFeedback.objects
        .filter(
            user=request.user,
            food_id=food_id,
        )
        .select_related("food")
        .first()
    )

    if feedback is None:

        return JsonResponse({
            "success": True,
            "feedback": None,
            "food_id": food_id,
        })

    return JsonResponse({
        "success": True,
        "feedback": feedback.feedback,
        "food_id": feedback.food.food_id,
        "created_at": feedback.created_at.isoformat(),
        "updated_at": feedback.updated_at.isoformat(),
    })


# ============================================================
# SAVE / UPDATE FEEDBACK
# ============================================================


@login_required
@require_http_methods(["POST"])
def feedback_api(request, food_id):
    """
    Create or update feedback for a food.

    Expected JSON:

        {
            "feedback": "like"
        }

    or:

        {
            "feedback": "dislike"
        }

    Optional:

        {
            "feedback": "like",
            "recommendation_history_id": 15
        }
    """

    # ========================================================
    # GET FOOD
    # ========================================================

    try:

        food = Food.objects.get(
            food_id=food_id
        )

    except Food.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "message": "Food not found.",
                "food_id": food_id,
            },
            status=404,
        )

    # ========================================================
    # READ REQUEST DATA
    # ========================================================

    data = _get_json_body(request)

    feedback_value = str(
        data.get(
            "feedback",
            "",
        )
    ).strip().lower()

    # ========================================================
    # VALIDATE FEEDBACK
    # ========================================================

    if feedback_value not in {
        "like",
        "dislike",
    }:

        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Feedback must be "
                    "'like' or 'dislike'."
                ),
            },
            status=400,
        )

    # ========================================================
    # OPTIONAL HISTORY
    # ========================================================

    history = None

    history_id = data.get(
        "recommendation_history_id"
    )

    if history_id not in (
        None,
        "",
    ):

        try:

            history = (
                RecommendationHistory.objects
                .filter(
                    id=int(history_id),
                    user=request.user,
                )
                .first()
            )

        except (
            TypeError,
            ValueError,
        ):

            history = None

        if history is None:

            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        "Recommendation history "
                        "was not found."
                    ),
                },
                status=400,
            )

    # ========================================================
    # CREATE OR UPDATE
    # ========================================================

    feedback_object, created = (
        RecommendationFeedback.objects.update_or_create(
            user=request.user,
            food=food,
            defaults={
                "feedback": feedback_value,
                "recommendation_history": history,
            },
        )
    )
    UserInteraction.objects.create(
    user=request.user,
    food=food,
    interaction_type=feedback_value,
)

    # ========================================================
    # RESPONSE
    # ========================================================

    return JsonResponse({
        "success": True,
        "created": created,
        "feedback": feedback_object.feedback,
        "food_id": food.food_id,
        "message": (
            "Feedback saved."
            if created
            else "Feedback updated."
        ),
        "created_at": (
            feedback_object.created_at.isoformat()
        ),
        "updated_at": (
            feedback_object.updated_at.isoformat()
        ),
    })


# ============================================================
# REMOVE FEEDBACK
# ============================================================


@login_required
@require_http_methods(["DELETE"])
def remove_feedback_api(request, food_id):
    """
    Remove the current user's feedback for a food.

    Example:

        DELETE
        /accounts/api/feedback/IND_ARCH_03368/
    """

    deleted_count, _ = (
        RecommendationFeedback.objects
        .filter(
            user=request.user,
            food_id=food_id,
        )
        .delete()
    )

    return JsonResponse({
        "success": True,
        "removed": deleted_count > 0,
        "food_id": food_id,
        "feedback": None,
    })


# ============================================================
# USER FEEDBACK LIST
# ============================================================


@login_required
@require_http_methods(["GET"])
def feedback_list_api(request):
    """
    Return all feedback belonging to the logged-in user.

    This will later help the personalization engine
    understand the user's likes and dislikes.
    """

    feedback_items = (
        RecommendationFeedback.objects
        .filter(
            user=request.user
        )
        .select_related("food")
        .order_by("-updated_at")
    )

    results = []

    for item in feedback_items:

        results.append({
            "food_id": item.food.food_id,
            "name": item.food.food_name,
            "feedback": item.feedback,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        })

    return JsonResponse({
        "success": True,
        "count": len(results),
        "feedback": results,
    })