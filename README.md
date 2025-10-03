# AAROHAN - AI-Based Student Dropout Prediction & Counseling System

**Problem Statement ID**: SIH 2025  
**Organization**: Government Institution  
**Category**: Educational Technology & AI-Driven Intervention System  
**Development Status**: ✅ Fully Functional Prototype

## 📋 Executive Summary

AAROHAN is a **lightweight, AI-powered student dropout prediction and counseling system** designed specifically for public educational institutions with limited budgets. The system provides **accurate, early warning detection** of at-risk students and delivers **structured, phased interventions** to prevent dropouts before they occur.

Unlike expensive commercial analytics platforms, AAROHAN leverages **Random Forest machine learning** combined with **rule-based safety thresholds** to deliver precise predictions while maintaining **interpretability**, **transparency**, and **actionable insights** for counselors, mentors, and administrators.

### 🎯 Core Value Proposition

- ✅ **Preventive Rather Than Reactive**: Catches at-risk students early, before critical failures occur
- ✅ **Lightweight & Cost-Effective**: Runs on modest infrastructure (single server or local machine)
- ✅ **Structured Intervention Hierarchy**: Phased escalation (Green → Yellow → Orange → Red) with clear stakeholder responsibilities
- ✅ **Consolidated Data Platform**: Eliminates fragmented spreadsheets by unifying attendance, academics, fees, and behavioral data
- ✅ **Non-Technical Interface**: Intuitive dashboards requiring no technical expertise
- ✅ **Automated Notifications**: Real-time alerts to counselors, mentors, and parents at the right intervention phase

### � Key Features

- 🧠 **Random Forest ML Model**: 85% accuracy dropout prediction
- 🎯 **4-Tier Risk Classification**: Green/Yellow/Orange/Red phased intervention
- 📊 **Real-time Dashboards**: Counselor, admin, and student views
- 🔔 **Automated Notifications**: SMS/Email alerts to stakeholders
- 📈 **Post-Intervention Tracking**: Monitor recovery progress after interventions
- 🧪 **Psychological Assessment Integration**: Stress and motivation quizzes
- 📋 **What-If Simulation**: Test scenarios before implementing interventions

## 🏗️ System Architecture

```
AAROHAN/
├── backend/                          # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py                  # FastAPI server with API endpoints
│   │   ├── utils.py                 # Prediction pipeline & utilities
│   │   ├── models/
│   │   │   ├── rf_pipeline_broad.joblib    # Trained Random Forest model
│   │   │   ├── feature_utils.py            # Feature engineering functions
│   │   │   ├── prediction_pipeline.py      # ML prediction logic
│   │   │   ├── integration_pipeline.py     # Unified system integration
│   │   │   └── RF-training-script.py       # Model training script
│   │   └── data/
│   │       ├── merged_dataset.csv          # Training data
│   │       └── test_students_dataset_new_rf.csv  # Test data
│   ├── requirements.txt             # Python dependencies
│   └── start.sh                     # Server startup script
│
├── frontend/                        # React + Tailwind UI
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # Main dashboard with risk overview
│   │   │   ├── StudentProfile.tsx   # Individual student details
│   │   │   ├── Simulation.tsx       # What-if scenario simulator
│   │   │   └── Landing.tsx          # Landing page
│   │   ├── components/
│   │   │   ├── RiskBadge.tsx        # Green/Yellow/Orange/Red indicators
│   │   │   ├── DashboardLayout.tsx  # Layout wrapper
│   │   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   │   └── ui/                  # Reusable UI components (shadcn/ui)
│   │   └── services/
│   │       └── api.ts               # Backend API integration
│   ├── package.json
│   └── vite.config.ts
│
├── README.md                        # This file
├── DEPLOYMENT.md                    # Deployment guide (Render + Vercel)
└── render.yaml                      # Render.com configuration
```

### Technology Stack

**Backend**:
- Python 3.9+ with FastAPI microservices
- Random Forest (scikit-learn) for ML predictions
- PostgreSQL/MongoDB for data storage
- Joblib for model persistence

**Frontend**:
- React 18 + TypeScript
- Tailwind CSS for styling
- shadcn/ui component library
- Recharts for data visualization
- Vite for build tooling

**Deployment**:
- Backend: Render.com (or local server)
- Frontend: Vercel
- Database: MongoDB Atlas (cloud) or local instance

## 🧠 Technical Approach

### 1. Machine Learning Model: Random Forest Classifier

