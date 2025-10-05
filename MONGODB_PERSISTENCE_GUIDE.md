# MongoDB Data Persistence Setup Guide

## 🎯 Overview

This implementation ensures your frontend **always displays data**, even when the Render backend is inactive/sleeping. The system uses MongoDB as shared storage where:

1. **Backend** (FastAPI) writes/updates processed data to MongoDB
2. **Frontend** (React) reads data directly from MongoDB using the Data API
3. When backend sleeps → frontend shows the latest cached data from MongoDB

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   MongoDB Atlas │ ← Central data storage (always online)
│   (Free Tier)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐  ┌▼──────────┐
│ Backend│  │  Frontend  │
│FastAPI │  │   React    │
│(Render)│  │  (Vercel)  │
└────────┘  └────────────┘

Backend writes → MongoDB → Frontend reads
```

### Data Flow

1. **Backend Active**: Backend runs predictions → stores results in MongoDB → Frontend fetches live data
2. **Backend Sleeping**: Frontend fetches cached data directly from MongoDB → Shows last known state
3. **Backend Wakes Up**: Runs pipeline → Updates MongoDB → Frontend auto-refreshes on next fetch

---

## 📋 Prerequisites

- MongoDB Atlas account (free tier works)
- Render account (for backend deployment)
- Vercel account (for frontend deployment)

---

## 🔧 Part 1: MongoDB Atlas Setup

### Step 1: Create MongoDB Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign in or create account
3. Create a **Free M0 Cluster**
4. Choose a cloud provider and region
5. Click "Create Cluster"

### Step 2: Configure Database Access

1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **Password** authentication
4. Create username and password (save these!)
5. Set privileges to **"Read and write to any database"**
6. Click **"Add User"**

### Step 3: Configure Network Access

1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (or add `0.0.0.0/0`)
4. Click **"Confirm"**

### Step 4: Get Connection String

1. Go to **Database** → Click **"Connect"** on your cluster
2. Choose **"Connect your application"**
3. Copy the connection string (looks like: `mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`)
4. Replace `<password>` with your actual password
5. Save this for backend `.env` file

### Step 5: Enable MongoDB Data API

1. In Atlas, go to **"Data API"** (left sidebar under Services)
2. Click **"Enable the Data API"**
3. Create an API Key:
   - Click **"Create API Key"**
   - Give it a name (e.g., "Frontend Read Access")
   - Copy the **API Key** (you can't see it again!)
4. Note your **App ID** (shown in the Data API section)
5. Save both for frontend `.env` file

---

## 🐍 Part 2: Backend Configuration

### Step 1: Update Environment Variables

Create or update `backend/.env`:

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=YourAppName
DB_NAME=dropout_prediction

# Other existing variables
FRONTEND_URL=http://localhost:3000,http://localhost:5173,https://your-vercel-app.vercel.app
DEBUG=false
LOG_LEVEL=INFO
```

**For Render deployment:**
1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add environment variables:
   - `MONGO_URI` = (your connection string)
   - `DB_NAME` = `dropout_prediction`

### Step 2: Verify Backend Files

The following files have been created/updated:

✅ `backend/app/services/mongo_service.py` - MongoDB integration service  
✅ `backend/app/main.py` - Updated with MongoDB data caching  
✅ `backend/requirements.txt` - Already has `pymongo`

### Step 3: Test Backend Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Test the new endpoints:**

```bash
# Check MongoDB connection
curl http://localhost:8000/mongo-status

# Check backend is alive
curl http://localhost:8000/ping

# Run prediction pipeline (this will cache data in MongoDB)
curl http://localhost:8000/predict

# Verify cached data
curl http://localhost:8000/latest-data
```

---

## ⚛️ Part 3: Frontend Configuration

### Step 1: Update Environment Variables

Create or update `frontend/.env`:

```env
# Backend API
VITE_API_BASE_URL=https://your-render-backend.onrender.com

# MongoDB Data API Configuration
VITE_MONGO_APP_ID=your_mongo_data_api_app_id
VITE_MONGO_API_KEY=your_mongo_data_api_key
VITE_MONGO_CLUSTER=Cluster0
VITE_MONGO_DB=dropout_prediction
VITE_MONGO_COLLECTION=data
```

**Get the values:**
- `VITE_MONGO_APP_ID`: From Atlas → Data API section
- `VITE_MONGO_API_KEY`: API key you created earlier
- `VITE_MONGO_CLUSTER`: Your cluster name (default: `Cluster0`)

