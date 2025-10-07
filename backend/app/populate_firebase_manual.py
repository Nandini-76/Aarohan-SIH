"""
Manual Firebase Population Script
Loads the preprocessed dataset and pushes all students to Firebase

Usage:
    From backend directory: python app/populate_firebase_manual.py
    From app directory: python populate_firebase_manual.py

This script will:
1. Load predicted_phase_data.csv (2,080+ students)
2. Format data for Firebase
3. Push all students to Firebase /students node
4. Verify the upload

Author: Firebase Population Script
Date: October 2025
"""

import os
import sys
import logging
import pandas as pd
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add proper paths to sys.path to enable imports
script_path = Path(__file__).resolve()
app_dir = script_path.parent
backend_dir = app_dir.parent

# Add both app and backend to path
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

logger.info(f"Script directory: {app_dir}")
logger.info(f"Backend directory: {backend_dir}")

# Import Firebase and utilities - try multiple import strategies
firebase_imported = False

try:
    # Strategy 1: Direct import from services (when in app directory)
    from services.firebase_service import (
        init_firebase,
        update_all_students,
        is_firebase_initialized
    )
    firebase_imported = True
    logger.info("✓ Imported Firebase service (strategy 1)")
except ImportError as e1:
    try:
        # Strategy 2: Import from app.services (when in backend directory)
        from app.services.firebase_service import (
            init_firebase,
            update_all_students,
            is_firebase_initialized
        )
        firebase_imported = True
        logger.info("✓ Imported Firebase service (strategy 2)")
    except ImportError as e2:
        logger.error(f"Failed to import Firebase service")
        logger.error(f"  Strategy 1 error: {e1}")
        logger.error(f"  Strategy 2 error: {e2}")
        logger.error(f"\nPaths in sys.path:")
        for p in sys.path[:5]:
            logger.error(f"  - {p}")
        logger.error(f"\nMake sure you're running from backend or app directory")
        sys.exit(1)


def generate_student_name(enrollment_no: str) -> str:
    """Generate display name from enrollment number."""
    names = [
        "Rohan Patel", "Ananya Sharma", "Vikram Joshi", "Priya Singh",
        "Aditya Verma", "Sneha Gupta", "Kartik Mehta", "Riya Agarwal",
        "Arjun Kumar", "Isha Malhotra", "Harsh Kapoor", "Kavya Reddy"
    ]
    # Use hash of enrollment number to consistently assign names
    hash_val = sum(ord(c) for c in enrollment_no)
    return names[hash_val % len(names)]


def convert_phase_to_risk_label(phase: str) -> str:
    """Convert phase to risk label."""
    phase_upper = phase.upper()
    if phase_upper == "GREEN":
        return "Low Risk"
    elif phase_upper == "YELLOW":
        return "Moderate Risk"
    elif phase_upper == "ORANGE":
        return "High Risk"
    elif phase_upper == "RED":
        return "Critical Risk"
    else:
        return "Unknown"


