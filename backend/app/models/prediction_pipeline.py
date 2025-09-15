#!/usr/bin/env python3
"""
Prediction pipeline:
- Load merged dataset
- Apply data cleaning using basic_clean from utils
- Add engineered features using feature_utils
- Run Random Forest predictions
- Apply Red-Zone override rules
- Save dataset with final predictions
- Return JSON results for API
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix import paths - add the app directory to the path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import from app directory
try:
    from utils import basic_clean, apply_red_zone_rules_to_phase
    from models.feature_utils import add_engineered_features
except ImportError as e:
    logger.warning(f"Import warning: {e}")
    # Fallback - define minimal versions if imports fail
    def basic_clean(df):
        return df
    def add_engineered_features(df):
        return df
    def apply_red_zone_rules_to_phase(row, model_phase):
        return model_phase, ""

# ---------- CONFIG ----------
CURRENT_DIR = Path(__file__).parent
MERGED_DATA_PATH = CURRENT_DIR.parent / "data" / "merged_dataset.csv"
OUTPUT_PATH = CURRENT_DIR.parent / "data" / "merged_with_predictions.csv"
MODEL_PATH = CURRENT_DIR / "rf_pipeline_broad.joblib"
KEY = "enrollment_no"
# ----------------------------


def apply_rules(row):
    """
    Expanded rule-based override logic in strict priority:
    Red → Orange → Yellow → Green.
    
    Args:
        row: pandas Series containing student data.
        
    Returns:
        tuple: (phase, reason) or (None, None) if no override.
    """
    A = row.get('attendance', 0)
    C = row.get('cgpa', 0)
    B = row.get('backlogs', 0)
    S = row.get('suspension_flag', 0)
    F = row.get('fees_flag', 1)  # Default = 1 (paid), 0 = default
    
    # ============ RED ZONE RULES (HIGHEST PRIORITY) ============
    if A < 50:
        return "Red", "Critical attendance (<50)"
    if B > 7:
        return "Red", "Severe backlogs (>7)"
    if C < 4.5 and B > 5:
        return "Red", "Very low CGPA & high backlogs"
    if S >= 3:
        return "Red", "Multiple suspensions (≥3)"
    if F == 0 and A < 60:
        return "Red", "Fee default & poor attendance"
    if F == 0 and C < 4.5:
        return "Red", "Fee default & very weak CGPA"
    if A < 45 and C < 5 and B > 3:
        return "Red", "Severe academic issues (low attendance, low CGPA, high backlogs)"
    
    # ============ ORANGE ZONE RULES ============
    if 60 <= A <= 69:
        return "Orange", "Attendance in risk range (60–69)"
    if 5 <= C < 6 and 2 <= B <= 4:
        return "Orange", "Low CGPA with moderate backlogs"
    if S == 2 and A < 70:
        return "Orange", "Repeated discipline issues"
    if C < 6 and B > 4:
        return "Orange", "Low CGPA with backlogs"
    if A < 65 and F == 0:
        return "Orange", "Fee default & low attendance"
    
    # ============ YELLOW ZONE RULES ============
    if 70 <= A <= 79:
        return "Yellow", "Attendance in caution range (70–79)"
    if 6 <= C < 7 and B <= 2:
        return "Yellow", "Slightly weak academics (CGPA 6–7, low backlogs)"
    if S == 1 and A >= 70:
        return "Yellow", "Minor disciplinary issue"
    if F == 0 and A >= 70:
        return "Yellow", "Fee default but attendance acceptable"
    
    # ============ GREEN ZONE RULES ============
    if A >= 80 and C >= 7 and B == 0 and S == 0:
        return "Green", "Good performance & discipline"
    if A >= 85 and C >= 8:
        return "Green", "Strong academics (high attendance & CGPA)"
    if A >= 90:
        return "Green", "Excellent attendance"
    
    # No override → keep ML prediction
    return None, None


def apply_comprehensive_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply comprehensive rule-based overrides to ML predictions.
    
    This function:
    1. Takes ML model predictions in 'model_phase' column (renamed from 'ml_phase')
    2. Applies comprehensive rule-based overrides
    3. Creates 'final_phase' and 'override_reason' columns
    
    Args:
        df: DataFrame with model_phase column
        
    Returns:
        DataFrame with final_phase and override_reason columns added
    """
    df = df.copy()
    
    # Rename model predictions column for clarity
    if 'model_phase' in df.columns:
        df['ml_phase'] = df['model_phase']  # Keep original ML predictions
    else:
        df['ml_phase'] = 'Green'  # Default if no ML predictions
    
    # Initialize override columns
    df["final_phase"] = df["ml_phase"]  # Start with ML predictions
    df["override_reason"] = "Model prediction kept"
    
    override_count = 0
    
    # Apply rules row by row
    for idx, row in df.iterrows():
        override_phase, override_reason = apply_rules(row)
        
        if override_phase is not None:
            # Rule-based override triggered
            df.at[idx, "final_phase"] = override_phase
            df.at[idx, "override_reason"] = override_reason
            override_count += 1
        # If no override, keep ML prediction and "Model prediction kept" reason
    
    logger.info(f"Applied comprehensive overrides - {override_count} students overridden by rules")
    
    # Log distribution summary
    override_summary = df['override_reason'].value_counts()
    logger.info(f"Override reasons: {override_summary.to_dict()}")
    
    return df


