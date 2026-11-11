# Convolutional Neural Network (CNN) Model Architecture

## 1. Overview & Architectural Philosophy

The objective of Milestone 3.2 is to define, compile, and validate a simple, explainable baseline 2D Convolutional Neural Network for the 26-class Indian Sign Language (ISL) Alphabet Recognition system.

### Design Principles:
1. **Explainability for Academic Viva Defense:** Clear layer hierarchy without overly complex multi-branch architectures (e.g., ResNet/Inception skips), ensuring each layer's role is straightforward to explain.
2. **Compact Parameter Footprint:** Utilizes `GlobalAveragePooling2D` rather than a naive `Flatten` layer. This keeps total trainable parameters to **113,114** (~442 KB), eliminating spatial overfitting while enabling rapid inference on standard CPU/edge hardware.
3. **Strict Label Consistency:** Fully synchronized with the bidirectional label mapping generated in `training/label_classes.json` (26 output neurons corresponding to alphabetical indices `0` through `25`).

---

## 2. Layer-by-Layer Architectural Breakdown

```
Input Image (128x128x3, float32 [0, 1])
  │
  ├── [Conv Block 1]
  │     Conv2D (32 filters, 3x3, ReLU, Same Padding)  --> (128, 128, 32)
  │     MaxPooling2D (2x2 pool size)                  --> (64, 64, 32)
  │
  ├── [Conv Block 2]
  │     Conv2D (64 filters, 3x3, ReLU, Same Padding)  --> (64, 64, 64)
  │     MaxPooling2D (2x2 pool size)                  --> (32, 32, 64)
  │
  ├── [Conv Block 3]
  │     Conv2D (128 filters, 3x3, ReLU, Same Padding) --> (32, 32, 128)
  │     MaxPooling2D (2x2 pool size)                  --> (16, 16, 128)
  │
  └── [Classification Head]
        GlobalAveragePooling2D                        --> (128,)
        Dense (128 units, ReLU activation)            --> (128,)
        Dropout (rate = 0.4)                          --> (128,)
        Dense (26 units, Softmax activation)          --> (26,)
```

### Detailed Layer Specification:

| Stage | Layer Name | Layer Type | Output Shape | Kernel / Stride | Activation | Parameter Count | Receptive Field / Purpose |
|---|---|---|---|---|---|:---:|---|
| **Input** | `input_image` | `InputLayer` | `(None, 128, 128, 3)` | — | — | 0 | Ingests normalized RGB hand images |
| **Block 1** | `conv1` | `Conv2D` | `(None, 128, 128, 32)` | 3×3, stride 1, same | ReLU | 896 | Detects low-level edge and color gradient primitives |
| | `pool1` | `MaxPooling2D` | `(None, 64, 64, 32)` | 2×2, stride 2 | — | 0 | Downsamples spatial resolution by 50% |
| **Block 2** | `conv2` | `Conv2D` | `(None, 64, 64, 64)` | 3×3, stride 1, same | ReLU | 18,496 | Extracts mid-level finger edge configurations and contours |
| | `pool2` | `MaxPooling2D` | `(None, 32, 32, 64)` | 2×2, stride 2 | — | 0 | Downsamples spatial resolution by 50% |
| **Block 3** | `conv3` | `Conv2D` | `(None, 32, 32, 128)` | 3×3, stride 1, same | ReLU | 73,856 | Learns high-level spatial hand gestures and palm shapes |
| | `pool3` | `MaxPooling2D` | `(None, 16, 16, 128)` | 2×2, stride 2 | — | 0 | Final downsampling before classification head |
| **Head** | `global_average_pool` | `GlobalAveragePooling2D`| `(None, 128)` | 16×16 average | — | 0 | Averages spatial feature maps, enforcing translation invariance |
| | `dense_features` | `Dense` | `(None, 128)` | — | ReLU | 16,512 | Non-linear dense feature combination layer |
| | `dropout_regularization`| `Dropout` | `(None, 128)` | rate = 0.4 | — | 0 | Stochastically zeroes 40% of activations to prevent co-adaptation |
| | `class_probabilities` | `Dense` | `(None, 26)` | — | Softmax | 3,354 | Computes normalized probability distribution across A–Z |

---

## 3. Parameter Summary

- **Total Parameters:** **113,114** (~441.85 KB in float32 weights)
- **Trainable Parameters:** **113,114** (100%)
- **Non-Trainable Parameters:** **0** (0%)

