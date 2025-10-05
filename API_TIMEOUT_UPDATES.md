# API Timeout Configuration Updates

## Overview
Increased API timeouts across the application to better handle:
- ML model predictions (can take 5-30+ seconds on free-tier servers)
- Firebase Realtime Database operations (network latency)
- Backend cold starts on Render free tier (can take 30-60 seconds)
- Large dataset processing

## Changes Made

### 1. Frontend - API Service (axios)
**File**: `frontend/src/services/api.ts`

**Before**: 
```typescript
timeout: 10000, // 10 second timeout
```

**After**:
```typescript
timeout: 60000, // 60 second timeout for ML predictions and Firebase operations
```

**Impact**: Main API client now waits up to 60 seconds for responses, preventing premature timeout errors during ML predictions.

---

### 2. Frontend - Render Ping Service
**File**: `frontend/src/services/renderPing.ts`

**Before**:
```typescript
const PING_TIMEOUT = 30000; // 30 seconds timeout
```

**After**:
```typescript
const PING_TIMEOUT = 60000; // 60 seconds timeout for backend warmup
```

**Impact**: Health check pings now wait longer for backend to wake up from sleep on Render free tier.

---

### 3. Backend - Uvicorn Development Server
**File**: `backend/app/main.py`

**Before**:
```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
)
```

**After**:
```python
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info",
    timeout_keep_alive=75,  # Keep connections alive for 75 seconds
    timeout_graceful_shutdown=30  # Allow 30s for graceful shutdown
)
```

**Impact**: Development server keeps connections alive longer and allows more time for graceful shutdown.

---

### 4. Backend - Production Server (Render)
**File**: `backend/Procfile`

**Before**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**After**:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --timeout-keep-alive 75 --timeout-graceful-shutdown 30
```

**Impact**: Production server on Render now maintains connections for up to 75 seconds, crucial for ML operations.

---

### 5. Backend - Local Development Script
**File**: `backend/start.sh`

**Before**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**After**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --timeout-keep-alive 75 --timeout-graceful-shutdown 30
```

**Impact**: Consistent timeout configuration across all environments.

---

## Timeout Configuration Summary

| Component | Timeout Type | Duration | Purpose |
|-----------|-------------|----------|---------|
| **Frontend API Client** | Request timeout | 60 seconds | Wait for ML predictions and Firebase ops |
| **Frontend Render Ping** | Health check timeout | 60 seconds | Allow backend cold start time |
| **Backend Uvicorn** | Keep-alive timeout | 75 seconds | Maintain long-running connections |
| **Backend Uvicorn** | Graceful shutdown | 30 seconds | Complete in-flight requests on shutdown |

## Why These Values?

### 60 seconds for frontend requests:
- **ML Model Inference**: Random Forest with 1000+ students can take 10-30 seconds
- **Firebase Write Operations**: Batch writes to Firebase can take 5-15 seconds
- **Network Latency**: Free tier servers may have slower response times
- **Cold Start Recovery**: If backend was asleep, needs time to warm up

### 75 seconds for backend keep-alive:
- **Exceeds Frontend Timeout**: Must be longer than frontend timeout (60s) to prevent connection drops
- **Long Operations Buffer**: Provides extra time for operations that take exactly 60s
- **Standard Practice**: Most production servers use 65-120 seconds

### 30 seconds for graceful shutdown:
- **Request Completion**: Allows ongoing requests to finish naturally
- **Clean Disconnection**: Prevents abrupt connection termination
- **Database Operations**: Ensures Firebase/DB operations complete

## Testing the Changes

### Test Frontend Timeout:
1. Open browser DevTools → Network tab
2. Navigate to simulation page
3. Submit a large batch prediction (100+ students)
4. Observe request duration - should complete without timeout up to 60s

### Test Backend Timeout:
```bash
# Test with curl (should not timeout)
time curl -X POST "https://arohann.onrender.com/simulate" \
  -H "Content-Type: application/json" \
  -d @test_large_batch.json

# Should complete even if it takes 45-55 seconds
```

### Test Render Cold Start:
1. Wait for Render to sleep (15 minutes of inactivity)
2. Make a request from frontend
3. Frontend should wait up to 60s for backend to wake up
4. Request should succeed, not timeout

## Monitoring

### Watch for these metrics:
- **Request Duration**: Most requests should complete in 5-30 seconds
- **Timeout Errors**: Should see fewer "Request timeout" errors
- **Cold Start Success**: Backend should successfully wake from sleep
- **Connection Keep-Alive**: Fewer "connection closed" errors

### Log Messages:
```
# Frontend console
✅ API request completed in 45.2s
❌ Request timeout (exceeded 60s)  # Should be rare now

# Backend logs
INFO: Connection kept alive for 50s
INFO: Graceful shutdown initiated, waiting for 3 requests to complete
```

## Rollback Instructions

If timeouts cause issues, revert with:

```bash
# Frontend - reduce back to 10s
# In frontend/src/services/api.ts
timeout: 10000

# Backend - remove timeout flags
# In backend/Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Future Optimizations

Consider these if timeout issues persist:

1. **Request Queuing**: Implement request queue for large batches
2. **Progressive Loading**: Stream results as they're computed
3. **Background Jobs**: Use Celery/Redis for long-running tasks
4. **Response Compression**: Enable gzip to reduce transfer time
5. **CDN Caching**: Cache static prediction results
6. **Database Indexing**: Optimize Firebase queries
7. **Model Optimization**: Use smaller/faster ML model for real-time predictions

## Environment Variables

Optional: Configure timeouts via environment variables:

### Frontend (.env)
```bash
VITE_API_TIMEOUT=60000  # milliseconds
VITE_PING_TIMEOUT=60000
```

### Backend (.env)
```bash
UVICORN_TIMEOUT_KEEP_ALIVE=75  # seconds
UVICORN_TIMEOUT_GRACEFUL_SHUTDOWN=30
```

## Related Documentation
- [FastAPI Timeouts](https://www.uvicorn.org/settings/#timeouts)
- [Axios Timeout Configuration](https://axios-http.com/docs/req_config)
- [Render Free Tier Limitations](https://render.com/docs/free#free-web-services)
- [Firebase Performance Best Practices](https://firebase.google.com/docs/database/web/read-and-write#best-practices)

---

**Last Updated**: October 5, 2025
**Author**: AI Pair Programming Session
**Status**: ✅ Deployed and Active
