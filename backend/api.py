from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from predict import predict_food
from nutrition_data import get_warnings, get_safer_alternatives
import tempfile
import os

app = FastAPI(title="NutriScan AI Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
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
    # 1. Save uploaded image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # 2. Run prediction
        predictions = predict_food(tmp_path, grams=int(grams))
        
        if not predictions:
            return {"success": False, "message": "No food detected"}

        top_match = predictions[0]
        
        # 3. Get warnings based on the selected health profile
        warnings = get_warnings(top_match["food"], top_match["nutrition"], health_profile)
        
        # 4. Determine Risk Level Logic
        # Low: 0-1 warnings | Moderate: 2-3 warnings | High: 4+ warnings
        risk_count = len(warnings)
        if risk_count <= 1:
            risk_level = "low"
        elif risk_count <= 3:
            risk_level = "moderate"
        else:
            risk_level = "high"

        # 5. Get alternatives
        alternatives = get_safer_alternatives(top_match["food"], health_profile)

        return {
            "success": True,
            "data": {
                "food_name": top_match["food"],
                "confidence": top_match["confidence"], # Float between 0 and 1
                "nutrition": top_match["nutrition"],   # Expecting: cals, protein, carbs, fat, gi
                "warnings": warnings,
                "risk_level": risk_level,              # 'low', 'moderate', or 'high'
                "alternatives": alternatives,
                "top_matches": predictions[:3]         # Send top 3 items for the UI badges
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
        
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/api/health")
async def health_check():
    return {"status": "online"}