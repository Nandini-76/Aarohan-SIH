# 🔥 Firebase Integration Setup Guide

## Overview

This guide explains how to configure Firebase Realtime Database to ensure your application data persists even when the backend (Render free tier) goes to sleep. This is crucial for judges and evaluators who need to see your latest predictions at any time.

## Architecture

```
Backend (FastAPI on Render) → Writes to Firebase Realtime Database
                                       ↓
Frontend (React on Vercel) ← Reads from Firebase Realtime Database
```

**Key Benefits:**
- ✅ Backend writes predictions to Firebase whenever active
- ✅ Frontend always displays latest data from Firebase
- ✅ Judges can view predictions even when backend is sleeping
- ✅ No data loss during backend cold starts
- ✅ Real-time updates when backend is active

---

## 🔧 Part 1: Backend Configuration (Render)

### Step 1: Set Environment Variables on Render

1. Go to your **Render Dashboard** → Select your backend service
2. Navigate to **Environment** tab
3. Add the following environment variables:

```bash
FIREBASE_PROJECT_ID=aarohan-f7274
FIREBASE_PRIVATE_KEY_ID=8e8b7c497fd44032463720aa0dce88ebf35f1708
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDJObH1k0g1rMMe
xna4VXl4JHAWYWH3bc0SrpaNWVExqDUGSpKaSlPoWFM+RQ3T8z5PbzUBYv5mg21V
XMIzJQvijRyH+2Xgn++r5qg1vG0lew7FQswUNfFzwrEN8WmcAQ8Ym26eKNFMw2j0
zQzBPWdPy4luS+RV98If1stfQgGXvMp+VfV2Bax9AaLaajhS6cf+ZQWQ2GnkxMyz
7U5csDqYfWVm9GXsVV8eLk0keFGbzfvDWssDBZ+OkgAMg/PJSa3++X0FD0n6PG4C
Mw0YfsFbiCmGrbODEhnTE02iy9ZDbwuBGMJheOz1AwAjObxLKpi3I7ogqwC5gRfg
56ztYgh3AgMBAAECggEASJkos+V1xWu1n9pRhdLMtsRKrkBnJGo4dReJGKkTSpuZ
udHYz5KmcCrBqbMnOINHRUhlcsEg8KJVJVmIdQRWI9/uXb8dM+vv//CBWpXHOSEL
JK8jSt1lZfLlhxbEl/Sn2iRlxekLDitoJ/38rpE1P0w7IpB96mgvYOZRTGZXhcMC
6t5a4fSUPQAxvJAFEIDisKpR+XS19JLcga9t7jhTmvwALd5pdlOrPvKzOva7RGw9
gUhtPcxQpMgT47Px7/wrxfftAbez5BFQpArLDEtDnIKa8OMtlOgixSD8LDpyp8t+
gpTX7ccN1D6iSFA/dMMe6TOkRI+wSN3mZe1qiK/rHQKBgQDnryO0ifI0qmaVRDGL
nQ5NhRosGg6cyrLsCILLLDrFdSyYciI5fg9suq/RdQL/1R08766ImB/e2CQM87FC
gwpUp180JeCo9W0LJ/wpHF3lNc31REeQLepIxpWTNGWuO/MmO3sp+60I50OITysu
ZiokQxmb39udtrh0Vhk5CRXc/QKBgQDeWDF+NI18mhmeXl9q9+RawADxS/iCj1sS
rd/e9SrKb3jOBM/Ba0n5RJmFkZY98doykVNUzgul52BLewEiML0FZgyYykGxuNRA
KgKrtz5LVo91ohTokWUUWiwh5GQOox7/C34B3jLhxXjvXWiLtRX7i1EtJ4YmHnYJ
VaMJY/WvgwKBgCJi9TqzirZUYDthTrU5D0lkKvlGuMp+r0WnEbqUCvkJph/OONQt
qJ5rqvK8mkBcYiWMMWxmn7xUei1N8g48IsljuhakVI7fNlsEiUGUyz7c2H/BrZlx
pyc8CjE6Aql0jmcrRuF5UDpVEMnnbjJJyZFuQBvJgvAKkZ/6s22qsosFAoGAHQK2
2ney6koVA6PeoU9c3TZmKRW3hBl+UY6cQjQM9ELdKUxZayw7h6maumHHj6eJx8VM
cSk9PdVVrCONf0+KqjSpehoRvkWWdBTHKm6LUzslFr0iK0IlRSWK0pVBNOO1vKNc
OpQqYWjpoZm3dVsYVizUV6brive4gPlKf4QqX08CgYBK5Kt52gHbfpqiTJgT9J15
8/tXI1uTUYNlpcTCqJORYV4RMAV40S1iK3nC2wURLy+PpbELj9Xhtun89sKGRT4h
egLceCkYZW0tfn7dkqZ6Sr25N1YtdB0BD9ITdCHWKxbKyayXA+PYuWZHl5I/aRjX
pgGSFQiV1FJgKjJYFYY86g==
-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@aarohan-f7274.iam.gserviceaccount.com
FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
```

