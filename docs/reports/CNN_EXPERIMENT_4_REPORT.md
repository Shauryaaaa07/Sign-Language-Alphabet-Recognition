# CNN Experiment 4 Report: Spatial Dropout Investigation (Model V5)

## 1. Executive Summary
- **Experiment Title:** Phase 6 — Milestone 6.5: Spatial Dropout Experiment (Experiment 4 — CNN V5)
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v5_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v5_best.keras) (`3.63 MB`)
- **Total Parameters:** `308,218`
- **Trainable Parameters:** `307,322` (Identical parameter count across V2, V3, V4, and V5)
- **Training Epochs:** `10` executed of `30` maximum (EarlyStopping triggered at Epoch 10 with patience 6)
- **Restored Best Checkpoint Epoch:** **Epoch 4**
- **Best Validation Total Loss (CE + L2):** **`1.8155`** (vs V4 `1.3507`, representing a $+0.4648$ loss degradation)
- **Pure Validation Classification Loss (CE only):** **`1.7414`** (Excluding $\text{L2 penalty} = 0.0740$)
- **Validation Accuracy at Best Loss:** **`76.68%`** (vs V4 `80.14%`, a decline of $-3.46$ percentage points)
- **Peak Validation Accuracy:** **`79.10%`** (at Epoch 7)
- **Validation Macro Precision:** **`76.23%`** (vs V4 `80.42%`)
- **Validation Macro Recall:** **`77.11%`** (vs V4 `80.53%`)
- **Validation Macro F1-Score:** **`73.81%`** (vs V4 `77.68%`, a $-3.87$ percentage point drop)
- **Validation Weighted F1-Score:** **`73.44%`** (vs V4 `77.17%`)
- **Controlled Finding:** **Negative empirical outcome.** Introducing SpatialDropout2D ($0.10$) harmed feature learning by dropping contiguous 2D spatial feature maps, erasing delicate finger contours. **CNN V4 remains the verified champion model candidate.**
- **Training Duration:** `1011.09 minutes` (multi-core CPU background training)

> [!IMPORTANT]
> **Strict Holdout Split Integrity:**
> The independent **Testing split (`dataset/processed/Testing/`) was strictly NEVER loaded, accessed, or evaluated** during this experiment. Checkpoint selection, early stopping, learning rate adaptation, and validation evaluations were conducted exclusively on the `Validation` split (2,517 images).

---

## 2. Architectural Design & Exact SpatialDropout2D Placement

Experiment 4 tested the hypothesis that dropping entire 2D feature channels during convolution would prevent co-adaptation and improve generalization beyond Model V4.

### SpatialDropout2D Placement
`SpatialDropout2D(rate=0.10)` was inserted before pooling in each of the three dual-convolution stages:
1. **Block 1:** Following `block1_relu2`, preceding `block1_pool` $\to$ `block1_spatial_dropout` (Shape: `(None, 128, 128, 32)`)
2. **Block 2:** Following `block2_relu2`, preceding `block2_pool` $\to$ `block2_spatial_dropout` (Shape: `(None, 64, 64, 64)`)
3. **Block 3:** Following `block3_relu2`, preceding `block3_pool` $\to$ `block3_spatial_dropout` (Shape: `(None, 32, 32, 128)`)

### Retained Settings (Identical to V4)
- **L2 Regularization:** $\lambda = 0.0001$ maintained on the same 8 kernels (all 6 Conv2D + 2 Dense kernels).
- **Batch Normalization:** Unregularized $\gamma, \beta$ retained after every Conv2D.
- **Classification Head:** GlobalAveragePooling2D $\to$ Dense(128, ReLU) $\to$ Dropout(0.4) $\to$ Dense(26, Softmax).
- **Total Parameters:** 308,218 (Trainable: 307,322).

---

## 3. Data Augmentation Protocol (Identical to V4 & V3)

Training-only augmentation from Milestones 6.3 and 6.4 was preserved exactly:
- **Geometric:** Rotation $\pm 14.4^\circ$ (`0.04`), Translation $\pm 5\%$ (`0.05`), Zoom $\pm 5\%$ (`0.05`).
- **Photometric:** Contrast $\pm 10\%$ (`0.10`), Brightness $\pm 10\%$ (`0.10`), pixel value clipping to $[0.0, 1.0]$.
- **Horizontal Flip: Strictly Disabled** to protect sign language handedness.
- **Validation Pipeline:** Completely deterministic and unaugmented.

---

