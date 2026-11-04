# Milestone 5.2 Report: Manual Browser & Hardware Verification Protocol

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 5 — Comprehensive Integration, Verification & Audit  
**Milestone:** 5.2 — Manual Browser & Hardware Verification  
**Date:** November 1, 2026  
**Status:** COMPLETE (Checklist Ready for Human Hardware Testing)

---

## 1. Executive Summary

Milestone 5.2 bridges the gap between automated software integration and physical real-world evaluation. While 100% of programmatic tests have succeeded (including backend endpoints, model inference, frontend linting, production builds, state machine simulations, and lifecycle guards), automated testing environments cannot physically interface with real optical camera sensors or audible sound card DACs.

This milestone establishes the formalized, human-executable manual verification protocol:
1. **Startup Procedures Verified:** Verified the exact environment commands required to spin up the FastAPI Uvicorn backend service and React/Vite development server concurrently.
2. **Comprehensive Manual Checklist Created ([`MANUAL_HARDWARE_TESTING_CHECKLIST.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md)):** Formulated 26 structured manual test cases covering Application Startup, Image Upload, Physical Webcam, Actual Speech Output, and Complete End-to-End User Flow.
3. **Academic Integrity & Status Transparency:** All physical manual test cases are formally cataloged as `NOT TESTED (Pending Human Hardware Verification)` to ensure empirical transparency until validated on a physical machine with camera and speakers enabled.
4. **Practical Hardware Troubleshooting:** Authored practical troubleshooting workflows for OS camera permission denials, camera locks (`NotReadableError`), missing hardware, offline backend servers, and muted sound channels.
5. **README Update:** Updated root documentation with verified multi-terminal execution instructions.

---

## 2. Verified Server Startup Procedures

The startup commands were empirically checked against project configuration files ([`backend/main.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/main.py), [`backend/config.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/backend/config.py), and [`frontend/package.json`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/frontend/package.json)):

### Terminal 1: FastAPI Inference Backend
```bash
# Activate Python 3.11 environment (e.g. fortress)
conda activate fortress

# Run Uvicorn server from repository root
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Service Root:** `http://127.0.0.1:8000/`
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`
- **Health Diagnostics:** `http://127.0.0.1:8000/health`

### Terminal 2: React 19 + Vite 8 Frontend
```bash
cd frontend
npm run dev
```
- **Local Application Port:** `http://localhost:5173/`

---

## 3. Manual Testing Checklist Overview

The manual test protocol ([`docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md)) groups verification into 5 core operational domains:

### Section A: Application Startup & Connectivity
- **TC-START-01:** Backend Uvicorn startup and lifespan model loading.
- **TC-START-02:** Frontend Vite server startup and bundle serving.
- **TC-START-03:** Top-right `StatusIndicator` health badge polling (green `Backend Connected`).
- **TC-START-04:** Browser DevTools inspection for clean console without runtime errors.

### Section B: Image Upload Recognition
- **TC-UPLOAD-01:** File selection via drag-and-drop or browsing with real JPEG/PNG test images.
- **TC-UPLOAD-02:** Inference classification output (predicted letter, confidence %, Top-3 candidates).
- **TC-UPLOAD-03:** Quick-add action sending recognized letter to Text Builder.
- **TC-UPLOAD-04:** Rejection and user-friendly error banners for corrupt/non-image bytes.
- **TC-UPLOAD-05:** Rejection of oversized files exceeding 10 MB.

### Section C: Physical Webcam Recognition
- **TC-CAM-01:** Browser permission dialog prompt (`navigator.mediaDevices.getUserMedia`).
- **TC-CAM-02:** Viewport live video streaming with blue reticle overlay and 500ms indicator.
- **TC-CAM-03:** Hand posture recognition with real-time in-flight request locking.
- **TC-CAM-04:** Stability engine locking in after 3 consecutive frames with confidence $\ge 0.75$.
- **TC-CAM-05:** Runaway insertion guard (holding static hand pose does not auto-flood text).
- **TC-CAM-06:** Manual explicit letter insertion via "Add Letter" button.
- **TC-CAM-07:** Hardware teardown on "Stop Camera" (hardware webcam LED indicator turns off).
- **TC-CAM-08:** Teardown on tab switch (switching to Image Upload immediately halts camera).

### Section D: Actual Speech Output (Voice Conversion)
- **TC-SPEECH-01:** Audible spoken English speech through physical speakers or headphones.
- **TC-SPEECH-02:** State progression from `Speaking...` to `Speech Finished`.
- **TC-SPEECH-03:** Mid-playback cancellation via "Stop" button without error alerts.
- **TC-SPEECH-04:** Voice dropdown selection among available OS English voices.
- **TC-SPEECH-05:** Inaction and button disabling on empty/whitespace text.

### Section E: Complete End-to-End User Workflow
- **TC-FLOW-01 to TC-FLOW-08:** Step-by-step assembly of complete multi-word sentences (`"HI ALL"`), testing space insertion, duplicate space blocking, backspace deletion, clipboard copying, voice conversion playback, and inline clear confirmation.

---

## 4. Pending Physical Hardware Tests (Honesty Notice)

The following tests require human hardware evaluation in a browser session:

| Test ID | Domain | Requirement Requiring Physical Hardware |
| :--- | :--- | :--- |
| **TC-CAM-01 to TC-CAM-08** | Physical Camera | Real optical sensor, human hand signing poses under ambient room lighting, hardware camera LED confirmation. |
| **TC-SPEECH-01 to TC-SPEECH-04** | Physical Audio | Real audio sound card DAC, physical speakers/headphones, natural voice intelligibility evaluation. |

---

## 5. Known Limitations & Recommendations

1. **Ambient Lighting Sensitivity:**
   The underlying baseline 2D CNN (59.04% test accuracy) was trained on pre-cropped images. Live webcam recognition is sensitive to background shadows, skin tone variation, and hand distance. Signers should hold hand gestures squarely within the reticle box under direct, even lighting against a plain background.
2. **Dynamic Signs (J and Z):**
   Standard ISL involves motion for letters J and Z. In this single-frame 2D CNN system, signers should use the established static keyframe poses (crossed fingers for J, perpendicular palm for Z).
3. **OS-Dependent Speech Voices:**
   Browser speech synthesis quality depends on the host operating system's installed speech synthesis voices (e.g. Microsoft David/Zira on Windows, Siri voices on macOS).

---

## 6. Changed & Created Files

| File | Status | Description |
| :--- | :--- | :--- |
| [`docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md) | **Created** | Comprehensive manual testing protocol, 26-item checklist table, and troubleshooting guide. |
| [`README.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/README.md) | **Updated** | Added multi-terminal local execution instructions and reference link to checklist. |
| [`docs/reports/MANUAL_HARDWARE_VERIFICATION_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/MANUAL_HARDWARE_VERIFICATION_REPORT.md) | **Created** | Milestone 5.2 report documenting procedures, pending tests, and limitations. |

---

## 7. Git Status

```bash
On branch main
Changes not staged for commit:
	modified:   README.md
	modified:   frontend/src/App.jsx

Untracked files:
	backend/README.md
	backend/config.py
	backend/main.py
	backend/model_loader.py
	backend/prediction.py
	backend/schemas.py
	backend/tests/
	docs/reports/AUGMENTATION_SAMPLE_REVIEW.png
	docs/reports/BACKEND_MILESTONE_4_1_REPORT.md
	docs/reports/BASELINE_TRAINING_REPORT.md
	docs/reports/CLEANED_DATASET_VERIFICATION.md
	docs/reports/CLEANING_SIMULATION_REPORT.md
	docs/reports/CNN_MODEL_ARCHITECTURE.md
	docs/reports/DATASET_AUDIT_REPORT.md
	docs/reports/DATASET_CLEANING_PLAN.md
	docs/reports/EXCLUDED_FILES_MANIFEST.json
	docs/reports/FINAL_MODEL_EVALUATION_REPORT.md
	docs/reports/FRONTEND_MILESTONE_4_2_REPORT.md
	docs/reports/MANUAL_HARDWARE_TESTING_CHECKLIST.md
	docs/reports/MANUAL_HARDWARE_VERIFICATION_REPORT.md
	docs/reports/PHASE_5_INTEGRATION_AUDIT_REPORT.md
	docs/reports/TEXT_BUILDER_MILESTONE_4_4_REPORT.md
	docs/reports/TEXT_TO_SPEECH_MILESTONE_4_5_REPORT.md
	docs/reports/WEBCAM_MILESTONE_4_3_REPORT.md
	frontend/src/components/
	frontend/src/hooks/
	frontend/src/services/
	frontend/src/tests/
	frontend/src/utils/
	results/classification_report.csv
	results/confusion_matrix.png
	results/per_class_metrics.png
	results/test_predictions.csv
	results/training_accuracy.png
	results/training_history.csv
	results/training_loss.png
	training/build_clean_dataset.py
	training/data_pipeline.py
	training/evaluate_model.py
	training/inspect_dataset.py
	training/label_classes.json
	training/model.py
	training/simulate_dataset_cleaning.py
	training/train_model.py
```
*(No commits or git pushes executed in compliance with project instructions).*
