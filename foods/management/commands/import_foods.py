import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from foods.models import Food


class Command(BaseCommand):
    help = "Import MoodBite food dataset into the Django database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="moodbite_master_final_v1_5615.csv",
            help="Path to the MoodBite master CSV file",
        )

        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing Food records before importing",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["file"])

        # Allow running the command from the Django project root.
        if not csv_path.is_absolute():
            csv_path = Path.cwd() / csv_path

        if not csv_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"CSV file not found:\n{csv_path}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"CSV found: {csv_path}"
            )
        )

        if options["clear"]:
            deleted_count, _ = Food.objects.all().delete()

            self.stdout.write(
                self.style.WARNING(
                    f"Deleted existing Food records: {deleted_count}"
                )
            )

        imported = 0
        skipped = 0
        updated = 0

        def clean(value):
            if value is None:
                return ""

            value = str(value).strip()

            if value.lower() in {"nan", "none", "null"}:
                return ""

            return value

        def to_float(value):
            value = clean(value)

            if not value:
                return None

            try:
                return float(value)
            except (ValueError, TypeError):
                return None

        def to_int(value):
            value = clean(value)

            if not value:
                return 0

            try:
                return int(float(value))
            except (ValueError, TypeError):
                return 0

        def to_bool(value):
            value = clean(value).lower()

            if value in {"true", "1", "yes", "y"}:
                return True

            if value in {"false", "0", "no", "n"}:
                return False

            return None

        def get(row, key):
            return clean(row.get(key, ""))

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                self.stdout.write(
                    self.style.ERROR(
                        "CSV has no header row."
                    )
                )
                return

            required_columns = {
                "food_id",
                "food_name",
                "ingredients",
                "instructions",
            }

            missing_columns = required_columns - set(reader.fieldnames)

            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(
                        "Missing required CSV columns: "
                        + ", ".join(sorted(missing_columns))
                    )
                )
                return

            for row_number, row in enumerate(reader, start=2):

                food_id = get(row, "food_id")
                food_name = get(row, "food_name")

                if not food_id or not food_name:
                    skipped += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f"Skipped row {row_number}: "
                            "missing food_id or food_name"
                        )
                    )

                    continue

                defaults = {
                    # Classification
                    "food_name": food_name,
                    "food_type": get(row, "food_type"),
                    "cuisine": get(row, "cuisine"),
                    "category": get(row, "category"),
                    "diet_type": get(row, "diet_type"),

                    # Recipe
                    "ingredients": get(row, "ingredients"),
                    "instructions": get(row, "instructions"),
                    "servings": get(row, "servings"),

                    "prep_time_min": to_float(
                        row.get("prep_time_min")
                    ),
                    "cook_time_min": to_float(
                        row.get("cook_time_min")
                    ),
                    "total_time_min": to_float(
                        row.get("total_time_min")
                    ),

                    # Source
                    "recipe_source": get(
                        row, "recipe_source"
                    ),
                    "recipe_source_url": get(
                        row, "recipe_source_url"
                    ),
                    "description": get(row, "description"),
                    "region": get(row, "region"),
                    "country": get(row, "country"),

                    # Image
                    "image_url": get(row, "image_url"),
                    "image_source": get(
                        row, "image_source"
                    ),
                    "image_status": get(
                        row, "image_status"
                    ),

                    # Nutrition
                    "calories_per_serving": to_float(
                        row.get("calories_per_serving")
                    ),
                    "protein_g": to_float(
                        row.get("protein_g")
                    ),
                    "carbs_g": to_float(
                        row.get("carbs_g")
                    ),
                    "fat_g": to_float(
                        row.get("fat_g")
                    ),
                    "fiber_g": to_float(
                        row.get("fiber_g")
                    ),
                    "sugar_g": to_float(
                        row.get("sugar_g")
                    ),
                    "sodium_mg": to_float(
                        row.get("sodium_mg")
                    ),

                    "nutrition_status": get(
                        row, "nutrition_status"
                    ),
                    "nutrition_coverage_pct": to_float(
                        row.get("nutrition_coverage_pct")
                    ),
                    "nutrition_basis": get(
                        row, "nutrition_basis"
                    ),

                    # Price
                    "price_min_inr": to_float(
                        row.get("price_min_inr")
                    ),
                    "price_max_inr": to_float(
                        row.get("price_max_inr")
                    ),
                    "price_avg_inr": to_float(
                        row.get("price_avg_inr")
                    ),

                    "price_status": get(
                        row, "price_status"
                    ),
                    "price_basis": get(
                        row, "price_basis"
                    ),
                    "price_confidence": get(
                        row, "price_confidence"
                    ),

                    # Mood / Hunger
                    "spice_score": to_float(
                        row.get("spice_score")
                    ),
                    "comfort_score": to_float(
                        row.get("comfort_score")
                    ),
                    "energy_score": to_float(
                        row.get("energy_score")
                    ),
                    "indulgence_score": to_float(
                        row.get("indulgence_score")
                    ),
                    "freshness_score": to_float(
                        row.get("freshness_score")
                    ),
                    "adventure_score": to_float(
                        row.get("adventure_score")
                    ),
                    "satiety_score": to_float(
                        row.get("satiety_score")
                    ),

                    "mood_status": get(
                        row, "mood_status"
                    ),
                    "mood_basis": get(
                        row, "mood_basis"
                    ),
                    "mood_confidence": get(
                        row, "mood_confidence"
                    ),

                    # International data
                    "source_meal_id": get(
                        row, "source_meal_id"
                    ),
                    "alternate_name": get(
                        row, "alternate_name"
                    ),
                    "tags": get(row, "tags"),
                    "youtube_url": get(
                        row, "youtube_url"
                    ),

                    "creative_commons_confirmed": to_bool(
                        row.get(
                            "creative_commons_confirmed"
                        )
                    ),

                    # QA
                    "nutrition_quality_flag": get(
                        row, "nutrition_quality_flag"
                    ),
                    "nutrition_outlier": to_bool(
                        row.get("nutrition_outlier")
                    ) or False,

                    "core_missing_count": to_int(
                        row.get("core_missing_count")
                    ),

                    "image_missing": to_bool(
                        row.get("image_missing")
                    ) or False,

                    "nutrition_missing": to_bool(
                        row.get("nutrition_missing")
                    ) or False,

                    "price_missing": to_bool(
                        row.get("price_missing")
                    ) or False,

                    "mood_missing_count": to_int(
                        row.get("mood_missing_count")
                    ),

                    "qa_score_final": to_float(
                        row.get("qa_score_final")
                    ),

                    "image_url_present": to_bool(
                        row.get("image_url_present")
                    ) or False,

                    "image_url_domain": get(
                        row, "image_url_domain"
                    ),

                    "qa_status_final": get(
                        row, "qa_status_final"
                    ),
                }

                try:
                    food, created = Food.objects.update_or_create(
                        food_id=food_id,
                        defaults=defaults,
                    )

                    if created:
                        imported += 1
                    else:
                        updated += 1

                except Exception as exc:
                    skipped += 1

                    self.stdout.write(
                        self.style.ERROR(
                            f"Row {row_number} failed "
                            f"({food_id}): {exc}"
                        )
                    )

                if (imported + updated + skipped) % 500 == 0:
                    self.stdout.write(
                        f"Processed: "
                        f"{imported + updated + skipped}"
                    )

        total = Food.objects.count()

        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                "MOODBITE IMPORT COMPLETE"
            )
        )
        self.stdout.write("=" * 60)
        self.stdout.write(
            f"New records imported : {imported}"
        )
        self.stdout.write(
            f"Existing records updated: {updated}"
        )
        self.stdout.write(
            f"Rows skipped          : {skipped}"
        )
        self.stdout.write(
            f"Database total        : {total}"
        )
        self.stdout.write("=" * 60)