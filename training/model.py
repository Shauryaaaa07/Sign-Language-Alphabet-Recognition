#!/usr/bin/env python3
"""
Convolutional Neural Network (CNN) Model Architecture
=====================================================

Indian Sign Language (ISL) Alphabet Recognition Project
Milestone 3.2: Explainable CNN Baseline for 26-Class Fingerspelling

This module defines, compiles, and validates a clean, beginner-friendly 2D CNN
architecture for ISL alphabet recognition using TensorFlow/Keras.

Key Architectural Characteristics:
- Input Layer: (128, 128, 3) normalized RGB image tensors.
- Feature Extraction: 3 sequential Convolution + MaxPooling blocks (32, 64, 128 filters).
- Feature Aggregation: GlobalAveragePooling2D (reduces spatial dimensions without parameter explosion).
- Regularization: Dropout (rate=0.4) before classification layer.
- Output Layer: Dense(26, activation='softmax') with verified label mapping.
- Optimization: Adam (lr=0.001) + Sparse Categorical Cross-Entropy loss.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from training.data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        DEFAULT_RANDOM_SEED,
        create_dataset_pipeline,
        discover_and_verify_classes,
        get_augmentation_layer,
    )
except ModuleNotFoundError:
    from data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        DEFAULT_RANDOM_SEED,
        create_dataset_pipeline,
        discover_and_verify_classes,
        get_augmentation_layer,
    )

DEFAULT_NUM_CLASSES = 26
DEFAULT_LEARNING_RATE = 0.001


def load_verified_classes(mapping_path: str = DEFAULT_MAPPING_PATH) -> List[str]:
    """
    Loads and validates the label mapping file to ensure strict alignment
    with the 26-class output layer.
    """
    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(
            f"Class mapping file not found at '{mapping_path}'. "
            f"Please run 'training/data_pipeline.py' first."
        )

    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    classes = mapping_data.get("classes", [])
    if len(classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(
            f"Mapping file contains {len(classes)} classes; expected {DEFAULT_NUM_CLASSES}."
        )

    # Verify indices 0 to 25
    c2i = mapping_data.get("class_to_index", {})
    expected_indices = set(range(DEFAULT_NUM_CLASSES))
    actual_indices = set(c2i.values())
    if actual_indices != expected_indices:
        raise ValueError(
            f"Class indices mismatch. Expected {expected_indices}, got {actual_indices}."
        )

    return classes


def build_model(
    input_shape: Tuple[int, int, int] = (*DEFAULT_IMAGE_SIZE, 3),
    num_classes: int = DEFAULT_NUM_CLASSES,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> keras.Model:
    """
    Constructs and compiles the explainable baseline 2D CNN model.

    Architecture Layout:
    --------------------
    1. Input: (128, 128, 3)
    2. Conv Block 1: Conv2D(32, (3,3), relu, same) -> MaxPool2D(2,2)
    3. Conv Block 2: Conv2D(64, (3,3), relu, same) -> MaxPool2D(2,2)
    4. Conv Block 3: Conv2D(128, (3,3), relu, same) -> MaxPool2D(2,2)
    5. Head: GlobalAveragePooling2D -> Dense(128, relu) -> Dropout(0.4) -> Dense(26, softmax)
    """
    inputs = keras.Input(shape=input_shape, name="input_image")

    # --- Convolutional Block 1 ---
    x = layers.Conv2D(
        filters=32,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
        name="conv1",
    )(inputs)
    x = layers.MaxPooling2D(pool_size=(2, 2), name="pool1")(x)

    # --- Convolutional Block 2 ---
    x = layers.Conv2D(
        filters=64,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
        name="conv2",
    )(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name="pool2")(x)

    # --- Convolutional Block 3 ---
    x = layers.Conv2D(
        filters=128,
        kernel_size=(3, 3),
        activation="relu",
        padding="same",
        name="conv3",
    )(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name="pool3")(x)

    # --- Classification Head ---
    # GlobalAveragePooling2D condenses each 16x16 feature map into a single average value,
    # dramatically reducing parameter count compared to Flatten while providing spatial invariance.
    x = layers.GlobalAveragePooling2D(name="global_average_pool")(x)
    x = layers.Dense(128, activation="relu", name="dense_features")(x)
    x = layers.Dropout(rate=0.4, name="dropout_regularization")(x)

    outputs = layers.Dense(
        units=num_classes,
        activation="softmax",
        name="class_probabilities",
    )(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="ISL_Alphabet_Baseline_CNN")

    # Compile with Adam and Sparse Categorical Crossentropy
    # Sparse categorical crossentropy is used because labels are integer indices in [0, 25].
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    return model


def validate_forward_pass(
    model: keras.Model,
    dataset_dir: str = DEFAULT_DATASET_DIR,
    mapping_path: str = DEFAULT_MAPPING_PATH,
) -> bool:
    """
    Executes a comprehensive non-training forward pass validation:
    1. Verifies input/output shapes.
    2. Passes a real batch from dataset/processed/Training through the model.
    3. Checks finite numerical outputs, probability validity, and sum to 1.
    4. Reports parameter statistics.
    """
    print("\n" + "=" * 70)
    print("CNN ARCHITECTURE: FORWARD-PASS VALIDATION GATE")
    print("=" * 70)

    # 1. Print Model Summary
    model.summary()
    total_params = model.count_params()
    trainable_params = sum(int(np.prod(v.shape)) for v in model.trainable_weights)
    non_trainable_params = total_params - trainable_params

    print(f"\n[PARAM CHECK] Total Parameters        : {total_params:,}")
    print(f"[PARAM CHECK] Trainable Parameters    : {trainable_params:,}")
    print(f"[PARAM CHECK] Non-Trainable Parameters: {non_trainable_params:,}")

    # 2. Shape Verification
    expected_input_shape = (None, 128, 128, 3)
    expected_output_shape = (None, DEFAULT_NUM_CLASSES)
    assert model.input_shape == expected_input_shape, f"Input shape mismatch: {model.input_shape}"
    assert model.output_shape == expected_output_shape, f"Output shape mismatch: {model.output_shape}"
    print(f"[SHAPE CHECK] Input Shape Verified  : {model.input_shape}")
    print(f"[SHAPE CHECK] Output Shape Verified : {model.output_shape}")

    # 3. Real Batch Forward Pass
    classes = load_verified_classes(mapping_path)
    train_dir = os.path.join(dataset_dir, "Training")
    train_ds = create_dataset_pipeline(
        split_dir=train_dir,
        classes=classes,
        batch_size=32,
        is_training=False,  # Unaugmented deterministic sample batch
        enable_augmentation=False,
    )

    sample_images, sample_labels = next(iter(train_ds.take(1)))
    print(f"\n[FEED-FORWARD] Passing sample batch through model: {sample_images.shape}")
    predictions = model(sample_images, training=False).numpy()

    # 4. Numerical Assertions
    assert predictions.shape == (32, DEFAULT_NUM_CLASSES), f"Prediction shape mismatch: {predictions.shape}"
    assert np.all(np.isfinite(predictions)), "Model produced NaN or Inf values!"
    assert np.all(predictions >= 0.0) and np.all(predictions <= 1.0), "Probabilities out of [0, 1] bounds!"

    # Probability sum assertion (per image sum == 1.0 within floating point tolerance)
    row_sums = np.sum(predictions, axis=1)
    np.testing.assert_allclose(
        row_sums,
        1.0,
        atol=1e-5,
        err_msg="Softmax probabilities do not sum to 1.0!",
    )
    print(f"[PROBABILITY CHECK] All {len(predictions)} sample predictions sum to 1.0000 (tolerance 1e-5).")
    print(f"[SAMPLE OUTPUT] Top predicted class for image 0: index={np.argmax(predictions[0])} (prob={np.max(predictions[0]):.4f})")

    print("\n" + "=" * 70)
    print("[ALL MODEL CHECKS PASSED] Forward-pass validation successful.")
    print("=" * 70)
    return True


def generate_augmentation_review(
    dataset_dir: str = DEFAULT_DATASET_DIR,
    output_png_path: str = "docs/reports/AUGMENTATION_SAMPLE_REVIEW.png",
    sample_classes: Optional[List[str]] = None,
    seed: int = DEFAULT_RANDOM_SEED,
) -> str:
    """
    Generates a visual comparison grid displaying original Training images
    alongside their augmented counterparts to confirm that hand gestures remain
    identifiable and uncorrupted.
    """
    if sample_classes is None:
        # Select 5 representative classes with distinct visual features:
        # A (closed fist), B (open flat palm), C (curved hand),
        # J (crossed fingers static keyframe), Z (two-handed flat palm)
        sample_classes = ["A", "B", "C", "J", "Z"]

    print(f"\n[VISUAL INSPECTION] Generating augmentation comparison for classes: {sample_classes}")
    aug_layer = get_augmentation_layer(seed=seed)

    fig, axes = plt.subplots(len(sample_classes), 4, figsize=(12, 3 * len(sample_classes)))
    plt.subplots_adjust(hspace=0.35, wspace=0.15)

    rescaling_layer = layers.Rescaling(scale=1.0 / 255.0)

    for row_idx, cls_name in enumerate(sample_classes):
        cls_dir = os.path.join(dataset_dir, "Training", cls_name)
        fnames = sorted([f for f in os.listdir(cls_dir) if f.lower().endswith(".jpg")])
        if not fnames:
            continue

        sample_file = os.path.join(cls_dir, fnames[0])
        raw_img = keras.utils.load_img(sample_file, target_size=DEFAULT_IMAGE_SIZE)
        img_array = keras.utils.img_to_array(raw_img)
        norm_img = rescaling_layer(tf.expand_dims(img_array, axis=0))

        # Column 1: Original Image
        axes[row_idx, 0].imshow(norm_img[0].numpy())
        axes[row_idx, 0].set_title(f"Class '{cls_name}' (Original)", fontsize=11, fontweight="bold")
        axes[row_idx, 0].axis("off")

        # Columns 2, 3, 4: 3 Distinct Augmentation Passes
        for col_idx in range(1, 4):
            aug_img = aug_layer(norm_img, training=True)
            # Clip display values to [0, 1]
            display_img = np.clip(aug_img[0].numpy(), 0.0, 1.0)
            axes[row_idx, col_idx].imshow(display_img)
            axes[row_idx, col_idx].set_title(f"Augmented #{col_idx}", fontsize=10)
            axes[row_idx, col_idx].axis("off")

    fig.suptitle(
        "ISL Alphabet Recognition: Conservative Data Augmentation Review\n"
        "(Rotation ±14.4°, Translation ±5%, Zoom ±5% | Horizontal Flip Strictly Disabled)",
        fontsize=13,
        fontweight="bold",
        y=0.99,
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"[VISUAL INSPECTION] Saved inspection artifact to: {output_png_path}")
    return output_png_path


def main() -> int:
    parser = argparse.ArgumentParser(description="ISL Alphabet Recognition CNN Model Architecture")
    parser.add_argument("--dataset-dir", default=DEFAULT_DATASET_DIR, help="Path to cleaned dataset root.")
    parser.add_argument("--mapping-path", default=DEFAULT_MAPPING_PATH, help="Path for label mapping JSON.")
    parser.add_argument(
        "--inspection-png",
        default="docs/reports/AUGMENTATION_SAMPLE_REVIEW.png",
        help="Path to save augmentation inspection image.",
    )
    parser.add_argument("--run-self-test", action="store_true", help="Run full forward-pass validation gate.")
    args = parser.parse_args()

    classes = load_verified_classes(args.mapping_path)
    model = build_model(num_classes=len(classes))

    # Run forward pass validation
    is_valid = validate_forward_pass(
        model=model,
        dataset_dir=args.dataset_dir,
        mapping_path=args.mapping_path,
    )

    # Generate augmentation visual inspection artifact
    generate_augmentation_review(
        dataset_dir=args.dataset_dir,
        output_png_path=args.inspection_png,
    )

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
