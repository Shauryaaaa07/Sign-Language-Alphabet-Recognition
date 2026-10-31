# Environment Setup Guide

This guide details how to configure your local development machine to run the backend, frontend, and training pipelines.

---

## 1. Prerequisites
- **Python:** Python 3.10 or 3.11 is required for TensorFlow stability on Windows. (Avoid Python 3.14 for ML dependencies as binary wheels are unavailable).
- **Node.js:** Node.js v18+ or v20+ with npm.
- **Git:** Git installed with command-line tools.

---

## 2. Python Virtual Environment Setup

### Using Conda / Miniconda (Recommended):
```bash
# Create a dedicated environment with Python 3.11
conda create -n isl-env python=3.11 -y
conda activate isl-env

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Or install training pipeline dependencies
cd ../training
pip install -r requirements.txt
```

### Using standard Python venv (with Python 3.11):
```bash
py -3.11 -m venv .venv
# Activate on Windows PowerShell:
.venv\Scripts\Activate.ps1
# Activate on Command Prompt:
.venv\Scripts\activate.bat

# Install dependencies:
pip install -r backend/requirements.txt
```

---

## 3. Frontend Setup (React + Vite + Tailwind CSS)

```bash
cd frontend
npm install
npm run dev
```
The frontend development server will launch at: `http://localhost:5173/`

To test production build:
```bash
npm run build
```

---

## 4. Running the Backend Service (Phase 6 onwards)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 5. Security & Git Discipline
- **NEVER** commit `.venv/`, `node_modules/`, or large image datasets.
- Ensure `.gitignore` is active before staging files (`git status`).
- Never push to GitHub without group approval.
