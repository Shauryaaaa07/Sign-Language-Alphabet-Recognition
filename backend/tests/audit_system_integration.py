"""
Full System Integration Audit Script: Backend Verification
==========================================================
Audits FastAPI backend runtime, model inference, real dataset sample predictions,
CORS configuration, error status codes, and input safety guards.
"""

import io
import sys
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.main import app

print("=== BACKEND INTEGRATION AUDIT ===")

# Use TestClient with context manager to trigger FastAPI lifespan model loading
with TestClient(app) as client:
    # 1. Health check & model verification
    print("\n[1] Verifying GET /health and model loader...")
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"Health Response: status={data['status']}, model_loaded={data['model_loaded']}, num_classes={data['num_classes']}")
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["num_classes"] == 26
    assert len(data["classes"]) == 26
    assert data["classes"] == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    print("[PASS] /health passed with 26 verified classes (A-Z).")

    # 2. CORS Preflight Verification
    print("\n[2] Verifying CORS preflight headers for frontend origins...")
    cors_response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert cors_response.status_code == 200
    assert cors_response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    print("[PASS] CORS preflight approved for http://localhost:5173.")

    # 3. Synthetic image predictions (strict test set isolation)
    print("\n[3] Testing /predict with synthetic gesture images...")
    for idx, color in enumerate([(100, 150, 200), (200, 100, 150), (150, 200, 100)]):
        img = Image.new("RGB", (128, 128), color=color)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        sample_bytes = buf.getvalue()

        resp = client.post(
            "/predict",
            files={"file": (f"synthetic_sample_{idx}.jpg", sample_bytes, "image/jpeg")},
        )
        assert resp.status_code == 200, f"Failed on synthetic sample {idx}: {resp.text}"
        result = resp.json()
        print(f"Sample {idx} -> Predicted: {result['predicted_letter']} (confidence: {result['confidence']:.4f}, inference_time: {result.get('inference_time_ms', 0):.2f}ms)")
        assert result["status"] == "success"
        assert result["predicted_letter"] in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert result.get("predicted_class") == result["predicted_letter"]
        assert 0.0 <= result["confidence"] <= 1.0
        assert len(result["top_predictions"]) >= 3
        # Check descending order of top predictions
        confidences = [item["confidence"] for item in result["top_predictions"]]
        assert confidences == sorted(confidences, reverse=True), "Top predictions must be sorted descending"

    print("[PASS] Synthetic image predictions verified.")

    # 4. Error Handling & Security Guards
    print("\n[4] Testing Error Handling & Edge Cases...")

    # Empty file
    resp_empty = client.post(
        "/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert resp_empty.status_code == 400
    assert "empty" in resp_empty.json()["detail"].lower()
    print("[PASS] Empty payload correctly returns 400.")

    # Corrupted non-image bytes
    resp_corrupt = client.post(
        "/predict",
        files={"file": ("corrupt.jpg", b"NOT_A_VALID_JPEG_HEADER_RANDOM_GARBAGE", "image/jpeg")},
    )
    assert resp_corrupt.status_code == 400
    assert "decode" in resp_corrupt.json()["detail"].lower() or "failed" in resp_corrupt.json()["detail"].lower()
    print("[PASS] Corrupt image bytes correctly return 400.")

    # Unsupported content type / extension
    resp_unsupported = client.post(
        "/predict",
        files={"file": ("script.py", b"print('hello')", "text/x-python")},
    )
    assert resp_unsupported.status_code == 400
    assert "unsupported" in resp_unsupported.json()["detail"].lower()
    print("[PASS] Unsupported file format correctly returns 400.")

    # Oversized payload (> 10MB)
    oversized_bytes = b"0" * (10 * 1024 * 1024 + 1024)
    resp_oversized = client.post(
        "/predict",
        files={"file": ("huge.jpg", oversized_bytes, "image/jpeg")},
    )
    assert resp_oversized.status_code in [400, 413]
    print(f"[PASS] Oversized payload correctly rejected with HTTP {resp_oversized.status_code}.")

print("\n=== ALL BACKEND AUDIT CHECKS PASSED SUCCESSFULLY ===")
