# Dataset Cleaning Simulation Report (Dry-Run)

## 1. Executive Summary
- **Simulation Execution Timestamp (UTC):** `2026-10-31 18:55:56 UTC`
- **Execution Mode:** Read-Only Simulation (`dataset/raw/` remains 100% immutable).
- **Validation Gate Status:** `PASS`
- **Total Physical Files Inspected:** `25977` (plus 26 isolated in `Letters/`)
- **Original Valid Images:** `25975`
- **Original Invalid / Corrupted Files:** `2`
- **Total Files Retained:** `25085`
- **Total Files Marked for Exclusion:** `892`
- **Total Unique SHA-256 Hashes:** `25085`
- **Total Unique Duplicate Groups:** `786`

---

## 2. Duplicate Groups & Split-Wise Distribution
A duplicate group is defined as a cluster of two or more physical files sharing the exact same SHA-256 hash.

- **Total Unique Duplicate Groups:** `786`
  - Duplicate groups isolated within a single split: `138`
  - Duplicate groups spanning exactly two splits: `598`
  - Duplicate groups spanning all three splits: `50`

### Excluded Files Breakdown by Reason
| Exclusion Reason | File Count | Description |
|---|:---:|---|
| `CORRUPTED_NON_IMAGE_SCRIPT` | 2 | Non-image Python batch-renaming text scripts |
| `CROSS_SPLIT_LEAKAGE_TEST_HOLD` | 689 | Excluded from Train/Val because canonical copy is preserved in Testing |
| `CROSS_SPLIT_LEAKAGE_VAL_HOLD` | 48 | Excluded from Train because canonical copy is preserved in Validation |
| `INTRA_SPLIT_DUPLICATE` | 153 | Redundant duplicate within the same split (lexicographically higher path) |
| **Total Excluded** | **892** | |

---

## 3. Split Counts & Imbalance Ratios (Before vs. After)

| Split | Initial Valid Images | Retained Clean Images | Excluded Files | Min Class | Max Class | Imbalance Ratio (After) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Training** | 18198 | 17407 | 791 | 508 | 700 | 1.378:1 |
| **Testing** | 5198 | 5161 | 37 | 190 | 200 | 1.053:1 |
| **Validation** | 2579 | 2517 | 62 | 75 | 101 | 1.347:1 |
| **Total** | **25975** | **25085** | **892** (incl. 2 corrupt) | - | - | - |

---

## 4. Per-Class Image Distribution (A–Z Before vs. After)

| Class | Training (Before / After) | Testing (Before / After) | Validation (Before / After) | Total Clean Retained |
| :---: | :---: | :---: | :---: | :---: |
| **A** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **B** | 700 / 700 | 200 / 199 | 100 / 100 | **999** |
| **C** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **D** | 700 / 694 | 200 / 190 | 100 / 100 | **984** |
| **E** | 700 / 650 | 199 / 199 | 100 / 100 | **949** |
| **F** | 700 / 650 | 200 / 200 | 100 / 100 | **950** |
| **G** | 700 / 688 | 200 / 196 | 100 / 99 | **983** |
| **H** | 699 / 648 | 200 / 199 | 100 / 76 | **923** |
| **I** | 699 / 696 | 200 / 200 | 100 / 100 | **996** |
| **J** | 700 / 650 | 200 / 197 | 101 / 101 | **948** |
| **K** | 700 / 584 | 199 / 193 | 75 / 75 | **852** |
| **L** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **M** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **N** | 700 / 692 | 200 / 198 | 100 / 99 | **989** |
| **O** | 700 / 700 | 200 / 199 | 100 / 100 | **999** |
| **P** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **Q** | 700 / 644 | 200 / 197 | 101 / 101 | **942** |
| **R** | 700 / 641 | 200 / 197 | 100 / 76 | **914** |
| **S** | 700 / 699 | 200 / 200 | 100 / 100 | **999** |
| **T** | 700 / 624 | 200 / 198 | 100 / 100 | **922** |
| **U** | 700 / 700 | 200 / 199 | 101 / 101 | **1000** |
| **V** | 700 / 700 | 200 / 200 | 100 / 100 | **1000** |
| **W** | 700 / 693 | 200 / 200 | 100 / 100 | **993** |
| **X** | 700 / 698 | 200 / 200 | 100 / 99 | **997** |
| **Y** | 700 / 508 | 200 / 200 | 101 / 97 | **805** |
| **Z** | 700 / 648 | 200 / 200 | 100 / 93 | **941** |

---

## 5. Manual Review & Cross-Class Conflict Warnings
- **Cross-Class Hash Inconsistencies:** None detected (`0`). No identical image appears in different class folders.

---

## 6. Simulation Invariant Validation
- **Invariant 1: Every retained file belongs to exactly one split:** `PASSED`
- **Invariant 2: No exact SHA-256 duplicate remains across simulated splits:** `PASSED`
- **Invariant 3: No invalid/corrupt image is retained:** `PASSED`
- **Invariant 4: All 26 classes remain represented in all splits:** `PASSED`
- **Invariant 5: Testing retains all unique valid image hashes:** `PASSED`
