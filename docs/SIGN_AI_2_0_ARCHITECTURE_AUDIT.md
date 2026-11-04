# SignAI 2.0 — Architecture Audit & System Specification

**Project:** SignAI — Indian Sign Language Alphabet Recognition Platform  
**Audit Scope:** Complete System Audit Prior to Advanced Upgrade (Stage 0)  
**Date:** November 2026  
**Auditor:** Senior AI/ML Engineer, Computer Vision Researcher, Backend Architect, Frontend Engineer  
**Status:** Certified Baseline Established (Immutability Enforced)

---

## 1. Executive Summary & Purpose

This audit establishes the rigorous technical foundation for the **SignAI 2.0 Upgrade**. SignAI is an existing, functional academic research prototype designed to recognize the 26 Indian Sign Language (ISL) fingerspelling alphabet classes (A–Z).

This upgrade is **additive and modular**. It enhances the system with:
1. MediaPipe Hand Landmark Detection & Real-Time Skeletal Tracking
2. Landmark-based Alphabet Classification (independent model pipeline)
3. Multimodal CNN + Landmark Feature Fusion
4. Dynamic Temporal Gesture Recognition infrastructure (LSTM / GRU for moving signs like J and Z)
5. Explainable AI with Grad-CAM activation heatmaps
6. Confidence Calibration & Uncertainty Quantification
7. Real-Time Camera Quality & Illumination Monitoring
8. Smart Text Builder with Undo, Timestamped History, and Multilingual Speech Synthesis
9. Interactive Practice Mode and Advanced Multi-Model Analytics

---

## 2. Existing Baseline Architecture & Artifact Verification

### 2.1 Model Checkpoint Immutability & Forensic Hashing
The primary static vision model is **CNN V4** (Experiment 3).

| Property | Value | Verification Source |
|---|---|---|
| **Checkpoint Path** | `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` | Local File System |
| **Cryptographic SHA-256** | `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762` | Direct Binary Hash |
| **Trainable Parameters** | 308,218 parameters | Keras Model Inspection |
| **Input Tensor Shape** | `(None, 128, 128, 3)` (RGB, float32 normalized $[0.0, 1.0]$) | Model Graph |
| **Output Tensor Shape** | `(None, 26)` (Softmax probability distribution) | Model Graph |
| **Grad-CAM Conv Layer** | `block3_conv2` (Output: `(None, 32, 32, 128)`) | Model Graph |
| **Independent Test Accuracy** | **86.34%** (4,456 correct / 5,161 independent test images) | `results/final/v4_test_predictions.csv` |
| **Macro F1-Score** | **83.96%** | `results/final/v4_test_classification_report.csv` |
| **Weighted F1-Score** | **83.87%** | `results/final/v4_test_classification_report.csv` |

```
CNN V4 Layer Topology:
InputLayer: (None, 128, 128, 3)
  ├── Block 1: Conv2D(32, 3x3) -> BatchNorm -> ReLU -> Conv2D(32, 3x3) -> BatchNorm -> ReLU -> MaxPool(2x2) -> (64, 64, 32)
  ├── Block 2: Conv2D(64, 3x3) -> BatchNorm -> ReLU -> Conv2D(64, 3x3) -> BatchNorm -> ReLU -> MaxPool(2x2) -> (32, 32, 64)
  ├── Block 3: Conv2D(128, 3x3) -> BatchNorm -> ReLU -> Conv2D(128, 3x3) [Grad-CAM Layer] -> BatchNorm -> ReLU -> MaxPool(2x2) -> (16, 16, 128)
  └── Classifier Head: GlobalAveragePooling2D(128) -> Dense(128, ReLU) -> Dropout(0.40) -> Dense(26, Softmax)
```

> [!IMPORTANT]
> **PRESERVATION MANDATE:** The weights and architecture of CNN V4 are frozen. No training or fine-tuning will touch `saved_models/experiments/isl_alphabet_cnn_v4_best.keras`. It serves as the baseline benchmark and default fallback.

---

### 2.2 Dataset Partitions & Leakage Audit

The project uses the deduplicated, quarantined **RealSign ISL Dataset**:

