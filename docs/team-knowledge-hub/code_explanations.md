# Code Explanations: Architecture & Pipeline Walkthrough

This guide provides clear explanations of the core project components so team members can explain them during project reviews.

---

## 1. Project Architecture Walkthrough
The system is divided into three distinct layers:
1. **Frontend (`frontend/`):** React 19 + Vite + Tailwind CSS. Runs client-side in the browser, accesses the user's camera securely, and synthesizes English voice output.
2. **Backend (`backend/`):** FastAPI asynchronous web framework. Exposes REST endpoints (`/predict`, `/predict-frame`, `/metrics`) and handles image preprocessing via OpenCV.
3. **ML Engine (`training/` & `saved_models/`):** TensorFlow/Keras CNN pipeline. Separated into distinct inspection, preprocessing, training, and evaluation scripts.

---

## 2. Key Directories & Their Responsibilities

### `docs/project-documents/`
Contains the immutable reference documents:
- `ISL_Alphabet_Recognition_PDR.pdf` (Project Design Report)
- `ISL_Alphabet_Recognition_TDR.pdf` (Technical Design Report)
- `DESIGN_CHANGES_LOG.md` (Tracks any verified parameter changes)

### `dataset/` (Local Only)
Contains `raw/` and `custom/` image folders. Excluded from Git to maintain a lightweight repository and respect data privacy.

### `saved_models/`
Stores the trained `.keras` weights and `label_classes.json` mapping. Loaded into memory as a singleton by FastAPI to ensure low inference latency without reloading weights per request.

### `results/`
Stores genuine evaluation artifacts generated on held-out test data (`confusion_matrix.png`, `accuracy_loss_curves.png`, `evaluation_metrics.json`). No fake or hardcoded metrics are permitted.
