# Dataset Cleaning Plan: Non-Destructive Deduplication & Quarantine

## 1. Executive Summary & Purpose

The initial execution of the dataset audit tool (`training/inspect_dataset.py`) on the raw RealSign dataset (`dataset/raw`) revealed an overall status of `FAIL` (exit code `1`) due to two distinct integrity failures:
1. **Corrupted / Invalid Non-Image Files:** 2 files (`Testing/E/301.jpg` and `Testing/K/301.jpg`) which are actually Python batch-renaming text scripts rather than valid JPEG images.
2. **Cross-Split Data Leakage:** 818 pairwise exact duplicates (spanning 648 unique SHA-256 hash clusters) shared across `Training`, `Testing`, and `Validation` splits.

This document formalizes the **Dataset Cleaning Strategy** to transition the dataset to an audit-passing state (`PASS`, exit code `0`) while guaranteeing zero data snooping, preserving benchmark validity, and maintaining absolute raw data immutability.

---

## 2. Core Architectural Principles

### 2.1 Immutability of Raw Data (`dataset/raw/`)
Under no circumstances will files in `dataset/raw/` be renamed, deleted, moved, or modified in place. The raw download and extraction serve as the ground-truth archival baseline. All cleaning operations are executed non-destructively by generating:
1. An auditable, machine-readable exclusion manifest (`docs/reports/EXCLUDED_FILES_MANIFEST.json`).
2. A clean, processed dataset directory (`dataset/processed/` or symlinked index) utilized by training pipelines in Phase 3.

### 2.2 Strict Holdout Preservation (Testing Set as Golden Benchmark)
In supervised machine learning, test set contamination (train-test leakage) artificially inflates evaluation metrics and invalidates generalizability claims.
- The `Testing` split represents our independent academic evaluation benchmark.
- Whenever an identical image is found in both `Testing` and `Training`, the `Testing` instance is prioritized and preserved. The instance in `Training` is excluded.
- Whenever an identical image is found in both `Testing` and `Validation`, the `Testing` instance is prioritized and preserved. The instance in `Validation` is excluded.

### 2.3 Deterministic Priority Hierarchy
When resolving identical SHA-256 hashes across splits, conflicts are resolved deterministically using the following priority order:

$$\text{Testing (Holdout Benchmark)} \succ \text{Validation (Hyperparameter Tuning)} \succ \text{Training (Model Fitting)}$$

| Conflict Scenario | Retained Split | Excluded Split(s) | Exclusion Reason |
|---|---|---|---|
| Image exists in `Testing` AND `Training` | `Testing` | `Training` | `CROSS_SPLIT_LEAKAGE_TEST_HOLD` |
| Image exists in `Testing` AND `Validation` | `Testing` | `Validation` | `CROSS_SPLIT_LEAKAGE_TEST_HOLD` |
| Image exists in `Testing`, `Validation`, AND `Training` | `Testing` | `Validation`, `Training` | `CROSS_SPLIT_LEAKAGE_TEST_HOLD` |
| Image exists in `Validation` AND `Training` | `Validation` | `Training` | `CROSS_SPLIT_LEAKAGE_VAL_HOLD` |

### 2.4 Deterministic Intra-Split Deduplication
When duplicate images appear within the same split (e.g., 147 pairs in Training, 38 in Testing, 12 in Validation):
- The surviving image is selected deterministically by sorting file paths lexicographically (alphabetical order) and retaining the first entry: `min(file_paths)`.
- All subsequent duplicates in that split are excluded with reason `INTRA_SPLIT_DUPLICATE`.

---

## 3. Quarantine Strategy for Corrupted Files

The two non-image files identified during the audit:
- `dataset/raw/Testing/E/301.jpg` (SHA-256: `91ca47fa65b0580983d5a49806b744d03da04d0ef9d7990022d250d0658a98f4`)
- `dataset/raw/Testing/K/301.jpg` (SHA-256: `91ca47fa65b0580983d5a49806b744d03da04d0ef9d7990022d250d0658a98f4`)

