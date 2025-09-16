#!/usr/bin/env python3
"""
Test a real student from the dataset to see if CSV data has old override reasons
"""
import requests
import json

def test_real_students():
    """Test real students that might have the fee default issue"""
    
    # Test students that previously showed "Fee default & poor attendance"
    test_students = ["2023ENG020", "2023ENG025", "2023ENG030", "2023ENG035"]
    
    for student_id in test_students:
        print(f"=== Testing Student {student_id} ===")
        
        try:
            # Test the API endpoint
            response = requests.get(f"http://127.0.0.1:8000/students/{student_id}")
            
            if response.status_code == 200:
                result = response.json()
                
                fees_flag = result.get('fees_flag', 'N/A')
                override_reason = result.get('override_reason', '')
                final_phase = result.get('final_phase', '')
                
                print(f"  Fees Flag: {fees_flag}")
                print(f"  Final Phase: {final_phase}")
                print(f"  Override Reason: '{override_reason}'")
                
                # Check for contradiction
                if fees_flag == 0 and ('fee' in override_reason.lower() or 'default' in override_reason.lower()):
                    print(f"  ❌ CONTRADICTION: fees_flag=0 but override mentions fees")
                    print(f"     This is from old CSV data, not the API logic")
                elif fees_flag == 1 and ('fee' in override_reason.lower() or 'default' in override_reason.lower()):
                    print(f"  ✅ CORRECT: fees_flag=1 and override mentions fees")
                else:
                    print(f"  ✅ CONSISTENT: No fee contradiction")
                    
                print()
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                print()
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()

if __name__ == '__main__':
    test_real_students()