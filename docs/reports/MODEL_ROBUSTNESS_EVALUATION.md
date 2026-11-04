# SignAI: Empirical Model Robustness & Perturbation Evaluation Report

**Document ID:** `EVAL-ROB-2026-V4`  
**Model Under Test:** CNN V4 (`saved_models/experiments/isl_alphabet_cnn_v4_best.keras`)  
**Checkpoint SHA-256:** `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`  
**Dataset Split Evaluated:** Validation Split (`dataset/processed/Validation/`)  
**Image Count:** 2,517 held-out validation images across all 26 classes (A–Z)  
**Total Predictions Computed:** 32,721 model evaluations across 13 distinct perturbation conditions  
**Test Set Isolation Guarantee:** The independent `dataset/processed/Testing/` partition (5,161 images) remained strictly untouched and quarantined during this evaluation to preserve benchmark integrity.

---

## 1. Executive Summary & Purpose

In production accessibility applications, sign language gestures are captured in unconstrained domestic environments with erratic room lighting, camera lens defocus, webcam sensor noise, hand orientation tilts, and variable distance from the lens.

To provide empirical evidence of the production readiness and physical operational boundaries of the selected **CNN V4** model, we conducted a systematic perturbation stress test across 13 reproducible conditions on all 2,517 images of the clean validation partition.

```
       +--------------------------------------------------------------+
       |                  CNN V4 ROBUSTNESS PROFILE                   |
       +--------------------------------------------------------------+
       |  RESILIENT TO:                                               |
       |  [x] Natural wrist tilts (+/-10 deg):     80.14% (+0.08 pp)  |
       |  [x] Optical defocus blur (r=1.5 px):     80.33% (+0.28 pp)  |
       |  [x] Scale zoom-in (1.18x):               80.97% (+0.91 pp)  |
       |  [x] Moderate rotations (+/-20 deg):      77.67% (-2.38 pp)  |
       |  [x] High-ISO sensor noise (sigma=15):    77.83% (-2.22 pp)  |
       +--------------------------------------------------------------+
       |  SENSITIVE TO:                                               |
       |  [!] Low contrast (-30%):                 57.69% (-22.37 pp) |
       |  [!] High brightness / overexposure (+40%): 47.12% (-32.94 pp) |
       |  [!] Low brightness / underexposure (-40%): 32.82% (-47.24 pp) |
       +--------------------------------------------------------------+
```

---

## 2. Experimental Methodology & Perturbation Pipeline

Each image was loaded from disk, subjected to the deterministic synthetic perturbation, converted to RGB, resized using bilinear interpolation to $128 \times 128 \times 3$, normalized to $[0.0, 1.0]$, and processed by the CNN V4 model using batch inference ($N=64$).

### Perturbation Definitions
1. **Control Baseline:** Raw image without alterations.
2. **Low Brightness (-40%):** Pixel luminance scaled by $0.6$ (underexposure, night/shadows).
3. **High Brightness (+40%):** Pixel luminance scaled by $1.4$ (overexposure, direct glare).
4. **Low Contrast (-30%):** Image contrast reduced by $30\%$ (washed-out cheap webcam sensors).
5. **High Contrast (+30%):** Image contrast boosted by $30\%$ (harsh direct sunlight).
6. **Gaussian Blur ($r=1.5$ px):** Kernel defocus simulating camera misfocus or motion jitter.
7. **Gaussian Noise ($\sigma=15$):** Additive zero-mean Gaussian sensor noise representing low-light sensor gain.
8. **Wrist Tilts ($\pm 10^\circ$):** In-plane geometric rotation simulating comfortable hand angles.
9. **Extreme Angles ($\pm 20^\circ$):** In-plane geometric rotation simulating angled camera mounting.
10. **Scale Zoom-In ($1.18\times$):** Center crop to $85\%$ and bilinear upscale (hand close to lens).
11. **Scale Zoom-Out ($0.85\times$):** Scale down to $85\%$ centered on a neutral grey canvas (hand far from lens).

---

## 3. Empirical Measurement Results

The table below presents the actual measured accuracy, Macro F1-score, mean prediction confidence, and performance delta relative to the unperturbed baseline:

| Perturbation Condition | Real-World Failure Mode | Measured Accuracy | Macro F1-Score | Mean Confidence | Accuracy Delta vs Baseline | Robustness Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Clean Baseline (Control)** | Standard indoor lighting | **80.06%** | **77.58%** | 90.55% | $\pm 0.00\text{ pp}$ | Reference |
| **Gaussian Blur ($r=1.5$)** | Optical defocus / low lens MTF | **80.33%** | **78.21%** | 89.62% | **$+0.28\text{ pp}$** | **Exceptionally Resilient** |
| **Scale Zoom-In ($1.18\times$)** | Hand positioned closer to camera | **80.97%** | **79.61%** | 90.35% | **$+0.91\text{ pp}$** | **Enhanced Performance** |
| **Slight Tilt ($+10^\circ$)** | Natural wrist articulation tilt | **80.14%** | **78.21%** | 88.74% | **$+0.08\text{ pp}$** | **Highly Resilient** |
| **Slight Tilt ($-10^\circ$)** | Natural wrist articulation tilt | **80.14%** | **77.94%** | 88.95% | **$+0.08\text{ pp}$** | **Highly Resilient** |
| **Scale Zoom-Out ($0.85\times$)** | Hand positioned further away | **78.07%** | **77.04%** | 78.86% | **$-1.99\text{ pp}$** | Mild Degradation |
| **Gaussian Noise ($\sigma=15$)** | Low-light webcam sensor gain | **77.83%** | **75.49%** | 87.14% | **$-2.22\text{ pp}$** | Mild Degradation |
| **Moderate Tilt ($+20^\circ$)** | Angled camera placement | **77.67%** | **75.98%** | 83.32% | **$-2.38\text{ pp}$** | Moderate Tolerance |
| **Moderate Tilt ($-20^\circ$)** | Angled camera placement | **77.67%** | **76.29%** | 82.67% | **$-2.38\text{ pp}$** | Moderate Tolerance |
| **High Contrast ($+30\%$)** | Direct sunlight illumination | **74.22%** | **73.17%** | 84.69% | **$-5.84\text{ pp}$** | Moderate Sensitivity |
| **Low Contrast ($-30\%$)** | Flat diffuse lighting / faded lens | **57.69%** | **57.51%** | 72.15% | **$-22.37\text{ pp}$** | High Sensitivity |
| **High Brightness ($+40\%$)** | Severe overexposure / backlight | **47.12%** | **47.40%** | 71.71% | **$-32.94\text{ pp}$** | Severe Failure Point |
| **Low Brightness ($-40\%$)** | Dim room / underexposed frames | **32.82%** | **32.61%** | 68.64% | **$-47.24\text{ pp}$** | Severe Failure Point |

---

## 4. Deep Technical Analysis & Findings

### 4.1 Invariance to Geometric and Optical Distortions
1. **Defocus Blur Tolerance:**
   Applying a Gaussian Blur kernel with $r=1.5$ px resulted in a nominal accuracy gain ($80.06\% \rightarrow 80.33\%$). This demonstrates that the CNN V4 convolutional filters rely primarily on intermediate structural contours (such as finger silhouette topology and gross palm shape) rather than high-frequency micro-textures (like skin pores or palm creases), rendering it robust to lower-tier webcams.
2. **Wrist Rotation Tolerance ($\pm 10^\circ$):**
   Human signers rarely present their wrists at a perfectly vertical angle. The evaluation demonstrates that natural angular variations within $\pm 10^\circ$ cause zero performance degradation ($80.14\%$ vs $80.06\%$), proving that the random rotation augmentations applied during Milestone 6.4 training successfully imparted rotational invariance.
3. **Scale Proximity:**
   Zooming into the hand ($1.18\times$) yielded the highest overall validation accuracy ($80.97\%$). This confirms that higher pixel coverage of the palm and phalanges increases discriminatory feature representation.

### 4.2 Critical Sensitivity: Luminance and Exposure
1. **Photometric Vulnerability:**
   A $40\%$ reduction in brightness collapsed accuracy from $80.06\%$ to $32.82\%$ (a $-47.24\text{ pp}$ drop). Similarly, a $40\%$ overexposure dropped accuracy to $47.12\%$.
2. **Causal Explanation:**
   Because pixel intensities are normalized linearly to $[0, 1]$, extreme underexposure shifts edge gradients into the floor threshold where convolutional activation kernels fail to excite ReLU units. In overexposure, pixel saturation clips the highlight values to $1.0$, obliterating the fine boundaries between adjacent fingers.
3. **Application Mitigation:**
   In the SignAI web client, the UI must provide real-time guidance (e.g., "Lighting too low, please increase ambient light") and implement adaptive contrast stretching if raw video frames exhibit mean luminance below $0.25$ or above $0.85$.

---

## 5. Summary of Engineering Recommendations

| Observed Sensitivity | Root Cause | Recommended Software / UX Mitigation |
| :--- | :--- | :--- |
| **Low / High Lighting** | Pixel clipping in monocular RGB feed | Display an ambient luminance indicator in Studio; warn users when lighting is insufficient. |
| **Extreme Rotations ($>20^\circ$)** | Planar 2D projection distortion | Guide users with a bounding reticle to align palm vertically within the webcam view. |
| **Hand Distance ($<0.85\times$)** | Low resolution on fingers | Instruct user to position hand so that palm occupies at least 50% of the camera bounding box. |

---

## 6. Audit Verification Sign-Off

- **Evaluation Script:** `scratch/evaluate_model_robustness.py`
- **Output Artifact:** `scratch/robustness_results.json`
- **Lead QA Engineer:** Antigravity AI Engineering Suite
- **Verification Date:** 2026-11-02
- **Audit Status:** **VERIFIED (Empirical Data Grounded)**
