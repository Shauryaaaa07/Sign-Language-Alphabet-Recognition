# Milestone 4.3 Report: Live Webcam Sign Recognition Integration

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 4 — Full-Stack Application Integration  
**Milestone:** 4.3 — Live Webcam Sign Recognition  
**Date:** November 1, 2026  
**Status:** COMPLETE (Ready for User Review)

---

## 1. Executive Summary

Milestone 4.3 introduces real-time, browser-native live webcam Indian Sign Language (ISL) alphabet recognition into the existing React + Vite + Tailwind CSS frontend, directly integrated with the Phase 4.1 FastAPI backend.

Key accomplishments in this milestone include:
1. **Live Camera Stream (`WebcamRecognition.jsx`):** Developed a responsive, user-friendly live camera component using `navigator.mediaDevices.getUserMedia()` configured strictly for video (audio explicitly disabled).
2. **Aspect-Ratio Preserving Frame Capture:** Built a canvas-based video capture pipeline sampling at ~500ms intervals with automatic center-square cropping to 256×256 pixels, preventing aspect ratio distortion when fed into the 128×128 ISL CNN model.
3. **In-Flight Concurrency Guard:** Implemented a non-blocking mutex lock (`isProcessingRef`) preventing subsequent capture ticks while preceding network inferences are in transit.
4. **Consecutive Confidence Stability Engine:** Enforced a robust 3-frame stability threshold requiring consecutive identical classifications with $\ge 75\%$ confidence before updating the locked "Stable Prediction" display.
5. **Seamless Mode Switching (`App.jsx`):** Added intuitive tab controls allowing instantaneous toggling between "Upload Image" and "Live Webcam" modes, with full hardware resource teardown on unmount or tab switch.
6. **Rigorous Verification:** Zero linter warnings (`oxlint`), successful production build (`vite build`), and 100% pass on automated stability and concurrency unit tests.

---

## 2. Architecture & Component Design

### 2.1 Component Hierarchy
```
frontend/src/
├── App.jsx                       # Top-level view router & mode toggle (Upload vs. Webcam)
├── components/
│   ├── Header.jsx               # Navigation bar & backend connectivity polling
│   ├── ImageUploader.jsx        # Milestone 4.2 drag-and-drop file upload
│   ├── PredictionResult.jsx     # Milestone 4.2 single-image inference card
│   ├── StatusIndicator.jsx      # Backend health badge with live ping
│   └── WebcamRecognition.jsx    # NEW: Milestone 4.3 live stream recognition core
├── services/
│   └── api.js                   # Handles Multipart FormData for both Files and Blobs
└── tests/
    └── webcam_stability.test.mjs # Automated unit tests for stability & locking
```

### 2.2 Mode Switching Lifecycle
In [`frontend/src/App.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/App.jsx), switching between `"upload"` and `"webcam"` conditionally mounts/unmounts `<WebcamRecognition>`:
- When navigating away from `"webcam"`, React triggers the component unmount cleanup callback.
- All hardware camera tracks are immediately stopped via `track.stop()`.
- Recurring interval timers are cleared via `clearInterval()`.
- Hardware camera indicator lights turn off immediately, preventing background battery and memory drain.

---

## 3. Real-Time Video & Inference Pipeline

### 3.1 Media Stream Acquisition
`WebcamRecognition.jsx` queries the browser media subsystem:
```javascript
const stream = await navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 640 },
    height: { ideal: 480 },
    facingMode: 'user',
  },
  audio: false, // Strictly NO audio requested
});
```
- **Audio Privacy:** Microphone access is explicitly turned off (`audio: false`), preventing unnecessary permissions or audio eavesdropping.
- **Error Diagnostics:** Handled specific exceptions:
  - `NotAllowedError` / `PermissionDeniedError`: User or OS denied camera access.
  - `NotFoundError` / `DevicesNotFoundError`: No video input device connected.
  - `NotReadableError` / `TrackStartError`: Camera locked by another program (e.g. Teams, Zoom).

### 3.2 Aspect-Ratio Preserving Center Crop
The underlying ISL baseline CNN was trained on square (1:1) bounding boxes. Standard webcam sensors produce 4:3 or 16:9 widescreen frames. Directly compressing widescreen frames to a square distorts hand geometry.
`WebcamRecognition.jsx` calculates and crops the center square before transmission:
```javascript
const videoW = video.videoWidth || 640;
const videoH = video.videoHeight || 480;
const minDim = Math.min(videoW, videoH);
const startX = (videoW - minDim) / 2;
const startY = (videoH - minDim) / 2;

