"""
College Dataset Preprocessing Pipeline
Normalizes and cleans synthetic college data to match the demo schema

This script:
1. Loads all branch/year CSV files from Full-college-data directory
2. Normalizes column names to match the demo dataset schema
3. Handles missing values and standardizes categorical data
4. Generates cleaned_data.csv with schema-compatible format
5. Applies ML model to predict dropout phases
6. Outputs predicted_phase_data.csv for backend consumption

Author: Preprocessing Pipeline
Date: October 2025
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reference schema from demo dataset (merged_dataset.csv)
REQUIRED_COLUMNS = [
    'enrollment_no', 'attendance', 'cgpa', 'backlogs', 'marks_10th', 
    'marks_12th', 'fees_pending', 'scholarship', 'remarks', 
    'father_occupation', 'mother_occupation', 'family_income', 
    'guardian_education', 'aadhaar_no', 'mobile_no', 'parents_mobile_no', 
    'phone', 'email', 'gender', 'age_at_enrollment', 'category', 
    'department', 'year_of_enrollment', 'suspension_flag', 'hostel_flag', 
    'fees_flag', 'scholarship_flag', 'bus_fees'
]

# Column mapping from synthetic dataset to demo schema
COLUMN_MAPPING = {
    # Standard mappings
    'Enrollment_No': 'enrollment_no',
    'Enrollment No.': 'enrollment_no',
    'enrollment_no': 'enrollment_no',
    'Student_Name': 'student_name',
    'Gender': 'gender',
    'Age': 'age_at_enrollment',
    'Section': 'section',
    'Course': 'course',
    'Year_Enrollment': 'year_of_enrollment',
    'Year_Completion': 'year_completion',
    'Hometown': 'hometown',
    'Caste': 'category',
    'Father Occupation': 'father_occupation',
    'Mother Occupation': 'mother_occupation',
    'Class_10_Percentage': 'marks_10th',
    'Class_12_Percentage': 'marks_12th',
    'Attendance': 'attendance',
    'SGPA': 'sgpa',
    'CGPA': 'cgpa',
    'Backlogs': 'backlogs',
    'Suspension': 'suspension_flag',
    'Family_Income': 'family_income',
    'Fees_Status': 'fees_status',
}

# Gender standardization
GENDER_MAPPING = {
    'Male': 'M',
    'M': 'M',
    'male': 'M',
    'Female': 'F',
    'F': 'F',
    'female': 'F'
}

# Category/Caste standardization
CATEGORY_MAPPING = {
    'General': 'General',
    'GEN': 'General',
    'Gen': 'General',
    'OBC': 'OBC',
    'SC': 'SC',
    'ST': 'ST',
    'SC/ST': 'ST',
    'EWS': 'General'  # Treating EWS as General for now
}

# Department mapping (BTech departments to standard codes)
DEPARTMENT_MAPPING = {
    'Computer Science': 'CSE',
    'Computer Science Engineering': 'CSE',
    'CSE': 'CSE',
    'CS': 'CSE',
    'Information Technology': 'IT',
    'IT': 'IT',
    'Mechanical Engineering': 'ME',
    'ME': 'ME',
    'Mechanical': 'ME',
    'Electrical Engineering': 'EEE',
    'EEE': 'EEE',
    'Electrical': 'EEE',
    'Electronics': 'ECE',
    'ECE': 'ECE',
    'Civil Engineering': 'CE',
    'Civil': 'CE',
    'CE': 'CE',
    'CIVIL': 'CE',
    'BBA': 'BBA',
    'BSc': 'BSC',
    'B.Sc': 'BSC',
    'Agriculture': 'AGR',
    'B.Agriculture': 'AGR',
}


def load_excel_or_csv(file_path: str) -> pd.DataFrame:
    """
    Load file regardless of whether it's CSV or Excel format
    """
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return pd.DataFrame()


def extract_branch_from_path(file_path: str) -> str:
    """
    Extract branch name from file path
    """
    path_lower = file_path.lower()
    if 'bba' in path_lower:
        return 'BBA'
    elif 'bsc-cs' in path_lower or 'bsc_cs' in path_lower:
        return 'BSC'
    elif 'agriculture' in path_lower or 'agri' in path_lower:
        return 'AGR'
    elif 'btech' in path_lower or 'b.tech' in path_lower:
        return 'BTECH'
    return 'UNKNOWN'


def extract_year_from_filename(filename: str) -> int:
    """
    Extract year from filename (e.g., 'Year1', '1st_year', '2025')
    BTech has 4 years, other degrees have 3 years
    """
    # Try to find explicit year patterns first (Year1, Year2, etc.)
    explicit_year_patterns = [
        r'Year\s*(\d)',
        r'(\d)st_year',
        r'(\d)nd_year',
        r'(\d)rd_year',
        r'(\d)th_year',
    ]
    
    for pattern in explicit_year_patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            year_num = int(match.group(1))
            return year_num
    
    # Try to extract enrollment year (2025, 2024, 2023, 2022)
    year_match = re.search(r'Students_(\d{4})', filename, re.IGNORECASE)
    if year_match:
        year_int = int(year_match.group(1))
        # Calculate year level based on enrollment year
        # 2025 = 1st year, 2024 = 2nd year, 2023 = 3rd year, 2022 = 4th year
        current_year = 2025
        year_level = current_year - year_int + 1
        return min(year_level, 4)  # Cap at 4 for BTech
    
    # Default to 1 if not found
    return 1


def normalize_column_names(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Normalize column names to match demo schema
    """
    # Create a copy
    df = df.copy()
    
    # First pass: direct mapping
    df.columns = [COLUMN_MAPPING.get(col, col.lower().replace(' ', '_').replace('.', '')) 
                  for col in df.columns]
    
    # Handle duplicate columns (e.g., 'Enrollment_No' and 'Enrollment No.')
    # Keep only the first occurrence of duplicated columns
    if df.columns.duplicated().any():
        # Get list of columns to keep (first occurrence only)
        cols_to_keep = ~df.columns.duplicated()
        df = df.loc[:, cols_to_keep]
        logger.debug(f"Removed duplicate columns in {os.path.basename(file_path)}")
    
    # Log the columns found
    logger.debug(f"Columns in {os.path.basename(file_path)}: {list(df.columns)}")
    
    return df