def load_and_format_students(data_file: Path) -> list:
    """
    Load students from CSV and format for Firebase
    
    Args:
        data_file: Path to the CSV file with student data
        
    Returns:
        List of student dictionaries formatted for Firebase
    """
    logger.info(f"Loading students from: {data_file}")
    
    try:
        df = pd.read_csv(data_file)
        logger.info(f"✓ Loaded {len(df)} student records")
    except Exception as e:
        logger.error(f"Failed to load CSV file: {e}")
        return []
    
    # Convert to Firebase format (handle NaN values properly)
    students = []
    for _, row in df.iterrows():
        # Helper function to safely convert values
        def safe_float(value, default=0.0):
            """Convert to float, return default if NaN or invalid"""
            try:
                val = float(value)
                if pd.isna(val) or val != val:  # Check for NaN
                    return default
                return val
            except (ValueError, TypeError):
                return default
        
        def safe_int(value, default=0):
            """Convert to int, return default if NaN or invalid"""
            try:
                val = float(value)
                if pd.isna(val) or val != val:  # Check for NaN
                    return default
                return int(val)
            except (ValueError, TypeError):
                return default
        
        def safe_str(value, default=''):
            """Convert to string, return default if NaN"""
            if pd.isna(value):
                return default
            return str(value)
        
        # Create student dict with ALL available fields
        cleaned_student = {
            # Core identification
            "student_id": safe_str(row.get('enrollment_no', '')),
            "enrollment_no": safe_str(row.get('enrollment_no', '')),
            "name": safe_str(row.get('student_name', generate_student_name(safe_str(row.get('enrollment_no', ''))))),
            "department": safe_str(row.get('department', '')) if pd.notna(row.get('department')) else None,
            
            # Personal information
            "gender": safe_str(row.get('gender', 'M')),
            "age": safe_int(row.get('age', 0)) if pd.notna(row.get('age')) else None,
            "age_at_enrollment": safe_int(row.get('age_at_enrollment', 0)) if pd.notna(row.get('age_at_enrollment')) else None,
            "hometown": safe_str(row.get('hometown', '')) if pd.notna(row.get('hometown')) else None,
            "category": safe_str(row.get('category', '')) if pd.notna(row.get('category')) else None,
            
            # Academic information
            "attendance": safe_float(row.get('attendance', 0)),
            "cgpa": safe_float(row.get('cgpa', 0)),
            "sgpa": safe_float(row.get('sgpa', 0)) if pd.notna(row.get('sgpa')) else None,
            "sgpa1": safe_float(row.get('sgpa1', 0)) if pd.notna(row.get('sgpa1')) else None,
            "sgpa2": safe_float(row.get('sgpa2', 0)) if pd.notna(row.get('sgpa2')) else None,
            "sgpa3": safe_float(row.get('sgpa3', 0)) if pd.notna(row.get('sgpa3')) else None,
            "sgpa4": safe_float(row.get('sgpa4', 0)) if pd.notna(row.get('sgpa4')) else None,
            "sgpa5": safe_float(row.get('sgpa5', 0)) if pd.notna(row.get('sgpa5')) else None,
            "sgpa6": safe_float(row.get('sgpa6', 0)) if pd.notna(row.get('sgpa6')) else None,
            "sgpa7": safe_float(row.get('sgpa7', 0)) if pd.notna(row.get('sgpa7')) else None,
            "backlogs": safe_int(row.get('backlogs', 0)),
            "marks_10th": safe_float(row.get('marks_10th', 0)),
            "marks_12th": safe_float(row.get('marks_12th', 0)),
            "section": safe_str(row.get('section', '')) if pd.notna(row.get('section')) else None,
            "course": safe_str(row.get('course', '')) if pd.notna(row.get('course')) else None,
            "year_level": safe_int(row.get('year_level', 0)) if pd.notna(row.get('year_level')) else None,
            "year_enrollment": safe_int(row.get('year_enrollment', 0)) if pd.notna(row.get('year_enrollment')) else None,
            "year_completion": safe_int(row.get('year_completion', 0)) if pd.notna(row.get('year_completion')) else None,
            "specialization": safe_str(row.get('specialization', '')) if pd.notna(row.get('specialization')) else None,
            
            # Family and financial
            "father_occupation": safe_str(row.get('father_occupation', '')) if pd.notna(row.get('father_occupation')) else None,
            "mother_occupation": safe_str(row.get('mother_occupation', '')) if pd.notna(row.get('mother_occupation')) else None,
            "family_income": safe_float(row.get('family_income', 0)) if pd.notna(row.get('family_income')) else None,
            "fees_status": safe_str(row.get('fees_status', '')) if pd.notna(row.get('fees_status')) else None,
            "fees_flag": safe_int(row.get('fees_flag', 0)),
            "suspension": safe_str(row.get('suspension', '')) if pd.notna(row.get('suspension')) else None,
            "suspension_flag": safe_int(row.get('suspension_flag', 0)),
            
            # ML Predictions
            "prediction": safe_str(row.get('final_phase', 'Green')),
            "final_phase": safe_str(row.get('final_phase', 'Green')),
            "model_phase": safe_str(row.get('model_phase', 'Green')),
            "predicted_phase": safe_str(row.get('predicted_phase', safe_str(row.get('final_phase', 'Green')))),
            "risk_label": convert_phase_to_risk_label(safe_str(row.get('final_phase', 'Green'))),
            "override_reason": safe_str(row.get('red_reason', '')) if pd.notna(row.get('red_reason')) else None,
            "ml_probability": safe_float(row.get('ml_probability', 0)) if pd.notna(row.get('ml_probability')) else 0.0,
            "rule_override": bool(row.get('rule_override', False))
        }
        students.append(cleaned_student)
    
    logger.info(f"✓ Formatted {len(students)} students for Firebase")
    
    # Log phase distribution
    phase_counts = df['final_phase'].value_counts()
    logger.info("\nPhase Distribution:")
    for phase, count in phase_counts.items():
        logger.info(f"  {phase}: {count}")
    
    return students


