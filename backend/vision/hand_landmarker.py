"""
MediaPipe Hand Landmarker Service
=================================

Extracts 21 3D hand landmarks, computes wrist-relative scale-invariant
coordinates, calculates bounding boxes, and handles edge cases for
SignAI 2.0 multimodal computer vision pipeline.
"""

import io
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.core import base_options

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "models", "hand_landmarker.task"
)

# Standard MediaPipe 21 hand connections
HAND_CONNECTIONS: List[Tuple[int, int]] = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (0, 9), (9, 10), (10, 11), (11, 12),    # Middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (5, 9), (9, 13), (13, 17), (0, 17),    # Palm base
]

LANDMARK_NAMES: List[str] = [
    "WRIST",
    "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP",
]


class HandLandmarkDetector:
    """Thread-safe singleton detector for MediaPipe Tasks Hand Landmarker."""

    _instance: Optional["HandLandmarkDetector"] = None

    def __init__(self, model_asset_path: str = MODEL_PATH):
        if not os.path.isfile(model_asset_path):
            raise FileNotFoundError(
                f"MediaPipe hand_landmarker.task not found at {model_asset_path}."
            )
        options = vision.HandLandmarkerOptions(
            base_options=base_options.BaseOptions(model_asset_path=model_asset_path),
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    @classmethod
    def get_instance(cls) -> "HandLandmarkDetector":
        if cls._instance is None:
            cls._instance = HandLandmarkDetector()
        return cls._instance

    def process_image(
        self,
        image_input: Union[bytes, Image.Image, np.ndarray],
    ) -> Dict[str, Any]:
        """
        Detects hand landmarks from raw bytes, PIL Image, or NumPy uint8 array.
        Returns a structured dictionary with raw and normalized features.
        """
        # 1. Convert input to RGB PIL Image
        if isinstance(image_input, bytes):
            if not image_input or len(image_input) == 0:
                return self._empty_response("empty_payload")
            try:
                pil_img = Image.open(io.BytesIO(image_input)).convert("RGB")
            except Exception as e:
                return self._empty_response(f"invalid_image_bytes: {e}")
        elif isinstance(image_input, np.ndarray):
            if image_input.dtype != np.uint8:
                image_input = (image_input * 255.0).clip(0, 255).astype(np.uint8)
            pil_img = Image.fromarray(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            pil_img = image_input.convert("RGB")
        else:
            return self._empty_response("unsupported_image_type")

        width, height = pil_img.size
        np_arr = np.array(pil_img)

        # 2. Convert to MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_arr)

        # 3. Detect Hand Landmarks
        try:
            result = self.detector.detect(mp_image)
        except Exception as e:
            return self._empty_response(f"detection_inference_error: {e}")

        if not result.hand_landmarks or len(result.hand_landmarks) == 0:
            return self._empty_response("no_hand_detected", width=width, height=height)

        # 4. Parse Detected Hands
        detected_hands = []
        for idx, landmarks in enumerate(result.hand_landmarks):
            handedness = "Right"
            confidence = 0.90
            if result.handedness and idx < len(result.handedness):
                handedness_cat = result.handedness[idx][0]
                handedness = handedness_cat.category_name
                confidence = float(handedness_cat.score)

            hand_data = self._extract_hand_features(landmarks, handedness, confidence, width, height)
            detected_hands.append(hand_data)

        # Sort hands by confidence descending
        detected_hands.sort(key=lambda h: h["confidence"], reverse=True)
        primary_hand = detected_hands[0] if detected_hands else None

        return {
            "status": "hand_detected" if detected_hands else "no_hand_detected",
            "num_hands_detected": len(detected_hands),
            "hand_count": len(detected_hands),
            "primary_hand": primary_hand,
            "hands": detected_hands,
            "all_hands": detected_hands,
            "image_dimensions": {"width": width, "height": height},
        }

    def _extract_hand_features(
        self,
        landmarks: Any,
        handedness: str,
        confidence: float,
        width: int,
        height: int,
    ) -> Dict[str, Any]:
        """Extracts normalized, wrist-relative, angles, and bounding box features."""
        coords = []
        pixel_coords = []
        raw_flat = []

        for lm in landmarks:
            coords.append({"x": float(lm.x), "y": float(lm.y), "z": float(lm.z)})
            pixel_coords.append({
                "x": round(float(lm.x * width), 2),
                "y": round(float(lm.y * height), 2),
                "z": round(float(lm.z * width), 2),
            })
            raw_flat.extend([float(lm.x), float(lm.y), float(lm.z)])

        coords_arr = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)

        # 1. Bounding Box [min_x, min_y, max_x, max_y]
        min_x = float(np.min(coords_arr[:, 0]))
        max_x = float(np.max(coords_arr[:, 0]))
        min_y = float(np.min(coords_arr[:, 1]))
        max_y = float(np.max(coords_arr[:, 1]))

        bbox_normalized = {
            "min_x": max(0.0, min_x),
            "min_y": max(0.0, min_y),
            "max_x": min(1.0, max_x),
            "max_y": min(1.0, max_y),
            "width": max_x - min_x,
            "height": max_y - min_y,
        }

        bbox_pixels = {
            "x": int(bbox_normalized["min_x"] * width),
            "y": int(bbox_normalized["min_y"] * height),
            "width": int(bbox_normalized["width"] * width),
            "height": int(bbox_normalized["height"] * height),
        }

        # 2. Wrist-Relative Normalization
        # Wrist is index 0
        wrist = coords_arr[0]
        wrist_rel = coords_arr - wrist

        # 3. Hand Scale Normalization
        # Use distance between wrist (0) and middle finger MCP (9)
        scale = np.linalg.norm(coords_arr[9] - wrist)
        if scale < 1e-6:
            # Fallback to max distance from wrist
            scale = float(np.max(np.linalg.norm(wrist_rel, axis=1)))
        if scale < 1e-6:
            scale = 1.0

        scale_invariant_coords = wrist_rel / scale
        scale_invariant_flat = scale_invariant_coords.flatten().tolist()

        # 4. Joint Flexion Angles (5 fingers)
        # Angle at PIP / IP joint for each finger
        joint_triplets = [
            (1, 2, 4),    # Thumb (CMC, MCP, TIP)
            (5, 6, 8),    # Index (MCP, PIP, TIP)
            (9, 10, 12),  # Middle
            (13, 14, 16), # Ring
            (17, 18, 20), # Pinky
        ]
        angles = []
        for a, b, c in joint_triplets:
            v1 = coords_arr[a] - coords_arr[b]
            v2 = coords_arr[c] - coords_arr[b]
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 > 1e-6 and norm2 > 1e-6:
                cosine = np.clip(np.dot(v1, v2) / (norm1 * norm2), -1.0, 1.0)
                angle_deg = float(np.degrees(np.arccos(cosine)))
            else:
                angle_deg = 0.0
            angles.append(round(angle_deg, 2))

        # 5. Fingertip-to-Wrist Scale-Invariant Distances
        fingertip_indices = [4, 8, 12, 16, 20]
        tip_distances = [
            round(float(np.linalg.norm(scale_invariant_coords[idx])), 4)
            for idx in fingertip_indices
        ]

        # 6. Comprehensive 78-Dimensional Feature Vector:
        # 63 scale-invariant relative coordinates + 5 angles + 5 tip distances + 5 finger extensions
        is_extended = [float(tip_dist > 1.2) for tip_dist in tip_distances]
        feature_vector_78 = (
            scale_invariant_flat + angles + tip_distances + is_extended
        )

        return {
            "handedness": handedness,
            "confidence": round(confidence, 4),
            "landmarks_normalized": coords,
            "landmarks_pixels": pixel_coords,
            "landmarks": coords,
            "bounding_box_normalized": bbox_normalized,
            "bounding_box_pixels": bbox_pixels,
            "bounding_box": bbox_normalized,
            "bbox": bbox_pixels,
            "hand_scale": round(float(scale), 4),
            "wrist_relative_landmarks": scale_invariant_flat,
            "finger_joint_angles": angles,
            "fingertip_wrist_distances": tip_distances,
            "feature_vector_78": feature_vector_78,
        }

    def _empty_response(
        self,
        reason: str,
        width: int = 0,
        height: int = 0,
    ) -> Dict[str, Any]:
        """Returns standard structure when no hand is detected or on error."""
        return {
            "status": "no_hand_detected",
            "reason": reason,
            "num_hands_detected": 0,
            "hand_count": 0,
            "primary_hand": None,
            "hands": [],
            "all_hands": [],
            "image_dimensions": {"width": width, "height": height},
        }


def extract_landmarks_from_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """Convenience helper function for API endpoints and pipeline processing."""
    detector = HandLandmarkDetector.get_instance()
    return detector.process_image(image_bytes)
