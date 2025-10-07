"""
Merge comprehensive data with ML predictions
"""
import pandas as pd
from pathlib import Path

# Paths
data_dir = Path(__file__).parent / "data"
comprehensive_file = data_dir / "comprehensive_data.csv"
predicted_file = data_dir / "predicted_phase_data.csv"
output_file = data_dir / "comprehensive_predicted.csv"

print("="*60)
print("Merging Comprehensive Data with Predictions")
print("="*60)

# Load both files
print("\nLoading comprehensive data...")
comp_df = pd.read_csv(comprehensive_file)
print(f"✓ Loaded {len(comp_df)} records with {len(comp_df.columns)} fields")
print(f"  Fields: {list(comp_df.columns)}")

print("\nLoading predicted data...")
pred_df = pd.read_csv(predicted_file)
print(f"✓ Loaded {len(pred_df)} records with {len(pred_df.columns)} fields")
print(f"  Fields: {list(pred_df.columns)}")

# Merge on enrollment_no
print("\nMerging datasets...")
merged_df = comp_df.merge(
    pred_df[['enrollment_no', 'final_phase', 'model_phase', 'predicted_phase', 
             'red_reason', 'ml_probability', 'rule_override']],
    on='enrollment_no',
    how='left'
)

print(f"✓ Merged {len(merged_df)} records with {len(merged_df.columns)} fields")

# Save merged data
merged_df.to_csv(output_file, index=False)
print(f"\n✓ Saved comprehensive predicted data to: {output_file}")
print(f"  Total records: {len(merged_df)}")
print(f"  Total fields: {len(merged_df.columns)}")

# Show phase distribution
print("\nPhase Distribution:")
if 'final_phase' in merged_df.columns:
    for phase, count in merged_df['final_phase'].value_counts().items():
        print(f"  {phase}: {count}")

print("\n" + "="*60)
print("✅ Merge complete!")
print("="*60)
