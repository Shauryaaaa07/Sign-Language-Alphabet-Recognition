"""
Bidirectional LSTM Temporal Architecture for Dynamic Gestures
============================================================

Processes variable/normalized sequences of 78-dimensional hand landmarks
to classify dynamic sign trajectories (e.g., dynamic letters J, Z).
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers

from backend.vision.landmark_features import FEATURE_DIM


def build_lstm_model(
    sequence_length: int = 30,
    feature_dim: int = FEATURE_DIM,
    num_classes: int = 3,
    l2_reg: float = 0.001,
    dropout_rate: float = 0.30,
) -> keras.Model:
    """
    Constructs a 2-layer Bidirectional LSTM classifier:
    Input: (seq_len, 78)
    -> Masking(mask_value=0.0)
    -> Bidirectional(LSTM(64, return_sequences=True))
    -> Dropout(0.3)
    -> Bidirectional(LSTM(32))
    -> Dense(64, relu)
    -> Dropout(0.2)
    -> Dense(num_classes, softmax)
    """
    inputs = keras.Input(shape=(sequence_length, feature_dim), name="temporal_sequence_input")
    x = layers.Masking(mask_value=0.0, name="masking_layer")(inputs)

    x = layers.Bidirectional(
        layers.LSTM(64, return_sequences=True, kernel_regularizer=regularizers.l2(l2_reg)),
        name="bi_lstm_1",
    )(x)
    x = layers.Dropout(dropout_rate, name="lstm_dropout_1")(x)

    x = layers.Bidirectional(
        layers.LSTM(32, return_sequences=False, kernel_regularizer=regularizers.l2(l2_reg)),
        name="bi_lstm_2",
    )(x)

    x = layers.Dense(64, activation="relu", kernel_regularizer=regularizers.l2(l2_reg), name="temporal_dense")(x)
    x = layers.Dropout(0.2, name="temporal_dropout_2")(x)

    outputs = layers.Dense(num_classes, activation="softmax", name="temporal_probabilities")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="SignAI_BiLSTM_DynamicGesture")
    return model