| Split | Location | Image Count | Classes | Role in SignAI 2.0 |
|---|---|---|---|---|
| **Training** | `dataset/processed/Training/` | **17,407** | 26 (A–Z) | Training landmark & fusion models |
| **Validation** | `dataset/processed/Validation/` | **2,517** | 26 (A–Z) | Model selection, tuning, calibration |
| **Testing** | `dataset/processed/Testing/` | **5,161** | 26 (A–Z) | **Strictly Frozen** (Held-out benchmark only) |
| **Total** | `dataset/processed/` | **25,085** | 26 (A–Z) | Immutability strictly enforced |

> [!CAUTION]
> **Data Integrity Rule:** The `Testing` split will NEVER be used for training, feature extraction tuning, temperature scaling calibration, or threshold selection. All development occurs strictly on `Training` and `Validation`.

---

### 2.3 Existing Endpoints & Backend Contract

The FastAPI backend (`backend/main.py`) runs on `http://127.0.0.1:8000`:

1. `GET /health` -> `HealthResponse`:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "model_name": "isl_alphabet_cnn_v4_best.keras",
     "num_classes": 26,
     "classes": ["A", "B", ..., "Z"]
   }
   ```
2. `POST /predict` -> `PredictionResponse`:
   - Payload: `multipart/form-data` with field name `file`.
   - Response: `predicted_letter`, `predicted_class`, `confidence` (0.0 to 1.0), `top_predictions` (`[{letter, confidence}]`), `inference_time_ms`, `status`.
3. Allowed CORS: `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`.

---

### 2.4 Existing Frontend Architecture & Routes

The React 19 + Vite frontend operates hash-based navigation:
- `/#home`: Landing page with step-by-step workflow and text builder overview.
- `/#studio`: Dual-tab recognition studio (Camera with 3-frame stability buffer + Drag-and-drop Image Upload) and Text Builder with SpeechSynthesis.
- `/#learn`: 26 alphabet cards with practice modal links.
- `/#dashboard`: Live browser session history and telemetry.
- `/#performance`: Experiment progression (V1 to V5), robustness curves, and confusion matrix.
- `/#about`: Project DL-010 academic context, technology stack, and documented limitations.

---

### 2.5 Existing Test Baseline

- **Backend Tests:** 12 tests passing (`backend/tests/test_api_endpoints.py`).
- **Frontend Tests:** 57 tests passing across 6 suites:
  1. `v4_api_compatibility.test.mjs` (6 suites)
  2. `e2e_full_workflow.test.mjs` (16 steps + edge cases)
  3. `speech_synthesis.test.mjs` (5 suites)
  4. `text_builder.test.mjs` (11 suites)
  5. `webcam_stability.test.mjs` (3 suites)
  6. `new_ui_components.test.mjs` (6 suites)
- **Total Existing Test Baseline:** **69 automated tests** (100% passing).
- All 69 baseline tests must remain passing throughout the upgrade.

---

## 3. Dependency & Environment Inventory

- **Python Runtime:** 3.11.16 (`fortress` conda environment)
- **TensorFlow:** 2.16.2
- **scikit-learn:** 1.9.1
- **Pillow:** 12.3.0
- **NumPy:** 1.26.4
- **FastAPI:** 0.115.0+ / Pydantic v2
- **Node.js / NPM:** Node v20+ / npm v10+
- **Vite:** 8.3.5
- **React:** 19.3.1

---

## 4. Integration Risks & Mitigation Strategies

| Risk | Impact | Prevention / Mitigation Strategy |
|---|---|---|
| **CNN V4 Degradation** | Breaking working baseline | Checkpoint SHA-256 immutability verification in test suite; load as read-only. |
| **API Breaking Changes** | Frontend breakage | Maintain strict backward compatibility for `/predict` and `/health`. Route new capabilities through namespaced routers (`/vision/*`, `/explain/*`, `/temporal/*`). |
| **MediaPipe Heavyweight Load** | Browser freeze or high latency | Use client-side MediaPipe WASM with requestAnimationFrame and frame throttling (15-20 FPS); add server-side `hand_landmarker.py` for batch feature extraction and offline evaluation. |
| **Static vs Dynamic Data Leakage** | Scientifically invalid dynamic claims | Clearly declare that RealSign contains static images. Temporal LSTM/GRU pipeline is built as an extensible architecture, with trained dynamic models marked as pending recorded video dataset collection. |
| **Overfitting on Hand Landmarks** | False high confidence | Train Landmark classifier strictly on `Training` split; evaluate on `Validation`. Use normalized wrist-relative angles and scale-invariant distances. |
| **Grad-CAM Graph Errors in Keras 3** | Inference failure | Use `tf.GradientTape` targeting `model.get_layer('block3_conv2').output` with an isolated sub-model. |

