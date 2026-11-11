# Baseline Model Error Analysis & Improvement Plan

**Project:** AI-Based Indian Sign Language (ISL) Alphabet Recognition and Voice Conversion System  
**Phase:** Phase 6 — Model Improvement & Advanced Experimentation  
**Milestone:** 6.1 — Baseline Model Error Analysis  
**Date:** November 1, 2026  
**Status:** COMPLETE (Ready for Review)

---

## 1. Executive Summary

Phase 3 established the first verifiable baseline 2D Convolutional Neural Network (CNN) for 26-class Indian Sign Language fingerspelling, and Phase 3.4 conducted the independent test evaluation. The baseline model achieved:
- **Independent Test Accuracy:** `59.04%` (3,047 / 5,161 correct predictions)
- **Macro F1-Score:** `56.74%` | **Weighted F1-Score:** `56.66%`
- **Macro Precision:** `60.71%` | **Macro Recall:** `59.15%`
- **Total Trainable Parameters:** `113,114`
- **Model Checkpoint Evaluated:** `saved_models/isl_alphabet_cnn_best.keras` (1.34 MB)

While the model functions successfully as an initial proof of concept, empirical analysis reveals **severe overfitting starting at Epoch 4**, massive cross-class confusion for morphologically similar hand signs, and a total recall failure on class **W** (`0.0%` recall).

This document provides a rigorous, data-driven post-mortem of the baseline model's failure modes and defines a ranked, evidence-based improvement plan for Phase 6.

---

## 2. Training Behavior & Overfitting Post-Mortem

### 2.1 Complete Metric Trajectory (Epoch-by-Epoch)

The baseline model was trained for 8 epochs on CPU using `training/train_model.py` before `EarlyStopping` (patience = 5) halted training:

| Epoch (1-based) | Training Loss | Training Accuracy | Validation Loss | Validation Accuracy | Learning Rate | Checkpoint Action |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 2.9881 | 8.73% | 2.9117 | 12.51% | 1.00e-03 | Saved Checkpoint |
| **2** | 2.3061 | 22.83% | 2.8542 | 33.06% | 1.00e-03 | Saved Checkpoint |
| **3** | **1.6748** | **41.54%** | **2.8015** | **55.78%** | 1.00e-03 | **Saved Best Checkpoint** |
| **4** | 1.1634 | 58.17% | 3.0857 | 62.46% | 1.00e-03 | - *(Loss Increased)* |
| **5** | 0.8728 | 68.60% | 3.2669 | 69.85% | 1.00e-03 | - |
| **6** | 0.6827 | 76.04% | 3.7099 | 74.37% | 1.00e-03 | - |
| **7** | 0.5078 | 82.87% | 3.8813 | 74.45% | 5.00e-04 | `ReduceLROnPlateau` |
| **8** | 0.4623 | 83.90% | 3.9598 | 76.08% | 5.00e-04 | **EarlyStopping Halted** |

### 2.2 Overfitting Genesis & Divergence Dynamics
1. **The Overfitting Pivot (Epoch 4):**
   Up to Epoch 3, training and validation loss decreased in tandem ($2.9881 \rightarrow 1.6748$ train loss; $2.9117 \rightarrow 2.8015$ val loss). At Epoch 4, training loss dropped sharply to $1.1634$, but validation loss reversed direction, rising to $3.0857$. Over the next 4 epochs, validation loss escalated monotonically to $3.9598$—a **41.3% divergence** from the optimal point.
2. **Divergence Between Best Validation Loss and Peak Validation Accuracy:**
   - **Best Validation Loss:** Epoch 3 (`val_loss = 2.8015`, `val_acc = 55.78%`).
   - **Peak Validation Accuracy:** Epoch 8 (`val_loss = 3.9598`, `val_acc = 76.08%`).
   - *Machine Learning Explanation:* In classification neural networks, accuracy measures only the rank order of class logits (whether the correct class has the highest score), whereas cross-entropy loss measures probability calibration and penalty for confident errors. Between Epochs 4 and 8, the model became severely overconfident—assigning near-1.0 probabilities to incorrect classes on hard validation examples.
