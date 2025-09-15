"""
Utility functions for student dropout prediction system.
Includes red-zone rule engine and helper functions.

Author: AI Assistant
Date: September 15, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


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


def apply_red_zone_rules_to_phase(row: pd.Series, model_phase: str) -> Tuple[str, str]:
    """
    Apply Red-Zone override rules to determine final phase.
    
    This function takes the ML model's prediction and applies strict safety override rules.
    If any red-zone condition is met, it overrides to Red regardless of model prediction.
    
    Original extensive Red-zone criteria:
    A = Attendance, B = Backlogs, C = CGPA, F = Fees Flag, S = Suspension
    
    Args:
        row: Pandas Series containing student data
        model_phase: The ML model's prediction (Green, Yellow, Orange, Red)
        
    Returns:
        Tuple of (final_phase, red_reason)
        - final_phase: Final prediction after applying overrides
        - red_reason: Explanation if overridden, empty string otherwise
    """
    def is_red_zone(row):
        """
        Apply strict rules to decide if student is in Red zone.
        A = Attendance, B = Backlogs, C = CGPA, F = Fees Flag, S = Suspension
        """
        A = row.get("attendance", 100)
        B = row.get("backlogs", 0)
        C = row.get("cgpa", 10)
        F = row.get("fees_flag", 1)
        S = row.get("suspension_flag", 0)

        # RULES (original extensive logic)
        if A < 35: return "Attendance < 35"
        if B > 7: return "Backlogs > 7"
        if A < 45 and B > 5: return "Low attendance & high backlogs"
        if C < 4.5 and B > 5: return "Very low CGPA & high backlogs"
        if A < 45 and C < 5: return "Low attendance & low CGPA"
        if S >= 2 and A < 50: return "Multiple suspensions & low attendance"
        if S >= 2 and B > 3: return "Multiple suspensions & backlogs"
        if S >= 3 and C < 5: return "Multiple suspensions & low CGPA"
        if F == 0 and B > 2: return "Fee default & backlogs"
        if F == 0 and C < 4.5: return "Fee default & very low CGPA"
        if F == 0 and A < 50: return "Fee default & low attendance"
        if A < 45 and C < 5 and B > 3: return "Low attendance, low CGPA, high backlogs"
        if C < 5.5 and F == 0 and B > 2: return "Low CGPA, fee default & backlogs"
        if A < 45 and S > 2 and B > 3: return "Low attendance, suspensions & backlogs"
        if C < 5.5 and F == 0 and A < 45: return "Low CGPA, fee default & low attendance"
        if A < 45 and C < 5 and B > 5 and F == 0: return "Severe academic issues"
        if F == 0 and S > 3 and A < 50 and C < 4.5: return "Fee default, suspensions, very weak academics"

        return None  # Not Red-Zone
    
    # Apply the red-zone check
    red_reason = is_red_zone(row)
    
    if red_reason:
        return "Red", red_reason
    
    # No override needed, keep model prediction
    return model_phase, ""


def apply_red_zone_rules(student_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Legacy function for backward compatibility.
    Apply red-zone rule engine to determine high-risk students.
    
    Original extensive Red-zone criteria:
    A = Attendance, B = Backlogs, C = CGPA, F = Fees Flag, S = Suspension
    
    Args:
        student_data: Dictionary containing student features
        
    Returns:
        Tuple of (predicted_phase, red_reason)
        - predicted_phase: "Red" if triggered, None otherwise
        - red_reason: Explanation if Red, empty string otherwise
    """
    def is_red_zone(data):
        """
        Apply strict rules to decide if student is in Red zone.
        A = Attendance, B = Backlogs, C = CGPA, F = Fees Flag, S = Suspension
        """
        A = data.get("attendance", 100)
        B = data.get("backlogs", 0)
        C = data.get("cgpa", 10)
        F = data.get("fees_flag", 1)
        S = data.get("suspension_flag", 0)

        # RULES (original extensive logic)
        if A < 35: return "Attendance < 35"
        if B > 7: return "Backlogs > 7"
        if A < 45 and B > 5: return "Low attendance & high backlogs"
        if C < 4.5 and B > 5: return "Very low CGPA & high backlogs"
        if A < 45 and C < 5: return "Low attendance & low CGPA"
        if S >= 2 and A < 50: return "Multiple suspensions & low attendance"
        if S >= 2 and B > 3: return "Multiple suspensions & backlogs"
        if S >= 3 and C < 5: return "Multiple suspensions & low CGPA"
        if F == 0 and B > 2: return "Fee default & backlogs"
        if F == 0 and C < 4.5: return "Fee default & very low CGPA"
        if F == 0 and A < 50: return "Fee default & low attendance"
        if A < 45 and C < 5 and B > 3: return "Low attendance, low CGPA, high backlogs"
        if C < 5.5 and F == 0 and B > 2: return "Low CGPA, fee default & backlogs"
        if A < 45 and S > 2 and B > 3: return "Low attendance, suspensions & backlogs"
        if C < 5.5 and F == 0 and A < 45: return "Low CGPA, fee default & low attendance"
        if A < 45 and C < 5 and B > 5 and F == 0: return "Severe academic issues"
        if F == 0 and S > 3 and A < 50 and C < 4.5: return "Fee default, suspensions, very weak academics"

        return None  # Not Red-Zone
    
    red_reason = is_red_zone(student_data)
    
    if red_reason:
        return "Red", red_reason
    
    # No red-zone trigger
    return None, ""


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
        'fees_flag': 1 if student_data.get('fees_flag', 'Y') == 'N' else 0,
        'suspension_flag': student_data.get('suspension_flag', 0),
        'gender': student_data.get('gender', 'M')
    }
    
    return features


