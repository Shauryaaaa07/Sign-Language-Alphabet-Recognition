# Backend Foundation & Model Integration Report (Milestone 4.1)

## 1. Executive Summary

Milestone 4.1 establishes the production-grade, modular FastAPI backend service for the Indian Sign Language (ISL) Alphabet Recognition project. The backend successfully integrates the trained baseline CNN checkpoint (`saved_models/isl_alphabet_cnn_best.keras`), verified A–Z class mapping (`training/label_classes.json`), and serves low-latency inference over HTTP with robust input validation and CORS configuration.

---

## 2. Backend Files Created

| File | Purpose | Implementation Details |
|---|---|---|
| [`backend/config.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/config.py) | Centralized Configuration | Stores paths for model checkpoint, label mapping, target dimensions (128x128x3), upload size limits (10 MB), and CORS origins (`http://localhost:5173`). |
| [`backend/schemas.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/schemas.py) | Pydantic Schemas | Strict typing for `HealthResponse`, `PredictionResponse`, `TopPrediction`, and `ErrorResponse`. |
| [`backend/model_loader.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/model_loader.py) | Single-Instance Model Manager | Loads `.keras` model once during application startup, caches model and class mappings in memory, verifies 26 output units, and prevents per-request reloading. |
| [`backend/prediction.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/prediction.py) | Image Preprocessing & Inference | Decodes bytes safely using Pillow, converts to RGB, resizes to 128×128 (bilinear), normalizes to $[0, 1]$, extracts top-1 and top-3 predictions with confidence scores. |
| [`backend/main.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/main.py) | FastAPI Application | Configures lifespan startup events, CORS middleware, `GET /health`, `POST /predict`, and error handling for bad requests and payload limits. |
| [`backend/requirements.txt`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/requirements.txt) | Dependencies Specification | Declares FastAPI, Uvicorn, Python-Multipart, TensorFlow, Pillow, NumPy, and Pydantic. |
| [`backend/README.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/README.md) | Backend Documentation Guide | Setup instructions, startup commands, endpoint documentation, request/response examples, and troubleshooting matrix. |
| [`backend/tests/test_api.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/tests/test_api.py) | Automated Pytest Suite | 8 comprehensive tests verifying startup, endpoints, synthetic inference, empty uploads, corrupted files, and MIME validation. |

---

## 3. Model Loading & Verification

- **Checkpoint Path:** `saved_models/isl_alphabet_cnn_best.keras` (1.34 MB)
- **Label Mapping Source:** `training/label_classes.json`
- **Output Classes Verified:** Exactly 26 classes (`A` through `Z`), indices `0` through `25`.
- **Startup Protocol:** Model is loaded once into global memory inside FastAPI's `lifespan` context manager. Requests access the pre-warmed model instance directly without disk I/O.
- **Model Immutability:** Model weights remain strictly frozen; inference runs in evaluation mode (`training=False`).

---

## 4. Preprocessing Alignment with Training Pipeline

To ensure model accuracy during real-world inference, `backend/prediction.py` strictly replicates the preprocessing pipeline established in `training/data_pipeline.py`:

| Dimension / Step | Training Pipeline (`data_pipeline.py`) | Backend Inference (`prediction.py`) | Alignment Status |
|---|---|---|:---:|
| **Color Mode** | RGB (3 channels) | Pillow `.convert("RGB")` | **Identical** |
| **Spatial Dimensions** | 128 × 128 | 128 × 128 | **Identical** |
| **Resampling Filter** | Bilinear interpolation | `Image.Resampling.BILINEAR` | **Identical** |
| **Pixel Normalization** | Divided by 255.0 to $[0.0, 1.0]$ | Divided by 255.0 to $[0.0, 1.0]$ | **Identical** |
| **Data Type** | `tf.float32` | `np.float32` | **Identical** |
| **Orientation Safety** | **No horizontal flipping** | **No horizontal flipping** | **Identical** |
| **Augmentation Mode** | Active only during training | Completely disabled | **Identical** |

---

## 5. API Endpoints & Verification Results

### 5.1 `GET /health`
- **HTTP Status:** 200 OK
- **Sample Response:**
  ```json
  {
    "status": "healthy",
    "model_loaded": true,
    "num_classes": 26,
    "classes": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
  }
  ```

### 5.2 `POST /predict`
- **Input:** Multipart form upload (`file=@image.jpg;type=image/jpeg`)
- **HTTP Status:** 200 OK
- **Sample Response:**
  ```json
  {
    "predicted_letter": "A",
    "confidence": 0.8924,
    "top_predictions": [
      { "letter": "A", "confidence": 0.8924 },
      { "letter": "S", "confidence": 0.0612 },
      { "letter": "T", "confidence": 0.0215 }
    ],
    "status": "success"
  }
  ```

### 5.3 Error Handling Gates
- **Empty file upload:** Returns HTTP 400 Bad Request with detail `"Uploaded file payload is empty (0 bytes)."`.
- **Corrupted / Non-image bytes:** Returns HTTP 400 Bad Request with detail `"Failed to decode image file. Ensure it is a valid JPEG/PNG image."`.
- **Unsupported MIME type (e.g. PDF):** Returns HTTP 400 Bad Request with detail `"Unsupported file format 'application/pdf'."`.
- **Oversized files (>10 MB):** Returns HTTP 413 Payload Too Large.

---

## 6. Automated Pytest Results

The test suite in [`backend/tests/test_api.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/tests/test_api.py) executed cleanly in the `fortress` Python environment:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.2.0, pluggy-1.7.0
plugins: anyio-4.15.1
collected 8 items

backend/tests/test_api.py::test_model_loading_and_classes PASSED         [ 12%]
backend/tests/test_api.py::test_health_endpoint PASSED                   [ 25%]
backend/tests/test_api.py::test_root_endpoint PASSED                     [ 37%]
backend/tests/test_api.py::test_predict_valid_synthetic_image PASSED     [ 50%]
backend/tests/test_api.py::test_predict_different_image_dimensions PASSED [ 62%]
backend/tests/test_api.py::test_predict_empty_file_rejected PASSED       [ 75%]
backend/tests/test_api.py::test_predict_corrupt_non_image_rejected PASSED [ 87%]
backend/tests/test_api.py::test_predict_unsupported_content_type PASSED  [100%]

======================== 8 passed, 1 warning in 10.66s ========================
```

---

## 7. How to Start the Backend Server

Run the development server from the repository root:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 8. Academic Scope & Limitations

1. **Confidence Metric Interpretation:** The `confidence` score output by `/predict` represents the model's raw Softmax probability distribution. As is standard in neural networks, Softmax outputs reflect relative class logits rather than mathematically calibrated real-world Bayesian certainty.
2. **Single-Frame Hand Snapshots:** The endpoint classifies static image frames. Temporal sequences for movement-dependent gestures (ISL J & Z) are evaluated on static keyframe configurations as documented in Milestone 3.2.
