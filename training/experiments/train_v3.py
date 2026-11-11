#!/usr/bin/env python3
"""
Experiment 2 Training Pipeline (CNN V3 - Photometric Data Augmentation)
=======================================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase 6 — Milestone 6.3: Photometric Data Augmentation (Experiment 2)

Architecture:
-------------
- Reuses exact CNN V2 architecture from `training/experiments/model_v2.py`:
  * 3 Double-Convolution blocks with BatchNormalization and explicit ReLU.
  * GlobalAveragePooling2D.
  * Dense(128, relu) -> Dropout(0.4) -> Dense(26, softmax).
  * Trainable parameters: 307,322 (Total: 308,218).

Augmentation Additions:
-----------------------
- Unchanged geometric training augmentation:
  * RandomRotation(0.04) (approx +-14.4 deg)
  * RandomTranslation(0.05, 0.05) (+-5%)
  * RandomZoom((-0.05, 0.05)) (+-5%)
  * NO horizontal flip (preserves ISL hand orientation)
- Photometric training-only augmentation:
  * RandomContrast(factor=0.10)
  * RandomBrightness(factor=0.10, value_range=(0.0, 1.0))
  * Strict clipping to [0.0, 1.0]

Data Protocol:
--------------
- Training: dataset/processed/Training (17,407 images)
- Validation: dataset/processed/Validation (2,517 images) - strictly unaugmented
- Testing: STRICTLY SEALED / NOT LOADED OR ACCESSED.
"""

import argparse
import glob
import json
import os
import random
import sys
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Deterministic seeds
RANDOM_SEED = 42
os.environ["PYTHONHASHSEED"] = str(RANDOM_SEED)
os.environ["TF_DETERMINISTIC_OPS"] = "1"
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
tf.random.set_seed(RANDOM_SEED)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from training.data_pipeline import DEFAULT_DATASET_DIR, DEFAULT_IMAGE_SIZE
from training.experiments.model_v2 import build_model_v2, load_label_classes

# Experiment 2 destination paths
EXP_MODEL_DIR = os.path.join(REPO_ROOT, "saved_models", "experiments")
EXP_RESULTS_DIR = os.path.join(REPO_ROOT, "results", "experiments")
CHECKPOINT_PATH = os.path.join(EXP_MODEL_DIR, "isl_alphabet_cnn_v3_best.keras")
HISTORY_CSV_PATH = os.path.join(EXP_RESULTS_DIR, "v3_training_history.csv")
ACCURACY_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v3_training_accuracy.png")
LOSS_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v3_training_loss.png")
VAL_REPORT_PATH = os.path.join(EXP_RESULTS_DIR, "v3_val_classification_report.csv")
VAL_CM_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v3_val_confusion_matrix.png")
AUG_SAMPLES_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v3_augmentation_samples.png")


def ensure_directories():
    """Creates required experiment output directories."""
    os.makedirs(EXP_MODEL_DIR, exist_ok=True)
    os.makedirs(EXP_RESULTS_DIR, exist_ok=True)


def build_v3_augmentation_layer(
    rotation_factor: float = 0.04,
    translation_factor: float = 0.05,
    zoom_factor: float = 0.05,
    contrast_factor: float = 0.10,
    brightness_factor: float = 0.10,
    seed: int = RANDOM_SEED,
) -> keras.Sequential:
    """
    Constructs the Experiment 2 photometric + geometric augmentation pipeline.
    
    Includes:
    - RandomRotation (0.04)
    - RandomTranslation (0.05)
    - RandomZoom (0.05)
    - RandomContrast (0.10)
    - RandomBrightness (0.10, value_range=(0.0, 1.0))
    - Strict avoidance of RandomFlip
    """
    aug_layers = [
        layers.RandomRotation(factor=rotation_factor, seed=seed),
        layers.RandomTranslation(
            height_factor=translation_factor,
            width_factor=translation_factor,
            seed=seed,
        ),
        layers.RandomZoom(
            height_factor=(-zoom_factor, zoom_factor),
            width_factor=(-zoom_factor, zoom_factor),
            seed=seed,
        ),
        layers.RandomContrast(factor=contrast_factor, seed=seed),
        layers.RandomBrightness(factor=brightness_factor, value_range=(0.0, 1.0), seed=seed),
    ]
    return keras.Sequential(aug_layers, name="v3_photometric_geometric_augmentation")


