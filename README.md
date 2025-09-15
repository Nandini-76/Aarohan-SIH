# AI-based Drop-out Prediction and Counseling System - Prototype

**Problem Statement ID**: 25102  
**Organization**: Government of Rajasthan  
**Department**: Directorate of Technical Education (DTE)  
**Development Phase**: ✅ Stage-1 (Rule-based) + 🆕 Stage-2 (ML-Enhanced)

## 📋 Project Overview

This prototype implements a **hybrid student dropout prediction system** that combines rule-based scoring with machine learning refinement. The system identifies at-risk students before end-term evaluations using both deterministic rules and probabilistic ML models.

### 🎯 Problem Statement
- **Challenge**: By the time end-term marks reveal failures, many students have already disengaged
- **Solution**: Early risk detection using 7 key student factors with ML-enhanced accuracy
- **Input**: CSV files from institutes with student data
- **Output**: Consolidated dashboard with mentor notifications and confidence scores

### 🆕 Stage-2 Enhancements (NEW!)
- **Logistic Regression Model**: Trained on the 7 key factors for probabilistic risk assessment
- **Hybrid Risk Refinement**: ML probabilities refine rule-based classifications using conservative thresholds
- **Training Pipeline**: Automated model training with synthetic data generation
- **API-driven Training**: `/train` endpoint for model retraining
- **Performance Metrics**: Real-time model evaluation and monitoring

## 🏗️ Architecture Overview

```
prototype/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI with rule-based + ML hybrid system
│   │   ├── models/              # 🆕 Trained ML models directory
│   │   │   ├── model.joblib     # 🆕 Logistic Regression model
│   │   │   ├── scaler.joblib    # 🆕 Feature scaler
│   │   │   ├── metrics.json     # 🆕 Model performance metrics
│   │   │   └── .gitignore       # 🆕 Model files exclusion
│   │   └── data/
│   │       ├── students.csv     # Sample student data (15 records)
│   │       └── training.csv     # 🆕 Generated training data (auto-created)
│   ├── train_model.py           # 🆕 ML model training script
│   ├── test_integration.py      # 🆕 API integration tests
│   ├── requirements.txt         # Python + ML dependencies
│   └── start.sh                # Server startup script
└── README.md                   # This documentation
```

## 📊 Risk Assessment Model

### 7 Key Factors
1. **enrollment_no** (string) - Primary key identifier
2. **fees_paid** (Y/N) - Fee payment status
3. **gpa** (float) - Overall academic performance (0-10)
4. **marks_10** (float) - 10th grade percentage
5. **marks_12** (float) - 12th grade percentage  
6. **attendance_percent** (float) - Class attendance percentage
7. **backlogs** (int) - Number of failed/pending subjects
8. **suspension** (Y/N) - Previous disciplinary action

### Rule-based Scoring Algorithm
```python
# Risk Score Calculation
score = 0
if fees_paid == 'N': score += 2
if gpa < 5: score += 2  
if marks_10 < 50: score += 1
if marks_12 < 50: score += 1
if attendance_percent < 70: score += 2
if backlogs >= 3: score += 2
if suspension == 'Y': score += 3

# Risk Level Classification
if score >= 6: level = "High Risk"
elif score >= 3: level = "Medium Risk" 
else: level = "Low Risk"
```

### 🧠 Machine Learning Enhancement (Stage-2)

**Logistic Regression Formula**:
```
P(dropout=1|X) = 1 / (1 + exp(-(β₀ + Σ βᵢ xᵢ)))

Where X = [attendance_percent, gpa, marks_10, marks_12, backlogs, fees_flag, suspension_flag]
- fees_flag = 1 if fees_paid == 'N' else 0  
- suspension_flag = 1 if suspension == 'Y' else 0
```

**Hybrid Risk Refinement Logic**:
```python
# Conservative ML thresholds for rule refinement
if ml_proba >= 0.75:      # High confidence → Override to High Risk
    risk_level = "High Risk" 
elif ml_proba >= 0.45 and rule_risk == "Low Risk":  # Medium confidence → Upgrade Low to Medium
    risk_level = "Medium Risk"
elif ml_proba < 0.30:     # Low confidence → Keep rule-based result
    pass  # No override
```

