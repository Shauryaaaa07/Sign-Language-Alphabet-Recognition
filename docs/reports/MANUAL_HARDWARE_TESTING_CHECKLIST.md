# Manual Browser & Hardware Verification Checklist

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 5 — Milestone 5.2  
**Document Type:** Manual Execution & Hardware Validation Protocol  
**Date:** November 1, 2026  
**Auditor / Tester:** ____________________  
**Testing Environment:** OS: Windows / macOS / Linux &bull; Browser: Chrome / Edge / Firefox &bull; Camera: Integrated / USB &bull; Audio: Speakers / Headphones  

---

## 1. Overview & Verification Objective

While all 34 automated unit and integration tests (Pytest, Oxlint, Vite build, and 4 Node.js test suites) have passed with 100% success, physical optical cameras and physical audio transducers (speakers/headphones) require direct human interaction in a live web browser.

This document serves as the standardized protocol for manual hardware verification.

> [!IMPORTANT]
> In adherence with academic and testing integrity standards, all physical manual tests are initially logged with status **`NOT TESTED`**. Testers must record actual physical observations, timestamps, and hardware details during live execution.

---

## 2. Server Startup Procedures

Execute these commands in two separate terminal windows from the repository root:

### Terminal 1: FastAPI Backend
```bash
# Ensure Python 3.11 environment is active (e.g. fortress)
conda activate fortress

# Start Uvicorn ASGI server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Expected Terminal Output:**
  ```
  INFO: Started server process
  INFO: Waiting for application startup.
  [INFO] Initializing ISL Alphabet Recognition Backend...
  [BACKEND INIT] Loading trained CNN model from: saved_models/isl_alphabet_cnn_best.keras
  [BACKEND INIT] Model loaded successfully. Input shape: (None, 128, 128, 3), Output shape: (None, 26)
  [INFO] Model and label classes initialized successfully.
  INFO: Application startup complete.
  INFO: Uvicorn running on http://127.0.0.1:8000
  ```

### Terminal 2: React + Vite Frontend
```bash
cd frontend
npm run dev
```
- **Expected Terminal Output:**
  ```
  VITE v8.3.5 ready in 150 ms
  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
  ```

---

## 3. Manual Testing Checklist & Results Table

### Section A: Application Startup & Connectivity

| Test ID | Test Description | Action / Procedure | Expected Result | Actual Result | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-START-01** | Backend Startup | Run `uvicorn backend.main:app --port 8000` | Process binds to port 8000, model loads, 26 classes discovered. | | `NOT TESTED` | |
| **TC-START-02** | Frontend Startup | Run `npm run dev` in `frontend/` | Vite serves application on `http://localhost:5173/`. | | `NOT TESTED` | |
| **TC-START-03** | Health Indicator | Navigate to `http://localhost:5173/` in browser | Top-right status badge displays green pill: `Backend Connected`. | | `NOT TESTED` | |
| **TC-START-04** | Console Cleanliness | Open Browser DevTools (`F12` $\rightarrow$ Console) | No uncaught JavaScript exceptions, 404 network errors, or CORS warnings. | | `NOT TESTED` | |

---

### Section B: Image Upload Recognition

| Test ID | Test Description | Action / Procedure | Expected Result | Actual Result | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-UPLOAD-01** | Valid A–Z Sample | Upload sample image (e.g. `dataset/processed/Testing/A/175.jpg`) | Displays image preview, "Recognize Sign Gesture" button activates. | | `NOT TESTED` | |
| **TC-UPLOAD-02** | Prediction Output | Click "Recognize Sign Gesture" | Shows predicted letter (e.g. 'A'), confidence %, and Top-3 candidate distribution. | | `NOT TESTED` | |
| **TC-UPLOAD-03** | Quick-Add to Builder | Click "Add '[Letter]' to Sentence" on prediction card | Letter appends to Text Builder assembly area below. | | `NOT TESTED` | |
| **TC-UPLOAD-04** | Corrupt File Handling | Upload a non-image file renamed to `.jpg` (e.g. text file) | Displays clean error: "Failed to decode image file. Ensure it is a valid JPEG/PNG". | | `NOT TESTED` | |
| **TC-UPLOAD-05** | Oversized File Guard | Attempt uploading an image exceeding 10 MB | Front/back guard rejects upload with size error message. | | `NOT TESTED` | |

