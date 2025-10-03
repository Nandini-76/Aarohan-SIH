# AAROHAN Deployment Guide

Complete guide for deploying AAROHAN Student Dropout Prediction System to production.

## 📋 Table of Contents

- [Deployment Architecture](#deployment-architecture)
- [Prerequisites](#prerequisites)
- [Backend Deployment (Render.com)](#backend-deployment-rendercom)
- [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
- [Database Setup (MongoDB Atlas)](#database-setup-mongodb-atlas)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Testing Deployment](#testing-deployment)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Deployment Architecture

AAROHAN uses a modern, scalable microservices architecture:

```
┌─────────────────┐
│   Vercel CDN    │  ← Frontend (React + Vite)
│  (Edge Network) │     Static assets, global delivery
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────┐
│  Render.com     │  ← Backend (FastAPI + Python)
│  Web Service    │     API endpoints, ML predictions
└────────┬────────┘
         │ MongoDB Driver
         ↓
┌─────────────────┐
│ MongoDB Atlas   │  ← Database
│  Cloud Cluster  │     Student data, predictions
└─────────────────┘
```

**Benefits**:
- ✅ **Automatic scaling** on both platforms
- ✅ **Zero-downtime deployments** with rollback capability
- ✅ **Global CDN** for fast frontend delivery
- ✅ **Free tier available** for prototypes/testing
- ✅ **HTTPS by default** on all endpoints

---

## 📋 Prerequisites

Before deployment, ensure you have:

- [ ] **GitHub Account** with repository access
- [ ] **Vercel Account** (free tier available) - [Sign up](https://vercel.com/signup)
- [ ] **Render Account** (free tier available) - [Sign up](https://render.com/register)
- [ ] **MongoDB Atlas Account** (free tier M0 cluster) - [Sign up](https://www.mongodb.com/cloud/atlas/register)
- [ ] **Git repository** with AAROHAN codebase pushed

---

## 🖥️ Backend Deployment (Render.com)

### Step 1: Create Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"** and authorize Render to access your GitHub
4. Choose your AAROHAN repository

### Step 2: Configure Service Settings

**Basic Settings**:
- **Name**: `aarohan-backend` (or your preferred name)
- **Region**: Choose closest to your users (e.g., Oregon, Frankfurt, Singapore)
- **Branch**: `main` (or your production branch)
- **Root Directory**: Leave blank (Render will use `render.yaml`)
- **Runtime**: `Python 3`

**Build Settings**:
- **Build Command**: 
  ```bash
  pip install -r backend/requirements.txt
  ```

- **Start Command**:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### Step 3: Set Environment Variables

Add these environment variables in Render dashboard:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11` | Python runtime version |
| `MONGO_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/` | From MongoDB Atlas (see below) |
| `DB_NAME` | `aarohan_production` | Database name |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Your Vercel URL (add after frontend deployment) |

**Optional Variables**:
| Key | Value | Purpose |
|-----|-------|---------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `ML_MODEL_PATH` | `app/models/rf_pipeline_broad.joblib` | Model file path |

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install Python dependencies
   - Start the FastAPI server
   - Assign a public URL (e.g., `https://aarohan-backend.onrender.com`)

3. **Wait 3-5 minutes** for initial build

4. **Verify deployment**:
   - Visit `https://your-backend.onrender.com/`
   - Should see: `{"status": "ok", "message": "AAROHAN API is running"}`

### Step 5: Configure Auto-Deploy (Optional)

- Enable **"Auto-Deploy"** to automatically redeploy on Git push
- Render will rebuild on every commit to `main` branch

---

## 🌐 Frontend Deployment (Vercel)

### Step 1: Import Project

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the framework

### Step 2: Configure Build Settings

**Project Settings**:
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Build Command**: 
  ```bash
  npm run build
  ```
- **Output Directory**: `dist`
- **Install Command**: `npm install` (auto-detected)

### Step 3: Set Environment Variables

Add in Vercel project settings → Environment Variables:

| Key | Value | Notes |
|-----|-------|-------|
| `VITE_API_BASE_URL` | `https://your-backend.onrender.com` | Backend URL from Render |

### Step 4: Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Install npm dependencies
   - Build production bundle
   - Deploy to global CDN
   - Assign URL (e.g., `https://aarohan-student-prediction.vercel.app`)

3. **Wait 2-3 minutes** for build

4. **Verify deployment**:
   - Visit your Vercel URL
   - Should see AAROHAN landing page
   - Test dashboard navigation

### Step 5: Update Backend CORS

**Important**: Now update your Render backend environment variable:

1. Go back to Render dashboard
2. Update `FRONTEND_URL` with your Vercel URL:
   ```
   https://aarohan-student-prediction.vercel.app
   ```
3. Render will automatically redeploy with new CORS settings

---

## 🗄️ Database Setup (MongoDB Atlas)

### Step 1: Create Cluster

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click **"Build a Database"**
3. Choose **"M0 Free"** tier
4. Select **Cloud Provider** (AWS recommended) and **Region**
5. Name cluster: `aarohan-cluster`
6. Click **"Create"**

### Step 2: Configure Network Access

1. Go to **"Network Access"** tab
2. Click **"Add IP Address"**
3. Choose **"Allow Access from Anywhere"** (0.0.0.0/0)
   - *For production, restrict to Render's IP ranges*
4. Click **"Confirm"**

### Step 3: Create Database User

1. Go to **"Database Access"** tab
2. Click **"Add New Database User"**
3. Authentication Method: **Password**
4. Username: `aarohan_admin`
5. Password: Generate strong password (save securely!)
6. Database User Privileges: **"Atlas admin"**
7. Click **"Add User"**

### Step 4: Get Connection String

1. Go to **"Database"** tab
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Driver: **Python**, Version: **3.11 or later**
5. Copy connection string:
   ```
   mongodb+srv://aarohan_admin:<password>@aarohan-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password
7. Add this to Render environment variables as `MONGO_URI`

### Step 5: Create Database and Collections

Connect to MongoDB Atlas and create:

**Database**: `aarohan_production`

**Collections**:
- `students` - Student profiles
- `predictions` - Risk predictions history
- `interventions` - Intervention tracking
- `simulations` - What-if simulation results

---

## 🔐 Environment Variables Reference

### Backend (Render)

Create a `.env` file for local development (don't commit!):

```bash
# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=aarohan_production

# CORS
FRONTEND_URL=http://localhost:5173,https://your-app.vercel.app

# Optional
LOG_LEVEL=INFO
ML_MODEL_PATH=app/models/rf_pipeline_broad.joblib
PYTHON_VERSION=3.11
```

### Frontend (Vercel)

Create `.env` file in `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

For production, set in Vercel dashboard:
```bash
VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## 💻 Local Development

### Backend Local Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=aarohan_dev
FRONTEND_URL=http://localhost:5173
EOF

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: `http://localhost:8000`

### Frontend Local Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

Frontend available at: `http://localhost:5173`

---

## ✅ Testing Deployment

### 1. Backend Health Check

```bash
curl https://your-backend.onrender.com/

# Expected response:
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "version": "2.0",
  "ml_model_loaded": true
}
```

### 2. Test Student Prediction

```bash
curl -X POST https://your-backend.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_no": "TEST001",
    "attendance": 75.0,
    "cgpa": 6.5,
    "backlogs": 2,
    "marks_10th": 75,
    "marks_12th": 78,
    "fees_flag": 0,
    "suspension_flag": 0,
    "gender": "M"
  }'
```

### 3. Frontend Integration Test

1. Open your Vercel URL
2. Navigate to **Dashboard**
3. Check if student data loads
4. Test **Simulation** page
5. Verify risk badges display correctly

### 4. Database Connection Test

Check MongoDB Atlas:
1. Go to **"Collections"** tab
2. Verify data is being written to collections
3. Check prediction records

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: `Module not found` errors

**Solution**:
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > backend/requirements.txt
git add backend/requirements.txt
git commit -m "Update dependencies"
git push
```

**Problem**: MongoDB connection timeout

**Solution**:
- Check MongoDB Atlas IP whitelist includes `0.0.0.0/0`
- Verify `MONGO_URI` is correct in Render environment variables
- Check MongoDB Atlas cluster is active (not paused)

**Problem**: CORS errors in browser

**Solution**:
- Verify `FRONTEND_URL` in Render includes your Vercel URL
- Check for trailing slashes (should be `https://app.vercel.app` not `https://app.vercel.app/`)
- Redeploy backend after updating CORS settings

### Frontend Issues

**Problem**: API calls failing with 404

**Solution**:
- Verify `VITE_API_BASE_URL` is set correctly in Vercel
- Check backend is deployed and running
- Test backend URL directly in browser

**Problem**: Blank page after deployment

**Solution**:
```bash
# Check build logs in Vercel
# Ensure no build errors
# Verify output directory is 'dist'
```

### Performance Issues

**Problem**: Slow API responses

**Solution**:
- Render free tier "spins down" after inactivity
- Consider upgrading to paid tier for always-on instances
- Implement Redis caching for frequently accessed data

---

## 🚀 Production Optimizations

### 1. Custom Domain Setup

**Vercel (Frontend)**:
1. Go to Project Settings → Domains
2. Add your custom domain (e.g., `aarohan.yourdomain.com`)
3. Update DNS records as instructed
4. Vercel auto-provisions SSL certificate

**Render (Backend)**:
1. Go to Service Settings → Custom Domains
2. Add subdomain (e.g., `api.yourdomain.com`)
3. Update CNAME record in DNS
4. Update `FRONTEND_URL` to use custom domain

### 2. Performance Monitoring

**Add monitoring tools**:
- **Sentry** for error tracking
- **LogRocket** for user session replay
- **New Relic** for APM

### 3. Caching Strategy

Implement Redis caching:
```python
# Add to backend
import redis
cache = redis.Redis(host='your-redis-url', port=6379)
```

---

## 📞 Support

If you encounter deployment issues:

- **Backend logs**: Check Render dashboard → Logs tab
- **Frontend logs**: Check Vercel dashboard → Deployments → View logs
- **GitHub Issues**: [Report issues](https://github.com/Gaurav8302/AROHANN/issues)

---

## 🔄 Continuous Deployment

Both Vercel and Render support automatic deployments:

1. **Push to GitHub** → Automatic build triggered
2. **Review deploy preview** (Vercel provides preview URLs for PRs)
3. **Merge to main** → Production deployment
4. **Rollback if needed** (one-click in both dashboards)

---

**Deployment checklist complete! Your AAROHAN system is now live and serving predictions globally.** 🎉