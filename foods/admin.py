from django.contrib import admin
from .models import Food


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = (
        "food_name",
        "food_type",
        "cuisine",
        "diet_type",
        "calories_per_serving",
        "protein_g",
        "price_avg_inr",
        "qa_status_final",
    )

    list_filter = (
        "food_type",
        "diet_type",
        "cuisine",
        "category",
        "country",
        "qa_status_final",
        "nutrition_status",
        "price_status",
    )

    search_fields = (
        "food_name",
        "food_id",
        "cuisine",
        "category",
        "ingredients",
    )

    ordering = ("food_name",)

    readonly_fields = (
        "food_id",
        "created_at",
        "updated_at",
    )

    list_per_page = 50