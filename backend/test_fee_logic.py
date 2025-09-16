#!/usr/bin/env python3
"""
Test students with fees_flag = 1 to ensure fee default logic works correctly
"""
import requests
import json

def test_student(enrollment_no):
    """Test a specific student's API response"""
    try:
        response = requests.get(f'http://127.0.0.1:8000/students/{enrollment_no}')
        if response.status_code == 200:
            data = response.json()
            print(f'API Response for student {enrollment_no}:')
            print('Key fields:')
            print('fees_flag:', data.get('fees_flag'))
            print('final_phase:', data.get('final_phase'))
            print('override_reason:', data.get('override_reason', 'No reason'))
            print()
            
            # Check if the logic is correct
            fees_flag = data.get('fees_flag', 0)
            override_reason = data.get('override_reason', '')
            
            print('Analysis:')
            if fees_flag == 1:
                print('⚠️  fees_flag=1 means outstanding fees')
                if 'fee' in override_reason.lower() or 'default' in override_reason.lower():
                    print('✅ override_reason correctly mentions fee default')
                else:
                    print('❓ override_reason does not mention fee (might be overridden by other factors)')
            else:
                print('✅ fees_flag=0 means NO outstanding fees')
                if 'fee' in override_reason.lower() or 'default' in override_reason.lower():
                    print('❌ CONTRADICTION: override_reason mentions fee/default but fees are paid!')
                else:
                    print('✅ No fee-related override reason - this is correct')
            
        else:
            print(f'API Error: {response.status_code} {response.text}')
    except Exception as e:
        print(f'Connection error: {e}')

if __name__ == '__main__':
    # Test students with fees_flag = 1
    test_students = ['2023ENG005', '2023ENG006', '2023ENG014']
    
    for student in test_students:
        test_student(student)
        print('=' * 50)