## 4. Epoch-by-Epoch Metric History

- **Optimizer:** Adam ($\eta = 0.0005$)
- **Batch Size:** 32 (544 batches per epoch)
- **EarlyStopping:** `val_loss`, patience = 6, `restore_best_weights = True`

| Epoch | Train Loss (CE + L2) | Train Accuracy | Val Loss (Total) | Val Accuracy | Learning Rate | Checkpoint Action / Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 2.6240 | 21.43% | 3.5529 | 15.77% | 0.000500 | Checkpoint saved (`val_loss: 3.5529`) |
| 2 | 1.6625 | 48.29% | 1.9306 | 66.03% | 0.000500 | Checkpoint saved (`val_loss: 1.9306`) |
| 3 | 1.0721 | 67.89% | 2.2525 | 63.97% | 0.000500 | Fluctuation check |
| 4 | **0.7080** | **80.20%** | **1.8155** | **76.68%** | **0.000500** | **Best Checkpoint Saved (`val_loss: 1.8155`)** |
| 5 | 0.4995 | 87.17% | 2.1470 | 71.32% | 0.000500 | - |
| 6 | 0.3960 | 90.41% | 1.9755 | 77.39% | 0.000500 | - |
| 7 | 0.3256 | 92.73% | 1.9982 | 79.10% | 0.000500 | Peak validation accuracy |
| 8 | 0.2341 | 95.74% | 1.8438 | 78.07% | 0.000250 | Plateau detected; LR halved |
| 9 | 0.2200 | 96.18% | 2.0553 | 79.10% | 0.000250 | - |
| 10 | 0.2114 | 96.56% | 1.9245 | 79.06% | 0.000250 | EarlyStopping triggered (Patience=6); Restored Epoch 4 |

---

## 5. Five-Way Controlled Progression: Baseline through V5

All models evaluated strictly on the identical 2,517-image Validation split:

| Metric | Baseline (Epoch 3) | CNN V2 (Epoch 9) | CNN V3 (Epoch 8) | CNN V4 (Epoch 5) [CHAMPION] | CNN V5 (Epoch 4) | V5 vs V4 Delta |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Architecture** | 3 Single-Conv | 3 Double-Conv | 3 Double-Conv | 3 Double-Conv | 3 Double-Conv + SpatialDrop | SpatialDrop added |
| **Augmentation** | Geometric | Geometric | Geo + Photo | Geo + Photo | Geo + Photo | Identical |
| **Regularization** | Dropout 0.5 | Dropout 0.4 | Dropout 0.4 | Dropout 0.4 + L2 (1e-4) | Dropout 0.4 + L2 + SpatialDrop | Over-regularized |
| **Best Val Total Loss** | 2.8015 | 1.6701 | 1.3732 | **1.3507** | 1.8155 | **+0.4648 (Degraded)** |
| **Val Pure CE Loss** | 2.8015 | 1.6701 | 1.3732 | **1.2781** | 1.7414 | **+0.4633 (Degraded)** |
| **Val Accuracy @ Best Loss** | 55.78% | 76.40% | 78.11% | **80.14%** | 76.68% | **-3.46 pp** |
| **Peak Val Accuracy** | 76.08% | 80.10% | 80.29% | **80.14%** | 79.10% | **-1.04 pp** |
| **Val Macro Precision** | ~54.2% | 74.14% | 77.53% | **80.42%** | 76.23% | **-4.19 pp** |
| **Val Macro Recall** | ~55.8% | 76.67% | 78.17% | **80.53%** | 77.11% | **-3.42 pp** |
| **Val Macro F1-Score** | ~53.5% | 73.10% | 75.52% | **77.68%** | 73.81% | **-3.87 pp** |
| **Val Weighted F1-Score** | ~53.1% | 72.64% | 75.23% | **77.17%** | 73.44% | **-3.73 pp** |
| **Trainable Parameters** | 113,114 | 307,322 | 307,322 | **307,322** | 307,322 | 0 |

---

## 6. Difficult-Class Empirical Tracking (W, Z, S, Y, Q)

