"""
Explainability Service Orchestrator
===================================

Coordinates Grad-CAM visual attribution on CNN V4 for user-uploaded images or webcam frames.
"""

from typing import Any, Dict, Optional, Union
import numpy as np
from PIL import Image

from backend.explainability.gradcam import GradCAMExplainer, TARGET_CONV_LAYER
from backend.explainability.heatmap_generator import overlay_heatmap_on_image
from backend.model_loader import get_mappings, get_model
from backend.prediction import preprocess_image

_explainer_instance: Optional[GradCAMExplainer] = None


def get_explainer() -> GradCAMExplainer:
    global _explainer_instance
    if _explainer_instance is None:
        model = get_model()
        _explainer_instance = GradCAMExplainer(model, layer_name=TARGET_CONV_LAYER)
    return _explainer_instance


def explain_prediction(
    image_bytes: bytes,
    class_idx: Optional[int] = None,
    alpha: float = 0.45,
) -> Dict[str, Any]:
    """
    Executes CNN inference and generates a Grad-CAM attribution heatmap.

    Returns:
        Structured response with predicted letter, top predictions,
        layer name, original/heatmap/overlay base64 data URIs, and academic disclaimer.
    """
    # 1. Preprocess for model input (1, 128, 128, 3)
    input_tensor = preprocess_image(image_bytes)

    # 2. Get mappings and explainer
    _, idx_to_class = get_mappings()
    explainer = get_explainer()

    # 3. Generate heatmap
    heatmap, pred_idx, confidence = explainer.generate_heatmap(
        input_tensor, class_idx=class_idx
    )
    predicted_letter = idx_to_class[pred_idx]

    # 4. Generate Top-3 predictions
    model = get_model()
    raw_probs = model(input_tensor, training=False).numpy()[0]
    top_indices = np.argsort(raw_probs)[::-1][:3]
    top_predictions = [
        {"letter": idx_to_class[i], "confidence": round(float(raw_probs[i]), 4)}
        for i in top_indices
    ]

    # 5. Generate Colormapped and Blended Overlay Base64
    _, _, heatmap_b64, overlay_b64 = overlay_heatmap_on_image(
        heatmap, image_bytes, alpha=alpha
    )

    return {
        "status": "success",
        "predicted_letter": predicted_letter,
        "predicted_class_idx": int(pred_idx),
        "confidence": round(float(confidence), 4),
        "top_predictions": top_predictions,
        "target_layer_name": explainer.layer_name,
        "heatmap_base64": heatmap_b64,
        "overlay_base64": overlay_b64,
        "academic_note": (
            "Grad-CAM visualizes gradient-weighted activations in layer block3_conv2. "
            "Warm regions (red/orange) represent high influence on the prediction; "
            "cool regions (blue) indicate negligible activation. Heatmaps indicate "
            "statistical sensitivity and do not constitute proof of human-like reasoning."
        ),
    }
