# nutrition_data.py
# Nutrition data, health profiles, warnings and lookup functions
# Per 100g nutrition for original 10 classes + Indian Foods (instant local cache) 
NUTRITION_DB = {
    # Original 10
    "pizza":        {"calories": 266, "protein": 11, "carbs": 33, "fat": 10, "gi": 60},
    "hamburger":    {"calories": 295, "protein": 17, "carbs": 24, "fat": 14, "gi": 50},
    "sushi":        {"calories": 143, "protein": 5,  "carbs": 28, "fat": 1,  "gi": 55},
    "ice_cream":    {"calories": 207, "protein": 3,  "carbs": 24, "fat": 11, "gi": 57},
    "fried_rice":   {"calories": 163, "protein": 4,  "carbs": 28, "fat": 4,  "gi": 72},
    "omelette":     {"calories": 154, "protein": 11, "carbs": 1,  "fat": 12, "gi": 0},
    "pancakes":     {"calories": 227, "protein": 6,  "carbs": 40, "fat": 6,  "gi": 67},
    "samosa":       {"calories": 262, "protein": 5,  "carbs": 28, "fat": 15, "gi": 55},
    "cup_cakes":    {"calories": 305, "protein": 3,  "carbs": 52, "fat": 10, "gi": 65},
    "caesar_salad": {"calories": 90,  "protein": 6,  "carbs": 8,  "fat": 5,  "gi": 15},
    
    # Extended Indian Foods
    "roti":                 {"calories": 297, "protein": 9, "carbs": 46, "fat": 8, "gi": 62},
    "naan":                 {"calories": 317, "protein": 9, "carbs": 50, "fat": 9, "gi": 71},
    "paratha":              {"calories": 326, "protein": 8, "carbs": 43, "fat": 14, "gi": 68},
    "biryani":              {"calories": 160, "protein": 6, "carbs": 22, "fat": 5, "gi": 65},
    "pulao":                {"calories": 130, "protein": 3, "carbs": 25, "fat": 2, "gi": 60},
    "jeera_rice":           {"calories": 150, "protein": 3, "carbs": 28, "fat": 3, "gi": 68},
    "dal_makhani":          {"calories": 130, "protein": 5, "carbs": 12, "fat": 7, "gi": 43},
    "paneer_butter_masala": {"calories": 210, "protein": 7, "carbs": 10, "fat": 16, "gi": 28},
    "chole":                {"calories": 160, "protein": 7, "carbs": 22, "fat": 5, "gi": 33},
    "palak_paneer":         {"calories": 150, "protein": 8, "carbs": 6, "fat": 11, "gi": 15},
    "rajma":                {"calories": 140, "protein": 6, "carbs": 20, "fat": 4, "gi": 29},
    "pakora":               {"calories": 250, "protein": 6, "carbs": 24, "fat": 15, "gi": 65},
    "vada_pav":             {"calories": 300, "protein": 6, "carbs": 40, "fat": 12, "gi": 70},
    "panipuri":             {"calories": 150, "protein": 3, "carbs": 25, "fat": 4, "gi": 65},
    "gulab_jamun":          {"calories": 320, "protein": 4, "carbs": 55, "fat": 10, "gi": 75},
    "jalebi":               {"calories": 300, "protein": 3, "carbs": 60, "fat": 5, "gi": 80},
    "rasgulla":             {"calories": 180, "protein": 4, "carbs": 38, "fat": 1, "gi": 65},
    "kheer":                {"calories": 140, "protein": 4, "carbs": 20, "fat": 5, "gi": 55},
}

# Categories for the UI 
INDIAN_FOOD_CATEGORIES = {
    "Breads": ["roti", "naan", "paratha"],
    "Rice Dishes": ["biryani", "pulao", "jeera_rice"],
    "Curries/Dals": ["dal_makhani", "paneer_butter_masala", "chole", "palak_paneer", "rajma"],
    "Snacks": ["samosa", "pakora", "vada_pav", "panipuri"],
    "Desserts": ["gulab_jamun", "jalebi", "rasgulla", "kheer"]
}

