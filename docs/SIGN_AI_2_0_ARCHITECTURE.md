# SignAI 2.0 — System Architecture Specification

## 1. Overview & Architectural Philosophy

**SignAI 2.0** is a multimodal Indian Sign Language (ISL) alphabet recognition research prototype. The platform elevates traditional computer vision fingerspelling recognition by integrating two complementary input paradigms:

1. **Deep Visual Representation Stream:** A frozen, pre-trained 2D Convolutional Neural Network (CNN V4) that captures rich texture, palm contours, and spatial finger features from 128×128 RGB images.
2. **Geometric Landmark Representation Stream:** MediaPipe Hand Landmarker (Tasks Vision API) extracting 21 3D hand keypoints transformed into a deterministic, scale-invariant, wrist-relative 78-dimensional feature vector.

These two streams are coupled via a lightweight **Multimodal Feature Fusion Head** with automatic runtime degradation to CNN V4 whenever hand landmarks are obscured or undetected.

```
                           +-------------------------+
                           |  Input Frame / Capture  |
                           +------------+------------+
                                        |
                   +--------------------+--------------------+
                   |                                         |
                   v                                         v
       +-----------------------+                 +-----------------------+
       |   Image Preprocessor  |                 | MediaPipe Landmarker  |
       |  (128x128x3 RGB, /255) |                 | (21 3D Hand Keypoints)|
       +-----------+-----------+                 +-----------+-----------+
                   |                                         |
                   v                                         v
       +-----------------------+                 +-----------------------+
       |   Frozen CNN V4 Base  |                 | Landmark Feature Eng. |
       |  (dense_features 128) |                 | (78-d Scale-Invariant)|
       +-----------+-----------+                 +-----------+-----------+
                   |                                         |
                   +--------------------+--------------------+
                                        |
                                        v
                          +---------------------------+
                          |  Concatenation Head (192) |
                          +-------------+-------------+
                                        |
                                        v
                          +---------------------------+
                          | Multimodal Dense Head     |
                          | (96 units, BatchNorm, L2) |
                          +-------------+-------------+
                                        |
                                        v
                          +---------------------------+
                          | Softmax Classifier (A-Z)  |
                          +---------------------------+
```

---

## 2. Component Subsystems

### 2.1 Backend Architecture (FastAPI & Python 3.11)

The backend is organized into modular services and versioned API routers:

- **`backend/main.py`:** Application entry point, lifespan management, CORS configuration, and modular router registration.
- **`backend/routers/`:**
  - `vision_routes.py`: Endpoints for 21-point hand landmark extraction (`/vision/landmarks`) and camera optical quality evaluation (`/vision/quality`).
  - `explainability_routes.py`: Gradient-weighted Class Activation Mapping (`/explain/gradcam`) on layer `block3_conv2`.
  - `model_routes.py`: Model architecture specifications (`/models/summary`), multimodal prediction with fallback (`/models/fusion/predict`), and 3-way concurrent comparison (`/models/compare`).
  - `temporal_routes.py`: Streaming landmark sequence collector (`/temporal/stream`), buffer reset (`/temporal/reset`), and motion energy status (`/temporal/status`).
  - Legacy Compatibility: Direct `/health` and `/predict` endpoints remain 100% backward-compatible.
- **`backend/vision/`:**
  - `hand_landmarker.py`: MediaPipe Hand Landmarker task wrapper configured for `num_hands=2`. Extracts 21 3D normalized and pixel coordinates, handedness (Left/Right), independent bounding boxes, and scale for both hands simultaneously.
  - `landmark_features.py`: Computes wrist-relative scale-invariant coordinates, joint flexion angles, fingertip Euclidean distances, and binary extension flags (78-dim per detected hand). Never combines dual hands into a single 78-dim vector.
  - `camera_quality.py`: Evaluates mean brightness, standard deviation contrast, Laplacian blur variance, and hand framing percentage.
