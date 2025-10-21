"""
predict_all_compatibilities_exact_features.py
- Now GUI-ready: allows passing student profile directly from PyQt table
"""

import os
import glob
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

MODELS_DIR = "sources/model"
RESULTS_DIR = "sources/results"
os.makedirs(RESULTS_DIR, exist_ok=True)


# =============================
# LOADING MODEL AND FEATURES
# =============================
def load_all_specialization_models(models_dir=MODELS_DIR):
    model_folders = sorted([p for p in glob.glob(os.path.join(models_dir, "*_model")) if os.path.isdir(p)])
    all_models = {}
    for folder in model_folders:
        spec_safe = os.path.basename(folder)
        spec_display = spec_safe.replace("_model", "").replace("_", " ")
        try:
            model = joblib.load(os.path.join(folder, "model.joblib"))
            scaler = joblib.load(os.path.join(folder, "scaler.joblib"))
            le = joblib.load(os.path.join(folder, "label_encoder.joblib"))
            features_path = os.path.join(folder, "features.txt")
            if not os.path.exists(features_path):
                print(f"[WARN] features.txt missing in {folder} — skipping")
                continue
            with open(features_path, "r", encoding="utf-8") as f:
                features = [line.strip() for line in f if line.strip()]
            all_models[spec_display] = {
                "model": model,
                "scaler": scaler,
                "le": le,
                "features": features,
                "model_dir": folder
            }
            print(f"[OK] Loaded model for specialization: '{spec_display}' ({len(features)} features)")
        except Exception as e:
            print(f"[ERROR] Failed loading model folder {folder}: {e}")
    return all_models


def union_all_features(all_models):
    feat_set = set()
    for spec_data in all_models.values():
        feat_set.update(spec_data["features"])
    return sorted(feat_set)


# =============================
# STUDENT PROFILE HANDLING
# =============================
def generate_dummy_student(all_features, seed=None):
    rng = np.random.default_rng(seed)

    # Randomly assign a "student type" or personality
    student_type = rng.choice([
        "tech_strong",      # great in CPE, ECE, TECH, etc.
        "math_strong",      # excels in math/science
        "balanced",         # roughly good at everything
        "lazy",             # weaker overall
        "creative"          # strong in non-technical/general courses
    ])

    profile = {}

    for feat in all_features:
        if any(ch in feat for ch in ["CPE", "ECE", "EE", "TECH"]):
            if student_type == "tech_strong":
                mean, std = 0.85, 0.10
            elif student_type == "lazy":
                mean, std = 0.55, 0.18
            else:
                mean, std = 0.7, 0.15

        elif "MATH" in feat or "STAT" in feat:
            if student_type == "math_strong":
                mean, std = 0.85, 0.10
            elif student_type == "lazy":
                mean, std = 0.5, 0.18
            else:
                mean, std = 0.7, 0.15

        else:
            if student_type == "creative":
                mean, std = 0.82, 0.10
            elif student_type == "lazy":
                mean, std = 0.6, 0.15
            else:
                mean, std = 0.7, 0.14

        val = rng.normal(mean, std)
        val += rng.uniform(-0.05, 0.05)
        val = float(np.clip(val, 0.0, 1.0))

        profile[feat] = val

    profile["_type"] = student_type
    return profile



# =============================
# CORE PREDICTION LOGIC
# =============================
def predict_all_compatibilities(all_models, student_profile):
    rows = []
    for spec, data in all_models.items():
        model = data["model"]
        scaler = data["scaler"]
        le = data["le"]
        features = data["features"]

        x = np.array([student_profile.get(f, 0.0) for f in features], dtype=float).reshape(1, -1)
        try:
            x_scaled = scaler.transform(x)
        except Exception as e:
            x_scaled = x
            print(f"[WARN] scaler.transform failed for specialization '{spec}': {e}")

        try:
            probs = model.predict_proba(x_scaled)[0]
        except Exception:
            try:
                raw_scores = model.decision_function(x_scaled)[0]
                exp = np.exp(raw_scores - np.max(raw_scores))
                probs = exp / exp.sum()
            except Exception:
                pred = model.predict(x_scaled)[0]
                probs = np.array([1.0 if cls == pred else 0.0 for cls in le.classes_])

        for job_label, p in zip(le.classes_, probs):
            rows.append({
                "specialization": spec,
                "job": job_label,
                "compatibility_percent": float(np.round(p * 100.0, 3))
            })

    df = pd.DataFrame(rows)
    return df.sort_values(by="compatibility_percent", ascending=False).reset_index(drop=True)


# =============================
# SAVE RESULTS
# =============================
def save_results(df_results, username, out_path=None):
    user_dir = os.path.join(RESULTS_DIR, username)
    Path(user_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%m_%d")
    base_filename = f"predicted_compatibilities_{date_str}.xlsx"
    if out_path is None:
        out_path = os.path.join(user_dir, base_filename)

    base_name, ext = os.path.splitext(out_path)
    counter = 1
    while os.path.exists(out_path):
        out_path = f"{base_name}_{counter}{ext}"
        counter += 1

    df_results.to_excel(out_path, index=False)
    print(f"[OK] _predict_compatibility.py | Saved compatibility results to: {out_path}")
    return out_path

def predicting_with_profile(username, student_profile):
    """
    This is the clean function to call from PyQt GUI.
    It skips any prompts and uses the student_profile directly.
    """
    print("=== Loading specialization models from:", MODELS_DIR)
    all_models = load_all_specialization_models()
    if not all_models:
        print("No models loaded.")
        return

    df = predict_all_compatibilities(all_models, student_profile)
    
    print("[OK] GUI prediction completed.")
    return  df
