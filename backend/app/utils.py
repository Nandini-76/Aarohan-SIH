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
        
    Note: Does NOT provide defaults for required features to allow proper validation
    """
    features = {}
    
    # Required features - no defaults provided to allow validation to catch missing ones
    if 'attendance_percent' in student_data:
        features['attendance'] = student_data['attendance_percent']
    elif 'attendance' in student_data:
        features['attendance'] = student_data['attendance']
    
    if 'cgpa' in student_data:
        features['cgpa'] = student_data['cgpa']
    
    if 'backlogs' in student_data:
        features['backlogs'] = student_data['backlogs']
    
    if 'suspension_flag' in student_data:
        features['suspension_flag'] = int(student_data['suspension_flag'])
    
    if 'gender' in student_data:
        features['gender'] = student_data['gender']
    
    # Optional features - provide defaults
    features['marks_10th'] = student_data.get('marks_10', student_data.get('marks_10th', 60))
    features['marks_12th'] = student_data.get('marks_12', student_data.get('marks_12th', 60))
    features['fees_flag'] = _normalize_fees_flag(student_data.get('fees_flag', 0))
    
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
    result_df['predicted_phase'] = 'Green'
    
    for idx, row in result_df.iterrows():
        # Convert row to dictionary
        student_data = row.to_dict()
        
        # Get prediction
        prediction = process_single_prediction(student_data, ml_model, ml_scaler)
        
        # Send notification if student is at Orange or Red risk
        final_risk_level = prediction['final_phase']
        send_notification(student_data, final_risk_level)
        
        # Update DataFrame with new format
        result_df.at[idx, 'model_phase'] = prediction['model_phase']
        result_df.at[idx, 'final_phase'] = prediction['final_phase']
        result_df.at[idx, 'red_reason'] = prediction['red_reason']
        result_df.at[idx, 'ml_probability'] = prediction['ml_probability']
        result_df.at[idx, 'rule_override'] = prediction['rule_override']
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
    Strict Red Zone Safety Override Only.
    
    This function ONLY checks for critical safety thresholds that should force Red.
    For Green, Yellow, Orange → ML model prediction is always used (no overrides).
    
    Args:
        row: pandas Series or dict containing student data
        
    Returns:
        tuple: ("Red", reason) for critical cases, (None, None) otherwise
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
    
    # ============ STRICT RED ZONE SAFETY OVERRIDES ONLY ============
    
    # Critical attendance thresholds
    if A < 30:
        return "Red", "Forced Red due to critical safety threshold: Attendance <30%"
    
    # Critical CGPA threshold
    if C < 3.0:
        return "Red", "Forced Red due to critical safety threshold: CGPA <3.0"
    
    # Critical backlog threshold
    if B >= 8:
        return "Red", "Forced Red due to critical safety threshold: Backlogs ≥8"
    
    # Critical suspension threshold
    if S >= 3:
        return "Red", "Forced Red due to critical safety threshold: Suspensions ≥3"
    
    # Combined critical thresholds (extremely severe cases)
    if A < 35 and C < 4.0:
        return "Red", "Forced Red due to critical safety threshold: Extremely poor attendance + very low CGPA"
    
    if C < 4.0 and B >= 6:
        return "Red", "Forced Red due to critical safety threshold: Very low CGPA + high backlogs"
    
    # No override → use ML prediction for Green, Yellow, Orange
    return None, None


def generate_ml_explanation(model_phase: str, features: dict, ml_probability: float = None) -> str:
    """
    Generate explanation text based on ML model prediction and student features.
    
    Args:
        model_phase: ML model prediction (Green, Yellow, Orange, Red)
        features: Student feature dictionary
        ml_probability: ML model probability score
        
    Returns:
        str: Explanation text for the prediction
    """
    A = features.get('attendance', 0)
    C = features.get('cgpa', 0)
    B = features.get('backlogs', 0)
    S = features.get('suspension_flag', 0)
    
    # Base explanation with ML confidence
    if ml_probability is not None:
        confidence = f" (ML confidence: {ml_probability:.1%})"
    else:
        confidence = ""
    
    if model_phase == "Green":
        if A >= 85 and C >= 7.5:
            return f"Low risk - Strong academic performance{confidence}"
        elif A >= 80:
            return f"Low risk - Good attendance record{confidence}"
        elif C >= 8.0:
            return f"Low risk - High CGPA performance{confidence}"
        else:
            return f"Low risk - Overall stable performance{confidence}"
    
    elif model_phase == "Yellow":
        factors = []
        if 65 <= A < 80:
            factors.append("moderate attendance")
        if 5.5 <= C < 7.0:
            factors.append("borderline CGPA")
        if B >= 1:
            factors.append(f"{B} backlog(s)")
        if S >= 1:
            factors.append("disciplinary issues")
        
        if factors:
            return f"Medium risk - {', '.join(factors)}{confidence}"
        else:
            return f"Medium risk - Multiple risk indicators detected{confidence}"
    
    elif model_phase == "Orange":
        factors = []
        if A < 65:
            factors.append("low attendance")
        if C < 5.5:
            factors.append("low CGPA")
        if B >= 3:
            factors.append("multiple backlogs")
        if S >= 2:
            factors.append("repeated disciplinary issues")
        
        if factors:
            return f"High risk - {', '.join(factors)}{confidence}"
        else:
            return f"High risk - Significant academic concerns{confidence}"
    
    elif model_phase == "Red":
        return f"Critical risk - ML model prediction{confidence}"
    
    else:
        return f"Risk assessment based on ML model{confidence}"
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
        
        # Add models directory to Python path for feature_utils import
        import sys
        models_dir = CURRENT_DIR / "models"
        if str(models_dir) not in sys.path:
            sys.path.insert(0, str(models_dir))
        
        obj = joblib.load(MODEL_PATH)
        
        if isinstance(obj, dict):
            pipeline = obj.get("pipeline")
            phase_map = obj.get("phase_map", {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"})
        else:
            # If obj is the pipeline directly
            pipeline = obj
            phase_map = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}
        
        # Validate pipeline has required methods
        if pipeline is not None and hasattr(pipeline, 'predict'):
            logger.info("✅ Model loaded successfully")
            return pipeline, phase_map
        else:
            logger.warning(f"Invalid pipeline object: {type(pipeline)}")
            return None, None
        
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        logger.info("📋 Falling back to rule-based predictions only")
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
    
    # Validate required raw features before proceeding
    required_raw_features = ['attendance', 'cgpa', 'backlogs', 'suspension_flag', 'gender']
    missing_features = [f for f in required_raw_features if f not in features]
    if missing_features:
        raise ValueError(f"Missing required features for prediction: {missing_features}")
    
    # Default values
    ml_probability = None
    model_phase = "Green"  # Default ML prediction
    
    # Try ML prediction if model is available
    if ml_model is not None:
        # Handle different model formats
        if isinstance(ml_model, tuple) and len(ml_model) == 2:
            # New format: (pipeline, phase_map)
            pipeline, phase_map = ml_model
        elif isinstance(ml_model, dict):
            # Dictionary format with pipeline and phase_map
            pipeline = ml_model.get("pipeline")
            phase_map = ml_model.get("phase_map", {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"})
        else:
            # Direct pipeline format
            pipeline = ml_model
            phase_map = {0: "Green", 1: "Yellow", 2: "Orange", 3: "Red"}
        
        # Only proceed if we have a valid pipeline
        if pipeline is not None and hasattr(pipeline, 'predict'):
            try:
                # Create a DataFrame with the single student's data (model expects DataFrame)
                single_student_df = pd.DataFrame([features])
                
                # Add engineered features to match training data
                try:
                    # Import the updated feature engineering function
                    add_engineered_features = None
                    validate_model_features = None
                    
                    # Try multiple import paths for different environments
                    try:
                        from models.feature_utils import add_engineered_features, validate_model_features
                    except ImportError:
                        try:
                            from app.models.feature_utils import add_engineered_features, validate_model_features
                        except ImportError:
                            try:
                                import sys
                                import os
                                # Add both possible model directories to path
                                model_paths = [
                                    os.path.join(os.path.dirname(__file__), "models"),
                                    os.path.join(os.path.dirname(__file__), "..", "models"),
                                    "/opt/render/project/src/backend/app/models"  # Render production path
                                ]
                                for path in model_paths:
                                    if os.path.exists(path) and path not in sys.path:
                                        sys.path.insert(0, path)
                                from feature_utils import add_engineered_features, validate_model_features
                            except ImportError:
                                pass
                    
                    # Apply feature engineering if available
                    if add_engineered_features is not None:
                        # Validate raw features first
                        required_raw_features = ['attendance', 'cgpa', 'backlogs', 'suspension_flag', 'gender']
                        missing_raw = [f for f in required_raw_features if f not in single_student_df.columns]
                        if missing_raw:
                            raise ValueError(f"Missing required raw features for prediction: {missing_raw}")
                        
                        # Add engineered features
                        single_student_df = add_engineered_features(single_student_df)
                        
                        # Validate all features are present
                        if validate_model_features is not None:
                            validate_model_features(single_student_df)
                        
                        logger.debug("✅ All engineered features added and validated for ML prediction")
                    else:
                        logger.error("❌ Feature engineering function not available - model will likely fail!")
                        raise ImportError("Feature engineering module not found")
                        
                except ImportError as e:
                    logger.error(f"❌ Failed to import feature engineering: {e}")
                    raise ImportError(f"Feature engineering not available: {e}")
                except ValueError as e:
                    logger.error(f"❌ Feature validation failed: {e}")
                    raise ValueError(f"Invalid features for prediction: {e}")
                except Exception as e:
                    logger.error(f"❌ Feature engineering failed: {e}")
                    raise RuntimeError(f"Feature engineering error: {e}")
                
                # Get ML prediction (model handles preprocessing internally)
                y_pred = pipeline.predict(single_student_df)[0]
                
                # Handle both numeric and string predictions
                if isinstance(y_pred, str):
                    # Model returns phase name directly
                    model_phase = y_pred
                else:
                    # Model returns numeric code, map to phase name
                    y_pred_int = int(y_pred)
                    model_phase = phase_map.get(y_pred_int, "Green")
                
                # Get probability if available
                if hasattr(pipeline, 'predict_proba'):
                    y_proba = pipeline.predict_proba(single_student_df)
                    ml_probability = float(y_proba[0][1]) if y_proba.shape[1] > 1 else None
                    
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}, using default")
        else:
            logger.warning(f"Invalid pipeline object: {type(pipeline)}, using default")
    
    # Apply unified override rules (Red zone safety only)
    override_phase, override_reason = apply_unified_override_rules(features)
    
    # Determine final results and explanations
    if override_phase is not None:
        # Red zone safety override
        final_phase = override_phase
        explanation = override_reason
        rule_override = True
    else:
        # Use ML prediction - generate ML-based explanation
        final_phase = model_phase
        explanation = generate_ml_explanation(model_phase, features, ml_probability)
        rule_override = False
    
    # Return unified result format
    return {
        'model_phase': model_phase,
        'final_phase': final_phase,
        'override_reason': explanation,
        'red_reason': override_reason if override_phase is not None else "",
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
    add_engineered_features = None
    validate_model_features = None
    
    # Try multiple import paths for different environments
    try:
        from models.feature_utils import add_engineered_features, validate_model_features
    except ImportError:
        try:
            from app.models.feature_utils import add_engineered_features, validate_model_features
        except ImportError:
            try:
                import sys
                import os
                # Add both possible model directories to path
                model_paths = [
                    os.path.join(os.path.dirname(__file__), "models"),
                    os.path.join(os.path.dirname(__file__), "..", "models"),
                    "/opt/render/project/src/backend/app/models"  # Render production path
                ]
                for path in model_paths:
                    if os.path.exists(path) and path not in sys.path:
                        sys.path.insert(0, path)
                from feature_utils import add_engineered_features, validate_model_features
            except ImportError:
                pass
    
    if add_engineered_features is not None:
        logger.info("⚙️ Adding engineered features...")
        try:
            df = add_engineered_features(df)
            logger.info(f"✅ Dataset after feature engineering: {len(df.columns)} columns")
            
            # Validate all features are present
            if validate_model_features is not None:
                validate_model_features(df)
                logger.info("✅ All required model features validated")
                
        except Exception as e:
            logger.error(f"❌ Feature engineering failed in batch pipeline: {e}")
            raise RuntimeError(f"Feature engineering error in batch processing: {e}")
    else:
        logger.error("❌ Feature engineering not available - predictions will likely fail!")
        raise ImportError("Feature engineering module not found for batch processing")

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


def send_notification(student_data: Dict[str, Any], risk_level: str) -> None:
    """
    Simulate WhatsApp notification for students at Orange or Red risk levels.
    
    This function simulates sending notifications to counselors, mentors, and parents
    when a student is identified as being at Orange or Red risk. Currently logs 
    the notification instead of actually sending it. Can be easily replaced with
    actual Twilio API calls later.
    
    Args:
        student_data: Dictionary containing student information
        risk_level: Final risk level ("Green", "Yellow", "Orange", or "Red")
    """
    # Only send notifications for Orange and Red risk levels
    if risk_level not in ["Orange", "Red"]:
        return
    
    # Extract student information
    student_id = student_data.get('enrollment_no', 'Unknown')
    
    # Generate student name from enrollment number for demo purposes
    # In a real system, this would come from the student database
    student_name = generate_student_name_from_id(student_id)
    
    # Format the notification message
    notification_message = (
        f"🚨 Student {student_name} is at {risk_level} risk. "
        f"Notification sent to Counselor, Mentor, and Parents."
    )
    
    # Log the simulated notification
    logger.info(f"[Notification] WhatsApp message simulated for {student_id}: \"{notification_message}\"")
    
    # TODO: Replace this with actual Twilio API call when ready
    # Example for future implementation:
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(
    #     body=notification_message,
    #     from_='whatsapp:+1234567890',
    #     to='whatsapp:+counselor_number'
    # )


def generate_student_name_from_id(student_id: str) -> str:
    """
    Generate a realistic student name from enrollment number for demonstration.
    In a real system, this would be replaced with actual database lookup.
    
    Args:
        student_id: Student enrollment number
        
    Returns:
        Generated student name for demonstration
    """
    if not student_id or student_id == 'Unknown':
        return "Unknown Student"
    
    # Sample names for demonstration
    sample_names = [
        "Ananya Sharma", "Rohan Patel", "Priya Singh", "Arjun Kumar", 
        "Sneha Gupta", "Vikram Joshi", "Kavya Reddy", "Aditya Verma",
        "Riya Agarwal", "Kartik Mehta", "Isha Malhotra", "Harsh Kapoor"
    ]
    
    # Use hash of student_id to consistently get the same name for the same ID
    name_index = hash(student_id) % len(sample_names)
    return sample_names[name_index]
