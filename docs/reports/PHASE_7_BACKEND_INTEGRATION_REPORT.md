# Phase 7 — Milestone 7.1: Backend Model Integration Report

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Milestone:** 7.1 — Integrate Final CNN V4 into FastAPI Backend  
**Date:** November 2, 2026  
**Status:** **`VERIFIED_AND_COMPLETE`**  

---

## 1. Executive Summary

In Milestone 7.1, the production-selected **CNN V4 model candidate** (`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`) was integrated into the FastAPI backend service. 

All backend components (`backend/config.py`, `backend/model_loader.py`, `backend/prediction.py`, `backend/schemas.py`, `backend/main.py`, and `backend/tests/test_api.py`) have been updated and verified. The model loads into memory upon FastAPI startup via application lifespan management, executes feed-forward inference on preprocessed 128×128 RGB normalized tensors, and returns verified prediction payloads with both `predicted_letter` and `predicted_class`, top-3 candidates, confidence bounds, and wall-clock inference latency.

Regression and unit tests executed via Pytest passed with **100% success (12/12 tests passed)** under **strict test set isolation** (zero access to `dataset/processed/Testing/`).

---

## 2. Integrated Model Checkpoint Details

The backend was updated to load the exact CNN V4 checkpoint selected during Milestone 6.6:

```
saved_models/experiments/isl_alphabet_cnn_v4_best.keras
```

| Parameter / Metric | Empirical Value |
|---|---|
| **Checkpoint Path** | `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` |
| **File Size** | 3,806,482 bytes (3.63 MB) |
| **SHA-256 Hash** | `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762` |
| **Model Architecture** | 3 Double-Convolution Blocks (32, 64, 128 filters) + BatchNormalization + MaxPool + GlobalAveragePooling2D + Dense 128 (ReLU) + Dropout (0.40) + Softmax (26) |
| **Kernel Regularization** | L2 Regularization ($\lambda = 0.0001$) on all Conv2D and Dense kernels |
| **Input Tensor Shape** | `(None, 128, 128, 3)` (float32, normalized `[0.0, 1.0]`) |
| **Output Tensor Shape** | `(None, 26)` (Softmax probability distribution over A–Z) |
| **Total Parameters** | 308,218 |
| **Trainable Parameters** | 307,322 |
| **Non-Trainable Parameters** | 896 (BatchNormalization moving statistics) |
| **Independent Test Accuracy** | **86.34%** (evaluated on held-out test set in Milestone 6.6) |
| **Independent Test Macro F1** | **83.96%** (evaluated on held-out test set in Milestone 6.6) |

---

## 3. Preprocessing Consistency Verification

The image preprocessing pipeline in `backend/prediction.py` strictly aligns with the training and evaluation pipeline defined in `training/data_pipeline.py`:

```
Uploaded Image Bytes
       │
       ▼
[PIL Image.open()] ──> In-memory decoding & error validation
       │
       ▼
[.convert('RGB')]  ──> Normalizes 1-channel Grayscale, 4-channel RGBA, or CMYK to 3 channels
       │
       ▼
[.resize((128, 128))] ──> Bilinear interpolation resampling
       │
       ▼
[np.asarray(..., dtype=np.float32)] ──> Convert to 32-bit floating point array
       │
       ▼
[img_array / 255.0] ──> Normalized pixel values bounded strictly in [0.0, 1.0]
       │
       ▼
[np.expand_dims(..., axis=0)] ──> Adds batch dimension -> (1, 128, 128, 3)
       │
       ▼
[model(input_tensor, training=False)] ──> Pure inference pass (BatchNorm uses moving stats, Dropout inactive)
```

### Safety and Orientation Guarantees:
- **No Test Augmentations:** No random horizontal flipping, brightness shifts, or zooming is applied at inference.
- **Orientation Integrity:** Image orientation is preserved as received from camera or file.
- **Format Compatibility:** Supports JPEG, PNG, WebP, BMP, and raw image byte buffers.

