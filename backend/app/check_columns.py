"""
Check all available columns in original data
"""
import pandas as pd
import os
from pathlib import Path

base_dir = Path(__file__).parent.parent / "Full-college-data"
all_cols = set()
branches = {
    'BBA': 'BBA',
    'Bsc-CS': 'BSC',
    'Bsc-agriculture': 'AGR',
    'Btech': 'BTECH'
}

print("Checking all original data columns...")
print("="*60)

for branch_dir, branch_code in branches.items():
    branch_path = base_dir / branch_dir
    if branch_path.exists():
        files = [f for f in os.listdir(branch_path) if f.endswith(('.xlsx', '.xls'))]
        for file in files:
            file_path = branch_path / file
            try:
                df = pd.read_excel(file_path)
                all_cols.update(df.columns)
                print(f"{branch_code} - {file}: {len(df.columns)} columns")
            except Exception as e:
                print(f"Error reading {file}: {e}")

print("\n" + "="*60)
print(f"All unique columns found ({len(all_cols)} total):")
print("="*60)
for col in sorted(all_cols):
    print(f"  {col}")
