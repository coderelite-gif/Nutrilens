# app.py
import streamlit as st
from PIL import Image
import os
import datetime

from nutrition_data import (
    HEALTH_PROFILES, get_warnings,
    get_safer_alternatives, NUTRITION_DB,
    search_local_foods, INDIAN_FOOD_CATEGORIES,get_gi,
)

# ── Page Config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Food Nutrition Analyzer",
    page_icon="🍽️",
    layout="centered"
)

# ── Constants ─────────────────────────────────────────────────────
CONDITION_TIPS = {
    "Type 2 Diabetes":        "Keep each meal under 45g carbs. Prefer low GI foods (GI < 55).",
    "Hypertension (High BP)": "Limit sodium and saturated fat. Avoid fried and processed foods.",
    "Weight Loss / Obesity":  "Stay under 400 kcal per meal. Prefer high protein, low fat options.",
    "High Cholesterol":       "Avoid high saturated fat foods. Prefer lean proteins and vegetables.",
    "PCOD / PCOS":            "Low GI diet is critical. Avoid refined carbs and sugary foods.",
    "Gym / Muscle Gain":      "Prioritise high protein meals. Target 25-30g protein per meal.",
    "Child (6-12 years)":     "Balanced nutrition is key. Ensure adequate protein and calcium.",
    "Senior Citizen (60+)":   "Prefer easily digestible foods. Maintain adequate protein intake.",
    "Healthy Adult":          "Maintain a balanced diet with all macronutrients.",
}

# ── Session State ─────────────────────────────────────────────────
if "meal_log"           not in st.session_state:
    st.session_state.meal_log           = []
if "search_results"     not in st.session_state:
    st.session_state.search_results     = []
if "search_query"       not in st.session_state:
    st.session_state.search_query       = ""
if "selected_food_key"  not in st.session_state:
    st.session_state.selected_food_key  = None
if "usda_result"        not in st.session_state:
    st.session_state.usda_result        = None

# ── Load Model (once) ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    from predict import predict_food
    return predict_food

predict_food = load_model()

# ── Sidebar ───────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
grams = st.sidebar.slider(
    "Portion Size (grams)",
    min_value=50, max_value=500, value=100, step=10,
    help="Adjust portion size to scale nutrition values"
)
st.sidebar.divider()
st.sidebar.header("🩺 Health Profile")
profile = st.sidebar.selectbox(
    "Select your condition",
    list(HEALTH_PROFILES.keys()),
    index=0
)
st.sidebar.divider()
st.sidebar.markdown("### 🥗 Supported Foods")
for food in ["🍕 Pizza", "🍔 Hamburger", "🍣 Sushi", "🍦 Ice Cream",
             "🍚 Fried Rice", "🍳 Omelette", "🥞 Pancakes",
             "🥟 Samosa", "🧁 Cup Cakes", "🥗 Caesar Salad"]:
    st.sidebar.write(food)

if profile != "Healthy Adult":
    st.sidebar.info(f"💡 {CONDITION_TIPS[profile]}")

# ── Header ────────────────────────────────────────────────────────
st.title("🍽️ Food Recognition & Nutrition Analysis")
st.write("Upload a food image to identify it and get its complete nutritional breakdown.")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📸 Analyse Food", "📊 Daily Log", "🔎 Food Search"])


