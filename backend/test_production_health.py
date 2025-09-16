#!/usr/bin/env python3
"""
Test the production backend health and prediction endpoints
"""

import requests
import json

# Test data
test_student = {
    'attendance': 65.0,
    'cgpa': 6.8,
    'backlogs': 3,
    'marks_10th': 75.0,
    'marks_12th': 72.0,
    'fees_flag': 0,
    'suspension_flag': 1,
    'gender': 'F'
}

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("https://aarohan-backend.onrender.com/health", timeout=10)
        print(f"🏥 Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_prediction_endpoint():
    """Test the prediction endpoint"""
    try:
        response = requests.post(
            "https://aarohan-backend.onrender.com/predict",
            json=test_student,
            timeout=15
        )
        print(f"\n🔮 Prediction Test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Student Risk: {result.get('final_phase', 'Unknown')}")
            print(f"ML Phase: {result.get('model_phase', 'Unknown')}")
            print(f"Override: {result.get('override_reason', 'None')}")
            if result.get('ml_probability') is not None:
                print(f"ML Confidence: {result.get('ml_probability'):.2%}")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Prediction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Production Backend")
    print("=" * 40)
    
    health_ok = test_health_endpoint()
    prediction_ok = test_prediction_endpoint()
    
    print(f"\n📊 Summary:")
    print(f"Health Endpoint: {'✅' if health_ok else '❌'}")
    print(f"Prediction Endpoint: {'✅' if prediction_ok else '❌'}")
    
    if health_ok and prediction_ok:
        print("🎉 Production backend is fully functional!")
    else:
        print("⚠️ Some issues detected")