# System Architecture & Technical Design

This document describes the end-to-end software architecture, component contracts, inference pipeline, and real-time gesture stabilization logic for the **AI-Based Indian Sign Language Alphabet Recognition and Voice Conversion System**.

---

## 1. High-Level Architecture (Three-Tier Decoupled Design)

The system is organized into three decoupled layers to maintain a clean separation of concerns:

```
[Client Layer: React 19 + Vite + Tailwind CSS]
                    │
                    ▼ HTTP REST (Multipart / JSON)
[API & Preprocessing Layer: Python FastAPI + OpenCV]
                    │
                    ▼ In-Memory Batch Tensor (Shape: 1, 128, 128, 3)
[Inference Layer: TensorFlow/Keras CNN (26 Output Classes)]
```

### Layer Responsibilities:
1. **Client / Presentation Layer (`frontend/`):**
   - Accesses user camera securely using `navigator.mediaDevices.getUserMedia`.
   - Supports static file upload (PNG/JPG/JPEG).
   - Manages client-side gesture stabilization (debounce & repeat-lock filter).
   - Collects validated letters in an editable Text Builder.
   - Synthesizes speech using the browser-native Web Speech API (`window.speechSynthesis`).
2. **API & Preprocessing Layer (`backend/`):**
   - Serves asynchronous REST endpoints using FastAPI.
   - Decodes incoming image streams, validates dimensions, and verifies RGB color consistency.
   - Resizes frames to standard tensor dimensions (proposed: $128 \times 128$) and normalizes pixel values to $[0, 1]$.
   - Manages model weights in memory using a Singleton Service Pattern.
   - Handles optional SQLite database persistence (deferred until the core recognition pipeline is verified).
3. **Machine Learning & Inference Layer (`training/` & `saved_models/`):**
   - Modular training scripts separate from the inference service.
   - Convolutional Neural Network with 26 softmax output neurons mapping to classes A–Z.
   - Stores genuine evaluation metrics and confusion matrices in `results/`.

---

## 2. End-to-End Gesture-to-Voice Workflow

The recognition pipeline processes gestures through six discrete stages:

```
[1. Hand Sign Input] ──> [2. Frame Capture] ──> [3. OpenCV Preprocessing]
                                                        │
[6. English Voice Output] <── [5. Debounce Text Builder] <── [4. CNN Inference]
```

1. **Input Acquisition:** The user displays an ISL fingerspelling hand sign before their webcam or uploads an image.
2. **Frame Handling:** The browser captures video frames at controlled intervals (proposed: 300–500 ms) and posts them to `/predict-frame`.
3. **Preprocessing:** OpenCV decodes the byte buffer, ensures RGB format, resizes to target dimensions ($128 \times 128$), and normalizes pixel intensity:
   $$\text{Normalized Pixel} = \frac{\text{Pixel Value}}{255.0}$$
4. **CNN Inference:** The preprocessed tensor is passed to the loaded model. The output layer generates class probability distributions via Softmax:
   $$P(y = i \mid x) = \frac{e^{z_i}}{\sum_{j=1}^{26} e^{z_j}}$$
5. **Debounce & Text Building:** The client verifies stability across consecutive matching predictions before appending the character.
6. **Voice Conversion:** When the user clicks "Speak", `window.speechSynthesis.speak()` reads the assembled text aloud in English.

---

## 3. Real-Time Camera Debounce & Stability Engine

In real-time webcam inference (15–30 FPS), streaming video introduces two significant failure modes:
1. **Flicker:** Transitory hand transitions causing brief false-positive classifications.
2. **Character Flooding:** A held sign triggering 20+ duplicate characters per second.

### Stabilization Algorithm:
```
           Incoming Frame Prediction (Letter L, Confidence C)
                                  │
                                  ▼
                     Is C >= Confidence Threshold?
                                  │
                       Yes ───────┴─────── No ──> Ignore Frame
                        │
                        ▼
           Does L match candidate in buffer?
                        │
             Yes ───────┴─────── No ──> Reset buffer counter to 1
              │
              ▼
    Increment buffer counter
              │
              ▼
   Has buffer reached N consecutive frames?
              │
   Yes ───────┴─────── No ──> Wait for next frame
    │
    ▼
Has L already been emitted for this continuous gesture? (Repeat-Lock)
    │
    No ───────> Append L to Text Builder & Set Repeat-Lock
    Yes ──────> Suppress duplicate character
```

- **Repeat-Lock Release:** Triggered when the user lowers their hand or changes to a different verified sign.

---

## 4. Parameter Management (Proposed vs Confirmed)

| Parameter | Proposed Value | Status | Finalization Criteria |
|---|---|---|---|
| Image Dimensions | $128 \times 128 \times 3$ | Proposed | Subject to Phase 2 dataset inspection and Phase 3 experiments |
| Confidence Threshold | $\ge 75\%\text{--}80\%$ | Proposed | Subject to real-time webcam calibration in Phase 8 |
| Frame Interval | $300\text{--}500\text{ ms}$ | Proposed | Tuned based on observed inference and network latency |
| Inference Latency | Unspecified | To be Measured | Measured on actual deployment hardware; no synthetic claims |
| Class List | A to Z (26 classes) | Subject to Audit | Motion-dependent signs (J & Z) inspected in Phase 2 Audit Gate |

---

## 5. Movement-Dependent Signs Policy (J & Z)
ISL fingerspelling includes dynamic letters (notably **'J'** and **'Z'**) that traditionally require motion strokes. A 2D static CNN cannot directly model temporal trajectories. 

Our engineering policy:
- The Phase 2 Dataset Audit Gate will inspect how public datasets represent these classes.
- Static CNN limits will be reported honestly as an architectural boundary, leaving temporal extensions (e.g., 3D CNNs or sequence models) for future development.
