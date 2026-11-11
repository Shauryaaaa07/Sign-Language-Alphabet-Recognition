#!/usr/bin/env python3
"""
Experiment 4 Training Pipeline (CNN V5 - SpatialDropout2D Experiment)
=====================================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase 6 — Milestone 6.5: Spatial Dropout Experiment (Experiment 4 / Model V5)

Architecture:
-------------
- Reuses exact CNN V4 architecture with SpatialDropout2D (0.10) added to conv blocks:
  * Block 1: 2x Conv(32, 3x3) + BN + ReLU -> SpatialDropout2D(0.10) -> MaxPool(2x2)
  * Block 2: 2x Conv(64, 3x3) + BN + ReLU -> SpatialDropout2D(0.10) -> MaxPool(2x2)
  * Block 3: 2x Conv(128, 3x3) + BN + ReLU -> SpatialDropout2D(0.10) -> MaxPool(2x2)
  * Head: GlobalAveragePooling2D -> Dense(128, relu) -> Dropout(0.4) -> Dense(26, softmax)
  * L2 Regularization (0.0001) maintained on all 6 Conv2D and 2 Dense kernels.
  * Trainable parameters: 307,322 (Total: 308,218).

Augmentation Pipeline:
----------------------
- Reuses exact V4/V3 photometric + geometric training-only augmentation:
  * RandomRotation(0.04) (approx +-14.4 deg)
  * RandomTranslation(0.05, 0.05) (+-5%)
  * RandomZoom((-0.05, 0.05)) (+-5%)
  * RandomContrast(factor=0.10)
  * RandomBrightness(factor=0.10, value_range=(0.0, 1.0))
  * Strict clipping to [0.0, 1.0]
  * NO horizontal flip (preserves ISL hand orientation)

Data Protocol:
--------------
- Training: dataset/processed/Training (17,407 images)
- Validation: dataset/processed/Validation (2,517 images) - strictly unaugmented
- Testing: STRICTLY SEALED / NOT LOADED OR ACCESSED.
"""

import argparse
import json
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
from training.experiments.model_v2 import load_label_classes

# Experiment 4 destination paths
EXP_MODEL_DIR = os.path.join(REPO_ROOT, "saved_models", "experiments")
EXP_RESULTS_DIR = os.path.join(REPO_ROOT, "results", "experiments")
CHECKPOINT_PATH = os.path.join(EXP_MODEL_DIR, "isl_alphabet_cnn_v5_best.keras")
HISTORY_CSV_PATH = os.path.join(EXP_RESULTS_DIR, "v5_training_history.csv")
ACCURACY_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v5_training_accuracy.png")
LOSS_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v5_training_loss.png")
VAL_REPORT_PATH = os.path.join(EXP_RESULTS_DIR, "v5_val_classification_report.csv")
VAL_CM_PLOT_PATH = os.path.join(EXP_RESULTS_DIR, "v5_val_confusion_matrix.png")


def ensure_directories():
    """Creates required experiment output directories."""
    os.makedirs(EXP_MODEL_DIR, exist_ok=True)
    os.makedirs(EXP_RESULTS_DIR, exist_ok=True)


def build_v5_augmentation_layer(
    rotation_factor: float = 0.04,
    translation_factor: float = 0.05,
    zoom_factor: float = 0.05,
    contrast_factor: float = 0.10,
    brightness_factor: float = 0.10,
    seed: int = RANDOM_SEED,
) -> keras.Sequential:
    """
    Constructs the V4/V3-identical photometric + geometric augmentation pipeline.
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
    return keras.Sequential(aug_layers, name="v5_photometric_geometric_augmentation")


def create_v5_dataset_pipeline(
    split_dir: str,
    classes: List[str],
    image_size: Tuple[int, int] = DEFAULT_IMAGE_SIZE,
    batch_size: int = 32,
    is_training: bool = False,
    enable_augmentation: bool = True,
    seed: int = RANDOM_SEED,
) -> tf.data.Dataset:
    """
    Builds the dataset pipeline for Experiment 4.
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
        aug_layer = build_v5_augmentation_layer(seed=seed)

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


