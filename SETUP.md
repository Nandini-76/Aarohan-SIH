# AAROHAN Setup Guide

Complete guide for setting up AAROHAN Student Dropout Prediction System for local development.

---

## 📋 Table of Contents

- [System Requirements](#-system-requirements)
- [Initial Setup](#-initial-setup)
- [Backend Configuration](#-backend-configuration)
- [Frontend Configuration](#-frontend-configuration)
- [Firebase Setup](#-firebase-setup)
- [Running the Application](#-running-the-application)
- [Troubleshooting](#-troubleshooting)

---

## 💻 System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 2 GB free space
- **Internet**: Required for Firebase and API calls

### Software Requirements

- **Python**: 3.9 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 16.0 or higher ([Download](https://nodejs.org/))
- **Git**: Latest version ([Download](https://git-scm.com/downloads))
- **Code Editor**: VS Code recommended ([Download](https://code.visualstudio.com/))

### Optional Tools

- **Postman**: For API testing ([Download](https://www.postman.com/downloads/))
- **MongoDB Compass**: For database visualization (if using MongoDB)

---

## 🚀 Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Gaurav8302/AROHANN.git
cd AROHANN
```

### 2. Verify Installations

```bash
# Check Python version
python --version  # Should show 3.9 or higher

# Check Node.js version
node --version  # Should show 16.0 or higher

# Check npm version
npm --version  # Should show 8.0 or higher
```

---

## 🐍 Backend Configuration

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected Installation:**
- fastapi
- uvicorn
- pandas
- scikit-learn
- firebase-admin
- python-multipart
- pydantic
- And other dependencies...

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# backend/.env
FIREBASE_CREDENTIALS_PATH=./serviceAccountKey.json
PYTHON_VERSION=3.9
LOG_LEVEL=INFO
ML_MODEL_PATH=app/models/rf_pipeline_broad.joblib
```

### 5. Set Up Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Save the JSON file as `serviceAccountKey.json` in the `backend` directory

**⚠️ IMPORTANT**: Never commit `serviceAccountKey.json` to Git! It's already in `.gitignore`.

### 6. Verify ML Model

Check that the trained model exists:

```bash
ls app/models/rf_pipeline_broad.joblib
```

If missing, you'll need to train the model (see [Model Training](#model-training) section).

### 7. Test Backend Setup

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000 - you should see:
```json
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "version": "2.0",
  "ml_model_loaded": true
}
```

---

## ⚛️ Frontend Configuration

### 1. Navigate to Frontend Directory

```bash
cd ../frontend  # From backend directory
# OR
cd frontend  # From project root
```

### 2. Install Dependencies

```bash
npm install
```

**Expected Installation:**
- react
- react-dom
- typescript
- vite
- tailwindcss
- @radix-ui components
- firebase
- And other dependencies...

### 3. Configure Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
# frontend/.env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://your_project.firebaseio.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_API_URL=http://localhost:8000
```

**How to get Firebase config values:**
1. Firebase Console → Project Settings
2. Scroll to "Your apps" section
3. Click on the Web app (</> icon)
4. Copy the config values

### 4. Test Frontend Setup

```bash
npm run dev
```

Visit http://localhost:5173 - the React app should load.

---

## 🔥 Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Enter project name: `aarohan` (or your choice)
4. Follow the setup wizard

### 2. Enable Realtime Database

1. In Firebase Console, click **Realtime Database**
2. Click **Create Database**
3. Choose location closest to your users
4. Start in **Test Mode** (for development)

**Security Rules (for production, update these):**
```json
{
  "rules": {
    ".read": "auth != null",
    ".write": "auth != null",
    "students": {
      ".read": true,
      ".write": "auth != null"
    }
  }
}
```

### 3. Register Web App

1. In Project Overview, click the **Web** icon (</>)
2. Register app with nickname: `aarohan-web`
3. Copy the config object - you'll need this for frontend `.env`

### 4. Generate Service Account Key

1. Project Settings → Service Accounts
2. Click **Generate New Private Key**
3. Save as `backend/serviceAccountKey.json`

---

## 🎯 Running the Application

### Full Stack Development Setup

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### Testing the Integration

1. Open http://localhost:5173 in your browser
2. The dashboard should load student data
3. Check browser console for any errors
4. Test predictions by clicking on student profiles

---

## 🔧 Additional Configuration

### Model Training (Optional)

If you need to retrain the ML model:

```bash
cd backend/app/models
python RF-training-script.py
```

This will:
1. Load training data from `data/merged_dataset.csv`
2. Train the Random Forest model
3. Save the model as `rf_pipeline_broad.joblib`

### Database Seeding

To populate Firebase with initial student data:

```bash
cd backend
python app/populate_firebase.py
```

Or simply call the API endpoint:
```bash
curl http://localhost:8000/api/students
```

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: `ModuleNotFoundError`**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: `Firebase authentication failed`**
```bash
# Solution: Check serviceAccountKey.json exists
ls serviceAccountKey.json

# Verify FIREBASE_CREDENTIALS_PATH in .env
cat .env | grep FIREBASE
```

**Issue: `ML model not found`**
```bash
# Solution: Check model file exists
ls app/models/rf_pipeline_broad.joblib

# If missing, train the model
cd app/models
python RF-training-script.py
```

### Frontend Issues

**Issue: `Cannot connect to backend`**
```bash
# Solution: Check VITE_API_URL in .env
cat .env | grep VITE_API_URL

# Ensure backend is running
curl http://localhost:8000
```

**Issue: `Firebase configuration error`**
```bash
# Solution: Verify all Firebase env variables are set
cat .env | grep VITE_FIREBASE

# Check for missing variables
npm run dev  # Look for detailed error in console
```

**Issue: `npm install fails`**
```bash
# Solution: Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port Conflicts

**Backend port 8000 already in use:**
```bash
# Option 1: Kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Option 2: Use a different port
uvicorn app.main:app --reload --port 8001
```

**Frontend port 5173 already in use:**
```bash
# Vite will automatically try the next available port
# Or specify a custom port:
npm run dev -- --port 3000
```

---

## 📚 Next Steps

After setup is complete:

1. **Read the Documentation**: Check out [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment
2. **Run Tests**: See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for testing procedures
3. **Contribute**: Review [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines
4. **Explore the Code**: Start with `backend/app/main.py` and `frontend/src/App.tsx`

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/Gaurav8302/AROHANN/issues)
2. Search existing discussions
3. Open a new issue with:
   - Your operating system
   - Python/Node.js versions
   - Error messages (full stack trace)
   - Steps to reproduce

---

## ✅ Setup Checklist

Use this checklist to verify your setup:

- [ ] Python 3.9+ installed and verified
- [ ] Node.js 16+ installed and verified
- [ ] Repository cloned successfully
- [ ] Backend virtual environment created and activated
- [ ] Backend dependencies installed
- [ ] `serviceAccountKey.json` configured
- [ ] Backend `.env` file created
- [ ] Frontend dependencies installed
- [ ] Frontend `.env` file created with Firebase config
- [ ] Backend runs successfully on port 8000
- [ ] Frontend runs successfully on port 5173
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Dashboard loads without errors
- [ ] Firebase connection verified

---

<div align="center">

**Setup Complete! 🎉**

Ready to start developing? Check out the [Contributing Guide](./CONTRIBUTING.md)!

</div>
