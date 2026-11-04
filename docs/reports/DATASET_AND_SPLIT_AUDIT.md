# Dataset and Data Split Audit Report

**Project:** SignAI — Indian Sign Language Alphabet Recognition Platform  
**Target Scope:** Complete 26-Class ISL Fingerspelling Alphabet (A–Z)  
**Audit Date:** November 2026  
**Auditor:** Senior ML Engineer & Technical Documentation Specialist  
**Audit Outcome:** **VERIFIED & CERTIFIED**

---

## 1. Dataset Provenance, Attribution & Licensing

| Attribute | Specification | Verification Evidence |
|---|---|---|
| **Dataset Title** | RealSign Indian Sign Language Dataset | Upstream repository metadata |
| **Upstream Source** | [RealSign62/RealSign-Indian-Sign-Language-Dataset](https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset) | Git commit history & upstream release |
| **Licensing Terms** | Creative Commons Zero v1.0 Universal (`CC0 1.0 Universal` — Public Domain Dedication) | Verified from upstream repository `LICENSE` file |
| **Commercial & Academic Rights** | Full rights to copy, modify, distribute, and perform without restriction | CC0 1.0 Public Domain terms |
| **Authors / Contributors** | Aaptha Boggaram, Ankith Boggaram, Ashwin Srinivasa Ramanujan, Aryan Sharma, Bharathi R | Academic citation in upstream README |
| **BibTeX Citation** | ```bibtex<br>@misc{boggaram2023realsign,<br>  author = {Boggaram, Aaptha and Boggaram, Ankith and Ramanujan, Ashwin Srinivasa and Sharma, Aryan and R, Bharathi},<br>  title = {RealSign Indian Sign Language Dataset},<br>  year = {2023},<br>  publisher = {GitHub},<br>  howpublished = {\url{https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset}}<br>}<br>``` | Maintained in `docs/reports/DATASET_AUDIT_REPORT.md` |

---

## 2. Directory Structure & Partition Manifest

The dataset in `dataset/processed/` is organized into three decoupled partitions across all 26 alphabetical classes ($A$ through $Z$):

```
dataset/
├── raw/                      # 100% Immutable original upstream archive (25,977 files)
│   ├── Letters/              # 26 isolated reference visualization cards (A.jpg - Z.jpg)
│   ├── Training/             # Original training directory
│   ├── Testing/              # Original testing directory
│   └── Validation/           # Original validation directory
└── processed/                # Deduplicated, verified production dataset (25,085 files)
    ├── Training/             # 17,407 clean images (26 classes A–Z)
    ├── Validation/           # 2,517 clean images (26 classes A–Z)
    └── Testing/              # 5,161 held-out test images (26 classes A–Z)
```

### Partition Distribution Summary

| Split | Raw Physical Files | Corrupt Excluded | Cross-Split Duplicates Excluded | Clean Retained Images | Split % | Imbalance Ratio |
|---|---|---|---|---|---|---|
| **Training** | 18,198 | 0 | 791 | **17,407** | 69.39% | 1.378 : 1 |
| **Validation** | 2,579 | 0 | 62 | **2,517** | 10.03% | 1.347 : 1 |
| **Testing** | 5,200 | 2 | 37 | **5,161** | 20.58% | 1.053 : 1 |
| **Total** | **25,977** | **2** | **890** | **25,085** | **100.0%** | — |

*Note: 26 isolated static reference cards in `dataset/raw/Letters/` are strictly excluded from all machine learning splits.*

---

## 3. Forensic Duplicate & Leakage Quarantine Analysis

During the Phase 2 Dataset Audit, an exhaustive SHA-256 cryptographic hash audit was executed across all 25,977 raw files. The audit detected two severe anomalies in the raw upstream distribution:

### 3.1 Corrupted Non-Image Files (2 Files)
Two files in the upstream archive failed Pillow image decoding (`UnidentifiedImageError`):
1. `dataset/raw/Testing/E/301.jpg` (314 bytes)
2. `dataset/raw/Testing/K/301.jpg` (314 bytes)

