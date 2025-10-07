"""
Quick script to verify Firebase contains the data
"""
import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Import Firebase service
try:
    from services.firebase_service import init_firebase, is_firebase_initialized
    from firebase_admin import db
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)

def main():
    """Verify Firebase data"""
    logger.info("="*60)
    logger.info("Firebase Verification Script")
    logger.info("="*60)
    
    # Load credentials
    service_account_path = Path(__file__).parent.parent / "serviceAccountKey.json"
    if service_account_path.exists():
        with open(service_account_path, 'r') as f:
            cred_data = json.load(f)
        
        os.environ['FIREBASE_PROJECT_ID'] = cred_data.get('project_id', '')
        os.environ['FIREBASE_PRIVATE_KEY_ID'] = cred_data.get('private_key_id', '')
        os.environ['FIREBASE_PRIVATE_KEY'] = cred_data.get('private_key', '')
        os.environ['FIREBASE_CLIENT_EMAIL'] = cred_data.get('client_email', '')
        
        database_url = os.getenv('FIREBASE_DATABASE_URL')
        if not database_url:
            project_id = cred_data.get('project_id', '')
            database_url = f"https://{project_id}-default-rtdb.firebaseio.com"
            os.environ['FIREBASE_DATABASE_URL'] = database_url
        
        logger.info(f"\n✓ Loaded credentials for project: {cred_data.get('project_id')}")
    else:
        logger.error("❌ Service account key not found")
        exit(1)
    
    # Initialize Firebase
    logger.info("Initializing Firebase...")
    if not init_firebase():
        logger.error("❌ Failed to initialize Firebase")
        exit(1)
    
    if not is_firebase_initialized():
        logger.error("❌ Firebase not initialized properly")
        exit(1)
    
    logger.info("✓ Firebase initialized\n")
    
    # Get students count
    try:
        ref = db.reference("students")
        students = ref.get()
        
        if students:
            count = len(students)
            logger.info(f"✅ Firebase contains {count} students")
            
            # Show phase distribution
            phases = {}
            for enrollment, student in students.items():
                phase = student.get('final_phase', 'Unknown')
                phases[phase] = phases.get(phase, 0) + 1
            
            logger.info("\nPhase Distribution:")
            for phase in ['Green', 'Yellow', 'Orange', 'Red']:
                if phase in phases:
                    logger.info(f"  {phase}: {phases[phase]}")
            
            # Sample a few enrollments
            sample_enrollments = list(students.keys())[:5]
            logger.info(f"\nSample enrollment numbers:")
            for enrollment in sample_enrollments:
                student = students[enrollment]
                logger.info(f"  {enrollment}: {student.get('name', 'N/A')} - {student.get('final_phase', 'N/A')}")
            
        else:
            logger.warning("⚠️  No students found in Firebase at /students path")
            
    except Exception as e:
        logger.error(f"❌ Error reading from Firebase: {e}")
        exit(1)
    
    logger.info("\n" + "="*60)
    logger.info("Verification complete!")
    logger.info("="*60)

if __name__ == "__main__":
    main()
