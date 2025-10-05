# 🚀 Quick Start: Firebase Integration

## For Backend (Render)

### 1. Set Environment Variables

In Render Dashboard → Environment:

```bash
FIREBASE_PROJECT_ID=aarohan-f7274
FIREBASE_PRIVATE_KEY_ID=8e8b7c497fd44032463720aa0dce88ebf35f1708
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
[Copy entire key from serviceAccountKey.json]
-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@aarohan-f7274.iam.gserviceaccount.com
FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
```

### 2. Redeploy

Backend will auto-redeploy. Check logs for: `"Firebase initialized successfully"`

---

## For Frontend (Vercel)

### 1. Install Firebase

```bash
cd frontend
npm install firebase
```

### 2. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```bash
VITE_FIREBASE_API_KEY=AIzaSyCIl-lS6088wyntMipdf8bZJADtIyqsTtU
VITE_FIREBASE_AUTH_DOMAIN=aarohan-f7274.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=aarohan-f7274
VITE_FIREBASE_STORAGE_BUCKET=aarohan-f7274.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=667188000435
VITE_FIREBASE_APP_ID=1:667188000435:web:75857ad32cb591460022c6
```

### 3. Deploy

```bash
git add .
git commit -m "Add Firebase integration"
git push
```

---

## Testing

### Test Backend
```bash
curl https://your-backend.onrender.com/firebase/status
```

Expected: `"firebase_initialized": true`

### Test Frontend
1. Open browser console
2. Should see: `"Firebase initialized successfully"`
3. Run a simulation
4. Data appears in real-time

### Test Persistence
1. Wait 15 minutes (backend sleeps)
2. Refresh frontend
3. Last data still visible ✅

---

## Usage in React Component

```tsx
import { useEffect, useState } from 'react';
import { listenToLatestData } from '@/services/firebase';

export function MyComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const unsubscribe = listenToLatestData(setData);
    return () => unsubscribe();
  }, []);

  return <div>{data?.latest_simulation?.risk_level}</div>;
}
```

---

## Check Firebase Console

View data at: https://console.firebase.google.com/project/aarohan-f7274/database

---

## Troubleshooting

**Backend not connecting?**
- Check environment variables are exactly as shown
- Verify private key includes newlines
- Check Render logs

**Frontend not loading?**
- Ensure all `VITE_` variables are set
- Redeploy after adding variables
- Check browser console for errors

---

✅ **Done!** Your app now persists data via Firebase.
