# SignAI 2.0 — Multimodal Indian Sign Language Recognition & Voice Platform

<div align="center">

### **Your Hands. Your Voice.**

*A modular, multimodal deep learning and computer vision platform that translates 26-class Indian Sign Language (ISL) fingerspelling into real-time visual explanations, text, and spoken English.*

[![Python 3.11](https://img.shields.io/badge/Python-3.11.16-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow 2.16](https://img.shields.io/badge/TensorFlow-2.16.2-FF6F00.svg)](https://www.tensorflow.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-1.2.0-00BFA5.svg)](https://developers.google.com/mediapipe)
[![React 19](https://img.shields.io/badge/React-19.3.1-61DAFB.svg)](https://react.dev/)
[![Vite 8](https://img.shields.io/badge/Vite-8.3.5-646CFF.svg)](https://vitejs.dev/)
[![Backend Tests](https://img.shields.io/badge/Backend_Tests-49%2F49_Passed-brightgreen.svg)]()
[![Frontend Tests](https://img.shields.io/badge/Frontend_Suites-6%2F6_Passed-brightgreen.svg)]()

</div>

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Models & Empirical Benchmarks](#3-models--empirical-benchmarks)
4. [Frontend Application (8 Interactive Views)](#4-frontend-application-8-interactive-views)
5. [Backend REST API Reference](#5-backend-rest-api-reference)
6. [Quickstart & Local Installation](#6-quickstart--local-installation)
7. [Verification & Automated Testing](#7-verification--automated-testing)
8. [Repository Directory Structure](#8-repository-directory-structure)
9. [Documentation Index](#9-documentation-index)
10. [Academic Integrity & Known Limitations](#10-academic-integrity--known-limitations)

---

## 1. Executive Summary

Millions of individuals in India rely on Indian Sign Language (ISL) as their primary mode of communication, yet everyday digital interfaces rarely understand manual fingerspelling. **SignAI 2.0** bridges this communication barrier through an integrated, explainable computer vision pipeline:

1. **Frozen Visual Baseline (CNN V4):** Classifies $128 \times 128 \times 3$ RGB frames across all 26 ISL alphabet classes (`A–Z`) with **86.34% test accuracy** and **83.96% Macro F1** on the strictly quarantined 5,161-image held-out test split.
2. **Dual-Hand MediaPipe Tracking (`num_hands=2`):** Detects up to two hands simultaneously via MediaPipe `hand_landmarker.task`, extracting 21 3D landmarks, handedness (`Left` / `Right`), bounding boxes, and independent wrist-normalized **78-dimensional** geometric vectors (joint angles + fingertip distances) per hand.
3. **Multimodal Feature Fusion:** Combines CNN V4 visual embeddings (`128D`) with MediaPipe kinematic embeddings (`64D`) into a `192D` late-fusion classifier (**86.32% validation accuracy**, **82.40% Macro F1**), with automatic fallback to pure CNN V4 whenever hand landmarks are unavailable.
4. **Explainable AI (Grad-CAM):** Computes gradient-weighted class activation heatmaps from layer `block3_conv2` to visually highlight discriminative finger regions behind each prediction.
5. **Optical Quality & Calibration:** Evaluates live frame brightness, contrast, and Laplacian blur sharpness while applying temperature scaling calibration ($T = 1.28$).
6. **Temporal Sequence Prototype:** Streams 30-frame 78D windows into Bidirectional LSTM and Bidirectional GRU networks to detect dynamic trajectories (`J`, `Z` vs `STATIC_HOLD`).
7. **Interactive Sentence Builder & Voice Output:** Uses a deterministic 3-frame stability filter ($\tau \ge 0.75$) to assemble clean English words and vocalize them through Web Speech API with pitch customization.

---

## 2. System Architecture

```text
[Live Webcam Stream / Uploaded Hand Gesture Image]
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│               PRESENTATION LAYER (React 19 + Vite 8)                 │
│   8 Hash-Routed Views: #home, #studio, #practice, #models,           │
│   #learn, #dashboard, #performance, #about                           │
│                                                                      │
│   • Dual-Hand Skeleton Canvas Overlay (Amber Left / Sapphire Blue R) │
│   • 3-Frame Stability Filter (τ ≥ 0.75) & Repeat-Lock Debouncer      │
│   • Interactive Sentence Builder (Space, Backspace, Undo, Clear)     │
│   • Web Speech Synthesis Engine with Pitch Control (0.5 – 1.5)       │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │ REST API (Multipart Image / JSON)
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│              SERVICE LAYER (Python 3.11 + FastAPI + Uvicorn)         │
│                                                                      │
│   • Core Routes:       GET /health, POST /predict                    │
│   • Vision Router:     POST /vision/landmarks, POST /vision/quality  │
│   • Explain Router:    POST /explain/gradcam                         │
│   • Model Lab Router:  GET /models/summary, POST /models/fusion/..., │
│                        POST /models/compare                          │
│   • Temporal Router:   POST /temporal/stream, /reset, GET /status    │
└──────────────────────────────────┬───────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌───────────────────┐    ┌───────────────────┐    ┌────────────────────┐
│  VISION STREAM    │    │  LANDMARK STREAM  │    │  TEMPORAL STREAM   │
│  CNN V4 (Frozen)  │    │  MediaPipe (2x21) │    │  30-Frame Sliding  │
│  128x128x3 RGB    │    │  78D Geometry/Hand│    │  Window Collector  │
│  308,218 Params   │    │  MLP / RF Models  │    │  BiLSTM / BiGRU    │
└─────────┬─────────┘    └─────────┬─────────┘    └────────────────────┘
          │    128D + 64D = 192D   │
          └───────────┬────────────┘
                      ▼
        ┌───────────────────────────┐
        │  MULTIMODAL FUSION HEAD   │
        │  (Automatic CNN Fallback) │
        └───────────────────────────┘
```

---

## 3. Models & Empirical Benchmarks

### 3.1 CNN Ablation Progression (V1–V5)

| Model Version | Architectural & Training Configuration | Validation Acc | Validation Loss | Validation Macro F1 | Held-Out Test Acc | Held-Out Macro F1 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline V1** | 3 Single-Conv Blocks + Flatten + Dense 128 | 61.27% | 1.8340 | 56.74% | 59.04% | 56.74% |
| **CNN V2** | 3 Double-Conv Blocks + BatchNorm + GAP | 80.10% | 1.6701 | 73.10% | — | — |
| **CNN V3** | V2 + Geometric & Photometric Augmentation | 80.29% | 1.3732 | 75.52% | — | — |
| **CNN V4 (Selected)** | **V3 + L2 Kernel Regularization ($\lambda = 10^{-4}$)** | **80.14%** | **1.3507** | **77.68%** | **86.34%** | **83.96%** |
| **CNN V5** | V4 + SpatialDropout2D (`0.15`) | 75.29% | 1.5422 | 70.08% | — | — |

### 3.2 Multimodal & Temporal Paradigm Comparison

| Model Identifier | Paradigm | Parameters | Validation Acc | Validation Macro F1 | Checkpoint Location |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **CNN V4** *(Production)* | Vision CNN | 308,218 *(307,322 trainable)* | 80.14% | 77.68% | [`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`](saved_models/experiments/isl_alphabet_cnn_v4_best.keras) |
| **Landmark MLP** | 78D Kinematics | 18,458 | 69.17% | 63.77% | [`saved_models/landmark_classifier/isl_landmark_mlp_best.keras`](saved_models/landmark_classifier/isl_landmark_mlp_best.keras) |
| **Landmark RF** | 78D Ensemble | Scikit-learn RF | 77.65% | — | [`saved_models/landmark_classifier/isl_landmark_rf_baseline.joblib`](saved_models/landmark_classifier/isl_landmark_rf_baseline.joblib) |
| **Multimodal Fusion** | CNN + Landmarks | 331,610 *(26,426 trainable)* | **86.32%** | **82.40%** | [`saved_models/fusion/isl_multimodal_fusion_best.keras`](saved_models/fusion/isl_multimodal_fusion_best.keras) |
| **BiLSTM / BiGRU** | Dynamic Prototype | 118,787 / 89,667 | *(Prototype)* | *(Prototype)* | [`saved_models/temporal/`](saved_models/temporal/) |

> **Quarantined Dataset Integrity:** `dataset/processed/Testing/` (5,161 images across 26 classes) remains untouched for final unseen CNN V4 evaluation (**4,456 / 5,161 correct predictions**). CNN V4 checkpoint SHA-256: `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`.

---

## 4. Frontend Application (8 Interactive Views)

Built with **React 19**, **Vite 8**, and **Tailwind CSS 4** in an **Editorial Modernist** interface:

| Route | View Name | Capabilities |
| :--- | :--- | :--- |
| `#home` | **Home** | System overview, interactive 4-step pipeline card, and quick-launch controls |
| `#studio` | **Studio** | Webcam & upload modes, Fusion vs CNN V4 switcher, dual-hand skeleton canvas, Grad-CAM modal, optical quality HUD, sentence builder, and TTS with Pitch slider |
| `#practice` | **Practice** | Guided sign drills with live image verification, `+50 XP` scoring, streak counter, and reset controls |
| `#models` | **Model Lab** | Architecture comparison cards and side-by-side multi-model inference on any test image |
| `#learn` | **Learn A–Z** | Complete 26-letter ISL alphabet reference cards backed by verified dataset imagery |
| `#dashboard` | **Dashboard** | Quarantined baseline KPIs, live `/health` heartbeat monitor, confidence histogram, and inference logs |
| `#performance` | **Performance** | Model V1–V5 progression bars, perturbation robustness stress-test metrics, and confusion matrix |
| `#about` | **About** | Multimodal research overview, tech stack, and explicit project limitations |

---

## 5. Backend REST API Reference

| Method | Endpoint | Summary |
| :--- | :--- | :--- |
| `GET` | `/` | Service metadata & documentation URLs |
| `GET` | `/health` | System health status, model initialization state, and 26 classes |
| `POST` | `/predict` | Pure CNN V4 prediction, top-3 candidates, and latency |
| `POST` | `/vision/landmarks` | Dual-hand MediaPipe 21-point detection, handedness, bounding boxes, and 78D vectors |
| `POST` | `/vision/quality` | Frame brightness, contrast, blur sharpness, and framing guidance |
| `POST` | `/explain/gradcam` | CNN V4 `block3_conv2` Grad-CAM heatmap overlay |
| `GET` | `/models/summary` | Live architectural specs & benchmark JSON across all paradigms |
| `POST` | `/models/fusion/predict` | Multimodal CNN + Landmark inference with graceful CNN V4 fallback |
| `POST` | `/models/compare` | Side-by-side live prediction comparing CNN V4, Landmark MLP, and Fusion |
| `POST` | `/temporal/stream` | Streams 78D frame features into the 30-frame temporal buffer |
| `POST` | `/temporal/reset` | Resets the temporal sliding window queue |
| `GET` | `/temporal/status` | Reports temporal buffer fullness, motion energy, and cooldown state |

---

## 6. Quickstart & Local Installation

### Prerequisites
- **Python 3.11** (tested with Python `3.11.16` via Conda)
- **Node.js 18+** & **npm**

### Step 1 — Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Shauryaaaa07/Sign-Language-Alphabet-Recognition.git
cd Sign-Language-Alphabet-Recognition

# Create and activate Conda environment
conda create -n fortress python=3.11 -y
conda activate fortress
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2 — Run Both Servers Locally

#### Terminal 1 — FastAPI Backend (`http://127.0.0.1:8000`)
```bash
conda activate fortress
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger API Explorer: `http://127.0.0.1:8000/docs`

#### Terminal 2 — React Vite Frontend (`http://127.0.0.1:5173`)
```bash
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

---

## 7. Verification & Automated Testing

All automated backend and frontend checks execute with **100% pass rate**:

```bash
# 1. Backend full Pytest suite (49 tests: 12 API integration + 37 unit tests)
pytest backend/tests -v

# 2. Backend unittest discovery (37 unit tests across 6 modules)
python -m unittest discover -s backend/tests -v

# 3. Frontend automated suites (6 test modules)
npm --prefix frontend test

# 4. Frontend linter (0 errors)
npm --prefix frontend run lint

# 5. Frontend production bundle check
npm --prefix frontend run build
```

> **Hardware Verification Note:** Live browser webcam rendering, lighting shifts, dual-hand physical tracking, and audio playback (`HW-01` to `HW-10`) are documented in [`docs/SIGN_AI_2_0_FINAL_READINESS_CHECKLIST.md`](docs/SIGN_AI_2_0_FINAL_READINESS_CHECKLIST.md) for interactive human execution on device hardware.

---

## 8. Repository Directory Structure

```text
.
├── backend/                     # FastAPI multimodal service, routers, vision, explainability & tests
│   ├── config.py
│   ├── main.py
│   ├── model_loader.py
│   ├── prediction.py
│   ├── schemas.py
│   ├── requirements.txt
│   ├── README.md
│   ├── explainability/          # Grad-CAM extractor & color heatmap generator
│   ├── routers/                 # Modular API routers (/vision, /explain, /models, /temporal)
│   ├── services/                # Multimodal fusion & temperature scaling calibration
│   ├── temporal/                # 30-frame sequence collector & BiLSTM/BiGRU engine
│   ├── tests/                   # 49 automated pytest / unittest checks
│   └── vision/                  # MediaPipe dual-hand landmarker, 78D kinematics, quality analyzer
├── dataset/                     # Ignored local dataset workspace (Training / Validation / Testing)
├── docs/                        # Complete SignAI 2.0 reports, audits, architecture & setup guides
│   ├── SIGN_AI_2_0_*.md         # Final Project Report, Demo Guide, Setup Guide, Changelog & Checklist
│   ├── architecture/            # Technical architecture specifications
│   ├── development/             # Developer environment documentation
│   └── reports/                 # Chronological milestone reports & experimental write-ups
├── frontend/                    # React 19 + Vite 8 Editorial Modernist web application
│   ├── public/                  # 26 ISL alphabet images, sample assets & evaluation charts
│   ├── src/                     # App.jsx (8 views), styling, utilities & 6 automated test suites
│   ├── package.json
│   └── README.md
├── realworld_test/              # Unseen multi-user lighting/blur real-world evaluation test images
├── results/                     # Confusion matrices, per-class metrics, training curves & audit CSVs
├── saved_models/                # Trained checkpoints (CNN V4, Fusion, Landmark MLP/RF, BiLSTM/BiGRU)
├── training/                    # Data cleaning, CNN V1–V5 ablation, landmark, fusion & temporal scripts
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```

---

## 9. Documentation Index

| Document | Description |
| :--- | :--- |
| [`docs/SIGN_AI_2_0_FINAL_PROJECT_REPORT.md`](docs/SIGN_AI_2_0_FINAL_PROJECT_REPORT.md) | Complete academic thesis-style report covering architecture, math, and benchmarks |
| [`docs/SIGN_AI_2_0_ARCHITECTURE.md`](docs/SIGN_AI_2_0_ARCHITECTURE.md) | Multimodal system design, dual-hand extraction, and fusion mechanics |
| [`docs/SIGN_AI_2_0_MODEL_COMPARISON.md`](docs/SIGN_AI_2_0_MODEL_COMPARISON.md) | Reconciled comparative metrics across all 5 model families |
| [`docs/SIGN_AI_2_0_DEMO_GUIDE.md`](docs/SIGN_AI_2_0_DEMO_GUIDE.md) | 9-act live presentation script & viva defense Q&A |
| [`docs/SIGN_AI_2_0_SETUP_GUIDE.md`](docs/SIGN_AI_2_0_SETUP_GUIDE.md) | Step-by-step cold-start environment & verification guide |
| [`docs/SIGN_AI_2_0_FINAL_CHANGELOG.md`](docs/SIGN_AI_2_0_FINAL_CHANGELOG.md) | Chronological changelog of stabilization & upgrade edits |
| [`docs/SIGN_AI_2_0_FINAL_READINESS_CHECKLIST.md`](docs/SIGN_AI_2_0_FINAL_READINESS_CHECKLIST.md) | Automated verification vs pending physical hardware testing matrix |
| [`backend/README.md`](backend/README.md) | Backend service, router API docs & test instructions |
| [`frontend/README.md`](frontend/README.md) | Frontend Editorial Modernist UI routes, canvas overlay & test guide |

---

## 10. Academic Integrity & Known Limitations

1. **Alphabetical Fingerspelling Scope:** Supports isolated static letters (`A–Z`). Full continuous sentence-level ISL grammar requires multi-signer gloss video datasets.
2. **Dynamic Motion Signs (`J` & `Z`):** BiLSTM and BiGRU recurrent models provide a verified temporal inference architecture prototype; production accuracy on continuous moving gestures requires large-scale video sequence training.
3. **Environmental & Illumination Sensitivity:** Severe backlighting or extreme motion blur degrades optical classification, directly motivating camera quality telemetry and landmark-based feature fusion.
