"""
Temporal Sequence Collector
===========================

Maintains a sliding temporal window of hand landmark features for dynamic
gesture recognition (e.g., dynamic ISL signs involving motion trajectories).
Includes motion energy detection, sequence normalization, and cooldown logic.
"""

from collections import deque
import time
from typing import Any, Deque, Dict, List, Optional, Tuple
import numpy as np

from backend.vision.landmark_features import FEATURE_DIM


class TemporalSequenceCollector:
    """
    Collects consecutive landmark feature vectors in a sliding temporal buffer.
    Detects dynamic hand motion and prepares normalized temporal sequences
    of shape (1, sequence_length, feature_dim) for LSTM/GRU inference.
    """

    def __init__(
        self,
        buffer_size: int = 30,
        cooldown_seconds: float = 1.5,
        motion_threshold: float = 0.05,
    ):
        self.buffer_size = buffer_size
        self.cooldown_seconds = cooldown_seconds
        self.motion_threshold = motion_threshold
        self.feature_dim = FEATURE_DIM

        self.buffer: Deque[np.ndarray] = deque(maxlen=buffer_size)
        self.timestamps: Deque[float] = deque(maxlen=buffer_size)
        self.last_trigger_time: float = 0.0

    def add_frame(self, feature_vector: np.ndarray, timestamp: Optional[float] = None) -> None:
        """Adds a feature vector (78-dim) to the temporal buffer."""
        if feature_vector is None:
            feature_vector = np.zeros(self.feature_dim, dtype=np.float32)
        else:
            feature_vector = np.asarray(feature_vector, dtype=np.float32).flatten()
            if feature_vector.shape[0] != self.feature_dim:
                # Resize or pad if mismatch
                padded = np.zeros(self.feature_dim, dtype=np.float32)
                l = min(len(feature_vector), self.feature_dim)
                padded[:l] = feature_vector[:l]
                feature_vector = padded

        now = timestamp if timestamp is not None else time.time()
        self.buffer.append(feature_vector)
        self.timestamps.append(now)

    def is_ready(self, min_frames: int = 15) -> bool:
        """Checks if enough frames have accumulated for sequence prediction."""
        return len(self.buffer) >= min_frames

    def is_in_cooldown(self, current_time: Optional[float] = None) -> bool:
        """Checks if cooldown period is active."""
        now = current_time if current_time is not None else time.time()
        return (now - self.last_trigger_time) < self.cooldown_seconds

    def mark_triggered(self, current_time: Optional[float] = None) -> None:
        """Sets the last trigger time to prevent rapid re-triggering."""
        self.last_trigger_time = current_time if current_time is not None else time.time()

    def compute_motion_energy(self) -> float:
        """
        Computes motion energy across the buffered frames by calculating
        mean Euclidean displacement of the normalized coordinates.
        Coordinates are stored in indices 0..62 of the 78-d vector.
        """
        if len(self.buffer) < 2:
            return 0.0

        coords_seq = np.array([f[:63] for f in self.buffer])  # shape (T, 63)
        diffs = np.diff(coords_seq, axis=0)  # shape (T-1, 63)
        displacements = np.linalg.norm(diffs.reshape(-1, 21, 3), axis=2)  # shape (T-1, 21)
        mean_motion = float(np.mean(displacements))
        return round(mean_motion, 4)

    def is_motion_significant(self) -> bool:
        """Returns True if hand motion exceeds the threshold for dynamic gestures."""
        return self.compute_motion_energy() >= self.motion_threshold

    def get_normalized_sequence(self, target_len: int = 30) -> np.ndarray:
        """
        Resamples or pads the collected buffer to exactly target_len frames.
        Returns a tensor of shape (1, target_len, feature_dim).
        """
        n_frames = len(self.buffer)
        if n_frames == 0:
            return np.zeros((1, target_len, self.feature_dim), dtype=np.float32)

        arr = np.array(self.buffer, dtype=np.float32)  # shape (n_frames, 78)

        if n_frames == target_len:
            seq = arr
        elif n_frames < target_len:
            # Pad at beginning with repeat of earliest frame or zeros
            pad_len = target_len - n_frames
            padding = np.repeat(arr[:1], pad_len, axis=0)
            seq = np.vstack([padding, arr])
        else:
            # Linear temporal interpolation / sub-sampling to target_len
            indices = np.linspace(0, n_frames - 1, target_len).astype(np.int32)
            seq = arr[indices]

        return np.expand_dims(seq, axis=0)  # (1, target_len, 78)

    def clear(self) -> None:
        """Clears the temporal frame buffer."""
        self.buffer.clear()
        self.timestamps.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Returns collector status and motion summary."""
        now = time.time()
        energy = self.compute_motion_energy()
        return {
            "buffer_length": len(self.buffer),
            "buffer_capacity": self.buffer_size,
            "motion_energy": energy,
            "is_dynamic_motion": energy >= self.motion_threshold,
            "in_cooldown": (now - self.last_trigger_time) < self.cooldown_seconds,
            "cooldown_remaining_s": max(0.0, round(self.cooldown_seconds - (now - self.last_trigger_time), 2)),
        }
