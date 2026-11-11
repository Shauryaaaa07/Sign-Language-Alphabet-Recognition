#!/usr/bin/env python3
"""
Experiment 1 Training Pipeline (Model V2)
=========================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase 6 — Milestone 6.2: Train Improved CNN (V2) with Batch Normalization

Training Protocols:
-------------------
- Dataset:
  * Training: dataset/processed/Training/ (17,407 images)
  * Validation: dataset/processed/Validation/ (2,517 images)
  * Testing: STRICT HOLDOUT — NOT LOADED OR EVALUATED.
- Reproducibility: Seed = 42 (Python, NumPy, TensorFlow).
- Callbacks:
  * ModelCheckpoint: saved_models/experiments/isl_alphabet_cnn_v2_best.keras (val_loss)
  * EarlyStopping: patience = 6, restore_best_weights = True (val_loss)
  * ReduceLROnPlateau: factor = 0.5, patience = 3 (val_loss)
- Metrics & History:
  * results/experiments/v2_training_history.csv
  * results/experiments/v2_training_accuracy.png
  * results/experiments/v2_training_loss.png
  * results/experiments/v2_val_classification_report.csv
  * results/experiments/v2_val_confusion_matrix.png
"""

import argparse
import os
import random
import sys
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras

# Set deterministic random seeds
RANDOM_SEED = 42
os.environ["PYTHONHASHSEED"] = str(RANDOM_SEED)
os.environ["TF_DETERMINISTIC_OPS"] = "1"
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

# Paths configuration
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from training.data_pipeline import (
    DEFAULT_DATASET_DIR,
    DEFAULT_IMAGE_SIZE,
    create_dataset_pipeline,
)
from training.experiments.model_v2 import build_model_v2, load_label_classes

# Experiment 1 output destinations
EXP_MODEL_DIR = os.path.join(REPO_ROOT, "saved_models", "experiments")
EXP_RESULTS_DIR = os.path.join(REPO_ROOT, "results", "experiments")
CHECKPOINT_PATH = os.path.join(EXP_MODEL_DIR, "isl_alphabet_cnn_v2_best.keras")
HISTORY_CSV_PATH = os.path.join(EXP_RESULTS_DIR, "v2_training_history.csv")
ACCURACY_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v2_training_accuracy.png")
LOSS_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v2_training_loss.png")
VAL_REPORT_PATH = os.path.join(EXP_RESULTS_DIR, "v2_val_classification_report.csv")
VAL_CM_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v2_val_confusion_matrix.png")


def ensure_directories():
    """Creates required experiment destination directories."""
    os.makedirs(EXP_MODEL_DIR, exist_ok=True)
    os.makedirs(EXP_RESULTS_DIR, exist_ok=True)