---

### Section C: Physical Webcam Recognition

| Test ID | Test Description | Action / Procedure | Expected Result | Actual Result | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-CAM-01** | Permission Prompt | Click "Live Webcam" tab $\rightarrow$ Click "Start Camera" | Browser displays native dialog: `"Allow app to use your camera?"`. | | `NOT TESTED` | |
| **TC-CAM-02** | Video Feed Display | Grant permission | Live video feed renders in viewport; blue hand reticle overlays center; green `LIVE STREAM (500ms)` badge appears. | | `NOT TESTED` | |
| **TC-CAM-03** | Dynamic Signing | Hold hand gesture inside the central reticle square | Raw frame classification updates every ~500ms; spinner shows `Classifying` without screen freezing. | | `NOT TESTED` | |
| **TC-CAM-04** | Consecutive Stability | Hold gesture steady for >1.5s (3 consecutive frames $\ge 75\%$) | Candidate progress bar hits 3/3; large Stable Prediction badge locks in with green border. | | `NOT TESTED` | |
| **TC-CAM-05** | Manual Insertion Guard | Hold stable pose for 10 seconds without clicking buttons | Assembled text DOES NOT automatically flood with letters; text remains unchanged until user clicks. | | `NOT TESTED` | |
| **TC-CAM-06** | Add Stable Letter | Click "Add Letter" or "Add '[L]' to Sentence" | Letter appends to Text Builder. | | `NOT TESTED` | |
| **TC-CAM-07** | Camera Teardown | Click "Stop Camera" | Live stream terminates; hardware webcam LED indicator light immediately turns off; viewport resets. | | `NOT TESTED` | |
| **TC-CAM-08** | Mode Switch Teardown | Start camera, then click "Upload Image" tab | Switching tabs unmounts webcam; camera LED immediately turns off; hardware tracks released. | | `NOT TESTED` | |

---

### Section D: Actual Speech Output (Voice Conversion)

| Test ID | Test Description | Action / Procedure | Expected Result | Actual Result | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-SPEECH-01** | Audible Speech Playback | Assemble text (e.g. `"HELLO WORLD"`), click "Speak Sentence" | Speech status pill turns blue: `Speaking...`; audible natural English speech plays through speakers/headphones. | | `NOT TESTED` | |
| **TC-SPEECH-02** | Speech Completion | Allow speech utterance to finish | Status pill transitions to green: `Speech Finished`. | | `NOT TESTED` | |
| **TC-SPEECH-03** | Immediate Stop | Click "Speak Sentence", then click "Stop" mid-utterance | Audio playback instantly cuts off; status resets to `Speech Ready` without error alerts. | | `NOT TESTED` | |
| **TC-SPEECH-04** | Voice Selection | Select a different voice from the "Voice:" dropdown and speak | Playback switches to the selected accent/voice (e.g. British, American, Indian English). | | `NOT TESTED` | |
| **TC-SPEECH-05** | Empty Text Inaction | Clear all text, attempt clicking "Speak Sentence" | Button is disabled; no audio triggers; no exceptions thrown. | | `NOT TESTED` | |

---

### Section E: Complete End-to-End User Workflow

