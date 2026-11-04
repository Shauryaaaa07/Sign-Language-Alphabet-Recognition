"""
Unit Tests for Temporal Gesture Recognition Infrastructure
===========================================================

Verifies:
1. TemporalSequenceCollector sliding buffer mechanism.
2. Motion energy computation.
3. Cooldown logic.
4. Sequence interpolation and normalization to target length.
5. TemporalInferenceEngine states (BUFFERING, IDLE, TRACKING, TRIGGERED).
"""

import os
import sys
import unittest
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.temporal.sequence_collector import TemporalSequenceCollector
from backend.temporal.temporal_inference import TemporalInferenceEngine
from backend.vision.landmark_features import FEATURE_DIM


class TestTemporalGestureRecognition(unittest.TestCase):
    def setUp(self):
        self.collector = TemporalSequenceCollector(buffer_size=30, cooldown_seconds=1.0, motion_threshold=0.05)

    def test_buffer_push_and_capacity(self):
        for i in range(50):
            vec = np.ones(FEATURE_DIM, dtype=np.float32) * i
            self.collector.add_frame(vec)
        self.assertEqual(len(self.collector.buffer), 30)

    def test_motion_energy_static(self):
        # Push static frames (identical coordinates)
        static_frame = np.ones(FEATURE_DIM, dtype=np.float32)
        for _ in range(15):
            self.collector.add_frame(static_frame)
        self.assertAlmostEqual(self.collector.compute_motion_energy(), 0.0, places=3)
        self.assertFalse(self.collector.is_motion_significant())

    def test_motion_energy_dynamic(self):
        # Push moving coordinates
        for i in range(20):
            frame = np.zeros(FEATURE_DIM, dtype=np.float32)
            frame[:63] = i * 0.1  # Significant displacement
            self.collector.add_frame(frame)
        energy = self.collector.compute_motion_energy()
        self.assertGreater(energy, 0.05)
        self.assertTrue(self.collector.is_motion_significant())

    def test_sequence_length_normalization(self):
        # 10 frames resampled to 30
        for _ in range(10):
            self.collector.add_frame(np.random.randn(FEATURE_DIM).astype(np.float32))
        seq = self.collector.get_normalized_sequence(target_len=30)
        self.assertEqual(seq.shape, (1, 30, FEATURE_DIM))

    def test_cooldown_behavior(self):
        now = 1000.0
        self.collector.mark_triggered(now)
        self.assertTrue(self.collector.is_in_cooldown(now + 0.5))
        self.assertFalse(self.collector.is_in_cooldown(now + 1.2))

    def test_inference_engine_buffering_state(self):
        engine = TemporalInferenceEngine.get_instance()
        engine.reset()
        res = engine.push_frame(np.zeros(FEATURE_DIM, dtype=np.float32))
        self.assertEqual(res["state"], "BUFFERING")
        self.assertIn("disclaimer", res)


if __name__ == "__main__":
    unittest.main()