**For Vercel deployment:**
1. Go to your Vercel project settings
2. Navigate to **Environment Variables**
3. Add all `VITE_*` variables above

### Step 2: Verify Frontend Files

The following files have been created/updated:

✅ `frontend/src/services/mongoData.ts` - MongoDB Data API client  
✅ `frontend/src/pages/Dashboard.tsx` - Updated with fallback logic  
✅ `frontend/src/components/RenderPingStatus.tsx` - Enhanced status indicator  
✅ `frontend/.env.example` - Updated with MongoDB config

### Step 3: Test Frontend Locally

```bash
cd frontend
npm install  # or bun install
npm run dev  # or bun dev
```

**Test the fallback behavior:**

1. **Backend Active**: Dashboard should show "Live Data" badge (green)
2. **Backend Inactive**: Stop backend → Dashboard should show "Cached Data" badge (amber)
3. **No Data**: Clear MongoDB → Dashboard shows error message

---

## 🧪 Testing the Complete Flow

### Test Scenario 1: Normal Operation

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Navigate to Dashboard
4. You should see: ✅ **"Live Data"** badge (green, pulsing dot)

### Test Scenario 2: Backend Sleeping (MongoDB Fallback)

1. Stop the backend
2. Refresh Dashboard
3. You should see: 📦 **"Cached Data"** badge (amber)
4. Data should still display (from MongoDB)
5. Toast notification: "Backend is sleeping. Showing cached data."

### Test Scenario 3: Backend Restart

1. Restart backend
2. Hit `/predict` endpoint to update data
3. Wait ~1 minute or refresh Dashboard
4. Badge should change back to: ✅ **"Live Data"**

### Test Scenario 4: No Data Available

1. Clear MongoDB collection (or use fresh DB)
2. Stop backend
3. Refresh Dashboard
4. You should see: ❌ **"No Data"** badge (red)
5. Error message displayed

---

## 🚀 Deployment Checklist

### Backend (Render)

- [ ] MongoDB Atlas cluster created
- [ ] Database user created with read/write permissions
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string obtained and tested
- [ ] Environment variables set in Render:
  - [ ] `MONGO_URI`
  - [ ] `DB_NAME`
  - [ ] `FRONTEND_URL`
- [ ] Backend deployed successfully
- [ ] Test `/ping` endpoint returns `{"status": "ok"}`
- [ ] Test `/mongo-status` shows connected
- [ ] Run `/predict` to populate initial data

### Frontend (Vercel)

- [ ] MongoDB Data API enabled in Atlas
- [ ] API key created and saved
- [ ] App ID noted from Data API section
- [ ] Environment variables set in Vercel:
  - [ ] `VITE_API_BASE_URL`
  - [ ] `VITE_MONGO_APP_ID`
  - [ ] `VITE_MONGO_API_KEY`
  - [ ] `VITE_MONGO_CLUSTER`
  - [ ] `VITE_MONGO_DB`
  - [ ] `VITE_MONGO_COLLECTION`
- [ ] Frontend deployed successfully
- [ ] Test Dashboard loads with data
- [ ] Verify fallback works when backend sleeps

---

## 🎨 UI Features Added

### 1. Data Source Badge (Dashboard Header)

Shows current data source:

- 🟢 **"Live Data"** - Fetching from active backend (green, pulsing)
- 🟠 **"Cached Data"** - Reading from MongoDB (amber, database icon)
- 🔴 **"No Data"** - Both sources failed (red, X icon)

### 2. Enhanced Dev Status Panel (Bottom-Right, Dev Mode Only)

Shows:
- Backend status (Active ✅ / Sleeping ❌)
- Last health check time
- Render ping status
- Ping interval and last ping time

**Note**: Only visible in development mode (`npm run dev`)

### 3. Smart Toast Notifications

- Success: "✅ Data Loaded - Successfully fetched live data from backend"
- Fallback: "📦 Cached Data Loaded - Backend is sleeping. Showing cached data."
- Error: "Failed to load data. Backend is inactive and no cached data available."

---

## 🔍 Troubleshooting

### Issue: "MongoDB service not available"

**Solution:**
1. Check `backend/.env` has correct `MONGO_URI`
2. Verify MongoDB user password is correct
3. Test connection: `python -c "from pymongo import MongoClient; print(MongoClient('YOUR_URI').admin.command('ping'))"`

### Issue: "MongoDB Data API fetch failed"

