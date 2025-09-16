#!/usr/bin/env python3
"""
Test the trained Random Forest pipeline on the test dataset (broad classes),
and print feature importances.
"""

import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 👇 Import feature engineering helper so joblib.load can resolve it
from feature_utils import add_engineered_features  

# ---------- CONFIG ----------
DATA_PATH = "C:\\Users\\wanna\\Desktop\\dropout-repos\\prototype\\backend\\app\\models\\data\\new_test_dataset_v2.csv"   # ✅ balanced test dataset
MODEL_PATH = "C:\\Users\\wanna\\Desktop\\AAROHAN\\backend\\app\\models\\rf_pipeline_broad.joblib"                         # trained RF broad-phase model
TARGET_COL = "broad_phase"
TOP_N_FEATURES = 15  # number of most important features to display
# ----------------------------

BROAD_PHASE_MAP = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}


def main():
    print(f"📂 Loading test dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    if TARGET_COL not in df.columns:
        raise SystemExit(f"❌ Target column '{TARGET_COL}' not found in {DATA_PATH}")

    # Keep only raw features; pipeline does the feature engineering
    X = df.drop(columns=[TARGET_COL, "phase", "phase_label"], errors="ignore")
    y = df[TARGET_COL]

    # Optional sanity check: class balance
    counts = y.value_counts().sort_index()
    print("\n📊 Test dataset class distribution:")
    for k, v in counts.items():
        print(f"  {BROAD_PHASE_MAP.get(k, k)} → {v} samples")

    print(f"\n📦 Loading trained model: {MODEL_PATH}")
    obj = joblib.load(MODEL_PATH)
    pipeline = obj["pipeline"]

    # Predict
    y_pred = pipeline.predict(X)

    # Metrics
    acc = accuracy_score(y, y_pred)
    print(f"\n✅ Accuracy on test dataset: {acc:.4f}\n")

    print("📊 Classification Report:")
    labels_sorted = sorted(BROAD_PHASE_MAP.keys())
    target_names = [BROAD_PHASE_MAP[l] for l in labels_sorted]
    print(classification_report(
        y, y_pred,
        labels=labels_sorted,
        target_names=target_names,
        digits=4
    ))

    # Confusion matrix
    cm = confusion_matrix(y, y_pred, labels=labels_sorted)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print("\n🌀 Confusion Matrix (rows=true, cols=pred):")
    print(cm_df)

    # --- Feature Importances ---
    clf = pipeline.named_steps["clf"]
    try:
        feature_names = pipeline.named_steps["preproc"].get_feature_names_out()
    except Exception:
        feature_names = [f"f{i}" for i in range(len(clf.feature_importances_))]

    importances = clf.feature_importances_
    fi_df = pd.DataFrame({"feature": feature_names, "importance": importances})
    fi_df = fi_df.sort_values("importance", ascending=False).reset_index(drop=True)

    print(f"\n🌟 Top {TOP_N_FEATURES} Most Important Features:")
    print(fi_df.head(TOP_N_FEATURES).to_string(index=False))


if __name__ == "__main__":
    main()
