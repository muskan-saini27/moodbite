
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.models import (
    SavedFood,
    UserInteraction,
    RecommendationFeedback,
    RecommendationHistory,
)


@login_required
def analytics_dashboard(request):
    return render(request, "analytics.html")


@login_required
def analytics_api(request):
    user = request.user
    period = request.GET.get("period", "30d")

    valid_periods = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "all": None,
    }

    if period not in valid_periods:
        period = "30d"

    days = valid_periods[period]
    now = timezone.now()
    start_date = None
    previous_start = None

    if days is not None:
        start_date = now - timedelta(days=days)
        previous_start = now - timedelta(days=days * 2)

    interactions = UserInteraction.objects.filter(user=user)
    history = RecommendationHistory.objects.filter(user=user)
    feedback = RecommendationFeedback.objects.filter(user=user)
    previous_interactions = UserInteraction.objects.filter(user=user)
    previous_history = RecommendationHistory.objects.filter(user=user)

    if previous_start is not None and start_date is not None:
        previous_interactions = previous_interactions.filter(
            created_at__gte=previous_start,
            created_at__lt=start_date,
        )
        previous_history = previous_history.filter(
            created_at__gte=previous_start,
            created_at__lt=start_date,
        )
    else:
        previous_interactions = previous_interactions.none()
        previous_history = previous_history.none()

    previous_summary = {
        "interactions": previous_interactions.count(),
        "recommendations": previous_history.count(),
        "views": previous_interactions.filter(
            interaction_type="view"
        ).count(),
        "likes": previous_interactions.filter(
            interaction_type="like"
        ).count(),
        "saves": previous_interactions.filter(
            interaction_type="save"
        ).count(),
    }

    if start_date is not None:
        interactions = interactions.filter(
            created_at__gte=start_date
        )
        history = history.filter(
            created_at__gte=start_date
        )
        feedback = feedback.filter(
            updated_at__gte=start_date
        )

    interaction_types = [
        "view",
        "like",
        "dislike",
        "save",
        "unsave",
    ]

    interaction_counts = {
        kind: interactions.filter(
            interaction_type=kind
        ).count()
        for kind in interaction_types
    }

    total_interactions = interactions.count()
    recommendation_count = history.count()

    # Current saved-food total is a snapshot, not a count of save events.
    current_saved_count = SavedFood.objects.filter(
        user=user
    ).count()

    most_viewed = list(
        interactions
        .filter(interaction_type="view")
        .values("food__food_id", "food__food_name")
        .annotate(total=Count("id"))
        .order_by("-total", "food__food_name")[:5]
    )

    most_saved = list(
        interactions
        .filter(interaction_type="save")
        .values("food__food_id", "food__food_name")
        .annotate(total=Count("id"))
        .order_by("-total", "food__food_name")[:5]
    )

    most_liked = list(
        interactions
        .filter(interaction_type="like")
        .values("food__food_id", "food__food_name")
        .annotate(total=Count("id"))
        .order_by("-total", "food__food_name")[:5]
    )

    most_disliked = list(
        interactions
        .filter(interaction_type="dislike")
        .values("food__food_id", "food__food_name")
        .annotate(total=Count("id"))
        .order_by("-total", "food__food_name")[:5]
    )


    # Daily counts for the activity trend chart.
    # Include dates with zero activity so the selected period
    # is represented consistently.

    today = timezone.localdate()

    if days is not None:
        first_day = today - timedelta(days=days - 1)
    else:
        first_event = (
            interactions.order_by("created_at")
            .values_list("created_at", flat=True)
            .first()
        )

        first_day = (
            timezone.localtime(first_event).date()
            if first_event
            else today
        )

    daily_rows = (
        interactions
        .annotate(day=TruncDate("created_at"))
        .values("day", "interaction_type")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    daily_data = {}

    for offset in range((today - first_day).days + 1):
        day = first_day + timedelta(days=offset)

        daily_data[day.isoformat()] = {
            "views": 0,
            "likes": 0,
            "dislikes": 0,
            "saves": 0,
            "unsaves": 0,
        }

    interaction_key_map = {
        "view": "views",
        "like": "likes",
        "dislike": "dislikes",
        "save": "saves",
        "unsave": "unsaves",
    }

    for row in daily_rows:
        if row["day"] is None:
            continue

        day = row["day"].isoformat()
        kind = row["interaction_type"]

        if day in daily_data and kind in interaction_key_map:
            daily_data[day][interaction_key_map[kind]] = row["total"]

    trend = [
        {"date": day, **values}
        for day, values in daily_data.items()
    ]

    likes = interaction_counts["like"]
    dislikes = interaction_counts["dislike"]
    feedback_total = likes + dislikes

    like_ratio = (
        round(likes / feedback_total * 100, 1)
        if feedback_total
        else None
    )

    insights = []

    if most_liked:
        insights.append({
            "title": "Your most-liked food",
            "value": most_liked[0]["food__food_name"],
            "detail": (
                f"{most_liked[0]['total']} recorded like event(s) "
                f"in this period."
            ),
            "type": "positive",
        })

    if most_disliked:
        insights.append({
            "title": "Food receiving the most dislikes",
            "value": most_disliked[0]["food__food_name"],
            "detail": (
                f"{most_disliked[0]['total']} recorded dislike event(s) "
                f"in this period."
            ),
            "type": "attention",
        })

    if feedback_total:
        insights.append({
            "title": "Like share",
            "value": f"{like_ratio}%",
            "detail": (
                "Likes as a proportion of recorded like and dislike events."
            ),
            "type": "neutral",
        })
    else:
        insights.append({
            "title": "Feedback needed",
            "value": "No feedback yet",
            "detail": (
                "Like or dislike a recommended food to start building "
                "your feedback insights."
            ),
            "type": "neutral",
        })

    return JsonResponse({
        "success": True,
        "period": period,
        "summary": {
            "total_interactions": total_interactions,
            "recommendations": recommendation_count,
            "views": interaction_counts["view"],
            "likes": likes,
            "dislikes": dislikes,
            "saves": interaction_counts["save"],
            "unsaves": interaction_counts["unsave"],
            "current_saved_foods": current_saved_count,
            "like_ratio": like_ratio,
        },
        "interaction_counts": interaction_counts,
        "feedback": {
            "like": likes,
            "dislike": dislikes,
        },
        "trend": trend,
        "insights": insights,
        "most_viewed": most_viewed,
        "most_saved": most_saved,
        "most_liked": most_liked,
        "most_disliked": most_disliked,
    })
