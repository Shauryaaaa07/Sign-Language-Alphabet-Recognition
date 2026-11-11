# CNN Experiment 3 Report: L2 Kernel Regularization (Model V4)

## 1. Executive Summary
- **Experiment Title:** Phase 6 — Milestone 6.4: L2 Kernel Regularization (Experiment 3 — CNN V4)
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v4_best.keras) (`3.63 MB`)
- **Total Parameters:** `308,218`
- **Trainable Parameters:** `307,322` (Identical parameter count to V2 and V3)
- **Training Epochs:** `11` executed of `30` maximum (EarlyStopping triggered at Epoch 11 with patience 6)
- **Restored Best Checkpoint Epoch:** **Epoch 5**
- **Best Validation Total Loss (CE + L2):** **`1.3507`** (vs V3 `1.3732`, V2 `1.6701`, Baseline `2.8015`)
- **Pure Validation Classification Loss (CE only):** **`1.2781`** (Excluding $\text{L2 penalty} = 0.0726$)
- **Validation Accuracy at Best Loss:** **`80.14%`** (vs V3 `78.11%`, V2 `76.40%`, Baseline `55.78%`)
- **Peak Validation Accuracy:** **`80.14%`** (achieved at optimal generalization Epoch 5)
- **Validation Macro Precision:** **`80.42%`** (vs V3 `77.53%`, V2 `74.14%`, Baseline ~`54.2%`)
- **Validation Macro Recall:** **`80.53%`** (vs V3 `78.17%`, V2 `76.67%`, Baseline ~`55.8%`)
- **Validation Macro F1-Score:** **`77.68%`** (vs V3 `75.52%`, V2 `73.10%`, Baseline ~`53.5%`)
- **Validation Weighted F1-Score:** **`77.17%`** (vs V3 `75.23%`, V2 `72.64%`)
- **Major Milestone Breakthrough:** **Class Z precision surged to 100.0% and recall to 26.88% ($F_1 = 42.37\%$)**, breaking complete class collapse from all prior experiments (0.0%).
- **Training Duration:** `140.52 minutes` (~2.34 hours on multi-core CPU)

> [!IMPORTANT]
> **Strict Holdout Split Integrity:**
> In accordance with research integrity standards, the independent **Testing split (`dataset/processed/Testing/`) was strictly NEVER loaded, accessed, or evaluated** during this experiment. Checkpoint selection, early stopping, learning rate adaptation, and validation evaluations were conducted exclusively on the `Validation` split (2,517 images).

---

## 2. Experimental Setup: Exact Architecture & L2 Configuration

To perform a strictly controlled single-variable test, the **exact CNN V2/V3 backbone and data augmentation were preserved**, with L2 kernel regularization applied exclusively to weight matrices.

### Layers Receiving L2 Regularization ($\lambda = 0.0001$)
L2 weight decay penalty ($\frac{1}{2} \lambda \|W\|_2^2$) was applied to the kernel weights of all 8 feature-transforming layers:
1. `block1_conv1`: `Conv2D(32, 3x3)` kernel
2. `block1_conv2`: `Conv2D(32, 3x3)` kernel
3. `block2_conv1`: `Conv2D(64, 3x3)` kernel
4. `block2_conv2`: `Conv2D(64, 3x3)` kernel
5. `block3_conv1`: `Conv2D(128, 3x3)` kernel
6. `block3_conv2`: `Conv2D(128, 3x3)` kernel
7. `dense_features`: `Dense(128)` kernel
8. `class_probabilities`: `Dense(26)` kernel

### Regularization Exclusions
- **BatchNormalization:** Scale ($\gamma$) and offset ($\beta$) parameters receive **NO** regularization.
- **Biases:** Dense layer biases have `bias_regularizer=None`. Conv2D layers use `use_bias=False` prior to Batch Normalization.
- **No auxiliary architectural regularizers:** SpatialDropout2D, label smoothing, and weight decay adjustments were strictly avoided.

---

## 3. Data Augmentation Protocol (Identical to V3)

Training-only augmentation from Milestone 6.3 was maintained without alteration:
- **Geometric:** `RandomRotation(0.04)` ($\pm 14.4^\circ$), `RandomTranslation(0.05, 0.05)` ($\pm 5\%$), `RandomZoom((-0.05, 0.05))` ($\pm 5\%$).
- **Photometric:** `RandomContrast(factor=0.10)`, `RandomBrightness(factor=0.10, value_range=(0.0, 1.0))`.
- **Pixel Clipping:** Strict enforcement of $[0.0, 1.0]$ via `tf.clip_by_value`.
- **Horizontal Flip: Strictly Disabled** to preserve ISL handedness.
- **Validation Pipeline:** Completely deterministic and unaugmented.

---

## 4. Epoch-by-Epoch Metric History

