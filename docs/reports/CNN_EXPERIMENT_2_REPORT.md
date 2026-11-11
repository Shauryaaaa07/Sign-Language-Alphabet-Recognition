# CNN Experiment 2 Report: Photometric Data Augmentation (Model V3)

## 1. Executive Summary
- **Experiment Title:** Phase 6 — Milestone 6.3: Photometric Data Augmentation (Experiment 2 — CNN V3)
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v3_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v3_best.keras) (`3.63 MB`)
- **Total Parameters:** `308,218`
- **Trainable Parameters:** `307,322` (Identical parameter count to V2)
- **Training Epochs:** `14` executed of `30` maximum (EarlyStopping triggered at Epoch 14 with patience 6)
- **Restored Best Checkpoint Epoch:** **Epoch 8**
- **Best Validation Loss:** **`1.3732`** (Improvement of **-0.2969** vs V2 `1.6701`, and **-1.4283 (-50.98%)** vs Baseline `2.8015`)
- **Validation Accuracy at Best Loss:** **`78.11%`** (vs V2 `76.40%` and Baseline `55.78%`)
- **Peak Validation Accuracy:** **`80.29%`** (at Epoch 12)
- **Validation Macro Precision:** **`77.53%`** (vs V2 `74.14%` and Baseline ~`54.2%`)
- **Validation Macro Recall:** **`78.17%`** (vs V2 `76.67%` and Baseline ~`55.8%`)
- **Validation Macro F1-Score:** **`75.52%`** (vs V2 `73.10%` and Baseline ~`53.5%`)
- **Validation Weighted F1-Score:** **`75.23%`** (vs V2 `72.64%`)
- **Training Duration:** `196.68 minutes` (~3.28 hours on multi-core CPU)

> [!IMPORTANT]
> **Strict Holdout Split Integrity:**
> The independent **Testing split (`dataset/processed/Testing/`) was strictly NEVER loaded, accessed, or evaluated** during this experiment. Model selection, learning rate decay, early stopping, and validation evaluations were performed exclusively on the `Validation` split (2,517 images).

---

## 2. Exact Architecture Reused

To isolate the empirical effect of photometric augmentation, the **CNN V2 architecture was reused without architectural modifications**:
- **Source:** [`training/experiments/model_v2.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/training/experiments/model_v2.py) (`build_model_v2`)
- **No changes** to convolutional layer counts, filter depths, batch normalization, pooling, dense units, or dropout rate (0.4).
- **No L2 regularization** or SpatialDropout introduced.

```text
ISL_Alphabet_CNN_V2 Backbone (Reused in V3):
  Input: (None, 128, 128, 3)
  ├── Block 1:
  │   ├── Conv2D(32, 3x3, same) + BatchNorm + ReLU
  │   ├── Conv2D(32, 3x3, same) + BatchNorm + ReLU
  │   └── MaxPooling2D(2x2)
  ├── Block 2:
  │   ├── Conv2D(64, 3x3, same) + BatchNorm + ReLU
  │   ├── Conv2D(64, 3x3, same) + BatchNorm + ReLU
  │   └── MaxPooling2D(2x2)
  ├── Block 3:
  │   ├── Conv2D(128, 3x3, same) + BatchNorm + ReLU
  │   ├── Conv2D(128, 3x3, same) + BatchNorm + ReLU
  │   └── MaxPooling2D(2x2)
  └── Head:
      ├── GlobalAveragePooling2D
      ├── Dense(128, ReLU)
      ├── Dropout(0.4)
      └── Dense(26, Softmax)
```

---

## 3. Augmentation Configuration & API Compatibility

### Verified Keras & TensorFlow APIs
- **TensorFlow:** `2.16.2` | **Keras:** `3.15.1`
- `keras.layers.RandomBrightness` and `keras.layers.RandomContrast` were verified and confirmed natively compatible.

### Augmentation Pipeline Breakdown
1. **Geometric Augmentations (Preserved from Baseline & V2):**
   - `RandomRotation(factor=0.04, seed=42)`: Rotation range $\pm 14.4^\circ$.
   - `RandomTranslation(height_factor=0.05, width_factor=0.05, seed=42)`: Horizontal and vertical shift $\pm 5\%$.
   - `RandomZoom(height_factor=(-0.05, 0.05), width_factor=(-0.05, 0.05), seed=42)`: Zoom in/out $\pm 5\%$.
   - **Horizontal Flip: Strictly Disabled** (ISL letters encode asymmetric hand configurations).
2. **Photometric Augmentations (Added in Experiment 2):**
   - `RandomContrast(factor=0.10, seed=42)`: Contrast variation within $\pm 10\%$.
   - `RandomBrightness(factor=0.10, value_range=(0.0, 1.0), seed=42)`: Brightness shift within $\pm 10\%$.
   - `tf.clip_by_value(augmented, 0.0, 1.0)`: Guaranteed enforcement of valid normalized pixel values.
3. **Inference & Validation Safety:**
   - Augmentation was mapped strictly to `dataset/processed/Training` (`is_training=True`).
   - The validation pipeline was completely deterministic and unaugmented.

### Visual Sample Review
- A comprehensive comparison grid was generated and saved to [`results/experiments/v3_augmentation_samples.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_augmentation_samples.png).
- It displays original images alongside 3 randomized photometric and geometric variations for target challenging classes (**W, Z, S, Y, Q**) and reference class **A**.
- Visual inspection confirms natural illumination shifts, subtle skin tone contrast variations, and edge preservation without artifact distortion or label alteration.

