"""
Pydantic Data Schemas
=====================

Request and response schemas for the ISL Alphabet Recognition API endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class TopPrediction(BaseModel):
    """Individual letter candidate prediction with confidence score."""
    letter: str = Field(..., description="Predicted ISL alphabet letter (A-Z)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model softmax probability score")


class PredictionResponse(BaseModel):
    """Inference response schema returned by the /predict endpoint."""
    predicted_letter: str = Field(..., description="Top predicted ISL alphabet letter")
    predicted_class: str = Field(..., description="Top predicted ISL class label (alias for predicted_letter)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Highest model prediction probability")
    top_predictions: List[TopPrediction] = Field(
        ...,
        description="Top-3 candidate predictions sorted in descending order of confidence",
    )
    inference_time_ms: Optional[float] = Field(
        None,
        description="End-to-end model inference duration in milliseconds",
    )
    status: str = Field(default="success", description="Processing execution status")


class HealthResponse(BaseModel):
    """System health response schema returned by the /health endpoint."""
    status: str = Field(..., description="Operational service status ('healthy' or 'degraded')")
    model_loaded: bool = Field(..., description="Whether the CNN checkpoint is loaded into memory")
    model_name: Optional[str] = Field(
        default=None,
        description="Filename of the currently active model checkpoint",
    )
    num_classes: int = Field(..., description="Number of supported ISL alphabet classes")
    classes: List[str] = Field(..., description="Alphabetical list of supported class labels")


class ErrorResponse(BaseModel):
    """Standardized error response schema."""
    detail: str = Field(..., description="Human-readable explanation of the error")
