#!/usr/bin/env python3
"""
Integration pipeline:
- Merge distributed datasets on enrollment_no
- Standardize schema and clean feature ranges
- Save merged dataset (API & ML ready)
"""

import pandas as pd
from pathlib import Path

# ---------- CONFIG ----------
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR.parent.parent / "distributed-data"
DATASETS = {
    "academics": DATA_DIR / "academics.csv",
    "finance": DATA_DIR / "finance.csv",
    "demographics": DATA_DIR / "demographics.csv",
    "discipline": DATA_DIR / "discipline.csv",
    "family": DATA_DIR / "family.csv",
    "contact": DATA_DIR / "contact.csv",
}
OUTPUT_PATH = CURRENT_DIR.parent / "data" / "merged_dataset.csv"
KEY = "enrollment_no"
# ----------------------------


def normalize_features(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize key numeric and categorical fields for ML consistency."""
    if "attendance" in df.columns:
        df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce").clip(0, 100)

    if "cgpa" in df.columns:
        df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce").clip(0, 10)

    if "backlogs" in df.columns:
        df["backlogs"] = pd.to_numeric(df["backlogs"], errors="coerce").fillna(0).astype(int)
        df.loc[df["backlogs"] < 0, "backlogs"] = 0

    if "suspension_flag" in df.columns:
        df["suspension_flag"] = pd.to_numeric(df["suspension_flag"], errors="coerce").fillna(0).astype(int)
        df.loc[~df["suspension_flag"].isin([0, 1, 2, 3, 4]), "suspension_flag"] = 0

    if "gender" in df.columns:
        df["gender"] = df["gender"].fillna("Unknown").astype(str)

    return df


def merge_datasets():
    """Merge all distributed datasets into a single dataset."""
    dfs = []
    for name, path in DATASETS.items():
        try:
            df = pd.read_csv(path)
            print(f"📂 Loaded {name} dataset → {df.shape[0]} rows, {df.shape[1]} cols")
            dfs.append(df)
        except FileNotFoundError:
            print(f"❌ Warning: {name} dataset not found at {path}")
            continue
        except Exception as e:
            print(f"❌ Error loading {name} dataset: {e}")
            continue

    if not dfs:
        raise ValueError("No datasets could be loaded!")

    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on=KEY, how="outer")

    # Fix duplicate columns created by merge (gender_x, gender_y -> gender)
    print("🔧 Cleaning duplicate columns from merge...")
    columns_to_fix = []
    
    # Find columns with _x and _y suffixes
    for col in merged.columns:
        if col.endswith('_x'):
            base_name = col[:-2]  # Remove '_x'
            y_col = base_name + '_y'
            if y_col in merged.columns:
                columns_to_fix.append(base_name)
    
    # For each duplicate column, merge the _x and _y versions
    for base_name in columns_to_fix:
        x_col = base_name + '_x'
        y_col = base_name + '_y'
        
        # Use the first non-null value between _x and _y columns
        merged[base_name] = merged[x_col].combine_first(merged[y_col])
        
        # Drop the duplicate columns
        merged = merged.drop(columns=[x_col, y_col])
        print(f"   ✅ Merged {x_col} + {y_col} → {base_name}")

    merged = normalize_features(merged)

    # Drop obvious duplicates and empty columns
    merged = merged.loc[:, ~merged.columns.duplicated()]
    merged = merged.dropna(axis=1, how="all")  # drop fully empty cols

    # Validate required features for the new model
    required_features = ['attendance', 'cgpa', 'backlogs', 'suspension_flag', 'gender']
    missing_features = [f for f in required_features if f not in merged.columns]
    
    if missing_features:
        print(f"⚠️  Warning: Missing required features: {missing_features}")
        print(f"   Available columns: {list(merged.columns)}")
    else:
        print(f"✅ All required features present: {required_features}")

    print(f"\n✅ Final merged dataset: {merged.shape[0]} rows, {merged.shape[1]} cols")
    return merged


def run_integration_pipeline():
    """Main integration pipeline runner."""
    print("🚀 Starting Integration Pipeline...")
    merged_df = merge_datasets()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n💾 Saved merged dataset → {OUTPUT_PATH}")

    summary = {
        "status": "success",
        "total_students": len(merged_df),
        "total_columns": len(merged_df.columns),
        "output_path": str(OUTPUT_PATH),
        "preview": merged_df.head().to_dict("records"),
        "columns": list(merged_df.columns),
    }

    print(f"\n🔍 Dataset preview:")
    print(merged_df.head())

    return summary


def main():
    result = run_integration_pipeline()
    print(f"\n✅ Integration complete: {result['total_students']} students merged")


if __name__ == "__main__":
    main()
