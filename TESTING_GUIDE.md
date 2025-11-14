# AAROHAN Testing Guide

Comprehensive testing procedures for the AAROHAN Student Dropout Prediction System.

---

## 📋 Table of Contents

- [Testing Overview](#-testing-overview)
- [Local Testing](#-local-testing)
- [Production Testing](#-production-testing)
- [Test Scenarios](#-test-scenarios)
- [Performance Testing](#-performance-testing)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Testing Overview

### Testing Layers

1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - API endpoints and Firebase integration
3. **End-to-End Tests** - Full user workflows
4. **Performance Tests** - Load and stress testing

### Tools Used

- **Backend**: pytest, requests
- **Frontend**: Vitest, React Testing Library
- **API Testing**: Postman, cURL
- **Performance**: Artillery, Lighthouse

---

## 💻 Local Testing

### Backend Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run specific test file:**
```bash
pytest tests/test_prediction.py
```

**Run with coverage:**
```bash
pytest --cov=app tests/
```

**Test categories:**
- `tests/test_api.py` - API endpoint tests
- `tests/test_model.py` - ML model tests
- `tests/test_firebase.py` - Firebase integration tests

### Frontend Tests

**Run all tests:**
```bash
cd frontend
npm test
```

**Run in watch mode:**
```bash
npm test -- --watch
```

**Run with coverage:**
```bash
npm test -- --coverage
```

---

## 🌐 Production Testing

### 1. Backend Health Check

**Test API is running:**

**Possible Causes:**
1. Firebase env vars not set on Vercel
2. Firebase env vars incorrect
3. Firebase has no data

**Solutions:**
1. Check Vercel → Settings → Environment Variables
   - All 7 VITE_FIREBASE_* variables present?
   - Correct values?
2. Redeploy frontend after adding variables
3. Run Test 1 to populate Firebase

---

### Issue: Dashboard loads but no auto-update

**Possible Causes:**
1. Real-time listener not initialized
2. Firebase WebSocket connection blocked

**Solutions:**
1. Check browser console for errors
2. Look for: "Cleaning up Firebase listener" on page unload
3. Verify Firebase Database URL is correct:
   - ✅ `https://aarohan-f7274-default-rtdb.firebaseio.com`
   - ❌ NOT Firestore URL

---

**Test API is running:**
```bash
curl https://arohann.onrender.com/
```

**Expected response:**
```json
{
  "status": "ok",
  "message": "AAROHAN API is running",
  "ml_model_loaded": true
}
```

### 2. Test Student Data Sync

**Trigger Firebase sync:**
```bash
curl https://arohann.onrender.com/api/students
```

**Verify in Firebase Console:**
1. Go to https://console.firebase.google.com
2. Select your project
3. Click "Realtime Database"
4. Check `/students` node contains data

### 3. Test Predictions

**Make a prediction:**
```bash
curl -X POST https://arohann.onrender.com/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "enrollment_no": "TEST001",
    "attendance": 65.0,
    "cgpa": 5.8,
    "backlogs": 2,
    "marks_10th": 75.0,
    "marks_12th": 78.0,
    "fees_flag": 0,
    "suspension_flag": 0,
    "gender": "M"
  }'
```

**Expected:** Risk phase prediction (Green/Yellow/Orange/Red)

### 4. Frontend Verification

**Check dashboard loads:**
1. Visit https://your-app.vercel.app
2. Dashboard should load within 2 seconds
3. Student data visible
4. No console errors

**Test real-time updates:**
1. Keep dashboard open
2. Trigger backend sync in another tab
3. Dashboard should auto-update with toast notification

---

## 🧪 Test Scenarios

### Scenario 1: Green Phase Student

**Input:**
- Attendance: 90%
- CGPA: 8.5
- Backlogs: 0
- Fees: Paid
- Suspension: None

**Expected Output:**
- Phase: Green
- No notifications sent
- Routine monitoring only

### Scenario 2: Yellow Phase Student

**Input:**
- Attendance: 75%
- CGPA: 6.5
- Backlogs: 1
- Fees: Paid
- Suspension: None

**Expected Output:**
- Phase: Yellow
- Counselor notified for watch
- Passive monitoring

### Scenario 3: Orange Phase Student

**Input:**
- Attendance: 65%
- CGPA: 5.5
- Backlogs: 3
- Fees: Paid
- Suspension: None

**Expected Output:**
- Phase: Orange
- Phased intervention triggered
- Counselor + mentor notified

### Scenario 4: Red Phase Student

**Input:**
- Attendance: 50%
- CGPA: 3.8
- Backlogs: 5
- Fees: Unpaid
- Suspension: Yes

**Expected Output:**
- Phase: Red
- Immediate alert to all stakeholders
- High-priority intervention

### Scenario 5: Rule Override

**Input:**
- Attendance: 58% (below 60% threshold)
- CGPA: 7.0 (good)
- Backlogs: 0

**Expected Output:**
- Model predicts: Yellow
- Rule override to: Orange
- Reason: "Attendance below 60% threshold"

---

## ⚡ Performance Testing

### Load Testing with Artillery

**Install Artillery:**
```bash
npm install -g artillery
```

**Create test configuration (`load-test.yml`):**
```yaml
config:
  target: "https://arohann.onrender.com"
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Health Check"
    flow:
      - get:
          url: "/"
  - name: "Prediction"
    flow:
      - post:
          url: "/api/predict"
          json:
            enrollment_no: "TEST001"
            attendance: 65.0
            cgpa: 5.8
            backlogs: 2
            marks_10th: 75.0
            marks_12th: 78.0
            fees_flag: 0
            suspension_flag: 0
            gender: "M"
```

**Run test:**
```bash
artillery run load-test.yml
```

**Performance Targets:**
- P95 response time: < 500ms
- P99 response time: < 1000ms
- Error rate: < 1%
- Throughput: > 50 req/s

### Frontend Performance (Lighthouse)

**Run Lighthouse audit:**
1. Open Chrome DevTools
2. Go to "Lighthouse" tab
3. Run audit for Performance

**Target Scores:**
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: API returns 500 error**

**Debug steps:**
1. Check Render logs for errors
2. Verify Firebase credentials are set
3. Check ML model is loaded
4. Test with simpler endpoint (`/`)

**Issue: Slow response times**

**Possible causes:**
- Render free tier sleeping (first request slow)
- Firebase rate limiting
- Large dataset processing

**Solutions:**
- Upgrade to paid Render plan
- Implement caching
- Optimize database queries

### Frontend Issues

**Issue: Dashboard doesn't load data**

**Debug steps:**
1. Check browser console for errors
2. Verify Firebase config in env variables
3. Test Firebase connection directly
4. Check CORS settings

**Issue: Real-time updates not working**

**Debug steps:**
1. Verify Firebase listeners are attached
2. Check Firebase security rules
3. Test with Firebase Emulator locally
4. Check browser console for Firebase errors

### Firebase Issues

**Issue: Permission denied errors**

**Solution:**
Update Firebase security rules to allow reads:
```json
{
  "rules": {
    "students": {
      ".read": true,
      ".write": "auth != null"
    }
  }
}
```

**Issue: Quota exceeded**

**Solution:**
- Monitor usage in Firebase Console
- Upgrade to paid plan if needed
- Implement pagination to reduce reads

---

## ✅ Testing Checklist

### Pre-Deployment Testing

- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Manual API testing completed
- [ ] Frontend loads without errors
- [ ] Firebase integration working
- [ ] Real-time updates functional
- [ ] All risk phases tested
- [ ] What-if simulations working

### Post-Deployment Testing

- [ ] Production API health check passes
- [ ] Student data syncs to Firebase
- [ ] Frontend dashboard loads
- [ ] Predictions working correctly
- [ ] Real-time updates functional
- [ ] Performance metrics acceptable
- [ ] Error tracking configured
- [ ] Monitoring dashboards set up

### User Acceptance Testing

- [ ] Counselors can view at-risk students
- [ ] Dashboard filters work correctly
- [ ] Student profiles display accurately
- [ ] Intervention history visible
- [ ] Notifications send properly
- [ ] What-if simulations intuitive
- [ ] Mobile responsive design works
- [ ] Accessibility requirements met

---

## 📊 Monitoring

### Key Metrics to Track

**Backend:**
- Response times (P50, P95, P99)
- Error rates
- Request throughput
- ML prediction accuracy
- Firebase write success rate

**Frontend:**
- Page load time
- Time to interactive
- Firebase read latency
- Client-side errors
- User engagement metrics

**Infrastructure:**
- Render service uptime
- Vercel deployment status
- Firebase quota usage
- CDN hit rates

---

## 📚 Additional Resources

- [API Documentation](./API.md)
- [Setup Guide](./SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

<div align="center">

**Testing Complete! 🎉**

Found an issue? [Report it on GitHub](https://github.com/Gaurav8302/AROHANN/issues)

</div>


**Cause:** Environment variables not loaded

**Solution:**
1. Verify all VITE_FIREBASE_* variables on Vercel
2. Variable names must start with `VITE_`
3. Redeploy after adding variables
4. Hard refresh browser (Ctrl+Shift+R)

---

### Issue: Timestamp shows very old data

**Expected Behavior!**
- Backend sleeps after 15 minutes of inactivity
- Firebase shows last saved predictions
- This is intentional - data is cached

**To Get Fresh Data:**
1. Visit: https://arohann.onrender.com/students
2. Wait for backend to complete
3. Dashboard will auto-update

---

## 📊 Success Criteria

All these should be true:

- [ ] Backend logs show: "Students data pushed to Firebase successfully"
- [ ] Firebase Console shows `/students` with 56 entries
- [ ] Dashboard loads in < 1 second
- [ ] Blue indicator shows timestamp
- [ ] Browser console shows: "Successfully loaded 56 students from Firebase"
- [ ] No backend API errors in console
- [ ] When backend runs, dashboard auto-updates (no refresh)
- [ ] Toast notification shows: "Data Updated"
- [ ] Timestamp updates to "Just updated"
- [ ] Multiple browsers can view simultaneously
- [ ] All browsers update together when backend runs

---

## 🎯 What This Proves

**Firebase-First Architecture Works:**

✅ Frontend ALWAYS reads from Firebase (instant)  
✅ Backend only writes to Firebase (when awake)  
✅ Real-time updates work (no refresh needed)  
✅ Multiple users supported (scalable)  
✅ Cost efficient (no unnecessary backend calls)  

**This is exactly what you wanted!**

---

## 📞 Quick Test Commands

```bash
# Test backend endpoint
curl https://arohann.onrender.com/students

# Check if real-time listener is active (browser console)
# Should see:
"Successfully loaded 56 students from Firebase"
"Real-time update: 56 students received from Firebase"
```

---

## Next Step

**After adding Firebase env vars to Vercel:**

1. Wait for Vercel to redeploy (~2 minutes)
2. Open your dashboard URL
3. Follow Test 1-5 above
4. Report results!

If all tests pass → **Architecture is complete and working!** 🎉
