"""
generate_data_and_train.py

- Reads all CSVs under sources/datasets/
- Builds feature space from every code_or_trait (courses, skills, traits)
- Generates realistic synthetic applicants (balanced across jobs)
- Saves generated dataset to sources/data/generated_training_data.xlsx
- Trains a RandomForest job classifier per specialization
- Saves model artifacts to sources/model/<specialization>_model/
"""

import os
import glob
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# -------------------------
# CONFIG
# -------------------------
DATASET_DIR = "sources/datasets"          # where your CSVs are
OUTPUT_DATA_PATH = "sources/data/generated_training_data.xlsx"
MODELS_DIR = "sources/model"
N_SYNTHETIC_PER_JOB = 1500                 # number of synthetic applicants per job (balanced)
RANDOM_SEED = 42

os.makedirs(os.path.dirname(OUTPUT_DATA_PATH), exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
np.random.seed(RANDOM_SEED)

# -------------------------
# HELPERS
# -------------------------
def read_all_csvs(dataset_dir):
    files = sorted(glob.glob(os.path.join(dataset_dir, "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {dataset_dir}")
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        # normalize column names (strip)
        df.columns = [c.strip() for c in df.columns]
        # ensure required columns exist
        required = {"specialization", "job", "type", "code_or_trait", "weight"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"File {f} missing required columns. Expected at least: {required}")
        dfs.append(df)
    all_jobs = pd.concat(dfs, ignore_index=True)
    return all_jobs

def build_job_trait_map(df_jobs):
    """
    Returns:
        job_map: dict keyed by (specialization, job) -> dict{code_or_trait: weight}
        specializations: sorted unique specialization list
        all_traits: sorted list of all code_or_trait across dataset
    """
    df = df_jobs.copy()
    # drop null traits
    df = df.dropna(subset=["code_or_trait", "weight"])
    df["code_or_trait"] = df["code_or_trait"].astype(str).str.strip()
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.0)

    all_traits = sorted(df["code_or_trait"].unique())
    job_map = {}
    for (spec, job), group in df.groupby(["specialization", "job"]):
        trait_dict = dict(zip(group["code_or_trait"], group["weight"]))
        # normalize weights for the job to 0-1 (so different jobs comparable)
        total = sum(trait_dict.values())
        if total > 0:
            # keep relative weight shape but scale to max 1
            max_w = max(trait_dict.values())
            if max_w > 0:
                trait_dict = {k: float(v) / float(max_w) for k, v in trait_dict.items()}
        job_map[(spec.strip(), job.strip())] = trait_dict
    specializations = sorted({spec for spec, _ in job_map.keys()})
    return job_map, specializations, all_traits

def synthesize_applicant_for_job(trait_list, job_traits, global_trait_mean=0.1, noise_scale=0.08):
    """
    trait_list: list of all traits (columns)
    job_traits: dict {trait: normalized_weight (0..1)} for the job
    Returns dict of trait -> value (0..1)
    Behavior:
      - Traits that the job emphasizes (weight close to 1) will center around higher values (e.g., 0.7-1.0)
      - Lesser traits get lower base values
      - Add gaussian noise, clip to [0,1]
    """
    profile = {}
    # base for traits not mentioned: small baseline
    baseline = global_trait_mean
    for t in trait_list:
        w = job_traits.get(t, 0.0)
        # Map weight w (0..1) to mean in [baseline, 0.95]
        mean = baseline + (0.95 - baseline) * (w ** 1.0)  # keep exponent 1 for linearity; tweak if desired
        # sample value with gaussian noise; sigma scaled by noise_scale and (1 - w) (more important traits less noisy)
        sigma = noise_scale * (1.0 - 0.6 * w)
        val = np.random.normal(loc=mean, scale=sigma)
        # add a small uniform jitter
        val += np.random.uniform(-0.03, 0.03)
        profile[t] = float(np.clip(val, 0.0, 1.0))
    return profile

# -------------------------
# GENERATE SYNTHETIC DATA
# -------------------------
def generate_synthetic_dataset(job_map, all_traits, samples_per_job=N_SYNTHETIC_PER_JOB):
    """
    For each (spec, job) in job_map, generate `samples_per_job` applicants biased to that job.
    Returns DataFrame with columns: applicant_id, specialization, job, <trait columns...>
    """
    records = []
    idx = 0
    for (spec, job), traits in job_map.items():
        for _ in range(samples_per_job):
            idx += 1
            profile = synthesize_applicant_for_job(all_traits, traits)
            rec = {"applicant_id": idx, "specialization": spec, "job": job}
            rec.update(profile)
            records.append(rec)
    df = pd.DataFrame.from_records(records)
    # shuffle rows
    df = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return df

# -------------------------
# TRAIN PER-SPECIALIZATION MODELS
# -------------------------
def train_and_save_models(df_train, all_traits, models_dir=MODELS_DIR):
    """
    For each specialization:
       - extract rows for that specialization
       - prepare X (all_traits), y (job)
       - standardize X with StandardScaler
       - fit RandomForestClassifier
       - evaluate and save artifacts to a folder:
            sources/model/<specialization>_model/
            - model.joblib
            - scaler.joblib
            - label_encoder.joblib
            - features.txt
            - report.txt
    """
    os.makedirs(models_dir, exist_ok=True)
    specs = sorted(df_train["specialization"].unique())
    results = {}
    for spec in specs:
        spec_safe = spec.replace("/", "_").replace(" ", "_")
        spec_dir = os.path.join(models_dir, f"{spec_safe}_model")
        os.makedirs(spec_dir, exist_ok=True)
        df_spec = df_train[df_train["specialization"] == spec].copy()
        if df_spec.shape[0] < 5:
            print(f"[WARN] Not enough samples for specialization {spec} (n={len(df_spec)}), skipping.")
            continue

        X = df_spec[all_traits].fillna(0.0).values
        y = df_spec["job"].astype(str).values

        # label encode target jobs
        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        # scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # split
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_enc, test_size=0.20, random_state=RANDOM_SEED, stratify=y_enc)

        # model
        clf = RandomForestClassifier(n_estimators=300, random_state=RANDOM_SEED, class_weight="balanced", n_jobs=-1)
        clf.fit(X_train, y_train)

        # evaluate
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)

        print(f"\n[INFO] Specialization: {spec}  |  samples: {len(df_spec)}  |  test_acc: {acc:.3f}")

        joblib.dump(clf, os.path.join(spec_dir, "model.joblib"))
        joblib.dump(scaler, os.path.join(spec_dir, "scaler.joblib"))
        joblib.dump(le, os.path.join(spec_dir, "label_encoder.joblib"))

        with open(os.path.join(spec_dir, "features.txt"), "w", encoding="utf-8") as f:
            for t in all_traits:
                f.write(t + "\n")

        with open(os.path.join(spec_dir, "report.txt"), "w", encoding="utf-8") as f:
            f.write(f"Specialization: {spec}\n")
            f.write(f"Total samples: {len(df_spec)}\n")
            f.write(f"Model test accuracy: {acc:.4f}\n\n")
            f.write(report)

        results[spec] = {"n_samples": len(df_spec), "test_accuracy": float(acc), "model_dir": spec_dir}
    return results

