"""
Enhanced preprocessing that preserves ALL original fields for comprehensive student profiles
while also creating ML-ready features
"""
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Column mappings (same as before)
COLUMN_MAPPING = {
    'enrollment_no': 'enrollment_no',
    'enrollment no': 'enrollment_no',
    'enrollment_number': 'enrollment_no',
    'student_name': 'student_name',
    'name': 'student_name',
    'gender': 'gender',
    'sex': 'gender',
    'age': 'age',
    'age_at_enrollment': 'age_at_enrollment',
    'section': 'section',
    'course': 'course',
    'department': 'department',
    'branch': 'department',
    'year': 'year',
    'year_level': 'year_level',
    'year_enrollment': 'year_enrollment',
    'year_of_enrollment': 'year_enrollment',
    'year_completion': 'year_completion',
    'year_of_completion': 'year_completion',
    'hometown': 'hometown',
    'city': 'hometown',
    'caste': 'category',
    'category': 'category',
    'father occupation': 'father_occupation',
    'father_occupation': 'father_occupation',
    'mother occupation': 'mother_occupation',
    'mother_occupation': 'mother_occupation',
    'family_income': 'family_income',
    'income': 'family_income',
    'class_10_percentage': 'marks_10th',
    'marks_10th': 'marks_10th',
    'class10_marks': 'marks_10th',
    'class_12_percentage': 'marks_12th',
    'marks_12th': 'marks_12th',
    'class12_marks': 'marks_12th',
    'attendance': 'attendance',
    'attendance_percentage': 'attendance',
    'sgpa': 'sgpa',
    'sgpa1': 'sgpa1',
    'sgpa2': 'sgpa2',
    'sgpa3': 'sgpa3',
    'sgpa4': 'sgpa4',
    'sgpa5': 'sgpa5',
    'cgpa': 'cgpa',
    'gpa': 'cgpa',
    'backlogs': 'backlogs',
    'arrears': 'backlogs',
    'suspension': 'suspension',
    'suspended': 'suspension',
    'fees_status': 'fees_status',
    'fee_status': 'fees_status',
}

GENDER_MAPPING = {
    'Male': 'M',
    'M': 'M',
    'male': 'M',
    'Female': 'F',
    'F': 'F',
    'female': 'F'
}

CATEGORY_MAPPING = {
    'SC': 'SC',
    'ST': 'ST',
    'OBC': 'OBC',
    'General': 'General',
    'GEN': 'General',
    'EWS': 'EWS',
}

def load_excel_or_csv(file_path: str) -> pd.DataFrame:
    """Load file regardless of format"""
    try:
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        else:
            return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Failed to load {file_path}: {e}")
        return pd.DataFrame()

def normalize_column_names(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """Normalize column names using mapping"""
    df = df.copy()
    
    # Handle duplicate columns
    if df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]
    
    # Normalize column names
    new_columns = {}
    for col in df.columns:
        col_lower = col.lower().strip().replace(' ', '_')
        if col_lower in COLUMN_MAPPING:
            new_columns[col] = COLUMN_MAPPING[col_lower]
        else:
            # Keep original column name if no mapping
            new_columns[col] = col_lower.replace(' ', '_')
    
    df = df.rename(columns=new_columns)
    return df

def extract_year_from_filename(filename: str) -> int:
    """Extract year level from filename"""
    filename_lower = filename.lower()
    if 'year1' in filename_lower or '1st' in filename_lower or 'first' in filename_lower:
        return 1
    elif 'year2' in filename_lower or '2nd' in filename_lower or 'second' in filename_lower:
        return 2
    elif 'year3' in filename_lower or '3rd' in filename_lower or 'third' in filename_lower or 'final' in filename_lower:
        return 3
    elif 'year4' in filename_lower or '4th' in filename_lower or 'fourth' in filename_lower:
        return 4
    return 1

