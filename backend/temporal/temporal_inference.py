"""
Temporal Dynamic Gesture Inference Engine
=========================================

Orchestrates real-time temporal sequence buffering, motion detection,
and recurrent model inference (LSTM / GRU) for dynamic signs.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import tensorflow as tf

from backend.temporal.sequence_collector import TemporalSequenceCollector
from backend.vision.landmark_features import FEATURE_DIM

logger = logging.getLogger(__name__)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPORAL_MODEL_DIR = os.path.join(REPO_ROOT, "saved_models", "temporal")
LSTM_MODEL_PATH = os.path.join(TEMPORAL_MODEL_DIR, "isl_bilstm_dynamic.keras")
TEMPORAL_METADATA_PATH = os.path.join(TEMPORAL_MODEL_DIR, "temporal_metadata.json")

DYNAMIC_GESTURE_DISCLAIMER = (
    "Dynamic gesture recognition infrastructure (BiLSTM/BiGRU) is implemented and verified. "
    "Full multi-signer dynamic dataset recording for moving signs (J, Z) is pending physical video collection."
)


class TemporalInferenceEngine:
    _instance: Optional["TemporalInferenceEngine"] = None

    def __init__(self, sequence_length: int = 30, motion_threshold: float = 0.05):
        self.sequence_length = sequence_length
        self.collector = TemporalSequenceCollector(
            buffer_size=sequence_length,
            motion_threshold=motion_threshold,
            cooldown_seconds=1.5,
        )
        self.classes: List[str] = ["STATIC_HOLD", "DYNAMIC_J", "DYNAMIC_Z"]
        self.model: Optional[tf.keras.Model] = None
        self._load_model()

    @classmethod
    def get_instance(cls) -> "TemporalInferenceEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self):
        """Loads trained temporal model checkpoint if available."""
        if os.path.exists(LSTM_MODEL_PATH):
            try:
                self.model = tf.keras.models.load_model(LSTM_MODEL_PATH, compile=False)
                logger.info(f"Loaded temporal model from {LSTM_MODEL_PATH}")
                if os.path.exists(TEMPORAL_METADATA_PATH):
                    with open(TEMPORAL_METADATA_PATH, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        self.classes = meta.get("classes", self.classes)
            except Exception as e:
                logger.warning(f"Could not load temporal model from {LSTM_MODEL_PATH}: {e}")
                self.model = None

    def push_frame(
        self,
        landmark_feature_78: Optional[np.ndarray],
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Feeds a frame into the temporal collector.
        If the buffer is ready, hand motion is significant, and cooldown has elapsed,
        it triggers dynamic gesture inference.
        """
        now = timestamp if timestamp is not None else time.time()
        self.collector.add_frame(landmark_feature_78, timestamp=now)

        stats = self.collector.get_stats()

        # Cooldown check
        if stats["in_cooldown"]:
            return {
                "state": "COOLDOWN",
                "motion_energy": stats["motion_energy"],
                "is_dynamic_motion": stats["is_dynamic_motion"],
                "predicted_gesture": None,
                "confidence": None,
                "cooldown_remaining_s": stats["cooldown_remaining_s"],
                "disclaimer": DYNAMIC_GESTURE_DISCLAIMER,
            }

        # Buffer accumulation check
        if not self.collector.is_ready(min_frames=15):
            return {
                "state": "BUFFERING",
                "buffer_length": stats["buffer_length"],
                "buffer_target": self.sequence_length,
                "motion_energy": stats["motion_energy"],
                "is_dynamic_motion": stats["is_dynamic_motion"],
                "predicted_gesture": None,
                "confidence": None,
                "disclaimer": DYNAMIC_GESTURE_DISCLAIMER,
            }

        # If motion is dynamic and model is available, perform prediction
        if stats["is_dynamic_motion"] and self.model is not None:
            seq_tensor = self.collector.get_normalized_sequence(self.sequence_length)
            probs = self.model(seq_tensor, training=False).numpy()[0]
            top_idx = int(np.argmax(probs))
            predicted_class = self.classes[top_idx]
            conf = float(probs[top_idx])

            if predicted_class != "STATIC_HOLD" and conf >= 0.65:
                self.collector.mark_triggered(now)
                return {
                    "state": "TRIGGERED",
                    "motion_energy": stats["motion_energy"],
                    "is_dynamic_motion": True,
                    "predicted_gesture": predicted_class,
                    "confidence": round(conf, 4),
                    "probabilities": {self.classes[i]: round(float(probs[i]), 4) for i in range(len(self.classes))},
                    "disclaimer": DYNAMIC_GESTURE_DISCLAIMER,
                }

        return {
            "state": "IDLE" if not stats["is_dynamic_motion"] else "TRACKING",
            "motion_energy": stats["motion_energy"],
            "is_dynamic_motion": stats["is_dynamic_motion"],
            "predicted_gesture": None,
            "confidence": None,
            "disclaimer": DYNAMIC_GESTURE_DISCLAIMER,
        }

    def reset(self):
        """Resets the internal temporal buffer."""
        self.collector.clear()
