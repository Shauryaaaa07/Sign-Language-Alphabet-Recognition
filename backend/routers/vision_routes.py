"""
Vision and Landmark Analysis Router
===================================

Endpoints for MediaPipe hand tracking, 21 landmark extraction,
and camera capture quality diagnostics.
"""

import io
from typing import Any, Dict
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image

from backend.config import MAX_UPLOAD_SIZE_BYTES
from backend.vision.camera_quality import CameraQualityAnalyzer
from backend.vision.hand_landmarker import HandLandmarkDetector

router = APIRouter(prefix="/vision", tags=["Computer Vision & MediaPipe"])


@router.post(
    "/landmarks",
    summary="Extract 21 Hand Landmarks & Geometry",
    description="Processes an image through MediaPipe Hand Landmarker to return 21 3D landmarks, bounding box, and 78-d features.",
)
async def extract_landmarks(file: UploadFile = File(...)) -> Dict[str, Any]:
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
            detector = HandLandmarkDetector.get_instance()
            result = detector.process_image(rgb_img)
            return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Image processing error: {e}")


@router.post(
    "/quality",
    summary="Analyze Camera Feed Quality",
    description="Evaluates brightness, contrast, Laplacian sharpness, and hand framing with actionable recommendations.",
)
async def analyze_quality(file: UploadFile = File(...)) -> Dict[str, Any]:
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
            analyzer = CameraQualityAnalyzer()
            assessment = analyzer.analyze_frame(rgb_img)
            return assessment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Quality analysis error: {e}")
