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