---

## 4. Epoch-by-Epoch Metric History

- **Batch Size:** 32 (544 training batches per epoch)
- **Initial Learning Rate:** $\eta = 0.0005$
- **Loss:** Sparse Categorical Cross-Entropy

| Epoch | Train Loss | Train Accuracy | Val Loss | Val Accuracy | Learning Rate | Checkpoint Action |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 1.9742 | 42.41% | 3.0287 | 27.18% | 0.000500 | Checkpoint saved (`val_loss: 3.0287`) |
| 2 | 0.5392 | 86.75% | 2.0173 | 62.06% | 0.000500 | Checkpoint saved (`val_loss: 2.0173`) |
| 3 | 0.1984 | 95.67% | 1.8737 | 72.98% | 0.000500 | Checkpoint saved (`val_loss: 1.8737`) |
| 4 | 0.1070 | 97.93% | 1.6900 | 78.03% | 0.000500 | Checkpoint saved (`val_loss: 1.6900`) |
| 5 | 0.0715 | 98.45% | 1.4776 | 78.27% | 0.000500 | Checkpoint saved (`val_loss: 1.4776`) |
| 6 | 0.0561 | 98.75% | 4.2971 | 36.39% | 0.000500 | Validation fluctuation |
| 7 | 0.0512 | 98.88% | 1.8817 | 73.78% | 0.000500 | Recovery |
| 8 | **0.0368** | **99.17%** | **1.3732** | **78.11%** | **0.000500** | **Best Checkpoint Saved (`val_loss: 1.3732`)** |
| 9 | 0.0422 | 98.94% | 1.7822 | 73.58% | 0.000500 | - |
| 10 | 0.0313 | 99.22% | 1.6248 | 79.10% | 0.000500 | - |
| 11 | 0.0275 | 99.36% | 1.7035 | 78.15% | 0.000500 | Plateau check |
| 12 | 0.0083 | 99.83% | 1.5127 | **80.29%** | 0.000250 | **Peak Validation Accuracy** |
| 13 | 0.0063 | 99.86% | 1.9472 | 78.47% | 0.000250 | - |
| 14 | 0.0055 | 99.93% | 1.8990 | 78.19% | 0.000250 | EarlyStopping triggered; restored Epoch 8 |

