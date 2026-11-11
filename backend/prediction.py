"""
Image Preprocessing and Prediction Service
==========================================

Handles safe image decoding, preprocessing consistent with the training pipeline,
and model inference for ISL alphabet fingerspelling recognition.
"""

import io
import time
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
import tensorflow as tf

from backend.config import IMAGE_SIZE
from backend.model_loader import get_mappings, get_model
from backend.schemas import PredictionResponse, TopPrediction


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Decodes raw image bytes and applies preprocessing strictly consistent with
    the training data pipeline:
    1. Decodes and converts to RGB (3 channels).
    2. Resizes to 128x128 using bilinear interpolation.
    3. Converts to float32 array.
    4. Normalizes pixel values to [0.0, 1.0] by dividing by 255.0.
    5. Adds batch dimension yielding shape (1, 128, 128, 3).

    Raises:
        ValueError: If image bytes are empty, truncated, or unreadable.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("Image payload is empty (0 bytes).")

    try:
        # 1. Open with Pillow safely
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Force raster load to catch corrupted image data
            img.load()

            # 2. Convert to RGB (handles RGBA, grayscale, or palette images)
            rgb_img = img.convert("RGB")

            # 3. Resize to 128x128 with bilinear interpolation
            resized_img = rgb_img.resize(IMAGE_SIZE, resample=Image.Resampling.BILINEAR)

            # 4. Convert to float32 NumPy array
            img_array = np.asarray(resized_img, dtype=np.float32)

            # 5. Normalize pixel values to [0.0, 1.0]
            normalized_array = img_array / 255.0

            # 6. Add batch dimension -> (1, 128, 128, 3)
            batch_tensor = np.expand_dims(normalized_array, axis=0)

            return batch_tensor

    except (UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Failed to decode image file. Ensure it is a valid JPEG/PNG image: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected image preprocessing error: {e}")


def predict_sign_alphabet(image_bytes: bytes, top_k: int = 3) -> PredictionResponse:
    """
    Performs end-to-end model inference on an uploaded hand gesture image.

    Returns:
        PredictionResponse containing:
        - predicted_letter: Alphabetical class with highest softmax score (A–Z)
        - predicted_class: Class label alias matching predicted_letter
        - confidence: Model softmax probability score (bounded in [0.0, 1.0])
        - top_predictions: Top-K candidate letters and their scores
        - inference_time_ms: Wall-clock inference time in milliseconds
        - status: 'success'
    """
    # 1. Preprocess image
    input_tensor = preprocess_image(image_bytes)

    # 2. Fetch cached model and label mappings
    model = get_model()
    _, idx_to_class = get_mappings()

    # 3. Feed-forward inference (inference mode, training=False)
    t0 = time.perf_counter()
    raw_predictions = model(input_tensor, training=False).numpy()[0]
    inference_time_ms = round((time.perf_counter() - t0) * 1000.0, 2)

    # 4. Identify top predicted class
    top_index = int(np.argmax(raw_predictions))
    top_letter = idx_to_class[top_index]
    top_confidence = float(raw_predictions[top_index])

    # 5. Extract Top-K predictions
    sorted_indices = np.argsort(raw_predictions)[::-1][:top_k]
    top_predictions: List[TopPrediction] = [
        TopPrediction(
            letter=idx_to_class[int(idx)],
            confidence=float(raw_predictions[idx]),
        )
        for idx in sorted_indices
    ]

    return PredictionResponse(
        predicted_letter=top_letter,
        predicted_class=top_letter,
        confidence=round(top_confidence, 4),
        top_predictions=top_predictions,
        inference_time_ms=inference_time_ms,
        status="success",
    )
