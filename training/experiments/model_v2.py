#!/usr/bin/env python3
"""
Improved CNN Architecture (Experiment 1 — Model V2)
===================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase 6 — Milestone 6.2: Experiment 1 Architecture

Key Architectural Enhancements over Baseline:
---------------------------------------------
1. Double Convolution Layers per Block (VGG-style):
   - Block 1: 2x Conv2D (32 filters, 3x3)
   - Block 2: 2x Conv2D (64 filters, 3x3)
   - Block 3: 2x Conv2D (128 filters, 3x3)
2. BatchNormalization + ReLU Post-Convolution:
   - Placed after every Conv2D and before non-linear activation.
   - Prevents internal covariate shift and stabilizes gradient flow.
3. Feature Aggregation & Regularization:
   - GlobalAveragePooling2D condensing spatial dimensions.
   - Dense(128, activation='relu') + Dropout(0.4) for classification head.
   - Dense(26, activation='softmax') output layer matching label mapping.
4. Optimization:
   - Adam with initial learning rate = 0.0005.
   - Sparse Categorical Cross-Entropy loss.
"""

import json
import os
import sys
from typing import List, Tuple

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Repository root path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_LABEL_PATH = os.path.join(REPO_ROOT, "training", "label_classes.json")
DEFAULT_NUM_CLASSES = 26
DEFAULT_LEARNING_RATE = 0.0005
DEFAULT_IMAGE_SIZE = (128, 128)


def load_label_classes(mapping_path: str = DEFAULT_LABEL_PATH) -> List[str]:
    """Loads and verifies the established 26-class mapping."""
    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(f"Class mapping file not found at: {mapping_path}")

    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    classes = data.get("classes", [])
    if len(classes) != DEFAULT_NUM_CLASSES:
        raise ValueError(f"Expected {DEFAULT_NUM_CLASSES} classes, found {len(classes)}")

    return classes


def build_model_v2(
    input_shape: Tuple[int, int, int] = (*DEFAULT_IMAGE_SIZE, 3),
    num_classes: int = DEFAULT_NUM_CLASSES,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> keras.Model:
    """
    Constructs and compiles the Experiment 1 CNN (Model V2).
    """
    inputs = keras.Input(shape=input_shape, name="input_image")

    # =========================================================================
    # Block 1: 32 Filters (2x Conv-BN-ReLU -> MaxPool)
    # =========================================================================
    x = layers.Conv2D(
        filters=32,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block1_conv1",
    )(inputs)
    x = layers.BatchNormalization(name="block1_bn1")(x)
    x = layers.ReLU(name="block1_relu1")(x)

    x = layers.Conv2D(
        filters=32,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block1_conv2",
    )(x)
    x = layers.BatchNormalization(name="block1_bn2")(x)
    x = layers.ReLU(name="block1_relu2")(x)

    x = layers.MaxPooling2D(pool_size=(2, 2), name="block1_pool")(x)

    # =========================================================================
    # Block 2: 64 Filters (2x Conv-BN-ReLU -> MaxPool)
    # =========================================================================
    x = layers.Conv2D(
        filters=64,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block2_conv1",
    )(x)
    x = layers.BatchNormalization(name="block2_bn1")(x)
    x = layers.ReLU(name="block2_relu1")(x)

    x = layers.Conv2D(
        filters=64,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block2_conv2",
    )(x)
    x = layers.BatchNormalization(name="block2_bn2")(x)
    x = layers.ReLU(name="block2_relu2")(x)

    x = layers.MaxPooling2D(pool_size=(2, 2), name="block2_pool")(x)

    # =========================================================================
    # Block 3: 128 Filters (2x Conv-BN-ReLU -> MaxPool)
    # =========================================================================
    x = layers.Conv2D(
        filters=128,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block3_conv1",
    )(x)
    x = layers.BatchNormalization(name="block3_bn1")(x)
    x = layers.ReLU(name="block3_relu1")(x)

    x = layers.Conv2D(
        filters=128,
        kernel_size=(3, 3),
        padding="same",
        use_bias=False,
        name="block3_conv2",
    )(x)
    x = layers.BatchNormalization(name="block3_bn2")(x)
    x = layers.ReLU(name="block3_relu2")(x)

    x = layers.MaxPooling2D(pool_size=(2, 2), name="block3_pool")(x)

    # =========================================================================
    # Classification Head
    # =========================================================================
    x = layers.GlobalAveragePooling2D(name="global_average_pool")(x)
    x = layers.Dense(128, activation="relu", name="dense_features")(x)
    x = layers.Dropout(rate=0.4, name="dropout_regularization")(x)

    outputs = layers.Dense(
        units=num_classes,
        activation="softmax",
        name="class_probabilities",
    )(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="ISL_Alphabet_CNN_V2")

    # Compile with Adam optimizer and sparse categorical cross-entropy
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    loss = keras.losses.SparseCategoricalCrossentropy()

    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=["accuracy"],
    )

    return model


if __name__ == "__main__":
    print("Testing Experiment 1 Model V2 definition...")
    classes = load_label_classes()
    print(f"Loaded {len(classes)} classes: {classes[0]}..{classes[-1]}")
    model = build_model_v2()
    model.summary()
    total_params = sum(int(tf.size(v)) for v in model.weights)
    trainable_params = sum(int(tf.size(v)) for v in model.trainable_weights)
    print(f"\nTotal Parameters: {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")
