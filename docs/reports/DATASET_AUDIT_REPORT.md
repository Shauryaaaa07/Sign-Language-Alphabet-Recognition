# Dataset Audit Report: Indian Sign Language Fingerspelling

## 1. Provenance & License Verification
- **Dataset Root Path:** `dataset/raw`
- **Upstream Source Repository:** [RealSign-Indian-Sign-Language-Dataset](https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset)
- **Upstream License:** Creative Commons Zero v1.0 Universal (`CC0 1.0 Universal` — Public Domain Dedication). Verified directly from upstream repository `LICENSE` file.
- **Local License File Status:** No standalone license file included in root of `Dataset.zip` archive; upstream licensing confirmed and preserved.
- **Citation Preservation:**
  ```bibtex
  @misc{boggaram2023realsign,
    author = {Boggaram, Aaptha and Boggaram, Ankith and Ramanujan, Ashwin Srinivasa and Sharma, Aryan and R, Bharathi},
    title = {RealSign Indian Sign Language Dataset},
    year = {2023},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset}}
  }
  ```
- **Audit Tool:** `training/inspect_dataset.py` (Two-stage Pillow verification: header validation via `verify()` + bitmap decoding via `load()`, combined with SHA-256 content hashing).

---

## 2. Directory Structure & Sibling Validation
- **Splits Detected:** `Training`, `Testing`, `Validation`
- **Isolated Reference Directory:** `Letters/` (contains 26 static reference images `A.jpg` through `Z.jpg`)
- **Reference Asset Isolation Rule:** Images in `Letters/` are strictly reference visualizations and are excluded from all training, validation, and testing splits.
- **Class Subdirectories:** All 26 classes (`A` through `Z`) are present as direct child directories in `Training/`, `Testing/`, and `Validation/`.

---

## 3. Physical Counts vs. Valid Image Counts (Per-Class A–Z Breakdown)

| Class | Training (Phys / Valid) | Testing (Phys / Valid) | Validation (Phys / Valid) | Total Valid Images |
| :---: | :---: | :---: | :---: | :---: |
| **A** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **B** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **C** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **D** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **E** | 700 / 700 | 200 / 199 | 100 / 100 | 999 |
| **F** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **G** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **H** | 699 / 699 | 200 / 200 | 100 / 100 | 999 |
| **I** | 699 / 699 | 200 / 200 | 100 / 100 | 999 |
| **J** | 700 / 700 | 200 / 200 | 101 / 101 | 1001 |
| **K** | 700 / 700 | 200 / 199 | 75 / 75 | 974 |
| **L** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **M** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **N** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **O** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **P** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **Q** | 700 / 700 | 200 / 200 | 101 / 101 | 1001 |
| **R** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **S** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **T** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **U** | 700 / 700 | 200 / 200 | 101 / 101 | 1001 |
| **V** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **W** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **X** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **Y** | 700 / 700 | 200 / 200 | 101 / 101 | 1001 |
| **Z** | 700 / 700 | 200 / 200 | 100 / 100 | 1000 |
| **Total** | **18,198 / 18,198** | **5,200 / 5,198** | **2,579 / 2,579** | **25,975** |

- **Total Physical Files Across Splits:** 25,977 (plus 26 isolated in `Letters/`)
- **Total Valid Image Files Across Splits:** 25,975
- **Corrupted / Invalid Non-Image Files:** Exactly 2 files detected and excluded from valid totals.

---

## 4. Forensic Investigation of Invalid / Corrupted Files

Both corrupted files failed PIL image decoding (`UnidentifiedImageError: cannot identify image file`). Byte-level inspection revealed that both files are ASCII Python scripts accidentally given `.jpg` extensions by the dataset creators:

1. **File 1:** `dataset/raw/Testing/E/301.jpg`
   - **File Size:** 314 bytes
   - **Decoded Content:**
     ```python
     import os

     loc = 'D:/Projects/Capstone Dataset/Split_dataset/Split_dataset/extra/'   #change this location to where your dataset images are saved
     x=251 #change this according to the number of files

     for i, filename in enumerate(os.listdir(loc)):
         os.rename(loc + filename, loc + str(x) + '.jpg')
         x+=1
     ```
2. **File 2:** `dataset/raw/Testing/K/301.jpg`
   - **File Size:** 314 bytes
   - **Decoded Content:** Identical Python script text as above.

**Root Cause:** The upstream authors used a Python renaming script to organize image batches and inadvertently renamed the script itself to `301.jpg` in both directories before packaging the archive.

