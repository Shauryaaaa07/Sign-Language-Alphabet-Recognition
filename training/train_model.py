#!/usr/bin/env python3
"""
Baseline CNN Model Training Script
==================================

Indian Sign Language (ISL) Alphabet Recognition Project
Milestone 3.3: Baseline CNN Model Training

This script trains the baseline 2D CNN model using the cleaned dataset
(Training and Validation splits only) with strict adherence to academic standards:
- Reprodicible seeds (42).
- Conservative training augmentation (rotation, translation, zoom; NO horizontal flip).
- Standard learning rate schedule and regularization.
- ModelCheckpoint, EarlyStopping, and ReduceLROnPlateau callbacks.
- Generates history CSV, loss/accuracy plots, and formal training report.
- STRICT RESTRICTION: The Testing dataset is NEVER loaded or evaluated in this milestone.
"""

import argparse
import datetime
import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from training.data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        create_dataset_pipeline,
        discover_and_verify_classes,
    )
    from training.model import build_model, load_verified_classes
except ModuleNotFoundError:
    from data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        create_dataset_pipeline,
        discover_and_verify_classes,
    )
    from model import build_model, load_verified_classes

# --- Hyperparameters & Settings ---
RANDOM_SEED = 42
MAX_EPOCHS = 30
BATCH_SIZE = 32
INITIAL_LR = 0.001
EARLY_STOPPING_PATIENCE = 5
REDUCE_LR_PATIENCE = 3
REDUCE_LR_FACTOR = 0.5
MIN_LR = 1e-6

DEFAULT_CHECKPOINT_PATH = "saved_models/isl_alphabet_cnn_best.keras"
DEFAULT_HISTORY_CSV = "results/training_history.csv"
DEFAULT_ACCURACY_PNG = "results/training_accuracy.png"
DEFAULT_LOSS_PNG = "results/training_loss.png"
DEFAULT_REPORT_PATH = "docs/reports/BASELINE_TRAINING_REPORT.md"


