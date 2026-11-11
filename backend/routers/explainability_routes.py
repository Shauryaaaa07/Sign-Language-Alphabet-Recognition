"""
Explainability and Grad-CAM Router
==================================

Provides Gradient-weighted Class Activation Mapping (Grad-CAM) explanations
for the frozen CNN V4 model at layer `block3_conv2`.
"""

from typing import Any, Dict
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from backend.config import MAX_UPLOAD_SIZE_BYTES
from backend.explainability.explainability_service import explain_prediction

router = APIRouter(prefix="/explain", tags=["Explainable AI (Grad-CAM)"])


@router.post(
    "/gradcam",
    summary="Generate Grad-CAM Attention Heatmap",
    description="Computes gradient-weighted activation maps for CNN V4 (layer block3_conv2) with visual overlay.",
)
async def generate_gradcam_explanation(
    file: UploadFile = File(...),
    target_class: int = Query(-1, description="Target class index (0-25), or -1 for top predicted class"),
    alpha: float = Query(0.45, ge=0.0, le=1.0, description="Heatmap overlay blend intensity"),
) -> Dict[str, Any]:
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size limit ({MAX_UPLOAD_SIZE_BYTES} bytes).",
        )

    try:
        c_idx = None if target_class < 0 else target_class
        result = explain_prediction(content, class_idx=c_idx, alpha=alpha)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Explainability error: {e}")