ctx.drawImage(video, startX, startY, minDim, minDim, 0, 0, 256, 256);
```
An on-screen visual reticle overlays the live video feed, guiding the user to position their signing hand within this square region.

### 3.3 Concurrency Guard (In-Flight Request Locking)
To avoid piling up network requests if inference latency exceeds the 500ms sampling interval:
- An `isProcessingRef` lock is set immediately before frame capture begins.
- Subsequent timer ticks check `if (isProcessingRef.current) return;` and safely discard the tick without queueing.
- The lock is released in a `finally` block once the HTTP response returns or fails.

---

## 4. Prediction Stability Engine

### 4.1 Stability State Machine
Due to transient frame jitter, shadows, and motion blur during live movement, raw single-frame neural network predictions can fluctuate rapidly. To deliver a smooth, reliable user experience, we implemented a deterministic 3-frame consecutive confidence state machine:

$$\text{Stability Condition: } \text{Count} \ge 3 \quad \text{where} \quad \text{Confidence} \ge 0.75 \quad \text{for identical letter } L$$

| Event | Condition | Action |
| :--- | :--- | :--- |
| **High Confidence Frame** | `conf >= 0.75` and `letter == candidate` | Increment `consecutiveCount += 1`. If `count >= 3`, lock `stablePrediction = letter`. |
| **New Candidate Frame** | `conf >= 0.75` and `letter != candidate` | Set `candidate = letter`, reset `consecutiveCount = 1`. |
| **Low Confidence Frame** | `conf < 0.75` | Reset `candidate = null`, `consecutiveCount = 0`. |
| **Network / Inference Error** | Request rejected or aborted | Reset `candidate = null`, `consecutiveCount = 0`. |
| **Camera Stopped / Unmounted** | User stops camera or switches tabs | Reset all state: `candidate = null`, `count = 0`, `stable = null`, `raw = null`. |

### 4.2 Dual Display Model
1. **Live Raw Prediction:** Displays the instantaneous classification, real-time confidence bar, and top-3 candidate distribution directly from the most recent frame.
2. **Stable Prediction:** Prominently highlights the verified gesture in a large, emerald-bordered badge with a 3-step progress bar showing candidate stability.

---

## 5. Verification & Testing

### 5.1 Static Code Quality & Linter
```bash
> cd frontend && npm run lint
oxlint
Found 0 warnings and 0 errors.
Finished in 26ms on 10 files with 104 rules using 11 threads.
```

### 5.2 Production Packaging Build
```bash
> cd frontend && npm run build
vite v8.3.5 building client environment for production...
✓ 22 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-DNcKI6uk.css   33.37 kB │ gzip:  6.68 kB
dist/assets/index-cGt5xsyH.js   253.84 kB │ gzip: 77.32 kB
✓ built in 275ms
```

### 5.3 Automated Unit Tests (`frontend/src/tests/webcam_stability.test.mjs`)
An automated test suite was constructed and executed to verify state machine transitions and hardware cleanup:
- **Test 1 (State Machine Transitions):** Tested 10 sequential events covering sub-threshold confidence, letter transitions, 3-frame stabilization, high-confidence extensions, drop below threshold, error reset, and full teardown. **Result: PASSED.**
- **Test 2 (Hardware Cleanup):** Simulated media stream teardown verifying all tracks (`track.stop()`) and intervals are cleared. **Result: PASSED.**
- **Test 3 (Concurrency Guard):** Dispatched 10 rapid interval triggers (every 20ms) while a simulated network call took 80ms. Maximum concurrent requests never exceeded 1, and 6 overlapping frames were safely dropped without memory leakage. **Result: PASSED.**

### 5.4 Physical Hardware Camera Testing Boundary (Honesty Statement)
- **Automated Verification:** Fully verified through mock media streams, synthetic canvas blobs, linter, production packaging, and state machine unit tests.
- **Physical Hardware Execution:** Automated environments and container/headless test runners do not possess physical camera hardware or permission grants to open real laptop webcams. Physical webcam validation must be performed by an end user in an interactive browser session (Chrome/Firefox/Edge) at `http://localhost:5173`. Clear camera permission guidance and fallback error messaging have been tested and verified.

---

## 6. Academic Limitations & Real-World Considerations

1. **Baseline CNN Test Accuracy (59.04%):**
   The underlying baseline 2D CNN (evaluated in Phase 3.4) achieved an overall test accuracy of 59.04% on curated, static cropped images. Performance on live uncropped webcam streams is inherently subject to ambient lighting, shadow variations, skin tone diversity, and background clutter.
2. **Static Representation for J and Z:**
   Traditional Indian Sign Language for letters **J** and **Z** incorporates dynamic motion (drawing the letter path in space). Single-frame 2D CNNs cannot capture temporal trajectories; they recognize standard static keyframe postures (e.g., crossed fingers for J, perpendicular palm for Z).
3. **User Guidance Reticle:**
   Because the dataset consists of tightly framed hand signs, users achieve the highest accuracy when placing their signing hand firmly within the blue reticle box against a neutral background.

---

## 7. Deliverables & File Changes

| File | Status | Description |
| :--- | :--- | :--- |
| [`frontend/src/components/WebcamRecognition.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/components/WebcamRecognition.jsx) | **Created** | Live camera preview, 500ms canvas capture, center cropping, request locking, stability logic, and dual prediction display. |
| [`frontend/src/App.jsx`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/App.jsx) | **Updated** | Added tab bar for mode switching between "Upload Image" and "Live Webcam" with immediate teardown on switch. |
| [`frontend/src/services/api.js`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/services/api.js) | **Updated** | Added fallback filename support for raw `Blob` payloads in `predictSignGesture`. |
| [`frontend/src/tests/webcam_stability.test.mjs`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/src/tests/webcam_stability.test.mjs) | **Created** | Automated unit tests for stability state machine, cleanup, and concurrency locks. |
| [`docs/reports/WEBCAM_MILESTONE_4_3_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/WEBCAM_MILESTONE_4_3_REPORT.md) | **Created** | Full milestone documentation report. |