3. **EarlyStopping Integrity:**
   `EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)` and `ModelCheckpoint(save_best_only=True)` correctly restored the **Epoch 3 checkpoint**. When tested against the holdout Test split in Phase 3.4, test accuracy was `59.04%` (matching the un-overfitted Epoch 3 validation accuracy of `55.78%`, rather than the illusory `76.08%` of Epoch 8).

### 2.3 Structural Causes of the Generalization Gap
- **Absence of Batch Normalization:** The 3-block CNN has no normalization layers between Conv2D and ReLU, allowing internal activations to drift significantly across training steps.
- **Under-Regularized Convolutions:** Dropout ($0.4$) is applied exclusively to the final Dense layer; the convolutional feature extractor has zero weight decay ($L_2 = 0$) or spatial dropout.
- **Information Bottleneck (Global Average Pooling):** Compressing $(16, 16, 128)$ feature maps directly into a 128-dimensional vector strips away the spatial coordinates of finger contacts and tips.
- **Limited Photometric Augmentation:** Training augmentation was restricted to spatial transforms (rotation $\pm 14^\circ$, translation $\pm 5\%$, zoom $\pm 5\%$). No brightness, contrast, or lighting variation was applied, allowing the model to latch onto specific illumination and skin tone artifacts.

---

## 3. Class-Wise Performance Analysis (All 26 Classes)

Derived from the empirical evaluation of 5,161 holdout images in [`results/classification_report.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/classification_report.csv):

| Class | Precision | Recall | F1-Score | Support | Performance Tier | Primary Diagnosis |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **G** | **96.53%** | **99.49%** | **97.99%** | 196 | **Top Performer** | Distinct two-handed horizontal grip silhouette. |
| **I** | 86.71% | 75.00% | 80.43% | 200 | High | Upright single-finger projection. |
| **B** | 77.11% | 77.89% | 77.50% | 199 | High | Open upright palm with tucked thumb. |
| **J** | 60.80% | 100.00% | 75.62% | 197 | High Recall / Low Precision | Absorbs false positives from F and K. |
| **H** | 58.53% | 100.00% | 73.84% | 199 | High Recall / Low Precision | Absorbs false positives from M and T. |
| **Y** | 80.75% | 65.00% | 72.02% | 200 | Moderate | Distinct thumb-and-pinky spread. |
| **A** | 62.27% | 85.00% | 71.88% | 200 | Moderate | Closed fist with upright thumb. |
| **O** | 94.26% | 57.79% | 71.65% | 199 | High Precision / Low Recall | Conservative circular hand contour. |
| **K** | 64.83% | 79.27% | 71.33% | 193 | Moderate | Two-finger upright V with thumb. |
| **C** | 79.38% | 63.50% | 70.56% | 200 | Moderate | Curved C-arc contour. |
| **Q** | 91.15% | 52.28% | 66.45% | 197 | High Precision / Low Recall | Downward pointing thumb-index pair. |
| **D** | 63.59% | 68.95% | 66.16% | 190 | Moderate | Upright index with circular loop. |
| **N** | 47.48% | 100.00% | 64.39% | 198 | High Recall / Low Precision | Severe false positive sink (219 errors). |
| **U** | 68.82% | 58.79% | 63.41% | 199 | Moderate | Parallel two-finger upright projection. |
| **M** | 78.05% | 48.00% | 59.44% | 200 | Moderate | Often confused with N (three vs two fingers). |
| **V** | 59.06% | 50.50% | 54.45% | 200 | Moderate | Two-finger spread; confused with X. |
| **L** | 45.07% | 68.50% | 54.37% | 200 | Moderate | L-shape; high false positives from S. |
| **P** | 48.23% | 54.50% | 51.17% | 200 | Moderate | Downward K-shape contour. |
| **R** | 50.00% | 50.76% | 50.38% | 197 | Moderate | Crossed fingers; confused with T. |
| **E** | 32.65% | 64.32% | 43.32% | 199 | Low Precision | **Massive false positive sink (264 errors).** |
| **T** | 41.94% | 39.39% | 40.62% | 198 | Low | Closed fist with thumb between fingers; confused with S. |
| **X** | 32.30% | 26.00% | 28.81% | 200 | **Severe Deficit** | Hooked index finger contour. |
| **S** | 29.24% | 25.00% | 26.95% | 200 | **Severe Deficit** | Closed fist with thumb over fingers. |
| **Z** | **100.00%** | **12.50%** | **22.22%** | 200 | **Severe Deficit** | Static representation of dynamic sign; 87.5% missed. |
| **F** | 29.81% | 15.50% | 20.39% | 200 | **Severe Deficit** | Thumb-index touch with 3 spread fingers. |
| **W** | **0.00%** | **0.00%** | **0.00%** | 200 | **Complete Failure** | **Zero true positives across entire test split.** |

---

## 4. Confusion Matrix Analysis & Morphological Error Patterns

Empirical inspection of [`results/test_predictions.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/test_predictions.csv) reveals the exact error clusters:

