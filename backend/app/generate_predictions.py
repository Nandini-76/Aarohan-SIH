"""
ML Prediction Pipeline for Cleaned College Data
Generates phase predictions using the trained RandomForest model

This script:
1. Loads cleaned_data.csv from preprocessing
2. Applies the trained RF model to predict dropout phases
3. Uses the unified prediction system from utils.py
4. Outputs predicted_phase_data.csv with all predictions
5. Maintains compatibility with the demo dataset format

Author: ML Prediction Pipeline
Date: October 2025
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import prediction utilities
try:
    from utils import (
        add_predictions_to_dataset,
        basic_clean
    )
except ImportError:
    logger.error("Failed to import utils. Make sure utils.py is in the same directory.")
    sys.exit(1)


def load_ml_model(model_path: Path) -> tuple:
    """
    Load the trained ML model and scaler
    
    Returns:
        tuple: (model, scaler) or (None, None) if loading fails
    """
    try:
        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}")
            return None, None
        
        # Load the model
        model = joblib.load(model_path)
        logger.info(f"✓ Loaded ML model from {model_path}")
        
        # Try to load scaler if it exists
        scaler_path = model_path.parent / "scaler.joblib"
        scaler = None
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            logger.info(f"✓ Loaded scaler from {scaler_path}")
        
        return model, scaler
        
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")
        return None, None


def verify_predictions(df: pd.DataFrame) -> None:
    """
    Verify and log prediction statistics
    """
    logger.info("\n" + "="*60)
    logger.info("PREDICTION STATISTICS")
    logger.info("="*60)
    
    # Check if prediction columns exist
    pred_cols = ['final_phase', 'model_phase', 'predicted_phase']
    available_pred_cols = [col for col in pred_cols if col in df.columns]
    
    if not available_pred_cols:
        logger.warning("No prediction columns found!")
        return
    
    # Use final_phase as the primary prediction
    main_pred_col = 'final_phase' if 'final_phase' in df.columns else available_pred_cols[0]
    
    logger.info(f"\nPrediction distribution ({main_pred_col}):")
    phase_counts = df[main_pred_col].value_counts()
    total = len(df)
    
    for phase, count in phase_counts.items():
        percentage = (count / total) * 100
        logger.info(f"  {phase}: {count} ({percentage:.1f}%)")
    
    # Check for overrides if available
    if 'rule_override' in df.columns:
        override_count = df['rule_override'].sum()
        if override_count > 0:
            logger.info(f"\nRule overrides applied: {override_count}")
    
    # Check for critical cases (Red phase)
    if 'final_phase' in df.columns:
        red_students = df[df['final_phase'] == 'Red']
        if len(red_students) > 0:
            logger.info(f"\n⚠️  Critical cases (Red phase): {len(red_students)}")
            
            # Show reasons if available
            if 'red_reason' in df.columns:
                red_reasons = red_students['red_reason'].value_counts()
                logger.info("  Reasons:")
                for reason, count in red_reasons.items():
                    if reason:  # Only show non-empty reasons
                        logger.info(f"    - {reason}: {count}")


def generate_predictions(input_file: Path, output_file: Path, model_path: Path) -> bool:
    """
    Main prediction generation function
    
    Args:
        input_file: Path to cleaned_data.csv
        output_file: Path to save predicted_phase_data.csv
        model_path: Path to the ML model
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("="*60)
    logger.info("ML Prediction Pipeline")
    logger.info("="*60)
    
    # Check if input file exists
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    # Load cleaned data
    logger.info(f"\nLoading cleaned data from: {input_file}")
    try:
        df = pd.read_csv(input_file)
        logger.info(f"✓ Loaded {len(df)} student records")
    except Exception as e:
        logger.error(f"Failed to load input file: {e}")
        return False
    
    # Apply basic cleaning (just in case)
    df = basic_clean(df)
    
    # Load ML model
    ml_model, ml_scaler = load_ml_model(model_path)
    
    if ml_model is None:
        logger.warning("⚠️  ML model not available. Predictions will use rule-based system only.")
    
    # Generate predictions
    logger.info("\nGenerating predictions...")
    try:
        df_with_predictions = add_predictions_to_dataset(df, ml_model, ml_scaler)
        logger.info(f"✓ Generated predictions for {len(df_with_predictions)} students")
    except Exception as e:
        logger.error(f"Failed to generate predictions: {e}")
        return False
    
    # Verify predictions
    verify_predictions(df_with_predictions)
    
    # Save to output file
    logger.info(f"\nSaving predictions to: {output_file}")
    try:
        df_with_predictions.to_csv(output_file, index=False)
        logger.info(f"✓ Saved {len(df_with_predictions)} records to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save output file: {e}")
        return False
    
    logger.info("\n" + "="*60)
    logger.info("✓ Prediction pipeline complete!")
    logger.info("="*60)
    
    return True


def main():
    """
    Main entry point
    """
    # Setup paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    models_dir = script_dir / "models"
    
    # Input and output files
    input_file = data_dir / "cleaned_data.csv"
    output_file = data_dir / "predicted_phase_data.csv"
    model_path = models_dir / "rf_pipeline_broad.joblib"
    
    # Alternative: check if model is in parent directory
    if not model_path.exists():
        alt_models_dir = script_dir.parent / "models"
        if alt_models_dir.exists():
            models_dir = alt_models_dir
            model_path = models_dir / "rf_pipeline_broad.joblib"
    
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Model path: {model_path}")
    
    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)
    
    # Run prediction pipeline
    success = generate_predictions(input_file, output_file, model_path)
    
    if success:
        logger.info("\n✅ Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
