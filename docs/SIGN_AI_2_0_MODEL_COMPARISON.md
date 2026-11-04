# SignAI 2.0 — Comparative Model Analysis

This document provides a scientific evaluation of the four model paradigms developed and integrated into the SignAI 2.0 platform.

---

## 1. Architectural Comparison Matrix

| Specification | Model 1: CNN V4 (Visual Baseline) | Model 2: Geometric Landmark MLP | Model 3: Multimodal Fusion Head | Model 4: Dynamic Temporal (BiLSTM / BiGRU) |
| :--- | :--- | :--- | :--- | :--- |
| **Model Type** | 2D Convolutional Neural Network | Multilayer Perceptron | Two-Stream Feature Fusion Head | Bidirectional Recurrent Neural Network |
| **Input Modality** | 128×128×3 RGB Image Tensor | 78-dimensional Landmark Vector | 128×128×3 Image + 78-d Vector | 30-frame Sequence of 78-d Vectors |
| **Total Parameters** | 308,218 | 18,458 | 331,610 | 118,787 (BiLSTM) / 89,667 (BiGRU) |
| **Trainable Parameters**| 308,218 (Frozen in V2.0) | 18,458 | 26,426 (CNN base frozen) | 118,787 / 89,667 |
| **Validation Accuracy** | 80.14% (Val split) | 69.17% (RF: 77.65%) | **86.32%** | Architectural Baseline (~53%) |
| **Test Accuracy** | 86.34% (Quarantined Test Set)| N/A (Trained on Train/Val only)| N/A (Evaluated on Val split) | N/A (Dynamic Video Collection Ongoing) |
| **Validation Macro F1** | 77.68% (Val split) | 63.77% (RF: 72.44%) | **82.40%** | N/A |
| **Test Macro F1** | 83.96% (Quarantined Test Set)| N/A | N/A | N/A |
| **Inference Latency** | ~28 ms (CPU) | ~3 ms (CPU) | ~38 ms (CPU) | ~12 ms (CPU) |
| **Lighting Sensitivity**| High (Degrades in low lux) | **Zero** (Normalized coordinates) | Low (Geometric branch stabilizes)| Low |
| **Background Invariance**| Moderate | **High** (Keypoints only) | High | High |
| **Explainability** | Grad-CAM (`block3_conv2`) | Feature Weight Attribution | Dual Attribution | Temporal Attention Weights |
| **Dynamic Sign Support** | Static Only (Single Frame) | Static Only | Static Only | **Dynamic Trajectories (J, Z)** |

---

## 2. In-Depth Paradigm Analysis

### Paradigm 1: CNN V4 (Visual Baseline)
- **Strengths:** Captures intricate visual cues such as palm creases, skin shading, thumb tucks, and subtle finger overlaps that lack discrete landmark annotations.
- **Weaknesses:** Vulnerable to environmental shifts. Validation stress tests revealed that severe illumination drops reduced accuracy to 32.82%, and extreme blur reduced accuracy to 47.12%.
- **Role in V2.0:** Serves as the immutable primary feature extractor and the fallback classifier.

### Paradigm 2: Geometric Landmark MLP
- **Strengths:** Exceptional computational efficiency (18,458 parameters, ~3 ms latency). Complete invariance to room illumination, camera white-balance shifts, skin tone variations, and background clutter.
- **Weaknesses:** Lower overall validation accuracy (69.17% MLP, 77.65% Random Forest) because MediaPipe hand landmarks abstract away fine-grained finger contact points and palm contours.
- **Role in V2.0:** Lightweight edge-device inference and secondary verification stream.

### Paradigm 3: Multimodal Feature Fusion Head
- **Strengths:** Synthesizes the contextual richness of CNN V4 with the geometric invariance of MediaPipe landmarks. Produces stable predictions under varying angles. Includes a zero-cost fallback guarantee: if hand landmarks cannot be resolved, inference seamlessly executes on the CNN stream.
- **Empirical Metrics:** Reached 86.32% validation accuracy and 82.40% macro F1 across all 26 alphabet classes with only 26,426 trainable parameters.
- **Role in V2.0:** Default recommended recognition engine in the Studio.

### Paradigm 4: Recurrent Temporal Networks (BiLSTM / BiGRU)
- **Strengths:** Designed specifically to address the fundamental limitation of static models on dynamic ISL signs (specifically the curved hook motion of **J** and the zig-zag trajectory of **Z**).
- **Status & Academic Transparency:** Architectural infrastructure, 30-frame sliding sequence collector, and motion energy tracking are fully implemented and verified. Full multi-signer training is pending physical video dataset recording.
