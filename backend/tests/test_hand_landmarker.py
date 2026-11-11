"""
Unit Tests for MediaPipe Hand Landmarker Module (Dual-Hand Support)
===================================================================

Tests:
1. Empty payload resilience
2. Invalid byte handling
3. Blank image (no hand detected)
4. Single-hand detection (Right hand)
5. Single-hand detection (Left hand)
6. Dual-hand detection (Both hands simultaneously)
7. Hands entering and leaving the frame (temporal transitions)
8. Separate independent 78-dimensional feature vectors (no cross-contamination)
9. Backward compatibility for legacy single-hand response schema
"""

import os
import sys
import unittest

import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.vision.hand_landmarker import (
    HandLandmarkDetector,
    HAND_CONNECTIONS,
    LANDMARK_NAMES,
    extract_landmarks_from_bytes,
)

SAMPLE_IMAGE = os.path.join(REPO_ROOT, "frontend", "public", "signs", "A.jpg")


class TestHandLandmarker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = HandLandmarkDetector.get_instance()
        if os.path.isfile(SAMPLE_IMAGE):
            cls.base_img = Image.open(SAMPLE_IMAGE).convert("RGB")
            w, h = cls.base_img.size
            cls.single_hand_img = cls.base_img.crop((0, 0, int(w * 0.55), h))
        else:
            cls.base_img = None
            cls.single_hand_img = None

    def test_singleton_instance(self):
        d1 = HandLandmarkDetector.get_instance()
        d2 = HandLandmarkDetector.get_instance()
        self.assertIs(d1, d2)

    def test_landmark_definitions(self):
        self.assertEqual(len(LANDMARK_NAMES), 21)
        self.assertEqual(LANDMARK_NAMES[0], "WRIST")
        self.assertEqual(LANDMARK_NAMES[4], "THUMB_TIP")
        self.assertEqual(LANDMARK_NAMES[8], "INDEX_FINGER_TIP")
        self.assertGreaterEqual(len(HAND_CONNECTIONS), 20)

    def test_empty_bytes(self):
        res = self.detector.process_image(b"")
        self.assertEqual(res["status"], "no_hand_detected")
        self.assertEqual(res["num_hands_detected"], 0)
        self.assertIsNone(res["primary_hand"])
        self.assertEqual(res["hands"], [])

    def test_invalid_bytes(self):
        res = self.detector.process_image(b"not_an_image_data")
        self.assertEqual(res["status"], "no_hand_detected")
        self.assertIn("invalid_image_bytes", res["reason"])
        self.assertEqual(res["num_hands_detected"], 0)
        self.assertEqual(res["hands"], [])

    def test_blank_image(self):
        black_img = np.zeros((200, 200, 3), dtype=np.uint8)
        res = self.detector.process_image(black_img)
        self.assertEqual(res["status"], "no_hand_detected")
        self.assertEqual(res["num_hands_detected"], 0)
        self.assertIsNone(res["primary_hand"])
        self.assertEqual(res["hands"], [])

    def test_single_hand_detection(self):
        if not self.single_hand_img:
            self.skipTest("Sample image not found")

        res = self.detector.process_image(self.single_hand_img)
        self.assertEqual(res["status"], "hand_detected")
        self.assertEqual(res["num_hands_detected"], 1)

        primary = res["primary_hand"]
        self.assertIsNotNone(primary)
        self.assertIn(primary["handedness"], ["Left", "Right"])
        self.assertGreater(primary["confidence"], 0.5)

        # Check 21 landmarks
        landmarks = primary["landmarks_normalized"]
        self.assertEqual(len(landmarks), 21)
        for lm in landmarks:
            self.assertIn("x", lm)
            self.assertIn("y", lm)
            self.assertIn("z", lm)

        # Check Bounding Box
        bbox = primary["bounding_box_normalized"]
        self.assertLessEqual(bbox["min_x"], bbox["max_x"])
        self.assertLessEqual(bbox["min_y"], bbox["max_y"])
        self.assertGreater(bbox["width"], 0.0)

        # Check 78-dim Feature Vector
        feat_vec = primary["feature_vector_78"]
        self.assertEqual(len(feat_vec), 78)

    def test_flipped_hand_detection(self):
        """Tests detection and handedness on a mirrored hand."""
        if not self.single_hand_img:
            self.skipTest("Sample image not found")

        flipped = self.single_hand_img.transpose(Image.FLIP_LEFT_RIGHT)
        res = self.detector.process_image(flipped)
        self.assertEqual(res["status"], "hand_detected")
        self.assertEqual(res["num_hands_detected"], 1)
        self.assertIn(res["primary_hand"]["handedness"], ["Left", "Right"])
        self.assertEqual(len(res["primary_hand"]["feature_vector_78"]), 78)

    def test_both_hands_simultaneously(self):
        """Tests simultaneous 2-hand detection on an authentic dual-hand image."""
        if not self.base_img:
            self.skipTest("Sample image A.jpg not found")

        res = self.detector.process_image(self.base_img)
        self.assertEqual(res["status"], "hand_detected")
        self.assertEqual(res["num_hands_detected"], 2)
        self.assertEqual(len(res["hands"]), 2)

        hand1 = res["hands"][0]
        hand2 = res["hands"][1]

        # Verify separate handedness
        handednesses = {hand1["handedness"], hand2["handedness"]}
        self.assertEqual(handednesses, {"Left", "Right"})

        # Verify separate 78-dimensional feature vectors (NOT merged)
        self.assertEqual(len(hand1["feature_vector_78"]), 78)
        self.assertEqual(len(hand2["feature_vector_78"]), 78)
        self.assertNotEqual(hand1["feature_vector_78"], hand2["feature_vector_78"])

        # Verify separate bounding boxes
        box1 = hand1["bounding_box_normalized"]
        box2 = hand2["bounding_box_normalized"]
        self.assertGreater(box1["width"], 0.0)
        self.assertGreater(box2["width"], 0.0)

    def test_hands_entering_and_leaving_frame(self):
        """Simulates sequence of frames where hands enter and exit camera view."""
        if not self.single_hand_img or not self.base_img:
            self.skipTest("Sample image not found")

        w, h = self.base_img.size
        black_img = Image.new("RGB", (w, h), color=(0, 0, 0))

        # Frame 0: No hands
        res0 = self.detector.process_image(black_img)
        self.assertEqual(res0["num_hands_detected"], 0)

        # Frame 1: One hand enters
        res1 = self.detector.process_image(self.single_hand_img)
        self.assertEqual(res1["num_hands_detected"], 1)

        # Frame 2: Both hands present
        res2 = self.detector.process_image(self.base_img)
        self.assertEqual(res2["num_hands_detected"], 2)

        # Frame 3: One hand exits (single hand remains)
        res3 = self.detector.process_image(self.single_hand_img)
        self.assertEqual(res3["num_hands_detected"], 1)

        # Frame 4: Both hands exit
        res4 = self.detector.process_image(black_img)
        self.assertEqual(res4["num_hands_detected"], 0)

    def test_backward_compatibility_schema(self):
        """Ensures all legacy keys (primary_hand, all_hands, etc.) remain intact."""
        if not self.base_img:
            self.skipTest("Sample image A.jpg not found")

        res = self.detector.process_image(self.base_img)
        self.assertIn("status", res)
        self.assertIn("num_hands_detected", res)
        self.assertIn("primary_hand", res)
        self.assertIn("all_hands", res)
        self.assertIn("hands", res)
        self.assertIn("image_dimensions", res)

        hand = res["primary_hand"]
        self.assertIn("landmarks_normalized", hand)
        self.assertIn("landmarks_pixels", hand)
        self.assertIn("bounding_box_normalized", hand)
        self.assertIn("bounding_box_pixels", hand)
        self.assertIn("wrist_relative_landmarks", hand)
        self.assertIn("finger_joint_angles", hand)
        self.assertIn("fingertip_wrist_distances", hand)
        self.assertIn("feature_vector_78", hand)


if __name__ == "__main__":
    unittest.main()