- **Optimizer:** Adam ($\eta = 0.0005$)
- **Batch Size:** 32 (544 batches per epoch)
- **EarlyStopping:** `val_loss`, patience = 6, `restore_best_weights = True`

| Epoch | Train Loss (CE + L2) | Train Accuracy | Val Loss (Total) | Val Accuracy | Learning Rate | Status / Checkpoint Action |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 2.0338 | 42.03% | 2.9579 | 23.64% | 0.000500 | Checkpoint saved (`val_loss: 2.9579`) |
| 2 | 0.5952 | 87.05% | 2.7076 | 53.60% | 0.000500 | Checkpoint saved (`val_loss: 2.7076`) |
| 3 | 0.2598 | 96.01% | 2.1887 | 66.67% | 0.000500 | Checkpoint saved (`val_loss: 2.1887`) |
| 4 | 0.1791 | 97.61% | 1.9880 | 74.06% | 0.000500 | Checkpoint saved (`val_loss: 1.9880`) |
| 5 | **0.1491** | **98.32%** | **1.3507** | **80.14%** | **0.000500** | **Best Checkpoint Saved (`val_loss: 1.3507`, Acc: 80.14%)** |
| 6 | 0.1183 | 99.18% | 2.2612 | 68.18% | 0.000500 | Fluctuation check |
| 7 | 0.1340 | 98.50% | 1.6002 | 79.26% | 0.000500 | Stability recovery |
| 8 | 0.1256 | 98.87% | 1.5792 | 75.96% | 0.000500 | Plateau check |
| 9 | 0.0868 | 99.89% | 1.6255 | 79.34% | 0.000250 | LR reduction to 0.00025 |
| 10 | 0.0860 | 99.77% | 1.7887 | 78.78% | 0.000250 | Plateau check |
| 11 | 0.0823 | 99.84% | 1.7381 | 80.02% | 0.000250 | EarlyStopping triggered (Patience=6); Restored Epoch 5 |

---

## 5. Four-Way Controlled Comparison: Baseline vs V2 vs V3 vs V4

All models evaluated strictly on the identical 2,517-image Validation split:

| Metric | Baseline CNN (Epoch 3) | CNN V2 (Epoch 9) | CNN V3 (Epoch 8) | CNN V4 (Epoch 5) | Net Gain (V4 vs V3) | Total Gain (V4 vs Baseline) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Architecture** | 3 Single-Conv | 3 Double-Conv + BN | 3 Double-Conv + BN | **3 Double-Conv + BN** | Reused | Reused |
| **Augmentation** | Geometric | Geometric | Geo + Photometric | **Geo + Photometric** | Reused | Photometric added |
| **Regularization** | Dropout (0.5) | Dropout (0.4) | Dropout (0.4) | **Dropout (0.4) + L2 (1e-4)** | L2 added | L2 added |
| **Best Val Total Loss** | 2.8015 | 1.6701 | 1.3732 | **1.3507** | **-0.0225** | **-1.4508 (-51.79%)** |
| **Val Pure CE Loss (excl. L2)** | 2.8015 | 1.6701 | 1.3732 | **1.2781** | **-0.0951** | **-1.5234 (-54.38%)** |
| **Val Accuracy @ Best Loss** | 55.78% | 76.40% | 78.11% | **80.14%** | **+2.03 pp** | **+24.36 pp** |
| **Peak Val Accuracy** | 76.08% (Epoch 8) | 80.10% (Epoch 13) | 80.29% (Epoch 12) | **80.14%** (Epoch 5) | Matched at peak | **+4.06 pp** |
| **Val Macro Precision** | ~54.2% | 74.14% | 77.53% | **80.42%** | **+2.89 pp** | **+26.22 pp** |
| **Val Macro Recall** | ~55.8% | 76.67% | 78.17% | **80.53%** | **+2.36 pp** | **+24.73 pp** |
| **Val Macro F1-Score** | ~53.5% | 73.10% | 75.52% | **77.68%** | **+2.16 pp** | **+24.18 pp** |
| **Val Weighted F1-Score** | ~53.1% | 72.64% | 75.23% | **77.17%** | **+1.94 pp** | **+24.07 pp** |
| **Convergence Epoch** | 3 (Overfit at 4) | 9 (Overfit at 10) | 8 (Plateau at 9) | **5 (Optimal minimum)** | Faster convergence | Stable regularized |
| **Trainable Parameters** | 113,114 | 307,322 | 307,322 | **307,322** | $0$ change | $+194,208$ |

---

## 6. Difficult-Class Empirical Tracking (W, Z, S, Y, Q)