# GI values for all 101 Food-101 classes 
# 0  = negligible/no carbs   |  <55 = Low   |  55-69 = Medium   |  70+ = High
GI_DB = {
    # Original 10 
    "pizza":                    60,
    "hamburger":                50,
    "sushi":                    55,
    "ice_cream":                57,
    "fried_rice":               72,
    "omelette":                  0,
    "pancakes":                 67,
    "samosa":                   55,
    "cup_cakes":                65,
    "caesar_salad":             15,
    # Breads / Pastries 
    "waffles":                  76,
    "french_toast":             65,
    "donuts":                   76,
    "churros":                  70,
    "baklava":                  65,
    "bread_pudding":            65,
    "beignets":                 70,
    "bruschetta":               62,
    "garlic_bread":             70,
    "pita_bread":               68,
    # Cakes / Desserts 
    "cheesecake":               45,
    "chocolate_cake":           65,
    "apple_pie":                65,
    "carrot_cake":              60,
    "strawberry_shortcake":     57,
    "cannoli":                  55,
    "tiramisu":                 50,
    "creme_brulee":             47,
    "panna_cotta":              45,
    "macarons":                 65,
    "mochi":                    57,
    "ice_cream":                57,
    "frozen_yogurt":            50,
    "chocolate_mousse":         45,
    # Pasta / Noodles 
    "macaroni_and_cheese":      64,
    "spaghetti_bolognese":      45,
    "spaghetti_carbonara":      45,
    "lasagna":                  50,
    "ravioli":                  50,
    "pad_thai":                 60,
    "ramen":                    65,
    "pho":                      50,
    "bibimbap":                 55,
    "takoyaki":                 55,
    "gyoza":                    50,
    "dumplings":                50,
    "spring_rolls":             60,
    "peking_duck":              30,
    "beef_and_broccoli":        25,
    "fried_calamari":           40,
    "shrimp_and_grits":         60,
    "crab_cakes":               45,
    "lobster_bisque":           35,
    "clam_chowder":             45,
    "oysters":                   0,
    "scallops":                  0,
    "sashimi":                   0,
    "mussels":                   0,
    # Rice / Grain dishes 
    "risotto":                  69,
    "paella":                   55,
    "bibimbap":                 55,
    "chicken_rice":             64,
    "pulled_pork":              25,
    # Meat dishes 
    "steak":                     0,
    "filet_mignon":              0,
    "grilled_salmon":            0,
    "grilled_cheese_sandwich":  53,
    "club_sandwich":            45,
    "hot_dog":                  52,
    "baby_back_ribs":           20,
    "pork_chop":                 0,
    "chicken_wings":            15,
    "chicken_quesadilla":       50,
    "beef_carpaccio":            0,
    "beef_tartare":              0,
    "foie_gras":                 0,
    "escargots":                 5,
    "huevos_rancheros":         45,
    "eggs_benedict":            45,
    # Salads / Vegetables 
    "greek_salad":              10,
    "caprese_salad":            15,
    "seaweed_salad":            20,
    "edamame":                  18,
    "guacamole":                10,
    "hummus":                   25,
    "falafel":                  42,
    "tabbouleh":                40,
    "ceviche":                   5,
    "poutine":                  70,
    "onion_rings":              65,
    "french_fries":             75,
    "nachos":                   65,
    "deviled_eggs":              5,
    "miso_soup":                10,
    "wonton_soup":              55,
    "tom_yum_goong":            25,
    "goulash":                  45,
    "beef_stew":                30,
    "beet_salad":               64,
    # Indian / South Asian 
    "butter_chicken":           35,
    "chicken_tikka_masala":     35,
    "breakfast_burrito":        55,
    "tacos":                    50,
    # Pizza / Flatbreads 
    "cheese_pizza":             60,
    "breakfast_burrito":        55,
    # Soups 
    "cup_cakes":                65,
    "hot_and_sour_soup":        35,
    "samosa":                   55,
    "macarons":                 65,
    "spaghetti_bolognese":      45,
    "crab_cakes":               45,
    "lobster_bisque":           35,
    "baklava":                  65,
    "apple_pie":                65,
    "churros":                  70,
    "red_velvet_cake":          60,
    "sushi":                    55,
    "takoyaki":                 55,
    "pho":                      50,
}

# Health profiles — daily targets 
HEALTH_PROFILES = {
    "Healthy Adult":          {"calories": 2000, "protein": 50,  "carbs": 275, "fat": 78},
    "Type 2 Diabetes":        {"calories": 1800, "protein": 60,  "carbs": 130, "fat": 60},
    "Hypertension (High BP)": {"calories": 1800, "protein": 50,  "carbs": 250, "fat": 55},
    "Weight Loss / Obesity":  {"calories": 1500, "protein": 70,  "carbs": 150, "fat": 50},
    "High Cholesterol":       {"calories": 1800, "protein": 55,  "carbs": 250, "fat": 45},
    "PCOD / PCOS":            {"calories": 1600, "protein": 65,  "carbs": 140, "fat": 55},
    "Gym / Muscle Gain":      {"calories": 2500, "protein": 150, "carbs": 300, "fat": 80},
    "Child (6-12 years)":     {"calories": 1600, "protein": 19,  "carbs": 220, "fat": 55},
    "Senior Citizen (60+)":   {"calories": 1600, "protein": 56,  "carbs": 200, "fat": 56},
}

