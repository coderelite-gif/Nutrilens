# barcode_api.py
# Fetches nutrition for packaged foods using barcode via Open Food Facts API
# NOTE: Open Food Facts is community-edited — always validate results.

import requests

HEADERS = {
    "User-Agent": "FoodRecognitionApp/1.0 (college-project; your-email@example.com)"
}

# ---------------------------------------------------------------------------
# Internal validation
# ---------------------------------------------------------------------------

def _looks_valid(result: dict) -> tuple[bool, str]:
    """Basic sanity checks. Returns (is_valid, reason_if_invalid)."""
    if result["name"] == "Unknown Product":
        return False, "Product name missing in database"
    if result["calories"] == 0 and result["protein"] == 0 and result["carbs"] == 0:
        return False, "All nutrition values are zero — likely an incomplete DB entry"
    if result["calories"] < 5 and result["fat"] == 0 and result["protein"] == 0:
        return False, "Nutrition profile looks like plain water — possible wrong DB entry"
    return True, ""


# ---------------------------------------------------------------------------
# Barcode lookup
# ---------------------------------------------------------------------------

def get_nutrition_by_barcode(barcode: str, validate: bool = True) -> dict | None:
    """
    Looks up a product barcode on Open Food Facts.
    Returns nutrition per 100g or None if not found / on error.

    Args:
        barcode:  EAN barcode string
        validate: if True, runs sanity checks and flags suspicious results
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        response = requests.get(url, timeout=8, headers=HEADERS)
    except requests.exceptions.ConnectionError:
        print("Barcode API error: No internet connection.")
        return None
    except requests.exceptions.Timeout:
        print("Barcode API error: Request timed out.")
        return None

    # Check HTTP status BEFORE calling .json() — a non-200 returns plain text
    # which causes "Expecting value: line 1 column 1" if you skip this check
    if response.status_code != 200:
        print(f"Barcode API error: HTTP {response.status_code} — {response.text[:100]}")
        return None

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print("Barcode API error: Response was not valid JSON.")
        return None

    if data.get("status") != 1:
        print(f"Barcode API: Product not found for barcode '{barcode}'")
        print("  → Tip: Try search_by_name_fallback() for Indian products missing from the index.")
        return None

    product    = data["product"]
    nutriments = product.get("nutriments", {})
    name       = product.get("product_name", "").strip() or "Unknown Product"

    # Some products report energy in kJ only — convert to kcal as fallback
    calories = nutriments.get("energy-kcal_100g") or \
               (nutriments.get("energy_100g", 0) / 4.184)

    result = {
        "name":         name,
        "barcode":      barcode,
        "calories":     round(float(calories), 1),
        "protein":      round(float(nutriments.get("proteins_100g",      0)), 1),
        "carbs":        round(float(nutriments.get("carbohydrates_100g", 0)), 1),
        "fat":          round(float(nutriments.get("fat_100g",           0)), 1),
        "fiber":        round(float(nutriments.get("fiber_100g",         0)), 1),
        "sodium":       round(float(nutriments.get("sodium_100g",        0)) * 1000, 1),  # g → mg
        "source":       "Open Food Facts",
        "data_warning": None,
    }

    # Validate — Open Food Facts is community-edited and has incorrect entries
    # e.g. a Lays barcode returning Coca-Cola data
    if validate:
        is_valid, reason = _looks_valid(result)
        if not is_valid:
            result["data_warning"] = reason
            print(f"⚠️  Data quality warning for '{name}' ({barcode}): {reason}")
            print(f"   → Verify at: https://world.openfoodfacts.org/product/{barcode}")

    return result


# ---------------------------------------------------------------------------
# Portion scaler
# ---------------------------------------------------------------------------

def scale_nutrition(nutrition: dict, grams: int) -> dict:
    """Scale nutrition values to a given portion size (grams)."""
    skip  = {"name", "source", "barcode", "data_warning"}
    scale = grams / 100
    scaled = {k: round(v * scale, 1) for k, v in nutrition.items() if k not in skip}
    return {
        "name":         nutrition["name"],
        "barcode":      nutrition.get("barcode"),
        **scaled,
        "source":       nutrition["source"],
        "data_warning": nutrition.get("data_warning"),
    }


# ---------------------------------------------------------------------------
# Name-based fallback (for barcodes not in Open Food Facts)
# ---------------------------------------------------------------------------

def search_by_name_fallback(query: str, max_results: int = 3) -> list[dict]:
    """
    Search Open Food Facts by product name.
    Use this when a barcode lookup returns None (common for Indian products).

    Example:
        results = search_by_name_fallback("Maggi masala noodles")
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action":        "process",
        "json":          1,
        "page_size":     max_results,
        "fields":        "product_name,nutriments",
    }
    try:
        response = requests.get(url, params=params, timeout=8, headers=HEADERS)
        if response.status_code != 200:
            return []
        products = response.json().get("products", [])
        results  = []
        for p in products:
            n    = p.get("nutriments", {})
            name = p.get("product_name", "").strip()
            if not name:
                continue
            calories = n.get("energy-kcal_100g") or (n.get("energy_100g", 0) / 4.184)
            results.append({
                "name":         name,
                "calories":     round(float(calories), 1),
                "protein":      round(float(n.get("proteins_100g",      0)), 1),
                "carbs":        round(float(n.get("carbohydrates_100g", 0)), 1),
                "fat":          round(float(n.get("fat_100g",           0)), 1),
                "fiber":        round(float(n.get("fiber_100g",         0)), 1),
                "sodium":       round(float(n.get("sodium_100g",        0)) * 1000, 1),
                "source":       "Open Food Facts (name search)",
                "data_warning": None,
            })
        return results
    except Exception as e:
        print(f"Name search error: {e}")
        return []


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Barcode Lookup Tests ===\n")

    test_barcodes = {
        "Maggi Noodles (IN)": "8901058000570",
        "Lays Classic":       "4890008100309",
        "Invalid barcode":    "0000000000000",
    }

    for label, barcode in test_barcodes.items():
        print(f"--- {label} ({barcode}) ---")
        result = get_nutrition_by_barcode(barcode)
        if result:
            if result["data_warning"]:
                print(f"  ⚠️  WARNING: {result['data_warning']}")
            print("  Per 100g:", result)
            print("  Per 150g:", scale_nutrition(result, 150))
        print()

    # Fallback for products not in barcode index
    print("=== Name Search Fallback: 'Maggi masala noodles' ===")
    fallback = search_by_name_fallback("Maggi masala noodles")
    if fallback:
        for r in fallback:
            print(f"  → {r['name']} | Cal: {r['calories']} | Carbs: {r['carbs']}g | Protein: {r['protein']}g")
    else:
        print("  No results found.")