**Forensic Investigation:** Decoding revealed these were plain ASCII Python scripts used by the original dataset authors for batch file renaming:
```python
import os
loc = 'D:/Projects/Capstone Dataset/Split_dataset/Split_dataset/extra/'
x = 251
for i, filename in enumerate(os.listdir(loc)):
    os.rename(loc + filename, loc + str(x) + '.jpg')
    x += 1
```
The script files were accidentally renamed to `301.jpg` and committed to the archive. Both were quarantined and excluded from `dataset/processed/`.

### 3.2 Cross-Split Duplicate Elimination (890 Image Pairs)
A total of **890 image files** sharing identical cryptographic SHA-256 content hashes appeared across multiple splits:
- `Training` $\leftrightarrow$ `Testing` overlap: 663 duplicate pairs
- `Training` $\leftrightarrow$ `Validation` overlap: 101 duplicate pairs
- `Testing` $\leftrightarrow$ `Validation` overlap: 54 duplicate pairs
- All three splits overlap: 72 duplicate pairs

**Academic Safeguard:** Allowing identical images to exist in both training and test sets would cause **data snooping and artificial performance inflation**. All cross-split duplicates were deterministically quarantined and recorded in `docs/reports/EXCLUDED_FILES_MANIFEST.json`. The resulting `dataset/processed/` splits have **zero cross-split duplicate overlap**.

---

## 4. Signer-Independent / Person-Wise Separation Audit

A crucial question in gesture recognition research is whether the training and testing sets feature **signer-independent** partitions (i.e. model tested on individuals unseen during training).

### 4.1 Filename Prefix & Metadata Examination
An automated audit of all 25,085 filenames across `dataset/processed/` was executed:
- **Training Split (17,407 files):**
  - Sequentially numbered filenames without prefix (`0.jpg`, `1.jpg`...): **13,543 files (77.8%)**
  - Contributor-prefixed filenames (`ary` - Aryan, `anki` - Ankith, `S_ash_` - Ashwin, `I_aap_` - Aaptha): **3,864 files (22.2%)**
- **Validation Split (2,517 files):**
  - Sequentially numbered filenames: **2,491 files (98.9%)**
  - Contributor-prefixed filenames: **26 files (1.1%)**
- **Testing Split (5,161 files):**
  - Sequentially numbered filenames: **5,149 files (99.8%)**
  - Contributor-prefixed filenames: **12 files (0.2%)**

### 4.2 Research Finding & Academic Disclosure
> [!IMPORTANT]
> **Academic Integrity Finding: Signer-Independent Separation is NOT Supported by Metadata**  
> While the RealSign dataset is known to have been recorded by 4–5 student signers, **the upstream creators anonymized and sequentially re-indexed over 98% of the validation and testing images**. No subject metadata, participant IDs, or signer mapping logs exist in the repository or archive.
>
> Consequently, **we cannot truthfully claim that the test set is strictly person-independent (leave-one-signer-out)**. The dataset partitions represent an **independent random/chronological partition** with confirmed zero image-level duplication, rather than a verified multi-subject cross-validation benchmark.

---

## 5. Per-Class Distribution in Cleaned Dataset (26 Classes A–Z)

