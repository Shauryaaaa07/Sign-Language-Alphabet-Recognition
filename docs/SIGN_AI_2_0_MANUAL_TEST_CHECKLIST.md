# SignAI 2.0 — Physical Hardware Manual Test Checklist

This checklist guides the human operator through hands-on verification of physical webcam hardware, dual-hand MediaPipe tracking, real-time deep learning inference, Grad-CAM attention heatmaps, and multilingual speech synthesis.

---

## Pre-Requisites & Environment Setup

1. **Verify Backend Server is Running:**
   - Open a browser tab to `http://127.0.0.1:8000/health`.
   - Expected JSON: `{"status": "healthy", "model_loaded": true, "num_classes": 26, ...}`.
2. **Verify Frontend UI is Running:**
   - Open a browser tab to `http://127.0.0.1:5173`.
   - Expected UI: SignAI 2.0 homepage with navigation bar ("Studio", "Practice", "Lab", "Dashboard", "Performance", "About").
3. **Hardware Requirements:**
   - Operational USB or built-in webcam.
   - Operational audio speaker or headphones.
   - Normal room lighting (avoid dark shadows or direct window glare).

---

## Physical Hardware Verification Checklist

Follow each test step in order. Record your findings in the brackets and observation fields below.

---

### [ ] HW-01: Webcam Startup & Viewfinder Stream
- **Target Page:** `http://127.0.0.1:5173/#studio`
- **Steps:**
  1. Navigate to the **Studio** page.
  2. Click the blue **Start Camera** button.
  3. If prompted by the browser, click **Allow** for camera permissions.
- **Expected Observations:**
  - [ ] Browser requests camera permissions cleanly.
  - [ ] Live video feed appears in the viewfinder without distortion.
  - [ ] Green status pill shows `Camera active`.
  - [ ] Frame rate is smooth (no freezing or major stutter).
- **Operator Notes / Actual Behavior:**
  - Camera Model: _____________________________________________
  - Observed Latency: Smooth [ ] / Stuttering [ ]

---

### [ ] HW-02: Single-Hand Tracking & Skeleton Overlay
- **Target Page:** Studio Viewfinder
- **Steps:**
  1. Ensure the **Skeleton Overlay** toggle switch is enabled (ON).
  2. Hold your **Right hand** in front of the camera (fingers spread).
  3. Move your hand slowly left, right, up, down, and then quickly.
  4. Lower your right hand and present your **Left hand**.
- **Expected Observations:**
  - [ ] All 21 landmarks track accurately across the palm and fingertips.
  - [ ] **Right Hand:** Bones rendered in **Sapphire Blue** (`#2563EB`) with label `RIGHT HAND`.
  - [ ] **Left Hand:** Bones rendered in **Warm Orange** (`#EA580C`) with label `LEFT HAND`.
  - [ ] Viewfinder pill shows `1 Hand (Right)` or `1 Hand (Left)`.
  - [ ] Coordinates align naturally with your mirrored physical movements.
- **Operator Notes / Actual Behavior:**
  - Tracking Stability: Stable [ ] / Jittery [ ] / Lost Tracking [ ]

---

### [ ] HW-03: Dual-Hand Simultaneous Tracking
- **Target Page:** Studio Viewfinder
- **Steps:**
  1. Present **BOTH hands** to the camera at the same time.
  2. Keep hands separated by a few inches so both are fully visible.
  3. Slowly bring hands closer together, then move one hand out of the frame and back in.
- **Expected Observations:**
  - [ ] Viewfinder pill changes to green `2 Hands (Dual Tracking)`.
  - [ ] Two distinct skeleton colors appear simultaneously: Blue for Right, Orange for Left.
  - [ ] Two independent dashed bounding boxes appear around each hand.
  - [ ] Hand labels (`RIGHT HAND (xx%)` and `LEFT HAND (xx%)`) do not overlap or collide.
  - [ ] When one hand exits, tracking gracefully drops to 1 hand without errors.
- **Operator Notes / Actual Behavior:**
  - Dual Tracking Result: Both Tracked [ ] / One Dropped [ ] / Inverted Handedness [ ]

---

### [ ] HW-04: CNN V4 Baseline Recognition
- **Target Page:** Studio Recognition Panel
- **Steps:**
  1. In the Studio model selector, choose **CNN V4 Only**.
  2. Present your hand and form the sign for **A** (closed fist with thumb resting alongside).
  3. Hold steady for 3 consecutive frames.
  4. Repeat for signs **B** (open palm, 4 fingers vertical, thumb folded) and **L** (index and thumb forming an L-shape).
- **Expected Observations:**
  - [ ] Circular stability indicator advances ($1 \to 2 \to 3$) and locks the letter.
  - [ ] Output card displays predicted letter with top-3 candidates.
  - [ ] Inference time is displayed in milliseconds ($\sim 40\text{--}90\text{ ms}$).
- **Operator Recorded Metrics:**
  - Sign A: Predicted: _____ | Confidence: _____% | Latency: _____ ms
  - Sign B: Predicted: _____ | Confidence: _____% | Latency: _____ ms
  - Sign L: Predicted: _____ | Confidence: _____% | Latency: _____ ms

---

### [ ] HW-05: Multimodal Fusion Recognition
- **Target Page:** Studio Recognition Panel
- **Steps:**
  1. In the Studio model selector, switch to **Multimodal Fusion**.
  2. Sign the same letters (**A**, **B**, **L**).
  3. Show **both hands** simultaneously.
