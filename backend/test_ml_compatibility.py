#!/usr/bin/env python3
"""
Test ML model compatibility between main.py and utils.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils import predict_with_unified_system, load_ml_model
import joblib
from pathlib import Path

def test_ml_model_compatibility():
    """Test that ML model works with the unified system"""
    
    print("🧪 Testing ML Model Compatibility")
    print("=" * 50)
    
    # Test student data
    test_student = {
        'attendance': 75,
        'cgpa': 7.5,
        'backlogs': 1,
        'fees_flag': 0,
        'suspension_flag': 0,
        'marks_10th': 80,
        'marks_12th': 85,
        'gender': 'M',
        'age_at_enrollment': 19
    }
    
    print("1. Testing with utils.py model loading:")
    try:
        ml_model_utils = load_ml_model()
        if ml_model_utils is not None:
            prediction_utils = predict_with_unified_system(test_student, ml_model_utils)
            print(f"   ✅ Utils model: {prediction_utils['model_phase']} -> {prediction_utils['final_phase']}")
        else:
            print("   ⚠️ Utils model: Not loaded (file not found)")
    except Exception as e:
        print(f"   ❌ Utils model error: {e}")
    
    print("\n2. Testing with main.py-style model loading:")
    try:
        # Simulate how main.py loads the model
        MODEL_PATH = Path(__file__).parent / "app" / "models" / "rf_pipeline_broad.joblib"
        if MODEL_PATH.exists():
            ml_model_main = joblib.load(MODEL_PATH)
            prediction_main = predict_with_unified_system(test_student, ml_model_main)
            print(f"   ✅ Main model: {prediction_main['model_phase']} -> {prediction_main['final_phase']}")
        else:
            print("   ⚠️ Main model: File not found")
    except Exception as e:
        print(f"   ❌ Main model error: {e}")
    
    print("\n3. Testing with None (rules only):")
    try:
        prediction_rules = predict_with_unified_system(test_student, None)
        print(f"   ✅ Rules only: {prediction_rules['model_phase']} -> {prediction_rules['final_phase']}")
    except Exception as e:
        print(f"   ❌ Rules only error: {e}")

if __name__ == "__main__":
    test_ml_model_compatibility()