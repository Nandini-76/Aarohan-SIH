#!/usr/bin/env python3
"""
Train a Random Forest model on student_phase_dataset_rf_small_balanced.csv
using broad classification (Green, Yellow, Orange, Red).

Feature engineering is handled inside feature_utils,
so raw data can be used in training and production.
"""

import pandas as pd
import joblib
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# 👇 Import shared feature engineering
from feature_utils import add_engineered_features

# ---------- CONFIG ----------
DATA_PATH = "new_training_dataset_v2.csv"   # ✅ smaller balanced dataset
MODEL_PATH = "rf_pipeline_broad.joblib"
TARGET_COL = "broad_phase"
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_ESTIMATORS = 500     # more trees for robustness
MAX_DEPTH = None
# ----------------------------

BROAD_PHASE_MAP = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Clip/normalize numeric + categorical fields."""
    if "attendance" in df.columns:
        df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce").clip(0, 100)
    if "cgpa" in df.columns:
        df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce").clip(0, 10)
    if "backlogs" in df.columns:
        df["backlogs"] = pd.to_numeric(df["backlogs"], errors="coerce").fillna(0).astype(int)
        df.loc[df["backlogs"] < 0, "backlogs"] = 0
    for f in ["fees_flag", "suspension_flag"]:
        if f in df.columns:
            df[f] = pd.to_numeric(df[f], errors="coerce").fillna(0).astype(int)
            df.loc[~df[f].isin([0, 1]), f] = (df.loc[~df[f].isin([0, 1]), f] != 0).astype(int)
    if "gender" in df.columns:
        df["gender"] = df["gender"].fillna("Unknown").astype(str)
    return df


def make_onehot_encoder():
    ver = sklearn.__version__.split('.')
    try:
        major = int(ver[0])
        minor = int(ver[1]) if len(ver) > 1 else 0
    except Exception:
        major, minor = 0, 0
    if major > 1 or (major == 1 and minor >= 2):
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    else:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def main():
    print(f"📂 Loading dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    df = basic_clean(df)

    if TARGET_COL not in df.columns:
        raise SystemExit(f"Target column '{TARGET_COL}' not found in {DATA_PATH}")

    y = df[TARGET_COL].astype(int)
    X = df.drop(columns=[TARGET_COL, "phase", "phase_label"], errors="ignore")

    # Raw feature groups
    base_numeric = [
        "attendance", "cgpa", "backlogs", "fees_flag", "suspension_flag"
    ]
    categorical = ["gender"]

    # Pipelines
    num_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    onehot = make_onehot_encoder()
    cat_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", onehot)
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", num_pipeline, base_numeric + [
            "att_cgpa_interaction", "att_backlog_ratio",
            "backlog_pressure", "ari", "penalty_score"
        ]),
        ("cat", cat_pipeline, categorical)
    ], remainder="drop")

    clf = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        random_state=RANDOM_STATE,
        class_weight="balanced",   # dataset is balanced but keep safe
        n_jobs=-1
    )

    pipeline = Pipeline(steps=[
        ("feature_eng", FunctionTransformer(add_engineered_features)),
        ("preproc", preprocessor),
        ("clf", clf)
    ])

    # Split & Train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    print("🌲 Training Random Forest (broad classes)...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {acc:.4f}\n")

    print("📊 Classification report:")
    labels_sorted = sorted(BROAD_PHASE_MAP.keys())
    target_names = [BROAD_PHASE_MAP[l] for l in labels_sorted]
    print(classification_report(y_test, y_pred, labels=labels_sorted, target_names=target_names, digits=4))

    cm = confusion_matrix(y_test, y_pred, labels=labels_sorted)
    cm_df = pd.DataFrame(cm, index=target_names, columns=target_names)
    print("\n🌀 Confusion matrix (rows=true, cols=pred):")
    print(cm_df)

    # Save pipeline
    joblib.dump({"pipeline": pipeline, "phase_map": BROAD_PHASE_MAP}, MODEL_PATH)
    print(f"\n💾 Saved pipeline and metadata to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