### 4.1 Top 15 Most Frequent Confusion Pairs

| Rank | True Class | Misclassified As | Error Count | % of True Class | Visual / Morphological Hypothesis |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **T** | **S** | **69** | **34.8%** | *Hypothesis:* Both T and S feature a clenched fist. T places the thumb tucked between the index and middle fingers, while S wraps the thumb across the front. At 128×128 downsampling, the thumb crease boundary is lost. |
| **2** | **R** | **T** | **62** | **31.5%** | *Hypothesis:* R (crossed index and middle fingers) and T (finger tucked under thumb) share compact, multi-finger overlap contours that blur together without high-frequency edge filters. |
| **3** | **M** | **N** | **52** | **26.0%** | *Hypothesis:* Classic morphological fingerspelling ambiguity: M rests three fingers on the palm, while N rests two fingers. At 128×128, counting fingers against a skin-colored palm is a notorious challenge. |
| **4** | **Z** | **E** | **50** | **25.0%** | *Hypothesis:* Static Z is captured as a flat, horizontal hand without motion. E features curled fingers. Both present an identical rectangular palm silhouette. |
| **5** | **Z** | **K** | **50** | **25.0%** | *Hypothesis:* In certain signer angles, the flat hand edge of Z resembles the diagonal two-finger branch of K. |
| **6** | **Z** | **N** | **50** | **25.0%** | *Hypothesis:* Flat horizontal palm orientation shared with two-finger resting posture of N. |
| **7** | **M** | **H** | **50** | **25.0%** | *Hypothesis:* Both M and H incorporate horizontal finger alignments across the opposite hand in Indian Sign Language. |
| **8** | **L** | **U** | **50** | **25.0%** | *Hypothesis:* Both signs share an extended upright index finger contour. |
| **9** | **I** | **V** | **50** | **25.0%** | *Hypothesis:* Vertical finger projections against open backgrounds share identical bounding box aspect ratios. |
| **10** | **Q** | **E** | **50** | **25.4%** | *Hypothesis:* Downward-curled finger loop of Q resembles the clenched fingertip profile of E. |
| **11** | **V** | **X** | **50** | **25.0%** | *Hypothesis:* Upright two-finger V vs hooked index finger X share palm angle and knuckle positions. |
| **12** | **W** | **E** | **50** | **25.0%** | *Hypothesis:* Three extended fingers in W misclassified as curled E due to lack of finger separation filters. |
| **13** | **C** | **E** | **49** | **24.5%** | *Hypothesis:* Semi-curled C arc resembles partially closed fist of E from lateral camera angles. |
| **14** | **X** | **R** | **49** | **24.5%** | *Hypothesis:* Bent index finger contour overlaps with crossed-finger silhouette. |
| **15** | **X** | **P** | **49** | **24.5%** | *Hypothesis:* Knuckle ridge and bent finger orientation match downward P pose. |

### 4.2 The "False Positive Sink" Phenotype (Classes E and N)
- **Class E Absorbs 264 False Positives:** True W (50), True Z (50), True Q (50), True C (49), True F (38), and True S (27) are erroneously mapped to E. The model defaulted to E whenever it observed a compact, indistinct palm mass.
- **Class N Absorbs 219 False Positives:** While N achieved 100% recall, its precision was only 47.48% because it absorbed True M (52), True Z (50), True F (45), True S (39), and True W (23).

