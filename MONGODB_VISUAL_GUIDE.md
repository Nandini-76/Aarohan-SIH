# 🎨 AAROHAN MongoDB Persistence - Visual Guide

## 🏗️ System Architecture

```
╔══════════════════════════════════════════════════════════════════════════╗
║                         AAROHAN SYSTEM ARCHITECTURE                       ║
║                      MongoDB Data Persistence Layer                       ║
╚══════════════════════════════════════════════════════════════════════════╝

                            ┌─────────────────┐
                            │  MongoDB Atlas  │
                            │   (Free M0)     │
                            │   - 512MB       │
                            │   - 24/7 Active │
                            │   - Global CDN  │
                            └────────┬────────┘
                                     │
                      ┌──────────────┼──────────────┐
                      │              │              │
                 WRITE│         READ │         READ │
                      │              │              │
              ┌───────▼──────┐  ┌────▼─────────┐  │
              │   Backend    │  │   Backend    │  │
              │   FastAPI    │  │   FastAPI    │  │
              │  (Render)    │  │   /latest    │  │
              │              │  │   endpoint   │  │
              │  /predict    │  │              │  │
              │  endpoint    │  │  (Optional)  │  │
              └──────────────┘  └──────────────┘  │
                                                   │
                                       ┌───────────▼────────┐
                                       │ MongoDB Data API   │
                                       │  (Read-Only)       │
                                       │  Public Endpoint   │
                                       └───────────┬────────┘
                                                   │
                                              ┌────▼─────┐
                                              │ Frontend │
                                              │  React   │
                                              │ (Vercel) │
                                              └──────────┘
```

---

## 🔄 Data Flow Scenarios

### Scenario 1: Normal Operation (Backend Active)

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │────1───▶│ Frontend │────2───▶│ Backend  │
│ (Judge)  │         │  React   │         │  FastAPI │
└──────────┘         └────┬─────┘         └────┬─────┘
                          │                     │
                          │                     │ 3. Write
                          │                     ▼
                          │              ┌──────────┐
                          │              │ MongoDB  │
                          │              │  Atlas   │
                          │              └──────────┘
                          │
                     4. Return data
                          │
                          ▼
                   ┌─────────────┐
                   │  Dashboard  │
                   │ "Live Data" │
                   │   (Green)   │
                   └─────────────┘

Steps:
1. User opens Dashboard
2. Frontend calls Backend API /students
3. Backend writes latest to MongoDB (cache update)
4. Backend returns data to Frontend
5. Dashboard shows "Live Data" badge
```

### Scenario 2: Backend Sleeping (Fallback Mode)

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  User    │────1───▶│ Frontend │────2───▶│ Backend  │
│ (Judge)  │         │  React   │    ❌   │ (Asleep) │
└──────────┘         └────┬─────┘         └──────────┘
                          │
                          │ 3. Fallback
                          │
                          ▼
                   ┌──────────────┐
                   │   MongoDB    │
                   │   Data API   │
                   └──────┬───────┘
                          │
                     4. Cached data
                          │
                          ▼
                   ┌─────────────┐
                   │  Dashboard  │
                   │"Cached Data"│
                   │  (Amber)    │
                   └─────────────┘

Steps:
1. User opens Dashboard
2. Frontend tries Backend API → Timeout/Error
3. Frontend falls back to MongoDB Data API
4. MongoDB returns cached data (last known state)
5. Dashboard shows "Cached Data" badge
6. Toast: "Backend is sleeping. Showing cached data."
```

### Scenario 3: Backend Restarts

```
Backend Sleeping                Backend Waking Up               Backend Active
     │                                  │                            │
     │  Frontend shows                  │  Backend starts            │  Backend runs
     │  "Cached Data"                   │  Health checks             │  /predict
     │       │                          │  restore                   │      │
     │       ▼                          │      │                     │      ▼
     │  ┌────────┐                      │  ┌───▼────┐               │  ┌────────┐
     │  │MongoDB │                      │  │Backend │               │  │MongoDB │
     │  │  Read  │                      │  │Starting│               │  │ Update │
     │  └────────┘                      │  └────────┘               │  └───┬────┘
     │                                  │                            │      │
     ▼                                  ▼                            ▼      ▼
[Amber Badge]                    [Checking...]                 [Green Badge]
```

---

## 🎨 UI Elements

### Dashboard Header - Data Source Indicator