| Class | Training Samples | Validation Samples | Testing Samples (Held-Out) | Total Clean Samples | Class Balance % |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | 700 | 100 | 200 | 1,000 | 3.99% |
| **B** | 700 | 100 | 199 | 999 | 3.98% |
| **C** | 700 | 100 | 200 | 1,000 | 3.99% |
| **D** | 694 | 100 | 190 | 984 | 3.92% |
| **E** | 650 | 100 | 199 | 949 | 3.78% |
| **F** | 650 | 100 | 200 | 950 | 3.79% |
| **G** | 688 | 99 | 196 | 983 | 3.92% |
| **H** | 648 | 76 | 199 | 923 | 3.68% |
| **I** | 696 | 100 | 200 | 996 | 3.97% |
| **J** | 650 | 101 | 197 | 948 | 3.78% |
| **K** | 584 | 75 | 193 | 852 | 3.40% |
| **L** | 700 | 100 | 200 | 1,000 | 3.99% |
| **M** | 700 | 100 | 200 | 1,000 | 3.99% |
| **N** | 692 | 99 | 198 | 989 | 3.94% |
| **O** | 700 | 100 | 199 | 999 | 3.98% |
| **P** | 700 | 100 | 200 | 1,000 | 3.99% |
| **Q** | 644 | 101 | 197 | 942 | 3.76% |
| **R** | 641 | 76 | 197 | 914 | 3.64% |
| **S** | 699 | 100 | 200 | 999 | 3.98% |
| **T** | 624 | 100 | 198 | 922 | 3.68% |
| **U** | 700 | 101 | 199 | 1,000 | 3.99% |
| **V** | 700 | 100 | 200 | 1,000 | 3.99% |
| **W** | 693 | 100 | 200 | 993 | 3.96% |
| **X** | 698 | 99 | 200 | 997 | 3.97% |
| **Y** | 508 | 97 | 200 | 805 | 3.21% |
| **Z** | 648 | 93 | 200 | 941 | 3.75% |
| **Total** | **17,407** | **2,517** | **5,161** | **25,085** | **100.0%** |

---

## 6. Image Preprocessing & Standardization Pipeline

The data pipeline in `training/data_pipeline.py` and backend inference in `backend/prediction.py` enforce exact mathematical consistency:

```
[Raw Compressed Bytes]
        │
        ▼ Pillow safe decode (PIL.Image.open)
[Arbitrary Format] ──> Converted to 3-Channel RGB (Image.convert('RGB'))
        │
        ▼ Bilinear Interpolation (Image.Resampling.BILINEAR)
[Target Tensor: 128 × 128]
        │
        ▼ NumPy conversion (dtype=float32) & [0, 1] Scaling
[Normalized Tensor: arr / 255.0]
        │
        ▼ Batch dimension expansion (Shape: 1, 128, 128, 3)
[CNN V4 Model Forward Pass]
```

1. **Color Space Standardization:** Non-RGB inputs (RGBA, Grayscale, CMYK) are safely rasterized to 3-channel standard RGB.
2. **Dimension Resampling:** All frames are resized to $128 \times 128$ using bilinear interpolation (`Image.Resampling.BILINEAR`).
3. **Intensity Normalization:** Raw 8-bit integer pixels $[0, 255]$ are divided by $255.0$, mapping values strictly to floating-point $[0.0, 1.0]$.
4. **Orientation Invariance Rule:** **No horizontal flipping or mirror augmentations** are permitted during evaluation or inference, as ISL fingerspelling gestures are handedness-sensitive.

---

## 7. Model Checkpoint Integrity Certification

The active production checkpoint was verified using SHA-256 cryptographic hashing:

- **Model File Path:** `saved_models/experiments/isl_alphabet_cnn_v4_best.keras`
- **File Size:** `3,806,482 bytes` (3.63 MB)
- **SHA-256 Hash:** `4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762`
- **Architecture Name:** `ISL_Alphabet_CNN_V4`
- **Input Dimensions:** `(None, 128, 128, 3)`
- **Output Dimensions:** `(None, 26)` (Softmax probabilities for classes A–Z)
- **Trainable Parameters:** `307,322`
- **Non-Trainable Parameters:** `896` (BatchNormalization scale/offset)
- **Total Parameters:** `308,218`
- **Regularization:** L2 weight penalty ($\lambda = 1.0 \times 10^{-4}$) present on all 8 convolutional and dense weight matrices.

---

## 8. Audit Conclusion

The dataset and model configuration comply with the highest standards of computer vision research:
1. Upstream provenance and CC0 licensing are verified.
2. The dataset contains **all 26 classes (A through Z)** with zero class reduction.
3. All 890 cross-split duplicates were eliminated, preventing data snooping.
4. Signer-independent limitations are transparently declared.
5. Preprocessing pipeline guarantees mathematical consistency across training, testing, and live web inference.
