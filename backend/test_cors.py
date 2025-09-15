#!/usr/bin/env python3
"""
Simple test script to verify CORS configuration and API accessibility
"""

import requests
import json

# Test the deployed API
API_BASE_URL = "https://arohann.onrender.com"

def test_cors_and_endpoints():
    """Test CORS configuration and basic endpoints"""
    
    print("🔍 Testing CORS Configuration and API Endpoints")
    print(f"API Base URL: {API_BASE_URL}")
    print("-" * 50)
    
    # Test 1: Health check endpoint
    try:
        print("1. Testing health check endpoint...")
        response = requests.get(f"{API_BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        print(f"   CORS Headers: {cors_headers}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: OPTIONS preflight request
    try:
        print("2. Testing OPTIONS preflight request...")
        headers = {
            'Origin': 'https://arohann.vercel.app',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{API_BASE_URL}/students", headers=headers)
        print(f"   Status: {response.status_code}")
        
        # Check preflight response headers
        preflight_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        print(f"   Preflight Headers: {preflight_headers}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Students endpoint
    try:
        print("3. Testing students endpoint...")
        response = requests.get(f"{API_BASE_URL}/students")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Students count: {len(data.get('students', []))}")
        else:
            print(f"   Error response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 4: Simulate cross-origin request
    try:
        print("4. Testing simulated cross-origin request...")
        headers = {
            'Origin': 'https://arohann.vercel.app',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{API_BASE_URL}/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        # Check if origin is allowed
        allowed_origin = response.headers.get('Access-Control-Allow-Origin')
        print(f"   Allowed Origin: {allowed_origin}")
        
        if allowed_origin in ['*', 'https://arohann.vercel.app']:
            print("   ✅ CORS appears to be working correctly!")
        else:
            print("   ⚠️  CORS may not be configured properly for Vercel domain")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()
    
    # Test 5: CORS test endpoint
    try:
        print("5. Testing CORS debug endpoint...")
        headers = {
            'Origin': 'https://arohann.vercel.app',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{API_BASE_URL}/cors-test", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        print(f"   CORS Headers: {cors_headers}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_cors_and_endpoints()