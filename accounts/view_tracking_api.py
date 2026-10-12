from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from foods.models import Food

from .models import (
    FoodView,
    UserInteraction,
)


@login_required
@require_POST
def record_food_view_api(request, food_id):
    """
    Record that the logged-in user opened a food detail page.
    """

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


    food_view = FoodView.objects.create(
        user=request.user,
        food=food,
    )

    UserInteraction.objects.create(
    user=request.user,
    food=food,
    interaction_type="view",
   )

    return JsonResponse(
        {
            "success": True,
            "food_id": food.food_id,
            "view_id": food_view.id,
            "viewed_at": (
                food_view.viewed_at.isoformat()
            ),
            "message": "Food view recorded.",
        }
    )