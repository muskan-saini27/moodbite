import requests
import json
import time
from pathlib import Path

BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php"

output_dir = Path("data/raw/international")
output_dir.mkdir(parents=True, exist_ok=True)

all_meals = {}

for letter in "abcdefghijklmnopqrstuvwxyz":
    print(f"Downloading {letter.upper()}...")

    response = requests.get(
        BASE_URL,
        params={"f": letter},
        timeout=30
    )
    response.raise_for_status()

    data = response.json()

    meals = data.get("meals") or []

    for meal in meals:
        all_meals[meal["idMeal"]] = meal

    print(f"  Found: {len(meals)}")

    time.sleep(0.3)

with open(output_dir / "themealdb_all.json", "w", encoding="utf-8") as f:
    json.dump(
        list(all_meals.values()),
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print("=" * 50)
print(f"TOTAL UNIQUE MEALS: {len(all_meals)}")
print(f"Saved to: {output_dir / 'themealdb_all.json'}")
print("=" * 50)