def extract_branch_from_path(file_path: str) -> str:
    """Extract branch code from file path"""
    path_lower = file_path.lower()
    if 'bba' in path_lower:
        return 'BBA'
    elif 'bsc-cs' in path_lower or 'bsc_cs' in path_lower:
        return 'CS'
    elif 'agriculture' in path_lower or 'agri' in path_lower:
        return 'AGRI'
    elif 'btech' in path_lower or 'b.tech' in path_lower:
        return 'BTECH'
    return 'UNKNOWN'

def generate_enrollment_number(df: pd.DataFrame, branch: str, year_level: int) -> pd.DataFrame:
    """Generate enrollment numbers if missing"""
    df = df.copy()
    
    if 'enrollment_no' not in df.columns or df['enrollment_no'].isna().sum() > 0:
        year = 2026 - year_level  # Calculate enrollment year
        
        # Branch prefix mapping
        prefix_map = {
            'BBA': f'BBA{year}B',
            'CS': f'CS{year}C',
            'AGRI': f'AGRI{year}A',
            'BTECH': f'BTECH{year}T'
        }
        
        prefix = prefix_map.get(branch, f'{branch}{year}X')
        
        # Generate enrollment numbers
        empty_mask = df['enrollment_no'].isna() if 'enrollment_no' in df.columns else pd.Series([True] * len(df))
        count = int(empty_mask.sum())
        
        if count > 0:
            new_enrollments = [f"{prefix}{str(i+1).zfill(3)}" for i in range(count)]
            df.loc[empty_mask, 'enrollment_no'] = new_enrollments
    
    return df

def convert_fees_status_to_flag(fees_status: str) -> int:
    """Convert fees_status to flag (0=Paid, 1=Unpaid)"""
    if pd.isna(fees_status):
        return 0
    status_lower = str(fees_status).lower()
    if 'paid' in status_lower or 'complete' in status_lower:
        return 0
    else:
        return 1

def convert_suspension_to_flag(suspension: str) -> int:
    """Convert suspension to flag (0=No, 1=Yes)"""
    if pd.isna(suspension):
        return 0
    susp_lower = str(suspension).lower()
    return 1 if 'yes' in susp_lower or 'true' in susp_lower else 0

def process_single_file(file_path: str, branch: str, year_level: int) -> pd.DataFrame:
    """Process a single file with ALL fields preserved"""
    logger.info(f"  Processing: {os.path.basename(file_path)}")
    
    df = load_excel_or_csv(file_path)
    if df.empty:
        return df
    
    # Normalize column names
    df = normalize_column_names(df, file_path)
    
    # Standardize categorical values
    if 'gender' in df.columns:
        df['gender'] = df['gender'].map(GENDER_MAPPING).fillna('M')
    
    if 'category' in df.columns:
        df['category'] = df['category'].map(CATEGORY_MAPPING).fillna('General')
    
    # Generate enrollment numbers if needed
    df = generate_enrollment_number(df, branch, year_level)
    
    # Add derived fields
    if 'year_level' not in df.columns:
        df['year_level'] = year_level
    
    if 'department' not in df.columns:
        df['department'] = branch
    
    # Create ML-ready flag fields from text fields
    if 'fees_status' in df.columns and 'fees_flag' not in df.columns:
        df['fees_flag'] = df['fees_status'].apply(convert_fees_status_to_flag)
    
    if 'suspension' in df.columns and 'suspension_flag' not in df.columns:
        df['suspension_flag'] = df['suspension'].apply(convert_suspension_to_flag)
    
    # Calculate age_at_enrollment if not present
    if 'age_at_enrollment' not in df.columns and 'age' in df.columns and 'year_level' in df.columns:
        df['age_at_enrollment'] = df['age'] - (df['year_level'] - 1)
    
    logger.info(f"    ✓ Loaded {len(df)} records with {len(df.columns)} fields")
    
    return df

