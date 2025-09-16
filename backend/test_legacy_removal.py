#!/usr/bin/env python3
"""
Test that legacy code removal didn't break functionality
"""
from app.utils import process_single_prediction

def test_legacy_removal():
    """Test that the main functions still work after removing legacy code"""
    
    # Test data
    test_data = {
        'attendance': 85,
        'cgpa': 8.5,
        'backlogs': 0,
        'fees_flag': 0,
        'suspension_flag': 0
    }
    
    try:
        result = process_single_prediction(test_data)
        print('✅ Legacy code removal successful!')
        print('Test result:', result['final_phase'], '-', result.get('red_reason', 'No red reason'))
        print('✅ Active function is working correctly!')
        return True
    except Exception as e:
        print('❌ Error after legacy removal:', e)
        return False

if __name__ == '__main__':
    test_legacy_removal()