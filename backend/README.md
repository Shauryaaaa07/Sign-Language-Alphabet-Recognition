# SignAI 2.0 — FastAPI Multimodal Backend Service

This directory contains the modular, production-ready FastAPI inference backend for **SignAI 2.0 — Multimodal Indian Sign Language (ISL) Alphabet Recognition & Voice Conversion System**.

It powers real-time inference using the frozen **CNN V4** baseline checkpoint alongside **MediaPipe Dual-Hand Landmarker** tracking (`num_hands=2`, 78D kinematic features per hand), **Multimodal Feature Fusion** (`192D` CNN + Landmark concatenation), **Grad-CAM Visual Explainability** (`block3_conv2`), **Camera Optical Quality Telemetry**, and **Temporal Dynamic Sequence Inference** (`BiLSTM` / `BiGRU`).

---

## 1. Active Model Suite

| Model | Type | Checkpoint Path | Parameters | Primary Evaluation Metric |
| :--- | :--- | :--- | :--- | :--- |
| **CNN V4** *(Baseline)* | 2D Convolutional Neural Network | `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` | 308,218 | **86.34%** Test Acc · **83.96%** Macro F1 |
| **Multimodal Fusion** | Dual-Stream Late Fusion Head | `saved_models/fusion/isl_multimodal_fusion_best.keras` | 331,610 *(26,426 trainable)* | **86.32%** Val Acc · **82.40%** Macro F1 |
| **Landmark MLP** | Kinematic Geometric MLP | `saved_models/landmark_classifier/isl_landmark_mlp_best.keras` | 18,458 | **69.17%** Val Acc · **63.77%** Macro F1 |
| **Landmark RF** | Random Forest Classifier | `saved_models/landmark_classifier/isl_landmark_rf_baseline.joblib` | Ensemble | **77.65%** Val Acc |
| **BiLSTM / BiGRU** *(Prototype)* | Recurrent Dynamic Sequence | `saved_models/temporal/isl_bilstm_dynamic.keras` / `isl_bigru_dynamic.keras` | 118,787 / 89,667 | Dynamic Prototype (`STATIC_HOLD`, `J`, `Z`) |

> **CNN V4 Immutability SHA-256:** `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`

---

## 2. Backend Directory Structure

```text
backend/
├── config.py                     # Model paths, CORS origins, image specs (128x128 RGB), upload guards
├── main.py                       # FastAPI app, lifespan singleton loader, core /health & /predict routes
├── model_loader.py               # Thread-safe CNN V4 checkpoint & class mapping loader
├── prediction.py                 # Image decoding, bilinear resizing, [0,1] normalization, CNN inference
├── schemas.py                    # Pydantic response & error schemas
├── requirements.txt              # Verified Python runtime & test dependencies
├── README.md                     # Backend service documentation
├── routers/
│   ├── vision_routes.py          # /vision/landmarks & /vision/quality endpoints
│   ├── explainability_routes.py  # /explain/gradcam endpoint
│   ├── model_routes.py           # /models/summary, /models/fusion/predict, /models/compare endpoints
│   └── temporal_routes.py        # /temporal/stream, /temporal/reset, /temporal/status endpoints
├── vision/
│   ├── hand_landmarker.py        # MediaPipe HandLandmarker (num_hands=2), handedness & bounding boxes
│   ├── landmark_features.py      # 78-dim wrist-relative normalized geometry, joint angles & fingertip dists
│   ├── camera_quality.py         # Brightness, contrast & Laplacian blur sharpness analyzer
│   └── models/hand_landmarker.task
├── explainability/
│   ├── gradcam.py                # Gradient-weighted Class Activation Map extractor (block3_conv2)
│   ├── heatmap_generator.py      # Colorized overlay blending & base64 encoding
│   └── explainability_service.py # Unified Grad-CAM explanation service
├── services/
│   ├── fusion_service.py         # Multimodal CNN + Landmark inference with automatic CNN V4 fallback
│   └── calibration_service.py    # Temperature scaling (T=1.28) & Expected Calibration Error (ECE)
├── temporal/
│   ├── sequence_collector.py     # Sliding 30-frame window & motion energy calculator
│   └── temporal_inference.py     # BiLSTM / BiGRU temporal gesture recognizer
└── tests/
    ├── test_api.py               # 12 API integration tests (pytest)
    ├── test_hand_landmarker.py   # 10 single & dual-hand MediaPipe tests (unittest)
    ├── test_camera_quality.py    # 7 optical quality & calibration tests (unittest)
    ├── test_temporal.py          # 6 temporal collector & sequence tests (unittest)
    ├── test_gradcam.py           # 5 Grad-CAM attribution & overlay tests (unittest)
    ├── test_new_routes.py        # 5 extended router integration tests (unittest)
    ├── test_fusion.py            # 4 multimodal fusion & fallback tests (unittest)
    └── audit_system_integration.py
```

---

## 3. Environment Setup & Launch

Recommended Python version: **Python 3.11** (tested with Python `3.11.16` in Conda env `fortress`).

```bash
# Activate environment and install dependencies
conda activate fortress
pip install -r backend/requirements.txt

# Start Uvicorn from the repository root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **Health Diagnostics:** `http://127.0.0.1:8000/health`

---

## 4. Complete API Reference (12 Endpoints)

| Method | Endpoint | Router Module | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | `main.py` | Root service metadata and quick endpoint links |
| `GET` | `/health` | `main.py` | Runtime health check, CNN V4 load confirmation, and 26 A–Z classes |
| `POST` | `/predict` | `main.py` | CNN V4 classification with top-3 candidates and latency (ms) |
| `POST` | `/vision/landmarks` | `vision_routes.py` | Dual-hand MediaPipe detection (`num_hands=2`), 21 3D points, 78D vectors, bboxes |
| `POST` | `/vision/quality` | `vision_routes.py` | Real-time brightness, contrast, Laplacian blur sharpness & feedback |
| `POST` | `/explain/gradcam` | `explainability_routes.py` | Layer `block3_conv2` Grad-CAM heatmap overlay & base64 visualization |
| `GET` | `/models/summary` | `model_routes.py` | Verified specs & benchmark summary across CNN V4, MLP, Fusion, and Temporal models |
| `POST` | `/models/fusion/predict` | `model_routes.py` | Multimodal CNN + Landmark inference with seamless fallback to CNN V4 |
| `POST` | `/models/compare` | `model_routes.py` | Side-by-side live prediction comparison across CNN V4, Landmark MLP, and Fusion |
| `POST` | `/temporal/stream` | `temporal_routes.py` | Pushes a 78D landmark vector into the 30-frame sliding sequence buffer |
| `POST` | `/temporal/reset` | `temporal_routes.py` | Clears the temporal sliding buffer state |
| `GET` | `/temporal/status` | `temporal_routes.py` | Reports buffer fullness, motion energy, and cooldown status |

---

## 5. Automated Testing (49 Tests)

```bash
# Run all 49 backend tests (37 unittest + 12 pytest API tests)
pytest backend/tests -v

# Run unittest-compatible modules directly (37 tests across 6 suites)
python -m unittest discover -s backend/tests -v
```