**Why Random Forest?**
- ✅ Robust with tabular educational data
- ✅ Handles non-linear relationships between features
- ✅ Provides feature importance for interpretability
- ✅ Resistant to overfitting
- ✅ Efficient on small-to-medium datasets
- ✅ No need for extensive feature scaling

**Model Performance (Prototype)**:
- **Accuracy**: 85%
- **Precision**: 80%
- **Recall**: 82%
- **F1-Score**: 81%

### 2. Data Sources & Key Features

**Input Data**:
- 📊 Attendance logs (percentage, streaks)
- 📚 Academic records (CGPA, backlogs, exam attempts)
- 💰 Fee payment history (delays, arrears)
- ⚠️ Disciplinary incidents (suspensions)
- 📝 Demographic data (10th/12th marks, gender)

**Core Features for Prediction**:

| Feature | Type | Description | Importance |
|---------|------|-------------|------------|
| `attendance` | float | Class attendance percentage (0-100) | 🔴 High |
| `cgpa` | float | Overall academic performance (0-10) | 🔴 High |
| `backlogs` | int | Number of failed/pending subjects | 🔴 High |
| `fees_flag` | binary | Fee payment status (0=paid, 1=unpaid) | 🟡 Medium |
| `suspension_flag` | binary | Disciplinary action (0=none, 1=suspended) | 🟡 Medium |
| `marks_10th` | float | 10th grade percentage | 🟢 Low |
| `marks_12th` | float | 12th grade percentage | 🟢 Low |
| `gender` | string | Student gender (M/F) | 🟢 Low |

### 3. Feature Engineering

The system automatically engineers 15+ features from raw data to improve prediction accuracy:

```python
# Interaction Features
att_cgpa_interaction = (attendance / 100) * cgpa
backlog_pressure = backlogs / (cgpa + 1)
att_backlog_ratio = attendance / (backlogs + 1)

# Composite Risk Indicators
risk_index = (100 - attendance) * 0.4 + (10 - cgpa) * 0.4 + backlogs * 2 + suspension_flag * 3

# Threshold-based Features (for Yellow/Orange separation)
attendance_gap = abs(attendance - 75)
cgpa_gap = abs(cgpa - 6.5)
yellow_zone_score = 1 if (70 ≤ attendance ≤ 79 and 5.0 ≤ cgpa ≤ 6.0) else 0

# Behavioral Flags
mild_backlog_flag = 1 if (1 ≤ backlogs ≤ 2) else 0
discipline_academic_combo = 1 if (suspension_flag > 0 and cgpa < 6.0) else 0
high_performer_flag = 1 if (attendance ≥ 85 and cgpa ≥ 8.0 and backlogs == 0) else 0
```

**Feature Importance Analysis** (from trained model):
```
1. attendance              (0.28)  # Strongest predictor
2. cgpa                    (0.24)
3. backlog_pressure        (0.18)  # Engineered feature
4. risk_index              (0.15)  # Composite score
5. att_cgpa_interaction    (0.10)
```

---

## 🚨 Risk Classification & Intervention Hierarchy

AAROHAN uses a **4-tier phased intervention system** that balances ML predictions with rule-based safety thresholds.

### Risk Phase Matrix

| Phase | Risk Level | ML Criteria | Rule Override Conditions | Stakeholders Notified |
|-------|------------|-------------|-------------------------|----------------------|
| 🟢 **Green** | Safe | High performance | - | None (routine monitoring) |
| 🟡 **Yellow** | Caution | Moderate signals | Declining trends | Counselor (watch) |
| 🟠 **Orange** | Moderate Risk | Warning signs | Attendance < 70% OR CGPA < 5.0 OR Backlogs ≥ 3 | **Phase 1**: Counselor<br>**Phase 2**: Counselor + Mentor<br>**Phase 3**: Parents + Counselor + Mentor |
| 🔴 **Red** | High Risk | Critical indicators | Attendance < 60% OR CGPA < 4.0 OR Fees unpaid + Suspension | **Immediate**: All stakeholders |

### Phase-Based Intervention Flow

#### 🟢 Green Zone
- **Condition**: Attendance ≥ 85%, CGPA ≥ 7.0, No backlogs, Fees paid
- **Action**: Routine monitoring only
- **Notifications**: None

#### 🟡 Yellow Zone
- **Condition**: Attendance 70-85%, CGPA 5.0-7.0, 1-2 backlogs
- **Action**: Counselor keeps watch (no escalation)
- **Notifications**: None (passive tracking)

#### 🟠 Orange Zone (Phased Escalation)
- **Condition**: Attendance 60-70%, CGPA 4.0-5.0, 3-5 backlogs

