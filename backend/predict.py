# predict.py

import os
import requests
import tensorflow as tf
import numpy as np
from PIL import Image
import json

from nutrition_data import get_nutrition_with_fallback

preprocess_input = tf.keras.applications.efficientnet.preprocess_input

MODEL_PATH       = 'efficientnet_b0_101_best.h5'
CLASS_NAMES_PATH = 'class_names.json'
MODEL_URL        = "https://huggingface.co/SuperEliteAgent/nutrilens-model/resolve/main/efficientnet_b0_101_best.h5"

# ---- Download model if not present ----
if not os.path.exists(MODEL_PATH):
    print("Model not found locally. Downloading from Hugging Face...")
    r = requests.get(MODEL_URL, stream=True)
    r.raise_for_status()
    with open(MODEL_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Model downloaded successfully.")

# ---- Load model ----
def _load():
    print("Loading EfficientNetB0...")
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)
    print(f"✅ Model loaded — {len(class_names)} classes")
    return model, class_names

_keras_model, CLASS_NAMES = _load()

@tf.function(reduce_retracing=True)
def _run_inference(input_tensor):
    return _keras_model(input_tensor, training=False)

# ---- Preprocess ----
def _preprocess(image_path: str):
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    arr = np.array(img, dtype=np.float32)
    arr = preprocess_input(arr)
    return tf.expand_dims(arr, axis=0)

# ---- Predict ----
def predict_food(image_path: str, grams: int = 100, top_k: int = 3):

    inp   = _preprocess(image_path)
    probs = _run_inference(inp).numpy()[0]

    top_indices = np.argsort(probs)[::-1][:top_k]

    results = []

    for i in top_indices:
        food_key   = CLASS_NAMES[i]
        food_name  = food_key.replace("_", " ").title()
        confidence = round(float(probs[i]) * 100, 1)

        nutrition = get_nutrition_with_fallback(food_key, grams)

        results.append({
            "food":       food_name,
            "food_key":   food_key,
            "confidence": confidence,
            "nutrition":  nutrition,
        })

    return results