**Threshold Rationale**:
- **0.75**: High confidence threshold to avoid false alarms for High Risk classification
- **0.45**: Moderate confidence to elevate Low Risk students who show ML warning signs  
- **0.30**: Low confidence region where rule-based system is preferred over ML uncertainty

## 🚀 API Endpoints

### 1. Health Check
```http
GET /
```
**Response**: System status and database connectivity

### 2. Run Risk Assessment Simulation
```http
POST /simulate
```
**Description**: 
- Loads student data from `backend/app/data/students.csv`
- Applies rule-based scoring algorithm
- 🆕 Computes ML dropout probabilities (if model loaded)
- 🆕 Applies ML-based risk refinement using conservative thresholds
- Saves results to MongoDB
- Returns simulation results with risk analysis and ML data

**Response**:
```json
{
  "simulation_id": "64f...",
  "timestamp": "2025-09-10T...",
  "students": [
    {
      "enrollment_no": "STU001",
      "risk_level": "Low Risk",
      "risk_score": 0,
      "ml_proba": 0.234,  // 🆕 ML dropout probability
      "risk_reasons": "No significant risk factors identified"
    }
  ],
  "counts": {
    "High Risk": 3,
    "Medium Risk": 5, 
    "Low Risk": 7,
    "Total": 15
  },
  "log": [...],
  "model_loaded": true,    // 🆕 Whether ML model was used
  "model_metrics": {...}   // 🆕 ML model performance info
}
```

### 3. 🆕 Train ML Model
```http
POST /train?token=devtoken
```
**Description**: 
- Trains Logistic Regression model on available data
- Generates synthetic training data if needed
- Returns training metrics and saves model files
- Requires security token for access

**Response**:
```json
{
  "success": true,
  "message": "Model trained successfully!",
  "metrics": {
    "test_accuracy": 0.8750,
    "test_f1": 0.8421,
    "test_auc": 0.9123
  },
  "model_path": "app/models/model.joblib"
}
```

### 4. Retrieve All Past Simulations  
```http
GET /simulations
```
**Description**: Returns all simulation history sorted by timestamp (newest first)

## 🗄️ Database Schema

**MongoDB Collection**: `simulations`
```javascript
{
  _id: ObjectId("..."),
  timestamp: ISODate("2025-09-10T..."),
  students: [
    {
      enrollment_no: "STU001",
      fees_paid: "Y",
      gpa: 7.5,
      risk_score: 0,
      risk_level: "Low Risk",
      risk_reasons: "No significant risk factors identified"
    }
  ],
  counts: {
    "High Risk": 3,
    "Medium Risk": 5,
    "Low Risk": 7,
    "Total": 15
  },
  log: ["Student STU002: High Risk (Score: 8) - Fees not paid (+2); Low GPA < 5 (+2); ..."]
}
```

## 📈 Sample Data Analysis

The prototype includes 15 carefully crafted sample records with mixed risk profiles:

| Risk Level | Count | Example Students |
|------------|-------|------------------|
| **High Risk** | 3 | STU004, STU007, STU012 |
| **Medium Risk** | 5 | STU002, STU010, STU014, STU015, STU009 |
| **Low Risk** | 7 | STU001, STU003, STU005, STU006, STU008, STU011, STU013 |

### High Risk Examples:
- **STU004**: Fees unpaid, GPA 2.8, Low marks, Poor attendance, Multiple backlogs, Suspended
- **STU007**: Fees unpaid, GPA 1.9, Very low marks, Very poor attendance, Many backlogs, Suspended  
- **STU012**: Fees unpaid, GPA 2.1, Very low marks, Very poor attendance, Excessive backlogs, Suspended

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- MongoDB (local or cloud instance)
- Git

### Quick Start (Stage-2 with ML)

1. **Clone and navigate to prototype**:
```bash
cd prototype/backend
```

2. **Set up Python environment**:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies (includes ML libraries)
pip install -r requirements.txt
```

3. **Configure environment variables** (optional):
```bash
export MONGO_URI="mongodb://localhost:27017"
export DB_NAME="dropout_prediction"
```

4. **Train the ML model** (first-time setup):
```bash
# Option 1: Direct training script
python train_model.py

