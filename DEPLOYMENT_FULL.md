# OneLab Payments Reconciler - Full Deployment Guide

Use this file as the single deployment guide for the project.

It is written for:

- manual deployment by a developer
- AI-assisted deployment in Claude, Cursor, or similar AI IDE tools

## Deployment Summary

This project should be deployed as **one combined FastAPI service**.

Why:

- the backend and frontend already work together
- the frontend is plain HTML, not a separate React or Vue app
- FastAPI serves the frontend at `/`
- this avoids extra CORS and cross-domain setup

## Simplest Render Setup For This Repo

Because your GitHub repository root is the top-level `OneLab` folder, the easiest deployment path is now:

- leave Render Root Directory empty
- build from the repo root
- start from the repo root

These helper files were added for that flow:

- `requirements.txt`
- `start_render.py`
- `render.yaml`

## Current Project Structure

```text
D:\OneLab\
|-- DEPLOYMENT_FULL.md
`-- reconciler\
    |-- backend\
    |   |-- api\
    |   |   `-- main.py
    |   |-- data\
    |   |   |-- transactions.csv
    |   |   `-- settlements.csv
    |   |-- engine\
    |   |   |-- loader.py
    |   |   |-- detectors.py
    |   |   `-- matcher.py
    |   |-- tests\
    |   |   `-- test_detectors.py
    |   |-- gaps_report.json
    |   `-- requirements.txt
    |-- frontend\
    |   `-- index.html
    `-- README.md
```

## How The App Works

- Backend code lives in `reconciler/backend`
- Frontend file lives in `reconciler/frontend/index.html`
- The FastAPI app entry point is `reconciler/backend/api/main.py`
- The backend serves the frontend HTML from the sibling `frontend/` folder
- The sample CSV files used by `/report` are inside `reconciler/backend/data`

Important:

- deploy from the `reconciler` root, not from `backend` alone
- if you deploy only `backend`, the app may not find `frontend/index.html`

## Main Endpoints

- `GET /` -> frontend upload UI
- `GET /health` -> health check JSON
- `GET /report` -> sample reconciliation JSON
- `POST /reconcile` -> uploaded CSV reconciliation

## Local Verification Before Deployment

Run these commands first:

```powershell
cd D:\OneLab\reconciler\backend
python -m pip install -r requirements.txt
python -m pytest tests -v
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Then verify:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/report`

Expected:

- all 4 pytest tests pass
- `/` loads the frontend page
- `/health` returns `{"status":"ok"}`
- `/report` returns JSON with `total_gaps = 6`

## Recommended Hosting Platform

Use **Render** as the primary deployment target.

This project fits Render well because:

- it is a small Python web service
- it does not need a database
- it only needs one web service for both frontend and backend

## Render Deployment Steps

### 1. Push the project to GitHub

Push either:

- the full `D:\OneLab` folder as a repo, or
- the `D:\OneLab\reconciler` folder as its own repo

### 2. Open Render

1. Go to `https://render.com`
2. Sign in
3. Click `New`
4. Click `Web Service`
5. Connect GitHub if needed
6. Choose the repository that contains this project

### 3. Configure the Render service

Use these exact settings for the current GitHub repo:

- Environment: `Python 3`
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

- Auto Deploy: enabled

### 4. Create the service

Click `Create Web Service`.

Render will:

- install the dependencies
- start the FastAPI app
- expose a public URL

## Post-Deployment Verification

Once the service is live, verify these URLs:

- `https://your-app.onrender.com/`
- `https://your-app.onrender.com/health`
- `https://your-app.onrender.com/report`

Expected results:

- `/` loads the frontend
- `/health` returns `{"status":"ok"}`
- `/report` returns JSON reconciliation data

## Alternate Render Setup

If you prefer deploying from the `reconciler` folder instead, this also works:

- Root Directory: `reconciler`
- Build Command:

```bash
python -m pip install -r backend/requirements.txt
```

- Start Command:

```bash
cd backend && python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

## Common Deployment Mistakes

### Wrong root directory

Problem:

- Render cannot find the correct files

Fix:

- either leave Root Directory empty and use the repo-root commands above
- or set Root Directory to `reconciler` and use the alternate commands

### Deploying only the backend folder

Problem:

- FastAPI cannot find `frontend/index.html`

Fix:

- deploy from the `reconciler` root so both `backend/` and `frontend/` are available

### Wrong build command

Problem:

- dependencies are not installed

Fix:

- use:

```bash
python -m pip install -r requirements.txt
```

### Wrong start command

Problem:

- service fails to start on Render

Fix:

- use:

```bash
python start_render.py
```

### Hardcoding port 8000 on Render

Problem:

- Render assigns its own runtime port

Fix:

- always use `--port $PORT`

### Missing CSV files

Problem:

- `/report` fails

Fix:

- make sure these files are committed:
  - `reconciler/backend/data/transactions.csv`
  - `reconciler/backend/data/settlements.csv`

## Use This File In Claude

If you want Claude to guide the deployment, paste this prompt:

```text
Help me deploy my FastAPI project using the instructions in DEPLOYMENT_FULL.md.

Project root:
D:\OneLab\reconciler

Current structure:
- backend/api/main.py
- backend/requirements.txt
- backend/data/transactions.csv
- backend/data/settlements.csv
- frontend/index.html

Important:
- backend and frontend are separate folders
- FastAPI still serves the frontend at GET /
- I want to deploy both together as one service
- deploy from the reconciler root

Please use this deployment setup:
- Platform: Render
- Build: python -m pip install -r requirements.txt
- Start: python start_render.py
- Health check: /health

Please give me:
1. exact deployment steps
2. Render field values
3. post-deploy verification steps
4. common mistakes to avoid
```

## Alternative Platform

If you do not use Render, keep the same startup pattern:

```bash
python start_render.py
```

This also works for platforms such as Railway if the repo is configured with the same folder layout.

## Final Recommendation

For this project:

- host backend and frontend together
- deploy from the `reconciler` root
- use Render first
- verify `/`, `/health`, and `/report` immediately after deploy
