# Render Keep-Alive Setup Guide

This guide explains how the automatic ping system works to keep your Render backend alive.

## 🎯 What this does

The frontend will automatically ping your Render backend every **2 minutes** to prevent it from going inactive due to Render's free tier limitations.

## 🔧 How it works

### Frontend (Vercel)
- **Ping Service**: `src/services/renderPing.ts`
- **Auto-starts**: Only in production mode (not during development)
- **Ping Endpoint**: `https://arohann.onrender.com/health`
- **Frequency**: Every 2 minutes
- **Timeout**: 30 seconds per ping

### Backend (Render)
- **Health Endpoint**: `/health` (lightweight endpoint)
- **Response**: Simple JSON status message
- **Added**: New dedicated health check for keep-alive pings

## 📋 Files Modified

### Frontend Changes:
1. **`src/services/api.ts`** - Updated API URL to point to Render
2. **`src/services/renderPing.ts`** - New ping service
3. **`src/App.tsx`** - Import ping service to auto-start
4. **`src/components/RenderPingStatus.tsx`** - Dev-only status indicator
5. **`.env`** - Already configured with correct API URL

### Backend Changes:
1. **`app/main.py`** - Added `/health` endpoint for lightweight pings

## 🚀 Deployment Steps

### 1. Deploy Backend to Render
Make sure your Render backend is deployed with the new health endpoint:
- URL: `https://arohann.onrender.com`
- Health check: `https://arohann.onrender.com/health`

### 2. Deploy Frontend to Vercel
Deploy your frontend to Vercel:
- URL: `https://arohann.vercel.app`
- The ping service will auto-start in production

### 3. Verify Setup
1. Visit your Vercel frontend: `https://arohann.vercel.app`
2. Open browser dev tools (F12) → Console
3. You should see ping logs every 2 minutes:
   ```
   🏓 Render ping successful (350ms) - 3:45:12 PM
   ```

## 🔍 Monitoring

### Development Mode
- Shows ping status indicator in bottom-right corner
- Real-time ping logs in console
- Only visible during `npm run dev`

### Production Mode
- Ping service runs silently in background
- Logs available in browser console (optional)
- No visual indicators (clean UI)

## ⚙️ Configuration

You can modify these settings in `src/services/renderPing.ts`:

```typescript
const PING_INTERVAL = 2 * 60 * 1000; // 2 minutes
const PING_TIMEOUT = 30000; // 30 seconds
const PING_ENDPOINT = '/health'; // Health endpoint
```

## 🛠️ Troubleshooting

### If pings fail:
1. Check Render backend is running: `https://arohann.onrender.com/health`
2. Check browser console for error messages
3. Verify CORS settings allow your Vercel domain

### If backend still goes inactive:
1. Increase ping frequency (reduce `PING_INTERVAL`)
2. Check Render logs for incoming requests
3. Ensure health endpoint responds quickly

## 📊 Expected Behavior

- **First visit**: Ping starts immediately, then every 2 minutes
- **Background tabs**: Pings continue even when tab is not active
- **Page refresh**: Service restarts automatically
- **Network errors**: Service continues trying (doesn't give up)

## 🎯 Cost Impact

- **Render**: Minimal additional load (1 request every 2 minutes)
- **Vercel**: No additional bandwidth cost
- **User**: No impact on frontend performance

The ping requests are tiny (< 1KB) and won't affect your Render bandwidth limits.

## 🔄 Manual Control (Optional)

You can manually control the ping service:

```typescript
import { renderPingService } from './services/renderPing';

// Stop pinging
renderPingService.stop();

// Start pinging
renderPingService.start();

// Check status
console.log(renderPingService.getStatus());
```

---

## ✅ Success Criteria

Your setup is working correctly when:
1. ✅ Frontend deploys to Vercel successfully
2. ✅ Backend responds to `https://arohann.onrender.com/health`
3. ✅ Browser console shows successful pings every 2 minutes
4. ✅ Render backend stays active longer than usual

Your Render backend should now stay active indefinitely! 🎉