| Test ID | Test Description | Action / Procedure | Expected Result | Actual Result | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-FLOW-01** | Upload Letter Recognition | In Upload mode, recognize letter 'H' and click Add Letter | Text Builder area displays `"H"`; Character: 1, Words: 1. | | `NOT TESTED` | |
| **TC-FLOW-02** | Webcam Sign Recognition | Switch to Webcam, stabilize on 'I', click Add Letter | Text Builder area displays `"HI"`; Character: 2, Words: 1. | | `NOT TESTED` | |
| **TC-FLOW-03** | Word Spacing | Click "Space" button | Text displays `"HI "`; duplicate space is blocked if clicked again. | | `NOT TESTED` | |
| **TC-FLOW-04** | Word Spelling & Repeats | Add 'A', 'L', 'L' using buttons or reference cards | Text displays `"HI ALL"`; repeated 'L' characters append cleanly. | | `NOT TESTED` | |
| **TC-FLOW-05** | Correction via Delete | Click "Delete" button | Removes last 'L', leaving `"HI AL"`. Re-add 'L' to restore `"HI ALL"`. | | `NOT TESTED` | |
| **TC-FLOW-06** | Clipboard Copying | Click "Copy Text" | System clipboard receives `"HI ALL"`; button briefly shows `"Copied!"`. | | `NOT TESTED` | |
| **TC-FLOW-07** | Voice Conversion | Click "Speak Sentence" | Audible voice clearly announces `"HI ALL"` through physical audio output. | | `NOT TESTED` | |
| **TC-FLOW-08** | Inline Clear Confirmation | Click "Clear Text" | Button prompts `"Confirm Clear?"`; clicking again safely empties text box. | | `NOT TESTED` | |

---

## 4. Practical Hardware Troubleshooting Guide

### 4.1 Camera Issues
- **Camera Permission Denied (`NotAllowedError`):**
  - *Cause:* User clicked "Block" or browser default policy blocks camera access.
  - *Fix:* In browser address bar, click the tune/lock icon $\rightarrow$ Toggle **Camera** to **Allow** $\rightarrow$ Refresh page (`F5`).
- **Camera Already in Use (`NotReadableError` / `TrackStartError`):**
  - *Cause:* Another application (Zoom, Microsoft Teams, Skype, OBS Studio, Windows Camera App) is locking the webcam hardware.
  - *Fix:* Close all other video conference and camera applications in Windows Task Manager, then click "Start Camera" again.
- **Webcam Device Not Found (`NotFoundError`):**
  - *Cause:* No webcam hardware is plugged in, or privacy shutter / physical switch is engaged.
  - *Fix:* Check USB webcam cable connection, ensure laptop camera privacy slider is open, or verify camera in Windows Device Manager (`Cameras` $\rightarrow$ `Integrated Camera`).

### 4.2 Backend Connectivity Issues
- **Backend Shows "Backend Offline":**
  - *Cause:* FastAPI / Uvicorn server is not running on `localhost:8000`.
  - *Fix:* Open terminal, navigate to project root, activate `fortress` environment, and run:
    ```bash
    uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
    ```
- **Backend Shows "Model Not Loaded" (Degraded):**
  - *Cause:* Missing model checkpoint file at `saved_models/isl_alphabet_cnn_best.keras`.
  - *Fix:* Verify file existence and SHA-256 hash `f3a2c91302ca4843b70a31621f70e209d40e4c3874e731995a8fda9cbc79bd29`.

### 4.3 Speech Synthesis & Audio Issues
- **No Audible Sound from Speakers / Headphones:**
  - *Cause:* Operating system volume muted, browser tab muted, or output device misconfigured.
  - *Fix:*
    1. Check Windows taskbar volume slider $\rightarrow$ ensure unmuted and $\ge 50\%$.
    2. Right-click browser tab $\rightarrow$ ensure "Unmute Tab" is selected.
    3. Test audio playback on another website (e.g. YouTube) to verify system output.
- **Speech Synthesis Shows "Speech Unavailable":**
  - *Cause:* Accessing via unsupported or severely outdated browser, or headless webview.
  - *Fix:* Open page in modern Google Chrome (v110+), Microsoft Edge (v110+), or Mozilla Firefox.
- **Voice List Dropdown is Empty:**
  - *Cause:* OS text-to-speech engine has not yet finished populating voices asynchronously.
  - *Fix:* Wait 2 seconds for `voiceschanged` event, or refresh page. The application automatically falls back to system default voice if list is empty.

---

## 5. Verification Sign-Off Form

| Role | Name | Signature / Identifier | Date | Final Status |
| :--- | :--- | :--- | :--- | :--- |
| **Lead Developer** | Antigravity AI Agent | *Automated Integration Completed* | 2026-11-01 | PASS (Automated) |
| **Human Evaluator** | ____________________ | ____________________ | _________ | `[ ] PASS  [ ] FAIL` |
