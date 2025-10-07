"""
Run Complete Preprocessing and Prediction Pipeline
Orchestrates the full data processing workflow

This script:
1. Runs preprocess_college_data.py to clean the raw data
2. Runs generate_predictions.py to add ML predictions
3. Provides a single entry point for the entire pipeline

Usage:
    python run_pipeline.py

Author: Pipeline Orchestrator
Date: October 2025
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_script(script_path: Path, script_name: str) -> bool:
    """
    Run a Python script and return success status
    
    Args:
        script_path: Path to the script
        script_name: Name of the script for logging
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Running {script_name}...")
    logger.info(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        # Print stdout
        if result.stdout:
            print(result.stdout)
        
        # Print stderr if there was an error
        if result.returncode != 0:
            logger.error(f"\n❌ {script_name} failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"Error output:\n{result.stderr}")
            return False
        
        logger.info(f"\n✅ {script_name} completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"\n❌ {script_name} timed out after 10 minutes")
        return False
    except Exception as e:
        logger.error(f"\n❌ {script_name} failed with exception: {e}")
        return False


def main():
    """
    Main pipeline orchestration
    """
    logger.info("="*60)
    logger.info("COMPLETE PREPROCESSING AND PREDICTION PIPELINE")
    logger.info("="*60)
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Define script paths
    preprocess_script = script_dir / "preprocess_college_data.py"
    predict_script = script_dir / "generate_predictions.py"
    
    # Check if scripts exist
    if not preprocess_script.exists():
        logger.error(f"Preprocessing script not found: {preprocess_script}")
        sys.exit(1)
    
    if not predict_script.exists():
        logger.error(f"Prediction script not found: {predict_script}")
        sys.exit(1)
    
    # Step 1: Run preprocessing
    logger.info("\n📊 STEP 1: Data Preprocessing")
    success = run_script(preprocess_script, "Data Preprocessing")
    
    if not success:
        logger.error("\n❌ Pipeline failed at preprocessing stage")
        sys.exit(1)
    
    # Step 2: Run prediction generation
    logger.info("\n🤖 STEP 2: Prediction Generation")
    success = run_script(predict_script, "Prediction Generation")
    
    if not success:
        logger.error("\n❌ Pipeline failed at prediction stage")
        sys.exit(1)
    
    # Success!
    logger.info("\n" + "="*60)
    logger.info("✅ COMPLETE PIPELINE FINISHED SUCCESSFULLY")
    logger.info("="*60)
    logger.info("\nOutput files:")
    
    data_dir = script_dir / "data"
    
    cleaned_file = data_dir / "cleaned_data.csv"
    predicted_file = data_dir / "predicted_phase_data.csv"
    
    if cleaned_file.exists():
        logger.info(f"  ✓ {cleaned_file}")
    
    if predicted_file.exists():
        logger.info(f"  ✓ {predicted_file}")
    
    logger.info("\nBackend is ready to serve the new dataset!")
    logger.info("Start the FastAPI server with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
