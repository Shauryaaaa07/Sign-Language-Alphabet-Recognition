"""
Model Loader Service
====================

Manages single-instance loading and memory caching of the trained Keras CNN
model checkpoint and verified A–Z class mappings.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

import tensorflow as tf
from tensorflow import keras

from backend.config import LABEL_CLASSES_PATH, MODEL_PATH, NUM_CLASSES

# Global singleton in-memory cache
_cached_model: Optional[keras.Model] = None
_cached_classes: Optional[List[str]] = None
_cached_class_to_idx: Optional[Dict[str, int]] = None
_cached_idx_to_class: Optional[Dict[int, str]] = None


def load_model_and_labels(
    model_path: str = MODEL_PATH,
    mapping_path: str = LABEL_CLASSES_PATH,
) -> Tuple[keras.Model, List[str], Dict[str, int], Dict[int, str]]:
    """
    Loads and validates the trained CNN model checkpoint and class mapping file.
    Caches instances in global memory to prevent reloading across HTTP requests.

    Raises:
        FileNotFoundError: If checkpoint or mapping file is missing.
        ValueError: If model output shape or class mapping does not match 26 classes.
    """
    global _cached_model, _cached_classes, _cached_class_to_idx, _cached_idx_to_class

    # 1. Verify file paths
    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Trained model checkpoint not found at: {os.path.abspath(model_path)}. "
            f"Please ensure the model checkpoint file exists."
        )

    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(
            f"Class mapping file not found at: {os.path.abspath(mapping_path)}. "
            f"Please run Milestone 3.1 data pipeline setup first."
        )

    # 2. Load and validate label mappings
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            mapping_data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to parse class mapping JSON at {mapping_path}: {e}")

    classes = mapping_data.get("classes", [])
    if len(classes) != NUM_CLASSES:
        raise ValueError(
            f"Class mapping contains {len(classes)} classes; expected {NUM_CLASSES}."
        )

    c2i = mapping_data.get("class_to_index", {})
    # Convert string keys in index_to_class to integer keys
    i2c = {int(k): v for k, v in mapping_data.get("index_to_class", {}).items()}

    # 3. Load Keras Model (Once)
    print(f"[BACKEND INIT] Loading trained CNN model from: {model_path}")
    try:
        model = keras.models.load_model(model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load Keras model from {model_path}: {e}")

    # 4. Verify Model Output Shape
    output_shape = model.output_shape
    if output_shape[-1] != NUM_CLASSES:
        raise ValueError(
            f"Model output shape {output_shape} does not match expected {NUM_CLASSES} classes."
        )

    print(f"[BACKEND INIT] Model loaded successfully. Input shape: {model.input_shape}, Output shape: {output_shape}")

    # Cache into global variables
    _cached_model = model
    _cached_classes = classes
    _cached_class_to_idx = c2i
    _cached_idx_to_class = i2c

    return _cached_model, _cached_classes, _cached_class_to_idx, _cached_idx_to_class


def get_model() -> keras.Model:
    """Returns the cached model instance, loading it if not already initialized."""
    if _cached_model is None:
        load_model_and_labels()
    return _cached_model


def get_classes() -> List[str]:
    """Returns the cached list of supported ISL alphabet classes."""
    if _cached_classes is None:
        load_model_and_labels()
    return _cached_classes


def get_mappings() -> Tuple[Dict[str, int], Dict[int, str]]:
    """Returns the cached bidirectional class-to-index and index-to-class mappings."""
    if _cached_class_to_idx is None or _cached_idx_to_class is None:
        load_model_and_labels()
    return _cached_class_to_idx, _cached_idx_to_class


def is_model_loaded() -> bool:
    """Returns True if the model is currently active in memory."""
    return _cached_model is not None
