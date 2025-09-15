#!/usr/bin/env python3
"""
Test script to verify the two-phase prediction system works correctly.
"""

import json
import requests
import time

def test_api_endpoints():
    """Test all API endpoints to verify two-phase system"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Two-Phase Prediction System")
    print("=" * 50)
    
    # Test 1: Good student (should be Green/Green)
    print("\n1. Testing good student (expected: Green/Green)")
    good_student = {
        "enrollment_no": "GOOD001",
        "attendance": 85.0,
        "cgpa": 8.5,
        "marks_10th": 85.0,
        "marks_12th": 80.0,
        "backlogs": 0,
        "fees_flag": 0,
        "suspension_flag": 0
    }
    
    try:
        response = requests.post(f"{base_url}/simulate", json=good_student)
        result = response.json()
        print(f"   Model Phase: {result['model_phase']}")
        print(f"   Final Phase: {result['final_phase']}")
        print(f"   Override: {result['rule_override']}")
        print(f"   Reason: {result['red_reason']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Red-zone student (should trigger override)
    print("\n2. Testing red-zone student (expected: Green->Red override)")
    red_zone_student = {
        "enrollment_no": "RED001",
        "attendance": 25.0,  # Very low attendance
        "cgpa": 2.5,        # Low CGPA
        "marks_10th": 40.0,
        "marks_12th": 35.0,
        "backlogs": 8,      # Many backlogs
        "fees_flag": 1,     # Fees not paid
        "suspension_flag": 1
    }
    
    try:
        response = requests.post(f"{base_url}/simulate", json=red_zone_student)
        result = response.json()
        print(f"   Model Phase: {result['model_phase']}")
        print(f"   Final Phase: {result['final_phase']}")
        print(f"   Override: {result['rule_override']}")
        print(f"   Reason: {result['red_reason']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Medium-risk student
    print("\n3. Testing medium-risk student")
    medium_student = {
        "enrollment_no": "MED001",
        "attendance": 65.0,
        "cgpa": 6.0,
        "marks_10th": 70.0,
        "marks_12th": 65.0,
        "backlogs": 2,
        "fees_flag": 0,
        "suspension_flag": 0
    }
    
    try:
        response = requests.post(f"{base_url}/simulate", json=medium_student)
        result = response.json()
        print(f"   Model Phase: {result['model_phase']}")
        print(f"   Final Phase: {result['final_phase']}")
        print(f"   Override: {result['rule_override']}")
        print(f"   Reason: {result['red_reason']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check predict endpoint format
    print("\n4. Testing predict endpoint format")
    try:
        response = requests.get(f"{base_url}/predict")
        result = response.json()
        print(f"   Status: {result['status']}")
        print(f"   Total Students: {result['total_students']}")
        print(f"   Final Phase Distribution: {result['phase_distribution']}")
        print(f"   Model Phase Distribution: {result['model_phase_distribution']}")
        print(f"   Red-zone Overrides: {result['red_zone_overrides']}")
        
        # Check preview format
        if result['preview']:
            sample = result['preview'][0]
            print(f"   Sample Preview Keys: {list(sample.keys())}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Two-Phase System Test Complete!")

if __name__ == "__main__":
    test_api_endpoints()
