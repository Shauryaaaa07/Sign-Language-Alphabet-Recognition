"""
Unit Tests for Grad-CAM Explainable AI Engine
=============================================

Tests:
1. Grad-CAM layer resolution (block3_conv2)
2. Heatmap shape and value bounds [0.0, 1.0]
3. Colormap and alpha overlay generation
4. Base64 data URI output formatting
5. Full explain_prediction pipeline on test image (A.jpg)
6. Invalid and corrupted input handling
"""

import os
import sys
import unittest
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.model_loader import get_model, load_model_and_labels
from backend.explainability.gradcam import GradCAMExplainer, TARGET_CONV_LAYER
from backend.explainability.heatmap_generator import overlay_heatmap_on_image
from backend.explainability.explainability_service import explain_prediction

SAMPLE_IMAGE = os.path.join(REPO_ROOT, "frontend", "public", "signs", "A.jpg")


class TestGradCAM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        load_model_and_labels()
        cls.model = get_model()
        cls.explainer = GradCAMExplainer(cls.model, layer_name=TARGET_CONV_LAYER)

    def test_layer_resolution(self):
        self.assertEqual(self.explainer.layer_name, "block3_conv2")
        self.assertIsNotNone(self.explainer.grad_model)

    def test_heatmap_generation_bounds(self):
        dummy_input = np.ones((1, 128, 128, 3), dtype=np.float32) * 0.5
        heatmap, class_idx, confidence = self.explainer.generate_heatmap(dummy_input)

        self.assertEqual(len(heatmap.shape), 2)
        self.assertGreaterEqual(float(np.min(heatmap)), 0.0)
        self.assertLessEqual(float(np.max(heatmap)), 1.0)
        self.assertGreaterEqual(class_idx, 0)
        self.assertLess(class_idx, 26)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)

    def test_overlay_generation(self):
        dummy_heatmap = np.random.uniform(0.0, 1.0, (32, 32)).astype(np.float32)
        dummy_img = (np.random.uniform(0, 255, (128, 128, 3))).astype(np.uint8)

        heat_rgb, blend_rgb, heat_b64, blend_b64 = overlay_heatmap_on_image(
            dummy_heatmap, dummy_img, alpha=0.5
        )

        self.assertEqual(heat_rgb.shape, (128, 128, 3))
        self.assertEqual(blend_rgb.shape, (128, 128, 3))
        self.assertTrue(heat_b64.startswith("data:image/png;base64,"))
        self.assertTrue(blend_b64.startswith("data:image/png;base64,"))

    def test_full_explain_service(self):
        if not os.path.isfile(SAMPLE_IMAGE):
            self.skipTest("Sample image A.jpg not found")

        with open(SAMPLE_IMAGE, "rb") as f:
            image_bytes = f.read()

        result = explain_prediction(image_bytes)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["predicted_letter"], "A")
        self.assertGreater(result["confidence"], 0.8)
        self.assertEqual(result["target_layer_name"], "block3_conv2")
        self.assertTrue(result["heatmap_base64"].startswith("data:image/png;base64,"))
        self.assertTrue(result["overlay_base64"].startswith("data:image/png;base64,"))
        self.assertIn("academic_note", result)

    def test_empty_bytes_error(self):
        with self.assertRaises(ValueError):
            explain_prediction(b"")


if __name__ == "__main__":
    unittest.main()