def load_all_college_data(base_dir: str) -> pd.DataFrame:
    """Load all college data preserving ALL original fields"""
    all_data = []
    
    branches = {
        'BBA': 'BBA',
        'Bsc-CS': 'CS',
        'Bsc-agriculture': 'AGRI',
        'Btech': 'BTECH'
    }
    
    for branch_dir, branch_code in branches.items():
        branch_path = os.path.join(base_dir, branch_dir)
        
        if not os.path.exists(branch_path):
            logger.warning(f"Branch directory not found: {branch_path}")
            continue
        
        files = [f for f in os.listdir(branch_path) 
                if f.endswith(('.csv', '.xlsx', '.xls'))]
        
        logger.info(f"\n Processing branch: {branch_code} ({len(files)} files)")
        
        for file in files:
            file_path = os.path.join(branch_path, file)
            year_level = extract_year_from_filename(file)
            
            df = process_single_file(file_path, branch_code, year_level)
            
            if not df.empty:
                all_data.append(df)
    
    if not all_data:
        logger.error("No data loaded!")
        return pd.DataFrame()
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    logger.info(f"\n✓ Combined {len(combined_df)} total records from all branches")
    logger.info(f"✓ Total fields: {len(combined_df.columns)}")
    
    return combined_df

def main():
    """Main preprocessing pipeline"""
    logger.info("="*60)
    logger.info("Enhanced College Dataset Preprocessing")
    logger.info("Preserving ALL original fields + ML-ready features")
    logger.info("="*60)
    
    # Paths
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent / "Full-college-data"
    output_dir = script_dir / "data"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "comprehensive_data.csv"
    
    logger.info(f"\nInput directory: {base_dir}")
    logger.info(f"Output file: {output_file}")
    
    if not base_dir.exists():
        logger.error(f"Base directory not found: {base_dir}")
        sys.exit(1)
    
    # Load all data
    combined_df = load_all_college_data(str(base_dir))
    
    if combined_df.empty:
        logger.error("No data to process!")
        sys.exit(1)
    
    # Ensure proper data types
    if 'attendance' in combined_df.columns:
        combined_df['attendance'] = pd.to_numeric(combined_df['attendance'], errors='coerce')
    if 'cgpa' in combined_df.columns:
        combined_df['cgpa'] = pd.to_numeric(combined_df['cgpa'], errors='coerce')
    if 'backlogs' in combined_df.columns:
        combined_df['backlogs'] = pd.to_numeric(combined_df['backlogs'], errors='coerce').fillna(0).astype(int)
    if 'marks_10th' in combined_df.columns:
        combined_df['marks_10th'] = pd.to_numeric(combined_df['marks_10th'], errors='coerce')
    if 'marks_12th' in combined_df.columns:
        combined_df['marks_12th'] = pd.to_numeric(combined_df['marks_12th'], errors='coerce')
    
    # Remove duplicates based on enrollment_no
    if 'enrollment_no' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['enrollment_no'], keep='first')
    
    # Save comprehensive data
    combined_df.to_csv(output_file, index=False)
    logger.info(f"\n✓ Saved comprehensive dataset to: {output_file}")
    logger.info(f"  Total records: {len(combined_df)}")
    logger.info(f"  Total fields: {len(combined_df.columns)}")
    
    # Print column list
    logger.info(f"\nAll fields preserved:")
    for col in sorted(combined_df.columns):
        logger.info(f"  {col}")
    
    # Print summary statistics
    logger.info("\n" + "="*60)
    logger.info("SUMMARY STATISTICS")
    logger.info("="*60)
    logger.info(f"Total students: {len(combined_df)}")
    
    if 'department' in combined_df.columns:
        logger.info(f"\nBy Department:")
        for dept, count in combined_df['department'].value_counts().items():
            logger.info(f"  {dept}: {count}")
    
    logger.info("\n" + "="*60)
    logger.info("✓ Enhanced preprocessing complete!")
    logger.info("="*60)

if __name__ == "__main__":
    main()
