#!/usr/bin/env python3
"""
Test to verify we have ONLY one unified override system working correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils import apply_unified_override_rules, predict_with_unified_system

def test_single_override_system():
    """Test that we have only one override system working"""
    
    print("🧪 Testing Single Unified Override System")
    print("=" * 50)
    
    # Test data
    test_student = {
        'attendance': 68,
        'cgpa': 8.29,
        'backlogs': 0,
        'fees_flag': 0,
        'suspension_flag': 0
    }
    
    print("1. Testing apply_unified_override_rules directly:")
    override_phase, override_reason = apply_unified_override_rules(test_student)
    print(f"   Override result: {override_phase} | '{override_reason}'")
    
    print("\n2. Testing predict_with_unified_system:")
    prediction = predict_with_unified_system(test_student)
    print(f"   Final phase: {prediction['final_phase']}")
    print(f"   Override reason: {prediction['override_reason']}")
    print(f"   Rule override: {prediction['rule_override']}")
    
    print("\n3. Verifying consistency:")
    if override_phase is not None:
        expected_final = override_phase
        expected_override = True
    else:
        expected_final = prediction['model_phase']  # Should use ML prediction
        expected_override = False
    
    if (prediction['final_phase'] == expected_final and 
        prediction['rule_override'] == expected_override):
        print("   ✅ Single system working consistently!")
    else:
        print("   ❌ Inconsistency detected!")
    
    print("\n4. Testing fees_flag logic:")
    test_student_fees = test_student.copy()
    test_student_fees['fees_flag'] = 1  # Unpaid fees
    test_student_fees['attendance'] = 75  # Good attendance
    
    prediction_fees = predict_with_unified_system(test_student_fees)
    print(f"   Student with unpaid fees: {prediction_fees['final_phase']}")
    print(f"   Reason: {prediction_fees['override_reason']}")
    
    print("\n5. Testing that old legacy function is gone:")
    try:
        from app.utils import apply_red_zone_rules_to_phase
        print("   ❌ Legacy function still exists!")
    except ImportError:
        print("   ✅ Legacy function successfully removed!")

if __name__ == "__main__":
    test_single_override_system()