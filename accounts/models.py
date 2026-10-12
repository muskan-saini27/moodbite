from django.conf import settings
from django.db import models


class SavedFood(models.Model):
    """
    Stores which food a specific authenticated user has saved.

    IMPORTANT:
    One food can be saved by many users,
    but the same user can save a food only once.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_saved_foods",
    )

    food = models.ForeignKey(
        "foods.Food",
        on_delete=models.CASCADE,
        related_name="user_saves",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "food"],
                name="accounts_unique_saved_food_per_user",
            )
        ]

        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
            models.Index(
                fields=["food"]
            ),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.food.food_name}"

class RecommendationHistory(models.Model):
    """
    Stores a recommendation session for one authenticated user.

    Each record contains the filters used by the user and
    a lightweight snapshot of the foods recommended at that time.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_recommendation_history",
    )

    mood = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    hunger = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    budget = models.FloatField(
        blank=True,
        null=True,
    )

    food_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    diet_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    results = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} "
            f"recommendation "
            f"{self.created_at:%Y-%m-%d %H:%M}"
        )

class UserPreference(models.Model):
    """
    Stores the default food preferences of one authenticated user.

    These preferences will later be used by the recommendation engine
    to personalize recommendations.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_preferences",
    )

    preferred_food_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    preferred_diet_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    preferred_cuisine = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    preferred_budget = models.FloatField(
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.username} preferences"

# ============================================================
# RECOMMENDATION FEEDBACK
# ============================================================


class RecommendationFeedback(models.Model):
    """
    Stores a user's feedback on a recommended food.

    Feedback values:
        like
        dislike
    """

    FEEDBACK_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_recommendation_feedback",
    )

    food = models.ForeignKey(
        "foods.Food",
        on_delete=models.CASCADE,
        related_name="recommendation_feedback",
    )

    recommendation_history = models.ForeignKey(
        "accounts.RecommendationHistory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_items",
    )

    feedback = models.CharField(
        max_length=20,
        choices=FEEDBACK_CHOICES,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "food"],
                name="accounts_unique_feedback_per_user_food",
            )
        ]

        indexes = [
            models.Index(
                fields=["user", "-updated_at"]
            ),
            models.Index(
                fields=["food"]
            ),
            models.Index(
                fields=["feedback"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} → "
            f"{self.food.food_name} → "
            f"{self.feedback}"
        )

class FoodView(models.Model):
    """
    Records when a user opens a food detail page.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_food_views",
    )

    food = models.ForeignKey(
        "foods.Food",
        on_delete=models.CASCADE,
        related_name="user_views",
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-viewed_at"]

        indexes = [
            models.Index(
                fields=["user", "-viewed_at"]
            ),
            models.Index(
                fields=["food"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} → "
            f"{self.food.food_name} → "
            f"viewed"
        )

class UserInteraction(models.Model):
    """
    Unified event log for user-food interactions.

    This stores individual interaction events so that
    MoodBite can later analyze user behavior and train
    recommendation models.
    """

    INTERACTION_CHOICES = [
        ("view", "View"),
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("save", "Save"),
        ("unsave", "Unsave"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moodbite_interactions",
    )

    food = models.ForeignKey(
        "foods.Food",
        on_delete=models.CASCADE,
        related_name="user_interactions",
    )

    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_CHOICES,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "-created_at"]
            ),
            models.Index(
                fields=["food", "-created_at"]
            ),
            models.Index(
                fields=["user", "interaction_type"]
            ),
            models.Index(
                fields=["interaction_type", "-created_at"]
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} → "
            f"{self.food.food_name} → "
            f"{self.interaction_type}"
        )