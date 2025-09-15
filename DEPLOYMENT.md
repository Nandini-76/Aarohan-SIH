# Deployment Guide (Vercel + Render)

This repository is configured for a split deployment:
- Frontend (Vite React) on Vercel
- Backend (FastAPI) on Render

## Prerequisites
- A GitHub repo (already pushed)
- Accounts on Vercel and Render

## Backend on Render
1. In Render, Create New → Web Service → Use this repo.
2. Root Directory: project root (Render will use `render.yaml`).
3. Build Command: `pip install -r backend/requirements.txt` (from blueprint).
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Environment Variables:
   - `PYTHON_VERSION` = `3.11`
   - `MONGO_URI` = your Mongo connection string
   - `DB_NAME` = `dropout_prediction`
   - `FRONTEND_URL` = your Vercel URL, e.g., `https://<project>.vercel.app`
6. Deploy. Note the backend URL (e.g., `https://arohann-backend.onrender.com`).

## Frontend on Vercel
1. In Vercel, import this GitHub repo.
2. Project Settings:
   - Framework Preset: Other
   - Root Directory: `frontend`
   - Build Command: `npm run vercel-build`
   - Output Directory: `dist`
3. Environment Variables:
   - `VITE_API_BASE_URL` = your Render backend URL from above
4. Deploy.

## Local env files
- Frontend: copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.
- Backend: copy `backend/.env.example` to `backend/.env` for local runs; on Render, set vars in dashboard.

## CORS
The backend uses `FRONTEND_URL` to set allowed origins (supports comma-separated values). Ensure it matches your Vercel domain.

## Health checks
- Backend: `GET /` on the Render URL should return status JSON.
- Frontend: App should load and call the backend using `VITE_API_BASE_URL`.

## Notes
- If you later enable model training files, ensure large binaries are not committed; use storage or rebuild.
- To reduce bundle size warnings, consider dynamic imports for Recharts.