"""
predict_all_compatibilities_exact_features.py

- Loads per-specialization models from sources/model/<spec_safe>_model/
  Each specialization folder must contain:
    - model.joblib
    - scaler.joblib
    - label_encoder.joblib
    - features.txt    (one code_or_trait per line; exactly the features used by the model)

- Two ways to obtain an input student profile:
    1) generate_dummy_student(all_features)  -> returns dict {feature: value}
    2) prompt_student_scores(all_features)  -> interactive console prompt to enter scores

- Produces a DataFrame with:
    specialization | job | compatibility_percent

- Saves the results to sources/results/predicted_compatibilities.xlsx
"""

import os
import glob
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

MODELS_DIR = "sources/model"
RESULTS_DIR = "sources/results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_all_specialization_models(models_dir=MODELS_DIR):
    """
    Find all specialization folders under models_dir that end with _model,
    load model.joblib, scaler.joblib, label_encoder.joblib and features.txt.
    Returns dict:
      { spec_display_name: { "model":..., "scaler":..., "le":..., "features": [...] } }
    """
    model_folders = sorted([p for p in glob.glob(os.path.join(models_dir, "*_model")) if os.path.isdir(p)])
    all_models = {}
    for folder in model_folders:
        spec_safe = os.path.basename(folder)          # e.g., "Software_&_Programming_model" or "Software_Programming_model"
        # convert safe name back to display name: replace underscores with spaces, keep original casing by reading features may include
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
            print(f"[OK] Loaded model for specialization: '{spec_display}' with {len(features)} features and {len(le.classes_)} job classes")
        except Exception as e:
            print(f"[ERROR] Failed loading model folder {folder}: {e}")
    return all_models


def union_all_features(all_models):
    """Return sorted list of all distinct features (code_or_trait) across all specialization models."""
    feat_set = set()
    for spec_data in all_models.values():
        feat_set.update(spec_data["features"])
    all_features = sorted(feat_set)
    return all_features


def generate_dummy_student(all_features, seed=42):
    """
    Generate a dummy student profile mapping every feature -> value in [0,1].
    Values are biased toward realistic ranges (not just uniform).
    Returns dict { feature: float }
    """
    rng = np.random.default_rng(seed)
    profile = {}
    for feat in all_features:
        # heuristic: if feature looks like a course code (contains digits or spaces), produce a wider range,
        # if it looks like a trait name (letters/spaces), give slightly higher mid.
        if any(c.isdigit() for c in feat) or any(ch in feat for ch in ["CPE", "MATH", "ECE", "EE", "TECH"]):
            # course code -> student score realistically 0.3 - 1.0 (30% - 100% normalized)
            val = rng.normal(0.75, 0.12)
        else:
            # trait/skill name -> range 0.25 - 0.98
            val = rng.normal(0.65, 0.18)
        # clip and jitter
        val = float(np.clip(val + rng.uniform(-0.03, 0.03), 0.0, 1.0))
        profile[feat] = val
    return profile


def prompt_student_scores(all_features):
    """
    Interactively prompt the user to enter a score for each feature (course code or trait).
    Accepts values either 0-1 or 0-100 (the function will normalize to 0..1).
    Press Enter to skip a feature (defaults to 0).
    Returns dict { feature: float (0..1) }.
    """
    print("\nEnter the student's score for each course/trait below.")
    print(" - You can enter a percentage (0-100) or a decimal (0-1).")
    print(" - Press Enter to skip a feature (defaults to 0).")
    profile = {}
    for feat in all_features:
        while True:
            try:
                raw = input(f"{feat}: ").strip()
                if raw == "":
                    score = 0.0
                    break
                # allow comma as decimal separator
                raw = raw.replace(",", ".")
                val = float(raw)
                # if user gave 0-100, convert
                if val > 1.0:
                    val = val / 100.0
                score = float(np.clip(val, 0.0, 1.0))
                break
            except ValueError:
                print("  Invalid input. Enter a number (0-100 or 0-1), or Enter to skip.")
        profile[feat] = score
    return profile