- **`backend/explainability/`:**
  - `gradcam.py`: TensorFlow GradientTape implementation for computing activation gradients on CNN V4 layer `block3_conv2`.
  - `heatmap_generator.py`: Colormap blending (cv2.COLORMAP_JET) and base64 PNG serialization.
- **`backend/services/`:**
  - `fusion_service.py`: Singleton service managing multimodal inference with automatic single-hand fallback and explicit dual-hand independent evaluation (evaluating both hands independently via Landmark MLP without inventing compound predictions).
  - `calibration_service.py`: Temperature scaling ($T=1.28$) and Expected Calibration Error (ECE) analysis.
- **`backend/temporal/`:**
  - `sequence_collector.py`: Ring buffer tracking sliding temporal sequences (default 30 frames), motion energy, and cooldown.
  - `temporal_inference.py`: Recurrent inference coordinator for dynamic sign trajectories (e.g., J and Z).

---

## 3. Dual-Hand Detection & Tracking Architecture

To reflect the reality of Indian Sign Language (where letters such as A, B, C, D, etc., are naturally formed with two hands or interaction between hands), SignAI 2.0 incorporates native dual-hand tracking:

1. **MediaPipe Configuration:**
   - Initialized with `num_hands=2` over the official `hand_landmarker.task` model bundle.
   - Retains single-hand backward compatibility while processing up to two simultaneous hands per frame.
2. **Independent Landmark & Feature Extraction:**
   - Each detected hand is extracted as a distinct object with its own:
     - 21 3D landmarks (normalized $x, y, z$ and pixel coordinates).
     - Handedness classification (`Left` or `Right`) with detection confidence.
     - Independent bounding box $(x_{min}, y_{min}, x_{max}, y_{max})$.
     - Independent 78-dimensional feature vector ($21\times 3$ wrist-relative coordinates + 5 joint angles + 5 fingertip distances + 5 binary extension flags).
   - Under no circumstances are the two hands concatenated or merged into an artificial combined 78-d vector.
3. **Dual-Hand Fusion Policy:**
   - When one hand is present, standard multimodal fusion (CNN V4 visual stream + primary hand geometric stream) is performed.
   - When two hands are present, the primary hand maintains the primary multimodal prediction, while both Left and Right hands undergo independent geometric evaluation via the Landmark MLP (`dual_hand_analysis["per_hand_predictions"]`).
   - The system displays a transparent disclaimer indicating that the static alphabet models classify single-hand postures, guaranteeing scientific integrity without inventing synthetic compound letter predictions.
4. **Studio Visual Overlay:**
   - Dual-color skeleton rendering:
     - **Right Hand:** Sapphire Blue (`#2563EB`) bones, sky blue (`#60A5FA`) joints, vibrant blue (`#3B82F6`) tips, and dashed bounding box.
     - **Left Hand:** Warm Orange (`#EA580C`) bones, amber (`#FB923C`) joints, orange (`#F97316`) tips, and dashed bounding box.
   - Dynamic anti-collision label positioning to avoid visual overlap when hands are adjacent or interacting.
   - Real-time hand count pill indicating current tracking state (`0 Hands`, `1 Hand (Left/Right)`, or `2 Hands (Dual Tracking)`).

---

## 4. Data Flow & Security Guardrails

1. **CNN V4 Model Checkpoint Immutability:**
   - The CNN V4 model (`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`, SHA-256: `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`) is strictly read-only.
   - Its weights are frozen (`trainable=False`) during multimodal fusion training.
2. **Dataset Quarantine:**
   - The independent `Testing` split (5,161 images) is quarantined.
   - All feature extraction, MLP training, and fusion head optimization strictly use `Training` (17,407) and `Validation` (2,517) splits.
3. **Graceful Degradation:**
   - If MediaPipe cannot detect a hand (poor lighting, partial occlusion, or blank background), the fusion pipeline transparently falls back to pure CNN V4 visual inference and logs `fallback_used: true`.
