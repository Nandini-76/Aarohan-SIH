# Quick Command Reference - Firebase Update

## 🚀 Deploy Updated Backend to Render

```bash
# 1. Commit changes
cd C:\Users\wanna\Desktop\AAROHAN
git add backend/app/main.py backend/app/populate_firebase_manual.py FIREBASE_UPDATE_SUMMARY.md
git commit -m "Fix: Load 2080 students into Firebase, remove legacy code"
git push origin main

# 2. Deploy on Render
# Go to: https://dashboard.render.com
# Click: Manual Deploy → Deploy latest commit
```

---

## 🔧 Manual Firebase Population (If Needed)

```bash
# Option 1: From local machine
cd C:\Users\wanna\Desktop\AAROHAN\backend
C:/Users/wanna/Desktop/AAROHAN/backend/venv/Scripts/python.exe app/populate_firebase_manual.py

# Option 2: After activating venv
cd C:\Users\wanna\Desktop\AAROHAN\backend
.\venv\Scripts\Activate.ps1
cd app
python populate_firebase_manual.py
```

---

## ✅ Verify Everything Works

```bash
# 1. Check if preprocessed file exists
Test-Path "C:\Users\wanna\Desktop\AAROHAN\backend\app\data\predicted_phase_data.csv"
# Should return: True

# 2. Check file has correct number of students
python -c "import pandas as pd; df = pd.read_csv(r'C:\Users\wanna\Desktop\AAROHAN\backend\app\data\predicted_phase_data.csv'); print(f'Students: {len(df)}')"
# Should output: Students: 2080

# 3. Test backend locally (before deploying)
cd C:\Users\wanna\Desktop\AAROHAN\backend
uvicorn app.main:app --reload
# Check logs should show: "Loaded 2080 students from predicted_phase_data.csv"

# 4. Test API endpoint
curl http://localhost:8000/students
# or open in browser: http://localhost:8000/docs
```

---

## 🔍 Check Render Logs After Deployment

```bash
# Look for these lines in Render logs:
✓ Loaded 2080 students from predicted_phase_data.csv (preprocessed)
Successfully stored 2080 students in Firebase at /students
✅ Successfully populated Firebase with 2080 students on startup
```

---

## 🌐 Test Frontend

```bash
# Open your deployed frontend
# URL: https://arohann.vercel.app (or your frontend URL)

# Check:
# - Total student count should be 2080
# - Filters should show all branches (BBA, BSc CS, Agriculture, BTech)
# - Phase distribution visible
# - All students load correctly
```

---

## 🐛 If Something Goes Wrong

### Clear Firebase and Repopulate

```bash
# Run manual population script
cd C:\Users\wanna\Desktop\AAROHAN\backend\app
python populate_firebase_manual.py
```

### Regenerate Preprocessed Data

```bash
# If predicted_phase_data.csv is missing or corrupt
cd C:\Users\wanna\Desktop\AAROHAN\backend\app
python run_pipeline.py
# This will recreate both cleaned_data.csv and predicted_phase_data.csv
```

### Check Firebase Console

```bash
# URL: https://console.firebase.google.com
# Navigate to: Your Project → Realtime Database (or Firestore)
# Check: /students node should have 2080 entries
```

---

## 📦 What to Commit

```bash
# Must commit:
git add backend/app/main.py
git add backend/app/populate_firebase_manual.py

# Optional but recommended:
git add backend/app/data/predicted_phase_data.csv
git add FIREBASE_UPDATE_SUMMARY.md
git add PREPROCESSING_COMPLETE_SUMMARY.md
git add QUICK_START.md

# Commit and push
git commit -m "Fix: Load preprocessed dataset into Firebase, remove legacy code"
git push origin main
```

---

## ⚡ Full Deployment Flow

```bash
# 1. Verify local setup
cd C:\Users\wanna\Desktop\AAROHAN\backend
Test-Path app/data/predicted_phase_data.csv  # Should be True

# 2. Test locally (optional but recommended)
uvicorn app.main:app --reload
# Check logs show 2080 students

# 3. Commit and push
git add -A
git commit -m "Fix: Load 2080 students into Firebase"
git push origin main

# 4. Deploy on Render
# Go to dashboard.render.com → Manual Deploy

# 5. Verify deployment
# Check Render logs for "2080 students"
# Test API: https://arohann.onrender.com/students
# Test Frontend: https://arohann.vercel.app

# 6. If needed, run manual population
# (from your local machine with Firebase credentials)
python backend/app/populate_firebase_manual.py
```

---

## 📊 Expected Behavior

### Before Update:
- Backend loads: 56 students
- Firebase stores: 56 students
- Frontend shows: 56 students

### After Update:
- Backend loads: 2,080 students ✅
- Firebase stores: 2,080 students ✅
- Frontend shows: 2,080 students ✅

---

## 🎯 Success Indicators

✅ Render logs show: `Loaded 2080 students from predicted_phase_data.csv`  
✅ Firebase console shows: 2,080 entries under /students  
✅ API returns: `"total": 2080`  
✅ Frontend displays: 2,080 students with filters working  
✅ Phase colors show correctly (Green/Yellow/Orange/Red)  

---

**All commands ready to copy-paste! Just follow the flow from top to bottom.** 🚀