**Important Notes:**
- ⚠️ Keep the entire private key in quotes (including newlines)
- ⚠️ Render will automatically handle the multiline key if wrapped in quotes
- ✅ Click "Save Changes" after adding all variables

### Step 2: Deploy Backend

After setting environment variables, trigger a new deployment:
- Render will automatically redeploy when you push to your repository
- Or manually trigger redeploy from Render dashboard

### Step 3: Verify Backend Firebase Connection

Visit: `https://your-backend.onrender.com/firebase/status`

Expected response:
```json
{
  "firebase_initialized": true,
  "environment_vars_configured": true,
  "project_id": "aarohan-f7274",
  "database_url": "https://aarohan-f7274-default-rtdb.firebaseio.com",
  "status": "connected"
}
```

---

## ⚛️ Part 2: Frontend Configuration (Vercel)

### Step 1: Set Environment Variables on Vercel

1. Go to your **Vercel Dashboard** → Select your project
2. Navigate to **Settings** → **Environment Variables**
3. Add the following variables (for all environments: Production, Preview, Development):

```bash
VITE_FIREBASE_API_KEY=AIzaSyCIl-lS6088wyntMipdf8bZJADtIyqsTtU
VITE_FIREBASE_AUTH_DOMAIN=aarohan-f7274.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=aarohan-f7274
VITE_FIREBASE_STORAGE_BUCKET=aarohan-f7274.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=667188000435
VITE_FIREBASE_APP_ID=1:667188000435:web:75857ad32cb591460022c6
```

**Note:** Since you're using Vite, all Firebase environment variables must be prefixed with `VITE_`

### Step 2: Install Firebase Package

Run in your frontend directory:

```bash
npm install firebase
```

or if using bun:

```bash
bun add firebase
```

### Step 3: Create Local .env File (Optional for local development)

Create `frontend/.env.local`:

```bash
VITE_FIREBASE_API_KEY=AIzaSyCIl-lS6088wyntMipdf8bZJADtIyqsTtU
VITE_FIREBASE_AUTH_DOMAIN=aarohan-f7274.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=aarohan-f7274
VITE_FIREBASE_STORAGE_BUCKET=aarohan-f7274.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=667188000435
VITE_FIREBASE_APP_ID=1:667188000435:web:75857ad32cb591460022c6
```

### Step 4: Deploy Frontend

```bash
git add .
git commit -m "Add Firebase integration"
git push
```

Vercel will automatically redeploy with the new environment variables.

---

## 🧪 Part 3: Testing the Integration

### Test Backend → Firebase Connection

1. **Run a simulation:**
   ```bash
   POST https://your-backend.onrender.com/simulate
   ```

2. **Check Firebase Console:**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Select project: `aarohan-f7274`
   - Navigate to **Realtime Database**
   - You should see data at `/latestData`

3. **Verify with API:**
   ```bash
   GET https://your-backend.onrender.com/firebase/status
   ```

### Test Frontend → Firebase Connection

1. Open your deployed frontend: `https://your-app.vercel.app`
2. Open browser console (F12)
3. Look for: `"Firebase initialized successfully"`
4. Run a simulation from the frontend
5. Data should appear instantly (real-time sync)

### Test Backend Sleep Scenario

1. Wait 15 minutes for Render backend to sleep (free tier)
2. Visit your frontend
3. **You should still see the last simulation data** from Firebase
4. This proves judges can view results even when backend is sleeping

---

## 📊 Firebase Data Structure

Your Firebase Realtime Database will have this structure:

```json
{
  "latestData": {
    "timestamp": "2025-10-05T01:00:00Z",
    "latest_simulation": {
      "enrollment_no": "2023ENG001",
      "final_phase": "Yellow",
      "risk_level": "Medium Risk",
      "ml_probability": 0.67,
      "rule_override": false
    },
    "backend_status": "active",
    "lastUpdated": "2025-10-05T01:00:00Z"
  },
  "students": {
    "2023ENG001": {
      "enrollment_no": "2023ENG001",
      "prediction": "Yellow",
      "timestamp": "2025-10-05T01:00:00Z"
    }
  },
  "batchPredictions": {
    "predictions": [...],
    "count": 150,
    "timestamp": "2025-10-05T01:00:00Z"
  }
}
```