- **Expected Observations:**
  - [ ] Multimodal inference badge shows active fusion mode.
  - [ ] Top prediction updates with confidence and latency.
  - [ ] When dual hands are present, the **Dual-Hand Analysis** card appears, displaying side-by-side independent Left and Right hand letter cards.
  - [ ] Disclaimer note explains that single-hand fingerspelling models evaluate postures independently.
- **Operator Recorded Metrics:**
  - Sign A (Fusion): Predicted: _____ | Confidence: _____% | Latency: _____ ms
  - Dual-Hand Display: Showed Left & Right Cards [ ] | Showed Single Card [ ]

---

### [ ] HW-06: Occlusion Handling & CNN Fallback
- **Target Page:** Studio Viewfinder (Multimodal Fusion Mode)
- **Steps:**
  1. While signing in Fusion mode, partially hide your fingers with a book/paper, or move half of your hand outside the frame so landmarks disappear.
- **Expected Observations:**
  - [ ] When MediaPipe loses landmarks, the system does NOT crash or freeze.
  - [ ] The system automatically falls back to CNN V4 visual inference.
  - [ ] As soon as the full hand returns to view, landmark tracking recovers immediately.
- **Operator Notes / Actual Behavior:**
  - Fallback Gracefulness: Seamless [ ] / UI Froze [ ] / Error Displayed [ ]

---

### [ ] HW-07: Grad-CAM Explainability Heatmap
- **Target Page:** Studio Prediction Panel
- **Steps:**
  1. Hold a clear hand sign in front of the camera.
  2. Click the **Grad-CAM Attention** button in the prediction card.
- **Expected Observations:**
  - [ ] A modal overlay appears displaying the captured hand frame.
  - [ ] A smooth Jet colormap heatmap is overlaid onto the image.
  - [ ] High-activation regions (red/yellow) concentrate on the hand (fingers/palm), not background clutter.
  - [ ] Clicking the close button dismisses the modal cleanly.
- **Operator Notes / Actual Behavior:**
  - Heatmap Focus: Concentrated on Hand [ ] / Diffuse / Background [ ]

---

### [ ] HW-08: Camera Quality Analyzer Warnings
- **Target Page:** Studio Viewfinder Banner
- **Steps:**
  1. Observe the camera quality status badge in normal lighting.
  2. Dim your room lights or partially cover the lens to simulate low light.
  3. Wave your hand rapidly to cause motion blur.
  4. Move your hand very far away from the camera.
- **Expected Observations:**
  - [ ] Normal light shows `Quality: Good` (green).
  - [ ] Low light shows advisory: `"Lighting is too low (room is dim)"`.
  - [ ] Motion blur shows advisory: `"Camera image is blurry"`.
  - [ ] Far distance shows advisory: `"Hand is too far — bring it closer"`.
- **Operator Notes / Actual Behavior:**
  - Warning Responsiveness: Dynamic & Accurate [ ] / Slow [ ] / Inaccurate [ ]

---

### [ ] HW-09: Camera Shutdown & Hardware LED Release
- **Target Page:** Studio Viewfinder
- **Steps:**
  1. Click the red **Stop Camera** button.
  2. Inspect the physical camera indicator LED on your laptop or monitor.
  3. Navigate to the **Learn** page, then return to **Studio**.
- **Expected Observations:**
  - [ ] Video stream disappears immediately from the viewfinder.
  - [ ] The physical camera LED turns OFF completely.
  - [ ] No background video stream or CPU usage remains active.
- **Operator Notes / Actual Behavior:**
  - Hardware LED: Turned Off Immediately [ ] / Stayed On [ ]

---

### [ ] HW-10: Text Builder & Multilingual Voice Synthesis (TTS)
- **Target Page:** Studio Text Builder Panel
- **Steps:**
  1. Add letters **H**, **E**, **L**, **L**, **O** using the **Add to Text** button or locked camera gesture.
  2. Test editing buttons: **Space**, **Backspace**, **Undo**, and **Clear**.
  3. Re-type or add "HELLO WORLD". Click **Copy to Clipboard** and paste into Notepad to verify.
  4. Select a voice from the voice dropdown (try both an English and a local voice if available).
  5. Adjust the **Speed** and **Pitch** sliders.
  6. Click **Speak Text**. While the voice is speaking, click **Stop Speech**.
- **Expected Observations:**
  - [ ] Text is accurately assembled; duplicate consecutive spaces are prevented.
  - [ ] Undo reverts the last operation accurately.
  - [ ] Copy to Clipboard successfully copies the text.
  - [ ] Speech plays clearly through the audio output device.
  - [ ] Stop Speech cancels speech playback immediately without audio lag.
- **Operator Notes / Actual Behavior:**
  - Voice Selected: _____________________________________________
  - Speech Audio Quality: Clear [ ] / Distorted [ ] / No Audio [ ]
  - Stop Speech Response: Instant [ ] / Delayed [ ]

---

## Operator Sign-Off & Hardware Verification Summary

| Item | Result Summary |
| :--- | :--- |
| **Operator Name:** | _____________________________________________ |
| **Date & Time of Test:** | _____________________________________________ |
| **Operating System & Browser:** | Windows 11 / Chrome / Edge (circle one) |
| **Total Physical Tests Checked:** | _____ / 10 |
| **Hardware Tests Passed:** | _____ / 10 |
| **Hardware Tests Failed / Issues:** | _____________________________________________ |
| **Operator Signature / Initials:** | _____________________________________________ |