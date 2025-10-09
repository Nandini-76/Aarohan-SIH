"""
AI-based Drop-out Prediction and Counseling System
FastAPI Backend with Rule-based Scoring System

Author: Pair Programming Session
Date: September 10, 2025
Problem Statement ID: 25102 - Government of Rajasthan DTE

This module implements a rule-based scoring system to identify students at risk
of dropping out based on 7 key factors. The system provides REST API endpoints
for simulation and historical data retrieval.
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response, Request, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ML model imports
try:
    import joblib
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    joblib = None
    StandardScaler = None

# Import utility functions - handle both local and deployed environments
try:
    # Try relative import first (for local development from app directory)
    from utils import (
        process_single_prediction, 
        add_predictions_to_dataset,
        validate_student_input,
        predict_with_unified_system,
        run_batch_prediction_pipeline,
        send_notification
    )
except ImportError:
    # Fall back to app.utils for deployed environment
    from app.utils import (
        process_single_prediction, 
        add_predictions_to_dataset,
        validate_student_input,
        predict_with_unified_system,
        run_batch_prediction_pipeline,
        send_notification
    )

# Import Firebase service - handle both local and deployed environments
try:
    from services.firebase_service import (
        init_firebase,
        update_latest_data,
        update_all_students,
        update_student_prediction,
        update_batch_predictions,
        is_firebase_initialized,
        merge_update_students
    )
except ImportError:
    try:
        from app.services.firebase_service import (
            init_firebase,
            update_latest_data,
            update_all_students,
            update_student_prediction,
            update_batch_predictions,
            is_firebase_initialized,
            merge_update_students
        )
    except ImportError:
        # Configure logging first
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.warning("Firebase service not available")
        # Define dummy functions if Firebase not available
        def init_firebase(): return False
        def update_latest_data(data): return False
        def update_all_students(students): return False
        def update_student_prediction(sid, data): return False
        def update_batch_predictions(preds): return False
        def is_firebase_initialized(): return False
        def merge_update_students(students): return {"updated": 0, "added": 0, "preserved": 0}

# Helper functions for API
def generate_student_name(enrollment_no: str) -> str:
    """Generate display name from enrollment number for consistency with frontend."""
    # Extract number from enrollment (e.g., "2023ENG001" -> "001")
    import re
    match = re.search(r'(\d+)$', enrollment_no)
    num = int(match.group(1)) if match else 1
    
    # Generate realistic names based on enrollment number
    first_names = [
        'Aarav', 'Ananya', 'Arjun', 'Diya', 'Ishaan', 'Kavya', 'Kiran', 'Meera',
        'Nikhil', 'Priya', 'Rahul', 'Riya', 'Rohan', 'Sakshi', 'Siddharth', 'Sneha',
        'Varun', 'Vani', 'Yash', 'Zara', 'Aditya', 'Aditi', 'Akash', 'Bhavya',
        'Charan', 'Deepika', 'Eshaan', 'Fathima', 'Gaurav', 'Harini'
    ]
    
    last_names = [
        'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Reddy', 'Patel', 'Shah',
        'Jain', 'Agarwal', 'Mehta', 'Chopra', 'Malhotra', 'Khanna', 'Rao',
        'Iyer', 'Nair', 'Pillai', 'Menon', 'Krishnan', 'Sundaram', 'Raman',
        'Prasad', 'Srinivas', 'Venkat', 'Mohan', 'Suresh', 'Ramesh', 'Dinesh', 'Ganesh'
    ]
    
    first_name = first_names[(num - 1) % len(first_names)]
    last_name = last_names[(num - 1) // len(first_names) % len(last_names)]
    
    return f"{first_name} {last_name}"


def _convert_phase_to_risk_label(phase: str) -> str:
    """Convert phase to human-readable risk label."""
    phase_map = {
        "Green": "Low Risk",
        "Yellow": "Medium Risk", 
        "Orange": "High Risk",
        "Red": "Critical Risk"
    }
    return phase_map.get(phase, "Unknown Risk")

# Import pipeline functions
# from models.integration_pipeline import run_integration_pipeline
# from models.prediction_pipeline import run_prediction_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data file path - handle both local and deployed environments
if os.path.exists("data/merged_dataset.csv"):
    DATA_FILE_PATH = "data/merged_dataset.csv"  # Local development
else:
    DATA_FILE_PATH = "app/data/merged_dataset.csv"  # Deployed environment

# ML Model configuration - handle both local and deployed environments
if os.path.exists("models"):
    MODELS_DIR = Path("models")  # Local development
else:
    MODELS_DIR = Path("app/models")  # Deployed environment

MODEL_PATH = MODELS_DIR / "rf_pipeline_broad.joblib"
SCALER_PATH = MODELS_DIR / "scaler.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

# Global ML model variables
ml_model = None
ml_scaler = None
ml_feature_names = None
ml_metrics = None
model_loaded = False

# FastAPI app initialization
app = FastAPI(
    title="AI-based Drop-out Prediction System",
    description="Rule-based scoring system for early identification of at-risk students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration - enhanced for local and production
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000,http://localhost:5173,https://arohann.vercel.app,https://aarohan.vercel.app")
FRONTEND_URL_REGEX = os.getenv("FRONTEND_URL_REGEX")

# Comprehensive allowed origins for all environments
default_origins = [
    # Local development - all common ports and hosts
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:8080",  # Vite frontend port
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",  # Vite frontend port
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    # Production Vercel deployments
    "https://arohann.vercel.app",
    "https://aarohan.vercel.app",
    # Add any additional production domains
]

# Development mode - be more permissive for local testing
if os.getenv("NODE_ENV") == "development" or os.getenv("ENVIRONMENT") == "development":
    # Add more local development origins
    dev_origins = [
        "http://localhost:3001",
        "http://localhost:4173",
        "http://127.0.0.1:3001", 
        "http://127.0.0.1:4173",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:5173",
    ]
    default_origins.extend(dev_origins)

if FRONTEND_URL.strip() == "*":
    # Use default origins instead of wildcard to allow credentials
    allowed_origins = default_origins
else:
    # Parse custom origins from environment
    custom_origins = [o.strip() for o in FRONTEND_URL.split(",") if o.strip()]
    allowed_origins = list(set(default_origins + custom_origins))

# Enhanced CORS configuration
cors_kwargs = dict(
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Use regex pattern to allow Vercel preview deployments (only if explicitly set)
if FRONTEND_URL_REGEX and FRONTEND_URL_REGEX.strip():
    cors_kwargs["allow_origin_regex"] = FRONTEND_URL_REGEX.strip()
    # When using regex, don't set allow_origins
    logger.info(f"CORS configured with regex pattern: {FRONTEND_URL_REGEX}")
else:
    cors_kwargs["allow_origins"] = allowed_origins
    logger.info(f"CORS configured with specific origins: {allowed_origins}")

app.add_middleware(CORSMiddleware, **cors_kwargs)

# Add explicit CORS preflight handler for better compatibility
@app.options("/{full_path:path}")
async def preflight_handler(request: Request):
    """Handle CORS preflight requests explicitly."""
    origin = request.headers.get("origin")
    
    # Check if origin is allowed
    if origin in allowed_origins:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, Origin, Access-Control-Request-Method, Access-Control-Request-Headers",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        }
        return Response(status_code=200, headers=headers)
    
    return Response(status_code=400)

# Pydantic models for request/response
class StudentRecord(BaseModel):
    """Individual student record model"""
    enrollment_no: str = Field(..., description="Student enrollment number")
    fees_paid: str = Field(..., pattern="^[YN]$", description="Fees payment status (Y/N)")
    gpa: float = Field(..., ge=0, le=10, description="Overall academic performance (0-10)")
    marks_10: float = Field(..., ge=0, le=100, description="10th grade marks percentage")
    marks_12: float = Field(..., ge=0, le=100, description="12th grade marks percentage")
    attendance_percent: float = Field(..., ge=0, le=100, description="Attendance percentage")
    backlogs: int = Field(..., ge=0, description="Number of academic backlogs")
    suspension: str = Field(..., pattern="^[YN]$", description="Suspension status (Y/N)")

class StudentProfile(BaseModel):
    """Complete student profile with prediction"""
    enrollment_no: str
    attendance: float
    cgpa: float
    backlogs: int
    marks_10th: float
    marks_12th: float
    fees_flag: int
    suspension_flag: int
    gender: str
    age_at_enrollment: Optional[int] = None
    category: Optional[str] = None
    department: Optional[str] = None
    final_phase: Optional[str] = None
    override_reason: Optional[str] = None
    ml_probability: Optional[float] = None

class SimulateRequest(BaseModel):
    """Request model for simulation endpoint"""
    enrollment_no: Optional[str] = Field(None, description="Student enrollment number")
    attendance: float = Field(..., ge=0, le=100, description="Attendance percentage")
    cgpa: float = Field(..., ge=0, le=10, description="CGPA (0-10)")
    backlogs: int = Field(..., ge=0, description="Number of backlogs")
    marks_10th: Optional[float] = Field(60, ge=0, le=100, description="10th grade marks")
    marks_12th: Optional[float] = Field(60, ge=0, le=100, description="12th grade marks")
    fees_flag: Optional[int] = Field(0, ge=0, le=1, description="Fees payment flag (0=paid, 1=unpaid)")
    suspension_flag: Optional[int] = Field(0, ge=0, description="Suspension flag (0=no suspension, 1=suspended)")
    gender: Optional[str] = Field("M", pattern="^[MF]$", description="Gender")
    email: Optional[str] = Field(None, description="Optional email address to receive report")

class SimulateResponse(BaseModel):
    """Response model for simulation endpoint"""
    enrollment_no: Optional[str] = Field(None, description="Student enrollment number (if provided)")
    model_phase: str = Field(..., description="ML model prediction: Red, Yellow, Orange, or Green")
    final_phase: str = Field(..., description="Final prediction after Red-Zone overrides")
    override_reason: str = Field("", description="Reason for override (if any)")
    ml_probability: Optional[float] = Field(None, description="ML model dropout probability")
    rule_override: bool = Field(False, description="Whether red-zone rules overrode ML prediction")
    notification_message: Optional[str] = Field(None, description="Notification message sent if risk is Orange/Red")
    report_id: Optional[str] = Field(None, description="Simulation ID for report generation (if orange/red)")
    report_generated: bool = Field(False, description="Whether PDF report was generated")
    email_sent: bool = Field(False, description="Whether report was sent via email")

class TrainingResponse(BaseModel):
    """Response model for training endpoint"""
    success: bool = Field(..., description="Whether training completed successfully")
    message: str = Field(..., description="Training status message")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Training metrics if successful")
    model_path: Optional[str] = Field(None, description="Path to saved model file")

class SimulationListResponse(BaseModel):
    """Response model for simulations list endpoint"""
    simulations: List[Dict[str, Any]] = Field(..., description="List of all past simulations")

class MergeResponse(BaseModel):
    """Response model for merge endpoint"""
    status: str = Field(..., description="Merge operation status")
    total_students: int = Field(..., description="Total number of students merged")
    total_columns: int = Field(..., description="Total number of columns in merged dataset")
    output_path: str = Field(..., description="Path to merged dataset file")
    preview: List[Dict[str, Any]] = Field(..., description="Preview of first 5 rows")
    columns: List[str] = Field(..., description="List of all column names")

class PredictResponse(BaseModel):
    """Response model for predict endpoint"""
    status: str = Field(..., description="Prediction operation status")
    total_students: int = Field(..., description="Total number of students processed")
    phase_distribution: Dict[str, int] = Field(..., description="Distribution of final predicted phases")
    model_phase_distribution: Dict[str, int] = Field(..., description="Distribution of ML model phases (before overrides)")
    red_zone_overrides: int = Field(..., description="Number of red-zone rule overrides")
    ml_model_used: bool = Field(..., description="Whether ML model was used")
    output_path: str = Field(..., description="Path to predictions file")
    preview: List[Dict[str, Any]] = Field(..., description="Preview of predictions with both phases")

class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    model_metrics: Optional[Dict[str, Any]] = Field(None, description="Model performance metrics")
    dataset_size: Optional[int] = Field(None, description="Size of training dataset")
    feature_importance: Optional[Dict[str, float]] = Field(None, description="Feature importance scores")
    model_info: Optional[Dict[str, Any]] = Field(None, description="Model configuration info")


# ML Model Management
async def run_preprocessing_if_needed():
    """
    Run preprocessing pipeline if predicted_phase_data.csv doesn't exist or is outdated.
    This ensures the large dataset is processed and ready for the backend.
    """
    try:
        data_dir = Path(__file__).parent / "data"
        predicted_data_file = data_dir / "predicted_phase_data.csv"
        cleaned_data_file = data_dir / "cleaned_data.csv"
        
        # Check if we need to run preprocessing
        needs_preprocessing = False
        
        if not predicted_data_file.exists():
            logger.info("Predicted data file not found - preprocessing needed")
            needs_preprocessing = True
        elif not cleaned_data_file.exists():
            logger.info("Cleaned data file not found - preprocessing needed")
            needs_preprocessing = True
        else:
            # Check if source data is newer than processed data
            full_college_data_dir = Path(__file__).parent.parent / "Full-college-data"
            if full_college_data_dir.exists():
                # Get the latest modification time of source files
                source_files = list(full_college_data_dir.rglob("*.csv")) + list(full_college_data_dir.rglob("*.xlsx"))
                if source_files:
                    latest_source_time = max(f.stat().st_mtime for f in source_files)
                    predicted_time = predicted_data_file.stat().st_mtime
                    
                    if latest_source_time > predicted_time:
                        logger.info("Source data is newer than predicted data - preprocessing needed")
                        needs_preprocessing = True
        
        if needs_preprocessing:
            logger.info("="*60)
            logger.info("RUNNING PREPROCESSING PIPELINE")
            logger.info("="*60)
            
            # Step 1: Run data preprocessing
            logger.info("\nStep 1: Preprocessing college data...")
            preprocess_script = Path(__file__).parent / "preprocess_college_data.py"
            
            if preprocess_script.exists():
                result = subprocess.run(
                    [sys.executable, str(preprocess_script)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    logger.info("✓ Data preprocessing completed successfully")
                    logger.info(result.stdout)
                else:
                    logger.error(f"Data preprocessing failed: {result.stderr}")
                    logger.warning("Continuing with existing data if available...")
                    return
            else:
                logger.warning(f"Preprocessing script not found: {preprocess_script}")
            
            # Step 2: Generate predictions
            if cleaned_data_file.exists():
                logger.info("\nStep 2: Generating ML predictions...")
                predict_script = Path(__file__).parent / "generate_predictions.py"
                
                if predict_script.exists():
                    result = subprocess.run(
                        [sys.executable, str(predict_script)],
                        capture_output=True,
                        text=True,
                        timeout=600  # 10 minutes timeout
                    )
                    
                    if result.returncode == 0:
                        logger.info("✓ Prediction generation completed successfully")
                        logger.info(result.stdout)
                    else:
                        logger.error(f"Prediction generation failed: {result.stderr}")
                        logger.warning("Continuing with existing data if available...")
                else:
                    logger.warning(f"Prediction script not found: {predict_script}")
            
            logger.info("="*60)
            logger.info("PREPROCESSING PIPELINE COMPLETED")
            logger.info("="*60)
        else:
            logger.info("✓ Predicted data file exists and is up to date - skipping preprocessing")
            
    except Exception as e:
        logger.error(f"Error during preprocessing check: {e}")
        logger.warning("Continuing with existing data if available...")


def load_student_data() -> pd.DataFrame:
    """
    Load student data from the most comprehensive available dataset.
    Priority: comprehensive_predicted.csv > predicted_phase_data.csv > merged_with_predictions.csv
    
    Returns:
        DataFrame with student data including predictions
    """
    data_dir = Path(__file__).parent / "data"
    
    # Try files in priority order
    file_paths = [
        data_dir / "comprehensive_predicted.csv",
        data_dir / "predicted_phase_data.csv",
        data_dir / "merged_with_predictions.csv",
        data_dir / "merged_dataset.csv"
    ]
    
    for file_path in file_paths:
        if file_path.exists():
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} students from {file_path.name}")
            
            # Ensure required columns exist
            if 'final_phase' not in df.columns and 'predicted_phase' in df.columns:
                df['final_phase'] = df['predicted_phase']
            
            # Add student_name if missing (generate from enrollment_no)
            if 'student_name' not in df.columns and 'enrollment_no' in df.columns:
                df['student_name'] = df['enrollment_no'].apply(
                    lambda x: f"Student {str(x)[-4:]}" if pd.notna(x) else "Unknown"
                )
            
            # Ensure year_level exists
            if 'year_level' not in df.columns and 'year' in df.columns:
                df['year_level'] = df['year']
            
            return df
    
    raise FileNotFoundError("No student data file found in data directory")


def load_ml_model():
    """
    Load trained ML model and scaler if available.
    
    Sets global variables: ml_model, ml_scaler, ml_feature_names, ml_metrics, model_loaded
    """
    global ml_model, ml_scaler, ml_feature_names, ml_metrics, model_loaded
    
    if not ML_AVAILABLE:
        logger.warning("ML libraries not available - continuing with rule-based system only")
        return
    
    try:
        # Add models directory to Python path for model dependencies
        import sys
        models_dir = Path(__file__).parent / "models"
        if str(models_dir) not in sys.path:
            sys.path.insert(0, str(models_dir))
        
        # Check if model file exists
        if not MODEL_PATH.exists():
            logger.info("ML model file not found - operating with rules only")
            logger.info(f"Expected model at: {MODEL_PATH}")
            return
        
        # Load model (this could be a pipeline or just the model)
        ml_model = joblib.load(MODEL_PATH)
        logger.info(f"Loaded model type: {type(ml_model).__name__}")
        
        # Check if we have a separate scaler or if it's included in pipeline
        if SCALER_PATH.exists():
            ml_scaler = joblib.load(SCALER_PATH)
            logger.info("Loaded separate scaler")
        else:
            # If no separate scaler, assume preprocessing is in pipeline or use identity
            logger.info("No separate scaler found - assuming preprocessing in pipeline")
            ml_scaler = None
        
        # Load metrics if available
        if METRICS_PATH.exists():
            with open(METRICS_PATH, 'r') as f:
                ml_metrics = json.load(f)
                ml_feature_names = ml_metrics.get('feature_names', [])
        else:
            # Default feature order (must match training script)
            ml_feature_names = ['attendance', 'cgpa', 'marks_10th', 'marks_12th', 'backlogs', 'fees_flag', 'suspension_flag']
        
        model_loaded = True
        logger.info("✅ ML model loaded successfully!")
        logger.info(f"Feature count: {len(ml_feature_names)}")
        if ml_metrics:
            logger.info(f"Test accuracy: {ml_metrics.get('test_accuracy', 'N/A')}")
            logger.info(f"Test F1-score: {ml_metrics.get('test_f1', 'N/A')}")
        
    except ImportError as e:
        logger.warning(f"Model dependencies not available: {e}")
        logger.info("Continuing with rule-based system only")
        ml_model = None
        ml_scaler = None
        ml_feature_names = None
        ml_metrics = None
        model_loaded = False
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        ml_model = None
        ml_scaler = None
        ml_feature_names = None
        ml_metrics = None
        model_loaded = False

async def periodic_firebase_update():
    """
    Background task that runs every 5 hours to refresh Firebase data.
    Updates predictions while preserving comprehensive fields.
    """
    import asyncio
    while True:
        try:
            # Wait 5 hours (18,000 seconds)
            await asyncio.sleep(18000)
            
            logger.info("⏰ Periodic update: Refreshing Firebase data (every 5 hours)")
            
            if is_firebase_initialized():
                await populate_firebase_on_startup()
                logger.info("✅ Periodic Firebase update completed successfully")
            else:
                logger.warning("⚠️ Firebase not initialized, skipping periodic update")
                
        except Exception as e:
            logger.error(f"❌ Periodic Firebase update failed: {e}")
            # Continue the loop even if update fails


async def populate_firebase_on_startup():
    """
    Load preprocessed dataset with predictions and push to Firebase on startup.
    This ensures the frontend always sees the latest data with 2,080+ students.
    Includes ALL comprehensive fields (42 total) from comprehensive_predicted.csv.
    """
    try:
        logger.info("🔄 Loading preprocessed dataset for Firebase...")
        
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        # Priority order: comprehensive_predicted.csv > predicted_phase_data.csv > merged_with_predictions.csv > merged_dataset.csv
        comprehensive_file = os.path.join(data_dir, "comprehensive_predicted.csv")
        predicted_phase_file = os.path.join(data_dir, "predicted_phase_data.csv")
        merged_with_pred_file = os.path.join(data_dir, "merged_with_predictions.csv")
        merged_file = os.path.join(data_dir, "merged_dataset.csv")
        
        # Try to load the comprehensive dataset first (all 42 fields)
        if os.path.exists(comprehensive_file):
            df = pd.read_csv(comprehensive_file)
            logger.info(f"✓ Loaded {len(df)} students from comprehensive_predicted.csv (42 fields with all original data)")
        elif os.path.exists(predicted_phase_file):
            df = pd.read_csv(predicted_phase_file)
            logger.info(f"✓ Loaded {len(df)} students from predicted_phase_data.csv (preprocessed)")
        elif os.path.exists(merged_with_pred_file):
            df = pd.read_csv(merged_with_pred_file)
            logger.info(f"Loaded {len(df)} students from merged_with_predictions.csv (demo with predictions)")
        elif os.path.exists(merged_file):
            df = pd.read_csv(merged_file)
            logger.info(f"Loaded {len(df)} students from merged_dataset.csv - generating predictions...")
            # Generate predictions on-the-fly for demo data
            df = add_predictions_to_dataset(df, ml_model, ml_scaler)
        else:
            logger.warning(f"No dataset found for startup population in {data_dir}")
            return
        
        # Convert to the format expected by Firebase (handle NaN values properly)
        # Helper functions to safely convert values (Firebase doesn't accept NaN)
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
        
        students = []
        for _, row in df.iterrows():
            # Base fields (always present)
            cleaned_student = {
                "student_id": safe_str(row.get('enrollment_no', '')),
                "enrollment_no": safe_str(row.get('enrollment_no', '')),
                "name": safe_str(row.get('student_name', '')) or generate_student_name(safe_str(row.get('enrollment_no', ''))),
                "department": safe_str(row.get('department', '')) if pd.notna(row.get('department')) else None,
                "attendance": safe_float(row.get('attendance', 0)),
                "cgpa": safe_float(row.get('cgpa', 0)),
                "backlogs": safe_int(row.get('backlogs', 0)),
                "marks_10th": safe_float(row.get('marks_10th', 0)),
                "marks_12th": safe_float(row.get('marks_12th', 0)),
                "fees_flag": safe_int(row.get('fees_flag', 0)),
                "suspension_flag": safe_int(row.get('suspension_flag', 0)),
                "gender": safe_str(row.get('gender', 'M')),
                "age_at_enrollment": safe_int(row.get('age_at_enrollment', 0)) if pd.notna(row.get('age_at_enrollment')) else None,
                "category": safe_str(row.get('category', '')) if pd.notna(row.get('category')) else None,
                "prediction": safe_str(row.get('final_phase', 'Green')),
                "final_phase": safe_str(row.get('final_phase', 'Green')),
                "model_phase": safe_str(row.get('model_phase', 'Green')),
                "risk_label": _convert_phase_to_risk_label(safe_str(row.get('final_phase', 'Green'))),
                "override_reason": safe_str(row.get('override_reason', row.get('red_reason', ''))),
                "ml_probability": safe_float(row.get('ml_probability', 0)) if pd.notna(row.get('ml_probability')) else 0.0,
                "rule_override": bool(row.get('rule_override', False))
            }
            
            # Add comprehensive fields if present (from comprehensive_predicted.csv)
            comprehensive_fields = {
                'hometown': safe_str(row.get('hometown', '')) if pd.notna(row.get('hometown')) else None,
                'age': safe_int(row.get('age', 0)) if pd.notna(row.get('age')) else None,
                'father_occupation': safe_str(row.get('father_occupation', '')) if pd.notna(row.get('father_occupation')) else None,
                'mother_occupation': safe_str(row.get('mother_occupation', '')) if pd.notna(row.get('mother_occupation')) else None,
                'family_income': safe_float(row.get('family_income', 0)) if pd.notna(row.get('family_income')) else None,
                'section': safe_str(row.get('section', '')) if pd.notna(row.get('section')) else None,
                'course': safe_str(row.get('course', '')) if pd.notna(row.get('course')) else None,
                'year_level': safe_int(row.get('year_level', 0)) if pd.notna(row.get('year_level')) else None,
                'year_enrollment': safe_int(row.get('year_enrollment', 0)) if pd.notna(row.get('year_enrollment')) else None,
                'year_completion': safe_int(row.get('year_completion', 0)) if pd.notna(row.get('year_completion')) else None,
                'specialization': safe_str(row.get('specialization', '')) if pd.notna(row.get('specialization')) else None,
                'sgpa1': safe_float(row.get('sgpa1', 0)) if pd.notna(row.get('sgpa1')) else None,
                'sgpa2': safe_float(row.get('sgpa2', 0)) if pd.notna(row.get('sgpa2')) else None,
                'sgpa3': safe_float(row.get('sgpa3', 0)) if pd.notna(row.get('sgpa3')) else None,
                'sgpa4': safe_float(row.get('sgpa4', 0)) if pd.notna(row.get('sgpa4')) else None,
                'sgpa5': safe_float(row.get('sgpa5', 0)) if pd.notna(row.get('sgpa5')) else None,
                'sgpa6': safe_float(row.get('sgpa6', 0)) if pd.notna(row.get('sgpa6')) else None,
                'sgpa7': safe_float(row.get('sgpa7', 0)) if pd.notna(row.get('sgpa7')) else None,
            }
            
            # Only add comprehensive fields if they exist in the dataframe
            for field, value in comprehensive_fields.items():
                if field in df.columns and value is not None:
                    cleaned_student[field] = value
            
            students.append(cleaned_student)
        
        # Smart merge-update: Updates predictions, preserves comprehensive fields
        if is_firebase_initialized():
            result = merge_update_students(students)
            logger.info(f"✅ Smart merge-update complete:")
            logger.info(f"   - Updated: {result['updated']} students (predictions refreshed)")
            logger.info(f"   - Added: {result['added']} new students")
            logger.info(f"   - Preserved: {result['preserved']} comprehensive fields")
            logger.info(f"   - Total students in Firebase: {result.get('total', len(students))}")
        else:
            logger.warning("Firebase not initialized, skipping startup population")
            
    except Exception as e:
        logger.error(f"Failed to populate Firebase on startup: {e}")
        # Don't raise - we want the app to start even if this fails

@app.on_event("startup")
async def startup_event():
    """Initialize ML model, run preprocessing if needed, and initialize Firebase on startup"""
    # Run preprocessing pipeline if needed
    await run_preprocessing_if_needed()
    
    # Load ML model
    load_ml_model()
    
    # Initialize Firebase for data persistence
    try:
        firebase_success = init_firebase()
        if firebase_success:
            logger.info("Firebase initialized successfully - data will be persisted")
            
            # Smart merge-update on every startup
            from app.services.firebase_service import get_student_count, get_last_update_timestamp
            
            firebase_student_count = get_student_count()
            last_update = get_last_update_timestamp()
            
            if firebase_student_count > 0:
                logger.info(f"✓ Firebase has {firebase_student_count} students")
                if last_update:
                    logger.info(f"📅 Last updated: {last_update}")
                logger.info("� Running smart merge-update: Refreshing predictions, preserving comprehensive data...")
                await populate_firebase_on_startup()
            else:
                logger.info("📭 Firebase is empty - populating with comprehensive data (42 fields)...")
                await populate_firebase_on_startup()
            
            # Start background task for periodic updates every 5 hours
            import asyncio
            asyncio.create_task(periodic_firebase_update())
            logger.info("⏰ Scheduled periodic Firebase updates every 5 hours")
        else:
            logger.warning("Firebase not configured - continuing without persistence layer")
    except Exception as e:
        logger.error(f"Firebase initialization error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutdown")


# ==========================================
# API Endpoints
# ==========================================
@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint"""
    try:
        return {
            "message": "AI-based Drop-out Prediction System is running",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "firebase_status": "connected" if is_firebase_initialized() else "not_configured",
            "model_loaded": model_loaded,
            "status": "healthy"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.head("/")
async def root_head():
    """HEAD health check for platform probes (returns 200 without body)."""
    return Response(status_code=200)


@app.get("/health", summary="Health Check for Keep-Alive")
async def health_check():
    """Lightweight health check endpoint for keep-alive pings"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    """Handle CORS preflight requests"""
    origin = request.headers.get("origin", "*")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400",
        }
    )


@app.get("/cors-test")
async def cors_test(request: Request):
    """Test endpoint to check CORS configuration"""
    origin = request.headers.get("origin")
    return {
        "message": "CORS test endpoint",
        "origin": origin,
        "allowed_origins": allowed_origins if 'allowed_origins' in globals() else "Not set",
        "user_agent": request.headers.get("user-agent"),
        "headers": dict(request.headers)
    }


@app.get("/students", summary="Get All Students")
async def get_all_students():
    """
    Get all student profiles from the merged dataset with predictions.
    
    Returns:
        List of all student profiles including final_phase and override_reason if available
    """
    try:
        # Priority order for loading data:
        # 1. comprehensive_predicted.csv (42 fields with all original data)
        # 2. predicted_phase_data.csv (large preprocessed dataset with predictions)
        # 3. merged_with_predictions.csv (demo dataset with predictions)
        # 4. merged_dataset.csv (demo dataset without predictions - generate on-the-fly)
        
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        # Try to load comprehensive_predicted.csv first (all original data + predictions)
        comprehensive_file = os.path.join(data_dir, "comprehensive_predicted.csv")
        if os.path.exists(comprehensive_file):
            df = pd.read_csv(comprehensive_file)
            logger.info(f"✓ Loaded {len(df)} student records from comprehensive_predicted.csv (42 fields)")
        # Fall back to predicted_phase_data.csv (from preprocessing pipeline)
        elif os.path.exists(os.path.join(data_dir, "predicted_phase_data.csv")):
            predicted_phase_file = os.path.join(data_dir, "predicted_phase_data.csv")
            df = pd.read_csv(predicted_phase_file)
            logger.info(f"✓ Loaded {len(df)} student records from predicted_phase_data.csv (preprocessed)")
        # Fall back to merged_with_predictions.csv (demo data with predictions)
        elif os.path.exists(os.path.join(data_dir, "merged_with_predictions.csv")):
            predictions_file = os.path.join(data_dir, "merged_with_predictions.csv")
            df = pd.read_csv(predictions_file)
            logger.info(f"Loaded {len(df)} student records with predictions from {predictions_file}")
        # Fall back to merged_dataset.csv (demo data without predictions)
        else:
            merged_file = os.path.join(data_dir, "merged_dataset.csv")
            if not os.path.exists(merged_file):
                raise HTTPException(status_code=404, detail=f"No dataset found in {data_dir}")
            
            df = pd.read_csv(merged_file)
            logger.info(f"Loaded {len(df)} student records from merged dataset")
            
            # Generate predictions using utils function (already imported at top of file)
            df = add_predictions_to_dataset(df, ml_model, ml_scaler)
        
        # Convert to JSON-serializable format
        students = []
        for _, row in df.iterrows():
            # Clean and standardize the student data
            cleaned_student = {
                "student_id": str(row.get('enrollment_no', '')),
                "enrollment_no": str(row.get('enrollment_no', '')),
                "name": generate_student_name(str(row.get('enrollment_no', ''))),
                "department": str(row.get('department', '')) if pd.notna(row.get('department')) else None,
                "attendance": float(row.get('attendance', 0)),
                "cgpa": float(row.get('cgpa', 0)),
                "backlogs": int(row.get('backlogs', 0)),
                "marks_10th": float(row.get('marks_10th', 0)),
                "marks_12th": float(row.get('marks_12th', 0)),
                "fees_flag": int(row.get('fees_flag', 0)),  # 0 = paid, 1 = unpaid
                "suspension_flag": int(row.get('suspension_flag', 0)),  # 0 = no suspension, 1 = suspended
                "gender": str(row.get('gender', 'M')),
                "age_at_enrollment": int(row.get('age_at_enrollment', 0)) if pd.notna(row.get('age_at_enrollment')) else None,
                "category": str(row.get('category', '')) if pd.notna(row.get('category')) else None,
                # Prediction results
                "prediction": str(row.get('final_phase', 'Green')),
                "final_phase": str(row.get('final_phase', 'Green')),
                "model_phase": str(row.get('model_phase', 'Green')),
                "risk_label": _convert_phase_to_risk_label(str(row.get('final_phase', 'Green'))),
                "override_reason": str(row.get('override_reason', row.get('red_reason', ''))),
                "ml_probability": float(row.get('ml_probability', 0)) if pd.notna(row.get('ml_probability')) else None,
                "rule_override": bool(row.get('rule_override', False))
            }
            
            # Log the payload for debugging
            logger.debug(f"Student {cleaned_student['enrollment_no']}: fees_flag={cleaned_student['fees_flag']}, "
                        f"suspension_flag={cleaned_student['suspension_flag']}, prediction={cleaned_student['prediction']}")
            
            students.append(cleaned_student)
        
        # Store all students in Firebase for frontend direct access
        if is_firebase_initialized():
            try:
                update_all_students(students)
                logger.info("Students data pushed to Firebase successfully")
            except Exception as fb_error:
                logger.warning(f"Failed to push students to Firebase: {fb_error}")
        
        logger.info(f"Returning {len(students)} student profiles")
        return {"students": students, "total": len(students)}
        
    except Exception as e:
        logger.error(f"Failed to get students: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve students: {str(e)}")


@app.get("/students/{enrollment_no}", summary="Get Student by Enrollment Number")
async def get_student_by_enrollment(enrollment_no: str):
    """
    Get a single student's profile and prediction by enrollment number.
    
    Args:
        enrollment_no: Student enrollment number
        
    Returns:
        Student profile with prediction information
    """
    try:
        # Prefer predictions file for consistency with list endpoint
        predictions_file = os.path.join(os.path.dirname(__file__), "data", "merged_with_predictions.csv")
        merged_file = os.path.join(os.path.dirname(__file__), "data", "merged_dataset.csv")

        if os.path.exists(predictions_file):
            df = pd.read_csv(predictions_file)
            logger.info(f"Loaded students from predictions file for single lookup: {predictions_file}")
        elif os.path.exists(merged_file):
            df = pd.read_csv(merged_file)
            logger.info(f"Loaded students from merged dataset for single lookup: {merged_file}")
        else:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {merged_file}")

        # Normalize and find student by enrollment number (case-insensitive, trimmed)
        target = str(enrollment_no).strip().upper()
        df['__enr_norm__'] = df['enrollment_no'].astype(str).str.strip().str.upper()
        student_df = df[df['__enr_norm__'] == target].drop(columns=['__enr_norm__'])
        if student_df.empty:
            raise HTTPException(status_code=404, detail=f"Student not found: {enrollment_no}")

        # Ensure predictions are present; if not, compute them for just this record
        if 'final_phase' not in student_df.columns or 'override_reason' not in student_df.columns:
            predicted_df = add_predictions_to_dataset(student_df, ml_model, ml_scaler)
        else:
            predicted_df = student_df
        student_row = predicted_df.iloc[0]
        
        # Convert to response format
        cleaned_student = {
            "student_id": str(student_row.get('enrollment_no', '')),
            "enrollment_no": str(student_row.get('enrollment_no', '')),
            "name": generate_student_name(str(student_row.get('enrollment_no', ''))),
            "department": str(student_row.get('department', '')) if pd.notna(student_row.get('department')) else None,
            "attendance": float(student_row.get('attendance', 0)),
            "cgpa": float(student_row.get('cgpa', 0)),
            "backlogs": int(student_row.get('backlogs', 0)),
            "marks_10th": float(student_row.get('marks_10th', 0)),
            "marks_12th": float(student_row.get('marks_12th', 0)),
            "fees_flag": int(student_row.get('fees_flag', 0)),  # 0 = paid, 1 = unpaid  
            "suspension_flag": int(student_row.get('suspension_flag', 0)),  # 0 = no suspension, 1 = suspended
            "gender": str(student_row.get('gender', 'M')),
            "age_at_enrollment": int(student_row.get('age_at_enrollment', 0)) if pd.notna(student_row.get('age_at_enrollment')) else None,
            "category": str(student_row.get('category', '')) if pd.notna(student_row.get('category')) else None,
            # Prediction results
            "prediction": str(student_row.get('final_phase', 'Green')),
            "final_phase": str(student_row.get('final_phase', 'Green')),
            "model_phase": str(student_row.get('model_phase', 'Green')),
            "risk_label": _convert_phase_to_risk_label(str(student_row.get('final_phase', 'Green'))),
            "override_reason": str(student_row.get('override_reason', student_row.get('red_reason', ''))),
            "ml_probability": float(student_row.get('ml_probability', 0)) if pd.notna(student_row.get('ml_probability')) else None,
            "rule_override": bool(student_row.get('rule_override', False))
        }
        
        # Log the payload for debugging
        logger.info(f"Retrieved student {cleaned_student['enrollment_no']}: fees_flag={cleaned_student['fees_flag']}, "
                   f"suspension_flag={cleaned_student['suspension_flag']}, prediction={cleaned_student['prediction']}")
        
        return cleaned_student
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get student {enrollment_no}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve student: {str(e)}")


@app.post("/simulate", response_model=SimulateResponse, summary="Simulate Dropout Prediction")
async def simulate_dropout_prediction(request: SimulateRequest):
    """
    Simulate dropout prediction for a student with given parameters using comprehensive rules.
    Generates PDF reports for Orange/Red risk levels and sends via email if provided.
    
    Args:
        request: Student parameters for simulation (includes optional email)
        
    Returns:
        Prediction result with phase, reason, probability, and report info
    """
    try:
        # Convert request to dictionary and validate
        student_data = request.dict()
        student_email = student_data.pop('email', None)  # Extract email before validation
        student_data = validate_student_input(student_data)
        
        # Use the improved prediction pipeline
        prediction_result = process_single_prediction(student_data, ml_model, ml_scaler)
        
        # Send notification if student is at Orange or Red risk and capture message
        final_risk_level = prediction_result['final_phase']
        notification_message = send_notification(student_data, final_risk_level)
        
        # Log simulation for debugging
        logger.info(f"Simulation for {student_data.get('enrollment_no', 'anonymous')}: "
                   f"fees_flag={student_data.get('fees_flag', 0)}, "
                   f"suspension_flag={student_data.get('suspension_flag', 0)}, "
                   f"model_phase={prediction_result['model_phase']}, "
                   f"final_phase={prediction_result['final_phase']}")

        # Initialize report fields
        report_id = None
        report_generated = False
        email_sent = False
        
        # Generate PDF report for Orange or Red risk levels
        if final_risk_level in ['Orange', 'Red']:
            try:
                # Import report and email services
                from services.report_service import generate_all_reports
                from services.email_service import send_report_email
                
                # Generate unique simulation ID
                import uuid
                report_id = f"sim_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                
                # Generate reports in all three languages
                logger.info(f"Generating PDF reports for {report_id}...")
                report_paths = generate_all_reports(
                    simulation_data=student_data,
                    prediction_result=prediction_result,
                    simulation_id=report_id
                )
                
                if report_paths:
                    report_generated = True
                    logger.info(f"Generated {len(report_paths)} report(s) for {report_id}")
                    
                    # Send email if email address was provided
                    if student_email and '@' in student_email:
                        logger.info(f"Sending report email to {student_email}...")
                        student_name = student_data.get('enrollment_no', 'Student')
                        email_sent = await send_report_email(
                            recipient_email=student_email,
                            student_name=student_name,
                            risk_level=final_risk_level,
                            report_paths=report_paths,
                            simulation_id=report_id
                        )
                        
                        if email_sent:
                            logger.info(f"Report email sent successfully to {student_email}")
                        else:
                            logger.warning(f"Failed to send report email to {student_email}")
                    else:
                        logger.info("No email provided, report available for download only")
                        
            except Exception as report_error:
                logger.error(f"Error generating/sending report: {report_error}")
                # Don't fail the entire request if report generation fails
                report_generated = False
                email_sent = False

        # Prepare response
        response = SimulateResponse(
            enrollment_no=request.enrollment_no if hasattr(request, 'enrollment_no') else None,
            model_phase=prediction_result['model_phase'],
            final_phase=prediction_result['final_phase'],
            override_reason=prediction_result['red_reason'],
            ml_probability=prediction_result['ml_probability'],
            rule_override=prediction_result['rule_override'],
            notification_message=notification_message,
            report_id=report_id,
            report_generated=report_generated,
            email_sent=email_sent
        )
        
        # Push latest simulation data to Firebase for judges to see
        if is_firebase_initialized():
            try:
                firebase_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "latest_simulation": {
                        "enrollment_no": request.enrollment_no if hasattr(request, 'enrollment_no') else "anonymous",
                        "final_phase": prediction_result['final_phase'],
                        "risk_level": _convert_phase_to_risk_label(prediction_result['final_phase']),
                        "ml_probability": prediction_result['ml_probability'],
                        "rule_override": prediction_result['rule_override'],
                        "report_id": report_id,
                        "report_generated": report_generated
                    },
                    "backend_status": "active"
                }
                update_latest_data(firebase_data)
                logger.info("Simulation data pushed to Firebase successfully")
            except Exception as fb_error:
                logger.warning(f"Failed to push to Firebase: {fb_error}")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/report/{simulation_id}", summary="Download Simulation Report")
async def get_report(
    simulation_id: str,
    language: str = Query("en", description="Report language: en, hi, or rj")
):
    """
    Download a generated PDF report for a simulation.
    
    Args:
        simulation_id: Unique simulation identifier
        language: Report language (en=English, hi=Hindi, rj=Rajasthani)
        
    Returns:
        PDF file for download
        
    Raises:
        HTTPException: If report not found
    """
    try:
        # Validate language parameter
        if language not in ['en', 'hi', 'rj']:
            raise HTTPException(status_code=400, detail="Invalid language. Must be en, hi, or rj")
        
        # Construct report path
        reports_dir = Path(__file__).parent / "reports" / simulation_id
        report_file = reports_dir / f"report_{language}.pdf"
        
        # Check if report exists
        if not report_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"Report not found for simulation {simulation_id} in language {language}"
            )
        
        # Map language codes to readable names
        language_names = {"en": "English", "hi": "Hindi", "rj": "Rajasthani"}
        language_name = language_names.get(language, language)
        
        # Return PDF file
        return FileResponse(
            path=str(report_file),
            media_type="application/pdf",
            filename=f"dropout_risk_report_{language}_{simulation_id}.pdf",
            headers={
                "Content-Disposition": f'attachment; filename="dropout_risk_report_{language_name}_{simulation_id}.pdf"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve report: {str(e)}")


@app.get("/report/{simulation_id}/all", summary="Download All Reports (Zipped)")
async def get_all_reports(simulation_id: str):
    """
    Download all three language reports as a zip file.
    
    Args:
        simulation_id: Unique simulation identifier
        
    Returns:
        ZIP file containing all three reports
        
    Raises:
        HTTPException: If reports not found
    """
    try:
        import zipfile
        import tempfile
        
        # Construct reports directory path
        reports_dir = Path(__file__).parent / "reports" / simulation_id
        
        if not reports_dir.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"No reports found for simulation {simulation_id}"
            )
        
        # Create temporary zip file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
            for language in ['en', 'hi', 'rj']:
                report_file = reports_dir / f"report_{language}.pdf"
                if report_file.exists():
                    zipf.write(report_file, arcname=f"report_{language}.pdf")
        
        # Return zip file
        return FileResponse(
            path=temp_zip.name,
            media_type="application/zip",
            filename=f"dropout_risk_reports_{simulation_id}.zip",
            headers={
                "Content-Disposition": f'attachment; filename="dropout_risk_reports_{simulation_id}.zip"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating zip file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create zip file: {str(e)}")


@app.get("/simulations", response_model=SimulationListResponse, summary="Get All Past Simulations")
async def get_simulations():
    """
    Retrieve all past simulation results from Firebase.
    
    Returns:
        List of all simulation records
        
    Raises:
        HTTPException: If Firebase query fails
    """
    try:
        # TODO: Implement Firebase-based simulation history retrieval
        # For now, return empty list as simulations are stored in Firebase /latestData
        logger.info("Simulations endpoint called - Firebase stores latest data only")
        return SimulationListResponse(simulations=[])
        
    except Exception as e:
        logger.error(f"Failed to retrieve simulations: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/students/search", summary="Search Students")
async def search_students(
    query: Optional[str] = None,
    enrollment: Optional[str] = None,
    name: Optional[str] = None,
    department: Optional[str] = None,
    branch: Optional[str] = None,
    year: Optional[int] = None,
    risk_level: Optional[str] = None,
    mentor_id: Optional[str] = None,
    counselor_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Flexible search across student records
    
    Supports:
    - Free text query
    - Field-specific filters
    - Pagination
    """
    try:
        from services.firebase_service import get_firestore_db
        
        db = get_firestore_db()
        if not db:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Start with all students
        query_ref = db.collection('students')
        
        # Apply filters
        if enrollment:
            query_ref = query_ref.where('enrollment_no', '==', enrollment)
        
        if department:
            query_ref = query_ref.where('department', '==', department)
        
        if branch:
            query_ref = query_ref.where('branch', '==', branch)
        
        if year:
            query_ref = query_ref.where('year', '==', year)
        
        if risk_level:
            query_ref = query_ref.where('final_phase', '==', risk_level)
        
        if mentor_id:
            query_ref = query_ref.where('mentor_id', '==', mentor_id)
        
        if counselor_id:
            query_ref = query_ref.where('counselor_id', '==', counselor_id)
        
        # Execute query
        results = query_ref.limit(limit).offset(offset).stream()
        
        students = []
        for doc in results:
            student_data = doc.to_dict()
            student_data['id'] = doc.id
            
            # Apply free text search if provided
            if query:
                search_term = query.lower()
                searchable_text = f"{student_data.get('name', '')} {student_data.get('enrollment_no', '')} {student_data.get('email', '')}".lower()
                if search_term not in searchable_text:
                    continue
            
            # Filter by name if provided
            if name:
                if name.lower() not in student_data.get('name', '').lower():
                    continue
            
            # Filter by tags if provided
            if tags:
                student_tags = student_data.get('tags', [])
                if not any(tag in student_tags for tag in tags):
                    continue
            
            students.append(student_data)
        
        return {
            "total": len(students),
            "students": students,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Student search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.post("/api/notify/one-click", summary="Send One-Click Notifications")
async def send_one_click_notification(
    sender_id: str,
    recipient_ids: List[str],
    message: str,
    language: str = "en",
    channels: List[str] = ["inapp", "email"],
    template_id: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Send bulk notifications from mentor to students
    
    Supports:
    - Multiple recipients
    - Multiple channels (in-app, email)
    - Template-based or custom messages
    - Background processing
    """
    try:
        from services.notification_service import send_one_click_message
        from services.i18n_service import get_translation
        
        # If template_id provided, load template
        final_message = message
        if template_id:
            final_message = get_translation(f"template_{template_id}", language)
        
        # Send notifications in background if available
        if background_tasks:
            background_tasks.add_task(
                send_one_click_message,
                sender_id=sender_id,
                recipient_ids=recipient_ids,
                message=final_message,
                language=language,
                channels=channels
            )
        else:
            # Send synchronously
            result = await send_one_click_message(
                sender_id=sender_id,
                recipient_ids=recipient_ids,
                message=final_message,
                language=language,
                channels=channels
            )
            
            if result.get("failed", 0) > 0:
                logger.warning(f"Some messages failed: {result}")
        
        return {
            "status": "success",
            "message": get_translation("mentor_one_click_sent", language, count=len(recipient_ids)),
            "recipient_count": len(recipient_ids)
        }
        
    except Exception as e:
        logger.error(f"One-click notification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/merge", response_model=MergeResponse, summary="Merge Distributed Datasets")
async def merge_datasets():
    """
    Run the integration pipeline to merge distributed datasets.
    
    This endpoint merges all distributed CSV files (academics, finance, demographics, 
    discipline, family, contact) into a single dataset and saves it as merged_dataset.csv.
    
    Returns:
        Merge results with dataset summary and preview
        
    Raises:
        HTTPException: If merge operation fails
    """
    try:
        logger.info("🚀 Starting dataset merge via API endpoint")
        
        # Import locally to avoid startup issues
        from models.integration_pipeline import run_integration_pipeline
        result = run_integration_pipeline()
        
        return MergeResponse(
            status=result["status"],
            total_students=result["total_students"],
            total_columns=result["total_columns"],
            output_path=result["output_path"],
            preview=result["preview"],
            columns=result["columns"]
        )
        
    except Exception as e:
        logger.error(f"Merge endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Merge operation failed: {str(e)}")


@app.get("/predict", response_model=PredictResponse, summary="Run Prediction Pipeline")
async def predict_students():
    """
    Run the unified prediction pipeline to generate dropout predictions.
    
    This endpoint:
    1. Uses the unified prediction system from utils.py
    2. Loads the merged dataset and applies ML model + rule overrides
    3. Saves results to merged_with_predictions.csv
    
    Returns:
        Prediction results with phase distribution and preview
        
    Raises:
        HTTPException: If prediction operation fails
    """
    try:
        logger.info("🤖 Starting unified prediction pipeline via API endpoint")
        
        # Use the unified batch prediction system
        results = run_batch_prediction_pipeline()
        
        return PredictResponse(
            status="success",
            total_students=results["total_students"],
            phase_distribution=results["final_phase_distribution"],
            model_phase_distribution=results["ml_phase_distribution"],
            red_zone_overrides=results["rule_overrides"],
            ml_model_used=results["ml_model_used"],
            output_path=results["output_path"],
            preview=results["preview"]
        )
        
    except Exception as e:
        logger.error(f"Unified prediction endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction operation failed: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse, summary="Get Model Metrics")
async def get_metrics():
    """
    Get ML model performance metrics and dataset information.
    
    This endpoint returns information about the loaded ML model including:
    - Model performance metrics (accuracy, precision, recall, F1)
    - Feature importance scores
    - Dataset size information
    - Model configuration details
    
    Returns:
        Model metrics and performance information
    """
    try:
        global ml_model, ml_metrics, model_loaded
        
        if not model_loaded or ml_model is None:
            return MetricsResponse(
                model_loaded=False,
                model_metrics=None,
                dataset_size=None,
                feature_importance=None,
                model_info={"message": "No ML model loaded"}
            )
        
        # Get dataset size from merged dataset if available
        dataset_size = None
        try:
            if Path(DATA_FILE_PATH).exists():
                df = pd.read_csv(DATA_FILE_PATH)
                dataset_size = len(df)
        except Exception as e:
            logger.warning(f"Could not read dataset for size info: {e}")
        
        # Extract feature importance if available
        feature_importance = None
        if hasattr(ml_model, 'feature_importances_'):
            try:
                # Get feature names if available
                feature_names = getattr(ml_model, 'feature_names_', None)
                if feature_names is None:
                    feature_names = [f"feature_{i}" for i in range(len(ml_model.feature_importances_))]
                
                feature_importance = dict(zip(feature_names, ml_model.feature_importances_.tolist()))
            except Exception as e:
                logger.warning(f"Could not extract feature importance: {e}")
        
        # Model configuration info
        model_info = {
            "model_type": type(ml_model).__name__,
            "model_loaded": True,
            "has_predict_proba": hasattr(ml_model, 'predict_proba'),
            "has_feature_importance": hasattr(ml_model, 'feature_importances_')
        }
        
        return MetricsResponse(
            model_loaded=model_loaded,
            model_metrics=ml_metrics,
            dataset_size=dataset_size,
            feature_importance=feature_importance,
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@app.post("/train", response_model=TrainingResponse, summary="Train ML Model")
async def train_model(token: str = Query(..., description="Security token (use 'devtoken' for development)")):
    """
    Train ML model using available training data.
    
    This endpoint triggers the training pipeline programmatically and returns training metrics.
    Requires a security token for access control.
    
    Args:
        token: Security token (must be 'devtoken' for this prototype)
        
    Returns:
        Training results including success status, metrics, and model paths
        
    Raises:
        HTTPException: If unauthorized or training fails
    """
    # Simple token-based security for prototype
    if token != "devtoken":
        raise HTTPException(status_code=401, detail="Invalid token. Use 'devtoken' for development.")
    
    try:
        logger.info("Training endpoint called but train_model not available")
        return TrainingResponse(
            success=False,
            message="Training functionality not implemented in this deployment",
            metrics=None,
            model_path=None
        )
            
    except Exception as e:
        logger.error(f"Training endpoint failed: {e}")
        return TrainingResponse(
            success=False,
            message=f"Training failed with error: {str(e)}",
            metrics=None,
            model_path=None
        )


@app.post("/api/admin/refresh-firebase", summary="Manually Refresh All Firebase Data")
async def refresh_firebase_data():
    """
    Manually trigger comprehensive Firebase data refresh.
    - Updates all student predictions
    - Preserves comprehensive fields (hometown, family, SGPA, etc.)
    - Same as automatic 5-hour update
    
    Useful for:
    - Forcing immediate update after data changes
    - Testing Firebase population
    - Recovery after errors
    
    Returns:
        Status of Firebase refresh operation with update statistics
    """
    try:
        if not is_firebase_initialized():
            raise HTTPException(
                status_code=503,
                detail="Firebase not initialized. Configure environment variables."
            )
        
        logger.info("🔄 Manual Firebase refresh triggered via API")
        
        # Run the same population logic as startup
        await populate_firebase_on_startup()
        
        # Get updated count
        from app.services.firebase_service import get_student_count
        student_count = get_student_count()
        
        return {
            "status": "success",
            "message": "Firebase data refreshed successfully",
            "students_in_firebase": student_count,
            "timestamp": datetime.utcnow().isoformat(),
            "update_type": "comprehensive",
            "fields_per_student": 42,
            "note": "All predictions updated, comprehensive fields preserved"
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh Firebase data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Firebase refresh failed: {str(e)}"
        )


@app.post("/firebase/update", summary="Update Firebase with Latest Data")
async def update_firebase_data(data: Optional[Dict[str, Any]] = None):
    """
    Manually trigger Firebase update with latest prediction data.
    This ensures judges can always see the latest results even when backend sleeps.
    
    Args:
        data: Optional custom data to push. If not provided, uses sample data.
        
    Returns:
        Status of Firebase update operation
    """
    try:
        if not is_firebase_initialized():
            return {
                "status": "warning",
                "message": "Firebase not initialized. Configure environment variables on Render.",
                "firebase_configured": False
            }
        
        # If no data provided, create sample summary data
        if data is None:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Backend pipeline completed",
                "status": "active",
                "last_simulation": "awaiting data"
            }
        
        success = update_latest_data(data)
        
        if success:
            return {
                "status": "success",
                "message": "Data successfully pushed to Firebase",
                "firebase_configured": True,
                "data": data
            }
        else:
            return {
                "status": "error",
                "message": "Failed to push data to Firebase",
                "firebase_configured": True
            }
            
    except Exception as e:
        logger.error(f"Firebase update endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=f"Firebase update failed: {str(e)}")


@app.get("/firebase/status", summary="Check Firebase Connection Status")
async def firebase_status():
    """
    Check if Firebase is properly initialized and connected.
    
    Returns:
        Firebase initialization status and configuration check
    """
    try:
        initialized = is_firebase_initialized()
        
        # Check environment variables
        env_vars_configured = all([
            os.getenv("FIREBASE_PROJECT_ID"),
            os.getenv("FIREBASE_PRIVATE_KEY"),
            os.getenv("FIREBASE_CLIENT_EMAIL"),
            os.getenv("FIREBASE_DATABASE_URL")
        ])
        
        return {
            "firebase_initialized": initialized,
            "environment_vars_configured": env_vars_configured,
            "project_id": os.getenv("FIREBASE_PROJECT_ID", "not_set"),
            "database_url": os.getenv("FIREBASE_DATABASE_URL", "not_set"),
            "status": "connected" if initialized else "not_configured"
        }
        
    except Exception as e:
        logger.error(f"Firebase status check failed: {e}")
        return {
            "firebase_initialized": False,
            "environment_vars_configured": False,
            "error": str(e),
            "status": "error"
        }


# ============================================================
# DASHBOARD REDESIGN API ENDPOINTS
# ============================================================

@app.get("/api/departments", summary="Get All Departments with Summary")
async def get_departments():
    """
    Get all departments with summary statistics.
    
    Returns:
        List of departments with:
        - Department ID and name
        - Total student count
        - Risk distribution (critical, at_risk, monitor, safe)
        - Average CGPA and attendance
        - Performance score
    """
    try:
        df = load_student_data()
        
        # Normalize department names
        df['department_norm'] = df['department'].str.strip().str.upper()
        
        departments = []
        for dept in df['department_norm'].unique():
            if pd.isna(dept) or dept == '':
                continue
                
            dept_df = df[df['department_norm'] == dept]
            
            # Calculate risk distribution
            phase_counts = dept_df['final_phase'].value_counts().to_dict()
            critical = phase_counts.get('Red', 0)
            at_risk = phase_counts.get('Orange', 0)
            monitor = phase_counts.get('Yellow', 0)
            safe = phase_counts.get('Green', 0)
            
            # Calculate averages
            avg_cgpa = float(dept_df['cgpa'].mean()) if 'cgpa' in dept_df.columns else 0.0
            avg_attendance = float(dept_df['attendance'].mean()) if 'attendance' in dept_df.columns else 0.0
            
            # Calculate performance score (0-100)
            # Based on: 50% safe students + 30% avg CGPA/10 + 20% avg attendance/100
            total_students = len(dept_df)
            safe_pct = (safe / total_students * 100) if total_students > 0 else 0
            performance_score = (
                (safe_pct * 0.5) +
                ((avg_cgpa / 10) * 100 * 0.3) +
                (avg_attendance * 0.2)
            )
            
            # Map CSV department names to frontend IDs and display names
            id_mapping = {
                'BBA': 'bba',
                'CS': 'bsc',
                'AGRI': 'bsc_agriculture',
                'BTECH': 'btech'
            }
            display_names = {
                'BBA': 'BBA',
                'CS': 'BSc',
                'AGRI': 'BSc Agriculture',
                'BTECH': 'BTech'
            }
            
            departments.append({
                "id": id_mapping.get(dept, dept.replace(' ', '_').lower()),
                "name": display_names.get(dept, dept.title()),
                "studentCount": int(total_students),
                "riskDistribution": {
                    "critical": int(critical),
                    "atRisk": int(at_risk),
                    "monitor": int(monitor),
                    "safe": int(safe)
                },
                "avgCgpa": round(avg_cgpa, 2),
                "avgAttendance": round(avg_attendance, 1),
                "performanceScore": round(performance_score, 1)
            })
        
        return {
            "success": True,
            "departments": sorted(departments, key=lambda x: x['name'])
        }
        
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/{dept_id}", summary="Get Department Details with Year Breakdown")
async def get_department_detail(dept_id: str):
    """
    Get detailed information for a specific department including year-wise breakdown.
    
    Args:
        dept_id: Department ID (e.g., 'btech', 'bba', 'bsc', 'bsc_agriculture')
        
    Returns:
        Department details with year-wise statistics and analytics data
    """
    try:
        df = load_student_data()
        
        # Map frontend IDs to CSV department values
        dept_mapping = {
            'bba': 'BBA',
            'bsc': 'CS',
            'bsc_agriculture': 'AGRI',
            'btech': 'BTECH'
        }
        
        csv_dept_name = dept_mapping.get(dept_id.lower())
        if not csv_dept_name:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        
        # Filter by department using CSV values
        df['department_norm'] = df['department'].str.strip().str.upper()
        dept_df = df[df['department_norm'] == csv_dept_name]
        
        if dept_df.empty:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        
        # Year-wise breakdown
        years_data = []
        for year in sorted(dept_df['year_level'].dropna().unique()):
            year_df = dept_df[dept_df['year_level'] == year]
            
            phase_counts = year_df['final_phase'].value_counts().to_dict()
            
            years_data.append({
                "year": int(year),
                "studentCount": int(len(year_df)),
                "avgCgpa": round(float(year_df['cgpa'].mean()), 2),
                "avgAttendance": round(float(year_df['attendance'].mean()), 1),
                "riskDistribution": {
                    "critical": int(phase_counts.get('Red', 0)),
                    "atRisk": int(phase_counts.get('Orange', 0)),
                    "monitor": int(phase_counts.get('Yellow', 0)),
                    "safe": int(phase_counts.get('Green', 0))
                }
            })
        
        # Department-level analytics
        phase_counts = dept_df['final_phase'].value_counts().to_dict()
        
        # CGPA distribution
        cgpa_bins = [0, 4, 5, 6, 7, 8, 9, 10]
        cgpa_labels = ['<4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
        dept_df['cgpa_range'] = pd.cut(dept_df['cgpa'], bins=cgpa_bins, labels=cgpa_labels, include_lowest=True)
        cgpa_distribution = dept_df['cgpa_range'].value_counts().to_dict()
        
        # Attendance distribution
        attendance_bins = [0, 30, 50, 75, 90, 100]
        attendance_labels = ['<30%', '30-50%', '50-75%', '75-90%', '90-100%']
        dept_df['attendance_range'] = pd.cut(dept_df['attendance'], bins=attendance_bins, labels=attendance_labels, include_lowest=True)
        attendance_distribution = dept_df['attendance_range'].value_counts().to_dict()
        
        # Display name mapping
        display_names = {
            'BBA': 'BBA',
            'CS': 'BSc',
            'AGRI': 'BSc Agriculture',
            'BTECH': 'BTech'
        }
        
        return {
            "success": True,
            "department": {
                "id": dept_id,
                "name": display_names.get(csv_dept_name, csv_dept_name),
                "totalStudents": int(len(dept_df)),
                "avgCgpa": round(float(dept_df['cgpa'].mean()), 2),
                "avgAttendance": round(float(dept_df['attendance'].mean()), 1),
                "riskDistribution": {
                    "critical": int(phase_counts.get('Red', 0)),
                    "atRisk": int(phase_counts.get('Orange', 0)),
                    "monitor": int(phase_counts.get('Yellow', 0)),
                    "safe": int(phase_counts.get('Green', 0))
                }
            },
            "years": years_data,
            "analytics": {
                "cgpaDistribution": [{"range": k, "count": int(v)} for k, v in cgpa_distribution.items()],
                "attendanceDistribution": [{"range": k, "count": int(v)} for k, v in attendance_distribution.items()],
                "yearComparison": [
                    {
                        "year": year["year"],
                        "avgCgpa": year["avgCgpa"],
                        "avgAttendance": year["avgAttendance"],
                        "atRiskCount": year["riskDistribution"]["critical"] + year["riskDistribution"]["atRisk"]
                    }
                    for year in years_data
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching department details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/{dept_id}/years/{year_no}", summary="Get Year Details with Section Breakdown")
async def get_year_detail(dept_id: str, year_no: int):
    """
    Get detailed information for a specific year within a department.
    
    Args:
        dept_id: Department ID
        year_no: Year number (1-4)
        
    Returns:
        Year details with section breakdown, analytics, and student list
    """
    try:
        df = load_student_data()
        
        # Map frontend IDs to CSV department values
        dept_mapping = {
            'bba': 'BBA',
            'bsc': 'CS',
            'bsc_agriculture': 'AGRI',
            'btech': 'BTECH'
        }
        
        csv_dept_name = dept_mapping.get(dept_id.lower())
        if not csv_dept_name:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        
        # Filter by department and year
        df['department_norm'] = df['department'].str.strip().str.upper()
        year_df = df[(df['department_norm'] == csv_dept_name) & (df['year_level'] == year_no)]
        
        if year_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {dept_id} Year {year_no}")
        
        # Section breakdown
        sections_data = []
        if 'section' in year_df.columns:
            for section in sorted(year_df['section'].dropna().unique()):
                section_df = year_df[year_df['section'] == section]
                phase_counts = section_df['final_phase'].value_counts().to_dict()
                
                sections_data.append({
                    "name": str(section),
                    "studentCount": int(len(section_df)),
                    "avgCgpa": round(float(section_df['cgpa'].mean()), 2),
                    "avgAttendance": round(float(section_df['attendance'].mean()), 1),
                    "riskDistribution": {
                        "critical": int(phase_counts.get('Red', 0)),
                        "atRisk": int(phase_counts.get('Orange', 0)),
                        "monitor": int(phase_counts.get('Yellow', 0)),
                        "safe": int(phase_counts.get('Green', 0))
                    }
                })
        
        # Year-level analytics
        phase_counts = year_df['final_phase'].value_counts().to_dict()
        
        # CGPA histogram data
        cgpa_bins = [0, 4, 5, 6, 7, 8, 9, 10]
        cgpa_labels = ['<4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
        year_df['cgpa_range'] = pd.cut(year_df['cgpa'], bins=cgpa_bins, labels=cgpa_labels, include_lowest=True)
        cgpa_histogram = year_df['cgpa_range'].value_counts().sort_index().to_dict()
        
        # Attendance trend (by risk phase)
        attendance_by_phase = {}
        for phase in ['Green', 'Yellow', 'Orange', 'Red']:
            phase_data = year_df[year_df['final_phase'] == phase]
            if not phase_data.empty:
                attendance_by_phase[phase] = round(float(phase_data['attendance'].mean()), 1)
        
        # Display name mapping
        display_names = {
            'BBA': 'BBA',
            'CS': 'BSc',
            'AGRI': 'BSc Agriculture',
            'BTECH': 'BTech'
        }
        
        return {
            "success": True,
            "year": {
                "department": display_names.get(csv_dept_name, csv_dept_name),
                "year": year_no,
                "totalStudents": int(len(year_df)),
                "avgCgpa": round(float(year_df['cgpa'].mean()), 2),
                "avgAttendance": round(float(year_df['attendance'].mean()), 1),
                "avgBacklogs": round(float(year_df['backlogs'].mean()), 1) if 'backlogs' in year_df.columns else 0,
                "riskDistribution": {
                    "critical": int(phase_counts.get('Red', 0)),
                    "atRisk": int(phase_counts.get('Orange', 0)),
                    "monitor": int(phase_counts.get('Yellow', 0)),
                    "safe": int(phase_counts.get('Green', 0))
                }
            },
            "sections": sections_data,
            "analytics": {
                "cgpaHistogram": [{"range": k, "count": int(v)} for k, v in cgpa_histogram.items()],
                "attendanceByPhase": attendance_by_phase,
                "riskTrend": {
                    "labels": ["Safe", "Monitor", "At Risk", "Critical"],
                    "values": [
                        phase_counts.get('Green', 0),
                        phase_counts.get('Yellow', 0),
                        phase_counts.get('Orange', 0),
                        phase_counts.get('Red', 0)
                    ]
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching year details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/{dept_id}/years/{year_no}/students", summary="Get Student List for Year")
async def get_year_students(
    dept_id: str, 
    year_no: int,
    section: Optional[str] = Query(None, description="Filter by section"),
    risk: Optional[str] = Query(None, description="Filter by risk phase (Red, Orange, Yellow, Green)"),
    search: Optional[str] = Query(None, description="Search by name or enrollment number")
):
    """
    Get list of students for a specific year with optional filters.
    
    Args:
        dept_id: Department ID
        year_no: Year number
        section: Optional section filter
        risk: Optional risk phase filter
        search: Optional search term
        
    Returns:
        Filtered list of students with compact data
    """
    try:
        df = load_student_data()
        
        # Map frontend IDs to CSV department values
        dept_mapping = {
            'bba': 'BBA',
            'bsc': 'CS',
            'bsc_agriculture': 'AGRI',
            'btech': 'BTECH'
        }
        
        csv_dept_name = dept_mapping.get(dept_id.lower())
        if not csv_dept_name:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        
        # Filter by department and year
        df['department_norm'] = df['department'].str.strip().str.upper()
        students_df = df[(df['department_norm'] == csv_dept_name) & (df['year_level'] == year_no)]
        
        # Apply filters
        if section:
            students_df = students_df[students_df['section'] == section]
        
        if risk:
            students_df = students_df[students_df['final_phase'] == risk]
        
        if search:
            search_term = search.lower()
            students_df = students_df[
                students_df['enrollment_no'].astype(str).str.lower().str.contains(search_term) |
                students_df['student_name'].astype(str).str.lower().str.contains(search_term)
            ]
        
        # Convert to compact format
        students = []
        for _, row in students_df.iterrows():
            students.append({
                "enrollmentNo": str(row.get('enrollment_no', '')),
                "name": str(row.get('student_name', 'Unknown')),
                "section": str(row.get('section', '')) if pd.notna(row.get('section')) else None,
                "cgpa": round(float(row.get('cgpa', 0)), 2),
                "attendance": round(float(row.get('attendance', 0)), 1),
                "backlogs": int(row.get('backlogs', 0)),
                "riskPhase": str(row.get('final_phase', 'Unknown')),
                "status": "Active"  # Can be enhanced with actual status logic
            })
        
        # Display name mapping
        display_names = {
            'BBA': 'BBA',
            'CS': 'BSc',
            'AGRI': 'BSc Agriculture',
            'BTECH': 'BTech'
        }
        
        return {
            "success": True,
            "department": display_names.get(csv_dept_name, csv_dept_name),
            "year": year_no,
            "totalCount": len(students),
            "filters": {
                "section": section,
                "risk": risk,
                "search": search
            },
            "students": students
        }
        
    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/departments/{dept_id}/years/{year_no}/sections", summary="Get Section Breakdown for Year")
async def get_year_sections(dept_id: str, year_no: int):
    """
    Get detailed section breakdown for a specific year.
    
    Args:
        dept_id: Department ID
        year_no: Year number
        
    Returns:
        List of sections with statistics
    """
    try:
        df = load_student_data()
        
        # Map frontend IDs to CSV department values
        dept_mapping = {
            'bba': 'BBA',
            'bsc': 'CS',
            'bsc_agriculture': 'AGRI',
            'btech': 'BTECH'
        }
        
        csv_dept_name = dept_mapping.get(dept_id.lower())
        if not csv_dept_name:
            raise HTTPException(status_code=404, detail=f"Department not found: {dept_id}")
        
        # Filter by department and year
        df['department_norm'] = df['department'].str.strip().str.upper()
        year_df = df[(df['department_norm'] == csv_dept_name) & (df['year_level'] == year_no)]
        
        if year_df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {dept_id} Year {year_no}")
        
        sections = []
        if 'section' in year_df.columns:
            for section in sorted(year_df['section'].dropna().unique()):
                section_df = year_df[year_df['section'] == section]
                phase_counts = section_df['final_phase'].value_counts().to_dict()
                
                sections.append({
                    "name": str(section),
                    "studentCount": int(len(section_df)),
                    "avgCgpa": round(float(section_df['cgpa'].mean()), 2),
                    "avgAttendance": round(float(section_df['attendance'].mean()), 1),
                    "avgBacklogs": round(float(section_df['backlogs'].mean()), 1) if 'backlogs' in section_df.columns else 0,
                    "riskDistribution": {
                        "critical": int(phase_counts.get('Red', 0)),
                        "atRisk": int(phase_counts.get('Orange', 0)),
                        "monitor": int(phase_counts.get('Yellow', 0)),
                        "safe": int(phase_counts.get('Green', 0))
                    },
                    "topPerformers": int(len(section_df[section_df['cgpa'] >= 8])),
                    "needsAttention": int(len(section_df[section_df['attendance'] < 75]))
                })
        
        # Display name mapping
        display_names = {
            'BBA': 'BBA',
            'CS': 'BSc',
            'AGRI': 'BSc Agriculture',
            'BTECH': 'BTech'
        }
        
        return {
            "success": True,
            "department": display_names.get(csv_dept_name, csv_dept_name),
            "year": year_no,
            "sections": sections
        }
        
    except Exception as e:
        logger.error(f"Error fetching sections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Development server entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        timeout_keep_alive=75,  # Keep connections alive for 75 seconds
        timeout_graceful_shutdown=30  # Allow 30s for graceful shutdown
    )