---

## 5. Class Balance & Image Property Analysis

- **Split `Training` (Valid images = 18,198):**
  - Minimum class count: 699 (Classes `H`, `I`)
  - Maximum class count: 700 (Remaining 24 classes)
  - Imbalance ratio: `1.001 : 1` (Highly balanced)
- **Split `Testing` (Valid images = 5,198):**
  - Minimum class count: 199 (Classes `E`, `K` — due to corrupted file exclusion)
  - Maximum class count: 200 (Remaining 24 classes)
  - Imbalance ratio: `1.005 : 1` (Highly balanced)
- **Split `Validation` (Valid images = 2,579):**
  - Minimum class count: 75 (Class `K`)
  - Maximum class count: 101 (Classes `J`, `Q`, `U`, `Y`)
  - Imbalance ratio: `1.347 : 1` (Slight variance; Class `K` underrepresented in validation split)
- **Image Specifications (Valid images):**
  - Color Modes: 100% `RGB`
  - Container Formats: 100% `JPEG`
  - Dimensions: Width min 133px, max 687px; Height min 122px, max 703px.

---

## 6. Duplicate & Data Leakage Analysis

Exact content duplicate detection was performed using SHA-256 cryptographic hashing across all 25,975 valid images.

### 6.1 Duplicate SHA-256 Hash Clusters
A total of **786 unique SHA-256 hashes** appear more than once in the dataset:
- **Intra-Split Unique Clusters (138 clusters total):**
  - Training only: 104 clusters
  - Testing only: 25 clusters
  - Validation only: 9 clusters
- **Cross-Split Leakage Clusters (648 clusters total):**
  - Testing & Training overlap: 549 clusters
  - Training & Validation overlap: 48 clusters
  - Testing & Validation overlap: 1 cluster
  - Testing, Training, & Validation (all three splits): 50 clusters

### 6.2 Pairwise Duplicate Counts
- **Intra-Split Duplicate Pairs:**
  - Intra-Training duplicate pairs: 147
  - Intra-Testing duplicate pairs: 38
  - Intra-Validation duplicate pairs: 12
  - **Total Intra-Split Duplicate Pairs:** 197
- **Cross-Split Data Leakage Pairs:**
  - `Training` $\leftrightarrow$ `Testing` duplicate pairs: 663
  - `Training` $\leftrightarrow$ `Validation` duplicate pairs: 101
  - `Testing` $\leftrightarrow$ `Validation` duplicate pairs: 54
  - **Total Inter-Split Leakage Pairs:** 818
- **Cross-Class Label Inconsistencies:** **0 pairs** (Identical images never appear across different class directories).

---

## 7. Movement-Dependent Signs Analysis (J & Z)

In Indian Sign Language (ISL), letters **J** and **Z** are traditionally dynamic gestures:
- ISL 'J' involves tracing a hook trajectory in space using the index finger.
- ISL 'Z' involves tracing a zig-zag trajectory in space.

### Visual Inspection Findings:
- **Class J Samples (`Letters/J.jpg`, `Training/J/0.jpg`):** Represented in RealSign as a static two-handed configuration where the dominant index finger crosses the non-dominant index finger.
- **Class Z Samples (`Letters/Z.jpg`, `Training/Z/anki0.jpg`):** Represented in RealSign as a static two-handed configuration where the dominant flat hand rests perpendicularly against the non-dominant palm.

### Single-Frame Architecture Scope Boundary:
A standard 2D Convolutional Neural Network processing single camera frames cannot infer temporal motion trajectories. RealSign resolves this by capturing static keyframe poses for J and Z. This representation is documented as a project scope boundary: the model learns the static RealSign convention for alphabet fingerspelling recognition.

---

## 8. Audit Outcome & Readiness Decision

- **Overall Audit Status:** `FAIL`
- **Audit Tool Exit Code:** `1`

### Root Cause of Failure:
1. **[FAIL] File Integrity Violation:** Detected 2 corrupted/unreadable non-image files (`Testing/E/301.jpg` and `Testing/K/301.jpg`).
2. **[FAIL] Critical Data Leakage:** Detected 818 cross-split exact duplicate image pairs overlapping between `Training`, `Testing`, and `Validation`. If left uncleaned, test set metrics would suffer from data snooping/leakage, yielding falsely inflated benchmark accuracy.

### Conclusion & Next Step:
The dataset requires non-destructive deduplication and quarantine prior to feature engineering and model training. Execution must proceed under `docs/reports/DATASET_CLEANING_PLAN.md`.
