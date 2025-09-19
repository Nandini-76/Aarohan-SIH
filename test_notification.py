import requests
import json

# Test the simulation endpoint with Orange risk scenario
test_data = {
    "enrollment_no": "2023TEST001",
    "attendance": 45,  # Low attendance should trigger Orange/Red
    "cgpa": 4.5,       # Low CGPA  
    "backlogs": 3,     # Multiple backlogs
    "marks_10th": 65,
    "marks_12th": 60,
    "fees_flag": 0,
    "suspension_flag": 0,
    "gender": "M"
}

try:
    # Make the request
    response = requests.post("http://localhost:8000/simulate", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API Response:")
        print(f"Final Phase: {result.get('final_phase')}")
        print(f"Notification Message: {result.get('notification_message')}")
        print(f"Full Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to backend server. Please start the server first.")
except Exception as e:
    print(f"❌ Error: {e}")