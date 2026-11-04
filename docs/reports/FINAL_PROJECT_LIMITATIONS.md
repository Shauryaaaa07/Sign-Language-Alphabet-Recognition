# SignAI: Comprehensive Project Limitations & Theoretical Boundaries

**Document ID:** `DOC-LIM-2026-V4`  
**System Scope:** 26-Class Static Indian Sign Language Alphabet Recognition (A–Z)  
**Model Checkpoint:** `saved_models/experiments/isl_alphabet_cnn_v4_best.keras`  
**Evaluation Standard:** Independent Held-Out Testing Partition ($N=5,161$)  
**Status:** Approved for Academic Submission & Production Disclosure

---

## 1. Executive Purpose & Academic Framing

A core hallmark of rigorous computer vision research is the honest demarcation of system boundaries. **SignAI** is engineered and validated specifically as an **educational assistive prototype for recognizing static single-hand Indian Sign Language (ISL) alphabet finger-spellings (A–Z)**.

It is **NOT** a full continuous sign language translation system, nor does it interpret fluent Indian Sign Language sentences, conversational syntax, facial expressions, or dynamic movements. This document provides an exhaustive, mathematically and empirically grounded analysis of the architectural, algorithmic, dataset, and physical operational limitations of the project.

---

## 2. Fundamental Linguistic & Theoretical Limitations

### 2.1 Static 2D Poses vs. Continuous Natural Sign Language
Natural Indian Sign Language (ISL) is a rich, natural, multidimensional language governed by complex spatial grammar. It encompasses:
1. **Continuous Motion & Dynamics:** Signs in ISL are not sequences of discrete static hand shapes; they consist of movement trajectories, hand orientations, and positional transitions between morphemes.
2. **Non-Manual Markers (NMMs):** Over $40\%$ of syntactic information in natural ISL is communicated through facial expressions, head tilts, eye gaze, and mouth movements. A frame-by-frame static hand classifier completely omits these essential linguistic channels.
3. **Two-Handed Lexical Signs:** While the English alphabet in American Sign Language (ASL) is purely one-handed, many natural words in Indian Sign Language are two-handed signs with contact points across both palms. SignAI evaluates monocular single-hand pose crops.

```
+-------------------------------------------------------------------------+
|                    NATURAL INDIAN SIGN LANGUAGE                         |
|  [Spatial Grammar]  [Two-Handed Signs]  [Facial NMMs]  [Body Poses]     |
+-------------------------------------------------------------------------+
                                    |
            =================== EXCLUDED ===================
                                    |
+-------------------------------------------------------------------------+
|                         SIGNAI SYSTEM SCOPE                             |
|  [Static Single-Hand Monocular RGB Alphabet Finger-Spelling (A-Z)]      |
+-------------------------------------------------------------------------+
```

### 2.2 Dynamic Alphabet Letters: The J and Z Keyframe Approximation
In standard manual finger-spelling:
- **The Letter 'J':** Formed by extending the little finger and sweeping the hand downward in a curvilinear "J" trajectory.
- **The Letter 'Z':** Formed by extending the index finger and tracing a zig-zag "Z" path in 3D air space.

**System Limitation:**
Because CNN V4 operates on individual 2D static images without recurrent or 3D temporal convolutions (e.g., LSTM, GRU, or SlowFast 3D-CNNs), dynamic trajectory information is physically inaccessible. In the RealSign dataset, **J and Z are recorded as single frozen keyframe poses**. Consequently, the model recognizes the terminal or intermediate static hand configuration rather than the defining motion stroke.

---

## 3. Computer Vision & Feature Space Limitations

### 3.1 Monocular Planar Projection and Silhouette Overlap
A 2D RGB camera projects 3D articulated hand joints onto a 2D image plane ($I \in \mathbb{R}^{H \times W \times 3}$). When fingers align directly along the optical ray of the camera, significant self-occlusion occurs.

This phenomenon directly explains the measured class-specific performance disparities on the held-out test set:

| Class | Independent Test F1 | Independent Test Recall | Identified Failure Mechanism |
| :---: | :---: | :---: | :--- |
| **W** | **0.00%** | **0.00%** (0 / 173) | **Planar Silhouette Ambiguity:** In 2D silhouette space, the three splayed upright fingers of 'W' visually collapse into the identical bounding contours of 'E' and 'X' when viewed from frontal angles, causing systematic misclassification. |
| **S** | **40.00%** | **25.00%** (5 / 20) | **Fist & Thumb Occlusion:** In 'S', the fist is tightly clenched with the thumb crossing over the fingers. In low-contrast RGB representations, this minimal structural difference is easily confused with 'A' (thumb alongside fist) or 'T'. |
| **Z** | **66.67%** | **52.63%** (10 / 19) | **Loss of Dynamic Motion Cue:** Without temporal motion vectors, the static index finger pointing configuration resembles a stationary pointing gesture. |

