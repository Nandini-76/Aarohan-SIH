"""
Integration Test Script for Stage-2 ML-Enhanced Dropout Prediction System

This script validates the complete pipeline:
1. API health check
2. ML model training (if needed)
3. Simulation with ML refinement
4. Data validation and logging

Author: Pair Programming Session  
Date: September 10, 2025 - Stage 2 Testing
"""

import requests
import json
import sys
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_health_check():
    """Test basic API health and connectivity."""
    print("🔍 Testing API health check...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is running: {data['message']}")
            print(f"   Version: {data['version']}")
            print(f"   Database: {data['database_status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_training_endpoint():
    """Test ML model training endpoint."""
    print("\n🤖 Testing ML model training...")
    
    try:
        response = requests.post(f"{BASE_URL}/train?token=devtoken", timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Training completed: {data['success']}")
            print(f"   Message: {data['message']}")
            
            if data['success'] and data['metrics']:
                metrics = data['metrics']
                print(f"   Test Accuracy: {metrics.get('test_accuracy', 'N/A'):.4f}")
                print(f"   Test F1-Score: {metrics.get('test_f1', 'N/A'):.4f}")
                print(f"   Test ROC-AUC: {metrics.get('test_auc', 'N/A'):.4f}")
                print(f"   Model Path: {data['model_path']}")
            
            return data['success']
        else:
            print(f"❌ Training failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Training request failed: {e}")
        return False

def test_simulation():
    """Test simulation endpoint with ML refinement."""
    print("\n📊 Testing simulation with ML refinement...")
    
    try:
        response = requests.post(f"{BASE_URL}/simulate", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Simulation completed successfully!")
            print(f"   Simulation ID: {data['simulation_id']}")
            print(f"   Model Loaded: {data['model_loaded']}")
            
            # Risk level counts
            counts = data['counts']
            print(f"   Risk Distribution:")
            print(f"     - High Risk:   {counts['High Risk']}")
            print(f"     - Medium Risk: {counts['Medium Risk']}")
            print(f"     - Low Risk:    {counts['Low Risk']}")
            print(f"     - Total:       {counts['Total']}")
            
            # Analyze students with ML probabilities
            students = data['students']
            ml_students = [s for s in students if s.get('ml_proba') is not None]
            
            if ml_students:
                print(f"\n🧠 ML Analysis Results:")
                print(f"   Students with ML probabilities: {len(ml_students)}")
                
                # Sort by ML probability (highest first)
                ml_students.sort(key=lambda x: x['ml_proba'], reverse=True)
                
                print(f"\n   Top 3 Students by Dropout Probability:")
                for i, student in enumerate(ml_students[:3]):
                    print(f"   {i+1}. {student['enrollment_no']}: {student['ml_proba']:.3f} "
                          f"({student['risk_level']}) - Rule Score: {student['risk_score']}")
                    
                # Count ML overrides
                ml_overrides = sum(1 for s in ml_students 
                                 if 'ML Override' in s.get('risk_reasons', '') or 'ML Upgrade' in s.get('risk_reasons', ''))
                print(f"\n   ML Risk Refinements Applied: {ml_overrides}")
                
                # Model performance info
                if data['model_metrics']:
                    metrics = data['model_metrics']
                    print(f"\n   Model Performance:")
                    print(f"     - Test Accuracy: {metrics.get('test_accuracy', 'N/A'):.4f}")
                    print(f"     - Test F1-Score: {metrics.get('test_f1', 'N/A'):.4f}")
            else:
                print("⚠️  No ML probabilities found (model may not be loaded)")
            
            # Log analysis
            if data['log']:
                print(f"\n📝 Risk Assessment Log ({len(data['log'])} entries):")
                for log_entry in data['log'][:3]:  # Show first 3 entries
                    print(f"   - {log_entry}")
                if len(data['log']) > 3:
                    print(f"   ... and {len(data['log']) - 3} more entries")
            
            return True
            
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Simulation request failed: {e}")
        return False

def test_simulations_list():
    """Test retrieval of simulation history."""
    print("\n📚 Testing simulations history...")
    
    try:
        response = requests.get(f"{BASE_URL}/simulations", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            simulations = data['simulations']
            
            print(f"✅ Retrieved {len(simulations)} simulation records")
            
            if simulations:
                latest = simulations[0]  # Should be sorted newest first
                print(f"   Latest simulation: {latest['_id']}")
                print(f"   Total students: {latest['counts']['Total']}")
                print(f"   High risk: {latest['counts']['High Risk']}")
            
            return True
        else:
            print(f"❌ History retrieval failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ History request failed: {e}")
        return False

def main():
    """Run complete integration test suite."""
    print("=" * 60)
    print("🧪 STAGE-2 ML-ENHANCED DROPOUT PREDICTION - INTEGRATION TESTS")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Health Check
    if test_health_check():
        tests_passed += 1
    
    # Test 2: Training (optional - may already be trained)
    print(f"\n🤖 Attempting ML model training (may skip if already trained)...")
    train_result = test_training_endpoint()
    if train_result is not False:  # Accept both True and None (already trained)
        tests_passed += 1
    
    # Small delay to ensure model is loaded
    time.sleep(2)
    
    # Test 3: Simulation with ML
    if test_simulation():
        tests_passed += 1
    
    # Test 4: History retrieval
    if test_simulations_list():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {tests_passed/total_tests*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Stage-2 system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the server logs and configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