def process_single_prediction(student_data: Dict[str, Any], ml_model=None, ml_scaler=None) -> Dict[str, Any]:
    """
    Process a single student prediction with red-zone override.
    
    Args:
        student_data: Student features
        ml_model: Trained ML model (optional)
        ml_scaler: Feature scaler (optional)
        
    Returns:
        Dictionary with prediction results including model_phase and final_phase
    """
    # Convert to model features
    features = convert_to_model_features(student_data)
    
    # Get ML model prediction first
    ml_probability = None
    model_phase = "Green"  # Default
    
    if ml_model is not None:
        try:
            # Check if model is a dictionary (saved model metadata)
            if isinstance(ml_model, dict):
                # If it's a dictionary, we might have model metadata but not the actual model
                logger.warning("Model is a dictionary - may contain metadata only")
                ml_probability = None
            elif hasattr(ml_model, 'predict_proba'):
                # Prepare features for ML model
                feature_order = ['attendance', 'cgpa', 'marks_10th', 'marks_12th', 'backlogs', 'fees_flag', 'suspension_flag']
                X = np.array([[features[f] for f in feature_order]])
                
                # Direct prediction (model is a pipeline or doesn't need scaling)
                ml_probability = float(ml_model.predict_proba(X)[0, 1])  # Convert to Python float
            else:
                logger.warning("Model object doesn't have predict_proba method")
                ml_probability = None
            
            # Convert ML probability to model phase
            if ml_probability is not None:
                if ml_probability >= 0.7:
                    model_phase = "Red"
                elif ml_probability >= 0.5:
                    model_phase = "Orange"
                elif ml_probability >= 0.4:
                    model_phase = "Yellow"
                else:
                    model_phase = "Green"
                
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            ml_probability = None
    
    # If ML model failed, use rule-based prediction as fallback for model_phase
    if ml_probability is None:
        # Calculate risk score for model prediction
        attendance = features.get('attendance', 80)
        cgpa = features.get('cgpa', 7.0)
        backlogs = features.get('backlogs', 0)
        suspension_flag = features.get('suspension_flag', 0)
        fees_flag = features.get('fees_flag', 0)
        
        # Risk scoring for model prediction (different from red-zone rules)
        risk_score = 0
        
        # Attendance factor (0-30 points)
        if attendance < 50:
            risk_score += 30
        elif attendance < 65:
            risk_score += 20
        elif attendance < 75:
            risk_score += 15
        elif attendance < 85:
            risk_score += 10
        
        # CGPA factor (0-25 points)
        if cgpa < 5.0:
            risk_score += 25
        elif cgpa < 6.5:
            risk_score += 15
        elif cgpa < 7.5:
            risk_score += 10
        elif cgpa < 8.5:
            risk_score += 5
        
        # Backlogs factor (0-20 points)
        if backlogs > 3:
            risk_score += 20
        elif backlogs > 1:
            risk_score += 15
        elif backlogs > 0:
            risk_score += 10
        
        # Disciplinary issues (0-15 points)
        if suspension_flag > 0:
            risk_score += 15
        if fees_flag > 0:
            risk_score += 10
        
        # Convert score to model phase and probability
        if risk_score >= 50:
            model_phase = "Orange"
            ml_probability = 0.75
        elif risk_score >= 30:
            model_phase = "Yellow"
            ml_probability = 0.55
        elif risk_score >= 15:
            model_phase = "Yellow"
            ml_probability = 0.45
        else:
            model_phase = "Green"
            ml_probability = 0.25
    
    # Apply red-zone overrides to get final phase
    # Convert features dict to pandas Series for compatibility
    features_series = pd.Series(features)
    final_phase, red_reason = apply_red_zone_rules_to_phase(features_series, model_phase)
    rule_override = (final_phase != model_phase)
    
    return {
        "model_phase": model_phase,
        "final_phase": final_phase,
        "red_reason": red_reason,
        "ml_probability": ml_probability,
        "rule_override": rule_override,
        # Keep legacy field for backward compatibility
        "predicted_phase": final_phase
    }


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