### 4.3 Root-Cause Analysis for Zero-Recall Class 'W'
Class W had 200 holdout test images and achieved **0 correct predictions**:
- Predicted as: E (50), K (33), X (28), P (23), N (23), F (10), V (10), Q (10), L (9), G (4).
- *Investigation of Training Data:* Training split contains 693 images of class W (fully comparable to other classes: mean = 669.5). Class W was NOT omitted from training.
- *Root Cause:* In Indian Sign Language, W involves a specific interlocking or three-finger spread. Because GlobalAveragePooling2D averages spatial features and the CNN lacks BatchNormalization, the model failed to develop a dedicated representation for W, routing its activations into neighboring classes with broader receptive fields.

---

## 5. Dataset and Preprocessing Observations

1. **Class Distribution Across Processed Splits:**
   - **Training (17,407 total):** Minimum = 508 (Y), Maximum = 700 (A, B, C, L, M, P, U, V), Mean = 669.5 images/class.
   - **Validation (2,517 total):** Minimum = 75 (K), Maximum = 101 (J, Q, U), Mean = 96.8 images/class.
   - **Testing (5,161 total):** Minimum = 190 (D), Maximum = 200 (15 classes), Mean = 198.5 images/class.
   - *Finding:* Class sample count is remarkably uniform across all 26 classes (~70% train ratio). **Class imbalance in sample count is NOT the primary driver of poor recall.**
2. **Spatial Resolution Bottleneck (128×128):**
   - Bilinear downsampling from raw resolutions (~300×300) to 128×128 eliminates subtle skin folds, finger separations (M vs N), and thumb overlap creases (T vs S).
3. **Dynamic Gestures in a Static Dataset (J & Z):**
   - In natural Indian Sign Language, J and Z require temporal motion trajectories. In the RealSign static dataset, they are forced into static 2D keyframes. While J achieved 100% recall (due to a distinctive crossed-finger pose), Z achieved only 12.5% recall because its static flat-hand pose is indistinguishable from E, K, and N without motion.

---

## 6. Ranked Model Improvement Plan (Phase 6 Architecture)

The following 7-point improvement roadmap is prioritized by expected performance impact and implementation feasibility:

### Priority 1: Batch Normalization & Modern Convolutional Blocks
- **Problem Addressed:** Gradient instability and severe overfitting starting at Epoch 4 (validation loss exploding from 2.80 to 3.96).
- **Proposed Change:** Insert `layers.BatchNormalization()` after every `Conv2D` layer and adopt a double-conv structure per block:
  `[Conv2D -> BatchNorm -> ReLU -> Conv2D -> BatchNorm -> ReLU -> MaxPool2D]`.
- **Expected Benefit:** Stabilizes layer distributions, accelerates convergence, provides implicit regularization, and prevents early divergence.
- **Potential Downside:** Modest increase in parameter count (~180k parameters vs 113k).
- **Evaluation Method:** Validation loss trajectory across epochs on the Validation split.

### Priority 2: Expanded Data Augmentation (Photometric & Lighting)
- **Problem Addressed:** Model memorization of background colors, lighting angles, and specific signer skin tones.
- **Proposed Change:** In `training/data_pipeline.py`, add `RandomBrightness(factor=0.15)` and `RandomContrast(factor=0.15)` to the existing spatial augmentations. **Strictly maintain NO HORIZONTAL FLIP** to preserve ISL handedness.
- **Expected Benefit:** Forces convolutional filters to learn structural hand geometry and finger edges rather than ambient lighting cues.
- **Potential Downside:** Minor increase in CPU preprocessing overhead during data streaming.
- **Evaluation Method:** Validation accuracy and reduction in false-positive hubs (E and N).

### Priority 3: Input Resolution Elevation to 160×160 or 224×224
- **Problem Addressed:** Loss of fine finger count boundaries (M vs N, T vs S) at 128×128.
- **Proposed Change:** Increase `IMAGE_SIZE` from `(128, 128)` to `(160, 160)` or `(224, 224)`.
- **Expected Benefit:** Retains critical sub-pixel edge details distinguishing 2 vs 3 fingers and thumb placement.
- **Potential Downside:** Higher memory footprint; batch size may need adjustment (e.g. 32 to 16 if VRAM/RAM constrained).
- **Evaluation Method:** Specific confusion matrix error count on M $\rightarrow$ N and T $\rightarrow$ S pairs.