**Solution:**
1. Verify Data API is enabled in Atlas
2. Check API key is correct in frontend `.env`
3. Ensure App ID matches your Atlas project
4. Test in browser console:
   ```javascript
   fetch('https://data.mongodb-api.com/app/YOUR_APP_ID/endpoint/data/v1/action/findOne', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'api-key': 'YOUR_API_KEY'
     },
     body: JSON.stringify({
       dataSource: 'Cluster0',
       database: 'dropout_prediction',
       collection: 'data',
       filter: { _id: 'latest' }
     })
   }).then(r => r.json()).then(console.log)
   ```

### Issue: "No document found in MongoDB"

**Solution:**
1. Backend hasn't run yet - call `/predict` endpoint to populate data
2. Or manually insert test data:
   ```javascript
   // In MongoDB Atlas → Collections → Insert Document
   {
     "_id": "latest",
     "timestamp": "2025-01-01T00:00:00",
     "total_students": 100,
     "phase_distribution": {
       "Green": 50,
       "Yellow": 30,
       "Orange": 15,
       "Red": 5
     },
     "preview": [ /* student records */ ]
   }
   ```

### Issue: CORS errors

**Solution:**
1. Ensure `FRONTEND_URL` in backend `.env` includes your frontend URL
2. Render may need CORS middleware configured (already done in `main.py`)
3. Check browser console for specific CORS error message

---

## 📊 MongoDB Data Structure

The backend stores data with this structure:

```json
{
  "_id": "latest",
  "timestamp": "2025-10-05T12:34:56.789Z",
  "total_students": 500,
  "phase_distribution": {
    "Green": 250,
    "Yellow": 150,
    "Orange": 75,
    "Red": 25
  },
  "model_phase_distribution": {
    "Green": 260,
    "Yellow": 145,
    "Orange": 70,
    "Red": 25
  },
  "red_zone_overrides": 10,
  "ml_model_used": "rf_pipeline_broad.joblib",
  "preview": [
    {
      "enrollment_no": "2023ENG001",
      "name": "Aarav Sharma",
      "department": "Computer Science",
      "attendance": 85.5,
      "cgpa": 8.2,
      "final_phase": "Green",
      // ... more student fields
    }
    // ... more students (typically 100-500 records)
  ],
  "output_path": "backend/app/data/merged_with_predictions.csv"
}
```

---

## 🎯 Benefits of This Implementation

✅ **Always Available UI** - Frontend works even when backend sleeps  
✅ **Cost Effective** - Uses free tiers (Render, Vercel, MongoDB Atlas)  
✅ **Judge-Friendly** - Demo always shows data, no "backend starting..." delays  
✅ **Automatic Sync** - Backend updates MongoDB when active  
✅ **Visual Feedback** - Clear indicators show data source  
✅ **Graceful Degradation** - Smart fallback from live → cached → error  
✅ **Development Friendly** - Dev panel shows all status information  

---

## 📝 API Endpoints Reference

### Backend Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ping` | GET | Simple health check (for frontend status indicator) |
| `/health` | GET | Detailed health check with uptime |
| `/mongo-status` | GET | MongoDB connection status |
| `/latest-data` | GET | Retrieve cached data from MongoDB |
| `/predict` | GET | Run prediction pipeline & cache to MongoDB |
| `/students` | GET | Get all students (from CSV) |

### MongoDB Data API

Endpoint structure:
```
POST https://data.mongodb-api.com/app/{APP_ID}/endpoint/data/v1/action/findOne
Headers: { "api-key": "YOUR_KEY", "Content-Type": "application/json" }
Body: { dataSource, database, collection, filter }
```

---

## 🔐 Security Notes

1. **MongoDB Credentials**: Never commit `.env` files
2. **API Keys**: Rotate periodically in production
3. **Network Access**: Consider restricting IPs in production
4. **Data API**: Read-only from frontend (backend has write access)
5. **CORS**: Configure allowed origins properly

---

## 📚 Additional Resources

- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [MongoDB Data API Docs](https://www.mongodb.com/docs/atlas/api/data-api/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)

---

## 🤝 Support

If you encounter issues:

1. Check console logs (browser DevTools + terminal)
2. Verify all environment variables are set correctly
3. Test each endpoint individually
4. Check MongoDB Atlas dashboard for connection logs
5. Review the troubleshooting section above

---

## ✨ Summary

You now have a robust data persistence system where:

- **Backend** writes to MongoDB when active
- **Frontend** reads from MongoDB anytime
- **Judges** always see data, never blank screens
- **System** handles backend sleep gracefully

Your application is now **production-ready** with intelligent fallback mechanisms! 🚀
