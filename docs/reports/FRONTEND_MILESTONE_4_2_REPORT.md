# Frontend Foundation & Image Upload Integration Report (Milestone 4.2)

## 1. Executive Summary

Milestone 4.2 establishes the user-facing web application for the **AI-Based Indian Sign Language (ISL) Alphabet Recognition System**. Built using React 19, Vite 8, and Tailwind CSS v4, the application provides an accessible, responsive interface allowing users to upload or drag-and-drop hand gesture images, communicate with the FastAPI backend service (`/predict`), and receive real-time classification results with top-3 candidate predictions and confidence distributions.

---

## 2. Frontend Components & Architecture

The frontend is structured into modular, beginner-friendly components located under `frontend/src/`:

```
frontend/src/
├── components/
│   ├── Header.jsx             # Branding, project title, and real-time backend connection status badge
│   ├── ImageUploader.jsx      # Drag-and-drop zone, file picker, client-side validation, instant image preview, predict button
│   ├── PredictionResult.jsx   # Prominent predicted letter card, confidence bar, top-3 candidates, confidence disclaimer
│   └── StatusIndicator.jsx    # Real-time backend connectivity badge with manual refresh control
├── services/
│   └── api.js                 # Centralized API service with timeout handling and multipart/form-data payload construction
├── App.jsx                    # Root container coordinating connection polling, upload states, and error handling
├── main.jsx                   # React root mount entry point
└── index.css                  # Global Tailwind CSS imports and baseline typography
```

---

## 3. UI States & Client-Side Validation

The application handles six distinct lifecycle states with visual feedback:

| UI State | Visual Representation | User Actions Available |
|---|---|---|
| **1. No Image Selected** | Dashed dropzone with upload prompt; prediction panel shows waiting placeholder. | Drag-and-drop or click to browse files. |
| **2. Image Selected** | High-contrast preview container displaying image, filename, and formatted size (KB/MB). | "Recognize Sign Alphabet", "Change Image", or "Remove Image". |
| **3. Prediction in Progress** | Spinner animation on button ("Classifying Gesture..."), prediction panel displays pulsing inference state. | Repeated clicks blocked; inputs temporarily disabled. |
| **4. Prediction Successful** | Large bold predicted letter card (e.g. `A`), percentage confidence, animated progress bar, top-3 candidates list. | Upload new image or re-classify. |
| **5. Prediction Failed** | Warning card displaying specific error details returned by client validation or backend HTTP response. | Select a clearer gesture image and retry. |
| **6. Backend Unavailable** | Red status pill ("Backend Offline"); predict button disabled with informative helper text. | Click refresh icon to re-probe `GET /health`. |

### Client-Side Validation Gates:
- **Format Filtering:** Restricts input to `JPEG`, `JPG`, `PNG`, `WebP`, and `BMP`.
- **Empty File Guard:** Rejects 0-byte files before sending over the network.
- **Payload Size Ceiling:** Enforces the backend's 10 MB limit (`10 * 1024 * 1024` bytes).

---

## 4. API Integration Details

All backend communication is centralized in [`frontend/src/services/api.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/services/api.js):
- **Base URL Configuration:** Configurable via Vite environment variable `import.meta.env.VITE_API_URL` (defaults to `http://localhost:8000`).
- **Health Check (`checkBackendHealth`):** Queries `GET /health` with a 4-second `AbortController` timeout on component mount and on a 15-second background polling cycle.
- **Gesture Classification (`predictSignGesture`):** Constructs a `FormData` object with exact field key `file`, allowing the browser to automatically set the `multipart/form-data` boundary without manual header tampering.

---

## 5. Verification & Test Execution Results

### 5.1 Automated Linter Verification (Oxlint)
```text
> frontend@0.0.0 lint
> oxlint

Found 0 warnings and 0 errors.
Finished in 21ms on 8 files with 104 rules using 11 threads.
```

### 5.2 Production Build Verification (Vite)
```text
> frontend@0.0.0 build
> vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 21 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-Cjmn2qkb.css   26.54 kB │ gzip:  5.76 kB
dist/assets/index-lkfKI3eM.js   238.21 kB │ gzip: 74.27 kB

✓ built in 300ms
```

### 5.3 Live Backend Integration Smoke Test
An automated integration test was executed against the active FastAPI backend:
- `GET http://127.0.0.1:8000/health`: HTTP 200 OK (`model_loaded: true`, 26 classes).
- `POST http://127.0.0.1:8000/predict` (Valid Image): HTTP 200 OK (returned predicted letter, confidence score, and top-3 candidates).
- `POST http://127.0.0.1:8000/predict` (Empty Payload): HTTP 400 Bad Request (`Uploaded file payload is empty (0 bytes).`).
- `POST http://127.0.0.1:8000/predict` (Corrupt Non-Image): HTTP 400 Bad Request (`Failed to decode image file.`).
- **Result:** **All 4 integration test gates PASSED.**

---

## 6. How to Run the Full Application Locally

1. **Start the FastAPI Backend:**
   ```bash
   conda activate fortress
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Start the React Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
3. Open your browser at [http://localhost:5173](http://localhost:5173).

---

## 7. Academic Scope & Limitations

1. **Static Gesture Focus:** In accordance with Milestone 4.2 scope, this version classifies static image uploads. Live webcam stream capture and browser SpeechSynthesis voice conversion are scheduled for Phase 4.3 and Phase 5.
2. **Confidence Metric Interpretation:** As noted in the UI disclaimer, model confidence represents the raw Softmax output probability and is not an absolute mathematical guarantee of real-world sign accuracy.
