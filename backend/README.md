# ISL Alphabet Recognition — FastAPI Backend Service

This directory contains the production-grade, lightweight FastAPI inference backend for the **AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System**.

The backend serves real-time inference predictions using the **selected final CNN V4 model checkpoint** (`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`), preprocessed identically to the training and evaluation pipeline.

---

## 1. Active Production Model (CNN V4)

| Attribute | Specification |
|---|---|
| **Checkpoint Path** | `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` |
| **Architecture** | 3 Double-Convolution Blocks + BatchNormalization + MaxPool + GAP + Dense 128 + Dropout (0.40) + Softmax (26) |
| **Regularization** | L2 Kernel Regularization ($\lambda = 0.0001$), Dense Dropout 0.40 |
| **Input Shape** | `(128, 128, 3)` RGB, normalized to `[0.0, 1.0]` |
| **Output Classes** | 26 (`A` through `Z`) |
| **Total Parameters** | 308,218 (Trainable: 307,322; Non-trainable: 896) |
| **Independent Test Accuracy** | **86.34%** (+27.30 pp over 59.04% baseline) |
| **Independent Test Macro F1** | **83.96%** (+27.22 pp over 56.74% baseline) |

---

## 2. Directory Structure

```
backend/
├── config.py             # Environment configuration, file paths, image dimensions, CORS
├── main.py               # FastAPI application, CORS middleware, lifespan model loader, endpoints
├── model_loader.py       # Single-instance model caching and label verification
├── prediction.py         # Image decoding, RGB conversion, 128x128 resize, normalization, inference
├── requirements.txt      # Python dependencies (FastAPI, Uvicorn, TensorFlow, Pillow, NumPy)
├── schemas.py            # Pydantic request and response schemas
├── README.md             # This backend documentation guide
└── tests/
    ├── audit_system_integration.py # Standalone backend audit script (isolated synthetic images)
    └── test_api.py       # Pytest regression suite (endpoints, schemas, error cases, isolation)
```

---

## 3. Environment Setup & Installation

### Recommended Environment:
- **Python:** Python 3.11 (tested with Python 3.11.16 on Windows).
- **Virtual Environment:** Conda (`fortress`) or standard `venv`.

### Installation:
```bash
# Activate your Python 3.11 environment (e.g. fortress)
conda activate fortress

# Install required backend dependencies
pip install -r backend/requirements.txt
```

---

## 4. Starting the Server

Run the Uvicorn development server from the repository root:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Interactive OpenAPI Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Documentation (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Diagnostics Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 5. API Endpoints

### 5.1 `GET /health`
Returns the runtime health status, model loading confirmation, active model checkpoint name, and supported class labels.

**Example Request:**
```bash
curl -X GET http://localhost:8000/health
```

**Example Response:**
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

---

### 5.2 `POST /predict`
Accepts a single hand gesture image file via `multipart/form-data` and returns the top predicted ISL alphabet letter, class alias, model softmax probability, top-3 candidate predictions, and inference execution time.

**Example cURL Request:**
```bash
curl -X POST http://localhost:8000/predict \
     -F "file=@sample_hand_gesture.jpg;type=image/jpeg"
```

**Example Python Request:**
```python
import requests

url = "http://localhost:8000/predict"
with open("sample_hand_gesture.jpg", "rb") as f:
    files = {"file": ("gesture.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

print(response.json())
```

**Example Response:**
```json
{
  "predicted_letter": "A",
  "predicted_class": "A",
  "confidence": 0.9412,
  "top_predictions": [
    {
      "letter": "A",
      "confidence": 0.9412
    },
    {
      "letter": "S",
      "confidence": 0.0415
    },
    {
      "letter": "T",
      "confidence": 0.0089
    }
  ],
  "inference_time_ms": 12.45,
  "status": "success"
}
```

---

## 6. Preprocessing Consistency Guarantee

The preprocessing pipeline in `backend/prediction.py` strictly mirrors `training/data_pipeline.py`:
1. **Safe Rasterization:** Pillow decodes raw image bytes safely and normalizes any input mode (RGBA, Grayscale, CMYK) to 3-channel **RGB**.
2. **Dimension Resampling:** Resized to **128 × 128** using bilinear interpolation (`Image.Resampling.BILINEAR`).
3. **Data Type & Range:** Converted to `float32` and divided by `255.0` to span `[0.0, 1.0]`.
4. **Orientation Integrity:** **Zero horizontal flipping or training augmentations** are applied during inference.
5. **Batch Dimension:** Input is formatted as `(1, 128, 128, 3)` before model forward pass.

---

## 7. Running Unit & Integration Tests

Execute the automated test suite with pytest:

```bash
pytest backend/tests/test_api.py -v
```

This verifies:
- Lifespan model loading of CNN V4 (308,218 parameters).
- Health endpoint integrity (`model_name` reporting V4).
- Successful inference on synthetic images across RGB, Grayscale, and RGBA.
- Preprocessing dimension preservation on non-square images (300×200).
- Response schema compliance (`predicted_letter`, `predicted_class`, `confidence`, `top_predictions`, `inference_time_ms`).
- Rejection of empty file uploads (HTTP 400).
- Rejection of corrupted/non-image bytes (HTTP 400).
- Rejection of unsupported MIME types (HTTP 400).
- Rejection of oversized payloads (> 10 MB limit).
- **Strict test set isolation:** Asserts tests never touch `dataset/processed/Testing/`.

---

## 8. Common Errors & Troubleshooting

| Error | Cause | Resolution |
|---|---|---|
| `FileNotFoundError: Trained model checkpoint not found` | The `.keras` file is missing or located in a custom path. | Verify `saved_models/experiments/isl_alphabet_cnn_v4_best.keras` exists or set `MODEL_PATH` environment variable. |
| `HTTP 400 Bad Request: Empty image payload` | The uploaded file contains 0 bytes. | Verify the client is properly attaching file content before sending. |
| `HTTP 400 Bad Request: Failed to decode image file` | The uploaded file is corrupted or not a valid image format (e.g. text file). | Ensure the uploaded file is a readable JPEG, PNG, or WebP image. |
| `HTTP 413 / 400: File exceeds maximum upload limit` | Image payload exceeds 10 MB. | Compress the image before uploading; typical gesture frames are < 2 MB. |
| `CORS Error in Browser` | Frontend running on an origin not listed in CORS origins. | Add the frontend origin (e.g. `http://localhost:5173`) to `CORS_ORIGINS` in `backend/config.py`. |