def plot_and_save_history(history_df: pd.DataFrame):
    """Generates and saves accuracy and loss progression curves."""
    epochs = range(1, len(history_df) + 1)

    # 1. Accuracy Curve
    plt.figure(figsize=(9, 5))
    plt.plot(epochs, history_df["accuracy"] * 100, "b-o", label="Training Accuracy", linewidth=2)
    plt.plot(epochs, history_df["val_accuracy"] * 100, "g-s", label="Validation Accuracy", linewidth=2)
    plt.title("Experiment 1 (Model V2) — Accuracy Progression", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Accuracy (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(ACCURACY_PLOT_PATH, dpi=150)
    plt.close()

    # 2. Loss Curve
    plt.figure(figsize=(9, 5))
    plt.plot(epochs, history_df["loss"], "r-o", label="Training Loss", linewidth=2)
    plt.plot(epochs, history_df["val_loss"], "m-s", label="Validation Loss", linewidth=2)
    plt.title("Experiment 1 (Model V2) — Loss Trajectory", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Sparse Categorical Cross-Entropy Loss", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(LOSS_PLOT_PATH, dpi=150)
    plt.close()


def evaluate_on_validation(
    model: keras.Model,
    val_dataset: tf.data.Dataset,
    classes: List[str],
) -> Dict[str, any]:
    """
    Evaluates the restored best model strictly on the Validation split.
    Calculates macro and per-class precision, recall, and F1 scores.
    """
    print("\n--- Evaluating Restored Model on Validation Split ---")
    y_true_all = []
    y_pred_all = []

    for batch_images, batch_labels in val_dataset:
        logits = model(batch_images, training=False)
        preds = tf.argmax(logits, axis=-1).numpy()
        y_pred_all.extend(preds)
        y_true_all.extend(batch_labels.numpy())

    y_true_all = np.array(y_true_all)
    y_pred_all = np.array(y_pred_all)

    # Classification report
    report_dict = classification_report(
        y_true_all,
        y_pred_all,
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )

    report_df = pd.DataFrame(report_dict).transpose()
    report_df.to_csv(VAL_REPORT_PATH)
    print(f"Validation classification report saved to: {VAL_REPORT_PATH}")

    # Confusion matrix
    cm = confusion_matrix(y_true_all, y_pred_all)
    plt.figure(figsize=(12, 10))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Experiment 1 (Model V2) — Validation Confusion Matrix", fontsize=13, fontweight="bold")
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=9)
    plt.yticks(tick_marks, classes, fontsize=9)
    plt.xlabel("Predicted Label", fontsize=11)
    plt.ylabel("True Label", fontsize=11)
    plt.tight_layout()
    plt.savefig(VAL_CM_PLOT_PATH, dpi=150)
    plt.close()
    print(f"Validation confusion matrix saved to: {VAL_CM_PLOT_PATH}")

    return {
        "macro_precision": report_dict["macro avg"]["precision"],
        "macro_recall": report_dict["macro avg"]["recall"],
        "macro_f1": report_dict["macro avg"]["f1-score"],
        "weighted_f1": report_dict["weighted avg"]["f1-score"],
        "val_accuracy": report_dict["accuracy"],
    }


def train_experiment_v2(
    epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 0.0005,
    patience_es: int = 6,
    patience_lr: int = 3,
):
    """Executes the full training and evaluation workflow for Experiment 1."""
    ensure_directories()
    classes = load_label_classes()

    train_dir = os.path.join(DEFAULT_DATASET_DIR, "Training")
    val_dir = os.path.join(DEFAULT_DATASET_DIR, "Validation")

    print(f"TensorFlow Version: {tf.__version__}")
    print(f"Keras Version: {getattr(keras, '__version__', 'integrated')}")
    print(f"Python Platform: {sys.platform}")
    print(f"Random Seed: {RANDOM_SEED}")
    print(f"Classes ({len(classes)}): {classes[0]}..{classes[-1]}")
    print(f"Training split: {train_dir}")
    print(f"Validation split: {val_dir}")
    print("Testing split: STRICTLY SEALED / NOT LOADED")

    # 1. Build Data Pipelines (Reuse existing augmentation: rotation 0.04, translation 0.05, zoom 0.05, no flip)
    print("\n--- Constructing tf.data Pipelines ---")
    train_dataset = create_dataset_pipeline(
        split_dir=train_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=True,
        enable_augmentation=True,
        seed=RANDOM_SEED,
    )

    val_dataset = create_dataset_pipeline(
        split_dir=val_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=False,
        enable_augmentation=False,
        seed=RANDOM_SEED,
    )

    # 2. Build Model V2
    print("\n--- Building Experiment 1 Model V2 ---")
    model = build_model_v2(
        num_classes=len(classes),
        learning_rate=learning_rate,
    )
    model.summary()

    total_params = sum(int(tf.size(v)) for v in model.weights)
    trainable_params = sum(int(tf.size(v)) for v in model.trainable_weights)

    # 3. Configure Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=CHECKPOINT_PATH,
            monitor="val_loss",
            mode="min",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            mode="min",
            patience=patience_es,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            mode="min",
            factor=0.5,
            patience=patience_lr,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    # 4. Train Model
    print(f"\n--- Starting Training (Max Epochs: {epochs}, Batch Size: {batch_size}, LR: {learning_rate}) ---")
    start_time = time.time()
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
        callbacks=callbacks,
        verbose=1,
    )
    train_duration = time.time() - start_time
    print(f"\nTraining completed in {train_duration:.2f} seconds ({train_duration / 60:.2f} minutes).")

    # 5. Save History Data & Plots
    history_df = pd.DataFrame(history.history)
    history_df.insert(0, "epoch", range(1, len(history_df) + 1))
    history_df.to_csv(HISTORY_CSV_PATH, index=False)
    print(f"Training history saved to: {HISTORY_CSV_PATH}")

    plot_and_save_history(history_df)
    print(f"Progression plots saved to: {ACCURACY_PLOT_PATH} and {LOSS_PLOT_PATH}")

    # 6. Evaluate Restored Best Model on Validation Split
    val_metrics = evaluate_on_validation(model, val_dataset, classes)

    best_val_loss_idx = history_df["val_loss"].idxmin()
    best_val_loss = history_df.loc[best_val_loss_idx, "val_loss"]
    best_loss_epoch = int(history_df.loc[best_val_loss_idx, "epoch"])
    val_acc_at_best_loss = history_df.loc[best_val_loss_idx, "val_accuracy"]
    peak_val_acc = history_df["val_accuracy"].max()
    peak_acc_epoch = int(history_df.loc[history_df["val_accuracy"].idxmax(), "epoch"])

    print("\n=======================================================")
    print("      EXPERIMENT 1 (MODEL V2) VALIDATION SUMMARY       ")
    print("=======================================================")
    print(f"Total Parameters:              {total_params:,}")
    print(f"Trainable Parameters:          {trainable_params:,}")
    print(f"Total Epochs Run:              {len(history_df)}")
    print(f"Best Validation Loss:          {best_val_loss:.4f} (at Epoch {best_loss_epoch})")
    print(f"Val Accuracy at Best Loss:     {val_acc_at_best_loss * 100:.2f}%")
    print(f"Peak Validation Accuracy:      {peak_val_acc * 100:.2f}% (at Epoch {peak_acc_epoch})")
    print(f"Validation Macro Precision:    {val_metrics['macro_precision'] * 100:.2f}%")
    print(f"Validation Macro Recall:       {val_metrics['macro_recall'] * 100:.2f}%")
    print(f"Validation Macro F1-Score:     {val_metrics['macro_f1'] * 100:.2f}%")
    print(f"Validation Weighted F1-Score:  {val_metrics['weighted_f1'] * 100:.2f}%")
    print(f"Training Duration:             {train_duration / 60:.2f} minutes")
    print("=======================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Experiment 1 Model V2")
    parser.add_argument("--epochs", type=int, default=30, help="Maximum epochs (default: 30)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--lr", type=float, default=0.0005, help="Initial learning rate (default: 0.0005)")
    args = parser.parse_args()

    train_experiment_v2(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