### Quarantine Policy:
1. These files are logged in `docs/reports/EXCLUDED_FILES_MANIFEST.json` under the reason `CORRUPTED_NON_IMAGE_SCRIPT`.
2. They are strictly excluded from copying or indexing into `dataset/processed/`.
3. Because both files contain identical Python batch-renaming code with no underlying image pixels, no data recovery is attempted.

---

## 4. Exclusion Manifest Specification

All exclusions will be documented in a structured JSON file at `docs/reports/EXCLUDED_FILES_MANIFEST.json`.

### 4.1 Schema Definition
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DatasetExclusionManifest",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "dataset_name": { "type": "string" },
        "generated_at": { "type": "string", "format": "date-time" },
        "total_files_audited": { "type": "integer" },
        "total_files_excluded": { "type": "integer" },
        "total_files_retained": { "type": "integer" }
      },
      "required": ["dataset_name", "generated_at", "total_files_audited", "total_files_excluded", "total_files_retained"]
    },
    "exclusions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "relative_path": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "split": { "type": "string", "enum": ["Training", "Testing", "Validation"] },
          "class_label": { "type": "string" },
          "reason": {
            "type": "string",
            "enum": [
              "CORRUPTED_NON_IMAGE_SCRIPT",
              "CROSS_SPLIT_LEAKAGE_TEST_HOLD",
              "CROSS_SPLIT_LEAKAGE_VAL_HOLD",
              "INTRA_SPLIT_DUPLICATE"
            ]
          },
          "retained_reference": { "type": ["string", "null"] }
        },
        "required": ["relative_path", "sha256", "split", "class_label", "reason", "retained_reference"]
      }
    }
  },
  "required": ["metadata", "exclusions"]
}
```

---

## 5. Post-Cleaning Class Distribution & Balance Handling

### 5.1 Estimated Post-Deduplication Image Counts
- **Training Set:** 18,198 initial $\rightarrow$ estimated ~17,450 to 17,500 clean images.
  - Distribution: ~650 to 700 images per class.
  - Ample volume for training a robust 26-class MobileNetV2 or CNN feature extractor.
- **Testing Set:** 5,200 initial $\rightarrow$ 5,198 valid images $\rightarrow$ estimated ~5,160 clean images after intra-test deduplication.
  - Distribution: ~195 to 200 images per class.
  - Provides a high-confidence, uncompromised test set.
- **Validation Set:** 2,579 initial $\rightarrow$ estimated ~2,470 clean images.
  - Distribution: Most classes have ~95 to 100 images; Class `K` has 75 images.

### 5.2 Class Imbalance Handling
- The slight underrepresentation in Class `K` within Validation (75 images) does not threaten model generalization.
- **No Artificial Oversampling:** Synthetic oversampling (e.g. duplicating images) will not be used, as it reintroduces duplicate sample issues.
- **Dynamic Real-Time Data Augmentation:** In Phase 3, during training, batches will undergo lightweight spatial augmentations (random rotations $\pm 10^\circ$, subtle translation $\pm 5\%$, brightness shifts $\pm 10\%$) using standard image data generators. This regularizes the network naturally across all classes.

---

## 6. Execution Safeguards & Next Steps

1. **Zero Raw Alterations:** `dataset/raw/` remains untouched.
2. **Deterministic Reproducibility:** Anyone running the cleaning script against `dataset/raw/` will generate the identical `EXCLUDED_FILES_MANIFEST.json` and clean dataset.
3. **Audit Verification Gate:** Upon execution of the cleaning step in Milestone 2.4, the audit tool (`training/inspect_dataset.py`) will be executed against `dataset/processed/` to programmatically verify:
   - 0 corrupted files.
   - 0 cross-split leakage pairs.
   - Overall status: `PASS` (exit code `0`).