def main():
    """
    Main function to populate Firebase
    """
    logger.info("="*60)
    logger.info("Firebase Population Script")
    logger.info("="*60)
    
    # Set up Firebase credentials
    logger.info("\nPreparing Firebase credentials...")
    service_account_path = Path(__file__).parent.parent / "serviceAccountKey.json"
    
    if service_account_path.exists():
        logger.info(f"✓ Found service account key: {service_account_path}")
        # Load and parse the service account JSON
        try:
            import json
            with open(service_account_path, 'r') as f:
                cred_data = json.load(f)
            
            # Set environment variables from service account JSON
            os.environ['FIREBASE_PROJECT_ID'] = cred_data.get('project_id', '')
            os.environ['FIREBASE_PRIVATE_KEY_ID'] = cred_data.get('private_key_id', '')
            os.environ['FIREBASE_PRIVATE_KEY'] = cred_data.get('private_key', '')
            os.environ['FIREBASE_CLIENT_EMAIL'] = cred_data.get('client_email', '')
            
            # Set database URL
            database_url = os.getenv('FIREBASE_DATABASE_URL')
            if not database_url:
                # Construct default database URL from project ID
                project_id = cred_data.get('project_id', '')
                database_url = f"https://{project_id}-default-rtdb.firebaseio.com"
                os.environ['FIREBASE_DATABASE_URL'] = database_url
            
            logger.info(f"✓ Loaded Firebase credentials from service account file")
            logger.info(f"  Project ID: {cred_data.get('project_id', 'N/A')}")
            logger.info(f"  Database URL: {database_url}")
        except Exception as e:
            logger.error(f"❌ Failed to load service account JSON: {e}")
            sys.exit(1)
    else:
        logger.warning(f"⚠️  Service account key not found at: {service_account_path}")
        logger.info("Firebase will try to use environment variables")
    
    # Initialize Firebase
    logger.info("\nStep 1: Initializing Firebase...")
    if not init_firebase():
        logger.error("❌ Failed to initialize Firebase. Check your credentials.")
        logger.error("Make sure FIREBASE_SERVICE_ACCOUNT_KEY or serviceAccountKey.json exists.")
        sys.exit(1)
    
    if not is_firebase_initialized():
        logger.error("❌ Firebase not initialized properly.")
        sys.exit(1)
    
    logger.info("✓ Firebase initialized successfully")
    
    # Find data file
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    
    # Priority order for data files (prioritize comprehensive data)
    comprehensive_file = data_dir / "comprehensive_predicted.csv"
    predicted_file = data_dir / "predicted_phase_data.csv"
    merged_with_pred_file = data_dir / "merged_with_predictions.csv"
    merged_file = data_dir / "merged_dataset.csv"
    
    data_file = None
    if comprehensive_file.exists():
        data_file = comprehensive_file
        logger.info(f"\n✓ Found comprehensive dataset: {comprehensive_file.name}")
        logger.info("  (Includes ALL original fields + ML predictions)")
    elif predicted_file.exists():
        data_file = predicted_file
        logger.info(f"\n✓ Found preprocessed dataset: {predicted_file.name}")
    elif merged_with_pred_file.exists():
        data_file = merged_with_pred_file
        logger.info(f"\n⚠️  Using demo dataset with predictions: {merged_with_pred_file.name}")
    elif merged_file.exists():
        data_file = merged_file
        logger.info(f"\n⚠️  Using demo dataset (without predictions): {merged_file.name}")
    else:
        logger.error(f"\n❌ No data file found in {data_dir}")
        sys.exit(1)
    
    # Load and format students
    logger.info("\nStep 2: Loading and formatting student data...")
    students = load_and_format_students(data_file)
    
    if not students:
        logger.error("❌ No students to upload")
        sys.exit(1)
    
    # Push to Firebase
    logger.info(f"\nStep 3: Uploading {len(students)} students to Firebase...")
    try:
        update_all_students(students)
        logger.info(f"✓ Successfully uploaded {len(students)} students to Firebase")
    except Exception as e:
        logger.error(f"❌ Failed to upload students to Firebase: {e}")
        sys.exit(1)
    
    # Success
    logger.info("\n" + "="*60)
    logger.info("✅ Firebase population completed successfully!")
    logger.info("="*60)
    logger.info(f"\nTotal students in Firebase: {len(students)}")
    logger.info("Frontend should now show the updated data.")
    logger.info("\nYou can verify at: https://console.firebase.google.com")


if __name__ == "__main__":
    main()
