# College Dataset Preprocessing System

## Overview

This system preprocesses and integrates a large synthetic college dataset into the existing dashboard backend. It maintains compatibility with the frontend while scaling from 56 demo students to thousands of real students across multiple branches and years.

## System Architecture

```
Full-college-data/           # Raw synthetic data
├── BBA/
├── Bsc-CS/
├── Bsc-agriculture/
└── Btech/

       ↓
       
preprocess_college_data.py   # Step 1: Clean & normalize
       ↓
       
data/cleaned_data.csv        # Intermediate output
       ↓
       
generate_predictions.py      # Step 2: ML predictions
       ↓
       
data/predicted_phase_data.csv  # Final output
       ↓
       
FastAPI Backend              # Serves to frontend
```

## Files

### Core Scripts

1. **`preprocess_college_data.py`**
   - Loads all branch/year CSV and Excel files
   - Normalizes column names to match demo schema
   - Standardizes categorical values (Gender: M/F, Category: SC/ST/OBC/General)
   - Handles missing values with intelligent defaults
   - Outputs: `data/cleaned_data.csv`

2. **`generate_predictions.py`**
   - Loads cleaned_data.csv
   - Applies trained RandomForest model for phase predictions
   - Uses unified prediction system with rule overrides
   - Outputs: `data/predicted_phase_data.csv`

3. **`run_pipeline.py`**
   - Orchestrates the complete pipeline
   - Runs both preprocessing and prediction scripts
   - Single command execution

4. **`config.py`**
   - Memory optimization settings
   - Configurable for Render free tier constraints

### Modified Files

- **`main.py`**: Updated to:
  - Auto-run preprocessing on startup if needed
  - Load `predicted_phase_data.csv` with fallback to demo data
  - Maintain exact same API response format

## Usage

### Option 1: Run Complete Pipeline

```bash
cd backend/app
python run_pipeline.py
```

This will:
1. Clean and normalize all data from `Full-college-data/`
2. Generate ML predictions
3. Create `predicted_phase_data.csv`

### Option 2: Run Steps Individually

```bash
# Step 1: Preprocess data
python preprocess_college_data.py

# Step 2: Generate predictions
python generate_predictions.py
```

### Option 3: Automatic on Backend Start

The backend automatically runs preprocessing if:
- `predicted_phase_data.csv` doesn't exist
- Source data is newer than processed data

Just start the server:
```bash
uvicorn app.main:app --reload
```

## Data Schema

### Required Columns (matches demo dataset)

```python
[
    'enrollment_no',      # Unique ID (string)
    'attendance',         # Percentage 0-100 (float)
    'cgpa',              # 0-10 scale (float)
    'backlogs',          # Count of backlogs (int)
    'marks_10th',        # Percentage (float)
    'marks_12th',        # Percentage (float)
    'fees_pending',      # Amount or NaN (float)
    'scholarship',       # Amount or NaN (float)
    'remarks',           # Text or empty (str)
    'father_occupation', # Occupation (str)
    'mother_occupation', # Occupation (str)
    'family_income',     # Income bracket (str)
    'guardian_education',# Education level (str)
    'aadhaar_no',        # ID number (float)
    'mobile_no',         # Phone (float)
    'parents_mobile_no', # Phone (float)
    'phone',             # Phone (float)
    'email',             # Email or empty (str)
    'gender',            # M or F (str)
    'age_at_enrollment', # Age (int)
    'category',          # SC/ST/OBC/General (str)
    'department',        # Branch code (str)
    'year_of_enrollment',# Year (int)
    'suspension_flag',   # 0 or 1 (int)
    'hostel_flag',       # 0 or 1 (int)
    'fees_flag',         # 0=Paid, 1=Pending (int)
    'scholarship_flag',  # 0 or 1 (int)
    'bus_fees'          # Amount (int)
]
```

### Prediction Columns (added by ML pipeline)

```python
[
    'model_phase',       # ML prediction: Green/Yellow/Orange/Red
    'final_phase',       # Final after rule overrides
    'predicted_phase',   # Alias for final_phase
    'red_reason',        # Reason if overridden to Red
    'ml_probability',    # Dropout probability 0-1
    'rule_override'      # Boolean: was rule applied?
]
```

## Column Mapping

The preprocessor automatically maps various column names to the standard schema:

| Source Columns | Target Column |
|----------------|---------------|
| Enrollment_No, Enrollment No. | enrollment_no |
| Gender (Male/Female) | gender (M/F) |
| Age | age_at_enrollment |
| Caste | category |
| Father Occupation | father_occupation |
| Mother Occupation | mother_occupation |
| Class_10_Percentage | marks_10th |
| Class_12_Percentage | marks_12th |
| Attendance | attendance |
| CGPA | cgpa |
| Backlogs | backlogs |
| Suspension (Yes/No) | suspension_flag (1/0) |
| Fees_Status (Paid/Partial/Pending) | fees_flag (0/1) |

## Categorical Value Standardization

### Gender
- Male, M, male → `M`
- Female, F, female → `F`

### Category (Caste)
- General, GEN, Gen → `General`
- OBC → `OBC`
- SC → `SC`
- ST, SC/ST → `ST`
- EWS → `General`

### Department
- Computer Science, CSE, CS → `CSE`
- Information Technology, IT → `IT`
- Mechanical, ME → `ME`
- Electrical, EEE → `EEE`
- Electronics, ECE → `ECE`
- Civil, CE, CIVIL → `CE`
- BBA → `BBA`
- B.Sc, BSc → `BSC`
- Agriculture, B.Agriculture → `AGR`

## Memory Optimization

For Render free tier (512MB RAM):

1. **Chunked Processing**: Process data in batches
2. **Streaming**: Don't load entire dataset in memory
3. **Lazy Loading**: Load ML model only when needed
4. **Cleanup**: Delete intermediate files after processing
5. **Compression**: Optional CSV compression

Configure in `config.py`:
```python
CHUNK_SIZE = 1000
MAX_STUDENTS_IN_MEMORY = 5000
ENABLE_PREDICTION_CACHE = False
```

## API Endpoint Changes

The `/students` endpoint now:

1. **Priority loading**:
   - First: `predicted_phase_data.csv` (preprocessed large dataset)
   - Fallback: `merged_with_predictions.csv` (demo data)
   - Last resort: `merged_dataset.csv` (generate predictions on-the-fly)

2. **Response format**: Unchanged - fully compatible with frontend

3. **Filters**: Branch, year, phase filtering still work

## Frontend Compatibility

✅ **No frontend changes needed**

The preprocessing ensures:
- Same column names as demo data
- Same value formats (M/F, department codes)
- Same API response structure
- Same filtering logic

## Troubleshooting

### Issue: Preprocessing takes too long
**Solution**: Reduce dataset size or increase timeout in `config.py`

### Issue: Out of memory on Render
**Solution**: 
- Set `ENABLE_PREDICTION_CACHE = False`
- Reduce `CHUNK_SIZE`
- Pre-process data locally and commit `predicted_phase_data.csv`

### Issue: Column mapping errors
**Solution**: Check source CSV column names and update `COLUMN_MAPPING` in `preprocess_college_data.py`

### Issue: Predictions not showing
**Solution**: 
- Check if ML model exists: `backend/app/models/rf_pipeline_broad.joblib`
- Verify predictions file: `backend/app/data/predicted_phase_data.csv`
- Check logs for errors

## Production Deployment

### Option A: Pre-process Locally (Recommended for Free Tier)

```bash
# On local machine
cd backend/app
python run_pipeline.py

# Commit the output file
git add data/predicted_phase_data.csv
git commit -m "Add preprocessed dataset"
git push
```

Then in `config.py`:
```python
RUN_PREPROCESSING_ON_STARTUP = False
```

### Option B: Process on Render (Requires More Memory)

Keep default settings and let it run on startup.

## Performance

- **Demo dataset**: 56 students → instant loading
- **Small dataset**: <1,000 students → <10 seconds
- **Medium dataset**: 1,000-5,000 students → <60 seconds
- **Large dataset**: >5,000 students → 2-5 minutes

## Logging

Logs show:
- Number of files processed per branch
- Records loaded from each file
- Data cleaning operations
- Prediction statistics (Green/Yellow/Orange/Red distribution)
- Memory usage warnings

Enable detailed logging:
```python
# In config.py
LOG_LEVEL = "DEBUG"
```

## Support

For issues or questions:
1. Check logs in terminal/console
2. Verify file structure matches expected layout
3. Test with demo data first
4. Check that source CSV files are readable

## Future Enhancements

- [ ] Support for streaming predictions
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Real-time data updates
- [ ] Incremental preprocessing (only new records)
- [ ] Parallel processing for large datasets
- [ ] Data validation and quality reports
- [ ] Automated testing suite
