# feature_utils.py
"""
Shared feature engineering utilities for student dropout prediction models.
Updated to match the newly trained Random Forest model with all required engineered features.

⚠️ CRITICAL: These features MUST be computed consistently for every prediction to match 
the trained model. Any missing feature will cause "missing columns" errors.
"""

import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all engineered features required by the new Random Forest model.
    
    Args:
        df: DataFrame with raw student features (attendance, cgpa, backlogs, 
            suspension_flag, gender)
    
    Returns:
        DataFrame with all engineered features added
        
    Required Raw Features:
        - attendance (0-100%)
        - cgpa (0-10 scale)
        - backlogs (integer >=0)
        - suspension_flag (integer 0-4)
        - gender (categorical)
    
    Generated Engineered Features:
        - att_cgpa_interaction
        - backlog_pressure  
        - att_backlog_ratio
        - risk_index
        - attendance_gap
        - cgpa_gap
        - mild_backlog_flag
        - yellow_zone_score
        - discipline_academic_combo
        - high_performer_flag
    """
    df = df.copy()
    
    # Validate required raw features
    required_features = ['attendance', 'cgpa', 'backlogs', 'suspension_flag', 'gender']
    missing_features = [f for f in required_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required features for model prediction: {missing_features}")
    
    logger.debug(f"Adding engineered features to {len(df)} student records")
    
    # ========== CORE ENGINEERED FEATURES ==========
    
    # 1. Attendance-CGPA interaction (normalized)
    df["att_cgpa_interaction"] = (df["attendance"] / 100) * df["cgpa"]
    
    # 2. Backlog pressure index
    df["backlog_pressure"] = df["backlogs"] / (df["cgpa"] + 1)
    
    # 3. Attendance-backlog ratio
    df["att_backlog_ratio"] = df["attendance"] / (df["backlogs"] + 1)
    
    # 4. Risk index (composite risk score)
    df["risk_index"] = (
        (100 - df["attendance"]) * 0.4 +
        (10 - df["cgpa"]) * 0.4 +
        df["backlogs"] * 2 +
        df["suspension_flag"] * 3
    )
    
    # ========== YELLOW vs ORANGE SEPARATION FEATURES ==========
    
    # 5. Attendance gap (distance from 75% threshold)
    df["attendance_gap"] = abs(df["attendance"] - 75)
    
    # 6. CGPA gap (distance from 6.5 threshold) 
    df["cgpa_gap"] = abs(df["cgpa"] - 6.5)
    
    # 7. Mild backlog flag (1-2 backlogs vs more)
    df["mild_backlog_flag"] = ((df["backlogs"] >= 1) & (df["backlogs"] <= 2)).astype(int)
    
    # ========== CLASSIFICATION SUPPORT FEATURES ==========
    
    # 8. Yellow zone score (borderline students)
    df["yellow_zone_score"] = (
        (df["attendance"] >= 70) & (df["attendance"] <= 79) &
        (df["cgpa"] >= 5.0) & (df["cgpa"] <= 6.0)
    ).astype(int)
    
    # 9. Discipline-academic combo (suspension + low CGPA)
    df["discipline_academic_combo"] = (
        (df["suspension_flag"] > 0) & (df["cgpa"] < 6.0)
    ).astype(int)
    
    # 10. High performer flag (excellent students)
    df["high_performer_flag"] = (
        (df["attendance"] >= 85) & 
        (df["cgpa"] >= 8.0) & 
        (df["backlogs"] == 0)
    ).astype(int)
    
    logger.debug("✅ All engineered features added successfully")
    
    # Log feature summary for debugging
    engineered_features = [
        'att_cgpa_interaction', 'backlog_pressure', 'att_backlog_ratio', 'risk_index',
        'attendance_gap', 'cgpa_gap', 'mild_backlog_flag', 'yellow_zone_score',
        'discipline_academic_combo', 'high_performer_flag'
    ]
    
    logger.debug(f"Added {len(engineered_features)} engineered features: {engineered_features}")
    
    return df


def validate_model_features(df: pd.DataFrame) -> bool:
    """
    Validate that all required features for the model are present.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        bool: True if all features are present
        
    Raises:
        ValueError: If any required features are missing
    """
    # Raw features required by model
    raw_features = ['attendance', 'cgpa', 'backlogs', 'suspension_flag', 'gender']
    
    # Engineered features that should be computed
    engineered_features = [
        'att_cgpa_interaction', 'backlog_pressure', 'att_backlog_ratio', 'risk_index',
        'attendance_gap', 'cgpa_gap', 'mild_backlog_flag', 'yellow_zone_score',
        'discipline_academic_combo', 'high_performer_flag'
    ]
    
    all_required_features = raw_features + engineered_features
    missing_features = [f for f in all_required_features if f not in df.columns]
    
    if missing_features:
        raise ValueError(f"Missing required features for prediction: {missing_features}")
    
    logger.debug(f"✅ All {len(all_required_features)} required features are present")
    return True
