#!/usr/bin/env python3
"""
Test the API to see what data is being returned
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
            print(json.dumps(data, indent=2))
            print()
            print('Key fields:')
            print('fees_flag:', data.get('fees_flag'))
            print('final_phase:', data.get('final_phase'))
            print('red_reason:', data.get('red_reason', 'No red reason'))
            print()
            
            # Check if there's a contradiction
            fees_flag = data.get('fees_flag', 0)
            red_reason = data.get('red_reason', '')
            
            print('Analysis:')
            if fees_flag == 0:
                print('✅ fees_flag=0 means NO outstanding fees')
                if 'fee' in red_reason.lower() or 'default' in red_reason.lower():
                    print('❌ CONTRADICTION: red_reason mentions fee/default but fees are paid!')
                else:
                    print('✅ No fee-related red reason - this is correct')
            elif fees_flag == 1:
                print('⚠️  fees_flag=1 means outstanding fees')
                if 'fee' in red_reason.lower() or 'default' in red_reason.lower():
                    print('✅ red_reason correctly mentions fee default')
                else:
                    print('❌ MISSING: red_reason should mention fee default')
            
        else:
            print(f'API Error: {response.status_code} {response.text}')
    except Exception as e:
        print(f'Connection error: {e}')

if __name__ == '__main__':
    # Test a few students
    test_students = ['2023ENG001', '2023ENG002', '2023ENG020']
    
    for student in test_students:
        test_student(student)
        print('=' * 50)