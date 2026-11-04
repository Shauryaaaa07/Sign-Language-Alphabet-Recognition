# Cleaned Dataset Verification Report

## 1. Executive Summary
- **Verification Timestamp (UTC):** `2026-10-31 21:00:46 UTC`
- **Verification Status:** `PASS`
- **Raw Source Directory:** `C:\Users\shaur\OneDrive\Desktop\Sign Language Alphabet Recognition\dataset\raw` (Read-only, 100% immutable)
- **Cleaned Dataset Directory:** `C:\Users\shaur\OneDrive\Desktop\Sign Language Alphabet Recognition\dataset\processed`
- **Exclusion Manifest Used:** `C:\Users\shaur\OneDrive\Desktop\Sign Language Alphabet Recognition\docs\reports\EXCLUDED_FILES_MANIFEST.json`
- **Total Physical Raw Files Scanned:** `25977` (plus 26 isolated in `Letters/`)
- **Total Clean Retained Images:** `25085`
- **Total Excluded Files:** `892`
- **Byte-for-byte SHA-256 Verified Matches:** `25085` / `25085`
- **SHA-256 Hash Mismatches:** `0`
- **Successfully Decoded Images:** `25085` / `25085`
- **Corrupt / Invalid Images in Cleaned Dataset:** `0`

---

## 2. Split-Wise Totals & Simulation Reconciliation

| Split | Simulation Expected Count | Actual Cleaned Count | Discrepancy | Imbalance Ratio |
|:---:|:---:|:---:|:---:|:---:|
| **Training** | 17,407 | 17,407 | 0 (Exact Match) | 1.378:1 |
| **Testing** | 5,161 | 5,161 | 0 (Exact Match) | 1.053:1 |
| **Validation** | 2,517 | 2,517 | 0 (Exact Match) | 1.347:1 |
| **Total** | **25,085** | **25,085** | **0 (Exact Match)** | - |

---

## 3. Per-Class Image Count Table (Cleaned Dataset)

| Class | Training | Testing | Validation | Total Clean Images |
| :---: | :---: | :---: | :---: | :---: |
| **A** | 700 | 200 | 100 | **1000** |
| **B** | 700 | 199 | 100 | **999** |
| **C** | 700 | 200 | 100 | **1000** |
| **D** | 694 | 190 | 100 | **984** |
| **E** | 650 | 199 | 100 | **949** |
| **F** | 650 | 200 | 100 | **950** |
| **G** | 688 | 196 | 99 | **983** |
| **H** | 648 | 199 | 76 | **923** |
| **I** | 696 | 200 | 100 | **996** |
| **J** | 650 | 197 | 101 | **948** |
| **K** | 584 | 193 | 75 | **852** |
| **L** | 700 | 200 | 100 | **1000** |
| **M** | 700 | 200 | 100 | **1000** |
| **N** | 692 | 198 | 99 | **989** |
| **O** | 700 | 199 | 100 | **999** |
| **P** | 700 | 200 | 100 | **1000** |
| **Q** | 644 | 197 | 101 | **942** |
| **R** | 641 | 197 | 76 | **914** |
| **S** | 699 | 200 | 100 | **999** |
| **T** | 624 | 198 | 100 | **922** |
| **U** | 700 | 199 | 101 | **1000** |
| **V** | 700 | 200 | 100 | **1000** |
| **W** | 693 | 200 | 100 | **993** |
| **X** | 698 | 200 | 99 | **997** |
| **Y** | 508 | 200 | 97 | **805** |
| **Z** | 648 | 200 | 93 | **941** |

---

## 4. Integrity & Verification Checks
- **Byte-for-Byte SHA-256 Source Match:** `PASSED` (All 25085 files match raw source hash).
- **PIL Two-Stage Image Decoding:** `PASSED` (0 corrupt images).
- **Cross-Split Duplicate Elimination:** `PASSED` (0 cross-split duplicates).
- **Manifest Reconciliation:** `PASSED` (All 892 exclusions accounted for).
- **Raw Dataset Immutability:** `PASSED` (No files deleted, moved, or renamed in `dataset/raw/`).
