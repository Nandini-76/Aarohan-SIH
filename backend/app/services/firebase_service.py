"""
Firebase Realtime Database Service
Provides persistence layer for student dropout prediction data

This service enables the frontend to display the latest predictions
even when the backend is sleeping/inactive on Render's free tier.
"""

import os
import firebase_admin
from firebase_admin import credentials, db
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def init_firebase():
    """
    Initialize Firebase Admin SDK with environment variables.
    Uses credentials from environment variables set in Render.
    
    Environment variables required:
    - FIREBASE_PROJECT_ID
    - FIREBASE_PRIVATE_KEY_ID
    - FIREBASE_PRIVATE_KEY
    - FIREBASE_CLIENT_EMAIL
    - FIREBASE_DATABASE_URL
    """
    try:
        # Check if already initialized
        if firebase_admin._apps:
            logger.info("Firebase already initialized")
            return True
        
        # Get credentials from environment variables
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")
        private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
        database_url = os.getenv("FIREBASE_DATABASE_URL")
        
        # Validate required environment variables
        if not all([project_id, private_key_id, private_key, client_email, database_url]):
            logger.warning("Firebase environment variables not configured. Skipping Firebase initialization.")
            return False
        
        # Replace escaped newlines in private key
        private_key = private_key.replace("\\n", "\n")
        
        cred_data = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "private_key": private_key,
            "client_email": client_email,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        cred = credentials.Certificate(cred_data)
        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })
        
        logger.info(f"Firebase initialized successfully for project: {project_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


def update_latest_data(data: dict):
    """
    Update the latest data in Firebase Realtime Database.
    This is the main endpoint that judges/viewers will read from.
    
    Args:
        data: Dictionary containing the data to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot update data.")
            return False
            
        ref = db.reference("latestData")
        
        # Add server timestamp
        data_with_timestamp = {
            **data,
            "lastUpdated": datetime.utcnow().isoformat(),
            "serverTimestamp": {".sv": "timestamp"}
        }
        
        ref.set(data_with_timestamp)
        logger.info("Data successfully pushed to Firebase at /latestData")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update Firebase: {e}")
        return False


def update_all_students(students: list):
    """
    Store all students data in Firebase for frontend direct access.
    Stores each student by enrollment number for easy querying.
    
    Args:
        students: List of student dictionaries with predictions
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot update students data.")
            return False
            
        ref = db.reference("students")
        
        # Convert list to dictionary keyed by enrollment_no
        students_dict = {}
        for student in students:
            enrollment = str(student.get('enrollment_no', student.get('Enrollment No', '')))
            if enrollment:
                students_dict[enrollment] = {
                    **student,
                    "lastUpdated": datetime.utcnow().isoformat()
                }
        
        # Store all students
        ref.set(students_dict)
        logger.info(f"Successfully stored {len(students_dict)} students in Firebase at /students")
        
        # Update last update timestamp
        set_last_update_timestamp()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to update students in Firebase: {e}")
        return False


def update_student_prediction(student_id: str, prediction_data: dict):
    """
    Store individual student prediction in Firebase.
    
    Args:
        student_id: Unique identifier for the student
        prediction_data: Dictionary containing prediction results
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot update student data.")
            return False
            
        ref = db.reference(f"students/{student_id}")
        
        prediction_with_timestamp = {
            **prediction_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        ref.set(prediction_with_timestamp)
        logger.info(f"Student prediction stored in Firebase for ID: {student_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update student prediction: {e}")
        return False


def update_specific_path(path: str, data: dict):
    """
    Update data at a specific path in Firebase.
    
    Args:
        path: Firebase path (e.g., "analytics/summary")
        data: Dictionary containing the data to store
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot update path.")
            return False
            
        ref = db.reference(path)
        ref.set(data)
        logger.info(f"Data successfully pushed to Firebase at /{path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update Firebase at {path}: {e}")
        return False


def get_data(path: str = "latestData") -> Optional[Dict[Any, Any]]:
    """
    Retrieve data from Firebase.
    
    Args:
        path: Firebase path to retrieve data from
        
    Returns:
        Dictionary containing the data, or None if error
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot retrieve data.")
            return None
            
        ref = db.reference(path)
        data = ref.get()
        logger.info(f"Data retrieved from Firebase at /{path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to retrieve data from Firebase: {e}")
        return None


def update_batch_predictions(predictions: list):
    """
    Store batch predictions in Firebase.
    
    Args:
        predictions: List of prediction dictionaries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot update batch predictions.")
            return False
            
        ref = db.reference("batchPredictions")
        
        batch_data = {
            "predictions": predictions,
            "count": len(predictions),
            "timestamp": datetime.utcnow().isoformat(),
            "serverTimestamp": {".sv": "timestamp"}
        }
        
        ref.set(batch_data)
        logger.info(f"Batch predictions stored in Firebase: {len(predictions)} records")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update batch predictions: {e}")
        return False


def is_firebase_initialized() -> bool:
    """
    Check if Firebase has been initialized.
    
    Returns:
        bool: True if Firebase is initialized and ready
    """
    return len(firebase_admin._apps) > 0


def get_student_count() -> int:
    """
    Get the count of students currently in Firebase.
    
    Returns:
        int: Number of students in Firebase, or 0 if error
    """
    try:
        if not firebase_admin._apps:
            return 0
            
        ref = db.reference("students")
        data = ref.get()
        
        if data is None:
            return 0
            
        count = len(data) if isinstance(data, dict) else 0
        logger.info(f"Firebase currently has {count} students")
        return count
        
    except Exception as e:
        logger.error(f"Failed to get student count from Firebase: {e}")
        return 0


def get_last_update_timestamp() -> Optional[str]:
    """
    Get the timestamp of the last Firebase update.
    
    Returns:
        str: ISO format timestamp of last update, or None if not available
    """
    try:
        if not firebase_admin._apps:
            return None
            
        ref = db.reference("metadata/lastUpdate")
        timestamp = ref.get()
        
        if timestamp:
            logger.info(f"Firebase last updated: {timestamp}")
        else:
            logger.info("No last update timestamp found in Firebase")
            
        return timestamp
        
    except Exception as e:
        logger.error(f"Failed to get last update timestamp: {e}")
        return None


def set_last_update_timestamp():
    """
    Set the current timestamp as the last update time in Firebase.
    """
    try:
        if not firebase_admin._apps:
            return False
            
        ref = db.reference("metadata")
        ref.update({
            "lastUpdate": datetime.utcnow().isoformat(),
            "serverTimestamp": {".sv": "timestamp"}
        })
        
        logger.info("Updated Firebase lastUpdate timestamp")
        return True
        
    except Exception as e:
        logger.error(f"Failed to set last update timestamp: {e}")
        return False


def merge_update_students(new_students: list):
    """
    Smart merge-update: Updates ML predictions while preserving comprehensive fields.
    
    This function:
    1. Fetches existing students from Firebase
    2. Updates only ML prediction fields from new data
    3. Preserves all comprehensive fields (hometown, family, SGPA, etc.)
    4. Adds new students if they don't exist
    
    Args:
        new_students: List of student dictionaries with updated predictions
        
    Returns:
        dict: {"updated": count, "added": count, "preserved": count}
    """
    try:
        if not firebase_admin._apps:
            logger.warning("Firebase not initialized. Cannot merge-update students.")
            return {"updated": 0, "added": 0, "preserved": 0}
            
        ref = db.reference("students")
        existing_students = ref.get() or {}
        
        # Fields that should be UPDATED (ML predictions and basic academic metrics)
        update_fields = {
            'attendance', 'cgpa', 'backlogs', 'marks_10th', 'marks_12th',
            'final_phase', 'model_phase', 'prediction', 'risk_label',
            'override_reason', 'ml_probability', 'rule_override',
            'fees_flag', 'suspension_flag'
        }
        
        # Fields that should be PRESERVED (comprehensive original data)
        preserve_fields = {
            'student_name', 'name', 'hometown', 'age', 'category',
            'father_occupation', 'mother_occupation', 'family_income',
            'section', 'course', 'year_level', 'year_enrollment', 
            'year_completion', 'specialization',
            'sgpa1', 'sgpa2', 'sgpa3', 'sgpa4', 'sgpa5', 'sgpa6', 'sgpa7',
            'age_at_enrollment', 'gender', 'department'
        }
        
        updated_count = 0
        added_count = 0
        preserved_count = 0
        
        merged_students = {}
        
        for new_student in new_students:
            enrollment = str(new_student.get('enrollment_no', ''))
            if not enrollment:
                continue
            
            existing = existing_students.get(enrollment, {})
            
            if existing:
                # Student exists - merge update
                merged = existing.copy()
                
                # Update prediction fields
                for field in update_fields:
                    if field in new_student:
                        merged[field] = new_student[field]
                
                # Count preserved fields (fields that exist in Firebase but not being updated)
                for field in preserve_fields:
                    if field in existing and existing[field] is not None:
                        # Field exists in Firebase and will be preserved
                        preserved_count += 1
                
                merged['lastUpdated'] = datetime.utcnow().isoformat()
                merged_students[enrollment] = merged
                updated_count += 1
                
            else:
                # New student - add with all fields
                merged_students[enrollment] = {
                    **new_student,
                    "lastUpdated": datetime.utcnow().isoformat()
                }
                added_count += 1
        
        # Update Firebase with merged data
        ref.set(merged_students)
        
        result = {
            "updated": updated_count,
            "added": added_count,
            "preserved": preserved_count,
            "total": len(merged_students)
        }
        
        logger.info(f"✅ Merge-update complete: {updated_count} updated, {added_count} added, {preserved_count} fields preserved")
        
        # Update last update timestamp
        set_last_update_timestamp()
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to merge-update students in Firebase: {e}")
        return {"updated": 0, "added": 0, "preserved": 0, "error": str(e)}