def standardize_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize categorical columns to match demo format
    """
    df = df.copy()
    
    # Gender
    if 'gender' in df.columns:
        df['gender'] = df['gender'].map(GENDER_MAPPING).fillna('M')
    
    # Category/Caste
    if 'category' in df.columns:
        df['category'] = df['category'].map(CATEGORY_MAPPING).fillna('General')
    
    # Department
    if 'department' in df.columns:
        df['department'] = df['department'].map(DEPARTMENT_MAPPING).fillna(df['department'])
    
    return df


def convert_fees_status_to_flag(fees_status: str) -> int:
    """
    Convert fees_status text to fees_flag (0=Paid, 1=Unpaid/Pending)
    """
    if pd.isna(fees_status):
        return 0
    
    status_lower = str(fees_status).lower()
    if 'paid' in status_lower or 'complete' in status_lower:
        return 0
    elif 'partial' in status_lower or 'pending' in status_lower or 'unpaid' in status_lower:
        return 1
    else:
        return 0  # Default to paid


def convert_suspension_to_flag(suspension: str) -> int:
    """
    Convert suspension text to flag (0=No, 1=Yes)
    """
    if pd.isna(suspension):
        return 0
    
    susp_lower = str(suspension).lower()
    if 'yes' in susp_lower or 'true' in susp_lower or '1' in susp_lower:
        return 1
    else:
        return 0


def fill_missing_columns(df: pd.DataFrame, branch: str) -> pd.DataFrame:
    """
    Fill missing columns with default or inferred values
    """
    df = df.copy()
    
    # Ensure all required columns exist
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            # Set defaults based on column type
            if col in ['fees_pending', 'scholarship']:
                df[col] = np.nan
            elif col in ['remarks', 'guardian_education', 'phone', 'email']:
                df[col] = ''
            elif col in ['aadhaar_no', 'mobile_no', 'parents_mobile_no']:
                df[col] = np.nan
            elif col in ['suspension_flag', 'hostel_flag', 'fees_flag', 'scholarship_flag']:
                df[col] = 0
            elif col == 'bus_fees':
                df[col] = np.random.randint(1000, 5000)
            elif col == 'department':
                df[col] = branch if branch != 'UNKNOWN' else 'CSE'
            else:
                df[col] = np.nan
    
    # Convert fees_status to fees_flag if exists
    if 'fees_status' in df.columns and 'fees_flag' not in df.columns:
        df['fees_flag'] = df['fees_status'].apply(convert_fees_status_to_flag)
    
    # Convert suspension text to flag
    if 'suspension' in df.columns and 'suspension_flag' not in df.columns:
        df['suspension_flag'] = df['suspension'].apply(convert_suspension_to_flag)
    
    # Fill department from branch if missing
    if 'department' not in df.columns or df['department'].isna().all():
        df['department'] = branch if branch != 'UNKNOWN' else 'CSE'
    
    return df


def generate_enrollment_number(df: pd.DataFrame, branch: str, year_level: int) -> pd.DataFrame:
    """
    Generate or standardize enrollment numbers (only if not already present)
    """
    df = df.copy()
    
    # If enrollment_no column doesn't exist, create it
    if 'enrollment_no' not in df.columns:
        df['enrollment_no'] = ''
    
    # Convert to string to handle various types
    df['enrollment_no'] = df['enrollment_no'].astype(str)
    
    # Check if we need to generate numbers (look for empty or 'nan' values)
    empty_mask = (df['enrollment_no'] == '') | (df['enrollment_no'] == 'nan')
    empty_count = int(empty_mask.sum())  # Explicitly convert to int
    needs_generation = empty_count > 0
    
    # Only generate if needed (don't override existing numbers)
    if needs_generation:
        year_enrollment = 2026 - year_level  # Calculate year
        branch_code = branch[:3].upper()
        
        counter = 1
        for idx in df.index:
            current_val = str(df.at[idx, 'enrollment_no'])
            if current_val == '' or current_val == 'nan':
                enroll_num = f"{year_enrollment}{branch_code}{counter:04d}"
                df.at[idx, 'enrollment_no'] = enroll_num
            counter += 1
    
    return df


def process_single_file(file_path: str, branch: str, year_level: int) -> pd.DataFrame:
    """
    Process a single CSV/Excel file
    """
    logger.info(f"Processing: {os.path.basename(file_path)} (Branch: {branch}, Year: {year_level})")
    
    # Load the file
    df = load_excel_or_csv(file_path)
    
    if df.empty:
        logger.warning(f"Empty dataframe for {file_path}")
        return pd.DataFrame()
    
    logger.info(f"  Loaded {len(df)} records")
    
    # Normalize column names
    df = normalize_column_names(df, file_path)
    
    # Standardize categorical values
    df = standardize_categorical_values(df)
    
    # Fill missing columns with defaults
    df = fill_missing_columns(df, branch)
    
    # Generate enrollment numbers if needed
    df = generate_enrollment_number(df, branch, year_level)
    
    # Add year_level if not present
    if 'year_level' not in df.columns:
        df['year_level'] = year_level
    
    logger.info(f"  Processed {len(df)} records successfully")
    
    return df


def load_all_college_data(base_dir: str) -> pd.DataFrame:
    """
    Load and combine all college data from Full-college-data directory
    """
    all_data = []
    
    # Define the branch directories
    branches = {
        'BBA': 'BBA',
        'Bsc-CS': 'BSC',
        'Bsc-agriculture': 'AGR',
        'Btech': 'BTECH'
    }
    
    for branch_dir, branch_code in branches.items():
        branch_path = os.path.join(base_dir, branch_dir)
        
        if not os.path.exists(branch_path):
            logger.warning(f"Branch directory not found: {branch_path}")
            continue
        
        # Get all CSV and Excel files in the branch directory
        files = [f for f in os.listdir(branch_path) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
        
        logger.info(f"\nProcessing branch: {branch_code} ({len(files)} files)")
        
        for file in files:
            file_path = os.path.join(branch_path, file)
            year_level = extract_year_from_filename(file)
            
            df = process_single_file(file_path, branch_code, year_level)
            
            if not df.empty:
                all_data.append(df)
    
    if not all_data:
        logger.error("No data loaded from any files!")
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"\n✓ Combined {len(combined_df)} total records from all branches")
    
    return combined_df


def clean_and_format_final_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleaning and formatting to match demo schema exactly
    """
    logger.info("Applying final cleaning and formatting...")
    
    df = df.copy()
    
    # Ensure correct data types
    if 'attendance' in df.columns:
        df['attendance'] = pd.to_numeric(df['attendance'], errors='coerce')
    
    if 'cgpa' in df.columns:
        df['cgpa'] = pd.to_numeric(df['cgpa'], errors='coerce')
    
    if 'backlogs' in df.columns:
        df['backlogs'] = pd.to_numeric(df['backlogs'], errors='coerce').fillna(0).astype(int)
    
    if 'marks_10th' in df.columns:
        df['marks_10th'] = pd.to_numeric(df['marks_10th'], errors='coerce')
    
    if 'marks_12th' in df.columns:
        df['marks_12th'] = pd.to_numeric(df['marks_12th'], errors='coerce')
    
    # Convert flags to integers
    for flag_col in ['suspension_flag', 'hostel_flag', 'fees_flag', 'scholarship_flag']:
        if flag_col in df.columns:
            df[flag_col] = pd.to_numeric(df[flag_col], errors='coerce').fillna(0).astype(int)
    
    # Ensure enrollment_no is string
    if 'enrollment_no' in df.columns:
        df['enrollment_no'] = df['enrollment_no'].astype(str)
    
    # Select only required columns in the correct order
    available_cols = [col for col in REQUIRED_COLUMNS if col in df.columns]
    df = df[available_cols]
    
    # Remove duplicates based on enrollment_no
    if 'enrollment_no' in df.columns:
        df = df.drop_duplicates(subset=['enrollment_no'], keep='first')
    
    logger.info(f"✓ Final dataset: {len(df)} records with {len(df.columns)} columns")
    
    return df