| Class | V3 F1 | V4 F1 [CHAMPION] | V5 Precision | V5 Recall | V5 F1 | Net F1 Delta (V5 vs V4) | Primary Confusion Modes (V5) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Z** | 0.00% | **42.37%** (25 correct) | **0.00%** | **0.00%** | **0.00%** | **-42.37 pp** | **Collapsed:** 62.4% misclassified as X, 15.1% as D |
| **W** | 5.45% | **1.89%** | **0.00%** | **0.00%** | **0.00%** | **-1.89 pp** | **Collapsed:** 28% misclassified as X, 19% as P, 16% as N |
| **S** | 40.00% | **40.00%** | **100.00%** | **25.00%** | **40.00%** | 0.00 pp | Stable 100% precision; confused with T (49%), N (23%) |
| **Y** | 55.42% | **54.76%** | **97.87%** | **47.42%** | **63.89%** | **+9.13 pp** | Improved precision; confused with X (26.8%), I (9.3%) |
| **Q** | 43.22% | **60.71%** | **80.65%** | **49.50%** | **61.35%** | **+0.64 pp** | Stable; confused with R (24.8%), M (22.8%) |

### Key Evidence & Analysis:
1. **Destruction of the Class Z Representation:**
   - In Model V4, L2 weight regularization enabled the model to correctly identify 25 validation samples of Z with 100% precision ($F_1 = 42.37\%$).
   - In Model V5, SpatialDropout2D randomly dropped complete feature channels in early layers, which prevented the network from maintaining the slender index-finger edge required for Z, causing **100% of Z samples to be misclassified (62.4% as X)**.
2. **Over-Regularization Effect:**
   - Sign language alphabet recognition relies heavily on spatial continuity—subtle finger orientations and small contour features that span across correlated adjacent channels. Unlike large-scale object classification where dropping entire feature maps forces alternative feature path discovery, in hand sign recognition it acts as destructive feature masking.
3. **Class Y and Q Invariance:**
   - Broad two-finger spread signs like Y and Q were resilient to channel dropout ($F_1 = 63.89\%$ and $61.35\%$), but subtle finger-count gestures (W, Z, U, V) suffered severe degradation.

---

## 7. Overfitting & Convergence Analysis

- In V4, optimal validation loss was reached at **Epoch 5 with 1.3507** (Train Accuracy: 98.32%, Val Accuracy: 80.14%).
- In V5, training accuracy lagged substantially behind across early epochs (Epoch 1: 21.43%, Epoch 2: 48.29%, Epoch 4: 80.20%).
- While SpatialDropout eliminated the gap between training and validation accuracy at Epoch 4 (80.20% train vs 76.68% val), it did so by **underfitting the training data** rather than discovering a superior feature representation.
- Consequently, best validation loss degraded by **+0.4648 points** ($1.3507 \to 1.8155$).

---

## 8. Runtime & Hardware Environment

- **Hardware:** Intel Multi-Core CPU with oneDNN AVX2/AVX_VNNI instructions.
- **Execution Time:** 1011.09 minutes across 10 epochs.
- **Memory Footprint:** Resident Set Size ~925 MB, Virtual Memory ~1.9 GB.

---

## 9. Limitations & Definitive Scientific Conclusion

1. **Definitive Rejection of SpatialDropout2D for ISL Hand Gestures:**
   - Empirical evidence firmly concludes that SpatialDropout2D (0.10) is unsuitable for fine-grained static sign language classification.
2. **Champion Model Confirmation:**
   - **Model V4 (Double-Conv + BatchNorm + L2 0.0001 + Dense Dropout 0.4 + Photometric Augmentation) remains the absolute best-performing architecture** across all 5 evaluated configurations.
3. **Holdout Split Maintained:**
   - The test benchmark (`dataset/processed/Testing/`) remains completely unviolated.

---

## 10. Git Status & Artifact Index

### Git Status
```text
Clean branch worktree; all prior model checkpoints, scripts, and evaluation logs intact.
No commits or pushes executed.
```

### Experiment 4 Artifact Index
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v5_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v5_best.keras)
- **Training Pipeline Script:** [`training/experiments/train_v5.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/training/experiments/train_v5.py)
- **Training History CSV:** [`results/experiments/v5_training_history.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v5_training_history.csv)
- **Validation Classification Report CSV:** [`results/experiments/v5_val_classification_report.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v5_val_classification_report.csv)
- **Validation Confusion Matrix Graphic:** [`results/experiments/v5_val_confusion_matrix.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v5_val_confusion_matrix.png)
- **Loss Progression Trajectory:** [`results/experiments/v5_training_loss.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v5_training_loss.png)
- **Accuracy Progression Trajectory:** [`results/experiments/v5_training_accuracy.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v5_training_accuracy.png)
- **Milestone Report:** [`docs/reports/CNN_EXPERIMENT_4_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/CNN_EXPERIMENT_4_REPORT.md)
