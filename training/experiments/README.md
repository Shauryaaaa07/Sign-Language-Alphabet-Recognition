# Phase 6 Experiments: Architectural Exploration & Model Optimization

This directory houses experimental model architectures and training pipelines developed in **Phase 6** of the **AI-Based Indian Sign Language (ISL) Alphabet Recognition System**.

---

## Strict Holdout Evaluation Safeguards
In strict compliance with project integrity principles:
1. **Testing Set Sealed:** All experiments are trained on `dataset/processed/Training/` and validated on `dataset/processed/Validation/`. The independent holdout `dataset/processed/Testing/` split is **strictly never accessed or evaluated** during Phase 6 experimentation.
2. **Immutable Class Mapping:** All models use the canonical 26-class mapping (`training/label_classes.json`).
3. **Preservation of Baseline:** The baseline architecture (`training/model.py`, `saved_models/isl_alphabet_cnn_best.keras`, and `results/training_history.csv`) remains untainted and preserved for rigorous comparative analysis.

---

## Experiment Registry

### Experiment 1: Double-Convolution with Batch Normalization (Model V2)
- **Script:** `training/experiments/train_v2.py`
- **Architecture:** `training/experiments/model_v2.py`
- **Key Enhancements:**
  - VGG-style 2x Conv2D per block (32, 64, 128 filters).
  - Batch Normalization after every convolution.
  - Initial learning rate reduced to $0.0005$ with Adam optimizer.
  - EarlyStopping with patience=6, ReduceLROnPlateau with patience=3.
- **Checkpoint:** `saved_models/experiments/isl_alphabet_cnn_v2_best.keras`
- **Results:** `results/experiments/`
- **Report:** `docs/reports/CNN_EXPERIMENT_1_REPORT.md`