---

## 5. Three-Way Quantitative Comparison: Baseline vs V2 vs V3

All metrics evaluated on the identical 2,517-image Validation split:

| Evaluation Metric | Baseline CNN (Epoch 3) | Experiment 1: V2 (Epoch 9) | Experiment 2: V3 (Epoch 8) | Net Gain (V3 vs Baseline) | Net Gain (V3 vs V2) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Best Validation Loss** | 2.8015 | 1.6701 | **1.3732** | **-50.98% (-1.4283)** | **-17.78% (-0.2969)** |
| **Val Accuracy @ Best Loss** | 55.78% | 76.40% | **78.11%** | **+22.33 pp** | **+1.71 pp** |
| **Peak Val Accuracy** | 76.08% (Epoch 8) | 80.10% (Epoch 13) | **80.29%** (Epoch 12) | **+4.21 pp** | **+0.19 pp** |
| **Validation Macro Precision** | ~54.2% | 74.14% | **77.53%** | **+23.33 pp** | **+3.39 pp** |
| **Validation Macro Recall** | ~55.8% | 76.67% | **78.17%** | **+22.37 pp** | **+1.50 pp** |
| **Validation Macro F1-Score** | ~53.5% | 73.10% | **75.52%** | **+22.02 pp** | **+2.42 pp** |
| **Validation Weighted F1-Score**| ~53.1% | 72.64% | **75.23%** | **+22.13 pp** | **+2.59 pp** |
| **Trainable Parameters** | 113,114 | 307,322 | 307,322 | $+194,208$ | Identical ($0$) |
| **Augmentation Techniques** | Geometric only | Geometric only | **Geometric + Photometric** | Illumination invariance | Contrast & brightness |

---

## 6. Difficult-Class Empirical Analysis (W, Z, S, Y, Q)

A detailed review of the target difficult classes provides strong empirical insights into the model's behavior:

| Class | V2 Precision | V2 Recall | V2 F1 | V3 Precision | V3 Recall | V3 F1 | Net F1 Delta | Primary Misclassification Mode (V3) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **W** | 0.00% | 0.00% | 0.00% | **30.00%** | **3.00%** | **5.45%** | **+5.45 pp** | Misclassified as X (26%), E (24%), C (16%) |
| **Z** | 0.00% | 0.00% | 0.00% | **0.00%** | **0.00%** | **0.00%** | 0.00 pp | Misclassified as Q (52.7%), D (28.0%), C (19.4%) |
| **S** | 100.00% | 25.00% | 40.00% | **100.00%** | **25.00%** | **40.00%** | 0.00 pp | Misclassified as T (25.0%), F (23.0%), Y (23.0%) |
| **Y** | 50.00% | 25.77% | 34.01% | **66.67%** | **47.42%** | **55.42%** | **+21.41 pp** | Misclassified as Q (22.7%), C (17.5%) |
| **Q** | 40.00% | 51.49% | 45.02% | **37.78%** | **50.50%** | **43.22%** | -1.80 pp | Misclassified as E (24.8%), P (13.9%), M (8.9%) |

### Key Evidence-Based Observations:
1. **Class W Symmetry Breaking:**
   - In baseline and V2, class W had completely collapsed to 0 predictions.
   - Under photometric augmentation, the model correctly identified 3 instances of W, with precision leaping from 0% to **30.0%**. However, subtle palm orientation still causes confusion with classes X and E, indicating that hand edge contrast helped, but spatial keypoints are needed for complete disambiguation.
2. **Major Breakthrough on Class Y:**
   - Class Y recall jumped from **25.77% to 47.42%**, and precision improved from **50.0% to 66.67%**, yielding an F1 surge from **34.01% to 55.42% (+21.41%)**. The dual-finger spread in Y benefited strongly from lighting variation training.
