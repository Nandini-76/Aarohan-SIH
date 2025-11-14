# AAROHAN Deployment Guide

Complete guide for deploying AAROHAN to production using Render, Vercel, and Firebase.

---

## 📋 Table of Contents

- [Deployment Overview](#-deployment-overview)
- [Prerequisites](#-prerequisites)
- [Firebase Setup](#-firebase-setup)
- [Backend Deployment (Render)](#-backend-deployment-render)
- [Frontend Deployment (Vercel)](#-frontend-deployment-vercel)
- [Post-Deployment](#-post-deployment)
- [Monitoring & Maintenance](#-monitoring--maintenance)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ Deployment Overview

AAROHAN uses a modern, scalable cloud architecture:

```
┌─────────────────┐
│   Vercel CDN    │  ← Frontend (React + Vite)
│  (Global Edge)  │     Static hosting, instant deployments
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────┐
│  Render.com     │  ← Backend (FastAPI + Python ML)
│  Web Service    │     API endpoints, predictions
└────────┬────────┘
         │ Firebase SDK
         ↓
┌─────────────────┐
│    Firebase     │  ← Database (Realtime Database)
│   Google Cloud  │     Real-time data sync
└─────────────────┘
```

### Why This Stack?

- ✅ **Free Tier Available** - $0 cost for prototypes
- ✅ **Auto-Scaling** - Handles traffic spikes automatically
- ✅ **Global CDN** - Fast loading worldwide
- ✅ **Zero-Downtime Deployments** - Seamless updates
- ✅ **HTTPS by Default** - Secure connections
- ✅ **Git Integration** - Deploy on push

---

## 📋 Prerequisites

Before starting, ensure you have:

### Accounts (all free tiers available)
- [ ] **GitHub Account** - [Sign up](https://github.com/signup)
- [ ] **Render Account** - [Sign up](https://render.com/register)
- [ ] **Vercel Account** - [Sign up](https://vercel.com/signup)
- [ ] **Google Account** for Firebase - [Sign up](https://accounts.google.com/signup)

### Repository
- [ ] Code pushed to GitHub repository
- [ ] All local changes committed
- [ ] `.gitignore` properly configured (no secrets)

### Credentials
- [ ] Firebase service account key
- [ ] Environment variables documented

---

## 🔥 Firebase Setup

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Create a project"** or **"Add project"**
3. **Project name**: `aarohan-production` (or your choice)
4. **Google Analytics**: Optional (can disable for simplicity)
5. Click **"Create project"**

### 2. Enable Realtime Database

1. In the left sidebar, click **"Realtime Database"**
2. Click **"Create Database"**
3. **Location**: Choose closest to your target users
   - Asia: `asia-southeast1`
   - US: `us-central1`
   - Europe: `europe-west1`
4. **Security rules**: Start in **"Locked mode"** (we'll update later)
5. Click **"Enable"**

### 3. Update Security Rules

In the Realtime Database section, go to **"Rules"** tab:

```json
{
  "rules": {
    "students": {
      ".read": true,
      ".write": "auth != null"
    },
    "predictions": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

Click **"Publish"** to save.

**Security Notes:**
- `.read: true` on students allows public dashboard access
- `.write: "auth != null"` requires authentication for writes
- For production, consider more restrictive rules

### 4. Get Firebase Configuration

**For Frontend (Web App Config):**

1. Go to **Project Overview** → Click the **Web icon** (</>)
2. **App nickname**: `aarohan-web`
3. **Don't** check "Also set up Firebase Hosting" (we're using Vercel)
4. Click **"Register app"**
5. **Copy the config object** - you'll need this for Vercel

Example:
```javascript
{
  apiKey: "AIza...",
  authDomain: "aarohan-prod.firebaseapp.com",
  databaseURL: "https://aarohan-prod.firebaseio.com",
  projectId: "aarohan-prod",
  storageBucket: "aarohan-prod.appspot.com",
  messagingSenderId: "123456",
  appId: "1:123456:web:abc123"
}
```

**For Backend (Service Account):**

1. Go to **Project Settings** (gear icon) → **Service Accounts**
2. Click **"Generate new private key"**
3. Click **"Generate key"**
4. Save the JSON file securely (you'll upload this to Render)

---

## 🖥️ Backend Deployment (Render)

### 1. Create Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect account"** and authorize Render to access GitHub
4. Select your `AROHANN` repository

### 2. Configure Service

**Basic Settings:**
- **Name**: `aarohan-backend`
- **Region**: Choose closest to Firebase database location
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r backend/requirements.txt
  ```
- **Start Command**:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Free tier: Select **"Free"** (good for development/testing)
- Production: Select **"Starter"** ($7/month for better performance)

### 3. Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11` | Python runtime |
| `ML_MODEL_PATH` | `app/models/rf_pipeline_broad.joblib` | Model file path |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

**Firebase Service Account:**

For `serviceAccountKey.json`, you have two options:

**Option A: Environment Variable (Recommended)**
1. Copy the entire contents of `serviceAccountKey.json`
2. Add env variable:
   - **Key**: `FIREBASE_SERVICE_ACCOUNT`
   - **Value**: Paste the JSON content
3. Update `backend/app/firebase_config.py` to read from env var:

```python
import os
import json
import firebase_admin
from firebase_admin import credentials, db

# Get service account from environment variable
service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
if service_account_json:
    cred = credentials.Certificate(json.loads(service_account_json))
else:
    cred = credentials.Certificate('serviceAccountKey.json')

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-project.firebaseio.com'
})
```

**Option B: Secret Files**
1. Go to **"Secret Files"** section in Render
2. **Filename**: `serviceAccountKey.json`
3. **Contents**: Paste the JSON
4. This will be available at `/etc/secrets/serviceAccountKey.json`

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone repository
   - Install dependencies
   - Start the application
   - Assign a public URL: `https://aarohan-backend.onrender.com`

3. **Wait 3-5 minutes** for initial build
4. Check **"Logs"** tab for progress

### 5. Verify Deployment

Once deployed, test the backend:

```bash
# Health check
curl https://your-backend.onrender.com/

# Expected response:
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "ml_model_loaded": true
}
```

### 6. Enable Auto-Deploy

In service settings:
- Turn on **"Auto-Deploy"** → Deploys automatically on Git push to `main`

---

## 🌐 Frontend Deployment (Vercel)

### 1. Import Project

1. Log in to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. **Import Git Repository** → Select your `AROHANN` repo
4. Click **"Import"**

### 2. Configure Project

**Framework Preset:** Vite (auto-detected)

**Build & Development Settings:**
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (auto-detected)
- **Output Directory**: `dist` (auto-detected)
- **Install Command**: `npm install` (auto-detected)

### 3. Environment Variables

Click **"Environment Variables"** section:

Add the Firebase config from Step 4 of Firebase Setup:

| Variable Name | Value | Example |
|---------------|-------|---------|
| `VITE_FIREBASE_API_KEY` | `<your-api-key>` | `AIzaSyC...` |
| `VITE_FIREBASE_AUTH_DOMAIN` | `<project-id>.firebaseapp.com` | `aarohan-prod.firebaseapp.com` |
| `VITE_FIREBASE_DATABASE_URL` | `https://<project-id>.firebaseio.com` | `https://aarohan-prod.firebaseio.com` |
| `VITE_FIREBASE_PROJECT_ID` | `<project-id>` | `aarohan-prod` |
| `VITE_FIREBASE_STORAGE_BUCKET` | `<project-id>.appspot.com` | `aarohan-prod.appspot.com` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | `<sender-id>` | `123456789` |
| `VITE_FIREBASE_APP_ID` | `<app-id>` | `1:123456:web:abc` |
| `VITE_API_URL` | `https://your-backend.onrender.com` | Backend URL from Render |

**Important:**
- Apply to: **Production, Preview, and Development**
- Click **"Add"** for each variable

### 4. Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Install dependencies
   - Build the React app
   - Deploy to global CDN
   - Assign URL: `https://your-project.vercel.app`

3. **Wait 2-3 minutes** for deployment

### 5. Verify Deployment

Visit your Vercel URL - the dashboard should load with student data.

### 6. Custom Domain (Optional)

To use a custom domain (e.g., `aarohan.yourdomain.com`):

1. Go to **Project Settings** → **Domains**
2. Click **"Add"**
3. Enter your domain
4. Follow DNS configuration instructions
5. Vercel will auto-provision SSL certificate

### 7. Enable Auto-Deploy

- Vercel auto-deploys on every push to `main`
- Preview deployments for every PR

---

## 🚀 Post-Deployment

### 1. Update Frontend with Backend URL

Make sure `VITE_API_URL` in Vercel points to your Render backend:

```
VITE_API_URL=https://aarohan-backend.onrender.com
```

If you update this, Vercel will auto-redeploy.

### 2. Test End-to-End

1. Visit your Vercel URL
2. Dashboard should load student data from Firebase
3. Test predictions by clicking student profiles
4. Check browser console for errors

### 3. Configure CORS

In `backend/app/main.py`, ensure CORS allows your Vercel domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "http://localhost:5173"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to trigger redeployment.

---

## 📊 Monitoring & Maintenance

### Render Monitoring

**Logs:**
- View real-time logs in Render dashboard
- Download logs for debugging

**Metrics:**
- CPU usage
- Memory usage
- Request latency

**Health Checks:**
Render automatically pings your `/` endpoint to ensure uptime.

### Vercel Analytics

**Built-in Analytics:**
- Page views
- Unique visitors
- Top pages
- Performance metrics

Enable in: Project Settings → Analytics

### Firebase Monitoring

**Database Usage:**
- Firebase Console → Realtime Database → Usage tab
- Monitor reads/writes
- Storage size

**Free Tier Limits:**
- 1 GB stored
- 10 GB/month downloaded
- 100 simultaneous connections

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: Build fails on Render**

*Error:* `Could not find a version that satisfies the requirement scikit-learn...`

**Solution:**
- Check `requirements.txt` has correct package versions
- Ensure Python version is specified: `PYTHON_VERSION=3.11`
- Try pinning scikit-learn version: `scikit-learn==1.3.0`

**Issue: Service crashes on startup**

*Error:* `ModuleNotFoundError: No module named 'app'`

**Solution:**
- Verify start command includes `cd backend`:
  ```bash
  cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Issue: Firebase authentication fails**

*Error:* `Could not load credentials from serviceAccountKey.json`

**Solution:**
- Check `FIREBASE_SERVICE_ACCOUNT` env variable is set
- Verify JSON is valid (use JSON validator)
- Ensure no extra whitespace in env variable

### Frontend Issues

**Issue: Build fails on Vercel**

*Error:* `Module not found: Can't resolve 'firebase'`

**Solution:**
- Ensure `firebase` is in `dependencies`, not `devDependencies` in `package.json`
- Run `npm install firebase --save` and commit

**Issue: Firebase config not found**

*Error:* `Firebase: No Firebase App '[DEFAULT]' has been created`

**Solution:**
- Verify all `VITE_FIREBASE_*` env variables are set in Vercel
- Check variable names start with `VITE_` (required for Vite)
- Redeploy after adding env variables

**Issue: CORS errors**

*Error:* `Access to fetch at 'https://backend...' from origin 'https://frontend...' has been blocked by CORS`

**Solution:**
- Add Vercel domain to `allow_origins` in backend CORS config
- Redeploy backend after changes

### Render Free Tier Sleeping

**Issue:** Backend takes 30-60 seconds to respond on first request

**Why:** Render free tier spins down after 15 minutes of inactivity

**Solutions:**

1. **Upgrade to Paid Plan** ($7/month for always-on)

2. **Keep-Alive Ping** (15-minute intervals):
   - Use a service like [UptimeRobot](https://uptimerobot.com/) (free)
   - Ping: `https://your-backend.onrender.com/` every 14 minutes

3. **User Communication:**
   - Add loading message: "Waking up server, please wait..."
   - First load may be slow, subsequent loads instant

---

## 🎯 Deployment Checklist

Use this to verify complete deployment:

### Pre-Deployment
- [ ] All code committed and pushed to GitHub
- [ ] `.env` files not committed (check `.gitignore`)
- [ ] All tests passing locally
- [ ] Documentation updated

### Firebase
- [ ] Project created
- [ ] Realtime Database enabled
- [ ] Security rules configured
- [ ] Web app registered
- [ ] Service account key generated

### Backend (Render)
- [ ] Service created and deployed
- [ ] Environment variables configured
- [ ] Firebase credentials loaded
- [ ] Health check endpoint responds
- [ ] Logs show no errors
- [ ] Auto-deploy enabled

### Frontend (Vercel)
- [ ] Project imported and deployed
- [ ] All Firebase env variables set
- [ ] Backend URL configured
- [ ] Site loads without errors
- [ ] Can fetch student data
- [ ] Predictions work
- [ ] Auto-deploy enabled

### Post-Deployment
- [ ] CORS configured for Vercel domain
- [ ] End-to-end testing complete
- [ ] Monitoring enabled
- [ ] Team has access credentials
- [ ] Documentation URL shared

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Firebase Docs**: https://firebase.google.com/docs
- **GitHub Issues**: https://github.com/Gaurav8302/AROHANN/issues

---

<div align="center">

**Deployment Complete! 🎉**

Your AAROHAN system is now live and ready for production use!

</div>