def create_v3_dataset_pipeline(
    split_dir: str,
    classes: List[str],
    image_size: Tuple[int, int] = DEFAULT_IMAGE_SIZE,
    batch_size: int = 32,
    is_training: bool = False,
    enable_augmentation: bool = True,
    seed: int = RANDOM_SEED,
) -> tf.data.Dataset:
    """
    Builds the dataset pipeline for Experiment 2 with photometric augmentation and clipping.
    """
    dataset = keras.utils.image_dataset_from_directory(
        directory=split_dir,
        labels="inferred",
        label_mode="int",
        class_names=classes,
        color_mode="rgb",
        batch_size=batch_size,
        image_size=image_size,
        shuffle=is_training,
        seed=seed if is_training else None,
        interpolation="bilinear",
    )

    # Rescale uint8 [0, 255] to float32 [0.0, 1.0]
    rescaling_layer = layers.Rescaling(scale=1.0 / 255.0)
    dataset = dataset.map(
        lambda x, y: (rescaling_layer(x), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    # Training-only photometric and geometric augmentation with clipping
    if is_training and enable_augmentation:
        aug_layer = build_v3_augmentation_layer(seed=seed)

        def augment_and_clip(images, labels):
            augmented = aug_layer(images, training=True)
            clipped = tf.clip_by_value(augmented, 0.0, 1.0)
            return clipped, labels

        dataset = dataset.map(
            augment_and_clip,
            num_parallel_calls=tf.data.AUTOTUNE,
        )

    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    return dataset


def save_augmentation_sample_grid(
    train_dir: str,
    classes: List[str],
    target_classes: List[str] = ["W", "Z", "S", "Y", "Q", "A"],
    output_path: str = AUG_SAMPLES_PLOT_PATH,
):
    """
    Generates and saves a visual comparison grid showing original images vs
    photometrically augmented counterparts for key target classes.
    """
    aug_layer = build_v3_augmentation_layer(seed=RANDOM_SEED)

    num_classes_to_plot = len(target_classes)
    fig, axes = plt.subplots(num_classes_to_plot, 4, figsize=(12, 3 * num_classes_to_plot))
    plt.suptitle("Experiment 2: Photometric Data Augmentation Samples\n(Original vs 3 Augmented Variations)", fontsize=14, fontweight="bold")

    for idx, cls_name in enumerate(target_classes):
        cls_folder = os.path.join(train_dir, cls_name)
        img_files = sorted(glob.glob(os.path.join(cls_folder, "*.jpg")) + glob.glob(os.path.join(cls_folder, "*.png")))
        if not img_files:
            continue
        
        # Load sample image
        sample_path = img_files[0]
        pil_img = Image.open(sample_path).convert("RGB").resize(DEFAULT_IMAGE_SIZE)
        img_array = np.array(pil_img, dtype=np.float32) / 255.0
        img_tensor = tf.expand_dims(img_array, axis=0)

        # Original
        axes[idx, 0].imshow(img_array)
        axes[idx, 0].set_title(f"Class '{cls_name}' (Original)", fontsize=10, fontweight="bold")
        axes[idx, 0].axis("off")

        # 3 Augmented variations
        for var_idx in range(1, 4):
            aug_tensor = aug_layer(img_tensor, training=True)
            aug_clipped = tf.clip_by_value(aug_tensor, 0.0, 1.0)[0].numpy()
            axes[idx, var_idx].imshow(aug_clipped)
            axes[idx, var_idx].set_title(f"Augmented #{var_idx}", fontsize=10)
            axes[idx, var_idx].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Augmentation sample grid saved to: {output_path}")


def plot_and_save_history(history_df: pd.DataFrame):
    """Generates and saves accuracy and loss progression curves for Experiment 2."""
    epochs = range(1, len(history_df) + 1)

    # 1. Accuracy Curve
    plt.figure(figsize=(9, 5))
    plt.plot(epochs, history_df["accuracy"] * 100, "b-o", label="Training Accuracy", linewidth=2)
    plt.plot(epochs, history_df["val_accuracy"] * 100, "g-s", label="Validation Accuracy", linewidth=2)
    plt.title("Experiment 2 (Model V3 Photometric) — Accuracy Progression", fontsize=13, fontweight="bold")
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
    plt.title("Experiment 2 (Model V3 Photometric) — Loss Trajectory", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Loss", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(LOSS_PLOT_PATH, dpi=150)
    plt.close()


def evaluate_on_validation(
    model: keras.Model,
    val_dataset: tf.data.Dataset,
    classes: List[str],
) -> Dict[str, float]:
    """
    Evaluates the restored best model exclusively on the unaugmented Validation split.
    """
    print("\n--- Evaluating Restored Model on Validation Split ---")
    y_true: List[int] = []
    y_pred: List[int] = []

    for images, labels in val_dataset:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy().tolist())
        y_pred.extend(np.argmax(preds, axis=1).tolist())

    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)

    report_dict = classification_report(
        y_true_np,
        y_pred_np,
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )
    report_df = pd.DataFrame(report_dict).transpose()
    report_df.to_csv(VAL_REPORT_PATH)
    print(f"Validation classification report saved to: {VAL_REPORT_PATH}")

    cm = confusion_matrix(y_true_np, y_pred_np)
    plt.figure(figsize=(14, 12))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("Experiment 2 (Model V3) — Validation Confusion Matrix", fontsize=14, fontweight="bold")
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
        "report_dict": report_dict,
    }