def apply_phase_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """
    Legacy function - now redirects to comprehensive overrides.
    Maintained for backward compatibility.
    """
    return apply_comprehensive_overrides(df)


def load_model():
    """
    Load the trained Random Forest model.
    
    Returns:
        tuple: (model_pipeline, phase_map) or (None, None) if loading fails
    """
    try:
        logger.info(f"📦 Loading trained model: {MODEL_PATH}")
        
        if not MODEL_PATH.exists():
            logger.warning(f"Model file not found: {MODEL_PATH}")
            return None, None
            
        obj = joblib.load(MODEL_PATH)
        
        if isinstance(obj, dict):
            pipeline = obj.get("pipeline")
            phase_map = obj.get("phase_map", {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"})
        else:
            # If obj is the pipeline directly
            pipeline = obj
            phase_map = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}
        
        logger.info("✅ Model loaded successfully")
        return pipeline, phase_map
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        return None, None


def run_prediction_pipeline():
    """
    Main function to run the prediction pipeline.
    
    Returns:
        dict: Results with predictions and summary
    """
    logger.info("🚀 Starting Prediction Pipeline...")
    
    # 1. Load merged dataset
    if not MERGED_DATA_PATH.exists():
        raise FileNotFoundError(f"Merged dataset not found: {MERGED_DATA_PATH}")
    
    logger.info(f"📂 Loading merged dataset: {MERGED_DATA_PATH}")
    df = pd.read_csv(MERGED_DATA_PATH)
    logger.info(f"Loaded {len(df)} students with {len(df.columns)} features")

    if KEY not in df.columns:
        raise ValueError(f"❌ Missing key column '{KEY}' in merged dataset")

    # 2. Apply data cleaning
    logger.info("🧹 Applying data cleaning...")
    df = basic_clean(df)
    
    # 3. Add engineered features
    logger.info("⚙️ Adding engineered features...")
    df = add_engineered_features(df)
    logger.info(f"Dataset after feature engineering: {len(df.columns)} columns")

    # 4. Load trained model
    pipeline, phase_map = load_model()
    
    # 5. Run ML predictions
    if pipeline is not None:
        logger.info("🤖 Running ML predictions...")
        
        # Prepare features for model (exclude enrollment_no and any non-feature columns)
        feature_columns = [col for col in df.columns if col not in [KEY, 'predicted_phase', 'red_reason', 'ml_probability']]
        X = df[feature_columns]
        
        # Handle missing values for ML model
        X = X.fillna(0)
        
        try:
            # Get predictions
            y_pred = pipeline.predict(X)
            y_proba = pipeline.predict_proba(X)[:, 1] if hasattr(pipeline, 'predict_proba') else None
            
            # Map predictions to model_phase (raw ML predictions)
            df["model_phase"] = [phase_map.get(p, "Unknown") for p in y_pred]
            
            if y_proba is not None:
                df["ml_probability"] = y_proba
            else:
                df["ml_probability"] = None
                
            logger.info("✅ ML predictions completed")
            
        except Exception as e:
            logger.error(f"❌ ML prediction failed: {e}")
            # Fallback to default predictions
            df["model_phase"] = "Green"
            df["ml_probability"] = None
    else:
        logger.warning("⚠️ No model available, using default predictions")
        df["model_phase"] = "Green"
        df["ml_probability"] = None

    # 6. Apply comprehensive rule-based override system
    logger.info("🚨 Applying comprehensive rule-based overrides...")
    df = apply_comprehensive_overrides(df)

    # 7. Save final dataset with all required columns
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"💾 Saved dataset with predictions → {OUTPUT_PATH}")

    # 8. Generate summary
    ml_phase_counts = df["ml_phase"].value_counts().to_dict()
    final_phase_counts = df["final_phase"].value_counts().to_dict()
    override_count = len(df[df["override_reason"] != "Model prediction kept"])
    
    logger.info(f"🔍 Prediction Summary:")
    logger.info(f"  ML predictions: {ml_phase_counts}")
    logger.info(f"  Final predictions: {final_phase_counts}")
    logger.info(f"  Rule-based overrides: {override_count} students")

    # 9. Return results for API
    results = {
        "status": "success",
        "total_students": len(df),
        "ml_phase_distribution": ml_phase_counts,
        "final_phase_distribution": final_phase_counts,
        "rule_overrides": override_count,
        "ml_model_used": pipeline is not None,
        "output_path": str(OUTPUT_PATH),
        "preview": df[[KEY, "ml_phase", "final_phase", "override_reason", "ml_probability"]].head().to_dict('records'),
        "sample_predictions": df.head(5).to_dict('records')
    }
    
    return results


def main():
    """CLI entry point"""
    try:
        results = run_prediction_pipeline()
        print(f"\n✅ Prediction complete:")
        print(f"   Total students: {results['total_students']}")
        print(f"   ML predictions: {results['ml_phase_distribution']}")
        print(f"   Final predictions: {results['final_phase_distribution']}")
        print(f"   Rule-based overrides: {results['rule_overrides']}")
        print(f"   ML model used: {results['ml_model_used']}")
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
