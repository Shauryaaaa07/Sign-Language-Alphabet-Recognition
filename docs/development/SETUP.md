# Developer Environment Setup Guide

This guide details how to configure your local environment for backend development, frontend application execution, and machine learning training.

---

## 1. Prerequisites
- **Python:** Python 3.10 or 3.11 is required for TensorFlow and OpenCV binary wheel stability on Windows. (Avoid Python 3.14 for ML dependencies as precompiled wheels are unavailable).
- **Node.js:** Node.js v18+ or v20+ with npm.
- **Git:** Git 2.30+ installed with command-line tools.

---

## 2. Python Virtual Environment Setup

### Option A: Using Conda (Recommended):
```bash
# Create and activate an environment with Python 3.11
conda create -n isl-env python=3.11 -y
conda activate isl-env

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Or install ML training dependencies
cd ../training
pip install -r requirements.txt
```

### Option B: Using Standard Python venv (Python 3.11):
```bash
py -3.11 -m venv .venv

# Activate on Windows PowerShell:
.venv\Scripts\Activate.ps1
# Activate on Windows Command Prompt:
.venv\Scripts\activate.bat

# Install dependencies:
pip install -r backend/requirements.txt
```

---

## 3. Frontend Application Setup (React + Vite + Tailwind CSS)

```bash
cd frontend
npm install
npm run dev
```
The development server will run at: `http://localhost:5173/`

To verify the production build:
```bash
npm run build
```

---

## 4. Backend Service Execution (Phase 6 Onwards)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 5. Security & Exclusions
- Ensure `.gitignore` is active prior to staging files.
- Never commit credentials, `.env` files, or downloaded image archives.
