"""
Multimodal Fusion Service
=========================

Combines visual features from CNN V4 with 78-dimensional geometric MediaPipe
hand landmarks. Supports dual-hand tracking with independent evaluation strategy.
Gracefully degrades to CNN V4 if hand landmarks are not detected.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from PIL import Image
import tensorflow as tf

from backend.config import IMAGE_SIZE
from backend.model_loader import get_mappings, get_model
from backend.schemas import TopPrediction
from backend.vision.hand_landmarker import HandLandmarkDetector
from backend.vision.landmark_features import FEATURE_DIM

logger = logging.getLogger(__name__)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FUSION_MODEL_PATH = os.path.join(REPO_ROOT, "saved_models", "fusion", "isl_multimodal_fusion_best.keras")
FUSION_METADATA_PATH = os.path.join(REPO_ROOT, "saved_models", "fusion", "validation_comparison.json")
LANDMARK_MODEL_PATH = os.path.join(REPO_ROOT, "saved_models", "landmark_classifier", "isl_landmark_mlp_best.keras")


class MultimodalFusionService:
    _instance: Optional["MultimodalFusionService"] = None

    def __init__(self):
        self.fusion_model: Optional[tf.keras.Model] = None
        self.landmark_mlp: Optional[tf.keras.Model] = None
        self.metadata: Dict[str, Any] = {}
        self.classes: List[str] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.detector = HandLandmarkDetector.get_instance()
        self._load_models()

    @classmethod
    def get_instance(cls) -> "MultimodalFusionService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_models(self):
        """Loads trained multimodal fusion head and landmark MLP if checkpoints exist."""
        # 1. Fusion Model
        if os.path.exists(FUSION_MODEL_PATH):
            try:
                self.fusion_model = tf.keras.models.load_model(FUSION_MODEL_PATH, compile=False)
                logger.info(f"Loaded multimodal fusion model from {FUSION_MODEL_PATH}")
                if os.path.exists(FUSION_METADATA_PATH):
                    with open(FUSION_METADATA_PATH, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load fusion model from {FUSION_MODEL_PATH}: {e}. Fallback enabled.")
                self.fusion_model = None
        else:
            logger.info("Fusion model checkpoint not found on disk. Falling back to CNN V4.")
            self.fusion_model = None

        # 2. Landmark MLP Model for independent per-hand classification
        if os.path.exists(LANDMARK_MODEL_PATH):
            try:
                self.landmark_mlp = tf.keras.models.load_model(LANDMARK_MODEL_PATH, compile=False)
                logger.info(f"Loaded landmark MLP model from {LANDMARK_MODEL_PATH}")
            except Exception as e:
                logger.warning(f"Failed to load landmark MLP from {LANDMARK_MODEL_PATH}: {e}")
                self.landmark_mlp = None

    def predict(
        self,
        image_rgb: Image.Image,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Runs multimodal inference on an RGB PIL Image.
        
        1. Runs Hand Landmark Detector to extract 78-d feature vectors (1 or 2 hands).
        2. If landmarks are detected and fusion model is available:
           Runs multimodal model [image_tensor, primary_landmark_vector].
        3. If two hands are detected:
           Evaluates each hand independently without fabricating a combined sign.
        4. If landmarks are NOT detected or fusion model is unavailable:
           Falls back to pure CNN V4 model, returning fallback metadata.
        """
        t0 = time.perf_counter()
        
        # 1. Landmark extraction
        landmark_res = self.detector.process_image(image_rgb)
        hands = landmark_res.get("hands", [])
        num_hands = len(hands)
        has_hand = landmark_res["status"] == "hand_detected" and landmark_res["primary_hand"] is not None
        
        # 2. Prepare normalized image tensor (1, 128, 128, 3)
        resized_img = image_rgb.resize(IMAGE_SIZE, resample=Image.Resampling.BILINEAR)
        img_array = np.asarray(resized_img, dtype=np.float32) / 255.0
        image_tensor = np.expand_dims(img_array, axis=0)

        # Independent per-hand predictions
        per_hand_preds = []
        if self.landmark_mlp is not None and hands:
            for h in hands:
                try:
                    feat_batch = np.expand_dims(np.array(h["feature_vector_78"], dtype=np.float32), axis=0)
                    mlp_probs = self.landmark_mlp(feat_batch, training=False).numpy()[0]
                    h_top_idx = int(np.argmax(mlp_probs))
                    per_hand_preds.append({
                        "handedness": h["handedness"],
                        "predicted_letter": self.classes[h_top_idx],
                        "confidence": round(float(mlp_probs[h_top_idx]), 4),
                        "landmark_confidence": h["confidence"],
                    })
                except Exception:
                    pass

        # Check if multimodal inference can proceed
        if has_hand and self.fusion_model is not None:
            try:
                feature_vec = landmark_res["primary_hand"]["feature_vector_78"]
                landmark_tensor = np.expand_dims(np.array(feature_vec, dtype=np.float32), axis=0)
                
                # Multimodal forward pass on primary/dominant hand
                probs = self.fusion_model([image_tensor, landmark_tensor], training=False).numpy()[0]
                elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                
                top_idx = int(np.argmax(probs))
                top_letter = self.classes[top_idx]
                top_conf = float(probs[top_idx])
                
                sorted_indices = np.argsort(probs)[::-1][:top_k]
                top_predictions = [
                    {"letter": self.classes[i], "confidence": round(float(probs[i]), 4)}
                    for i in sorted_indices
                ]
                
                dual_strategy = "INDEPENDENT_EVALUATION" if num_hands >= 2 else "SINGLE_HAND"
                dual_notice = (
                    "Dual hands detected. Each hand is evaluated independently. "
                    "ISL alphabet models are trained on single-hand fingerspelling; "
                    "two-hand compound signs require a dedicated two-hand vocabulary."
                ) if num_hands >= 2 else None

                return {
                    "mode": "MULTIMODAL_FUSION",
                    "fallback_used": False,
                    "fallback_reason": None,
                    "predicted_letter": top_letter,
                    "confidence": round(top_conf, 4),
                    "top_predictions": top_predictions,
                    "inference_time_ms": elapsed_ms,
                    "landmark_summary": {
                        "hand_count": num_hands,
                        "handedness": landmark_res["primary_hand"]["handedness"],
                        "confidence": landmark_res["primary_hand"]["confidence"],
                        "hand_scale": landmark_res["primary_hand"]["hand_scale"],
                        "all_handedness": [h["handedness"] for h in hands],
                    },
                    "dual_hand_analysis": {
                        "is_dual_hand": num_hands >= 2,
                        "hand_count": num_hands,
                        "strategy": dual_strategy,
                        "per_hand_predictions": per_hand_preds,
                        "notice": dual_notice,
                    },
                    "status": "success",
                }
            except Exception as e:
                logger.error(f"Multimodal inference error: {e}. Falling back to CNN V4.")
                # Fallback to CNN V4 below

        # Fallback to pure CNN V4
        cnn_v4 = get_model()
        _, idx_to_class = get_mappings()
        
        probs = cnn_v4(image_tensor, training=False).numpy()[0]
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        
        top_idx = int(np.argmax(probs))
        top_letter = idx_to_class[top_idx]
        top_conf = float(probs[top_idx])
        
        sorted_indices = np.argsort(probs)[::-1][:top_k]
        top_predictions = [
            {"letter": idx_to_class[i], "confidence": round(float(probs[i]), 4)}
            for i in sorted_indices
        ]
        
        reason = "Landmarks unavailable (no hand detected)" if not has_hand else "Fusion model unavailable"
        
        return {
            "mode": "CNN_V4_FALLBACK",
            "fallback_used": True,
            "fallback_reason": reason,
            "predicted_letter": top_letter,
            "confidence": round(top_conf, 4),
            "top_predictions": top_predictions,
            "inference_time_ms": elapsed_ms,
            "landmark_summary": None,
            "dual_hand_analysis": {
                "is_dual_hand": False,
                "hand_count": 0,
                "strategy": "FALLBACK_CNN_ONLY",
                "per_hand_predictions": [],
                "notice": "Fallback to visual CNN stream.",
            },
            "status": "success",
        }
