# SignAI — Indian Sign Language Recognition & Voice Conversion Platform

<div align="center">

### **Your Hands. Your Voice.**

*A production-ready, multimodal deep learning platform that bridges Indian Sign Language (ISL) fingerspelling and spoken English in real time.*

[![Python 3.11](https://img.shields.io/badge/Python-3.11.16-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow 2.16](https://img.shields.io/badge/TensorFlow-2.16.2-FF6F00.svg)](https://www.tensorflow.org/)
[![React 19](https://img.shields.io/badge/React-19.3.1-61DAFB.svg)](https://react.dev/)
[![Vite 8](https://img.shields.io/badge/Vite-8.3.5-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS 4](https://img.shields.io/badge/Tailwind-4.3.3-38B2AC.svg)](https://tailwindcss.com/)
[![Tests Passing](https://img.shields.io/badge/Automated_Tests-69%2F69_Passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 1. Executive Summary

Over 18 million individuals in India belong to the deaf and hard-of-hearing community. Communication barriers persist because the vast majority of hearing individuals are unfamiliar with Indian Sign Language (ISL).

**SignAI** solves this challenge through an end-to-end accessibility platform:
1. **Vision Engine:** Captures fingerspelled ISL signs from user webcam video streams or uploaded photos.
2. **Deep Neural Network:** Standardizes inputs to $128 \times 128 \times 3$ RGB tensors and classifies them across 26 letters ($A$ through $Z$) using our optimized **CNN V4** model (86.34% independent test accuracy, 83.96% Macro F1).
3. **Gesture Stabilization:** Implements a deterministic 3-consecutive-frame buffer filter ($\tau \ge 0.75$) with repeat-lock logic to eliminate hand transition flicker and character flooding.
4. **Sentence Constructor:** Provides an interactive Text Builder for word assembly, spacing, backspacing, and real-time sentence construction.
5. **Vocal Output:** Converts the constructed text into natural English speech via the browser-native Web Speech API (`window.speechSynthesis`).

---

## 2. System Architecture

SignAI operates as a **Three-Tier Decoupled System**:

```
[User Hand Gesture]
        │
        ▼ (Webcam Stream / File Upload)
┌────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER (Frontend)            │
│   React 19 • Vite 8 • Tailwind CSS 4 • Router v7       │
│                                                        │
│   • 6 Dedicated Routes (/, /studio, /learn, etc.)      │
│   • Dark / Light / System Theme Engine                 │
│   • 3-Frame Stability Filter & Repeat-Lock Machine     │
│   • Interactive Text Builder (Space / Backspace)       │
│   • Web Speech API Speech Synthesis Engine             │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP POST /predict (Multipart)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 SERVICE LAYER (Backend)                │
│             Python 3.11 • FastAPI • Uvicorn            │
│                                                        │
│   • Single-Instance Lifespan Model Caching             │
│   • Safe Bilinear Resampling & RGB Conversion          │
│   • Normalized Float32 Tensor Generation [0, 1]        │
│   • 10 MB Payload Guard & Strict MIME Validation       │
└───────────────────────────┬────────────────────────────┘
                            │ In-Memory Batch Tensor (1, 128, 128, 3)
                            ▼
┌────────────────────────────────────────────────────────┐
│               INFERENCE ENGINE (ML Core)               │
│          TensorFlow 2.16.2 / Keras 3.15.1              │
│                                                        │
│   • CNN V4 (308,218 Parameters; 3 Double-Conv Blocks) │
│   • Batch Normalization + L2 Regularization (1e-4)     │
│   • Global Average Pooling + Dense 128 (Dropout 0.40)  │
│   • 26-Class Softmax Probability Distribution          │
└────────────────────────────────────────────────────────┘
```

---

## 3. Controlled Experimentation & Model Benchmark

To achieve optimal generalization while respecting academic rigor, 5 model iterations were developed and validated under strictly controlled conditions:

| Model Version | Architecture Innovations & Techniques | Validation Accuracy | Validation Loss | Macro F1 | Test Accuracy (Held-out) | Test Macro F1 (Held-out) |
|---|---|---|---|---|---|---|
| **Baseline V1** | 3 Single-Conv Blocks, Flatten, Dense 128 | 61.27% | 1.8340 | 58.10% | 59.04% | 56.74% |
| **CNN V2** | 3 Double-Conv Blocks + Batch Normalization + GAP | 80.10% | 1.6701 | 73.10% | — | — |
| **CNN V3** | V2 + Geometric & Photometric Augmentation | 80.29% | 1.3732 | 75.52% | — | — |
| **CNN V4 (Selected)** | **V3 + L2 Kernel Regularization ($\lambda = 10^{-4}$)** | **80.14%** | **1.3507** | **77.68%** | **86.34%** | **83.96%** |
| **CNN V5** | V4 + SpatialDropout2D (0.15) | 75.29% | 1.5422 | 70.08% | — | — |

### Selected Candidate: CNN V4
- **Parameters:** 308,218 total (307,322 trainable, 896 non-trainable).
- **Independent Test Accuracy:** **86.34%** (4,456 of 5,161 correct predictions on held-out test split).
- **Macro F1 Score:** **83.96%** (+27.22 percentage points over baseline).
- **Perfection Classes (100% Precision & Recall):** D, H, L, R.
- **Top Performers (>90% F1):** B, G, J, K, M, O, P.

---

## 4. Frontend Application Routes

The SignAI web application features six production-ready routes accessible from the responsive navigation header:

| Route | View Name | Description |
|---|---|---|
| `/` | **Home** | SaaS landing experience featuring product value proposition, live stats, 4 core capability pillars, and interactive pipeline walkthrough card. |
| `/studio` | **Recognition Studio** | Production workspace with dual modes (File Upload & Live Webcam), reticle viewfinder, Prediction Hero, top-3 candidates, sentence constructor, and Web Speech controls. |
| `/learn` | **Alphabet Guide** | Visual reference gallery containing verified dataset sample photographs for all 26 ISL letters with modal placement tips. |
| `/dashboard` | **System Dashboard** | Operational diagnostics display showing 4 grounded KPI metrics, live `/health` connection monitor with auto-refresh, and decoupled architecture diagram. |
| `/performance` | **Benchmark & Evaluation** | Complete academic evaluation dashboard featuring the V1–V5 experiment comparison, full per-class metrics table, embedded confusion matrix, and failure mode analysis. |
| `/about` | **About & Mission** | Overview of India's 18M+ deaf population accessibility gap, UN SDG 10 alignment, decoupled 3-tier technical architecture, and academic integrity charter. |

### Visual Design System
- **Dark Mode (Default):** Deep slate background (`#0B1220`) with glassmorphism cards (`#111C30`).
- **Light Mode:** Modern crisp off-white background (`#F4F7FC`) with clean white surfaces (`#FFFFFF`).
- **System Mode:** Seamlessly synchronizes with OS preference via React 19's `useSyncExternalStore`.

---

## 5. Quickstart & Local Installation

### Prerequisites
- **Python 3.11** (e.g. via Conda environment `fortress`)
- **Node.js v20+ or v24+** and **npm 11+**

### Step 1: Clone and Configure Environment

```bash
# Clone the repository
git clone https://github.com/your-username/sign-language-alphabet-recognition.git
cd sign-language-alphabet-recognition

# Set up Python environment
conda create -n fortress python=3.11 -y
conda activate fortress
pip install -r backend/requirements.txt

# Set up Frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Start the Servers

Launch both servers in separate terminal sessions:

#### Terminal 1 — FastAPI Backend Service:
```bash
conda activate fortress
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend active at `http://127.0.0.1:8000` (API Docs: `http://127.0.0.1:8000/docs`)*

#### Terminal 2 — React Vite Frontend:
```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```
*Frontend active at `http://127.0.0.1:5173/`*

---

## 6. Verification & Automated Testing

SignAI includes 69 automated tests verifying backend contracts, error boundaries, UI interactions, and state machines:

```bash
# Run all frontend tests (57 tests)
npm --prefix frontend test

# Run frontend code linting (0 warnings, 0 errors)
npm --prefix frontend run lint

# Compile production frontend build
npm --prefix frontend run build

# Run backend test suite (12 pytest checks)
pytest backend/tests/test_api.py -v

# Run backend standalone integration audit
python backend/tests/audit_system_integration.py
```

### Hardware Verification Protocol
> [!NOTE]
> While all mock MediaStream lifecycles, canvas image extractions, and speech syntheses pass automated unit testing, **physical webcam input** and **physical audio output** require real-world user hardware. Follow our step-by-step checklist in [docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md).

---

## 7. Directory Structure

```
.
├── backend/
│   ├── config.py             # Paths, CORS origins, 10MB limits, image dimensions
│   ├── main.py               # FastAPI app, lifespan singleton model loader, endpoints
│   ├── model_loader.py       # Thread-safe model weight caching
│   ├── prediction.py         # Pillow RGB decoder, 128x128 resize, normalization, inference
│   ├── requirements.txt      # FastAPI, Uvicorn, TensorFlow, Pillow, NumPy
│   ├── schemas.py            # Pydantic v2 schemas for health and prediction responses
│   └── tests/
│       ├── audit_system_integration.py # Standalone integration audit
│       └── test_api.py       # 12 Pytest test cases
├── dataset/
│   └── processed/
│       ├── Training/         # 26 folders (A–Z) used for model training
│       ├── Validation/       # 26 folders (A–Z) used for hyperparameter tuning
│       └── Testing/          # 26 folders (A–Z) strictly held-out test split (5,161 images)
├── docs/
│   ├── architecture/
│   │   └── ARCHITECTURE.md   # Complete system architecture and state machines
│   ├── development/
│   │   └── SETUP.md          # Environment setup and developer execution guide
│   └── reports/              # 16 milestone reports and academic design blueprints
├── frontend/
│   ├── public/               # Static assets, verified alphabet samples, and eval charts
│   ├── src/
│   │   ├── components/       # Reusable UI components (Webcam, Upload, Prediction, Builder)
│   │   ├── context/          # React 19 ThemeContext (Dark, Light, System)
│   │   ├── hooks/            # useTheme custom hook
│   │   ├── pages/            # 6 route views (Home, Studio, Learn, Dashboard, etc.)
│   │   ├── services/         # API client module
│   │   ├── tests/            # 5 frontend test suites (57 tests)
│   │   ├── utils/            # Pure logic for text mutations & speech synthesis
│   │   ├── App.jsx           # Routing configuration & layout
│   │   └── index.css         # Tailwind CSS 4 theme tokens
│   ├── package.json
│   └── vite.config.js
├── results/
│   ├── confusion_matrix.png  # High-resolution confusion matrix
│   ├── per_class_metrics.png # Per-class precision, recall, and F1 distribution chart
│   └── experiments/          # CSV histories and training metric curves for V1–V5
├── saved_models/
│   └── experiments/
│       └── isl_alphabet_cnn_v4_best.keras # Selected production model checkpoint
└── training/
    ├── data_pipeline.py      # TF data generator with data augmentations
    ├── evaluate_model.py     # Independent evaluation script
    ├── label_classes.json    # Verified mapping of 26 classes
    └── train_model.py        # Model training script
```

---

## 8. Academic Integrity & Honest Limitations

1. **Static 2D CNN vs Dynamic Motion (J & Z):** Natural ISL fingerspelling for 'J' and 'Z' entails continuous spatial trajectories. As a static 2D CNN system, SignAI classifies static keyframes. Future extensions will integrate temporal sequence models (e.g. MediaPipe Hands + LSTM / Transformer).
2. **Planar Occlusion (W vs E/I/X):** Certain viewing angles introduce finger overlap in 2D projections. Multi-view inputs or 3D landmark estimations are recommended for next-generation iterations.
3. **Hardware Transparency:** Automated test suites verify 100% of mock logic. Real-world camera and speaker validations are transparently documented as requiring user device execution.

---

## 9. License & Acknowledgments

This project is developed under the **MIT License**. We gratefully acknowledge the open-source community, TensorFlow, FastAPI, and React teams for providing the robust foundations that make accessible assistive technology possible.
