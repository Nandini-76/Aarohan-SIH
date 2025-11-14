# AAROHAN - AI-Based Student Dropout Prediction & Counseling System

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

**Smart India Hackathon 2025 | Educational Technology & AI-Driven Intervention**

[Features](#-features) • [Demo](#-live-demo) • [Installation](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

AAROHAN is an **AI-powered student dropout prediction and counseling system** designed for educational institutions. The system provides **early warning detection** of at-risk students and delivers **structured, phased interventions** to prevent dropouts before they occur.

### 🎯 Key Highlights

- 🧠 **85% Accurate Predictions** using Random Forest ML model
- 🎯 **4-Tier Risk Classification** (Green/Yellow/Orange/Red)
- 📊 **Real-time Dashboards** for counselors and administrators
- 🔔 **Automated Notifications** to stakeholders at appropriate intervention phases
- 📈 **Post-Intervention Tracking** to monitor student recovery
- 💰 **Cost-Effective** - runs on modest infrastructure
- 🚀 **Production-Ready** - deployed on Render + Vercel + Firebase

---

## ✨ Features

### Core Functionality

- **🧠 Machine Learning Predictions**
  - Random Forest classifier with 85% accuracy
  - Predicts dropout risk based on attendance, CGPA, backlogs, fees, and behavioral data
  - 15+ engineered features for enhanced accuracy

- **🎯 4-Tier Risk Classification**
  - 🟢 **Green**: Safe students (routine monitoring)
  - 🟡 **Yellow**: Caution zone (counselor watch)
  - 🟠 **Orange**: Moderate risk (phased intervention - 3 levels)
  - 🔴 **Red**: High risk (immediate intervention)

- **📊 Interactive Dashboards**
  - Real-time student risk overview
  - Filterable by department, year, risk level
  - Individual student profiles with intervention history
  - Performance trends and analytics

- **🔔 Smart Notifications**
  - Automated alerts to counselors, mentors, and parents
  - Phased escalation based on risk level
  - Email/SMS integration (configurable)

- **📈 What-If Simulations**
  - Test hypothetical scenarios
  - Predict impact of attendance/grade improvements
  - Data-driven intervention planning

- **🔐 Firebase Integration**
  - Real-time data synchronization
  - Instant dashboard updates
  - Scalable cloud storage

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AAROHAN System Architecture               │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐        ┌─────────────┐
│   Frontend   │ HTTPS   │   Backend    │  REST  │   Firebase  │
│ React + Vite │◄───────►│  FastAPI +   │◄──────►│  Realtime   │
│   (Vercel)   │         │  Python ML   │        │  Database   │
└──────────────┘         └──────────────┘        └─────────────┘
                                │
                                │ ML Model
                                ↓
                        ┌──────────────┐
                        │ Random Forest│
                        │   Pipeline   │
                        │ (.joblib)    │
                        └──────────────┘
```

### Technology Stack

**Backend:**
- Python 3.9+ with FastAPI
- scikit-learn (Random Forest ML)
- Firebase Admin SDK
- Pandas for data processing
- Joblib for model persistence

**Frontend:**
- React 18 + TypeScript
- Vite build tool
- Tailwind CSS + shadcn/ui components
- Recharts for visualizations
- Firebase SDK for real-time data

**Deployment:**
- Backend: Render.com
- Frontend: Vercel
- Database: Firebase Realtime Database
- Version Control: GitHub

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Gaurav8302/AROHANN.git
cd AROHANN
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with:
# FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json

# Start the server
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file with Firebase config:
# VITE_FIREBASE_API_KEY=your_api_key
# VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
# VITE_FIREBASE_DATABASE_URL=your_database_url
# VITE_FIREBASE_PROJECT_ID=your_project_id
# VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
# VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
# VITE_FIREBASE_APP_ID=your_app_id

# Start development server
npm run dev
```

Frontend will run at `http://localhost:5173`

### 4. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📖 Documentation

Comprehensive documentation is available in the `docs` folder:

- **[SETUP.md](./SETUP.md)** - Detailed installation and configuration guide
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment instructions
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Contribution guidelines
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Testing procedures

### API Documentation

The API is documented using OpenAPI/Swagger. Once the backend is running, visit:
- Interactive API Docs: http://localhost:8000/docs
- Alternative UI: http://localhost:8000/redoc

### Key Endpoints

```
GET  /                          # Health check
POST /api/predict               # Predict dropout risk for student
GET  /api/students              # Get all students (writes to Firebase)
GET  /api/students/{id}         # Get specific student data
POST /api/simulate              # Run what-if scenarios
GET  /api/dashboard/stats       # Get dashboard statistics
```

---

## 🧠 Machine Learning Model

### Model Details

- **Algorithm**: Random Forest Classifier
- **Accuracy**: 85%
- **Precision**: 80%
- **Recall**: 82%
- **F1-Score**: 81%

### Input Features

| Feature | Type | Description | Importance |
|---------|------|-------------|------------|
| `attendance` | float | Attendance percentage (0-100) | 🔴 High |
| `cgpa` | float | CGPA (0-10 scale) | 🔴 High |
| `backlogs` | int | Number of failed subjects | 🔴 High |
| `fees_flag` | binary | Fee payment status | 🟡 Medium |
| `suspension_flag` | binary | Disciplinary actions | 🟡 Medium |
| `marks_10th` | float | 10th grade marks | 🟢 Low |
| `marks_12th` | float | 12th grade marks | 🟢 Low |
| `gender` | string | Student gender | 🟢 Low |

### Feature Engineering

The model uses 15+ engineered features including:
- Attendance-CGPA interaction
- Backlog pressure index
- Risk score composites
- Zone-specific indicators
- Behavioral flags

---

## 🚨 Risk Classification System

### Phase Matrix

| Phase | Criteria | Intervention | Stakeholders |
|-------|----------|--------------|--------------|
| 🟢 Green | Attendance ≥ 85%, CGPA ≥ 7.0 | Routine monitoring | None |
| 🟡 Yellow | Attendance 70-85%, CGPA 5.0-7.0 | Counselor watch | Counselor (passive) |
| 🟠 Orange | Attendance 60-70%, CGPA 4.0-5.0 | Phased escalation (3 levels) | Counselor → Mentor → Parents |
| 🔴 Red | Attendance < 60%, CGPA < 4.0 | Immediate action | All stakeholders |

### Orange Phase Escalation

1. **Phase 1**: Counselor notification + one-on-one session
2. **Phase 2**: Mentor engaged + psychological assessment
3. **Phase 3**: Parents contacted + joint intervention meeting

---

## 🎥 Live Demo

**Production URL**: [https://aarohan.vercel.app](https://aarohan.vercel.app)

**Backend API**: [https://arohann.onrender.com](https://arohann.onrender.com)

**Test Credentials** (if authentication is enabled):
- Username: `demo@aarohan.edu`
- Password: `demo123`

---

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all React components
- Write tests for new features
- Update documentation as needed
- Ensure code passes linting checks

---

## 🧪 Testing

Run the test suite:

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing procedures.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 👥 Team

**AAROHAN Development Team** - Smart India Hackathon 2025

**Repository**: [github.com/Gaurav8302/AROHANN](https://github.com/Gaurav8302/AROHANN)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Gaurav8302/AROHANN/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gaurav8302/AROHANN/discussions)
- **Email**: support@aarohan.edu (replace with actual support email)

---

## 🙏 Acknowledgments

- Smart India Hackathon 2025 organizers
- Educational institutions that provided feedback
- Open-source community (scikit-learn, FastAPI, React)
- Students and counselors who helped shape this system

---

## 🏷️ Keywords

`AI` `Machine Learning` `Education Technology` `Dropout Prediction` `Student Analytics` `Early Warning System` `FastAPI` `React` `Firebase` `Python` `TypeScript` `Smart India Hackathon` `Government Project`

---

<div align="center">

**Built with ❤️ for accessible, equitable education**

*AAROHAN - Empowering institutions to prevent dropouts through intelligent intervention*

</div>