```
┌────────────────────────────────────────────────────────────┐
│  Student Guardian Dashboard          [●  Live Data    ]    │
│  Monitor student risk levels                               │
└────────────────────────────────────────────────────────────┘
                                       ▲
                                       │
                                  Data Source Badge
                                       │
                      ┌────────────────┴────────────────┐
                      │                                  │
            Backend Active              Backend Sleeping │
                      │                                  │
                      ▼                                  ▼
          ┌─────────────────────┐         ┌─────────────────────┐
          │  ● Live Data        │         │  🗄 Cached Data      │
          │  (Green, pulsing)   │         │  (Amber, static)     │
          └─────────────────────┘         └─────────────────────┘
```

### Dev Status Panel (Bottom-Right, Dev Mode Only)

```
┌──────────────────────────────────┐
│  🔧 Dev Status Panel             │
├──────────────────────────────────┤
│  Backend: ✅ Active              │
│  Last check: 14:23:45            │
├──────────────────────────────────┤
│  Render Ping: ✅ Active          │
│  Interval: 840s                  │
│  Last ping: 14:20:12             │
├──────────────────────────────────┤
│  (Dev only - hidden in prod)    │
└──────────────────────────────────┘
```

---

## 📊 MongoDB Document Structure

```json
MongoDB Collection: "data"
Document: { "_id": "latest" }

{
  "_id": "latest",                    ← Fixed ID for easy lookup
  "timestamp": "2025-10-05T14:23:45", ← When backend last updated
  
  "total_students": 500,               ← Summary statistics
  "phase_distribution": {
    "Green": 250,
    "Yellow": 150,
    "Orange": 75,
    "Red": 25
  },
  
  "model_phase_distribution": { ... }, ← ML model predictions
  "red_zone_overrides": 10,            ← Rule-based overrides
  "ml_model_used": "rf_pipeline.joblib",
  
  "preview": [                         ← Full student data
    {
      "enrollment_no": "2023ENG001",
      "name": "Aarav Sharma",
      "department": "Computer Science",
      "attendance": 85.5,
      "cgpa": 8.2,
      "backlogs": 0,
      "final_phase": "Green",
      "ml_probability": 0.92,
      // ... 20+ more fields
    },
    // ... 499 more students
  ],
  
  "output_path": "backend/app/data/merged_with_predictions.csv"
}
```

---

## 🔐 Security & Access

```
┌─────────────────────────────────────────────────────┐
│              MongoDB Atlas Security                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Backend (Write Access)                             │
│  ├─ Connection String: mongodb+srv://...            │
│  ├─ Username/Password Authentication                │
│  ├─ Read + Write permissions                        │
│  └─ Updates "latest" document                       │
│                                                      │
│  Frontend (Read-Only Access)                        │
│  ├─ MongoDB Data API                                │
│  ├─ API Key Authentication                          │
│  ├─ Read-only permissions                           │
│  └─ Public HTTPS endpoint                           │
│                                                      │
│  Network Access                                     │
│  ├─ Allow from anywhere (0.0.0.0/0)                │
│  └─ Or restrict to specific IPs in production       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Characteristics

```
┌──────────────────┬────────────────┬──────────────────┐
│   Data Source    │  Latency (avg) │   Availability   │
├──────────────────┼────────────────┼──────────────────┤
│ Backend API      │   200-500ms    │  95% (Render)    │
│ MongoDB Data API │   100-300ms    │  99.9% (Atlas)   │
│ Cache (Browser)  │   <10ms        │  100% (Local)    │
└──────────────────┴────────────────┴──────────────────┘

Fallback Chain:
  Backend API → MongoDB Data API → Error
  (Fastest)     (Reliable)         (Last resort)
```

---

## 🎯 Cost Breakdown (All FREE!)

```
┌────────────────────────────────────────────────────┐
│              Infrastructure Costs                   │
├────────────────────────────────────────────────────┤
│                                                     │
│  MongoDB Atlas (M0 Free Tier)                      │
│  ├─ Storage: 512MB                    $0.00/month  │
│  ├─ RAM: Shared                                    │
│  └─ Transfers: 10GB                                │
│                                                     │
│  Render (Free Tier)                                │
│  ├─ Hours: 750/month                  $0.00/month  │
│  ├─ Sleep after 15min inactive                     │
│  └─ Cold start: ~30 seconds                        │
│                                                     │
│  Vercel (Hobby Plan)                               │
│  ├─ Bandwidth: 100GB                  $0.00/month  │
│  ├─ Builds: Unlimited                              │
│  └─ Edge Network: Global CDN                       │
│                                                     │
│  TOTAL MONTHLY COST:                  $0.00 ✅     │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## 🚀 Deployment Workflow

