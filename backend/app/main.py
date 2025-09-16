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
import json
import logging
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure
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
        run_batch_prediction_pipeline
    )
except ImportError:
    # Fall back to app.utils for deployed environment
    from app.utils import (
        process_single_prediction, 
        add_predictions_to_dataset,
        validate_student_input,
        predict_with_unified_system,
        run_batch_prediction_pipeline
    )

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

# Environment configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://wannabe:gummy(*_*)@ai-based-dropout-system.k51tjan.mongodb.net/?retryWrites=true&w=majority&appName=AI-based-dropout-system")
DB_NAME = os.getenv("DB_NAME", "dropout_prediction")

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

# ML Probability Thresholds for Risk Refinement
# These thresholds are conservative to ensure high confidence before overriding rule-based results
ML_HIGH_RISK_THRESHOLD = 0.75  # Override to High Risk if ml_proba >= 0.75
ML_MEDIUM_RISK_THRESHOLD = 0.45  # Override to Medium Risk if ml_proba >= 0.45 (and current is Low)
ML_NO_OVERRIDE_THRESHOLD = 0.30  # Don't override if ml_proba < 0.30 (keep rule-based result)
#
# Threshold Rationale:
# - 0.75: High confidence threshold to avoid false alarms for High Risk classification
# - 0.45: Moderate confidence to elevate Low Risk students who show ML warning signs  
# - 0.30: Low confidence region where rule-based system is preferred over ML uncertainty

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

# MongoDB client initialization
mongo_client = None
database = None

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

class SimulateResponse(BaseModel):
    """Response model for simulation endpoint"""
    enrollment_no: Optional[str] = Field(None, description="Student enrollment number (if provided)")
    model_phase: str = Field(..., description="ML model prediction: Red, Yellow, Orange, or Green")
    final_phase: str = Field(..., description="Final prediction after Red-Zone overrides")
    override_reason: str = Field("", description="Reason for override (if any)")
    ml_probability: Optional[float] = Field(None, description="ML model dropout probability")
    rule_override: bool = Field(False, description="Whether red-zone rules overrode ML prediction")

class SimulationResponse(BaseModel):
    """Response model for simulation endpoint"""
    simulation_id: str = Field(..., description="Unique simulation identifier")
    timestamp: datetime = Field(..., description="Simulation execution timestamp")
    students: List[Dict[str, Any]] = Field(..., description="Processed student records with risk scores and ML probabilities")
    counts: Dict[str, int] = Field(..., description="Risk level distribution")
    log: List[str] = Field(..., description="Risk assessment log for Medium/High risk students")
    model_loaded: bool = Field(..., description="Whether ML model was loaded and used")
    model_metrics: Optional[Dict[str, Any]] = Field(None, description="ML model performance metrics if available")

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


# MongoDB connection management
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