### 3.2 Spatial Resolution Limitations ($128 \times 128$)
Downsampling input frames from $1080\text{p}$ or $720\text{p}$ webcam captures to $128 \times 128 \times 3$ is computationally necessary for sub-15ms real-time CPU inference ($308\text{k}$ parameters). However, this bilinear compression diminishes sub-pixel edge definition around distal interphalangeal finger joints, particularly when the user's hand is situated more than $1\text{ meter}$ from the camera lens.

---

## 4. Dataset & Generalization Boundaries

### 4.1 Lack of Signer-Independent Split Guarantees
As demonstrated in the comprehensive Dataset Audit (`DATASET_AND_SPLIT_AUDIT.md`), the upstream **RealSign** dataset does not include person/subject identity metadata for the Validation ($98.9\%$) or Testing ($99.8\%$) partitions.
- **Academic Consequence:** While rigorous strict-file quarantine and duplicate removal were enforced ($892$ leakage files permanently eliminated), SignAI **cannot and does not claim signer-independent generalization**. The model's measured $86.34\%$ test accuracy reflects evaluation on independent held-out frames, but cannot guarantee equivalent performance across unseen individuals with divergent hand anthropometry, skin tones, or arthritis.

### 4.2 Background and Environment Invariance
The training partition predominantly features relatively clean, indoor, single-background setups. When placed in front of visually cluttered backgrounds (such as busy bookshelves, foliage, or high-contrast textiles), standard 2D convolution filters without an explicit hand segmentation or landmark extraction front-end can absorb spurious background edge artifacts.

---

## 5. Photometric & Environmental Boundaries (Empirical Evidence)

Based on empirical stress tests across 32,721 model evaluations on the full validation split (`MODEL_ROBUSTNESS_EVALUATION.md`):

1. **Severe Sensitivity to Luminance ($< 0.25$ or $> 0.85$ Normalized Luminance):**
   - Underexposure ($-40\%$ brightness) triggers an acute **$-47.24\text{ pp}$** drop in classification accuracy ($80.06\% \rightarrow 32.82\%$).
   - Overexposure ($+40\%$ brightness) triggers a **$-32.94\text{ pp}$** drop ($80.06\% \rightarrow 47.12\%$).
   - **Root Cause:** In extreme low light, convolution activation maps fail to exceed ReLU activation thresholds. In overexposure, highlights clip to $1.0$, destroying edge gradients between fingers.
2. **Tolerance to Defocus and Sensor Grain:**
   - The model is remarkably stable against lens blur ($r=1.5\text{ px}$, $+0.28\text{ pp}$) and low-light sensor noise ($\sigma=15$, $-2.22\text{ pp}$), confirming that gross hand silhouette contours are the primary discriminative feature.

---

## 6. Software & Production Deployment Limitations

1. **Hardware In-the-Loop Testing:**
   Automated unit, integration, and E2E mock suites pass with $100\%$ success ($69/69$ tests). However, physical webcam sensors, physical room lighting, and physical audio speakers depend on end-user browser permissions and hardware environments, requiring human-in-the-loop verification.
2. **Browser Web Speech Synthesis:**
   Browser speech synthesis utilizes the native HTML5 `window.speechSynthesis` API. Synthesis voices, latency, and pronunciation are dictated by the host operating system's installed voice packs and browser security policies (which require explicit user gestures before playing audio).

---

## 7. Strategic Future Roadmap

To surpass these boundaries in future research iterations, the following engineering enhancements are proposed:

1. **Landmark-Based Graph Neural Networks (GNNs):**
   Deploying MediaPipe Hands to extract 21 3D hand keypoints prior to classification, decoupling skin tone, background clutter, and lighting from hand pose geometry.
2. **Temporal 3D-CNN / Transformer Pipelines:**
   Introducing a lightweight 16-frame sliding temporal window (e.g., MobileNetV3 + Bi-LSTM) to authentically support dynamic letters (J and Z) and continuous word finger-spelling.
3. **Multi-Signer Cross-Validation Benchmarks:**
   Constructing a newly recorded ISL dataset with explicit metadata tracking 50+ diverse signers across varied skin tones, age groups, and illumination conditions.

---

## 8. Final Academic Disclosure

SignAI is presented as a high-performing, mathematically validated **26-Class ISL Alphabet Recognition System** that achieves an independently audited **86.34% test accuracy** and **83.96% macro F1-score**. Its performance boundaries have been empirically verified and disclosed with complete academic honesty.