3. **Persisting Class Z Failure:**
   - Class Z remained at 0% recall and was predominantly classified as **Q (52.7%)** and **D (28.0%)**. In ISL, the Z gesture features an index finger tracing or pointing in space; from 2D webcams, its static contour strongly mimics the pointing posture of D and the downward finger of Q. Photometric augmentation alone cannot resolve identical static 2D silhouette overlaps.
4. **Other Substantial Class Gains:**
   - **Class A:** F1 jumped from $0.8214 \to \mathbf{0.9899}$ ($+16.85\%$) with 100% precision!
   - **Class B:** F1 jumped from $0.8065 \to \mathbf{0.9899}$ ($+18.34\%$) with 100% precision!
   - **Class I:** F1 jumped from $0.6755 \to \mathbf{0.8502}$ ($+17.47\%$)!
   - **Class J:** F1 jumped from $0.6756 \to \mathbf{0.8588}$ ($+18.32\%$)!

---

## 7. Overfitting & Convergence Observations

- **Lower Generalization Loss:**
  - Experiment 2 reached a best validation loss of **`1.3732`**, significantly lower than V2's `1.6701` and Baseline's `2.8015`.
  - Adding brightness and contrast variations reduced the model's sensitivity to background illumination, forcing the convolutional filters to focus on morphological hand boundaries rather than absolute pixel intensity.
- **Regularization Effect:**
  - In Epochs 4, 5, and 8, validation loss consistently settled around 1.4–1.6 before plateauing, showing that photometric jitter acted as an effective lightweight regularizer without impeding convergence.

---

## 8. Runtime & Hardware Environment

- **Operating System:** Windows 11 (64-bit)
- **Compute Unit:** Multi-core Intel CPU with oneDNN AVX2/AVX_VNNI instructions (GPU unavailable).
- **Execution Time:** 196.68 minutes (~3.28 hours) for 14 epochs (~14 minutes per epoch).
- **Memory Footprint:** Resident Set Size ~930 MB, Virtual Memory ~1.9 GB.

---

## 9. Limitations & Research Takeaways

1. **Static 2D Ambiguity:**
   - Photometric augmentation substantially boosts illumination invariance and enhances classes with distinctive finger counts (A, B, I, J, Y).
   - However, gestures with near-identical 2D palm silhouettes (e.g., Z vs Q/D, and W vs X/E) require either higher input resolution, specialized hand keypoint extraction (MediaPipe Hands), or geometric cutouts/erasing.
2. **Holdout Benchmark Protocol Maintained:**
   - The test set (`dataset/processed/Testing/`) remains pristine and untainted for the final benchmark evaluation.

---

## 10. Git Status & Artifact Directory Index

### Git Status
```text
Clean branch worktree; baseline files and checkpoints fully preserved.
No git commits or pushes executed.
```

### Experiment 2 Artifact Index
- **Model Checkpoint:** [`saved_models/experiments/isl_alphabet_cnn_v3_best.keras`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/saved_models/experiments/isl_alphabet_cnn_v3_best.keras)
- **Training Pipeline Script:** [`training/experiments/train_v3.py`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/training/experiments/train_v3.py)
- **Training History CSV:** [`results/experiments/v3_training_history.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_training_history.csv)
- **Accuracy Trajectory:** [`results/experiments/v3_training_accuracy.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_training_accuracy.png)
- **Loss Trajectory:** [`results/experiments/v3_training_loss.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_training_loss.png)
- **Validation Classification Report CSV:** [`results/experiments/v3_val_classification_report.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_val_classification_report.csv)
- **Validation Confusion Matrix Plot:** [`results/experiments/v3_val_confusion_matrix.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_val_confusion_matrix.png)
- **Augmentation Samples Grid:** [`results/experiments/v3_augmentation_samples.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/experiments/v3_augmentation_samples.png)
- **Milestone Report:** [`docs/reports/CNN_EXPERIMENT_2_REPORT.md`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/CNN_EXPERIMENT_2_REPORT.md)