---

## 4. API Endpoints & Response Contracts

### 4.1 `GET /health`

Returns service health, model load status, model checkpoint name, and the 26 supported classes:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "isl_alphabet_cnn_v4_best.keras",
  "num_classes": 26,
  "classes": [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
    "U", "V", "W", "X", "Y", "Z"
  ]
}
```

### 4.2 `POST /predict`

Accepts an image file upload (`multipart/form-data`) under parameter name `file`.

**Response Schema (`PredictionResponse`):**
```json
{
  "predicted_letter": "U",
  "predicted_class": "U",
  "confidence": 0.9999,
  "top_predictions": [
    {
      "letter": "U",
      "confidence": 0.9999
    },
    {
      "letter": "V",
      "confidence": 0.0001
    },
    {
      "letter": "W",
      "confidence": 0.0000
    }
  ],
  "inference_time_ms": 53.86,
  "status": "success"
}
```

- **Backwards Compatibility:** Contains `predicted_letter` for existing frontend components and `predicted_class` for standard classification schemas.
- **Latency Monitoring:** Returns `inference_time_ms` for real-time webcam frame rate tracking.

---

## 5. Automated Test Results

### 5.1 Pytest Suite (`backend/tests/test_api.py`)

Run command:
```bash
python -m pytest backend/tests/test_api.py -v
```

**Results: 12 passed in 9.75s**

| Test Case | Description | Result |
|---|---|---|
| `test_model_loading_and_classes` | Confirms model is loaded, 26 classes, input `(None, 128, 128, 3)`, 308,218 params | **PASS** |
| `test_health_endpoint` | Confirms `/health` returns status healthy and model_name containing "v4" | **PASS** |
| `test_root_endpoint` | Confirms `/` metadata and endpoint links | **PASS** |
| `test_predict_valid_synthetic_image` | Confirms `/predict` returns valid letter, confidence $\in [0, 1]$, top-3, latency | **PASS** |
| `test_predict_different_image_dimensions` | Confirms non-square images (300×200) are resized and classified properly | **PASS** |
| `test_predict_grayscale_synthetic_image` | Confirms 1-channel grayscale is automatically converted to 3-channel RGB | **PASS** |
| `test_predict_rgba_synthetic_image` | Confirms 4-channel RGBA transparent images convert to RGB seamlessly | **PASS** |
| `test_predict_empty_file_rejected` | Confirms empty 0-byte file returns HTTP 400 Bad Request | **PASS** |
| `test_predict_corrupt_non_image_rejected` | Confirms corrupt/text bytes return HTTP 400 Bad Request | **PASS** |
| `test_predict_unsupported_content_type` | Confirms unsupported MIME types (PDF) return HTTP 400 Bad Request | **PASS** |
| `test_predict_oversized_file_rejected` | Confirms files > 10 MB return HTTP 413 / 400 | **PASS** |
| `test_test_set_isolation` | Confirms test suite never accesses or references `dataset/processed/Testing/` | **PASS** |

### 5.2 Frontend Regression Test Suite

All 4 frontend test suites (E2E full workflow, speech synthesis, text builder, webcam stability) passed 100% with zero regressions against the updated backend schema.

---

## 6. Strict Test Set Isolation Guarantee

In compliance with academic integrity guidelines:
- The independent test set (`dataset/processed/Testing/`) was strictly **NOT accessed** during backend integration or testing.
- All integration and API tests used synthetic in-memory images generated via `PIL.Image.new()`.
- The evaluation metrics for CNN V4 reported in Section 2 were established once and for all during Milestone 6.6 on held-out test data.

---

## 7. How to Run the Backend Locally

```bash
# 1. Activate the Conda environment
conda activate fortress

# 2. Run the Uvicorn server from the repository root
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **API Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Health Check:** `http://127.0.0.1:8000/health`
- **Inference Endpoint:** `http://127.0.0.1:8000/predict`
