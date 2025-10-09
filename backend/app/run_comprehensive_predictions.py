"""
Generate predictions on comprehensive dataset
"""
import pandas as pd
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from generate_predictions import generate_predictions

# Paths
input_file = Path(__file__).parent / "data" / "comprehensive_data.csv"
output_file = Path(__file__).parent / "data" / "comprehensive_predicted.csv"
model_file = Path(__file__).parent / "models" / "rf_pipeline_broad.joblib"

print("="*60)
print("Generating predictions on comprehensive dataset")
print("="*60)
print(f"\nInput: {input_file}")
print(f"Output: {output_file}")
print(f"Model: {model_file}")

# Generate predictions
generate_predictions(input_file, output_file, model_file)

print("\n✓ Predictions complete!")
print(f"Output saved to: {output_file}")