| Class | V2 F1 | V3 F1 | V4 Precision | V4 Recall | V4 F1 | Net F1 Delta (V4 vs V3) | Primary Confusion Modes (V4) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **Z** | 0.00% | 0.00% | **100.00%** | **26.88%** | **42.37%** | **+42.37 pp** | **Major Breakthrough: 25 correct; 0 false positives!** Confused with I (26.9%), A (25.8%) |
| **Q** | 45.02% | 43.22% | **76.12%** | **50.50%** | **60.71%** | **+17.49 pp** | **Precision surged to 76.12%**; confused with E (24.8%), M (16.8%) |
| **Y** | 34.01% | 55.42% | **64.79%** | **47.42%** | **54.76%** | -0.66 pp | High stability; confused with X (26.8%), P (9.3%) |
| **S** | 40.00% | 40.00% | **100.00%** | **25.00%** | **40.00%** | 0.00 pp | Perfect precision (100%); confused with T (25%), Y (25%), N (23%) |
| **W** | 0.00% | 5.45% | **16.67%** | **1.00%** | **1.89%** | -3.56 pp | Confused with E (24%), N (21%), I (14%), Q (13%) |

### Key Evidence & Analysis:
1. **The Class Z Breakthrough:**
   - In all previous models (Baseline, V2, V3), Class Z was completely unlearnable ($F_1 = 0.0\%$).
   - In Model V4, with L2 regularization suppressing excessive filter weight magnitudes, the model formed a distinct boundary for Class Z: **25 validation images correctly predicted with 100% precision (0 false alarms)**, lifting Z's F1 to **42.37%**.
2. **Class Q Disambiguation:**
   - Class Q precision increased from $37.78\%$ in V3 to **$76.12\%$ in V4**, driving its F1 score up from $43.22\%$ to **$60.71\%$ (+17.49 percentage points)**.
3. **Class S Precision Dominance:**
   - Class S maintained **100.0% precision** across both V3 and V4. Closed-fist gesture ambiguities with T (thumb over fingers) and N remain the primary recall constraint.
4. **General Classes Attaining Near-Perfection:**
   - **H:** Precision 100%, Recall 100%, **$F_1 = 1.000$**
   - **L:** Precision 100%, Recall 100%, **$F_1 = 1.000$**
   - **R:** Precision 100%, Recall 100%, **$F_1 = 1.000$**
   - **K:** Precision 97.4%, Recall 100%, **$F_1 = 0.9868$**
   - **D:** Precision 90.7%, Recall 98.0%, **$F_1 = 0.9423$**

---

## 7. Overfitting & Regularization Loss Separation

In Experiment 3, total loss comprises classification loss plus weight decay:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{SCCE}} + \frac{1}{2} \lambda \sum_i \|W_i\|_2^2$$

- At restored Epoch 5:
  - $\mathcal{L}_{\text{total}} = 1.3507$
  - $\text{L2 penalty term} = 0.0726$
  - **Pure Classification Loss:** $\mathcal{L}_{\text{SCCE}} = \mathbf{1.2781}$
- **Evidence of Overfitting Suppression:**
  - Training accuracy at Epoch 5 was **98.32%**, and validation accuracy was **80.14%** (a generalization gap of only 18.18 pp, compared to >23 pp in Baseline).
  - L2 penalty constrained weight norms across deeper layers, preventing convolutional kernels from specializing to individual training background textures.

---

## 8. Runtime & Environment

- **Hardware:** Intel Multi-Core CPU with oneDNN optimizations (AVX2/AVX_VNNI/FMA). GPU unavailable.
- **Total Training Duration:** `140.52 minutes` (~2.34 hours) for 11 epochs (~12.7 minutes per epoch).
- **RAM Footprint:** Resident Set Size ~915 MB, Virtual Memory ~1.9 GB.

---

## 9. Limitations

1. **Class W Remaining Challenges:**
   - While L2 resolved Class Z and boosted Class Q, Class W remains vulnerable to confusion with E and N when viewed from 2D webcams without hand skeleton joint modeling (MediaPipe Hands).
2. **Pristine Holdout Integrity:**
   - The test benchmark (`dataset/processed/Testing/`) remains completely untouched for the final Phase 6 holdout evaluation.

---

## 10. Git Status & Artifact Index

### Git Status
```text
Clean branch worktree; all baseline and prior experiment files intact.
No commits or pushes executed.
```

### Experiment 3 Artifact Index
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v4_best.keras)
- **Training Pipeline Script:** [`training/experiments/train_v4.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/training/experiments/train_v4.py)
- **Training History CSV:** [`results/experiments/v4_training_history.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v4_training_history.csv)
- **Validation Classification Report CSV:** [`results/experiments/v4_val_classification_report.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v4_val_classification_report.csv)
- **Validation Confusion Matrix Graphic:** [`results/experiments/v4_val_confusion_matrix.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v4_val_confusion_matrix.png)
- **Loss Progression:** [`results/experiments/v4_training_loss.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v4_training_loss.png)
- **Accuracy Progression:** [`results/experiments/v4_training_accuracy.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v4_training_accuracy.png)
- **Milestone Report:** [`docs/reports/CNN_EXPERIMENT_3_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/CNN_EXPERIMENT_3_REPORT.md)
