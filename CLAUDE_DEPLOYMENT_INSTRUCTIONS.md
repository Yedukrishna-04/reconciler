# Claude Deployment Instructions

Use this file when you want to ask an AI chat assistant like Claude to help you deploy this project.

## What This Project Is

This is a Python FastAPI project with:

- a backend API
- a simple frontend HTML page
- sample CSV files for reconciliation
- separate `backend/` and `frontend/` folders

## Important Architecture Detail

The codebase now has **separate folders for backend and frontend**, but the backend still serves the frontend HTML.

That means:

- backend code lives in `backend/`
- frontend file lives in `frontend/`
- FastAPI still serves the frontend page at `/`
- the easiest deployment is still to deploy them **together as one service**

Relevant files:

- Repo root requirements file: `D:\OneLab\requirements.txt`
- Repo root start script: `D:\OneLab\start_render.py`
- Render blueprint: `D:\OneLab\render.yaml`
- Project root: `D:\OneLab\reconciler`
- Backend folder: `D:\OneLab\reconciler\backend`
- Frontend folder: `D:\OneLab\reconciler\frontend`
- Backend entry point: `D:\OneLab\reconciler\backend\api\main.py`
- Frontend file: `D:\OneLab\reconciler\frontend\index.html`
- Requirements: `D:\OneLab\reconciler\backend\requirements.txt`
- Sample transactions CSV: `D:\OneLab\reconciler\backend\data\transactions.csv`
- Sample settlements CSV: `D:\OneLab\reconciler\backend\data\settlements.csv`

## Recommended Deployment Strategy

Ask Claude to help you deploy this as **one combined FastAPI service** on Render.

Why:

- simplest setup
- frontend and backend stay on the same domain
- no CORS setup needed
- current code already supports this structure
- the repo-root helper files now make Render deployment simpler from the GitHub root

## Copy-Paste Prompt For Claude

Paste this entire prompt into Claude:

```text
I have a FastAPI project I want to deploy.

Project details:
- The GitHub repo root is: D:\OneLab
- The app folder is: D:\OneLab\reconciler
- The backend folder is: backend
- The frontend folder is: frontend
- Backend entry point is: backend/api/main.py
- Frontend file is: frontend/index.html
- The frontend is served by FastAPI at GET /
- The backend exposes:
  - GET /
  - GET /health
  - GET /report
  - POST /reconcile
- Dependencies are in backend/requirements.txt
- The app should be deployed so both frontend and backend work together

Important:
- This is not a separate React/Vue frontend
- The frontend is plain HTML/JS in a separate frontend folder, but it is still served by FastAPI
- I want the easiest deployment path

Please help me deploy this project on Render as a single web service.

Use these expected commands:
- Build command: python -m pip install -r requirements.txt
- Start command: python start_render.py

Please give me:
1. exact step-by-step deployment instructions
2. what to click in Render
3. what to set as Root Directory
4. how to verify the deployment after it goes live
5. common mistakes to avoid
```

## If Your GitHub Repo Root Is Different

If your GitHub repository root is `D:\OneLab` and the app is inside `reconciler`, tell Claude this too:

```text
My GitHub repo root is the top-level OneLab folder. I added a repo-root requirements.txt and start_render.py so Render can deploy from the repo root without setting a Root Directory.
```

## Expected Deployment Settings

Claude should guide you toward settings like these:

- Platform: Render
- Service type: Web Service
- Environment: Python
- Root Directory: leave empty
- Build Command:

```bash
python -m pip install -r requirements.txt
```

- Start Command:

```bash
python start_render.py
```

- Health Check Path:

```text
/health
```

## How To Ask Claude To Verify Frontend And Backend

Paste this follow-up prompt after deployment:

```text
My app is now deployed. Help me verify both frontend and backend.

I want to confirm:
- the frontend page loads at /
- /health returns {"status":"ok"}
- /report returns sample reconciliation JSON
- the upload flow for /reconcile still works

Please tell me exactly what URLs and behaviors I should test.
```

## If You Want Separate Frontend And Backend Deployments

This project does **not** currently need separate deployments, but if you want Claude to help split them, use this prompt:

```text
I want to split this app into two deployments:
- backend on Render
- frontend on a static host like Netlify or Vercel

Current project details:
- backend is FastAPI
- frontend is plain HTML/JS in frontend/index.html
- frontend currently calls relative API paths like /report and /reconcile

Please tell me what code changes are required to split deployment cleanly.

I expect you to cover:
1. CORS setup in FastAPI
2. replacing relative API calls with a configurable backend base URL
3. frontend deployment options
4. backend deployment settings
5. how to test the split deployment
```

## What Claude Should Understand About This Codebase

If Claude seems confused, give it this summary:

```text
This project is a monolithic FastAPI app that serves both the UI and the API.

Backend:
- backend/api/main.py
- backend/engine/loader.py
- backend/engine/detectors.py
- backend/engine/matcher.py

Frontend:
- frontend/index.html

Data files:
- backend/data/transactions.csv
- backend/data/settlements.csv

Main endpoints:
- GET /
- GET /health
- GET /report
- POST /reconcile
```

## Best Prompt To Use

If you want just one clean message to Claude, use this:

```text
Help me deploy my FastAPI project to Render.

This project already serves both frontend and backend from the same FastAPI app, so I want a single-service deployment.

Project structure:
- requirements.txt is at the repo root
- start_render.py is at the repo root
- backend/api/main.py is the app entry point
- frontend/index.html is the frontend served by GET /
- backend/requirements.txt contains dependencies
- backend/data/ contains sample CSV files used by /report

I want:
1. deployment steps
2. Render configuration values
3. Root Directory guidance
4. post-deploy verification steps
5. common deployment mistakes

Expected commands:
- Build: python -m pip install -r requirements.txt
- Start: python start_render.py
```

## Final Recommendation

For this project, ask Claude to deploy **frontend and backend together as one FastAPI service** first.

Only ask for split frontend/backend deployment if you specifically need:

- a separate frontend domain
- static frontend hosting
- a more production-style architecture
