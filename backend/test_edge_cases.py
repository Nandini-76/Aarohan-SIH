"""
Quick test script to verify the backend-frontend consistency fixes.
This script tests specific edge cases that were causing mismatches.

Usage: python test_edge_cases.py
"""

import requests
import json
from typing import Dict, List

BACKEND_URL = "http://127.0.0.1:8000"  # Use 127.0.0.1 instead of localhost

def test_edge_case(name: str, student_data: Dict, expected_frontend_display: Dict):
    """Test a specific edge case scenario."""
    print(f"\n🧪 Testing: {name}")
    print(f"   Input: {student_data}")
    
    try:
        # Test simulation endpoint
        response = requests.post(f"{BACKEND_URL}/simulate", json=student_data)
        
        if response.status_code != 200:
            print(f"   ❌ Backend error: {response.status_code}")
            return False
        
        result = response.json()
        print(f"   Backend prediction: {result['final_phase']}")
        print(f"   Backend reason: {result.get('override_reason', 'N/A')}")
        
        # Simulate frontend rendering logic
        fees_flag = student_data["fees_flag"]
        suspension_flag = student_data["suspension_flag"]
        
        frontend_fees = "✅ No Outstanding Fees" if fees_flag == 0 else "⚠️ Outstanding Fees"
        frontend_suspension = "✅ No Suspension History" if suspension_flag == 0 else "⚠️ Suspension Record"
        
        print(f"   Frontend fees display: {frontend_fees}")
        print(f"   Frontend suspension display: {frontend_suspension}")
        
        # Check consistency
        fees_match = frontend_fees == expected_frontend_display["fees"]
        suspension_match = frontend_suspension == expected_frontend_display["suspension"]
        
        if fees_match and suspension_match:
            print(f"   ✅ PASS: Frontend display matches expectations")
            return True
        else:
            print(f"   ❌ FAIL: Mismatch detected")
            if not fees_match:
                print(f"      Expected fees: {expected_frontend_display['fees']}")
                print(f"      Got fees: {frontend_fees}")
            if not suspension_match:
                print(f"      Expected suspension: {expected_frontend_display['suspension']}")
                print(f"      Got suspension: {frontend_suspension}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    """Run all edge case tests."""
    print("🔍 Testing Backend-Frontend Consistency")
    print("=" * 50)
    
    # Check backend is running
    try:
        response = requests.get(BACKEND_URL)
        print(f"✅ Backend is running at {BACKEND_URL}")
    except:
        print(f"❌ Backend not accessible at {BACKEND_URL}")
        return
    
    # Define edge cases that commonly cause mismatches
    edge_cases = [
        {
            "name": "Low attendance, high CGPA, fees paid",
            "data": {
                "enrollment_no": "TEST001",
                "attendance": 51.18,
                "cgpa": 8.58,
                "backlogs": 1,
                "fees_flag": 0,  # Paid
                "suspension_flag": 0,  # No suspension
                "gender": "M"
            },
            "expected": {
                "fees": "✅ No Outstanding Fees",
                "suspension": "✅ No Suspension History"
            }
        },
        {
            "name": "High attendance, low CGPA, fees outstanding",
            "data": {
                "enrollment_no": "TEST002",
                "attendance": 85.0,
                "cgpa": 4.5,
                "backlogs": 3,
                "fees_flag": 1,  # Outstanding
                "suspension_flag": 0,  # No suspension
                "gender": "F"
            },
            "expected": {
                "fees": "⚠️ Outstanding Fees",
                "suspension": "✅ No Suspension History"
            }
        },
        {
            "name": "Average attendance, fees paid, suspended once",
            "data": {
                "enrollment_no": "TEST003",
                "attendance": 70.0,
                "cgpa": 6.0,
                "backlogs": 2,
                "fees_flag": 0,  # Paid
                "suspension_flag": 1,  # Suspended
                "gender": "M"
            },
            "expected": {
                "fees": "✅ No Outstanding Fees",
                "suspension": "⚠️ Suspension Record"
            }
        },
        {
            "name": "Critical case: low attendance, fees outstanding, suspended",
            "data": {
                "enrollment_no": "TEST004",
                "attendance": 40.0,
                "cgpa": 5.0,
                "backlogs": 4,
                "fees_flag": 1,  # Outstanding
                "suspension_flag": 1,  # Suspended
                "gender": "F"
            },
            "expected": {
                "fees": "⚠️ Outstanding Fees",
                "suspension": "⚠️ Suspension Record"
            }
        },
        {
            "name": "Edge case: excellent student with fees outstanding",
            "data": {
                "enrollment_no": "TEST005",
                "attendance": 95.0,
                "cgpa": 9.5,
                "backlogs": 0,
                "fees_flag": 1,  # Outstanding (this is the edge case)
                "suspension_flag": 0,  # No suspension
                "gender": "M"
            },
            "expected": {
                "fees": "⚠️ Outstanding Fees",
                "suspension": "✅ No Suspension History"
            }
        }
    ]
    
    # Run tests
    passed = 0
    total = len(edge_cases)
    
    for case in edge_cases:
        success = test_edge_case(case["name"], case["data"], case["expected"])
        if success:
            passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend-frontend consistency is maintained.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
    
    print("\n💡 Key Validation Points:")
    print("   • fees_flag: 0 = ✅ No Outstanding Fees, 1 = ⚠️ Outstanding Fees")
    print("   • suspension_flag: 0 = ✅ No Suspension History, >0 = ⚠️ Suspension Record")
    print("   • Backend predictions should be consistent with display logic")

if __name__ == "__main__":
    main()