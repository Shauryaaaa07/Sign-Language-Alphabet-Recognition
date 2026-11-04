"""
Landmark Model Architecture Definitions
=======================================

Provides Multi-Layer Perceptron (MLP) and Random Forest classifiers
operating on 78-dimensional geometric hand landmark feature vectors.
"""

from typing import Tuple
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers


def build_landmark_mlp(
    input_dim: int = 78,
    num_classes: int = 26,
    l2_reg: float = 0.0005,
    dropout_rate: float = 0.3,
) -> keras.Model:
    """
    Constructs a regularized Multi-Layer Perceptron for landmark classification.
    Topology:
      Input(78)
      -> Dense(128, ReLU, L2) -> BatchNorm -> Dropout
      -> Dense(64, ReLU, L2) -> BatchNorm -> Dropout
      -> Dense(26, Softmax)
    """
    inputs = keras.Input(shape=(input_dim,), name="landmark_features_78")

    x = layers.Dense(
        128,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="dense_layer_1",
    )(inputs)
    x = layers.BatchNormalization(name="bn_1")(x)
    x = layers.Dropout(dropout_rate, name="dropout_1")(x)

    x = layers.Dense(
        64,
        activation="relu",
        kernel_regularizer=regularizers.l2(l2_reg),
        name="dense_layer_2",
    )(x)
    x = layers.BatchNormalization(name="bn_2")(x)
    x = layers.Dropout(dropout_rate * 0.75, name="dropout_2")(x)

    outputs = layers.Dense(
        num_classes,
        activation="softmax",
        name="landmark_probabilities",
    )(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="SignAI_Landmark_MLP")
    return model
