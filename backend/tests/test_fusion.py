"""
Unit Tests for Multimodal Fusion Service
========================================

Verifies:
1. Fusion service singleton initialization.
2. Inference on a valid RGB image.
3. Fallback behavior when hand is not detected (blank image).
4. Top-k candidate format and probabilities.
"""

import os
import sys
import unittest
import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.services.fusion_service import MultimodalFusionService


class TestMultimodalFusionService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = MultimodalFusionService.get_instance()

    def test_singleton_instance(self):
        s2 = MultimodalFusionService.get_instance()
        self.assertIs(self.service, s2)

    def test_fallback_on_blank_image(self):
        # Blank black image has no hand detected -> should fallback to CNN V4 cleanly
        blank_img = Image.fromarray(np.zeros((128, 128, 3), dtype=np.uint8))
        res = self.service.predict(blank_img)
        
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["fallback_used"])
        self.assertEqual(res["mode"], "CNN_V4_FALLBACK")
        self.assertIn("Landmarks unavailable", res["fallback_reason"])
        self.assertIn(res["predicted_letter"], list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.assertEqual(len(res["top_predictions"]), 3)
        self.assertGreaterEqual(res["confidence"], 0.0)
        self.assertLessEqual(res["confidence"], 1.0)

    def test_inference_on_real_hand_image(self):
        # Test on an existing training image that contains a hand
        sample_path = os.path.join(REPO_ROOT, "dataset", "processed", "Training", "A", "1.jpg")
        if not os.path.exists(sample_path):
            self.skipTest(f"Sample image {sample_path} not found")
            
        with Image.open(sample_path) as img:
            res = self.service.predict(img.convert("RGB"))
            
        self.assertEqual(res["status"], "success")
        self.assertIn(res["predicted_letter"], list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.assertGreater(res["confidence"], 0.0)
        self.assertIn(res["mode"], ["MULTIMODAL_FUSION", "CNN_V4_FALLBACK"])
        self.assertIn("inference_time_ms", res)
        self.assertEqual(len(res["top_predictions"]), 3)

    def test_dual_hand_inference(self):
        # Dual-hand image should trigger independent evaluation strategy
        sample_path = os.path.join(REPO_ROOT, "frontend", "public", "signs", "A.jpg")
        if not os.path.exists(sample_path):
            self.skipTest(f"Sample image {sample_path} not found")

        with Image.open(sample_path) as img:
            res = self.service.predict(img.convert("RGB"))

        self.assertEqual(res["status"], "success")
        self.assertIn(res["predicted_letter"], list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        self.assertIn("dual_hand_analysis", res)
        dha = res["dual_hand_analysis"]
        if dha["is_dual_hand"]:
            self.assertEqual(dha["strategy"], "INDEPENDENT_EVALUATION")
            self.assertGreaterEqual(dha["hand_count"], 2)
            self.assertIsNotNone(dha["notice"])
            self.assertGreaterEqual(len(dha["per_hand_predictions"]), 1)
            for p in dha["per_hand_predictions"]:
                self.assertIn("handedness", p)
                self.assertIn("predicted_letter", p)
                self.assertIn("confidence", p)


if __name__ == "__main__":
    unittest.main()
