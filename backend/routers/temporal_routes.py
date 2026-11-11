"""
Temporal Gesture Recognition Router
===================================

Endpoints for real-time temporal hand landmark sequence streaming,
motion energy tracking, and dynamic gesture inference.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel

from backend.temporal.temporal_inference import TemporalInferenceEngine

router = APIRouter(prefix="/temporal", tags=["Temporal Dynamic Gestures"])


class TemporalFramePayload(BaseModel):
    feature_vector_78: Optional[List[float]] = None
    timestamp: Optional[float] = None


@router.post(
    "/stream",
    summary="Push Frame to Temporal Buffer",
    description="Streams a landmark feature vector into the sliding temporal window and returns tracking/gesture status.",
)
async def stream_frame(payload: TemporalFramePayload) -> Dict[str, Any]:
    engine = TemporalInferenceEngine.get_instance()
    res = engine.push_frame(payload.feature_vector_78, timestamp=payload.timestamp)
    return res


@router.post(
    "/reset",
    summary="Reset Temporal Buffer",
    description="Clears the sliding temporal frame queue.",
)
async def reset_temporal() -> Dict[str, str]:
    engine = TemporalInferenceEngine.get_instance()
    engine.reset()
    return {"status": "success", "message": "Temporal sequence buffer reset."}


@router.get(
    "/status",
    summary="Temporal Engine Status",
    description="Returns current buffer fullness, motion energy, and cooldown status.",
)
async def get_temporal_status() -> Dict[str, Any]:
    engine = TemporalInferenceEngine.get_instance()
    return engine.collector.get_stats()