def build_model_v5(
    input_shape: Tuple[int, int, int] = (*DEFAULT_IMAGE_SIZE, 3),
    num_classes: int = 26,
    learning_rate: float = 0.0005,
    l2_reg: float = 0.0001,
    spatial_dropout_rate: float = 0.10,
) -> keras.Model:
    """
    Constructs and compiles the Experiment 4 CNN (Model V5) with SpatialDropout2D (0.10).
    
    Placement:
    - Block 1: After block1_relu2, before block1_pool -> block1_spatial_dropout
    - Block 2: After block2_relu2, before block2_pool -> block2_spatial_dropout
    - Block 3: After block3_relu2, before block3_pool -> block3_spatial_dropout
    """
    reg = keras.regularizers.l2(l2_reg)
    inputs = keras.Input(shape=input_shape, name="input_image")

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block1_conv1")(inputs)
    x = layers.BatchNormalization(name="block1_bn1")(x)
    x = layers.ReLU(name="block1_relu1")(x)

    x = layers.Conv2D(32, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block1_conv2")(x)
    x = layers.BatchNormalization(name="block1_bn2")(x)
    x = layers.ReLU(name="block1_relu2")(x)
    x = layers.SpatialDropout2D(spatial_dropout_rate, name="block1_spatial_dropout")(x)
    x = layers.MaxPooling2D((2, 2), name="block1_pool")(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block2_conv1")(x)
    x = layers.BatchNormalization(name="block2_bn1")(x)
    x = layers.ReLU(name="block2_relu1")(x)

    x = layers.Conv2D(64, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block2_conv2")(x)
    x = layers.BatchNormalization(name="block2_bn2")(x)
    x = layers.ReLU(name="block2_relu2")(x)
    x = layers.SpatialDropout2D(spatial_dropout_rate, name="block2_spatial_dropout")(x)
    x = layers.MaxPooling2D((2, 2), name="block2_pool")(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block3_conv1")(x)
    x = layers.BatchNormalization(name="block3_bn1")(x)
    x = layers.ReLU(name="block3_relu1")(x)

    x = layers.Conv2D(128, (3, 3), padding="same", use_bias=False, kernel_regularizer=reg, name="block3_conv2")(x)
    x = layers.BatchNormalization(name="block3_bn2")(x)
    x = layers.ReLU(name="block3_relu2")(x)
    x = layers.SpatialDropout2D(spatial_dropout_rate, name="block3_spatial_dropout")(x)
    x = layers.MaxPooling2D((2, 2), name="block3_pool")(x)

    # Classification Head
    x = layers.GlobalAveragePooling2D(name="global_average_pool")(x)
    x = layers.Dense(128, activation="relu", kernel_regularizer=reg, bias_regularizer=None, name="dense_features")(x)
    x = layers.Dropout(0.4, name="dropout_regularization")(x)
    outputs = layers.Dense(num_classes, activation="softmax", kernel_regularizer=reg, bias_regularizer=None, name="class_probabilities")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="ISL_Alphabet_CNN_V5")

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    loss = keras.losses.SparseCategoricalCrossentropy()

    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=["accuracy"],
    )
    return model


def plot_and_save_history(history_df: pd.DataFrame):
    """Generates and saves accuracy and loss progression curves for Experiment 4."""
    epochs = range(1, len(history_df) + 1)

    # 1. Accuracy Curve
    plt.figure(figsize=(9, 5))
    plt.plot(epochs, history_df["accuracy"] * 100, "b-o", label="Training Accuracy", linewidth=2)
    plt.plot(epochs, history_df["val_accuracy"] * 100, "g-s", label="Validation Accuracy", linewidth=2)
    plt.title("Experiment 4 (Model V5 SpatialDropout) — Accuracy Progression", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Accuracy (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(ACCURACY_PLOT_PATH, dpi=150)
    plt.close()

    # 2. Loss Curve
    plt.figure(figsize=(9, 5))
    plt.plot(epochs, history_df["loss"], "r-o", label="Training Total Loss (CE + L2)", linewidth=2)
    plt.plot(epochs, history_df["val_loss"], "m-s", label="Validation Total Loss (CE + L2)", linewidth=2)
    plt.title("Experiment 4 (Model V5 SpatialDropout) — Loss Trajectory", fontsize=13, fontweight="bold")
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
    Evaluates the restored best model exclusively on the unaugmented Validation split,
    calculating classification report, confusion matrix, and distinguishing pure CE loss from total loss.
    """
    print("\n--- Evaluating Restored Model on Validation Split ---")
    y_true: List[int] = []
    y_pred: List[int] = []
    y_pred_probs: List[np.ndarray] = []

    for images, labels in val_dataset:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy().tolist())
        y_pred.extend(np.argmax(preds, axis=1).tolist())
        y_pred_probs.extend(preds)

    y_true_np = np.array(y_true)
    y_pred_np = np.array(y_pred)
    y_pred_probs_np = np.array(y_pred_probs)

    # Pure Sparse Categorical Cross-Entropy loss (excluding L2 penalty)
    scce_fn = keras.losses.SparseCategoricalCrossentropy(reduction="sum_over_batch_size")
    pure_val_ce_loss = float(scce_fn(y_true_np, y_pred_probs_np).numpy())

    # Current L2 penalty sum from weights
    l2_penalty = sum(float(tf.reduce_sum(l).numpy()) for l in model.losses)
    total_val_loss_computed = pure_val_ce_loss + l2_penalty

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
    plt.title("Experiment 4 (Model V5) — Validation Confusion Matrix", fontsize=14, fontweight="bold")
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
        "pure_val_ce_loss": pure_val_ce_loss,
        "l2_penalty": l2_penalty,
        "total_val_loss_computed": total_val_loss_computed,
        "report_dict": report_dict,
    }


def train_experiment_v5(
    epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 0.0005,
    l2_reg: float = 0.0001,
    spatial_dropout_rate: float = 0.10,
    patience_es: int = 6,
    patience_lr: int = 3,
):
    """Executes the full training and evaluation workflow for Experiment 4."""
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
    print(f"L2 Kernel Regularization Factor: {l2_reg}")
    print(f"SpatialDropout2D Rate: {spatial_dropout_rate}")

    # 1. Build Data Pipelines (identical to V4/V3)
    print("\n--- Constructing tf.data Pipelines (V4-identical Augmentation) ---")
    train_dataset = create_v5_dataset_pipeline(
        split_dir=train_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=True,
        enable_augmentation=True,
        seed=RANDOM_SEED,
    )

    val_dataset = create_v5_dataset_pipeline(
        split_dir=val_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=False,
        enable_augmentation=False,
        seed=RANDOM_SEED,
    )

    # 2. Build Model V5 with SpatialDropout2D (0.10) and L2 Kernel Regularization
    print("\n--- Building Experiment 4 Model V5 (SpatialDropout2D = 0.10) ---")
    model = build_model_v5(
        num_classes=len(classes),
        learning_rate=learning_rate,
        l2_reg=l2_reg,
        spatial_dropout_rate=spatial_dropout_rate,
    )
    model.summary()

    total_params = sum(int(tf.size(v)) for v in model.weights)
    trainable_params = sum(int(tf.size(v)) for v in model.trainable_weights)
    print(f"\nTotal Regularization Losses Count: {len(model.losses)}")

    # 3. Callbacks configuration
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

    # 4. Train model
    print(f"\n--- Starting Experiment 4 Training (Max Epochs: {epochs}, Batch Size: {batch_size}, LR: {learning_rate}, L2: {l2_reg}, SpatialDropout: {spatial_dropout_rate}) ---")
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
    print("      EXPERIMENT 4 (MODEL V5) VALIDATION SUMMARY       ")
    print("=======================================================")
    print(f"Total Parameters:              {total_params:,}")
    print(f"Trainable Parameters:          {trainable_params:,}")
    print(f"Total Epochs Run:              {len(history_df)}")
    print(f"Best Validation Loss:          {best_val_loss:.4f} (at Epoch {best_loss_epoch})")
    print(f"Val Pure CE Loss (excl. L2):   {val_metrics['pure_val_ce_loss']:.4f}")
    print(f"Model L2 Penalty Term:         {val_metrics['l2_penalty']:.4f}")
    print(f"Val Accuracy at Best Loss:     {val_acc_at_best_loss * 100:.2f}%")
    print(f"Peak Validation Accuracy:      {peak_val_acc * 100:.2f}% (at Epoch {peak_acc_epoch})")
    print(f"Validation Macro Precision:    {val_metrics['macro_precision'] * 100:.2f}%")
    print(f"Validation Macro Recall:       {val_metrics['macro_recall'] * 100:.2f}%")
    print(f"Validation Macro F1-Score:     {val_metrics['macro_f1'] * 100:.2f}%")
    print(f"Validation Weighted F1-Score:  {val_metrics['weighted_f1'] * 100:.2f}%")
    print(f"Training Duration:             {train_duration / 60:.2f} minutes")
    print("=======================================================\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Experiment 4 Model V5 SpatialDropout2D")
    parser.add_argument("--epochs", type=int, default=30, help="Maximum epochs (default: 30)")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size (default: 32)")
    parser.add_argument("--lr", type=float, default=0.0005, help="Initial learning rate (default: 0.0005)")
    parser.add_argument("--l2", type=float, default=0.0001, help="L2 regularization factor (default: 0.0001)")
    parser.add_argument("--spatial-dropout", type=float, default=0.10, help="SpatialDropout2D rate (default: 0.10)")
    args = parser.parse_args()

    train_experiment_v5(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        l2_reg=args.l2,
        spatial_dropout_rate=args.spatial_dropout,
    )
