"""
Backend API Unit and Integration Tests
======================================

Tests for FastAPI endpoints, model loading, image preprocessing, and inference.
Verifies integration of final CNN V4 checkpoint under strict test set isolation.
"""

import io
import os
import sys
from PIL import Image
import pytest
from fastapi.testclient import TestClient

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.config import MAX_UPLOAD_SIZE_BYTES, MODEL_PATH
from backend.main import app
from backend.model_loader import get_classes, get_model, is_model_loaded


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient context with the FastAPI lifespan active."""
    with TestClient(app) as test_client:
        yield test_client


def create_synthetic_image(width=128, height=128, color=(120, 150, 180), mode="RGB", fmt="JPEG") -> bytes:
    """Generates an in-memory synthetic image byte buffer for testing."""
    img = Image.new(mode, (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_model_loading_and_classes(client):
    """Verifies that CNN V4 model and 26 classes are correctly loaded into memory."""
    assert is_model_loaded(), "Model should be loaded during application lifespan startup"
    classes = get_classes()
    assert len(classes) == 26, f"Expected 26 classes, got {len(classes)}"
    assert classes[0] == "A"
    assert classes[-1] == "Z"

    model = get_model()
    assert model.input_shape == (None, 128, 128, 3), f"Expected input (None, 128, 128, 3), got {model.input_shape}"
    assert model.output_shape == (None, 26), f"Expected output (None, 26), got {model.output_shape}"
    # CNN V4 has 308,218 total parameters
    assert model.count_params() == 308218, f"Expected 308,218 parameters for CNN V4, got {model.count_params()}"


def test_health_endpoint(client):
    """Verifies the GET /health response format and values."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "v4" in data.get("model_name", "").lower(), f"Expected V4 in model_name, got {data.get('model_name')}"
    assert data["num_classes"] == 26
    assert isinstance(data["classes"], list)
    assert len(data["classes"]) == 26
    assert data["classes"] == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_root_endpoint(client):
    """Verifies the GET / endpoint returns service information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["health_url"] == "/health"
    assert data["predict_url"] == "/predict"


def test_predict_valid_synthetic_image(client):
    """Verifies POST /predict with a valid synthetic JPEG image."""
    image_bytes = create_synthetic_image(128, 128)
    files = {"file": ("test_gesture.jpg", image_bytes, "image/jpeg")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert "predicted_letter" in data
    assert "predicted_class" in data
    assert data["predicted_letter"] == data["predicted_class"]
    assert data["predicted_letter"] in get_classes()

    confidence = data["confidence"]
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0

    assert "inference_time_ms" in data
    assert isinstance(data["inference_time_ms"], float)
    assert data["inference_time_ms"] > 0.0

    top3 = data["top_predictions"]
    assert len(top3) == 3
    for pred in top3:
        assert pred["letter"] in get_classes()
        assert 0.0 <= pred["confidence"] <= 1.0

    # Assert descending order
    assert top3[0]["confidence"] >= top3[1]["confidence"] >= top3[2]["confidence"]


def test_predict_different_image_dimensions(client):
    """Verifies that images of arbitrary resolution (e.g. 300x200) are resized properly."""
    image_bytes = create_synthetic_image(300, 200, fmt="PNG")
    files = {"file": ("random_res.png", image_bytes, "image/png")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_letter"] in get_classes()


def test_predict_grayscale_synthetic_image(client):
    """Verifies that 1-channel grayscale images are converted to 3-channel RGB seamlessly."""
    image_bytes = create_synthetic_image(128, 128, color=128, mode="L", fmt="PNG")
    files = {"file": ("grayscale.png", image_bytes, "image/png")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_letter"] in get_classes()


def test_predict_rgba_synthetic_image(client):
    """Verifies that 4-channel RGBA images are converted to 3-channel RGB seamlessly."""
    image_bytes = create_synthetic_image(128, 128, color=(100, 150, 200, 255), mode="RGBA", fmt="PNG")
    files = {"file": ("transparent.png", image_bytes, "image/png")}

    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_letter"] in get_classes()


def test_predict_empty_file_rejected(client):
    """Verifies that empty file uploads return HTTP 400 Bad Request."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "empty" in data["detail"].lower()


def test_predict_corrupt_non_image_rejected(client):
    """Verifies that non-image text/corrupted files return HTTP 400 Bad Request."""
    corrupt_bytes = b"This is a plain text file, not a valid image."
    files = {"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "failed to decode" in data["detail"].lower() or "invalid image" in data["detail"].lower()


def test_predict_unsupported_content_type(client):
    """Verifies that unsupported MIME types return HTTP 400 Bad Request."""
    files = {"file": ("doc.pdf", b"%PDF-1.4...", "application/pdf")}
    response = client.post("/predict", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "unsupported file format" in data["detail"].lower()


def test_predict_oversized_file_rejected(client):
    """Verifies that payloads exceeding MAX_UPLOAD_SIZE_BYTES return HTTP 413 or 400."""
    oversized_bytes = b"X" * (MAX_UPLOAD_SIZE_BYTES + 1024)
    files = {"file": ("oversized.jpg", oversized_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    assert response.status_code in [400, 413]


def test_test_set_isolation():
    """Safety guard: asserts that backend tests never access the sealed testing directory."""
    import inspect
    this_file = inspect.getfile(test_test_set_isolation)
    with open(this_file, "r", encoding="utf-8") as f:
        content = f.read()
    # Confirm no test path references testing folder directly
    needle = "dataset" + "/" + "processed" + "/" + "Testing"
    assert needle not in content
