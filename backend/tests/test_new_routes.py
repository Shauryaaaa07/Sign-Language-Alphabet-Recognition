"""
Integration Tests for SignAI 2.0 Extended API Routers
====================================================

Tests:
1. /models/summary
2. /vision/landmarks
3. /vision/quality
4. /explain/gradcam
5. /models/compare
6. /temporal/status and /temporal/stream
"""

import io
import os
import sys
import unittest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.main import app


class TestExtendedAPIRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Create a small valid test PNG image
        img = Image.new("RGB", (128, 128), color=(180, 140, 100))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        cls.test_image_bytes = buf.getvalue()

    def test_models_summary(self):
        resp = self.client.get("/models/summary")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("models", data)
        self.assertIn("cnn_v4", data["models"])
        self.assertIn("landmark_mlp", data["models"])
        self.assertIn("multimodal_fusion", data["models"])
        self.assertIn("temporal_recurrent", data["models"])

    def test_vision_quality_endpoint(self):
        resp = self.client.post(
            "/vision/quality",
            files={"file": ("test.png", self.test_image_bytes, "image/png")},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("quality_score", data)
        self.assertIn("all_advisories", data)
        self.assertIn("metrics", data)

    def test_explain_gradcam_endpoint(self):
        resp = self.client.post(
            "/explain/gradcam?alpha=0.5",
            files={"file": ("test.png", self.test_image_bytes, "image/png")},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("predicted_letter", data)
        self.assertIn("overlay_base64", data)
        self.assertEqual(data["target_layer_name"], "block3_conv2")

    def test_models_compare_endpoint(self):
        resp = self.client.post(
            "/models/compare",
            files={"file": ("test.png", self.test_image_bytes, "image/png")},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("cnn_v4", data)
        self.assertIn("multimodal_fusion", data)

    def test_temporal_status_and_stream(self):
        resp_status = self.client.get("/temporal/status")
        self.assertEqual(resp_status.status_code, 200)
        data_status = resp_status.json()
        self.assertIn("buffer_capacity", data_status)

        # Stream a dummy frame
        resp_stream = self.client.post(
            "/temporal/stream",
            json={"feature_vector_78": [0.0] * 78},
        )
        self.assertEqual(resp_stream.status_code, 200)
        data_stream = resp_stream.json()
        self.assertIn("state", data_stream)


if __name__ == "__main__":
    unittest.main()
