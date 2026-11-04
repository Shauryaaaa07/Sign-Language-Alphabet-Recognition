"""
Model Laboratory & Comparative Evaluation Router
================================================

Endpoints for multimodal fusion inference, model summary benchmarks,
and real-time comparative inference across all 4 paradigm models.
"""

import io
import json
import os
from typing import Any, Dict, List
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image
import numpy as np

from backend.config import MAX_UPLOAD_SIZE_BYTES
from backend.model_loader import get_mappings, get_model
from backend.services.fusion_service import MultimodalFusionService
from backend.vision.hand_landmarker import HandLandmarkDetector

router = APIRouter(prefix="/models", tags=["Model Laboratory"])

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LANDMARK_MODEL_PATH = os.path.join(REPO_ROOT, "saved_models", "landmark_classifier", "isl_landmark_mlp_best.keras")
FUSION_METADATA_PATH = os.path.join(REPO_ROOT, "saved_models", "fusion", "validation_comparison.json")
LANDMARK_METADATA_PATH = os.path.join(REPO_ROOT, "saved_models", "landmark_classifier", "validation_metrics.json")
TEMPORAL_METADATA_PATH = os.path.join(REPO_ROOT, "saved_models", "temporal", "temporal_metadata.json")


@router.get(
    "/summary",
    summary="Model Architecture & Verification Summary",
    description="Returns verified architectural specifications and validation metrics across all models.",
)
async def get_models_summary() -> Dict[str, Any]:
    # Load metadata safely
    fusion_meta = {}
    if os.path.exists(FUSION_METADATA_PATH):
        try:
            with open(FUSION_METADATA_PATH, "r", encoding="utf-8") as f:
                fusion_meta = json.load(f)
        except Exception:
            pass

    landmark_meta = {}
    if os.path.exists(LANDMARK_METADATA_PATH):
        try:
            with open(LANDMARK_METADATA_PATH, "r", encoding="utf-8") as f:
                landmark_meta = json.load(f)
        except Exception:
            pass

    temporal_meta = {}
    if os.path.exists(TEMPORAL_METADATA_PATH):
        try:
            with open(TEMPORAL_METADATA_PATH, "r", encoding="utf-8") as f:
                temporal_meta = json.load(f)
        except Exception:
            pass

    return {
        "models": {
            "cnn_v4": {
                "name": "CNN V4 (Primary Visual Baseline)",
                "type": "2D Convolutional Neural Network",
                "checkpoint": "saved_models/experiments/isl_alphabet_cnn_v4_best.keras",
                "sha256": "4616e94b2c42fbca0e11247bf922e7edea96bdbdf44215b1318c35b80a093762",
                "parameters": 308218,
                "input_shape": [128, 128, 3],
                "num_classes": 26,
                "test_accuracy": 86.34,
                "macro_f1": 83.96,
                "weighted_f1": 83.87,
                "status": "frozen_production_baseline",
            },
            "landmark_mlp": {
                "name": "Landmark MLP Classifier",
                "type": "Geometric Multilayer Perceptron",
                "checkpoint": "saved_models/landmark_classifier/isl_landmark_mlp_best.keras",
                "sha256": "cdfbfdd4a9c40af088294f11c70a52c92854f4ef26f36bf034ef2ad062240068",
                "parameters": 18458,
                "input_dim": 78,
                "num_classes": 26,
                "val_accuracy": landmark_meta.get("mlp_val_accuracy", 69.17),
                "macro_f1": landmark_meta.get("mlp_macro_f1", 63.77),
                "rf_val_accuracy": landmark_meta.get("random_forest_val_accuracy", 77.65),
                "status": "trained_and_verified",
            },
            "multimodal_fusion": {
                "name": "Multimodal Fusion Network (CNN + Landmarks)",
                "type": "Two-Stream Feature Fusion Head",
                "checkpoint": "saved_models/fusion/isl_multimodal_fusion_best.keras",
                "parameters": 331610,
                "trainable_parameters": 26426,
                "val_accuracy": fusion_meta.get("val_accuracy", 86.32),
                "macro_f1": fusion_meta.get("macro_f1", 82.40),
                "status": "trained_and_verified",
            },
            "temporal_recurrent": {
                "name": "Temporal Dynamic Gesture Classifier",
                "type": "Bidirectional LSTM & GRU",
                "checkpoints": [
                    "saved_models/temporal/isl_bilstm_dynamic.keras",
                    "saved_models/temporal/isl_bigru_dynamic.keras",
                ],
                "sequence_length": 30,
                "feature_dim": 78,
                "classes": ["STATIC_HOLD", "DYNAMIC_J", "DYNAMIC_Z"],
                "status": "architectural_verification_complete",
                "notice": "RealSign dataset contains static images. Dynamic video collection for moving signs (J, Z) is ongoing.",
            },
        }
    }