# Warning rules per health profile 
HEALTH_WARNINGS = {
    "Healthy Adult": {
        "calories": {"limit": 700, "message": "Very high calorie meal — consider a smaller portion"},
        "fat":      {"limit": 25,  "message": "High fat content — balance with lighter meals today"},
    },
    "Type 2 Diabetes": {
        "carbs":    {"limit": 45, "message": "High carbs alert — exceeds diabetic meal limit of 45g"},
        "gi":       {"limit": 55, "message": "High Glycemic Index — will spike blood sugar"},
    },
    "Hypertension (High BP)": {
        "fat":      {"limit": 15,  "message": "High fat content — increases cardiovascular risk"},
        "calories": {"limit": 500, "message": "High calorie meal — monitor daily intake carefully"},
    },
    "Weight Loss / Obesity": {
        "calories": {"limit": 400, "message": "High calorie meal — exceeds recommended per-meal limit"},
        "fat":      {"limit": 15,  "message": "High fat content — not ideal for weight loss"},
    },
    "High Cholesterol": {
        "fat":      {"limit": 12, "message": "High fat alert — limit saturated fat intake"},
    },
    "PCOD / PCOS": {
        "carbs":    {"limit": 40, "message": "High carbs — can worsen insulin resistance in PCOD"},
        "gi":       {"limit": 55, "message": "High GI food — avoid for better hormone regulation"},
    },
    "Gym / Muscle Gain": {
        "protein":  {"limit": 20, "message": "Low protein — add a protein source to this meal",
                     "below": True},
    },
    "Child (6-12 years)": {
        "fat":      {"limit": 20, "message": "High fat content — not ideal for children"},
    },
    "Senior Citizen (60+)": {
        "calories": {"limit": 500, "message": "High calorie meal — watch total daily intake"},
        "fat":      {"limit": 15,  "message": "High fat — harder to metabolise for older adults"},
        "carbs":    {"limit": 60,  "message": "High carbs — monitor blood sugar levels"},
    },
}


# Core functions 

def get_gi(food_key: str) -> int:
    """
    Returns GI for any food.
    Checks GI_DB first, falls back to NUTRITION_DB, defaults to 0.
    """
    return GI_DB.get(food_key, NUTRITION_DB.get(food_key, {}).get("gi", 0))


def get_nutrition(food_key: str, grams: float = 100):
    """
    Returns nutrition from local NUTRITION_DB scaled to portion size.
    Returns None if food not in local DB — caller should use
    get_nutrition_with_fallback() for full 101-class coverage.
    """
    data = NUTRITION_DB.get(food_key)
    if not data:
        return None
    scale = grams / 100
    return {
        "calories": round(data["calories"] * scale, 1),
        "protein":  round(data["protein"]  * scale, 1),
        "carbs":    round(data["carbs"]    * scale, 1),
        "fat":      round(data["fat"]      * scale, 1),
        "gi":       data["gi"],
        "source":   "Local Database",
    }


def get_nutrition_with_fallback(food_name: str, grams: int = 100) -> dict:
    """
    Full nutrition lookup for all 101 Food-101 classes.

    Priority:
    1. Local NUTRITION_DB  — instant, no network call
    2. USDA FoodData API   — 300k+ foods, real data
    3. Estimated average   — better than returning zeros
    """
    # 1. Local DB (covers original 10 classes + Indian foods instantly)
    local = get_nutrition(food_name, grams)
    if local:
        return local

    # 2. USDA API (covers all 101 classes + 300k more)
    try:
        from usda_api import get_nutrition_usda
        usda_result = get_nutrition_usda(food_name, grams)
        if usda_result:
            usda_result["gi"]     = get_gi(food_name)  
            usda_result["source"] = "USDA FoodData Central"
            return usda_result
    except Exception as e:
        print(f"⚠️ USDA API error for '{food_name}': {e}")

    # 3. Estimated fallback — never return zeros
    print(f"⚠️ No data found for '{food_name}' — using estimate")
    scale = grams / 100
    return {
        "calories": round(150 * scale, 1),
        "protein":  round(5   * scale, 1),
        "carbs":    round(15  * scale, 1),
        "fat":      round(5   * scale, 1),
        "gi":       get_gi(food_name),
        "source":   "Estimated Average",
    }