---

## 5. SignAI 2.0 Module Architecture

```
SignAI 2.0 Upgraded Architecture:

backend/
├── main.py                          # Unified FastAPI app with modular routers
├── config.py                        # Centralized paths and hyperparameters
├── model_loader.py                  # Singleton cache for CNN V4, Landmark, Fusion
├── prediction.py                    # Static CNN V4 inference pipeline
├── schemas.py                       # Extended Pydantic request/response schemas
├── vision/                          # [NEW] Advanced Vision Modules
│   ├── hand_landmarker.py           # MediaPipe 21-landmark extraction & normalization
│   ├── camera_quality.py            # Brightness, contrast, blur, hand framing analysis
│   └── landmark_features.py         # Angles, extension, wrist-relative feature engineering
├── explainability/                  # [NEW] Explainable AI Modules
│   ├── gradcam.py                   # Grad-CAM gradient calculation on block3_conv2
│   ├── heatmap_generator.py         # Colormap overlay and visualization generator
│   └── explainability_service.py    # Service orchestrator for explainability
├── services/                        # [NEW] Core Multi-Model Services
│   ├── fusion_service.py            # Multimodal CNN + Landmark inference & fallback
│   ├── calibration_service.py       # Temperature scaling & confidence calibration
│   └── analytics_service.py         # Multi-model metrics, latency & history tracking
├── temporal/                        # [NEW] Dynamic Gesture System
│   ├── sequence_collector.py        # Frame buffer, sequence normalization & padding
│   └── temporal_inference.py        # LSTM/GRU dynamic inference engine
├── routers/                         # [NEW] Namespaced FastAPI Routers
│   ├── prediction_routes.py         # /predict & /health backward compatibility
│   ├── vision_routes.py             # /vision/landmarks, /vision/quality
│   ├── explainability_routes.py     # /explain/gradcam
│   ├── model_routes.py              # /models/compare, /models/fusion
│   └── temporal_routes.py           # /temporal/status, /temporal/predict
└── tests/                           # Extended backend test suite

training/
├── landmark_pipeline/               # Landmark extraction, feature engineering, RF/SVM/MLP
├── fusion/                          # Multimodal fusion architecture and evaluation
├── temporal/                        # Sequence dataset collection, LSTM/GRU training
└── calibration/                     # Temperature scaling and reliability diagrams
```

---

## 6. Implementation Sequence (Stage-by-Stage)

1. **STAGE 0 — AUDIT:** Completed with this certified specification.
2. **STAGE 1 — MEDIAPIPE:** Backend `hand_landmarker.py` with 21 normalized landmarks, scale-invariant relative features, and unit tests.
3. **STAGE 2 — LANDMARK CLASSIFIER:** `training/landmark_pipeline/` feature extraction, dataset generation, Random Forest / SVM / MLP training and validation evaluation.
4. **STAGE 3 — EXPLAINABLE AI (GRAD-CAM):** `backend/explainability/` targeting `block3_conv2` with heatmap overlay and `/explain/gradcam` endpoint.
5. **STAGE 4 — CONFIDENCE & CAMERA QUALITY:** `backend/services/calibration_service.py` (temperature scaling, ECE) and `backend/vision/camera_quality.py` (blur, brightness, contrast).
6. **STAGE 5 — FUSION MODEL:** `training/fusion/` combining CNN V4 features and landmark vectors with fallback.
7. **STAGE 6 — TEMPORAL RECOGNITION:** `backend/temporal/` and `training/temporal/` sequence collector and LSTM/GRU architectures.
8. **STAGE 7 — APPLICATION UPGRADE:** Frontend Studio, Practice Mode, Model Lab, and multilingual speech integration.
9. **STAGE 8 — VALIDATION:** Full test suite execution (69 baseline + all new tests), lint, and production build.
10. **STAGE 9 — DOCUMENTATION:** 5 comprehensive technical reports in `docs/`.

---

## 7. Certified Acceptance Criteria Checklist

- [x] CNN V4 checkpoint verified (`4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`).
- [x] Original dataset splits documented and frozen.
- [x] Existing API contract documented for 100% backward compatibility.
- [x] Existing 69 automated tests recorded as baseline.
- [x] Implementation plan structured to prevent regressions.
