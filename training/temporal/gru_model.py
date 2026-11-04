"""
Bidirectional GRU Temporal Architecture for Dynamic Gestures
===========================================================

Lightweight temporal recurrent model for fast inference on low-power devices.
Processes sequences of 78-dimensional hand landmarks for dynamic gestures.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

from backend.vision.landmark_features import FEATURE_DIM


def build_gru_model(
    sequence_length: int = 30,
    feature_dim: int = FEATURE_DIM,
    num_classes: int = 3,
    l2_reg: float = 0.001,
    dropout_rate: float = 0.25,
) -> keras.Model:
    """
    Constructs a 2-layer Bidirectional GRU classifier:
    Input: (seq_len, 78)
    -> Masking(mask_value=0.0)
    -> Bidirectional(GRU(64, return_sequences=True))
    -> Dropout(0.25)
    -> Bidirectional(GRU(32))
    -> Dense(48, relu)
    -> Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=(sequence_length, feature_dim), name="temporal_gru_input")
    x = layers.Masking(mask_value=0.0, name="gru_masking")(inputs)

    x = layers.Bidirectional(
        layers.GRU(64, return_sequences=True, kernel_regularizer=regularizers.l2(l2_reg)),
        name="bi_gru_1",
    )(x)
    x = layers.Dropout(dropout_rate, name="gru_dropout_1")(x)

    x = layers.Bidirectional(
        layers.GRU(32, return_sequences=False, kernel_regularizer=regularizers.l2(l2_reg)),
        name="bi_gru_2",
    )(x)

    x = layers.Dense(48, activation="relu", kernel_regularizer=regularizers.l2(l2_reg), name="gru_dense")(x)

    outputs = layers.Dense(num_classes, activation="softmax", name="gru_probabilities")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="SignAI_BiGRU_DynamicGesture")
    return model