def get_warnings(food_name, nutrition, profile):
    warnings = []
    food_name = food_name.lower()
    
    # Extract common variables for readability
    sugar = nutrition.get("sugar", 0)
    gi = nutrition.get("gi", 0)
    sodium = nutrition.get("sodium", 0)
    sat_fat = nutrition.get("saturated_fat", 0)
    fiber = nutrition.get("fiber", 0)
    protein = nutrition.get("protein", 0)

    # 1. PROFILE-SPECIFIC LOGIC
    
    if profile == "Type 2 Diabetes":
        # Check for refined carbs and hidden sugars
        forbidden = ["ice cream", "cake", "candy", "soda", "syrup", "white bread", "juice", "honey"]
        if any(kw in food_name for kw in forbidden):
            warnings.append(f"🚩 High Glycemic Load: {food_name.capitalize()} contains refined sugars/carbs discouraged for diabetics.")
        
        if gi > 55:
            warnings.append("Glycemic Warning: This item has a Medium/High GI. Pair with fiber to slow glucose absorption.")
        if sugar > 10:
            warnings.append(f"Sugar Alert: {sugar}g of sugar exceeds the recommended per-serving limit for this profile.")

    elif profile == "Hypertension (High BP)":
        # Focus on Sodium and Saturated Fats
        salty_items = ["pizza", "burger", "chips", "pickle", "processed meat", "canned soup", "soy sauce"]
        if any(kw in food_name for kw in salty_items) or sodium > 350:
            warnings.append("Sodium Warning: High salt content detected. This can increase blood pressure and water retention.")
        
        if sat_fat > 5:
            warnings.append("Saturated Fat Alert: High intake is linked to arterial stiffness.")

    elif profile == "High Cholesterol":
        # Focus on Saturated Fat and Lack of Fiber
        if sat_fat > 4:
            warnings.append("Lipid Warning: Saturated fats can increase LDL (bad cholesterol) levels.")
        if "fried" in food_name or "butter" in food_name:
            warnings.append("Trans-Fat Risk: Fried or buttery foods are highly discouraged for heart health.")
        if fiber < 2:
            warnings.append("Fiber Deficiency: Low fiber prevents the natural removal of cholesterol from the body.")

    elif profile == "PCOD / PCOS":
        # Focus on Insulin Sensitivity (Low GI is key)
        if gi > 50 or "dairy" in food_name or "milk" in food_name:
            warnings.append("Hormonal Impact: High GI or heavy dairy may aggravate insulin resistance in PCOS profiles.")
        if sugar > 8:
            warnings.append("Inflammation Risk: Refined sugar can trigger androgen spikes.")

    elif profile == "Gym / Muscle Gain":
        # Focus on Protein Density
        if protein < 10 and nutrition.get("calories", 0) > 400:
            warnings.append("Empty Calories: High calorie count with low protein density is suboptimal for lean muscle gain.")

    # 2. GENERAL HEALTH TAGS (Applied to everyone)
    if "fried" in food_name:
        warnings.append("Preparation Warning: Deep-frying adds carcinogens and high-calorie density.")
    
    return warnings

def determine_risk_level(warnings, profile):
    """
    Logic to determine the card color: 
    0-1 warnings = low, 2 = moderate, 3+ or '🚩' = high
    """
    if any("🚩" in w or "Violation" in w or "Discouraged" in w for w in warnings):
        return "high"
    
    count = len(warnings)
    if count == 0: return "low"
    if count <= 2: return "moderate"
    return "high"


def get_safer_alternatives(food_key: str, profile: str) -> list:
    """
    Provides a list of safer, healthier food alternative suggestions 
    based on the food queried.
    """
    alternatives_map = {
        "pizza": ["Whole wheat thin crust pizza", "Caesar salad"],
        "hamburger": ["Grilled chicken sandwich", "Turkey burger"],
        "samosa": ["Baked samosa", "Roasted chana"],
        "ice_cream": ["Greek yogurt", "Fruit sorbet"],
        "fried_rice": ["Brown rice", "Quinoa salad"],
        "pancakes": ["Oatmeal", "Protein pancakes"],
        "cup_cakes": ["Fresh fruit", "Dark chocolate"],
        "gulab_jamun": ["Fruit salad", "Sugar-free rasgulla"],
        "jalebi": ["Fresh fruit with honey"],
        "biryani": ["Pulao with extra veggies", "Quinoa biryani"],
        "naan": ["Whole wheat roti"],
        "vada_pav": ["Sprout salad", "Poha"],
        "french_fries": ["Baked sweet potato fries", "Side salad"],
    }
    
    # Return mapped alternatives or a generic fallback
    return alternatives_map.get(food_key, ["A smaller portion size", "Pair with a high-fiber salad"])


def search_local_foods(query: str, max_results: int = 6) -> list:
    """
    Searches the NUTRITION_DB for a food name.
    Returns a list of dictionaries formatted for the frontend search results.
    """
    query = query.lower().strip()
    results = []
    
    for key, data in NUTRITION_DB.items():
        display_name = key.replace("_", " ").title()
        if query in key.lower() or query in display_name.lower():
            hit = {
                "food_key": key,
                "display_name": display_name,
                "calories": data["calories"],
                "protein": data["protein"],
                "carbs": data["carbs"],
                "fat": data["fat"],
                "gi": get_gi(key)
            }
            results.append(hit)
            
        if len(results) >= max_results:
            break
            
    return results