---

## 🔍 Using Firebase in Your Components

### Example: Display Latest Data in Dashboard

```tsx
import { useEffect, useState } from "react";
import { listenToLatestData } from "@/services/firebase";

export default function Dashboard() {
  const [firebaseData, setFirebaseData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Listen to Firebase updates
    const unsubscribe = listenToLatestData((data) => {
      setFirebaseData(data);
      setIsLoading(false);
    });

    // Cleanup listener on unmount
    return () => unsubscribe();
  }, []);

  if (isLoading) {
    return <div>Loading latest data...</div>;
  }

  if (!firebaseData) {
    return <div>No data available</div>;
  }

  return (
    <div>
      <h2>Latest Prediction Results</h2>
      <p>Last Updated: {firebaseData.lastUpdated}</p>
      <p>Backend Status: {firebaseData.backend_status}</p>
      
      {firebaseData.latest_simulation && (
        <div>
          <h3>Latest Simulation</h3>
          <p>Student: {firebaseData.latest_simulation.enrollment_no}</p>
          <p>Risk Level: {firebaseData.latest_simulation.risk_level}</p>
          <p>Phase: {firebaseData.latest_simulation.final_phase}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Firebase not initialized
```json
{
  "firebase_initialized": false,
  "status": "not_configured"
}
```

**Solution:**
1. Check all environment variables are set correctly on Render
2. Verify private key has proper newlines (use quotes)
3. Redeploy the backend service
4. Check logs: Render Dashboard → Logs

---

**Problem:** Firebase connection timeout

**Solution:**
1. Check Firebase Database URL is correct
2. Ensure Firebase Realtime Database is created in Firebase Console
3. Check Firebase Database Rules allow read/write access

---

### Frontend Issues

**Problem:** `Firebase not initialized`

**Solution:**
1. Verify all `VITE_` prefixed environment variables are set in Vercel
2. Redeploy frontend after adding variables
3. Check browser console for detailed error messages

---

**Problem:** Data not updating in real-time

**Solution:**
1. Check browser console for Firebase connection errors
2. Verify you're calling `listenToLatestData()` correctly
3. Ensure you're not blocking the listener (no ad blockers affecting Firebase)

---

## 🎯 API Endpoints Added

### Backend Endpoints

1. **Check Firebase Status**
   ```
   GET /firebase/status
   ```

2. **Manually Update Firebase**
   ```
   POST /firebase/update
   ```

### Automatic Updates

The `/simulate` endpoint now automatically pushes data to Firebase after each prediction.

---

## 🔐 Security Notes

- ✅ Backend uses Service Account credentials (server-side only)
- ✅ Frontend uses public Firebase config (client-side safe)
- ⚠️ Ensure Firebase Database Rules restrict write access to authenticated users
- ⚠️ Never commit `.env` files with credentials to Git
- ✅ Environment variables on Render/Vercel are encrypted

---

## 📱 Firebase Console Access

Access your Firebase Console at:
https://console.firebase.google.com/project/aarohan-f7274/database

Here you can:
- View real-time data updates
- Monitor read/write operations
- Export data for analysis
- Set up database rules and security

---

## ✅ Success Checklist

- [ ] Backend environment variables configured on Render
- [ ] Backend shows `firebase_initialized: true`
- [ ] Frontend environment variables configured on Vercel
- [ ] Firebase package installed in frontend
- [ ] Can see data in Firebase Console after simulation
- [ ] Frontend displays Firebase data correctly
- [ ] Data persists when backend sleeps

---

## 🚀 Deployment Commands

### Backend (from backend directory)
```bash
# Already handled by Render auto-deploy
# Just ensure environment variables are set
```

### Frontend (from frontend directory)
```bash
# Install dependencies
npm install

# Build and deploy (Vercel handles automatically)
git push
```

---

## 📚 Additional Resources

- [Firebase Realtime Database Docs](https://firebase.google.com/docs/database)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)

---

**Questions or Issues?** Check the logs:
- **Backend:** Render Dashboard → Your Service → Logs
- **Frontend:** Browser Console (F12)
- **Firebase:** Firebase Console → Usage

---

## 🎉 You're All Set!

Your application now has persistent data storage via Firebase. Judges and evaluators can view your predictions 24/7, even when the backend is sleeping on Render's free tier!