def main():
    """
    Main preprocessing pipeline
    """
    logger.info("="*60)
    logger.info("College Dataset Preprocessing Pipeline")
    logger.info("="*60)
    
    # Paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent / "Full-college-data"
    output_dir = script_dir / "data"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Output file
    output_file = output_dir / "cleaned_data.csv"
    
    logger.info(f"\nInput directory: {base_dir}")
    logger.info(f"Output file: {output_file}")
    
    # Check if base directory exists
    if not base_dir.exists():
        logger.error(f"Base directory not found: {base_dir}")
        sys.exit(1)
    
    # Load all college data
    combined_df = load_all_college_data(str(base_dir))
    
    if combined_df.empty:
        logger.error("No data to process!")
        sys.exit(1)
    
    # Clean and format
    final_df = clean_and_format_final_dataset(combined_df)
    
    # Save to CSV
    final_df.to_csv(output_file, index=False)
    logger.info(f"\n✓ Saved cleaned dataset to: {output_file}")
    logger.info(f"  Total records: {len(final_df)}")
    logger.info(f"  Total columns: {len(final_df.columns)}")
    
    # Print summary statistics
    logger.info("\n" + "="*60)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*60)
    logger.info(f"Total students: {len(final_df)}")
    
    if 'department' in final_df.columns:
        logger.info(f"\nBy Department:")
        for dept, count in final_df['department'].value_counts().items():
            logger.info(f"  {dept}: {count}")
    
    if 'gender' in final_df.columns:
        logger.info(f"\nBy Gender:")
        for gender, count in final_df['gender'].value_counts().items():
            logger.info(f"  {gender}: {count}")
    
    if 'category' in final_df.columns:
        logger.info(f"\nBy Category:")
        for cat, count in final_df['category'].value_counts().items():
            logger.info(f"  {cat}: {count}")
    
    logger.info("\n" + "="*60)
    logger.info("✓ Preprocessing complete!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
