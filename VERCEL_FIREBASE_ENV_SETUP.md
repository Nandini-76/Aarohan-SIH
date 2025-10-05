# Firebase Frontend Environment Variables - Vercel Setup

## Required Environment Variables for Vercel

Add these 7 environment variables to your Vercel project:

### 1. Go to Vercel Dashboard
https://vercel.com/your-username/your-project/settings/environment-variables

### 2. Add These Variables

```bash
VITE_FIREBASE_API_KEY=<your-web-api-key>
VITE_FIREBASE_AUTH_DOMAIN=aarohan-f7274.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=aarohan-f7274
VITE_FIREBASE_STORAGE_BUCKET=aarohan-f7274.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=<your-sender-id>
VITE_FIREBASE_APP_ID=<your-app-id>
```

### 3. How to Get These Values

1. **Firebase Console:** https://console.firebase.google.com
2. **Select Project:** aarohan-f7274
3. **Project Settings:** Click gear icon ⚙️ → Project Settings
4. **Web App Config:** Scroll to "Your apps" → Click Web app (</> icon)
5. **Copy Values:** Copy each value to corresponding VITE_ variable

### Example Firebase Config Object

```javascript
// This is what you'll see in Firebase Console
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXX",           // → VITE_FIREBASE_API_KEY
  authDomain: "aarohan-f7274.firebaseapp.com",   // → VITE_FIREBASE_AUTH_DOMAIN
  databaseURL: "https://aarohan-f7274-default-rtdb.firebaseio.com", // → VITE_FIREBASE_DATABASE_URL
  projectId: "aarohan-f7274",                    // → VITE_FIREBASE_PROJECT_ID
  storageBucket: "aarohan-f7274.appspot.com",    // → VITE_FIREBASE_STORAGE_BUCKET
  messagingSenderId: "123456789012",             // → VITE_FIREBASE_MESSAGING_SENDER_ID
  appId: "1:123456789012:web:abc123def456"       // → VITE_FIREBASE_APP_ID
};
```

## Important Notes

### Security
- ✅ **These are WEB credentials** - meant to be in browser
- ✅ **Firebase security rules** protect write access
- ✅ **Only reads are public** - backend writes with service account
- ❌ **DON'T use service account keys** in frontend (private-key should NEVER be in frontend)

### Environment
- Add to **Production**, **Preview**, and **Development** environments
- Or select **All** when adding variables

### After Adding Variables
1. **Redeploy** your frontend on Vercel
2. Vercel will rebuild with new environment variables
3. Test the Firebase fallback

## Testing Steps

### 1. Verify Variables Are Set
After deployment, check browser console:
```javascript
// Should NOT show "Firebase not initialized" warning
```

### 2. Test Backend Active
- Open dashboard
- Should load data normally
- No yellow banner

### 3. Test Backend Suspended
- Suspend Render service
- Refresh dashboard
- Should show yellow banner: "Showing Cached Data from Firebase"
- All students should display

### 4. Verify Data Source
Check browser console:
```
Successfully loaded data from backend API
// OR
Successfully loaded 56 students from Firebase
```

## Local Development

Create `frontend/.env.local`:

```bash
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=aarohan-f7274.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://aarohan-f7274-default-rtdb.firebaseio.com
VITE_FIREBASE_PROJECT_ID=aarohan-f7274
VITE_FIREBASE_STORAGE_BUCKET=aarohan-f7274.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## Troubleshooting

### "Firebase not initialized" in console
- Check if all 7 variables are added on Vercel
- Verify variable names start with `VITE_`
- Redeploy after adding variables

### Still showing CORS error when backend is down
- Verify Firebase variables are correct
- Check Firebase Console → Realtime Database has data at `/students`
- Open browser DevTools → Network tab → Should see Firebase API calls

### "No data available in Firebase"
- Backend needs to run at least ONCE to populate Firebase
- Check backend logs for "Students data pushed to Firebase successfully"
- Resume Render service temporarily to populate data

## What This Enables

✅ **Always-On Dashboard:** Judges can view predictions 24/7  
✅ **No Backend Required:** Frontend reads directly from Firebase when backend sleeps  
✅ **Automatic Fallback:** Seamless switching between backend and Firebase  
✅ **Cost Efficient:** Render free tier + Firebase free tier = $0/month  
✅ **Visual Feedback:** Yellow banner shows when using cached data

## Firebase Database URL

Make sure to use the **Realtime Database URL**, not Firestore:
```
✅ https://aarohan-f7274-default-rtdb.firebaseio.com
❌ https://firestore.googleapis.com/...
```

Find it in:
- Firebase Console → Realtime Database → Copy URL from top

## Next Step

**Add these variables to Vercel NOW, then redeploy! 🚀**
