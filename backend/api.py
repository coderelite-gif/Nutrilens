from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from predict import predict_food
from nutrition_data import get_warnings, get_safer_alternatives
import tempfile
import os

app = FastAPI(title="NutriLens AI Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nutrilens-tan-three.vercel.app",
        "https://nutrilens-3ekn3vyvq-coderelite-gifs-projects.vercel.app",
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    grams: int = Form(100),
    health_profile: str = Form("Healthy Adult")
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        predictions = predict_food(tmp_path, grams=int(grams))

        if not predictions:
            return {"success": False, "message": "No food detected"}

        top_match = predictions[0]

        warnings = get_warnings(top_match["food"], top_match["nutrition"], health_profile)

        risk_count = len(warnings)
        if risk_count <= 1:
            risk_level = "low"
        elif risk_count <= 3:
            risk_level = "moderate"
        else:
            risk_level = "high"

        alternatives = get_safer_alternatives(top_match["food"], health_profile)

        return {
            "success": True,
            "data": {
                "food_name":   top_match["food"],
                "confidence":  top_match["confidence"],
                "nutrition":   top_match["nutrition"],
                "warnings":    warnings,
                "risk_level":  risk_level,
                "alternatives": alternatives,
                "top_matches": predictions[:3]
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/api/recalculate-status")
async def recalculate_status(payload: dict):
    try:
        food_name   = payload.get("food_name", "")
        nutrition   = payload.get("nutrition", {})
        profile     = payload.get("profile", "Healthy Adult")

        warnings = get_warnings(food_name, nutrition, profile)

        risk_count = len(warnings)
        if risk_count <= 1:
            risk_level = "low"
        elif risk_count <= 3:
            risk_level = "moderate"
        else:
            risk_level = "high"

        return {
            "success":    True,
            "warnings":   warnings,
            "risk_level": risk_level
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/health")
async def health_check():
    return {"status": "online"}