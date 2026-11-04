# Baseline CNN Model Training Report

## 1. Executive Summary
- **Training Completion Timestamp (UTC):** `2026-10-31 23:08:55 UTC`
- **Model Architecture:** Baseline 2D Convolutional Neural Network (3 Conv Blocks + GlobalAveragePooling2D + Dense Head)
- **Total Trainable Parameters:** `113,114`
- **Total Epochs Configured:** `30`
- **Actual Epochs Completed:** `8`
- **Early Stopping Triggered:** `Yes (Patience=5 reached)`
- **Optimal Checkpoint Saved at Epoch:** `3`
- **Best Validation Loss:** `2.8015` (Epoch 3)
- **Validation Accuracy at Best Loss:** `55.78%`
- **Final Learning Rate:** `5.00e-04`
- **Total Training Duration:** `19.51 minutes` (`1170.4 seconds`)
- **Model Checkpoint Path:** `saved_models/isl_alphabet_cnn_best.keras` (`1.34 MB`)

> [!IMPORTANT]
> **Strict Holdout Protocol Confirmation:**
> In strict accordance with experimental ethics and the Milestone 3.3 directive, the **Testing dataset was NOT loaded or evaluated** during this run. Checkpoint selection and early stopping were governed strictly by the Validation split (`val_loss`). The Testing set remains an untainted independent holdout benchmark for Milestone 3.4.

---

## 2. Training Configuration & Hyperparameters

| Parameter | Configuration Value | Description |
|---|---|---|
| **Dataset Splits Used** | `Training` (17,407), `Validation` (2,517) | Sourced strictly from `dataset/processed/` |
| **Classes** | 26 (A–Z) | Discovered from directory and verified via `label_classes.json` |
| **Input Image Size** | 128 × 128 × 3 | Rescaled to float32 range `[0.0, 1.0]` |
| **Batch Size** | 32 | Yields 544 training steps and 79 validation steps per epoch |
| **Data Augmentation** | Conservative (Training Only) | Rotation $\pm 14.4^\circ$, Translation $\pm 5\%$, Zoom $\pm 5\%$, **No Horizontal Flip** |
| **Optimizer** | Adam | Initial $\eta = 0.001$, $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-7}$ |
| **Loss Function** | Sparse Categorical Cross-Entropy | Direct integer label loss |
| **ModelCheckpoint** | `val_loss` (mode: min) | Saves only best weights to `.keras` container |
| **EarlyStopping** | `val_loss` (patience: 5) | Restores best weights upon termination |
| **ReduceLROnPlateau**| `val_loss` (factor: 0.5, patience: 3)| Halves learning rate on validation loss stagnation |
| **Random Seed** | 42 | Full reproducibility |

---

## 3. Epoch-by-Epoch Metric History

| Epoch | Training Loss | Training Accuracy | Validation Loss | Validation Accuracy | Learning Rate | Checkpoint Action |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|  1 | 2.9881 | 8.73% | 2.9117 | 12.51% | 1.00e-03 | Saved Checkpoint |
|  2 | 2.3061 | 22.83% | 2.8542 | 33.06% | 1.00e-03 | Saved Checkpoint |
|  3 | 1.6748 | 41.54% | 2.8015 | 55.78% | 1.00e-03 | **Saved Best Checkpoint** |
|  4 | 1.1634 | 58.17% | 3.0857 | 62.46% | 1.00e-03 | - |
|  5 | 0.8728 | 68.60% | 3.2669 | 69.85% | 1.00e-03 | - |
|  6 | 0.6827 | 76.04% | 3.7099 | 74.37% | 1.00e-03 | - |
|  7 | 0.5078 | 82.87% | 3.8813 | 74.45% | 5.00e-04 | - |
|  8 | 0.4623 | 83.90% | 3.9598 | 76.08% | 5.00e-04 | - |

---

## 4. Visual Metric Artifacts
- **Accuracy Trajectory:** [`results/training_accuracy.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_accuracy.png)
- **Loss Trajectory:** [`results/training_loss.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_loss.png)
- **Raw History Data:** [`results/training_history.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_history.csv)