def predict_all_compatibilities(all_models, student_profile):
    """
    For each specialization model:
      - align the student_profile to the model's features (missing -> 0)
      - scale with that specialization's scaler
      - call predict_proba, map probabilities to job labels (label encoder)
      - produce list of dicts: {'specialization','job','compatibility_percent'}
    Returns DataFrame sorted by compatibility_percent desc.
    """
    rows = []
    for spec, data in all_models.items():
        model = data["model"]
        scaler = data["scaler"]
        le = data["le"]
        features = data["features"]

        # build X aligned to this model's features
        x = np.array([student_profile.get(f, 0.0) for f in features], dtype=float).reshape(1, -1)
        try:
            x_scaled = scaler.transform(x)
        except Exception as e:
            # if scaler fails (e.g., scaler was fit on different shape) try safe standardization:
            x_scaled = x  # fallback: raw values (not ideal, but keeps pipeline running)
            print(f"[WARN] scaler.transform failed for specialization '{spec}': {e} -- using raw values")

        # get probabilities
        try:
            probs = model.predict_proba(x_scaled)[0]
        except Exception as e:
            # if model doesn't support predict_proba, use normalized decision_function or predict fallback
            try:
                # try decision_function then softmax
                raw_scores = model.decision_function(x_scaled)[0]
                exp = np.exp(raw_scores - np.max(raw_scores))
                probs = exp / exp.sum()
            except Exception:
                # final fallback - one-hot on prediction
                pred = model.predict(x_scaled)[0]
                probs = np.array([1.0 if cls == pred else 0.0 for cls in le.classes_])

        # map job labels and append rows
        for job_label, p in zip(le.classes_, probs):
            rows.append({
                "specialization": spec,
                "job": job_label,
                "compatibility_percent": float(np.round(p * 100.0, 3))
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(by="compatibility_percent", ascending=False).reset_index(drop=True)
    return df


def save_results(df_results, out_path=None):
    """Save DataFrame to Excel (no styling). Returns saved path."""
    if out_path is None:
        out_path = os.path.join(RESULTS_DIR, "predicted_compatibilities.xlsx")
    Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
    df_results.to_excel(out_path, index=False)
    print(f"[OK] Saved compatibility results to: {out_path}")
    return out_path


# -----------------------
# Example CLI usage
# -----------------------
def main(interactive=True, use_dummy_if_no_input=True):
    print("=== Loading specialization models from:", MODELS_DIR)
    all_models = load_all_specialization_models(MODELS_DIR)
    if not all_models:
        print("No models loaded. Run generate_data_and_train first.")
        return

    # union of all features (so we can prompt in a canonical order)
    all_features = union_all_features(all_models)
    print(f"Total distinct features to provide: {len(all_features)}")

    # choose interactive or dummy
    student_profile = None
    if interactive:
        print("\nChoose input mode:")
        print("  1) Interactive: you will be prompted to enter scores per course/trait")
        print("  2) Dummy: use a generated realistic student profile")
        choice = input("Select 1 or 2 (default 2): ").strip() or "2"
        if choice == "1":
            print("\n>>> Interactive mode: enter scores for each course/trait (or Enter to default 0).")
            student_profile = prompt_student_scores(all_features)
        else:
            student_profile = generate_dummy_student(all_features)
            print("\n>>> Dummy profile generated (sample):")
            # show a few sample features
            sample_items = list(student_profile.items())[:18]
            for k, v in sample_items:
                print(f"  {k}: {v:.3f}")

    else:
        # non-interactive: use dummy
        student_profile = generate_dummy_student(all_features)

    # compute compatibilities
    print("\nComputing compatibilities across all specializations and jobs...")
    df_results = predict_all_compatibilities(all_models, student_profile)

    # show top results
    print("\nTop 15 job matches (specialization - job - %):")
    for i, row in df_results.head(15).iterrows():
        print(f"{i+1:02d}. {row['specialization']} -- {row['job']} : {row['compatibility_percent']}%")

    # aggregate specialization-level scores (mean of jobs probabilities under each specialization)
    spec_scores = df_results.groupby("specialization", as_index=False)["compatibility_percent"].mean()
    spec_scores = spec_scores.sort_values(by="compatibility_percent", ascending=False).reset_index(drop=True)
    print("\nSpecialization summary (average job compatibility %):")
    for i, r in spec_scores.iterrows():
        print(f"{i+1:02d}. {r['specialization']}: {r['compatibility_percent']:.2f}%")

    # save
    save_results(df_results)

    return df_results, student_profile


if __name__ == "__main__":
    # interactive CLI
    main(interactive=True)
