# SignAI 2.0 — Comprehensive Setup & Reproducibility Guide

This document provides complete, reproducible step-by-step instructions to configure, install, execute, and verify the **SignAI 2.0** application from scratch.

---

## 1. System Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS 12+, Ubuntu 22.04 LTS | Windows 11 (x64) |
| **Python** | Python 3.11.x (Strict: TensorFlow 2.16 requires $\le 3.11$) | Python 3.11.11 via Conda |
| **Node.js** | Node.js v18.0.0+ | Node.js v20.x or v22.x LTS (npm $\ge 9.x$) |
| **Memory (RAM)** | 8 GB | 16 GB DDR4/DDR5 |
| **Processor** | Intel Core i5 / AMD Ryzen 5 (AVX2 support) | Intel Core i7 / AMD Ryzen 7 |
| **Peripherals** | Integrated 720p Webcam, Audio Speaker/Headphones | 1080p Webcam (30 fps) |

---

## 2. Environment Setup & Dependency Installation

### Step 2.1: Python Environment Creation (Miniconda Recommended)
Open PowerShell or your command prompt:
```powershell
# Create an isolated Python 3.11 environment
conda create -n signai python=3.11 -y

# Activate the environment
conda activate signai
```

### Step 2.2: Python Machine Learning & Backend Dependencies
> [!IMPORTANT]
> TensorFlow 2.16.2 on Windows requires `numpy < 2.0.0` (specifically `numpy 1.26.4`). Installing NumPy 2.x will trigger binary incompatibility errors in TensorFlow and OpenCV.

Run the harmonized pip installation:
```powershell
pip install tensorflow-intel==2.16.2 "numpy<2.0.0,>=1.23.5"
pip install mediapipe==1.2.0 opencv-python==4.10.0.84
pip install fastapi==0.115.6 "uvicorn[standard]==0.34.0" pydantic==2.10.6 starlette==0.41.3
pip install scikit-learn==1.6.1 pillow==11.1.0 httpx pytest
```

### Step 2.3: Verify MediaPipe Model Bundle Asset
Confirm that the official Tasks API model bundle exists at:
```
backend/vision/models/hand_landmarker.task  (~7.8 MB)
```
If the file is absent, download it from the official Google MediaPipe Tasks repository:
```powershell
python -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task', 'backend/vision/models/hand_landmarker.task')"
```

### Step 2.4: Frontend Node.js Dependencies
Navigate to the repository root:
```powershell
npm --prefix frontend install
```

---

## 3. Cryptographic Model Checkpoint Verification

Before running the application, verify that the champion CNN V4 checkpoint is authentic and untampered:
```powershell
# Windows PowerShell
Get-FileHash -Path saved_models/experiments/isl_alphabet_cnn_v4_best.keras -Algorithm SHA256
```
**Expected Output:**
```
Algorithm: SHA256
Hash:      4616E94B2C42FBCA0E11247BF922E7EDEA96BDBDF44215B1318C35B80A093762
```

---

## 4. Running the Application

### Development Mode (Recommended)

Start the two decoupled tiers in separate terminal sessions:

#### Terminal 1 — Backend API Service:
```powershell
# Ensure your conda environment is active
conda activate signai

# Start Uvicorn ASGI server on port 8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend initializes the CNN V4 model, registers modular routers, and serves endpoints at `http://127.0.0.1:8000`.*

#### Terminal 2 — Frontend Vite Dev Server:
```cmd
npm --prefix frontend run dev
```
*Vite starts instantly at `http://127.0.0.1:5173`.*

Open your browser to:
👉 **`http://127.0.0.1:5173`**

---

### Production Build & Serving

To verify or deploy the compiled production bundle:

```powershell
# 1. Compile the optimized client bundle
npm --prefix frontend run build

# 2. Preview the compiled production build locally
npm --prefix frontend run preview
```
Output artifacts are generated in `frontend/dist/` (clean HTML5, minified JavaScript, and CSS).

---

## 5. Running the Complete Verification Test Suite

### 5.1 Backend Automated Tests (37 Unit Tests via Unittest)
```powershell
python -m unittest discover -s backend/tests
```
**Expected Output:**
```
Ran 37 tests in ~4.3s. OK
```

### 5.2 Full Backend API Suite (49 Tests via Pytest)
```powershell
pytest backend/tests
```
**Expected Output:**
```
49 passed in ~16s
```

### 5.3 Frontend Compatibility & State Tests (57 Tests)
```powershell
npm --prefix frontend test -- --run
```
**Expected Output:**
```
6 test files executed. 57/57 tests passed (100%).
```

### 5.4 Frontend Code Linting
```powershell
npm --prefix frontend run lint
```
**Expected Output:**
```
0 errors found.
```

---

## 6. Common Troubleshooting & Gotchas

### 1. `ImportError: cannot import name 'triu' from 'numpy'`
- **Cause:** NumPy 2.x was installed, which is incompatible with TensorFlow 2.16.2.
- **Resolution:** Force install NumPy 1.26.4:
  ```powershell
  pip install "numpy==1.26.4"
  ```

### 2. Browser Camera Access Denied (`NotAllowedError`)
- **Cause:** Browser blocked access to the webcam sensor.
- **Resolution:**
  - In Chrome / Edge: Click the site security padlock icon on the left side of the URL bar (`http://127.0.0.1:5173`).
  - Toggle **Camera** to **Allow**.
  - Refresh the page and click **Start Camera** again.

### 3. Backend Returns HTTP 500 on Grad-CAM
- **Cause:** Incompatible TensorFlow layer lookup.
- **Resolution:** Layer resolution is automated in `backend/explainability/gradcam.py` targeting `block3_conv2`. Ensure you are running Python with the `signai` environment active.

### 4. Port 8000 Already in Use
- **Cause:** A previous Uvicorn background process was not terminated.
- **Resolution (Windows):**
  ```powershell
  # Find PID using port 8000
  netstat -ano | findstr :8000
  # Terminate process by PID (e.g., 1234)
  taskkill /PID 1234 /F
  ```