### Priority 4: Kernel Regularization & Spatial Dropout
- **Problem Addressed:** Unconstrained weight growth in convolutional layers leading to overconfidence.
- **Proposed Change:** Add $L_2$ weight decay (`kernel_regularizer=regularizers.l2(1e-4)`) across all convolutional kernels, and replace standard dropout with `SpatialDropout2D(0.2)` in the final conv block.
- **Expected Benefit:** Directly penalizes large weight magnitudes, flattening the loss landscape and suppressing memorization.
- **Potential Downside:** May slightly slow training accuracy gain in the initial 2 epochs.
- **Evaluation Method:** Validation loss remaining below 2.0 without upward curvature.

### Priority 5: Spatial-Preserving Classification Head
- **Problem Addressed:** `GlobalAveragePooling2D` discards where finger tips are located in the bounding box.
- **Proposed Change:** Concatenate `GlobalAveragePooling2D` and `GlobalMaxPooling2D` (`layers.concatenate([avg_pool, max_pool])`), followed by `Dense(256) -> BatchNorm -> Dropout(0.5)`.
- **Expected Benefit:** Max-pooling captures peak activation (fingertips), while average-pooling captures overall palm mass, resolving asymmetric signs (L, U, I, V).
- **Potential Downside:** Increases dense layer parameter count.
- **Evaluation Method:** Recall on previously zero-recall class W and low-recall classes X and S.

### Priority 6: Label Smoothing & Loss Calibration
- **Problem Addressed:** Cross-entropy with hard integer targets drives logits to infinity, causing validation loss explosion on difficult edge cases.
- **Proposed Change:** Utilize `CategoricalCrossentropy(label_smoothing=0.1)` (with one-hot encoding) instead of hard sparse cross-entropy.
- **Expected Benefit:** Prevents the network from becoming overconfident, producing well-calibrated confidence scores that align with actual prediction accuracy.
- **Potential Downside:** Maximum reported confidence scores will rarely exceed 0.90–0.95.
- **Evaluation Method:** Brier score and alignment between confidence percentage and accuracy in webcam mode.

### Priority 7: Cosine Decay Learning Rate Schedule
- **Problem Addressed:** Abrupt step-down in learning rate (`ReduceLROnPlateau` with patience=3) came too late (Epoch 7) after the model had already overfitted.
- **Proposed Change:** Replace step reduction with a smooth `CosineDecay` schedule starting from $\eta = 5 \times 10^{-4}$ with a 2-epoch linear warmup.
- **Expected Benefit:** Allows smooth exploration of the parameter space in early epochs and gentle annealing into wide, flat minima.
- **Potential Downside:** Fixed epoch schedule requires predetermined epoch count (e.g. 20 epochs).
- **Evaluation Method:** Continuous loss curve smoothness on Validation split.

---

## 7. Data Leakage & Evaluation Safeguards

To maintain strict scientific and academic validity throughout Phase 6:
1. **Independent Holdout Protection:** The `dataset/processed/Testing/` split (5,161 images) **must remain strictly sealed**. No model selection, hyperparameter tuning, or early stopping decisions will reference test data.
2. **Validation-Only Selection:** All architectural comparisons, learning rate experiments, and checkpoint selections must be governed exclusively by `dataset/processed/Validation/` (2,517 images).
3. **Immutable Class Mapping:** The 26-class mapping (`training/label_classes.json`) from A (index 0) to Z (index 25) remains strictly frozen.
4. **Final Single-Pass Benchmark:** The independent test set will be evaluated exactly once on the final champion model candidate.

---

## 8. Summary of Baseline Metrics & Target Goals

| Metric | Phase 3 Baseline (Current) | Phase 6 Architectural Target |
| :--- | :---: | :---: |
| **Independent Test Accuracy** | `59.04%` | **$\ge 75.00\%$** |
| **Macro F1-Score** | `56.74%` | **$\ge 72.00\%$** |
| **Best Validation Loss** | `2.8015` | **$< 1.5000$** |
| **Epoch of Overfitting** | Epoch 4 | **No divergence before Epoch 15** |
| **Zero-Recall Classes** | 1 (Class W: `0.0%`) | **0 (All classes $> 40\%$ recall)** |
| **Classes with F1 $< 30\%$** | 5 (W, F, Z, S, X) | **$\le 1$ (Dynamic Z limitation)** |
| **Batch Normalization** | None | **In all Conv blocks** |
| **Input Resolution** | 128 × 128 | **160 × 160 or 224 × 224** |
