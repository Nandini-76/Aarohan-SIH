"""
Unified prediction and override system for student dropout prediction.
Includes ML pipeline, red-zone rule engine, and helper functions.
Handles both batch and live predictions through the same logic.

Author: AI Assistant
Date: September 16, 2025
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- PIPELINE CONFIG ----------
CURRENT_DIR = Path(__file__).parent
MERGED_DATA_PATH = CURRENT_DIR / "data" / "merged_dataset.csv"
OUTPUT_PATH = CURRENT_DIR / "data" / "merged_with_predictions.csv"
MODEL_PATH = CURRENT_DIR / "models" / "rf_pipeline_broad.joblib"
KEY = "enrollment_no"
# ------------------------------------


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic data cleaning for student dataset.
    Clips/normalizes numeric fields and handles categorical fields.
    
    Args:
        df: Raw student DataFrame
        
    Returns:
        Cleaned DataFrame with standardized fields
    """
    df = df.copy()
    
    # Clean attendance (0-100%)
    if "attendance" in df.columns:
        df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce").clip(0, 100)
    
    # Clean CGPA (0-10)
    if "cgpa" in df.columns:
        df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce").clip(0, 10)
    
    # Clean backlogs (0+)
    if "backlogs" in df.columns:
        df["backlogs"] = pd.to_numeric(df["backlogs"], errors="coerce").fillna(0).astype(int)
        df.loc[df["backlogs"] < 0, "backlogs"] = 0
    
    # Clean binary flags (0 or 1)
    for flag in ["fees_flag", "suspension_flag"]:
        if flag in df.columns:
            df[flag] = pd.to_numeric(df[flag], errors="coerce").fillna(0).astype(int)
            # Ensure only 0 or 1 values
            df.loc[~df[flag].isin([0, 1]), flag] = (df.loc[~df[flag].isin([0, 1]), flag] != 0).astype(int)
    
    # Clean gender
    if "gender" in df.columns:
        df["gender"] = df["gender"].fillna("Unknown").astype(str)
    
    # Clean marks (0-100%)
    for marks_col in ["marks_10th", "marks_12th"]:
        if marks_col in df.columns:
            df[marks_col] = pd.to_numeric(df[marks_col], errors="coerce").clip(0, 100)
    
    logger.info(f"Cleaned dataset: {len(df)} rows")
    return df