def set_reproducibility_seeds(seed: int = RANDOM_SEED) -> None:
    """Sets random seeds across Python, NumPy, and TensorFlow for deterministic execution."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    keras.utils.set_random_seed(seed)


def plot_training_metrics(
    history_df: pd.DataFrame,
    best_epoch: int,
    accuracy_png: str = DEFAULT_ACCURACY_PNG,
    loss_png: str = DEFAULT_LOSS_PNG,
) -> None:
    """Generates and saves clean publication-quality training curves."""
    os.makedirs(os.path.dirname(os.path.abspath(accuracy_png)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(loss_png)), exist_ok=True)

    epochs = history_df["epoch"]

    # 1. Accuracy Plot
    plt.figure(figsize=(9, 5.5))
    plt.plot(epochs, history_df["accuracy"], "o-", label="Training Accuracy", color="#1f77b4", linewidth=2)
    plt.plot(epochs, history_df["val_accuracy"], "s-", label="Validation Accuracy", color="#ff7f0e", linewidth=2)
    plt.axvline(best_epoch, color="#2ca02c", linestyle="--", alpha=0.8, label=f"Best Checkpoint (Epoch {best_epoch})")
    plt.title("ISL Alphabet Baseline CNN: Training & Validation Accuracy", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("Accuracy", fontsize=12)
    plt.ylim(bottom=0.0, top=1.02)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=11, loc="lower right")
    plt.tight_layout()
    plt.savefig(accuracy_png, dpi=150)
    plt.close()

    # 2. Loss Plot
    plt.figure(figsize=(9, 5.5))
    plt.plot(epochs, history_df["loss"], "o-", label="Training Loss", color="#1f77b4", linewidth=2)
    plt.plot(epochs, history_df["val_loss"], "s-", label="Validation Loss", color="#d62728", linewidth=2)
    plt.axvline(best_epoch, color="#2ca02c", linestyle="--", alpha=0.8, label=f"Best Checkpoint (Epoch {best_epoch})")
    plt.title("ISL Alphabet Baseline CNN: Training & Validation Loss", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Epoch", fontsize=12)
    plt.ylabel("Sparse Categorical Cross-Entropy Loss", fontsize=12)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(fontsize=11, loc="upper right")
    plt.tight_layout()
    plt.savefig(loss_png, dpi=150)
    plt.close()


def generate_training_report(
    report_path: str,
    history_df: pd.DataFrame,
    best_epoch: int,
    best_val_loss: float,
    best_val_acc: float,
    final_lr: float,
    early_stopped: bool,
    training_duration_sec: float,
    checkpoint_path: str,
    checkpoint_size_bytes: int,
) -> None:
    """Generates formal Markdown report with complete epoch-by-epoch table and metrics."""
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)

    duration_min = training_duration_sec / 60.0
    total_epochs_run = len(history_df)

    lines = [
        "# Baseline CNN Model Training Report",
        "",
        "## 1. Executive Summary",
        f"- **Training Completion Timestamp (UTC):** `{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        f"- **Model Architecture:** Baseline 2D Convolutional Neural Network (3 Conv Blocks + GlobalAveragePooling2D + Dense Head)",
        f"- **Total Trainable Parameters:** `113,114`",
        f"- **Total Epochs Configured:** `{MAX_EPOCHS}`",
        f"- **Actual Epochs Completed:** `{total_epochs_run}`",
        f"- **Early Stopping Triggered:** `{'Yes (Patience=5 reached)' if early_stopped else 'No (Completed full epochs)'}`",
        f"- **Optimal Checkpoint Saved at Epoch:** `{best_epoch}`",
        f"- **Best Validation Loss:** `{best_val_loss:.4f}` (Epoch {best_epoch})",
        f"- **Validation Accuracy at Best Loss:** `{best_val_acc * 100:.2f}%`",
        f"- **Final Learning Rate:** `{final_lr:.2e}`",
        f"- **Total Training Duration:** `{duration_min:.2f} minutes` (`{training_duration_sec:.1f} seconds`)",
        f"- **Model Checkpoint Path:** `{checkpoint_path}` (`{checkpoint_size_bytes / (1024 * 1024):.2f} MB`)",
        "",
        "> [!IMPORTANT]",
        "> **Strict Holdout Protocol Confirmation:**",
        "> In strict accordance with experimental ethics and the Milestone 3.3 directive, the **Testing dataset was NOT loaded or evaluated** during this run. Checkpoint selection and early stopping were governed strictly by the Validation split (`val_loss`). The Testing set remains an untainted independent holdout benchmark for Milestone 3.4.",
        "",
        "---",
        "",
        "## 2. Training Configuration & Hyperparameters",
        "",
        "| Parameter | Configuration Value | Description |",
        "|---|---|---|",
        "| **Dataset Splits Used** | `Training` (17,407), `Validation` (2,517) | Sourced strictly from `dataset/processed/` |",
        "| **Classes** | 26 (A–Z) | Discovered from directory and verified via `label_classes.json` |",
        "| **Input Image Size** | 128 × 128 × 3 | Rescaled to float32 range `[0.0, 1.0]` |",
        "| **Batch Size** | 32 | Yields 544 training steps and 79 validation steps per epoch |",
        "| **Data Augmentation** | Conservative (Training Only) | Rotation $\\pm 14.4^\\circ$, Translation $\\pm 5\\%$, Zoom $\\pm 5\\%$, **No Horizontal Flip** |",
        "| **Optimizer** | Adam | Initial $\\eta = 0.001$, $\\beta_1 = 0.9$, $\\beta_2 = 0.999$, $\\epsilon = 10^{-7}$ |",
        "| **Loss Function** | Sparse Categorical Cross-Entropy | Direct integer label loss |",
        "| **ModelCheckpoint** | `val_loss` (mode: min) | Saves only best weights to `.keras` container |",
        "| **EarlyStopping** | `val_loss` (patience: 5) | Restores best weights upon termination |",
        "| **ReduceLROnPlateau**| `val_loss` (factor: 0.5, patience: 3)| Halves learning rate on validation loss stagnation |",
        "| **Random Seed** | 42 | Full reproducibility |",
        "",
        "---",
        "",
        "## 3. Epoch-by-Epoch Metric History",
        "",
        "| Epoch | Training Loss | Training Accuracy | Validation Loss | Validation Accuracy | Learning Rate | Checkpoint Action |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for idx, row in history_df.iterrows():
        ep = int(row["epoch"])
        tr_l = float(row["loss"])
        tr_a = float(row["accuracy"])
        va_l = float(row["val_loss"])
        va_a = float(row["val_accuracy"])
        lr = float(row.get("learning_rate", row.get("lr", INITIAL_LR)))

        if ep == best_epoch:
            action = "**Saved Best Checkpoint**"
        elif ep < best_epoch and (idx == 0 or va_l < history_df.iloc[:idx]["val_loss"].min()):
            action = "Saved Checkpoint"
        else:
            action = "-"

        lines.append(
            f"| {ep:2d} | {tr_l:.4f} | {tr_a * 100:.2f}% | {va_l:.4f} | {va_a * 100:.2f}% | {lr:.2e} | {action} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Visual Metric Artifacts",
        "- **Accuracy Trajectory:** [`results/training_accuracy.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_accuracy.png)",
        "- **Loss Trajectory:** [`results/training_loss.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_loss.png)",
        "- **Raw History Data:** [`results/training_history.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/training_history.csv)",
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def train_baseline_model(
    dataset_dir: str = DEFAULT_DATASET_DIR,
    mapping_path: str = DEFAULT_MAPPING_PATH,
    checkpoint_path: str = DEFAULT_CHECKPOINT_PATH,
    history_csv_path: str = DEFAULT_HISTORY_CSV,
    accuracy_png_path: str = DEFAULT_ACCURACY_PNG,
    loss_png_path: str = DEFAULT_LOSS_PNG,
    report_path: str = DEFAULT_REPORT_PATH,
    max_epochs: int = MAX_EPOCHS,
    batch_size: int = BATCH_SIZE,
) -> keras.Model:
    """Executes the full baseline training loop with callbacks and metrics recording."""
    print("=" * 70)
    print("ISL ALPHABET RECOGNITION: BASELINE CNN MODEL TRAINING")
    print("=" * 70)

    # 1. Reproducibility
    set_reproducibility_seeds(RANDOM_SEED)
    print(f"[REPRODUCIBILITY] Seed set to {RANDOM_SEED} across Python, NumPy, and TensorFlow.")

    # 2. Label discovery
    classes = load_verified_classes(mapping_path)
    print(f"[DATASET] Loaded {len(classes)} verified classes: {', '.join(classes)}")

    # 3. Data Pipelines (TRAINING & VALIDATION ONLY - NEVER TESTING)
    print("[DATASET] Loading Training split (augmented, shuffled)...")
    train_ds = create_dataset_pipeline(
        split_dir=os.path.join(dataset_dir, "Training"),
        classes=classes,
        batch_size=batch_size,
        is_training=True,
        enable_augmentation=True,
        seed=RANDOM_SEED,
    )

    print("[DATASET] Loading Validation split (unaugmented, deterministic)...")
    val_ds = create_dataset_pipeline(
        split_dir=os.path.join(dataset_dir, "Validation"),
        classes=classes,
        batch_size=batch_size,
        is_training=False,
        enable_augmentation=False,
        seed=RANDOM_SEED,
    )

    print("[RESTRICTION CONFIRMED] Testing split is NOT loaded or accessed.")

    # 4. Model Construction
    model = build_model(
        input_shape=(*DEFAULT_IMAGE_SIZE, 3),
        num_classes=len(classes),
        learning_rate=INITIAL_LR,
    )
    print("\n[MODEL SUMMARY]")
    model.summary()

    # 5. Callbacks
    os.makedirs(os.path.dirname(os.path.abspath(checkpoint_path)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(history_csv_path)), exist_ok=True)

    checkpoint_cb = keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        monitor="val_loss",
        save_best_only=True,
        mode="min",
        verbose=1,
    )

    early_stopping_cb = keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=EARLY_STOPPING_PATIENCE,
        restore_best_weights=True,
        mode="min",
        verbose=1,
    )

    reduce_lr_cb = keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=REDUCE_LR_FACTOR,
        patience=REDUCE_LR_PATIENCE,
        min_lr=MIN_LR,
        mode="min",
        verbose=1,
    )

    csv_logger_cb = keras.callbacks.CSVLogger(
        filename=history_csv_path,
        separator=",",
        append=False,
    )

    callbacks_list = [checkpoint_cb, early_stopping_cb, reduce_lr_cb, csv_logger_cb]

    # 6. Model Fitting
    print("\n[TRAINING] Starting model.fit() ...")
    start_time = time.time()

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=max_epochs,
        callbacks=callbacks_list,
        verbose=1,
    )

    total_duration = time.time() - start_time
    print(f"\n[TRAINING COMPLETE] Elapsed time: {total_duration / 60:.2f} minutes ({total_duration:.1f}s)")

    # 7. Metrics Extraction & Analysis
    history_df = pd.read_csv(history_csv_path)
    # Ensure 1-based epoch numbering
    if history_df["epoch"].min() == 0:
        history_df["epoch"] = history_df["epoch"] + 1

    # Extract learning rates if recorded, else from optimizer
    if "learning_rate" not in history_df.columns and "lr" not in history_df.columns:
        history_df["learning_rate"] = INITIAL_LR

    # Identify optimal checkpoint
    min_loss_idx = history_df["val_loss"].idxmin()
    best_epoch = int(history_df.loc[min_loss_idx, "epoch"])
    best_val_loss = float(history_df.loc[min_loss_idx, "val_loss"])
    best_val_acc = float(history_df.loc[min_loss_idx, "val_accuracy"])
    early_stopped = len(history_df) < max_epochs

    current_lr = float(keras.ops.convert_to_numpy(model.optimizer.learning_rate)) if hasattr(model.optimizer, "learning_rate") else INITIAL_LR

    checkpoint_size = os.path.getsize(checkpoint_path) if os.path.exists(checkpoint_path) else 0

    print(f"[RESULT] Best Epoch            : {best_epoch}")
    print(f"[RESULT] Best Validation Loss  : {best_val_loss:.4f}")
    print(f"[RESULT] Best Validation Acc   : {best_val_acc * 100:.2f}%")
    print(f"[RESULT] Checkpoint File Size  : {checkpoint_size:,} bytes ({checkpoint_size / (1024 * 1024):.2f} MB)")
    print(f"[RESULT] Early Stopped         : {early_stopped}")

    # 8. Visual Artifacts
    print(f"[ARTIFACTS] Plotting curves to {accuracy_png_path} and {loss_png_path}...")
    plot_training_metrics(history_df, best_epoch, accuracy_png_path, loss_png_path)

    # 9. Markdown Report
    print(f"[REPORT] Writing training report to {report_path}...")
    generate_training_report(
        report_path=report_path,
        history_df=history_df,
        best_epoch=best_epoch,
        best_val_loss=best_val_loss,
        best_val_acc=best_val_acc,
        final_lr=current_lr,
        early_stopped=early_stopped,
        training_duration_sec=total_duration,
        checkpoint_path=checkpoint_path,
        checkpoint_size_bytes=checkpoint_size,
    )

    print("=" * 70)
    print("[SUCCESS] Baseline CNN model training pipeline complete.")
    print("=" * 70)
    return model


def main() -> int:
    parser = argparse.ArgumentParser(description="ISL Alphabet Recognition Baseline Training")
    parser.add_argument("--dataset-dir", default=DEFAULT_DATASET_DIR, help="Path to cleaned dataset root.")
    parser.add_argument("--mapping-path", default=DEFAULT_MAPPING_PATH, help="Path to label classes JSON.")
    parser.add_argument("--checkpoint-path", default=DEFAULT_CHECKPOINT_PATH, help="Output path for best checkpoint.")
    parser.add_argument("--history-csv", default=DEFAULT_HISTORY_CSV, help="Output path for training history CSV.")
    parser.add_argument("--accuracy-png", default=DEFAULT_ACCURACY_PNG, help="Output path for accuracy plot.")
    parser.add_argument("--loss-png", default=DEFAULT_LOSS_PNG, help="Output path for loss plot.")
    parser.add_argument("--report-path", default=DEFAULT_REPORT_PATH, help="Output path for Markdown report.")
    parser.add_argument("--epochs", type=int, default=MAX_EPOCHS, help="Max training epochs.")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size.")
    args = parser.parse_args()

    train_baseline_model(
        dataset_dir=args.dataset_dir,
        mapping_path=args.mapping_path,
        checkpoint_path=args.checkpoint_path,
        history_csv_path=args.history_csv,
        accuracy_png_path=args.accuracy_png,
        loss_png_path=args.loss_png,
        report_path=args.report_path,
        max_epochs=args.epochs,
        batch_size=args.batch_size,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
