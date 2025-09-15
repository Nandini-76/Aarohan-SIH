"""
Comprehensive backend testing script to validate all functionality
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_all_students():
    """Test getting all students"""
    print("\n🔍 Testing Get All Students Endpoint...")
    response = requests.get(f"{BASE_URL}/students")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total students: {data.get('total', 0)}")
    print(f"First student: {data.get('students', [{}])[0] if data.get('students') else 'None'}")
    return response.status_code == 200

def test_get_specific_student():
    """Test getting a specific student"""
    print("\n🔍 Testing Get Specific Student Endpoint...")
    enrollment_no = "2023ENG001"
    response = requests.get(f"{BASE_URL}/students/{enrollment_no}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Student data: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_simulate_green_case():
    """Test simulation with green case (low risk)"""
    print("\n🔍 Testing Simulate Endpoint - Green Case...")
    payload = {
        "attendance_percent": 85.0,
        "cgpa": 8.5,
        "backlogs": 1,
        "marks_10": 85,
        "marks_12": 87,
        "fees_flag": "Y",
        "suspension_flag": 0,
        "gender": "M"
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Prediction: {json.dumps(data, indent=2)}")
    return response.status_code == 200 and data.get("predicted_phase") == "Green"

def test_simulate_red_case_attendance():
    """Test simulation with red case - low attendance"""
    print("\n🔍 Testing Simulate Endpoint - Red Case (Low Attendance)...")
    payload = {
        "attendance_percent": 25.0,  # Should trigger red zone
        "cgpa": 7.0,
        "backlogs": 2,
        "marks_10": 75,
        "marks_12": 80,
        "fees_flag": "Y",
        "suspension_flag": 0,
        "gender": "F"
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Prediction: {json.dumps(data, indent=2)}")
    expected_red = data.get("predicted_phase") == "Red" and "Attendance < 35%" in data.get("red_reason", "")
    return response.status_code == 200 and expected_red

def test_simulate_red_case_backlogs():
    """Test simulation with red case - too many backlogs"""
    print("\n🔍 Testing Simulate Endpoint - Red Case (Excessive Backlogs)...")
    payload = {
        "attendance_percent": 75.0,
        "cgpa": 6.0,
        "backlogs": 8,  # Should trigger red zone
        "marks_10": 70,
        "marks_12": 75,
        "fees_flag": "Y",
        "suspension_flag": 0,
        "gender": "M"
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Prediction: {json.dumps(data, indent=2)}")
    expected_red = data.get("predicted_phase") == "Red" and "Backlogs > 7" in data.get("red_reason", "")
    return response.status_code == 200 and expected_red

def test_simulate_red_case_cgpa_backlogs():
    """Test simulation with red case - low CGPA + backlogs"""
    print("\n🔍 Testing Simulate Endpoint - Red Case (Low CGPA + Backlogs)...")
    payload = {
        "attendance_percent": 70.0,
        "cgpa": 4.0,  # Low CGPA
        "backlogs": 6,  # High backlogs
        "marks_10": 65,
        "marks_12": 70,
        "fees_flag": "Y",
        "suspension_flag": 0,
        "gender": "F"
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Prediction: {json.dumps(data, indent=2)}")
    expected_red = data.get("predicted_phase") == "Red" and "CGPA < 4.5 and Backlogs > 5" in data.get("red_reason", "")
    return response.status_code == 200 and expected_red

def test_simulate_red_case_suspension():
    """Test simulation with red case - multiple suspensions + poor attendance"""
    print("\n🔍 Testing Simulate Endpoint - Red Case (Suspensions + Poor Attendance)...")
    payload = {
        "attendance_percent": 50.0,  # Poor attendance
        "cgpa": 6.0,
        "backlogs": 3,
        "marks_10": 70,
        "marks_12": 75,
        "fees_flag": "Y",
        "suspension_flag": 2,  # Multiple suspensions
        "gender": "M"
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Prediction: {json.dumps(data, indent=2)}")
    expected_red = data.get("predicted_phase") == "Red" and "Multiple suspensions and Attendance < 60%" in data.get("red_reason", "")
    return response.status_code == 200 and expected_red

def test_error_handling():
    """Test error handling with invalid data"""
    print("\n🔍 Testing Error Handling...")
    
    # Test missing required fields
    payload = {
        "cgpa": 7.0,
        # Missing attendance_percent and backlogs
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Missing fields status: {response.status_code}")
    
    # Test invalid ranges
    payload = {
        "attendance_percent": 150.0,  # Invalid range
        "cgpa": 15.0,  # Invalid range
        "backlogs": -1,  # Invalid range
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload)
    print(f"Invalid ranges status: {response.status_code}")
    
    # Test non-existent student
    response = requests.get(f"{BASE_URL}/students/INVALID_ID")
    print(f"Non-existent student status: {response.status_code}")
    
    return True

def test_cors_headers():
    """Test CORS headers for frontend integration"""
    print("\n🔍 Testing CORS Headers...")
    # Test with a simple GET request to check CORS headers
    response = requests.get(f"{BASE_URL}/", headers={"Origin": "http://localhost:3000"})
    headers = response.headers
    print(f"Status: {response.status_code}")
    print(f"CORS allow-origin header: {headers.get('access-control-allow-origin', 'Not found')}")
    print(f"CORS allow-methods header: {headers.get('access-control-allow-methods', 'Not found')}")
    cors_enabled = bool(headers.get('access-control-allow-origin'))
    print(f"CORS headers present: {cors_enabled}")
    return cors_enabled

def run_all_tests():
    """Run all tests and generate a comprehensive report"""
    print("🚀 Starting Comprehensive Backend Testing...")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Get All Students", test_get_all_students),
        ("Get Specific Student", test_get_specific_student),
        ("Simulate Green Case", test_simulate_green_case),
        ("Simulate Red - Attendance", test_simulate_red_case_attendance),
        ("Simulate Red - Backlogs", test_simulate_red_case_backlogs),
        ("Simulate Red - CGPA+Backlogs", test_simulate_red_case_cgpa_backlogs),
        ("Simulate Red - Suspensions", test_simulate_red_case_suspension),
        ("Error Handling", test_error_handling),
        ("CORS Headers", test_cors_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "✅ PASS" if result else "❌ FAIL"))
        except Exception as e:
            results.append((test_name, f"❌ ERROR: {str(e)}"))
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        print(f"{test_name:.<30} {result}")
    
    passed = sum(1 for _, result in results if "✅ PASS" in result)
    total = len(results)
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready for frontend integration.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")

if __name__ == "__main__":
    run_all_tests()
