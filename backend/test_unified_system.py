#!/usr/bin/env python3
"""
Test the unified prediction system
"""
from app.utils import predict_with_unified_system, run_batch_prediction_pipeline

def test_unified_system():
    """Test that the unified system works for both batch and live predictions"""
    
    print("=== Testing Unified Prediction System ===")
    
    # Test 1: Live prediction using unified system
    print("\n1. Testing Live Prediction:")
    test_data = {
        'attendance': 85,
        'cgpa': 8.5,
        'backlogs': 0,
        'fees_flag': 0,
        'suspension_flag': 0,
        'enrollment_no': 'TEST001'
    }
    
    try:
        result = predict_with_unified_system(test_data)
        print(f"   ✅ Live prediction successful!")
        print(f"   Model phase: {result['model_phase']}")
        print(f"   Final phase: {result['final_phase']}")
        print(f"   Override reason: {result['override_reason']}")
        print(f"   Rule override: {result['rule_override']}")
    except Exception as e:
        print(f"   ❌ Live prediction failed: {e}")
        return False
    
    # Test 2: Fee default scenario
    print("\n2. Testing Fee Default Scenario:")
    fee_default_data = {
        'attendance': 55,  # Low attendance
        'cgpa': 6.0,      # Decent CGPA
        'backlogs': 1,    # Some backlogs
        'fees_flag': 1,   # UNPAID FEES
        'suspension_flag': 0,
        'enrollment_no': 'TEST002'
    }
    
    try:
        result = predict_with_unified_system(fee_default_data)
        print(f"   ✅ Fee default test successful!")
        print(f"   Final phase: {result['final_phase']}")
        print(f"   Override reason: {result['override_reason']}")
        
        # Should show fee-related override
        if 'fee' in result['override_reason'].lower() or 'default' in result['override_reason'].lower():
            print(f"   ✅ Correctly identifies fee default risk")
        else:
            print(f"   ⚠️  Fee default not identified in override reason")
    except Exception as e:
        print(f"   ❌ Fee default test failed: {e}")
        return False
    
    print("\n✅ Unified system tests completed successfully!")
    return True

if __name__ == '__main__':
    test_unified_system()