```
┌─────────────────────────────────────────────────┐
│         Development → Production Flow            │
└─────────────────────────────────────────────────┘

1. Local Development
   ├─ Backend: uvicorn app.main:app --reload
   ├─ Frontend: npm run dev
   └─ MongoDB: Atlas (shared cluster)

2. Push to GitHub
   ├─ git add .
   ├─ git commit -m "Add MongoDB persistence"
   └─ git push origin main

3. Render (Backend) Auto-Deploy
   ├─ Detects push to main branch
   ├─ Runs: pip install -r requirements.txt
   ├─ Starts: uvicorn app.main:app
   └─ Health check: /health endpoint

4. Vercel (Frontend) Auto-Deploy
   ├─ Detects push to main branch
   ├─ Runs: npm install && npm run build
   ├─ Deploys to global edge network
   └─ Available within ~1 minute

5. MongoDB Atlas
   ├─ Always online (no deployment needed)
   ├─ Monitors connections
   └─ Provides Data API endpoint

6. First Backend Run
   ├─ Hit: https://your-backend.onrender.com/predict
   ├─ Populates MongoDB with initial data
   └─ Frontend can now use cached data
```

---

## 📈 Monitoring & Debugging

```
┌────────────────────────────────────────────────────┐
│              Monitoring Endpoints                   │
├────────────────────────────────────────────────────┤
│                                                     │
│  Backend Health                                    │
│  GET /ping          → {"status": "ok"}            │
│  GET /health        → Full status + uptime         │
│  GET /mongo-status  → MongoDB connection info      │
│  GET /latest-data   → Current cached data          │
│                                                     │
│  Frontend Dev Panel (Dev Mode)                     │
│  ├─ Backend status check every 30s                │
│  ├─ Render ping status                             │
│  └─ Last check timestamps                          │
│                                                     │
│  Browser Console                                   │
│  ├─ "🔄 Attempting to fetch from backend..."      │
│  ├─ "⚠️ Backend unavailable, trying MongoDB..."   │
│  └─ "✅ Successfully cached in MongoDB"           │
│                                                     │
│  MongoDB Atlas Dashboard                           │
│  ├─ Real-time connections                          │
│  ├─ Data size usage                                │
│  └─ Query performance                              │
│                                                     │
└────────────────────────────────────────────────────┘
```

---

## ✅ Success Indicators

When everything is working correctly, you should see:

### ✓ Backend Logs
```
✅ MongoDB connected successfully to database: dropout_prediction
🤖 Starting unified prediction pipeline via API endpoint
✅ Successfully cached prediction results in MongoDB
```

### ✓ Frontend Console
```
API Base URL: https://your-backend.onrender.com
🔄 Attempting to fetch from backend...
API response received: 200
Toast: ✅ Data Loaded - Successfully fetched live data from backend
```

### ✓ MongoDB Atlas
```
- Collections: 1
- Documents in 'data': 1
- Document _id: "latest"
- Size: ~500KB - 2MB (depending on student count)
```

### ✓ UI Display
```
Dashboard Header: [● Live Data] (Green badge)
Stats Cards: Showing numbers (not zeros)
Student Table: Populated with student records
Dev Panel: Backend: ✅ Active
```

---

## 🎓 Learning Resources

### MongoDB Atlas
- [Getting Started](https://docs.atlas.mongodb.com/getting-started/)
- [Data API Tutorial](https://www.mongodb.com/docs/atlas/api/data-api/)
- [Security Best Practices](https://docs.atlas.mongodb.com/security/)

### FastAPI + MongoDB
- [Motor (Async MongoDB)](https://motor.readthedocs.io/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

### React + MongoDB
- [Data API with React](https://www.mongodb.com/developer/languages/javascript/react-mongodb-data-api/)
- [Fetch API Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

---

**Visual Guide Complete! 🎉**

*For implementation details, see:*
- `MONGODB_PERSISTENCE_GUIDE.md` - Complete setup
- `MONGODB_QUICK_START.md` - Quick reference
- `MONGODB_IMPLEMENTATION_SUMMARY.md` - What was done