> [!NOTE]
> **Why `GlobalAveragePooling2D` instead of `Flatten`?**
> If a `Flatten` layer had been applied after `pool3` (shape: `16 x 16 x 128 = 32,768` elements), connecting to `Dense(128)` would require $32,768 \times 128 + 128 = 4,194,432$ parameters in that layer alone.
>
> By utilizing `GlobalAveragePooling2D`, the 16×16 spatial map of each feature channel is averaged into a single scalar, reducing input dimensions from 32,768 to 128. This shrinks head parameters from over 4.1 million to just 16,512, completely preventing position-based overfitting while maintaining feature expressiveness.

---

## 4. Optimization & Loss Configuration

### 4.1 Loss Function: Sparse Categorical Cross-Entropy
- **Mathematical Formulation:**
  $$\mathcal{L} = -\log P(y_{\text{true}} \mid \mathbf{x})$$
- **Rationale:** The data pipeline yields target labels as integer scalars ($y \in \{0, 1, \dots, 25\}$) rather than one-hot encoded vectors ($\mathbf{y} \in \mathbb{R}^{26}$).
- **Computational Efficiency:** Integer representations save memory by avoiding the allocation of sparse 26-dimensional one-hot tensors across millions of image training steps.

### 4.2 Optimizer: Adam
- **Initial Learning Rate:** `0.001` ($\eta = 10^{-3}$)
- **Adaptive Moments:** Uses first-moment exponentially decaying average of gradients ($\beta_1 = 0.9$) and second-moment uncentered variance ($\beta_2 = 0.999$) with numerical stability constant $\epsilon = 10^{-7}$.

### 4.3 Evaluation Metric
- **Top-1 Accuracy:**
  $$\text{Accuracy} = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i)$$

---

## 5. Regularization & Data Augmentation Alignment

### 5.1 Dropout (Rate = 0.4)
- During training, 40% of the activations emerging from the dense feature layer are randomly set to zero per step.
- This forces the classification layer to avoid relying on any single dominant feature and prevents co-adaptation of neurons.
- During evaluation (`training=False`), dropout is deactivated, scaling activations appropriately.

### 5.2 Hand Geometry-Preserving Augmentation
Visual review confirmed the validity of conservative training augmentations:
- **Rotation ($\pm 14.4^\circ$):** Simulates natural slight camera or wrist tilt.
- **Translation ($\pm 5\%$):** Simulates off-center webcam positioning.
- **Zoom ($\pm 5\%$):** Simulates slight user distance shifts from the webcam.
- **Strict Prohibition of Horizontal Flipping:** In Indian Sign Language, finger orientations and specific hand configurations convey semantic distinction. Horizontal mirror reflections invert directional gestures and would corrupt fingerspelling training.

The visual inspection artifact verifying gesture preservation is located at [`docs/reports/AUGMENTATION_SAMPLE_REVIEW.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/docs/reports/AUGMENTATION_SAMPLE_REVIEW.png).

---

## 6. Forward-Pass Verification Gate

The forward pass test (`training/model.py`) executed against an actual batch from the cleaned dataset confirmed:
1. **Input Shape:** Verified as `(None, 128, 128, 3)`.
2. **Output Shape:** Verified as `(None, 26)`.
3. **Numerical Finiteness:** No `NaN` or `Inf` values produced.
4. **Probability Bounds:** $0.0 \le P(c \mid \mathbf{x}) \le 1.0$ for all classes $c \in \{0, \dots, 25\}$.
5. **Softmax Partition Function:** Sum of class probabilities per sample equals $1.0000$ (tolerance: $10^{-5}$).

---

## 7. Academic Scope & Known Limitations

1. **Movement-Dependent Signs (J & Z):**
   - In traditional Indian Sign Language, letters **J** (tracing a downward hook) and **Z** (tracing a zig-zag) are dynamic motion gestures requiring temporal tracking.
   - The RealSign dataset provides static keyframe representations (crossed index fingers for J, perpendicular palm contact for Z).
   - Because a single-frame 2D CNN accepts static spatial snapshots without temporal recurrent or 3D convolutional memory, the model recognizes the static RealSign keyframe convention. This is documented as an academic scope boundary.
2. **Lighting and Complex Backgrounds:**
   - RealSign images feature relatively neutral backgrounds. In real-world deployment, strong backlighting or skin-tone-colored cluttered backgrounds may degrade segmentation, motivating the future inclusion of MediaPipe hand landmark extraction or background normalization in Phase 5.