# Option 2: API-based training (after starting server)
curl -X POST "http://localhost:8000/train?token=devtoken"
```

5. **Start the enhanced server**:
```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows (PowerShell)
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access the API**:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Run ML-Enhanced Simulation**: POST http://localhost:8000/simulate
- **Train Model**: POST http://localhost:8000/train?token=devtoken

## 🧪 Testing the Stage-2 System

### Automated Integration Testing
```bash
# Run comprehensive test suite
python test_integration.py

# Expected output:
# ✅ API health check
# ✅ ML model training (if needed)  
# ✅ Simulation with ML refinement
# ✅ History retrieval
# 🎉 ALL TESTS PASSED!
```

### Manual Testing via API Documentation (Swagger UI)
1. Navigate to http://localhost:8000/docs
2. Test `/train` endpoint first (if model not trained):
   - Use token: `devtoken`
   - Check training metrics in response
3. Test `/simulate` endpoint:
   - Observe `model_loaded: true` in response
   - Check `ml_proba` values for each student
   - Look for ML refinement messages in risk_reasons
4. View results and MongoDB integration

### Using curl Commands
```bash
# Health check with ML model status
curl http://localhost:8000/

# Train ML model (first time)
curl -X POST "http://localhost:8000/train?token=devtoken"

# Run ML-enhanced simulation
curl -X POST http://localhost:8000/simulate

# Get simulation history
curl http://localhost:8000/simulations
```

### Expected ML Enhancement Results
With the trained model, you should see:
- Each student has `ml_proba` field (0.0 to 1.0)
- Risk refinements logged: `[ML Override: High confidence...]` 
- Model metrics in simulation response
- Conservative thresholds preventing false alarms

## 📋 Repository Analysis Summary

This prototype was built after analyzing 5 existing dropout prediction repositories:

### Key Insights Extracted:
1. **End-to-end-Drop-Out-Project**: XGBoost pipeline with SMOTE, hyperparameter tuning
2. **student-dropout-prediction**: Streamlit UI patterns, model persistence strategies
3. **student-dropout-prediction2**: Multi-algorithm comparison (ML vs Deep Learning)
4. **student-dropout-prediction3**: Modular architecture, CLI interfaces, model bundling
5. **StudentDropoutPrediction**: Comprehensive dashboard with explainability (SHAP/LIME)

### Reusable Components Identified:
- ✅ Data preprocessing and normalization patterns
- ✅ Risk scoring and classification logic  
- ✅ MongoDB integration for simulation storage
- ✅ FastAPI endpoint structure and error handling
- ✅ Comprehensive logging and monitoring
- ✅ 🆕 ML model training and integration patterns
- ✅ 🆕 Hybrid rule-based + ML refinement approach

## ✅ Stage-2 Implementation Complete!

### 🎯 Successfully Implemented:
- [x] **Logistic Regression Model**: Trained on 7 key factors with synthetic data generation
- [x] **Conservative ML Thresholds**: 0.75 (High), 0.45 (Medium upgrade), 0.30 (no override)  
- [x] **Hybrid Risk System**: Rule-based foundation with ML probability refinement
- [x] **API Training Endpoint**: `/train` with token protection for model retraining
- [x] **Performance Monitoring**: Real-time metrics and model evaluation
- [x] **Integration Tests**: Comprehensive test suite validating end-to-end pipeline

### 🚀 Future Stage-3 Possibilities:
- [ ] **Advanced Models**: XGBoost, Random Forest comparison with hyperparameter tuning
- [ ] **Real-time Notifications**: Automated mentor/counselor alert system
- [ ] **Dashboard Frontend**: Interactive visualization with SHAP explainability
- [ ] **Batch Processing**: CSV upload interface for bulk student assessment
- [ ] **Model Monitoring**: Drift detection and automatic retraining triggers
- [ ] **Multi-institution**: Tenant-based system for multiple colleges/universities

## 🏷️ Technical Tags
`FastAPI` `MongoDB` `Pandas` `Machine Learning` `Student Analytics` `Risk Assessment` `Educational Technology` `Government Project` `Rule-based System` `Early Warning System`

---

**Development Team**: Pair Programming Session  
**Date**: September 10, 2025  
**Status**: Stage-1 Complete ✅
