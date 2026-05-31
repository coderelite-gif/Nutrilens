# 🥗 NutriLens
### AI-Powered Food Recognition & Personalised Nutrition Analysis

> Point your camera at any food. Get instant nutrition facts, glycemic index, and personalised health warnings — all tailored to your health condition.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.x-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

---

## 📌 Overview

NutriScan is an end-to-end food intelligence system that combines deep learning image classification with a health-aware nutrition engine. Upload a photo of your meal and NutriLens will:

- **Identify** the food using a fine-tuned EfficientNetB0 model (101 food classes)
- **Retrieve** complete nutritional data including Glycemic Index, sodium, saturated fat, and sugar
- **Evaluate** whether the food is safe for your specific health condition
- **Scale** all values live to your exact portion size
- **Track** your daily macros against personalised targets

Built as a full-stack web application with both a production React + FastAPI stack and a self-contained Streamlit prototype.

---

## 🎯 Model Performance

| Metric | Value |
|---|---|
| Architecture | EfficientNetB0 (Transfer Learning) |
| Dataset | Food-101 (101,000 images, 101 classes) |
| Training Strategy | Two-phase fine-tuning |
| **Validation Accuracy** | **83.46%** |
| **Test Accuracy** | **82.57%** |
| Model Size | ~22 MB (.h5) |
| Inference Time | ~45ms (CPU) |

---

## 🏥 Supported Health Profiles

| Profile | Key Metrics Monitored |
|---|---|
| Type 2 Diabetes | Glycemic Load, Sugar, Carbohydrates |
| Hypertension | Sodium, Saturated Fat |
| Weight Loss / Obesity | Calories, Sugar |
| Gym / Muscle Gain | Protein Density, Calories |
| Healthy Adult | Calories, Sodium |

Each profile returns a **SUITABLE / CAUTION / UNSUITABLE** risk badge with specific warnings and healthier food alternatives.

---

## 🗂️ Project Structure

```
NutriLens  /
├── backend/
│   ├── api.py                  # FastAPI server & endpoints
│   ├── predict.py              # EfficientNetB0 inference module
│   ├── nutrition_data.py       # Nutrition DB, health profiles, suitability logic
│   ├── usda_api.py             # USDA FoodData Central API client + cache
│   ├── schemas.py              # Pydantic request/response models
│   └── class_names.json        # 101 Food-101 class label mapping
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main app — Analyse, Daily Log, Settings tabs
│   │   └── components/
│   │       ├── NutritionCard.jsx   # Result card with macro tiles & risk badge
│   │       ├── Suitability.jsx     # Client-side health suitability engine
│   │       └── ImageUploader.jsx   # File upload component
│   ├── package.json
│   └── vite.config.js
│
├── per_class_accuracy.png      # Per-class accuracy chart
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- The trained model file (see [Model](#-model) section below)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/NutriScan.git
cd NutriLens
```

---

### 2. Backend (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn tensorflow pillow numpy requests pydantic

# Start the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

API will be live at `http://localhost:8000`
Auto-generated docs at `http://localhost:8000/docs`

---

### 3. Frontend (React)

```bash
cd frontend

npm install
npm run dev
```

Frontend will be live at `http://localhost:5173`

---
---

## 🤖 Model

The trained model file (`efficientnet_b0_101_best.h5`, ~38MB) is not included in this repository.

**To use the model:**
- Train it yourself using the training notebook: `food recognition and nutrition analysis.ipynb`
- Or place a pre-trained `.h5` file in the `backend/` directory

**Training summary:**
- Base: `EfficientNetB0` with ImageNet weights
- Phase 1: 10 epochs, frozen base, LR = 1e-3
- Phase 2: 20 epochs, full fine-tune, LR = 1e-4
- Augmentation: RandomFlip, RandomRotation, RandomZoom, RandomContrast

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/analyze-image` | POST | Upload image → returns food name, nutrition, risk level, warnings, alternatives |
| `/api/recalculate-status` | POST | Recalculate suitability for a given nutrition + health profile |
| `/api/health` | GET | Server health check |

**Example request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-image" \
  -F "file=@pizza.jpg" \
  -F "grams=200" \
  -F "health_profile=Type 2 Diabetes"
```

---

## 🍱 Features

- **Image-based food recognition** — 101 food classes, top-3 predictions with confidence scores
- **Live portion scaling** — drag a slider (50g–1000g) and all nutrition values + risk assessments update instantly
- **Glycemic Load calculation** — computed per serving, not just per 100g
- **Indian food coverage** — extended nutrition database with 30+ Indian dishes (samosa, biryani, dal makhani, jalebi, and more)
- **USDA API fallback** — 300,000+ foods via USDA FoodData Central for anything outside local DB
- **Daily macro tracker** — log meals, track cumulative calories/protein/carbs/fat vs profile targets
- **Safer alternatives** — condition-specific healthier food suggestions per risk flag

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| ML Model | TensorFlow / Keras — EfficientNetB0 |
| Backend | FastAPI + Uvicorn |
| Data Validation | Pydantic |
| Frontend | React 18 + Vite + Tailwind CSS |
| Prototype | Streamlit |
| External Data | USDA FoodData Central API |
| Dataset | Food-101 (Bossard et al., 2014) |

---

## 📊 Food-101 Classes

The model recognises 101 food categories including: apple pie, baklava, bibimbap, caesar salad, cheesecake, chicken curry, chocolate cake, churros, dumplings, eggs benedict, falafel, french fries, fried rice, guacamole, hamburger, hot dog, ice cream, lasagna, macarons, omelette, pad thai, pancakes, pizza, ramen, samosa, sashimi, spaghetti carbonara, sushi, tacos, tiramisu, waffles, and 71 more.

---

## 🙏 Acknowledgements

- [Food-101 Dataset](https://data.vision.ee.ethz.ch/cvl/datasets_extra/food-101/) — Bossard et al., ECCV 2014
- [EfficientNet](https://arxiv.org/abs/1905.11946) — Tan & Le, ICML 2019
- [USDA FoodData Central](https://fdc.nal.usda.gov/) — U.S. Department of Agriculture
- [International GI Database](https://glycemicindex.com/) — University of Sydney

---

<p align="center">Made with ❤️ for smarter eating</p>