@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection and ML model on startup"""
    global mongo_client, database
    
    # Load ML model
    load_ml_model()
    
    # Connect to MongoDB
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URI)
        # Test connection with timeout
        await mongo_client.admin.command('ping', maxTimeMS=5000)
        database = mongo_client[DB_NAME]
        logger.info(f"Successfully connected to MongoDB: {DB_NAME}")
    except Exception as e:
        logger.warning(f"Failed to connect to MongoDB: {e}")
        logger.info("Continuing without database - using mock simulation IDs")
        mongo_client = None
        database = None

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names and values for consistent processing.
    
    Args:
        df: Raw dataframe from CSV
        
    Returns:
        Normalized dataframe with standardized column names and values
    """
    # Create a copy to avoid modifying original
    normalized_df = df.copy()
    
    # Normalize column names - remove spaces, convert to lowercase
    normalized_df.columns = [col.strip().lower().replace(' ', '_') for col in normalized_df.columns]
    
    # Ensure required columns exist
    required_cols = ['enrollment_no', 'fees_paid', 'gpa', 'marks_10', 'marks_12', 
                    'attendance_percent', 'backlogs', 'suspension']
    missing_cols = [col for col in required_cols if col not in normalized_df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Normalize string values (Y/N fields)
    for col in ['fees_paid', 'suspension']:
        if col in normalized_df.columns:
            normalized_df[col] = normalized_df[col].astype(str).str.upper().str.strip()
    
    # Ensure numeric columns are properly typed
    numeric_cols = ['gpa', 'marks_10', 'marks_12', 'attendance_percent', 'backlogs']
    for col in numeric_cols:
        if col in normalized_df.columns:
            normalized_df[col] = pd.to_numeric(normalized_df[col], errors='coerce')
    
    logger.info(f"Normalized {len(normalized_df)} student records")
    return normalized_df


def compute_ml_proba(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute ML dropout probabilities for students using the trained model.
    
    Args:
        df: Normalized dataframe with student data
        
    Returns:
        Dataframe with additional 'ml_proba' column (float between 0 and 1)
        Returns original df if model not loaded
    """
    global ml_model, ml_scaler, ml_feature_names, model_loaded
    
    if not model_loaded or ml_model is None or ml_scaler is None:
        # No model available - add null column for consistency
        df['ml_proba'] = None
        return df
    
    try:
        # Prepare feature matrix in the same order as training
        df_features = df.copy()
        
        # Create feature flags (same as training script)
        df_features['fees_flag'] = (df_features['fees_paid'] == 'N').astype(int)
        df_features['suspension_flag'] = (df_features['suspension'] == 'Y').astype(int)
        
        # Handle missing values with same defaults as training
        df_features['attendance_percent'].fillna(70.0, inplace=True)
        df_features['gpa'].fillna(5.0, inplace=True)
        df_features['marks_10'].fillna(60.0, inplace=True)
        df_features['marks_12'].fillna(60.0, inplace=True)
        df_features['backlogs'].fillna(0, inplace=True)
        
        # Extract features in exact training order
        X = df_features[ml_feature_names].values
        
        # Scale features
        X_scaled = ml_scaler.transform(X)
        
        # Predict probabilities (probability of dropout = class 1)
        ml_probabilities = ml_model.predict_proba(X_scaled)[:, 1]
        
        # Add to dataframe
        df['ml_proba'] = ml_probabilities
        
        logger.info(f"Computed ML probabilities for {len(df)} students")
        logger.info(f"ML proba range: {ml_probabilities.min():.3f} - {ml_probabilities.max():.3f}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to compute ML probabilities: {e}")
        # Fallback: add null column
        df['ml_proba'] = None
        return df


def apply_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rule-based scoring system to identify students at risk.
    
    Scoring Rules:
    - fees_paid = 'N' → +2 points
    - gpa < 5 → +2 points  
    - marks_10 < 50 → +1 point
    - marks_12 < 50 → +1 point
    - attendance_percent < 70 → +2 points
    - backlogs >= 3 → +2 points
    - suspension = 'Y' → +3 points
    
    Risk Levels:
    - score >= 6 → High Risk
    - score >= 3 → Medium Risk  
    - score < 3 → Low Risk
    
    Args:
        df: Normalized dataframe
        
    Returns:
        Dataframe with risk scores, levels, and reasons
    """
    result_df = df.copy()
    
    # Initialize risk score
    result_df['risk_score'] = 0
    result_df['risk_reasons'] = ''
    
    # Apply scoring rules
    # Rule 1: Fees not paid
    fees_mask = result_df['fees_paid'] == 'N'
    result_df.loc[fees_mask, 'risk_score'] += 2
    result_df.loc[fees_mask, 'risk_reasons'] += 'Fees not paid (+2); '
    
    # Rule 2: Low GPA
    gpa_mask = result_df['gpa'] < 5
    result_df.loc[gpa_mask, 'risk_score'] += 2
    result_df.loc[gpa_mask, 'risk_reasons'] += f'Low GPA < 5 (+2); '
    
    # Rule 3: Low 10th grade marks
    marks10_mask = result_df['marks_10'] < 50
    result_df.loc[marks10_mask, 'risk_score'] += 1
    result_df.loc[marks10_mask, 'risk_reasons'] += 'Low 10th marks < 50% (+1); '
    
    # Rule 4: Low 12th grade marks
    marks12_mask = result_df['marks_12'] < 50
    result_df.loc[marks12_mask, 'risk_score'] += 1
    result_df.loc[marks12_mask, 'risk_reasons'] += 'Low 12th marks < 50% (+1); '
    
    # Rule 5: Poor attendance
    attendance_mask = result_df['attendance_percent'] < 70
    result_df.loc[attendance_mask, 'risk_score'] += 2
    result_df.loc[attendance_mask, 'risk_reasons'] += 'Poor attendance < 70% (+2); '
    
    # Rule 6: Multiple backlogs
    backlogs_mask = result_df['backlogs'] >= 3
    result_df.loc[backlogs_mask, 'risk_score'] += 2
    result_df.loc[backlogs_mask, 'risk_reasons'] += 'Multiple backlogs >= 3 (+2); '
    
    # Rule 7: Suspension
    suspension_mask = result_df['suspension'] == 'Y'
    result_df.loc[suspension_mask, 'risk_score'] += 3
    result_df.loc[suspension_mask, 'risk_reasons'] += 'Previous suspension (+3); '
    
    # Determine risk levels based on rule scores
    def get_risk_level(score):
        if score >= 6:
            return "High Risk"
        elif score >= 3:
            return "Medium Risk"
        else:
            return "Low Risk"
    
    result_df['risk_level'] = result_df['risk_score'].apply(get_risk_level)
    result_df['rule_based_risk'] = result_df['risk_level'].copy()  # Store original rule-based result
    
    # ML-based risk refinement (if ML model is available)
    if 'ml_proba' in result_df.columns and result_df['ml_proba'].notna().any():
        logger.info("Applying ML-based risk refinement...")
        
        ml_overrides = 0
        for idx, row in result_df.iterrows():
            if pd.isna(row['ml_proba']):
                continue
                
            ml_proba = row['ml_proba']
            current_risk = row['risk_level']
            original_risk = current_risk
            
            # Apply ML threshold-based refinement
            if ml_proba >= ML_HIGH_RISK_THRESHOLD:
                # High confidence → override to High Risk
                result_df.at[idx, 'risk_level'] = 'High Risk'
                if original_risk != 'High Risk':
                    result_df.at[idx, 'risk_reasons'] += f' [ML Override: High confidence dropout risk (p={ml_proba:.3f})]'
                    ml_overrides += 1
                    
            elif ml_proba >= ML_MEDIUM_RISK_THRESHOLD and current_risk == 'Low Risk':
                # Medium confidence → upgrade Low Risk to Medium Risk
                result_df.at[idx, 'risk_level'] = 'Medium Risk'
                result_df.at[idx, 'risk_reasons'] += f' [ML Upgrade: Moderate dropout risk detected (p={ml_proba:.3f})]'
                ml_overrides += 1
                
            elif ml_proba < ML_NO_OVERRIDE_THRESHOLD:
                # Low ML confidence → keep rule-based result (no override)
                pass  # No change needed
        
        if ml_overrides > 0:
            logger.info(f"ML model refined {ml_overrides} risk assessments")
        else:
            logger.info("No ML refinements applied (all probabilities within rule-based agreement)")
    
    # Clean up risk reasons (remove trailing semicolon and space)
    result_df['risk_reasons'] = result_df['risk_reasons'].str.rstrip('; ')
    result_df.loc[result_df['risk_reasons'] == '', 'risk_reasons'] = 'No significant risk factors identified'
    
    logger.info(f"Applied risk scoring rules to {len(result_df)} students")
    return result_df


async def save_to_mongo(simulation_data: dict) -> str:
    """
    Save simulation results to MongoDB.
    
    Args:
        simulation_data: Dictionary containing simulation results
        
    Returns:
        String representation of the inserted document's ObjectId
        
    Raises:
        HTTPException: If database operation fails
    """
    if database is None:
        # Return a mock simulation ID when database is not connected (for testing)
        logger.warning("Database not connected - returning mock simulation ID")
        return f"mock_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Insert document with current timestamp
        simulation_data['timestamp'] = datetime.utcnow()
        result = await database.simulations.insert_one(simulation_data)
        
        # Convert ObjectId to string for JSON serialization
        simulation_id = str(result.inserted_id)
        logger.info(f"Saved simulation to MongoDB with ID: {simulation_id}")
        return simulation_id
        
    except Exception as e:
        logger.error(f"Failed to save to MongoDB: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {str(e)}")


# API Endpoints
@app.get("/", summary="Health Check")
async def root():
    """Health check endpoint"""
    try:
        return {
            "message": "AI-based Drop-out Prediction System is running",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "database_status": "connected" if database is not None else "disconnected",
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
        # Check if predictions file exists first  
        predictions_file = os.path.join(os.path.dirname(__file__), "data", "merged_with_predictions.csv")
        if os.path.exists(predictions_file):
            # Load predictions file directly
            df = pd.read_csv(predictions_file)
            logger.info(f"Loaded {len(df)} student records with predictions from {predictions_file}")
        else:
            # Load merged dataset and generate predictions on-the-fly
            merged_file = os.path.join(os.path.dirname(__file__), "data", "merged_dataset.csv")
            if not os.path.exists(merged_file):
                raise HTTPException(status_code=404, detail=f"Dataset not found: {merged_file}")
            
            df = pd.read_csv(merged_file)
            logger.info(f"Loaded {len(df)} student records from merged dataset")
            
            # Generate predictions using utils function
            from utils import add_predictions_to_dataset
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
    
    Args:
        request: Student parameters for simulation
        
    Returns:
        Prediction result with phase, reason, and probability
    """
    try:
        # Convert request to dictionary and validate
        student_data = request.dict()
        student_data = validate_student_input(student_data)
        
        # Use the improved prediction pipeline
        prediction_result = process_single_prediction(student_data, ml_model, ml_scaler)
        
        # Log simulation for debugging
        logger.info(f"Simulation for {student_data.get('enrollment_no', 'anonymous')}: "
                   f"fees_flag={student_data.get('fees_flag', 0)}, "
                   f"suspension_flag={student_data.get('suspension_flag', 0)}, "
                   f"model_phase={prediction_result['model_phase']}, "
                   f"final_phase={prediction_result['final_phase']}")

        return SimulateResponse(
            enrollment_no=request.enrollment_no if hasattr(request, 'enrollment_no') else None,
            model_phase=prediction_result['model_phase'],
            final_phase=prediction_result['final_phase'],
            override_reason=prediction_result['red_reason'],
            ml_probability=prediction_result['ml_probability'],
            rule_override=prediction_result['rule_override']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.post("/simulate_batch", response_model=SimulationResponse, summary="Run Risk Assessment Simulation")
async def simulate_risk_assessment():
    """
    Load student data from CSV, apply rule-based scoring, and save results to MongoDB.
    
    Returns:
        Simulation results including processed students, risk counts, and assessment log
        
    Raises:
        HTTPException: If file not found or processing fails
    """
    try:
        # Load data from CSV file
        if not os.path.exists(DATA_FILE_PATH):
            raise HTTPException(status_code=404, detail=f"Data file not found: {DATA_FILE_PATH}")
        
        df = pd.read_csv(DATA_FILE_PATH)
        logger.info(f"Loaded {len(df)} student records from {DATA_FILE_PATH}")
        
        # Normalize columns 
        normalized_df = normalize_columns(df)
        
        # Compute ML probabilities (if model available)
        ml_enhanced_df = compute_ml_proba(normalized_df)
        
        # Apply rule-based scoring with ML refinement
        processed_df = apply_rules(ml_enhanced_df)
        
        # Convert to list of dictionaries for JSON response
        students = processed_df.to_dict('records')
        
        # Calculate risk level counts
        risk_counts = processed_df['risk_level'].value_counts().to_dict()
        counts = {
            "High Risk": risk_counts.get("High Risk", 0),
            "Medium Risk": risk_counts.get("Medium Risk", 0),
            "Low Risk": risk_counts.get("Low Risk", 0),
            "Total": len(processed_df)
        }
        
        # Generate log for Medium and High risk students only
        log = []
        for _, student in processed_df.iterrows():
            if student['risk_level'] in ['Medium Risk', 'High Risk']:
                log_entry = (f"Student {student['enrollment_no']}: {student['risk_level']} "
                           f"(Score: {student['risk_score']}) - {student['risk_reasons']}")
                log.append(log_entry)
        
        # Prepare simulation data for MongoDB
        simulation_data = {
            "students": students,
            "counts": counts,
            "log": log
        }
        
        # Save to MongoDB and get simulation ID
        simulation_id = await save_to_mongo(simulation_data)
        
        logger.info(f"Simulation completed: {counts['High Risk']} High Risk, "
                   f"{counts['Medium Risk']} Medium Risk, {counts['Low Risk']} Low Risk")
        
        return SimulationResponse(
            simulation_id=simulation_id,
            timestamp=datetime.utcnow(),
            students=students,
            counts=counts,
            log=log,
            model_loaded=model_loaded,
            model_metrics=ml_metrics
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Student data file not found")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Student data file is empty")
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/simulations", response_model=SimulationListResponse, summary="Get All Past Simulations")
async def get_simulations():
    """
    Retrieve all past simulation results from MongoDB, sorted by timestamp (newest first).
    
    Returns:
        List of all simulation records with ObjectIds converted to strings
        
    Raises:
        HTTPException: If database query fails
    """
    if database is None:
        # Return empty list when database is not connected (for testing)
        logger.warning("Database not connected - returning empty simulations list")
        return SimulationListResponse(simulations=[])
    
    try:
        # Query all simulations, sorted by ObjectId (timestamp) in descending order
        cursor = database.simulations.find().sort("_id", -1)
        simulations = await cursor.to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for sim in simulations:
            sim["_id"] = str(sim["_id"])
            # Ensure timestamp is properly formatted
            if "timestamp" in sim and sim["timestamp"]:
                sim["timestamp"] = sim["timestamp"].isoformat()
        
        logger.info(f"Retrieved {len(simulations)} simulation records")
        
        return SimulationListResponse(simulations=simulations)
        
    except Exception as e:
        logger.error(f"Failed to retrieve simulations: {e}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


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


# Development server entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
