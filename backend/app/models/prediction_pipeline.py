#!/usr/bin/env python3
"""
Prediction pipeline - DEPRECATED
This file is now a wrapper around the unified system in utils.py
Use utils.run_batch_prediction_pipeline() for new code.
"""

import sys
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Import the unified system
from utils import run_batch_prediction_pipeline


def main():
    """CLI entry point - redirects to unified system"""
    try:
        results = run_batch_prediction_pipeline()
        print(f"\n✅ Unified Prediction complete:")
        print(f"   Total students: {results['total_students']}")
        print(f"   ML predictions: {results['ml_phase_distribution']}")
        print(f"   Final predictions: {results['final_phase_distribution']}")
        print(f"   Rule-based overrides: {results['rule_overrides']}")
        print(f"   ML model used: {results['ml_model_used']}")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise


# Legacy function redirects
def run_prediction_pipeline():
    """Legacy function - redirects to unified system"""
    return run_batch_prediction_pipeline()


if __name__ == "__main__":
    main()