# -------------------------
# SAVE GENERATED DATA
# -------------------------
def save_generated_data(df, path=OUTPUT_DATA_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_excel(path, index=False)
    print(f"[INFO] Saved generated dataset to: {path}")

def main():
    print("=== Loading CSV datasets from:", DATASET_DIR)
    df_jobs = read_all_csvs(DATASET_DIR)

    print("[1] Building job <-> trait maps ...")
    job_map, specializations, all_traits = build_job_trait_map(df_jobs)
    print(f"    found {len(job_map)} (spec,job) combinations across {len(specializations)} specializations")
    print(f"    total unique traits/codes: {len(all_traits)}")

    print(f"[2] Generating synthetic applicants: {N_SYNTHETIC_PER_JOB} samples per job (balanced) ...")
    df_generated = generate_synthetic_dataset(job_map, all_traits, samples_per_job=N_SYNTHETIC_PER_JOB)
    print(f"    generated {len(df_generated)} synthetic applicants")

    print("[3] Save generated dataset ...")
    save_generated_data(df_generated, OUTPUT_DATA_PATH)

    print("[4] Train per-specialization job models ...")
    results = train_and_save_models(df_generated, all_traits, models_dir=MODELS_DIR)

    print("\n=== Training summary ===")
    for spec, info in results.items():
        print(f" - {spec}: samples={info['n_samples']}, test_acc={info['test_accuracy']:.3f}, saved_in={info['model_dir']}")

    print("\nDone. Models saved under:", MODELS_DIR)
    print("Generated dataset saved at:", OUTPUT_DATA_PATH)

if __name__ == "__main__":
    main()
