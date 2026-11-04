"""
Temporal Gesture Sequence Dataset Utilities
===========================================

Provides sequence dataset loaders, kinematic synthesis for architectural
verification of dynamic gesture pipelines, and recording tools for physical ISL video captures.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class TemporalSequenceDataset:
    """
    Manages sequence datasets for dynamic ISL recognition (e.g., J, Z, or continuous signs).
    Feature shape: (N, sequence_length, feature_dim).
    """

    def __init__(self, sequence_length: int = 30, feature_dim: int = 78):
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim

    def generate_synthetic_kinematic_sequences(
        self,
        samples_per_class: int = 40,
        classes: Optional[List[str]] = None,
        noise_std: float = 0.02,
        seed: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Generates mathematically parameterized kinematic motion trajectories
        for testing and verifying the LSTM/GRU architectures before physical video dataset collection.

        For example:
        - Dynamic class 'J': Curved downward hook trajectory of index/pinky tip.
        - Dynamic class 'Z': Zig-zag 3-segment trajectory of index tip.
        - Static classes: Stationary hand position with subtle physiological tremor/jitter.
        """
        rng = np.random.default_rng(seed)
        if classes is None:
            classes = ["STATIC_HOLD", "DYNAMIC_J", "DYNAMIC_Z"]

        X_list = []
        y_list = []

        t = np.linspace(0, 1, self.sequence_length)

        for c_idx, c_name in enumerate(classes):
            for _ in range(samples_per_class):
                # Base 78-d vector
                seq = np.zeros((self.sequence_length, self.feature_dim), dtype=np.float32)

                # Base stationary posture
                base_hand = rng.normal(0.0, 0.2, size=self.feature_dim).astype(np.float32)

                if c_name == "DYNAMIC_J":
                    # Hook motion: x moves slightly, y moves down then loops back up
                    dx = 0.3 * np.sin(np.pi * t)
                    dy = 0.6 * t - 0.2 * np.sin(2 * np.pi * t)
                elif c_name == "DYNAMIC_Z":
                    # Zig-zag: 3 segments
                    dx = np.piecewise(
                        t,
                        [t < 0.33, (t >= 0.33) & (t < 0.66), t >= 0.66],
                        [lambda x: 3 * x, lambda x: 1.0 - 3 * (x - 0.33), lambda x: 3 * (x - 0.66)],
                    ) * 0.4
                    dy = 0.4 * t
                else:  # STATIC_HOLD
                    dx = np.zeros_like(t)
                    dy = np.zeros_like(t)

                for frame_idx in range(self.sequence_length):
                    frame_feat = base_hand.copy()
                    # Apply motion to tip landmarks (indices 24..35 in 78-d vector)
                    frame_feat[24] += dx[frame_idx]
                    frame_feat[25] += dy[frame_idx]
                    # Add subtle sensor noise
                    frame_feat += rng.normal(0, noise_std, size=self.feature_dim)
                    seq[frame_idx] = frame_feat

                X_list.append(seq)
                y_list.append(c_idx)

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.int32)
        return X, y, classes
