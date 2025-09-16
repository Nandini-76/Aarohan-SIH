#!/usr/bin/env python3
"""
Data analysis script to verify backend-frontend consistency fixes
"""

import pandas as pd
import sys
import os

def analyze_data():
    try:
        df = pd.read_csv('app/data/merged_with_predictions.csv')
        print('=== FINAL PHASE DISTRIBUTION ===')
        print(df['final_phase'].value_counts())
        
        print('\n=== FEES FLAG DISTRIBUTION ===')
        print(df['fees_flag'].value_counts())
        print('Legend: 0 = Fees Paid, 1 = Fees Outstanding')
        
        print('\n=== SUSPENSION FLAG DISTRIBUTION ===')
        print(df['suspension_flag'].value_counts()) 
        print('Legend: 0 = No Suspension, 1+ = Suspended')
        
        print('\n=== OVERRIDE REASON ANALYSIS ===')
        print(df['override_reason'].value_counts())
        
        print('\n=== SAMPLE OF EACH OVERRIDE TYPE ===')
        for reason in df['override_reason'].unique()[:5]:
            sample = df[df['override_reason'] == reason].iloc[0]
            print(f'REASON: {reason}')
            print(f'  Student: {sample["enrollment_no"]} | Attendance: {sample["attendance"]:.1f}% | CGPA: {sample["cgpa"]:.1f} | Backlogs: {sample["backlogs"]} | Final: {sample["final_phase"]}')
            print(f'  Fees Flag: {sample["fees_flag"]} | Suspension Flag: {sample["suspension_flag"]}')
            print()
            
        print('\n=== CONSISTENCY CHECK ===')
        # Check for potential frontend display issues
        fees_paid_count = len(df[df['fees_flag'] == 0])
        fees_outstanding_count = len(df[df['fees_flag'] == 1])
        no_suspension_count = len(df[df['suspension_flag'] == 0])
        has_suspension_count = len(df[df['suspension_flag'] > 0])
        
        print(f'Students with fees paid (fees_flag=0): {fees_paid_count}')
        print(f'Students with fees outstanding (fees_flag=1): {fees_outstanding_count}')
        print(f'Students with no suspension (suspension_flag=0): {no_suspension_count}')
        print(f'Students with suspension history (suspension_flag>0): {has_suspension_count}')
        
        print('\n=== FRONTEND DISPLAY MAPPING ===')
        print('fees_flag = 0 → Frontend shows: "✅ No Outstanding Fees"')
        print('fees_flag = 1 → Frontend shows: "⚠️ Outstanding Fees"')
        print('suspension_flag = 0 → Frontend shows: "✅ No Suspension History"')
        print('suspension_flag > 0 → Frontend shows: "⚠️ Suspension Record"')
        
    except FileNotFoundError:
        print("Error: Could not find app/data/merged_with_predictions.csv")
        print("Make sure you're running from the backend directory")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_data()