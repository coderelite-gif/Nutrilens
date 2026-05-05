
import requests
import json
import os

API_KEY  = os.getenv("USDA_API_KEY", "nlJizxGoqBWA6ewe6e12eLwGxnFGTq27CkukRbi2")
BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# ISSUE 2 FIX: disk cache so each food is only fetched once
CACHE_FILE = "data/usda_cache.json"
os.makedirs("data", exist_ok=True)

def _load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def _save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

_cache = _load_cache()


def search_food_usda(food_name: str) -> dict | None:
    """
    Searches USDA database for a food item.
    Returns nutrition per 100g or None if not found.
    Results are cached to disk after first fetch.
    """
    cache_key = food_name.lower().strip()

    # ISSUE 2 FIX: return cached result if available
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        response = requests.get(
            f"{BASE_URL}/foods/search",
            params={
                "query":    food_name,
                "api_key":  API_KEY,
                "pageSize": 5,
                "dataType": "SR Legacy,Foundation"
            },
            timeout=5
        )

        if response.status_code == 403:
            print("USDA API error: Invalid or missing API key")
            return None

        if response.status_code != 200:
            print(f"USDA API error: HTTP {response.status_code}")
            return None

        data = response.json()

        if not data.get("foods"):
            print(f"USDA: No results for '{food_name}'")
            return None

        # Prefer SR Legacy entries — most complete nutritional data
        food = next(
            (f for f in data["foods"] if f.get("dataType") == "SR Legacy"),
            data["foods"][0]
        )

        nutrients = {
            n["nutrientName"]: n["value"]
            for n in food.get("foodNutrients", [])
        }

        result = {
            "calories": round(nutrients.get("Energy", 0), 1),
            "protein":  round(nutrients.get("Protein", 0), 1),
            "carbs":    round(nutrients.get("Carbohydrate, by difference", 0), 1),
            "fat":      round(nutrients.get("Total lipid (fat)", 0), 1),
            "fiber":    round(nutrients.get("Fiber, total dietary", 0), 1),
            "sodium":   round(nutrients.get("Sodium, Na", 0), 1),
            "gi":       0,       # ISSUE 3 FIX: 0 not None — prevents TypeError in get_warnings()
            "source":   "USDA FoodData Central",
            "usda_name": food.get("description", food_name),
        }

        # Save to cache
        _cache[cache_key] = result
        _save_cache(_cache)
        print(f"USDA: ✅ '{food.get('description', food_name)}' cached")
        return result

    except Exception as e:
        print(f"USDA API error: {e}")
        return None


def get_nutrition_usda(food_key: str, grams: int = 100) -> dict | None:
    """
    Fetches nutrition from USDA scaled to portion size.
    Does NOT check local DB — that's nutrition_data.py's job.
    """
    food_name = food_key.replace("_", " ")
    data      = search_food_usda(food_name)
    if not data:
        return None

    scale = grams / 100
    return {
        "calories": round(data["calories"] * scale, 1),
        "protein":  round(data["protein"]  * scale, 1),
        "carbs":    round(data["carbs"]    * scale, 1),
        "fat":      round(data["fat"]      * scale, 1),
        "fiber":    round(data.get("fiber",  0) * scale, 1),
        "sodium":   round(data.get("sodium", 0) * scale, 1),
        "gi":       0,
        "source":   "USDA FoodData Central",
        "usda_name": data.get("usda_name", food_name),
    }

# Quick test
if __name__ == "__main__":
    tests = [
        ("pizza",     150),   # in local DB — should NOT hit API
        ("apple_pie", 100),   # not in local DB — hits USDA
        ("tiramisu",  100),   # not in local DB — hits USDA
        ("apple_pie", 100),   # second call — should use cache, no API call
    ]
    for food, grams in tests:
        print(f"\n--- {food} ({grams}g) ---")
        result = get_nutrition_usda(food, grams)
        if result:
            print(f"  cal={result['calories']}  P={result['protein']}g  "
                  f"C={result['carbs']}g  F={result['fat']}g  [{result['source']}]")
        else:
            print("  Not found")