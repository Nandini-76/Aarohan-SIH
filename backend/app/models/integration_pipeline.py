#!/usr/bin/env python3
"""
Integration pipeline:
- Merge distributed datasets on enrollment_no
- Save merged dataset (no cleaning, no model inference)
- Returns JSON-ready preview for API endpoints
"""

import pandas as pd
import os
from pathlib import Path

# ---------- CONFIG ----------
# Get the current file's directory and navigate to distributed-data
CURRENT_DIR = Path(__file__).parent
DATA_DIR = CURRENT_DIR.parent.parent / "distributed-data"   # Navigate to prototype/distributed-data
DATASETS = {
    "academics": DATA_DIR / "academics.csv",
    "finance": DATA_DIR / "finance.csv", 
    "demographics": DATA_DIR / "demographics.csv",
    "discipline": DATA_DIR / "discipline.csv",
    "family": DATA_DIR / "family.csv",
    "contact": DATA_DIR / "contact.csv",
}
OUTPUT_PATH = CURRENT_DIR.parent / "data" / "merged_dataset.csv"  # Save to app/data/
KEY = "enrollment_no"
# ----------------------------


def merge_datasets():
    """
    Merge all distributed datasets into a single dataset.
    
    Returns:
        pd.DataFrame: Merged dataset
    """
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

    # Merge on enrollment_no
    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on=KEY, how="outer")

    print(f"\n✅ Final merged dataset: {merged.shape[0]} rows, {merged.shape[1]} cols")
    return merged


def run_integration_pipeline():
    """
    Main function to run the integration pipeline.
    
    Returns:
        dict: Summary with dataset info and preview
    """
    print("🚀 Starting Integration Pipeline...")
    
    # Merge datasets
    merged_df = merge_datasets()
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Save merged dataset
    merged_df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n💾 Saved merged dataset → {OUTPUT_PATH}")
    
    # Return summary for API
    summary = {
        "status": "success",
        "total_students": len(merged_df),
        "total_columns": len(merged_df.columns),
        "output_path": str(OUTPUT_PATH),
        "preview": merged_df.head().to_dict('records'),
        "columns": list(merged_df.columns)
    }
    
    print(f"\n🔍 Dataset preview:")
    print(merged_df.head())
    
    return summary


def main():
    """CLI entry point"""
    result = run_integration_pipeline()
    print(f"\n✅ Integration complete: {result['total_students']} students merged")


if __name__ == "__main__":
    main()