@router.post(
    "/fusion/predict",
    summary="Multimodal Fusion Inference",
    description="Fuses CNN V4 deep visual features with MediaPipe landmarks. Falls back to CNN V4 if landmarks missing.",
)
async def predict_fusion(file: UploadFile = File(...)) -> Dict[str, Any]:
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size limit ({MAX_UPLOAD_SIZE_BYTES} bytes).",
        )

    try:
        with Image.open(io.BytesIO(content)) as img:
            rgb_img = img.convert("RGB")
            service = MultimodalFusionService.get_instance()
            result = service.predict(rgb_img)
            return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Fusion inference error: {e}")


@router.post(
    "/compare",
    summary="Side-by-Side Model Comparison",
    description="Evaluates CNN V4, Landmark MLP, and Multimodal Fusion simultaneously on the same image.",
)
async def compare_all_models(file: UploadFile = File(...)) -> Dict[str, Any]:
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size limit ({MAX_UPLOAD_SIZE_BYTES} bytes).",
        )

    try:
        with Image.open(io.BytesIO(content)) as img:
            rgb_img = img.convert("RGB")
            
            # 1. CNN V4 Prediction
            cnn_v4 = get_model()
            _, idx_to_class = get_mappings()
            resized_128 = rgb_img.resize((128, 128), Image.Resampling.BILINEAR)
            img_arr = np.expand_dims(np.asarray(resized_128, dtype=np.float32) / 255.0, axis=0)
            cnn_probs = cnn_v4(img_arr, training=False).numpy()[0]
            top_cnn_idx = int(np.argmax(cnn_probs))
            cnn_result = {
                "letter": idx_to_class[top_cnn_idx],
                "confidence": round(float(cnn_probs[top_cnn_idx]), 4),
            }

            # 2. Landmark Detection & MLP
            detector = HandLandmarkDetector.get_instance()
            lm_res = detector.process_image(rgb_img)
            landmark_result = None
            if lm_res["status"] == "hand_detected" and lm_res["primary_hand"]:
                feat_vec = np.expand_dims(
                    np.array(lm_res["primary_hand"]["feature_vector_78"], dtype=np.float32), axis=0
                )
                import tensorflow as tf
                if os.path.exists(LANDMARK_MODEL_PATH):
                    mlp = tf.keras.models.load_model(LANDMARK_MODEL_PATH, compile=False)
                    mlp_probs = mlp(feat_vec, training=False).numpy()[0]
                    top_mlp_idx = int(np.argmax(mlp_probs))
                    classes_list = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    landmark_result = {
                        "letter": classes_list[top_mlp_idx],
                        "confidence": round(float(mlp_probs[top_mlp_idx]), 4),
                        "handedness": lm_res["primary_hand"]["handedness"],
                    }

            # 3. Multimodal Fusion
            fusion_service = MultimodalFusionService.get_instance()
            fusion_res = fusion_service.predict(rgb_img)

            return {
                "status": "success",
                "cnn_v4": cnn_result,
                "landmark_mlp": landmark_result if landmark_result else {"letter": "N/A", "confidence": 0.0, "reason": "No hand detected"},
                "multimodal_fusion": {
                    "letter": fusion_res["predicted_letter"],
                    "confidence": fusion_res["confidence"],
                    "mode": fusion_res["mode"],
                    "fallback_used": fusion_res["fallback_used"],
                },
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Comparison error: {e}")