**Phase 1** (Initial Warning):
- Counselor notified
- One-on-one session scheduled

**Phase 2** (No Improvement):
- Mentor engaged alongside counselor
- Psychological quiz administered (stress/motivation)

**Phase 3** (Persistent Issues):
- Parents/guardians contacted
- Joint intervention meeting

#### 🔴 Red Zone (Immediate Action)
- **Condition**: Attendance < 60%, CGPA < 4.0, 6+ backlogs, Fees unpaid, Suspended
- **Action**:
  - Immediate high-priority alerts to all stakeholders
  - Urgent intervention meeting
  - Academic probation consideration
  - Intensive support program

## � API Endpoints

### 1. Health Check
```http
GET /
```
**Response**:
```json
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "version": "2.0",
  "ml_model_loaded": true
}
```

---

### 2. Student Risk Prediction
```http
POST /api/predict
```
**Request Body**:
```json
{
  "enrollment_no": "2023CSE045",
  "attendance": 55.0,
  "cgpa": 5.2,
  "backlogs": 3,
  "marks_10th": 75,
  "marks_12th": 78,
  "fees_flag": 0,
  "suspension_flag": 0,
  "gender": "F"
}
```

**Response**:
```json
{
  "enrollment_no": "2023CSE045",
  "name": "Kavya Reddy",
  "model_phase": "Yellow",
  "final_phase": "Orange",
  "rule_override": true,
  "override_reason": "Attendance below 60% threshold (55.0%) - elevated to Orange",
  "ml_probability": 0.42,
  "confidence": 0.85,
  "notification_message": "Alert sent to Counselor for Orange Phase 1 intervention",
  "recommendations": [
    "Schedule counseling session within 48 hours",
    "Assess attendance barriers"
  ]
}
```

---

### 3. What-If Simulation
```http
POST /api/simulate
```
**Description**: Test hypothetical scenarios by adjusting student parameters

**Request**: Same as `/api/predict`

**Response**: Includes simulation metadata and comparison with current state

---

### 4. Student Profile
```http
GET /api/students/{enrollment_no}
```

**Response**:
```json
{
  "enrollment_no": "2023CSE045",
  "name": "Kavya Reddy",
  "department": "Computer Science",
  "current_phase": "Orange",
  "intervention_history": [
    {
      "date": "2025-09-15",
      "phase": "Orange",
      "action_taken": "Counselor notified"
    }
  ],
  "performance_trend": {
    "cgpa_history": [7.2, 6.8, 6.0, 5.2],
    "attendance_history": [78, 72, 65, 55]
  }
}
```

---

### 5. Dashboard Statistics
```http
GET /api/dashboard/stats
```

**Response**:
```json
{
  "total_students": 1500,
  "risk_distribution": {
    "Green": 850,
    "Yellow": 420,
    "Orange": 180,
    "Red": 50
  },
  "intervention_outcomes": {
    "improved": 135,
    "declined": 25
  }
}
```



---

## 📚 Documentation

- **[README.md](./README.md)** (this file): Project overview and setup
- **[DEPLOYMENT.md](./DEPLOYMENT.md)**: Production deployment guide
- **[NEW_RF_MODEL_IMPLEMENTATION.md](./NEW_RF_MODEL_IMPLEMENTATION.md)**: ML model technical details

---

## 🤝 Contributing

AAROHAN is designed for educational institutions and government deployment. Contributions are welcome!

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

## � Team

**Development Team**: AAROHAN SIH 2025 Team  
**Problem Statement**: Student Dropout Prevention System  
**Target Users**: Educational Institutions, Government Bodies, Counselors, Faculty

---

## 📞 Support

For technical support or deployment assistance:
- **Issues**: [GitHub Issues](https://github.com/Gaurav8302/AROHANN/issues)
- **Documentation**: See project documentation files
- **Repository**: [GitHub Repository](https://github.com/Gaurav8302/AROHANN)

---

## � Acknowledgments

- Smart India Hackathon 2025
- Government institutions and educational partners
- Open-source ML community (scikit-learn, FastAPI, React)
- Students and counselors who provided valuable feedback

---

## 🏷️ Technical Tags

`AI` `Machine Learning` `Random Forest` `Educational Technology` `Dropout Prediction` `Student Analytics` `FastAPI` `React` `MongoDB` `Python` `TypeScript` `Counseling System` `Early Warning System` `Government Project` `SIH 2025`

---

**Built with ❤️ for accessible, equitable education**

*AAROHAN - Empowering institutions to prevent dropouts through intelligent intervention*