# ════════════════════════════════════════════════════════════════
# TAB 1 — Food Analysis
# ════════════════════════════════════════════════════════════════
with tab1:
    uploaded_file = st.file_uploader(
        "Upload a food image",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG"
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.divider()

        temp_path = "temp_image.jpg"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Analyzing your food... please wait"):
            results = predict_food(temp_path, grams)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        # ── Prediction results ────────────────────────────────────
        st.subheader("🔍 Analysis Results")
        st.caption(f"Nutrition values shown for {grams}g portion")

        for i, result in enumerate(results):
            food_name  = result["food"]
            food_key   = result["food_key"]
            confidence = result["confidence"]
            nutrition  = result["nutrition"]
            badge = "🟢" if confidence >= 70 else ("🟡" if confidence >= 40 else "🔴")

            with st.expander(
                f"{badge} #{i+1}  {food_name}  —  {confidence}% confidence",
                expanded=(i == 0)
            ):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🔥 Calories", f"{nutrition['calories']} kcal")
                col2.metric("💪 Protein",  f"{nutrition['protein']} g")
                col3.metric("🍞 Carbs",    f"{nutrition['carbs']} g")
                col4.metric("🧈 Fat",      f"{nutrition['fat']} g")
                st.write("Confidence Score:")
                st.progress(int(confidence))

        st.divider()

        # ── Top result details ────────────────────────────────────
        top      = results[0]
        food_key = top["food_key"]

        gi = get_gi(food_key)
        if gi != "N/A":
            if gi == 0:   gi_label = "🟢 None / Negligible (GI: 0)"
            elif gi < 55: gi_label = f"🟢 Low (GI: {gi})"
            elif gi < 70: gi_label = f"🟡 Medium (GI: {gi})"  
            else:         gi_label = f"🔴 High (GI: {gi})"  
            st.write(f"**Glycemic Index:** {gi_label}")

        warnings = get_warnings(food_key, top["nutrition"], profile)
        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w}")
        elif profile != "Healthy Adult":
            st.success(f"✅ Safe for {profile}")

        if warnings:
            alternatives = get_safer_alternatives(food_key, profile)
            if alternatives:
                st.info(f"💡 **Safer alternatives for {profile}:** {', '.join(alternatives)}")

        st.subheader("📊 Top Prediction Summary")
        st.success(f"Most likely: **{top['food']}** with **{top['confidence']}%** confidence")

        n     = top["nutrition"]
        total = n["protein"] + n["carbs"] + n["fat"]
        if total > 0:
            st.write("**Macronutrient Breakdown:**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Protein %", f"{round(n['protein']/total*100)}%")
            col2.metric("Carbs %",   f"{round(n['carbs']/total*100)}%")
            col3.metric("Fat %",     f"{round(n['fat']/total*100)}%")

        top_warnings = get_warnings(food_key, top["nutrition"], profile)
        risk_score   = 0
        if gi != "N/A":
            if gi > 70:   risk_score += 7
            elif gi > 55: risk_score += 5
        for w in top_warnings:
            w_lower = w.lower()
            if "carbs"     in w_lower: risk_score += 4
            elif "fat"     in w_lower: risk_score += 3
            elif "calorie" in w_lower: risk_score += 2
            else:                      risk_score += 2
        risk_score = min(10, risk_score)

        if profile != "Healthy Adult":
            st.subheader("🩺 Meal Risk Assessment")
            if risk_score >= 7:
                st.error(f"Risk Score: {risk_score}/10 🔴 High Risk for {profile}")
            elif risk_score >= 4:
                st.warning(f"Risk Score: {risk_score}/10 🟡 Moderate Risk for {profile}")
            else:
                st.success(f"Risk Score: {risk_score}/10 🟢 Low Risk for {profile}")

        st.divider()
        if st.button("➕ Add to Daily Log", key="tab1_add"):
            st.session_state.meal_log.append({
                "food":      top["food"],
                "grams":     grams,
                "nutrition": top["nutrition"],
                "time":      datetime.datetime.now().strftime("%I:%M %p"),
                "source":    "Image scan",
            })
            st.success(f"✅ {top['food']} ({grams}g) added to your daily log!")

    else:
        st.info("👆 Upload a food image above to get started!")
        st.markdown("""
### How it works:
1. 📸 Upload a photo of your food
2. 🤖 AI identifies the food using deep learning
3. 📊 Get instant nutrition breakdown
4. ⚖️ Adjust portion size using the sidebar slider
        """)


# ════════════════════════════════════════════════════════════════
# TAB 2 — Daily Macro Tracker
# ════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📊 Daily Meal Log")

    if not st.session_state.meal_log:
        st.info("No meals logged yet. Analyse a food and click 'Add to Daily Log'.")
    else:
        for i, meal in enumerate(st.session_state.meal_log):
            with st.expander(
                f"🍽️ {meal['time']} — {meal['food']} ({meal['grams']}g)",
                expanded=False
            ):
                n = meal["nutrition"]
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("🔥 Calories", f"{n['calories']} kcal")
                c2.metric("💪 Protein",  f"{n['protein']} g")
                c3.metric("🍞 Carbs",    f"{n['carbs']} g")
                c4.metric("🧈 Fat",      f"{n['fat']} g")
                st.caption(f"Source: {meal.get('source', 'Image scan')}")

                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.meal_log.pop(i)
                    st.rerun()

        st.divider()

        totals = {
            "calories": round(sum(m["nutrition"]["calories"] for m in st.session_state.meal_log), 1),
            "protein":  round(sum(m["nutrition"]["protein"]  for m in st.session_state.meal_log), 1),
            "carbs":    round(sum(m["nutrition"]["carbs"]    for m in st.session_state.meal_log), 1),
            "fat":      round(sum(m["nutrition"]["fat"]      for m in st.session_state.meal_log), 1),
        }

        st.subheader("📈 Today's Total")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Calories", f"{totals['calories']} kcal")
        c2.metric("💪 Protein",  f"{totals['protein']} g")
        c3.metric("🍞 Carbs",    f"{totals['carbs']} g")
        c4.metric("🧈 Fat",      f"{totals['fat']} g")

        st.subheader(f"🎯 Progress vs {profile} Daily Targets")
        targets = HEALTH_PROFILES[profile]

        for nutrient, label in [
            ("calories", "🔥 Calories"),
            ("protein",  "💪 Protein"),
            ("carbs",    "🍞 Carbs"),
            ("fat",      "🧈 Fat"),
        ]:
            consumed  = totals[nutrient]
            target    = targets[nutrient]
            pct       = min(int((consumed / target) * 100), 100)
            remaining = max(0, round(target - consumed, 1))
            over      = consumed > target
            st.write(f"**{label}:** {consumed} / {target} "
                     f"{'⚠️ over limit!' if over else f'— {remaining} remaining'}")
            st.progress(pct)

        st.divider()
        if st.button("🗑️ Clear All Meals"):
            st.session_state.meal_log = []
            st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 3 — Manual Food Search
