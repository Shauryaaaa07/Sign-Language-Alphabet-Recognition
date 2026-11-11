# SignAI Developer Environment Setup & Execution Guide

**Project:** SignAI — Indian Sign Language Alphabet Recognition and Voice Conversion Platform  
**Target OS:** Windows 10/11, macOS, Linux  
**Runtime:** Python 3.11 + Node.js v20+ / v24+  

---

## 1. System Requirements & Prerequisites

| Component | Minimum Specification | Recommended Specification | Verified Platform |
|---|---|---|---|
| **Operating System** | Windows 10, macOS 12, Ubuntu 22.04 | Windows 11 (64-bit) | Windows 11 Pro |
| **Python** | Python 3.10 | Python 3.11.x (with Conda) | Python 3.11.16 (`fortress`) |
| **Node.js** | Node.js v18.x LTS | Node.js v20.x or v24.x | Node.js v24.20.0 |
| **Package Managers** | npm 9+ | npm 11+ | npm 11.x |
| **Deep Learning** | CPU (AVX2 support) | NVIDIA GPU with CUDA 12+ (Optional) | Intel CPU AVX2 |
| **Hardware** | Integrated or USB Webcam | 720p 30fps Webcam + Audio Speakers | Tested in manual validation |

> [!IMPORTANT]
> **Python Version Warning:** Avoid Python 3.13 or 3.14 for machine learning dependencies, as TensorFlow 2.16 binary wheels are not compiled for Python $\ge 3.13$. Python 3.11 is strongly recommended.

---

## 2. Environment Setup

### 2.1 Option A: Conda Environment (Recommended)

```bash
# 1. Create a clean Conda environment with Python 3.11
conda create -n fortress python=3.11 -y

# 2. Activate the environment
conda activate fortress

# 3. Install backend and machine learning dependencies
pip install -r backend/requirements.txt
```

### 2.2 Option B: Standard Python Virtual Environment

```bash
# 1. Create a virtual environment using Python 3.11
python -m venv .venv

# 2. Activate the virtual environment
# Windows (Command Prompt):
.venv\Scripts\activate.bat

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 2.3 Frontend Dependencies Installation

```bash
cd frontend
npm install
cd ..
```

---

## 3. Starting the Local Servers

SignAI operates via two local servers running in tandem:

### Terminal 1: FastAPI Backend Service (Port 8000)

Run the Uvicorn server from the **project root directory**:

```bash
# Ensure Conda or venv is activated
conda activate fortress

# Launch the FastAPI backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Health Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Terminal 2: React + Vite Frontend Service (Port 5173)

From the project root:

```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Or from within the `frontend/` directory:

```bash
cd frontend
npm run dev
```

- **Application URL:** [http://127.0.0.1:5173/](http://127.0.0.1:5173/)

---

## 4. Running Verification & Test Suites

### 4.1 Frontend Test Suites (57 Automated Checks)

Runs all 5 unit, integration, and state machine test suites:

```bash
npm --prefix frontend test
```

Individual test execution:
```bash
# Backend V4 API compatibility & schema fallback
node frontend/src/tests/v4_api_compatibility.test.mjs

# End-to-end user workflow simulation ("HELLO WORLD")
node frontend/src/tests/e2e_full_workflow.test.mjs

# Web Speech API state machine & voice filtering
node frontend/src/tests/speech_synthesis.test.mjs

# Text Builder string operations & metrics
node frontend/src/tests/text_builder.test.mjs

# Real-time webcam stability filter & concurrency locking
node frontend/src/tests/webcam_stability.test.mjs
```

### 4.2 Frontend Code Quality & Production Build

```bash
# Run Oxlint (fast Rust-based linter)
npm --prefix frontend run lint

# Compile production bundle
npm --prefix frontend run build

# Preview production build locally
npm --prefix frontend run preview
```

### 4.3 Backend Test Suite (12 Pytest Checks)

```bash
pytest backend/tests/test_api.py -v
```

### 4.4 Standalone Backend Integration Audit

Verifies model initialization, CORS headers, synthetic image inference, and error handling:

```bash
python backend/tests/audit_system_integration.py
```

---

## 5. Physical Hardware Verification Protocol

Automated test suites mock video and audio streams. To perform real-world hardware testing with a physical webcam and audio output:

1. Launch both backend (`port 8000`) and frontend (`port 5173`) servers.
2. Open [http://127.0.0.1:5173/studio](http://127.0.0.1:5173/studio) in Google Chrome, Microsoft Edge, or Firefox.
3. Grant camera permissions when prompted.
4. Position your hand inside the reticle guide and perform ISL hand signs.
5. Follow the step-by-step verification checklist in:
   [docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md).

---

## 6. Troubleshooting & Common Issues

### Issue 1: Windows PowerShell Script Execution Disabled
**Symptom:** `profile.ps1 cannot be loaded because running scripts is disabled on this system.`  
**Solution:** Either run commands in Command Prompt (`cmd.exe`), or bypass the policy for the current session:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Issue 2: Port 8000 or 5173 Already in Use
**Symptom:** `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`  
**Solution:** Find and terminate the process holding the port:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux / macOS
lsof -i :8000
kill -9 <PID>
```

### Issue 3: Camera Not Found or Permission Denied
**Symptom:** The webcam reticle displays `Camera Access Denied` or `NotFoundError`.  
**Solution:**
- Ensure no other application (e.g. Zoom, Teams) is exclusively locking the webcam device.
- Check browser site permissions: click the lock/settings icon beside the URL bar and toggle "Camera" to "Allow".
- Test using the **Image Upload** mode to verify recognition independently of hardware.
