from pydantic import BaseModel
from typing import List, Optional

class NutritionData(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    gi: Optional[int]

class PredictionResponse(BaseModel):
    food_name: str
    confidence: float
    nutrition: NutritionData
    warnings: List[str]
    alternatives: List[str]