# Deployment Guide

This file explains how to deploy the OneLab payments reconciler project.

## Recommended Option

Use **Render** for deployment. It works well for this FastAPI app and supports the separated `backend/` and `frontend/` folder layout.

## Project Location

The app now has explicit folders for backend and frontend:

- Backend: [backend](D:/OneLab/reconciler/backend)
- Frontend: [frontend](D:/OneLab/reconciler/frontend)

Important:

- The backend serves the frontend file from the sibling `frontend/` folder
- For this GitHub repo, the easiest deployment is now from the repo root using the new root-level helper files
- You can still deploy from the `reconciler` root as an alternate setup

## Files Used In Deployment

- API entry point: [main.py](D:/OneLab/reconciler/backend/api/main.py)
- Requirements: [requirements.txt](D:/OneLab/reconciler/backend/requirements.txt)
- Frontend file: [index.html](D:/OneLab/reconciler/frontend/index.html)
- Health endpoint: [main.py](D:/OneLab/reconciler/backend/api/main.py#L30)
- Repo-root requirements file: [requirements.txt](D:/OneLab/requirements.txt)
- Repo-root start script: [start_render.py](D:/OneLab/start_render.py)
- Render blueprint: [render.yaml](D:/OneLab/render.yaml)

## Local Run Before Deployment

Install dependencies:

```powershell
cd D:\OneLab\reconciler\backend
python -m pip install -r requirements.txt
```

Run locally:

```powershell
cd D:\OneLab\reconciler\backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Verify locally:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/report`

## Deploy To Render

### 1. Push the project to GitHub

Push either:

- the full `D:\OneLab` folder as a repository, or
- the `D:\OneLab\reconciler` folder as its own repository

### 2. Create a new Web Service in Render

In Render:

1. Sign in to https://render.com
2. Click `New`
3. Click `Web Service`
4. Connect your GitHub repository
5. Select the repository that contains this project

### 3. Configure the service

Use these settings:

- **Environment**: `Python 3`
- **Root Directory**: leave empty
- **Build Command**:

```bash
python -m pip install -r requirements.txt
```

- **Start Command**:

```bash
python start_render.py
```

### 4. Optional settings

Recommended:

- **Health Check Path**: `/health`
- **Auto Deploy**: enabled

### 5. Deploy

Click `Create Web Service`.

Render will:

- install dependencies from `requirements.txt`
- start the FastAPI app using `uvicorn`
- expose a public URL

## How To Verify After Deployment

Once deployed, test these URLs:

- `https://your-render-url/`
- `https://your-render-url/health`
- `https://your-render-url/report`

Expected results:

- `/` should load the upload UI
- `/health` should return `{"status":"ok"}`
- `/report` should return JSON with sample reconciliation results

## What To Include In Submission

After deployment, include:

- the deployed Render URL
- a demo video showing the app working
- the project zip

## Troubleshooting

### Problem: App starts locally but fails on Render

Check:

- the Root Directory is correct
- the Build Command uses the repo-root `requirements.txt`
- the Start Command is `python start_render.py`

### Problem: Browser opens but page is blank

Check:

- the app root endpoint `/` is reachable
- [index.html](D:/OneLab/reconciler/frontend/index.html) exists
- the deployment logs do not show import errors

### Problem: `/report` fails

Check:

- [transactions.csv](D:/OneLab/reconciler/backend/data/transactions.csv) exists
- [settlements.csv](D:/OneLab/reconciler/backend/data/settlements.csv) exists
- the project was deployed with both the `backend/` and `frontend/` folders

## Alternative Platforms

If you deploy somewhere other than Render, keep the same startup command pattern:

```bash
python start_render.py
```

This works for most Python app hosting platforms such as Railway and similar services.
