# feature_utils.py
"""
Shared feature engineering utilities for student dropout prediction models.
Optimized feature engineering: focuses on attendance, CGPA, backlogs,
and penalties (fees/suspensions) while removing marks_10th, marks_12th,
and age_at_enrollment.
"""

import pandas as pd
import numpy as np

def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Attendance-CGPA synergy (normalized)
    if "attendance" in df.columns and "cgpa" in df.columns:
        df["att_cgpa_interaction"] = (df["attendance"] / 100.0) * (df["cgpa"] / 10.0)

    # 2. Attendance stress ratio
    if "attendance" in df.columns and "backlogs" in df.columns:
        df["att_backlog_ratio"] = df["backlogs"] / (df["attendance"] + 1.0)

    # 3. Backlog pressure index (log-scaled to avoid skew from extreme values)
    if "cgpa" in df.columns and "backlogs" in df.columns:
        df["backlog_pressure"] = np.log1p(df["backlogs"]) / (df["cgpa"] + 1.0)

    # 4. Academic Risk Index (low cgpa + high backlogs)
    if "cgpa" in df.columns and "backlogs" in df.columns:
        df["ari"] = (10 - df["cgpa"]) + (df["backlogs"] * 0.5)

    # 5. Penalty score (fees + suspension, weighted)
    if "fees_flag" in df.columns or "suspension_flag" in df.columns:
        fees = df["fees_flag"] if "fees_flag" in df.columns else 0
        suspension = df["suspension_flag"] if "suspension_flag" in df.columns else 0
        df["penalty_score"] = (fees * 0.7) + (suspension * 1.3)

    return df