def convert_to_model_features(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert API input format to model feature format.
    
    Args:
        student_data: Raw student data from API
        
    Returns:
        Processed feature dictionary ready for ML model
    """
    # Map API fields to model features
    features = {
        'attendance': student_data.get('attendance_percent', student_data.get('attendance', 0)),
        'cgpa': student_data.get('cgpa', 0),
        'backlogs': student_data.get('backlogs', 0),
        'marks_10th': student_data.get('marks_10', student_data.get('marks_10th', 0)),
        'marks_12th': student_data.get('marks_12', student_data.get('marks_12th', 0)),
        # Fix fees_flag logic - handle both string and numeric inputs
        'fees_flag': _normalize_fees_flag(student_data.get('fees_flag', 0)),
        'suspension_flag': int(student_data.get('suspension_flag', 0)),
        'gender': student_data.get('gender', 'M')
    }
    
    return features


def _normalize_fees_flag(fees_flag_value) -> int:
    """
    Normalize fees_flag to consistent 0/1 format.
    
    Args:
        fees_flag_value: Can be int (0/1), string ('Y'/'N', 'paid'/'unpaid'), or bool
        
    Returns:
        int: 0 = fees paid, 1 = fees unpaid
    """
    if isinstance(fees_flag_value, (int, float)):
        # Numeric: 0 = paid, 1 = unpaid (keep as is)
        return int(fees_flag_value)
    elif isinstance(fees_flag_value, str):
        # String values - handle various formats
        value = fees_flag_value.strip().upper()
        if value in ['N', 'NO', 'UNPAID', 'OUTSTANDING', 'FALSE', '1']:
            return 1  # Unpaid
        elif value in ['Y', 'YES', 'PAID', 'TRUE', '0']:
            return 0  # Paid
        else:
            logger.warning(f"Unknown fees_flag value: {fees_flag_value}, defaulting to 0 (paid)")
            return 0
    elif isinstance(fees_flag_value, bool):
        # Boolean: True = unpaid, False = paid
        return int(fees_flag_value)
    else:
        logger.warning(f"Unknown fees_flag type: {type(fees_flag_value)}, defaulting to 0 (paid)")
        return 0


def process_single_prediction(student_data: Dict[str, Any], ml_model=None, ml_scaler=None) -> Dict[str, Any]:
    """
    Process a single student prediction using the unified system.
    DEPRECATED: Use predict_with_unified_system for new code.
    
    Args:
        student_data: Student features
        ml_model: Trained ML model (optional)
        ml_scaler: Feature scaler (optional)
        
    Returns:
        Dictionary with prediction results including model_phase and final_phase
    """
    # Use the unified system for consistency
    return predict_with_unified_system(student_data, ml_model, ml_scaler)


def add_predictions_to_dataset(df: pd.DataFrame, ml_model=None, ml_scaler=None) -> pd.DataFrame:
    """
    Add predictions to the entire dataset.
    
    Args:
        df: DataFrame with student data
        ml_model: Trained ML model (optional)
        ml_scaler: Feature scaler (optional)
        
    Returns:
        DataFrame with prediction columns added (including both model_phase and final_phase)
    """
    result_df = df.copy()
    
    # Initialize prediction columns (new format)
    result_df['model_phase'] = 'Green'
    result_df['final_phase'] = 'Green'
    result_df['red_reason'] = ''
    result_df['ml_probability'] = None
    result_df['rule_override'] = False
    # Keep legacy column for backward compatibility
    result_df['predicted_phase'] = 'Green'
    
    for idx, row in result_df.iterrows():
        # Convert row to dictionary
        student_data = row.to_dict()
        
        # Get prediction
        prediction = process_single_prediction(student_data, ml_model, ml_scaler)
        
        # Update DataFrame with new format
        result_df.at[idx, 'model_phase'] = prediction['model_phase']
        result_df.at[idx, 'final_phase'] = prediction['final_phase']
        result_df.at[idx, 'red_reason'] = prediction['red_reason']
        result_df.at[idx, 'ml_probability'] = prediction['ml_probability']
        result_df.at[idx, 'rule_override'] = prediction['rule_override']
        # Legacy compatibility
        result_df.at[idx, 'predicted_phase'] = prediction['predicted_phase']
    
    logger.info(f"Added predictions to {len(result_df)} students")
    
    # Log summary for both phases
    model_phase_counts = result_df['model_phase'].value_counts()
    final_phase_counts = result_df['final_phase'].value_counts()
    override_count = result_df['rule_override'].sum()
    
    logger.info(f"Model phase summary: {model_phase_counts.to_dict()}")
    logger.info(f"Final phase summary: {final_phase_counts.to_dict()}")
    logger.info(f"Red-zone overrides: {override_count}")
    
    return result_df


def validate_student_input(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean student input data.
    
    Args:
        student_data: Raw student input
        
    Returns:
        Validated and cleaned student data
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = ['attendance_percent', 'cgpa', 'backlogs']
    
    # Check required fields
    for field in required_fields:
        if field not in student_data:
            # Try alternative field names
            alt_names = {
                'attendance_percent': ['attendance'],
                'cgpa': ['gpa'],
                'backlogs': ['backlogs']
            }
            
            found = False
            for alt_name in alt_names.get(field, []):
                if alt_name in student_data:
                    student_data[field] = student_data[alt_name]
                    found = True
                    break
            
            if not found:
                raise ValueError(f"Missing required field: {field}")
    
    # Validate ranges
    if not (0 <= student_data['attendance_percent'] <= 100):
        raise ValueError("Attendance must be between 0-100%")
    
    if not (0 <= student_data['cgpa'] <= 10):
        raise ValueError("CGPA must be between 0-10")
    
    if student_data['backlogs'] < 0:
        raise ValueError("Backlogs cannot be negative")
    
    # Set defaults for optional fields
    defaults = {
        'marks_10': 60,
        'marks_12': 60,
        'fees_flag': 'Y',
        'suspension_flag': 0,
        'gender': 'M'
    }
    
    for field, default_value in defaults.items():
        if field not in student_data:
            student_data[field] = default_value
    
    return student_data


# ===============================================
# UNIFIED PREDICTION AND OVERRIDE SYSTEM
# ===============================================

def apply_unified_override_rules(row):
    """
    Unified comprehensive override logic for both batch and live predictions.
    Uses optimized priority system: Red → Orange → Yellow → Green.
    
    Args:
        row: pandas Series or dict containing student data
        
    Returns:
        tuple: (phase, reason) or (None, None) if no override
    """
    # Handle both Series and dict inputs
    if hasattr(row, 'get'):
        get_func = row.get
    else:
        get_func = lambda key, default: row.get(key, default) if isinstance(row, dict) else getattr(row, key, default)
    
    A = get_func('attendance', 0)
    C = get_func('cgpa', 0)
    B = get_func('backlogs', 0)
    S = get_func('suspension_flag', 0)
    F = get_func('fees_flag', 0)  # 0 = paid, 1 = unpaid fees
    
    # ============ RED ZONE RULES (HIGHEST PRIORITY) ============
    # Critical attendance issues
    if A < 35:
        return "Red", "Critical attendance (<35%)"

    # Extremely poor attendance even if CGPA is high
    if A < 40:
        return "Red", "Extremely poor attendance (<40%)"

    # Severe backlog issues
    if B > 7:
        return "Red", "Severe backlogs (>7)"

    # Critical backlog count
    if B >= 10:
        return "Red", "Critical backlog count (≥10)"

    # Very low CGPA
    if C < 4:
        return "Red", "Very low CGPA (<4.0)"

    # Severe academic issues
    if A < 45 and C < 4.5:
        return "Red", "Severe academic issues (low attendance, low CGPA)"

    # Combined academic failures
    if C < 4.5 and B > 5:
        return "Red", "Very low CGPA & high backlogs"

    if A < 45 and C < 4.5 and B > 3:
        return "Red", "Severe academic issues (low attendance, low CGPA, high backlogs)"

    # CGPA + backlog + attendance all weak
    if A < 50 and C < 5 and B >= 5:
        return "Red", "Very weak academics across all metrics"

    # Disciplinary issues
    if S >= 3:
        return "Red", "Multiple suspensions (≥3)"

    if S >= 3 and B > 3:
        return "Red", "Multiple suspensions (≥3) & high backlogs"

    # Financial + academic combinations
    if F == 1 and A < 50:
        return "Red", "Fee default & poor attendance"

    if F == 1 and C < 4.5:
        return "Red", "Fee default & very weak CGPA"

    # Financial + disciplinary combo
    if F == 1 and S >= 2:
        return "Red", "Fee default & multiple suspensions"

    # One suspension + severe academics
    if S == 1 and A < 40 and C < 5:
        return "Red", "Suspension with severe academic risk"

    # ============ ORANGE ZONE RULES ============
    # Moderate attendance issues
    if 50 <= A <= 59:
        return "Orange", "Attendance in risk range (50–59%)"

    # Attendance borderline 45–49
    if 45 <= A < 50:
        return "Orange", "Very low attendance (45–49%)"

    # Academic concerns
    if 4.5 <= C < 5.5 and 2 <= B <= 4:
        return "Orange", "Low CGPA with moderate backlogs"

    if C < 5.5 and B > 4:
        return "Orange", "Low CGPA with backlogs"

    # CGPA borderline 5.0–5.5 with few backlogs
    if 5.0 <= C < 5.5 and B <= 2:
        return "Orange", "Borderline CGPA with limited backlogs"

    # CGPA okay but backlog pressure
    if C >= 6 and 3 <= B <= 5:
        return "Orange", "Moderate backlogs despite acceptable CGPA"

    # Disciplinary concerns
    if S == 2 and A < 60:
        return "Orange", "Repeated discipline issues"

    if S == 1 and 60 <= A < 70:
        return "Orange", "Disciplinary issue with average attendance"

    # Financial concerns
    if 45 < A < 60 and F == 1:
        return "Orange", "Fee default & low attendance"

    if F == 1 and 6 <= C < 7:
        return "Orange", "Fee default with weak academics"

    # ============ YELLOW ZONE RULES ============
    # Caution level attendance
    if 70 <= A <= 79 and 5 < C < 6:
        return "Yellow", "Attendance in caution range (70–79%) with weak academic performance"

    # Attendance borderline 65–69
    if 65 <= A < 70:
        return "Yellow", "Attendance below target (65–69%)"

    # Minor academic concerns
    if 6 <= C < 7 and B <= 2:
        return "Yellow", "Slightly weak academics (CGPA 6–7, low backlogs)"

    # Single backlog with CGPA 6–7
    if 6 <= C < 7 and B == 1:
        return "Yellow", "Weak CGPA with one backlog"

    # Minor disciplinary issues
    if S == 1 and A >= 70:
        return "Yellow", "Minor disciplinary issue"

    # Financial with acceptable performance
    if F == 1 and A >= 70:
        return "Yellow", "Fee default but attendance acceptable"

    if F == 1 and C >= 7:
        return "Yellow", "Fee default but strong academics"

    # ============ GREEN ZONE RULES ============
    # Excellence indicators
    if A >= 90 and C > 6.5:
        return "Green", "Excellent attendance"

    if A >= 85 and C >= 8:
        return "Green", "Strong academics (high attendance & CGPA)"

    if A >= 80 and C >= 7 and B == 0 and S == 0:
        return "Green", "Good performance & discipline"

    # Good CGPA even with average attendance
    if 75 <= A < 85 and C >= 8 and B <= 1 and S == 0:
        return "Green", "High CGPA offsets average attendance"

    # Outstanding CGPA with clean record
    if C >= 9 and B == 0 and S == 0:
        return "Green", "Outstanding CGPA with clean record"

    
    # No override → keep ML prediction
    return None, None


def load_ml_model():
    """
    Load the trained Random Forest model for predictions.
    
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


def predict_with_unified_system(student_data: Dict[str, Any], ml_model=None, ml_scaler=None) -> Dict[str, Any]:
    """
    Unified prediction system for both batch and live predictions.
    
    Args:
        student_data: Student features (dict or pandas Series)
        ml_model: Optional ML model tuple (pipeline, phase_map)
        ml_scaler: Optional scaler (not used currently)
        
    Returns:
        Dictionary with unified prediction results
    """
    # Convert to model features
    features = convert_to_model_features(student_data)
    
    # Default values
    ml_probability = None
    model_phase = "Green"  # Default ML prediction
    
    # Try ML prediction if model is available
    if ml_model is not None:
        pipeline, phase_map = ml_model
        try:
            # Prepare features for ML model
            feature_columns = ['attendance', 'cgpa', 'backlogs', 'marks_10th', 'marks_12th', 
                             'fees_flag', 'suspension_flag', 'gender', 'age_at_enrollment']
            
            # Create feature vector (handle missing columns)
            feature_vector = []
            for col in feature_columns:
                if col in features:
                    feature_vector.append(features[col])
                else:
                    feature_vector.append(0)  # Default value
            
            # Reshape for model
            X = np.array(feature_vector).reshape(1, -1)
            
            # Get ML prediction
            y_pred = pipeline.predict(X)[0]
            model_phase = phase_map.get(y_pred, "Green")
            
            # Get probability if available
            if hasattr(pipeline, 'predict_proba'):
                y_proba = pipeline.predict_proba(X)
                ml_probability = float(y_proba[0][1]) if y_proba.shape[1] > 1 else None
                
        except Exception as e:
            logger.warning(f"ML prediction failed: {e}, using default")
    
    # Apply unified override rules
    override_phase, override_reason = apply_unified_override_rules(features)
    
    # Determine final results
    if override_phase is not None:
        final_phase = override_phase
        red_reason = override_reason
        rule_override = True
    else:
        final_phase = model_phase
        red_reason = ""
        rule_override = False
    
    # Return unified result format
    return {
        'model_phase': model_phase,
        'final_phase': final_phase,
        'override_reason': red_reason if red_reason else "Model prediction kept",
        'red_reason': red_reason,
        'ml_probability': ml_probability,
        'rule_override': rule_override,
        'predicted_phase': final_phase  # For backward compatibility
    }


def run_batch_prediction_pipeline():
    """
    Run batch prediction pipeline using unified system.
    Generates the merged_with_predictions.csv file.
    
    Returns:
        dict: Results with predictions and summary
    """
    logger.info("🚀 Starting Unified Batch Prediction Pipeline...")
    
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
    
    # 3. Add engineered features (if feature_utils is available)
    try:
        from models.feature_utils import add_engineered_features
        logger.info("⚙️ Adding engineered features...")
        df = add_engineered_features(df)
        logger.info(f"Dataset after feature engineering: {len(df.columns)} columns")
    except ImportError:
        logger.warning("Feature engineering not available, using basic features")

    # 4. Load ML model
    ml_model = load_ml_model()
    
    # 5. Process each student through unified system
    logger.info("🤖 Running unified predictions...")
    results = []
    
    for idx, row in df.iterrows():
        student_data = row.to_dict()
        prediction = predict_with_unified_system(student_data, ml_model)
        
        # Add results back to dataframe
        for key, value in prediction.items():
            df.at[idx, key] = value
    
    # 6. Save results
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"💾 Saved dataset with predictions → {OUTPUT_PATH}")

    # 7. Generate summary
    ml_phase_counts = df["model_phase"].value_counts().to_dict()
    final_phase_counts = df["final_phase"].value_counts().to_dict()
    override_count = len(df[df["override_reason"] != "Model prediction kept"])
    
    logger.info(f"🔍 Unified Prediction Summary:")
    logger.info(f"  ML predictions: {ml_phase_counts}")
    logger.info(f"  Final predictions: {final_phase_counts}")
    logger.info(f"  Rule-based overrides: {override_count} students")

    # 8. Return results
    results = {
        "status": "success",
        "total_students": len(df),
        "ml_phase_distribution": ml_phase_counts,
        "final_phase_distribution": final_phase_counts,
        "rule_overrides": override_count,
        "ml_model_used": ml_model is not None,
        "output_path": str(OUTPUT_PATH),
        "preview": df[[KEY, "model_phase", "final_phase", "override_reason", "ml_probability"]].head().to_dict('records')
    }
    
    return results
