"""
FastAPI Application Entry Point
===============================

Indian Sign Language (ISL) Alphabet Recognition REST API service.
Provides health monitoring and real-time hand gesture classification endpoints.
"""

from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncGenerator

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    MAX_UPLOAD_SIZE_BYTES,
    MODEL_PATH,
)
from backend.model_loader import (
    get_classes,
    is_model_loaded,
    load_model_and_labels,
)
from backend.prediction import predict_sign_alphabet
from backend.schemas import ErrorResponse, HealthResponse, PredictionResponse
from backend.routers import explainability_routes, model_routes, temporal_routes, vision_routes

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("isl_backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager that loads and validates the trained CNN model
    once during application startup.
    """
    logger.info("Initializing ISL Alphabet Recognition Backend...")
    try:
        load_model_and_labels()
        logger.info("Model and label classes initialized successfully.")
    except Exception as e:
        logger.error(f"FATAL: Model initialization failed during startup: {e}")
        raise RuntimeError(f"Startup failed: {e}") from e

    yield

    logger.info("Shutting down ISL Alphabet Recognition Backend.")


# Instantiate FastAPI application
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular API routers
app.include_router(vision_routes.router)
app.include_router(explainability_routes.router)
app.include_router(model_routes.router)
app.include_router(temporal_routes.router)


@app.get(
    "/",
    summary="Root Service Info",
    tags=["General"],
)
async def root():
    """Returns basic service metadata and links to documentation."""
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
        "predict_url": "/predict",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="System Health & Model Status",
    tags=["Diagnostics"],
)
async def health_check():
    """
    Returns the backend service health status, model loading status,
    active model name, and supported alphabet class list.
    """
    loaded = is_model_loaded()
    classes = get_classes() if loaded else []
    model_name = os.path.basename(MODEL_PATH) if loaded else None
    return HealthResponse(
        status="healthy" if loaded else "degraded",
        model_loaded=loaded,
        model_name=model_name,
        num_classes=len(classes),
        classes=classes,
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image or unreadable payload"},
        413: {"model": ErrorResponse, "description": "Payload exceeds maximum allowed size"},
        500: {"model": ErrorResponse, "description": "Internal model inference failure"},
    },
    summary="Classify Hand Gesture Image",
    tags=["Inference"],
)
async def predict_gesture(file: UploadFile = File(...)):
    """
    Receives an uploaded hand gesture image file via multipart/form-data,
    applies standardized preprocessing (128x128 RGB, normalized to [0, 1]),
    and returns the predicted ISL alphabet letter with confidence metrics.
    """
    # 1. Validate file presence
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided in the request payload.",
        )

    # 2. Validate content type if available
    content_type = file.content_type or ""
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp", "application/octet-stream"]
    if content_type and content_type.lower() not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{content_type}'. Please upload a JPEG or PNG image.",
        )

    # 3. Read image bytes with safety size limit
    try:
        image_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file payload: {e}",
        )

    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file payload is empty (0 bytes).",
        )

    if len(image_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE),
            detail=f"File exceeds maximum upload limit of {MAX_UPLOAD_SIZE_BYTES / (1024 * 1024):.1f} MB.",
        )

    # 4. Perform preprocessing and inference
    try:
        prediction_result = predict_sign_alphabet(image_bytes)
        return prediction_result
    except ValueError as e:
        logger.warning(f"Validation error during image processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Inference processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal inference failure: {e}",
        )
