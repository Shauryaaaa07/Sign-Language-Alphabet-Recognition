"""
Unit Tests for Camera Quality and Calibration Services
======================================================
"""

import os
import sys
import unittest
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.vision.camera_quality import CameraQualityAnalyzer, get_camera_analyzer
from backend.services.calibration_service import (
    calibrate_probabilities,
    get_confidence_state,
    compute_expected_calibration_error,
    format_calibrated_prediction,
)

SAMPLE_IMAGE = os.path.join(REPO_ROOT, "frontend", "public", "signs", "A.jpg")


class TestCameraQualityAndCalibration(unittest.TestCase):

    def setUp(self):
        self.analyzer = get_camera_analyzer()

    # 1. Camera Quality Tests
    def test_camera_analyzer_real_image(self):
        if not os.path.isfile(SAMPLE_IMAGE):
            self.skipTest("Sample image A.jpg not found")

        with open(SAMPLE_IMAGE, "rb") as f:
            data = f.read()

        res = self.analyzer.analyze_frame(data)
        self.assertIn(res["status"], ["good", "suboptimal"])
        self.assertGreater(res["quality_score"], 0.0)
        self.assertIn("mean_brightness", res["metrics"])
        self.assertIn("contrast", res["metrics"])
        self.assertIn("laplacian_variance", res["metrics"])
        self.assertTrue(len(res["all_advisories"]) > 0)

    def test_camera_analyzer_dark_frame(self):
        dark_img = np.zeros((150, 150, 3), dtype=np.uint8)
        res = self.analyzer.analyze_frame(dark_img)
        self.assertLess(res["metrics"]["mean_brightness"], 10.0)
        self.assertIn("Lighting is too low", " ".join(res["all_advisories"]))

    def test_camera_analyzer_bright_frame(self):
        bright_img = np.ones((150, 150, 3), dtype=np.uint8) * 245
        res = self.analyzer.analyze_frame(bright_img)
        self.assertGreater(res["metrics"]["mean_brightness"], 230.0)
        self.assertIn("Image is too bright", " ".join(res["all_advisories"]))

    # 2. Calibration Tests
    def test_temperature_scaling_sum_to_one(self):
        raw_probs = np.array([0.90, 0.05, 0.03, 0.02] + [0.0] * 22, dtype=np.float32)
        raw_probs = raw_probs / np.sum(raw_probs)
        calibrated = calibrate_probabilities(raw_probs, temperature=1.5)

        self.assertAlmostEqual(float(np.sum(calibrated)), 1.0, places=4)
        # Higher temperature softens extreme probability
        self.assertLess(calibrated[0], raw_probs[0])

    def test_confidence_states(self):
        self.assertEqual(get_confidence_state(0.95, hand_detected=True), "HIGH_CONFIDENCE")
        self.assertEqual(get_confidence_state(0.72, hand_detected=True), "MODERATE_CONFIDENCE")
        self.assertEqual(get_confidence_state(0.55, hand_detected=True), "LOW_CONFIDENCE")
        self.assertEqual(get_confidence_state(0.30, hand_detected=True), "UNCERTAIN")
        self.assertEqual(get_confidence_state(0.95, hand_detected=False), "UNCERTAIN")

    def test_ece_computation(self):
        confs = np.array([0.95, 0.90, 0.85, 0.70, 0.60, 0.40], dtype=np.float32)
        accs = np.array([1.0, 1.0, 1.0, 0.0, 1.0, 0.0], dtype=np.float32)
        ece, bins = compute_expected_calibration_error(confs, accs, num_bins=5)

        self.assertGreaterEqual(ece, 0.0)
        self.assertLessEqual(ece, 1.0)
        self.assertEqual(len(bins), 5)

    def test_format_calibrated_prediction(self):
        classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        raw_probs = np.zeros(26, dtype=np.float32)
        raw_probs[0] = 0.92
        raw_probs[1] = 0.05
        raw_probs[2] = 0.03

        res = format_calibrated_prediction(
            predicted_letter="A",
            raw_confidence=0.92,
            all_raw_probs=raw_probs,
            classes=classes,
            hand_detected=True,
            temperature=1.28,
        )

        self.assertEqual(res["predicted_letter"], "A")
        self.assertEqual(res["decision_state"], "HIGH_CONFIDENCE")
        self.assertTrue(res["is_accepted"])
        self.assertEqual(len(res["top_candidates"]), 3)


if __name__ == "__main__":
    unittest.main()
