#!/usr/bin/env python3
"""
Test batch prediction pipeline
"""
from app.utils import run_batch_prediction_pipeline

try:
    print("Testing batch prediction pipeline...")
    result = run_batch_prediction_pipeline()
    print("✅ Batch pipeline successful!")
    print("   Total students:", result['total_students'])
    print("   Rule overrides:", result['rule_overrides']) 
    print("   ML model used:", result['ml_model_used'])
except Exception as e:
    print("❌ Batch pipeline failed:", e)