def train_experiment_v3(
    epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 0.0005,
    patience_es: int = 6,
    patience_lr: int = 3,
):
    """Executes the full training and evaluation workflow for Experiment 2."""
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

    # 1. Save visual sample grid of augmentations
    print("\n--- Generating Augmentation Sample Grid ---")
    save_augmentation_sample_grid(
        train_dir=train_dir,
        classes=classes,
        target_classes=["W", "Z", "S", "Y", "Q", "A"],
        output_path=AUG_SAMPLES_PLOT_PATH,
    )

    # 2. Build Data Pipelines
    print("\n--- Constructing tf.data Pipelines with Photometric Augmentation ---")
    train_dataset = create_v3_dataset_pipeline(
        split_dir=train_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=True,
        enable_augmentation=True,
        seed=RANDOM_SEED,
    )

    val_dataset = create_v3_dataset_pipeline(
        split_dir=val_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=False,
        enable_augmentation=False,
        seed=RANDOM_SEED,
    )

    # 3. Build Model V2 architecture (exact reuse)
    print("\n--- Reusing Exact Model V2 Architecture (No architectural changes) ---")
    model = build_model_v2(
        num_classes=len(classes),
        learning_rate=learning_rate,
    )
    model.summary()

    total_params = sum(int(tf.size(v)) for v in model.weights)
    trainable_params = sum(int(tf.size(v)) for v in model.trainable_weights)

    # 4. Callbacks configuration
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

    # 5. Fit model
    print(f"\n--- Starting Experiment 2 Training (Max Epochs: {epochs}, Batch Size: {batch_size}, LR: {learning_rate}) ---")
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

    # 6. Save History Data & Plots
    history_df = pd.DataFrame(history.history)
    history_df.insert(0, "epoch", range(1, len(history_df) + 1))
    history_df.to_csv(HISTORY_CSV_PATH, index=False)
    print(f"Training history saved to: {HISTORY_CSV_PATH}")

    plot_and_save_history(history_df)
    print(f"Progression plots saved to: {ACCURACY_PLOT_PATH} and {LOSS_PLOT_PATH}")

    # 7. Evaluate Restored Best Model on Validation Split
    val_metrics = evaluate_on_validation(model, val_dataset, classes)

    best_val_loss_idx = history_df["val_loss"].idxmin()
    best_val_loss = history_df.loc[best_val_loss_idx, "val_loss"]
    best_loss_epoch = int(history_df.loc[best_val_loss_idx, "epoch"])
    val_acc_at_best_loss = history_df.loc[best_val_loss_idx, "val_accuracy"]
    peak_val_acc = history_df["val_accuracy"].max()
    peak_acc_epoch = int(history_df.loc[history_df["val_accuracy"].idxmax(), "epoch"])

    print("\n=======================================================")
    print("      EXPERIMENT 2 (MODEL V3) VALIDATION SUMMARY       ")
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
    parser = argparse.ArgumentParser(description="Train Experiment 2 Model V3 Photometric Augmentation")
    parser.add_argument("--epochs", type=int, default=30, help="Maximum epochs (default: 30)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--lr", type=float, default=0.0005, help="Initial learning rate (default: 0.0005)")
    args = parser.parse_args()

    train_experiment_v3(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
