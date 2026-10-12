from django.db import models


class Food(models.Model):

    # =========================
    # IDENTITY
    # =========================

    food_id = models.CharField(
        max_length=100,
        primary_key=True
    )

    food_name = models.CharField(
        max_length=255
    )

    # =========================
    # CLASSIFICATION
    # =========================

    food_type = models.CharField(
        max_length=100,
        blank=True
    )

    cuisine = models.CharField(
        max_length=150,
        blank=True
    )

    category = models.CharField(
        max_length=150,
        blank=True
    )

    diet_type = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # RECIPE
    # =========================

    ingredients = models.TextField(
        blank=True
    )

    instructions = models.TextField(
        blank=True
    )

    servings = models.CharField(
        max_length=50,
        blank=True
    )

    prep_time_min = models.FloatField(
        null=True,
        blank=True
    )

    cook_time_min = models.FloatField(
        null=True,
        blank=True
    )

    total_time_min = models.FloatField(
        null=True,
        blank=True
    )

    # =========================
    # SOURCE / DESCRIPTION
    # =========================

    recipe_source = models.CharField(
        max_length=255,
        blank=True
    )

    recipe_source_url = models.URLField(
        max_length=1000,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    region = models.CharField(
        max_length=150,
        blank=True
    )

    country = models.CharField(
        max_length=150,
        blank=True
    )

    # =========================
    # IMAGE
    # =========================

    image_url = models.URLField(
        max_length=1000,
        blank=True
    )

    image_source = models.CharField(
        max_length=255,
        blank=True
    )

    image_status = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # NUTRITION
    # =========================

    calories_per_serving = models.FloatField(
        null=True,
        blank=True
    )

    protein_g = models.FloatField(
        null=True,
        blank=True
    )

    carbs_g = models.FloatField(
        null=True,
        blank=True
    )

    fat_g = models.FloatField(
        null=True,
        blank=True
    )

    fiber_g = models.FloatField(
        null=True,
        blank=True
    )

    sugar_g = models.FloatField(
        null=True,
        blank=True
    )

    sodium_mg = models.FloatField(
        null=True,
        blank=True
    )

    nutrition_status = models.CharField(
        max_length=100,
        blank=True
    )

    nutrition_coverage_pct = models.FloatField(
        null=True,
        blank=True
    )

    nutrition_basis = models.CharField(
        max_length=255,
        blank=True
    )

    # =========================
    # PRICE
    # =========================

    price_min_inr = models.FloatField(
        null=True,
        blank=True
    )

    price_max_inr = models.FloatField(
        null=True,
        blank=True
    )

    price_avg_inr = models.FloatField(
        null=True,
        blank=True
    )

    price_status = models.CharField(
        max_length=100,
        blank=True
    )

    price_basis = models.CharField(
        max_length=255,
        blank=True
    )

    price_confidence = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # MOOD / HUNGER SCORES
    # =========================

    spice_score = models.FloatField(
        null=True,
        blank=True
    )

    comfort_score = models.FloatField(
        null=True,
        blank=True
    )

    energy_score = models.FloatField(
        null=True,
        blank=True
    )

    indulgence_score = models.FloatField(
        null=True,
        blank=True
    )

    freshness_score = models.FloatField(
        null=True,
        blank=True
    )

    adventure_score = models.FloatField(
        null=True,
        blank=True
    )

    satiety_score = models.FloatField(
        null=True,
        blank=True
    )

    mood_status = models.CharField(
        max_length=100,
        blank=True
    )

    mood_basis = models.CharField(
        max_length=255,
        blank=True
    )

    mood_confidence = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # INTERNATIONAL SOURCE DATA
    # =========================

    source_meal_id = models.CharField(
        max_length=100,
        blank=True
    )

    alternate_name = models.CharField(
        max_length=255,
        blank=True
    )

    tags = models.TextField(
        blank=True
    )

    youtube_url = models.URLField(
        max_length=1000,
        blank=True
    )

    creative_commons_confirmed = models.BooleanField(
        null=True,
        blank=True
    )

    # =========================
    # QUALITY / QA
    # =========================

    nutrition_quality_flag = models.CharField(
        max_length=150,
        blank=True
    )

    nutrition_outlier = models.BooleanField(
        default=False
    )

    core_missing_count = models.IntegerField(
        default=0
    )

    image_missing = models.BooleanField(
        default=False
    )

    nutrition_missing = models.BooleanField(
        default=False
    )

    price_missing = models.BooleanField(
        default=False
    )

    mood_missing_count = models.IntegerField(
        default=0
    )

    qa_score_final = models.FloatField(
        null=True,
        blank=True
    )

    image_url_present = models.BooleanField(
        default=False
    )

    image_url_domain = models.CharField(
        max_length=255,
        blank=True
    )

    qa_status_final = models.CharField(
        max_length=100,
        blank=True
    )

    # =========================
    # DJANGO METADATA
    # =========================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "food_name"
        ]

        indexes = [
            models.Index(
                fields=["food_name"]
            ),

            models.Index(
                fields=["food_type"]
            ),

            models.Index(
                fields=["cuisine"]
            ),

            models.Index(
                fields=["category"]
            ),

            models.Index(
                fields=["diet_type"]
            ),

            models.Index(
                fields=["country"]
            ),

            models.Index(
                fields=["qa_status_final"]
            ),
        ]

    def __str__(self):
        return self.food_name