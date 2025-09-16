#!/usr/bin/env python3
"""
Test script to verify the updated red zone rules function works correctly.
"""

import sys
import os
import pandas as pd

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils import apply_red_zone_rules_to_phase

def test_red_zone_rules():
    """Test the updated red zone rules with various student scenarios"""
    
    print("🧪 Testing Updated Red Zone Rules")
    print("=" * 50)
    
    # Test cases with expected results
    test_cases = [
        {
            "name": "Good student - should remain Green",
            "data": {"attendance": 85, "cgpa": 8.5, "backlogs": 0, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Green",
            "expected_final": "Green",
            "expected_reason": ""
        },
        {
            "name": "Attendance below 40% - should be Red",
            "data": {"attendance": 35, "cgpa": 7.0, "backlogs": 1, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Green",
            "expected_final": "Red",
            "expected_reason": "Attendance below 40%"
        },
        {
            "name": "Very low attendance & low CGPA - should be Red",
            "data": {"attendance": 45, "cgpa": 4.5, "backlogs": 1, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "Very low attendance & low CGPA"
        },
        {
            "name": "Low attendance with multiple backlogs - should be Red",
            "data": {"attendance": 48, "cgpa": 6.0, "backlogs": 3, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "Low attendance with multiple backlogs"
        },
        {
            "name": "Too many backlogs - should be Red",
            "data": {"attendance": 70, "cgpa": 6.0, "backlogs": 5, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Orange",
            "expected_final": "Red",
            "expected_reason": "Too many backlogs"
        },
        {
            "name": "High backlogs & poor CGPA - should be Red",
            "data": {"attendance": 65, "cgpa": 4.8, "backlogs": 3, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "High backlogs & poor CGPA"
        },
        {
            "name": "Critically low CGPA - should be Red",
            "data": {"attendance": 70, "cgpa": 4.0, "backlogs": 1, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "Critically low CGPA"
        },
        {
            "name": "Multiple suspensions - should be Red",
            "data": {"attendance": 70, "cgpa": 6.0, "backlogs": 1, "fees_flag": 0, "suspension_flag": 2},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "Multiple suspensions"
        },
        {
            "name": "Suspensions with high backlogs - should be Red",
            "data": {"attendance": 70, "cgpa": 6.0, "backlogs": 3, "fees_flag": 0, "suspension_flag": 1},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "Suspensions with high backlogs"
        },
        {
            "name": "Unpaid fees - should be Red",
            "data": {"attendance": 75, "cgpa": 7.0, "backlogs": 1, "fees_flag": 1, "suspension_flag": 0},
            "model_phase": "Green",
            "expected_final": "Red",
            "expected_reason": "Unpaid fees"
        },
        {
            "name": "High composite risk index - should be Red",
            "data": {"attendance": 55, "cgpa": 5.5, "backlogs": 2, "fees_flag": 0, "suspension_flag": 1},
            "model_phase": "Yellow",
            "expected_final": "Red",
            "expected_reason": "High composite risk index"
        },
        {
            "name": "Borderline student - should remain as model prediction",
            "data": {"attendance": 65, "cgpa": 6.0, "backlogs": 2, "fees_flag": 0, "suspension_flag": 0},
            "model_phase": "Yellow",
            "expected_final": "Yellow",
            "expected_reason": ""
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        # Create pandas Series from test data
        row = pd.Series(test_case['data'])
        
        # Apply the function
        final_phase, red_reason = apply_red_zone_rules_to_phase(row, test_case['model_phase'])
        
        # Check results
        phase_correct = final_phase == test_case['expected_final']
        reason_correct = red_reason == test_case['expected_reason']
        
        print(f"   Input: {test_case['data']}")
        print(f"   Model Phase: {test_case['model_phase']}")
        print(f"   Expected: {test_case['expected_final']} | '{test_case['expected_reason']}'")
        print(f"   Actual:   {final_phase} | '{red_reason}'")
        
        if phase_correct and reason_correct:
            print(f"   ✅ PASSED")
            passed += 1
        else:
            print(f"   ❌ FAILED")
            if not phase_correct:
                print(f"      Phase mismatch: expected {test_case['expected_final']}, got {final_phase}")
            if not reason_correct:
                print(f"      Reason mismatch: expected '{test_case['expected_reason']}', got '{red_reason}'")
            failed += 1
        
        # Calculate and show risk index for debugging
        A = test_case['data']['attendance']
        B = test_case['data']['backlogs']
        C = test_case['data']['cgpa']
        S = test_case['data']['suspension_flag']
        F = test_case['data']['fees_flag']
        risk_index = (100 - A) + (B * 10) + ((10 - C) * 5) + (S * 20) + (F * 30)
        print(f"   Risk Index: {risk_index}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The updated red zone rules are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the function implementation.")
    
    return failed == 0

if __name__ == "__main__":
    test_red_zone_rules()