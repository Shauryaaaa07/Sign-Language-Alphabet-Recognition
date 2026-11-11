"""
Multimodal CNN + Landmark Fusion Model Architecture
===================================================

Combines deep visual representations from the frozen CNN V4 feature extractor
with 78-dimensional geometric MediaPipe hand landmark vectors.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

from backend.vision.landmark_features import FEATURE_DIM


def build_fusion_model(
    cnn_base_model: keras.Model,
    landmark_dim: int = FEATURE_DIM,
    num_classes: int = 26,
    l2_reg: float = 0.0005,
    dropout_rate: float = 0.30,
) -> keras.Model:
    """
    Constructs a two-stream multimodal architecture:
    Stream 1: Image Input (128x128x3) -> Frozen CNN V4 -> dense_features (128-d)
    Stream 2: Landmark Input (78-d) -> Dense(64, ReLU) -> BatchNorm
    Fusion: Concatenate [128 + 64 = 192-d] -> Dense(96, ReLU) -> Dropout -> Dense(26, Softmax)
    """
    # 1. Image Stream (Frozen CNN V4 feature extractor)
    # Extract sub-model from input to 'dense_features'
    image_input = keras.Input(shape=(128, 128, 3), name="input_image")
    cnn_feature_extractor = keras.Model(
        inputs=cnn_base_model.inputs,
        outputs=cnn_base_model.get_layer("dense_features").output,
        name="frozen_cnn_feature_extractor",
    )
    cnn_feature_extractor.trainable = False
    image_features = cnn_feature_extractor(image_input)  # (None, 128)

    # 2. Landmark Stream
    landmark_input = keras.Input(shape=(landmark_dim,), name="input_landmarks")
    landmark_branch = layers.Dense(
        64,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="landmark_proj",
    )(landmark_input)
    landmark_branch = layers.BatchNormalization(name="landmark_bn")(landmark_branch)

    # 3. Multimodal Concatenation (128 + 64 = 192)
    fused = layers.Concatenate(name="multimodal_fusion")([image_features, landmark_branch])

    # 4. Classification Head
    x = layers.Dense(
        96,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="fusion_dense_1",
    )(fused)
    x = layers.BatchNormalization(name="fusion_bn_1")(x)
    x = layers.Dropout(dropout_rate, name="fusion_dropout")(x)

    outputs = layers.Dense(
        num_classes,
        activation="softmax",
        name="multimodal_class_probabilities",
    )(x)

    fusion_model = keras.Model(
        inputs=[image_input, landmark_input],
        outputs=outputs,
        name="SignAI_Multimodal_Fusion",
    )
    return fusion_model