# ════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔎 Manual Food Search")
    st.write(
        "Search for any food by name — includes Indian dishes, packaged foods, "
        "and a global database of 300,000+ items via USDA."
    )

    # ── Search bar ────────────────────────────────────────────────
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input(
            "Food name",
            placeholder="e.g. dal makhani, biryani, paneer, omelette...",
            label_visibility="collapsed",
            key="food_search_input",
        )
    with col_btn:
        search_clicked = st.button("🔍 Search", use_container_width=True)

    search_grams = st.slider(
        "Portion size (grams)", 50, 500, 100, 10, key="search_grams_slider"
    )

    # ── Quick-pick Indian food categories ─────────────────────────
    with st.expander("🇮🇳 Browse Indian Foods by Category", expanded=False):
        for category, foods in INDIAN_FOOD_CATEGORIES.items():
            st.markdown(f"**{category}**")
            cols = st.columns(4)
            for idx, food_key in enumerate(foods):
                label = food_key.replace("_", " ").title()
                if cols[idx % 4].button(label, key=f"quick_{food_key}"):
                    st.session_state.selected_food_key = food_key
                    st.session_state.search_results    = []
                    st.session_state.usda_result       = None
            st.markdown("---")

    # ── Run search ────────────────────────────────────────────────
    if search_clicked and query.strip():
        # 1. Search local DB first (instant)
        local_hits = search_local_foods(query.strip(), max_results=6)
        st.session_state.search_results   = local_hits
        st.session_state.selected_food_key = None
        st.session_state.usda_result       = None

        # 2. Also fire off USDA for anything not in local DB
        if not local_hits:
            with st.spinner("Searching USDA database..."):
                try:
                    from usda_api import search_food_usda
                    usda = search_food_usda(query.strip())
                    st.session_state.usda_result = usda
                except Exception as e:
                    st.session_state.usda_result = None
                    st.warning(f"USDA search failed: {e}")

    # ── Display search results as selectable cards ─────────────────
    if st.session_state.search_results:
        st.markdown(f"**Found {len(st.session_state.search_results)} matches in local database:**")
        for hit in st.session_state.search_results:
            fk   = hit["food_key"]
            name = hit["display_name"]
            cal  = hit["calories"]
            gi   = hit.get("gi", 0)
            gi_badge = "🟢" if gi < 55 else ("🟡" if gi < 70 else "🔴")

            col_info, col_pick = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"**{name}** &nbsp; — &nbsp; "
                    f"🔥 {cal} kcal &nbsp; | &nbsp; "
                    f"💪 {hit['protein']}g protein &nbsp; | &nbsp; "
                    f"🍞 {hit['carbs']}g carbs &nbsp; | &nbsp; "
                    f"🧈 {hit['fat']}g fat &nbsp; | &nbsp; "
                    f"{gi_badge} GI {gi}"
                )
            with col_pick:
                if st.button("Select", key=f"select_{fk}"):
                    st.session_state.selected_food_key = fk
                    st.session_state.usda_result       = None
        st.divider()

    # ── USDA fallback result ───────────────────────────────────────
    elif st.session_state.usda_result:
        usda = st.session_state.usda_result
        st.markdown(f"**Found via USDA:** {usda.get('usda_name', query)}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔥 Calories", f"{usda['calories']} kcal")
        col2.metric("💪 Protein",  f"{usda['protein']} g")
        col3.metric("🍞 Carbs",    f"{usda['carbs']} g")
        col4.metric("🧈 Fat",      f"{usda['fat']} g")
        st.caption("Source: USDA FoodData Central | Values per 100g")

        scaled_usda = {k: round(v * search_grams / 100, 1)
                       for k, v in usda.items()
                       if k in ("calories", "protein", "carbs", "fat")}
        scaled_usda["gi"] = 0
        if st.button("➕ Add to Daily Log", key="usda_log"):
            st.session_state.meal_log.append({
                "food":      usda.get("usda_name", query).title(),
                "grams":     search_grams,
                "nutrition": scaled_usda,
                "time":      datetime.datetime.now().strftime("%I:%M %p"),
                "source":    "USDA search",
            })
            st.session_state.usda_result = None # Clear the card
            st.toast("✅ Added to daily log!")  # Use toast instead of success
            st.rerun()                          # Force immediate UI refresh

    elif search_clicked and query.strip() and not st.session_state.search_results:
        st.error("❌ No results found. Try a different spelling or a simpler term.")

    # ── Detailed card for selected food ───────────────────────────
    if st.session_state.selected_food_key:
        food_key = st.session_state.selected_food_key
        from nutrition_data import get_nutrition, get_gi

        nutrition = get_nutrition(food_key, search_grams)
        gi        = get_gi(food_key)
        name      = food_key.replace("_", " ").title()

        st.markdown(f"### 🍽️ {name}")
        st.caption(f"Nutrition for {search_grams}g portion | Source: Local Database")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔥 Calories", f"{nutrition['calories']} kcal")
        c2.metric("💪 Protein",  f"{nutrition['protein']} g")
        c3.metric("🍞 Carbs",    f"{nutrition['carbs']} g")
        c4.metric("🧈 Fat",      f"{nutrition['fat']} g")

        # GI label
        if gi == 0:   gi_label = "🟢 None / Negligible (GI: 0)"
        elif gi < 55: gi_label = f"🟢 Low (GI: {gi})"
        elif gi < 70: gi_label = f"🟡 Medium (GI: {gi})"
        else:         gi_label = f"🔴 High (GI: {gi})"
        st.write(f"**Glycemic Index:** {gi_label}")

        # Macronutrient breakdown bar
        total_macro = nutrition["protein"] + nutrition["carbs"] + nutrition["fat"]
        if total_macro > 0:
            p_pct = round(nutrition["protein"] / total_macro * 100)
            c_pct = round(nutrition["carbs"]   / total_macro * 100)
            f_pct = round(nutrition["fat"]     / total_macro * 100)
            st.write("**Macronutrient Breakdown:**")
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Protein %", f"{p_pct}%")
            mc2.metric("Carbs %",   f"{c_pct}%")
            mc3.metric("Fat %",     f"{f_pct}%")

        # Health warnings
        warnings = get_warnings(food_key, nutrition, profile)
        if warnings:
            for w in warnings:
                st.warning(f"⚠️ {w}")
        elif profile != "Healthy Adult":
            st.success(f"✅ Safe for {profile}")

        # Safer alternatives
        if warnings:
            alts = get_safer_alternatives(food_key, profile)
            if alts:
                st.info(f"💡 **Safer alternatives for {profile}:** {', '.join(alts)}")

        # Risk score
        risk_score = 0
        if gi > 70:   risk_score += 7
        elif gi > 55: risk_score += 5
        for w in warnings:
            w_lower = w.lower()
            if "carbs"     in w_lower: risk_score += 4
            elif "fat"     in w_lower: risk_score += 3
            elif "calorie" in w_lower: risk_score += 2
            else:                      risk_score += 2
        risk_score = min(10, risk_score)

        if profile != "Healthy Adult":
            st.subheader("🩺 Meal Risk Assessment")
            if risk_score >= 7:
                st.error(f"Risk Score: {risk_score}/10 🔴 High Risk for {profile}")
            elif risk_score >= 4:
                st.warning(f"Risk Score: {risk_score}/10 🟡 Moderate Risk for {profile}")
            else:
                st.success(f"Risk Score: {risk_score}/10 🟢 Low Risk for {profile}")

        st.divider()
        if st.button("➕ Add to Daily Log", key="search_log_btn"):
            st.session_state.meal_log.append({
                "food":      name,
                "grams":     search_grams,
                "nutrition": nutrition,
                "time":      datetime.datetime.now().strftime("%I:%M %p"),
                "source":    "Manual search",
            })
            st.session_state.selected_food_key = None # Clear the card
            st.toast(f"✅ {name} ({search_grams}g) added to your daily log!") # Toast
            st.rerun()                                # Force immediate UI refresh
            
    # ── Empty state hint ──────────────────────────────────────────
    if (not st.session_state.search_results
            and not st.session_state.selected_food_key
            and not st.session_state.usda_result):
        st.markdown("""
---
### How to use:
- **Search** any food by name — works for Indian dishes, global foods & packaged items
- **Browse** Indian foods by category using the expander above
- **Select** a result to see full nutrition, GI score & health warnings
- **Adjust** portion size with the slider, then add to your Daily Log

> 💡 Can't find an Indian dish? Try searching the main ingredient  
> e.g. search *"paneer"* instead of *"paneer lababdar"*
        """)