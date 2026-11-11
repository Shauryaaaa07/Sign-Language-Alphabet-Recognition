"""
Landmark Feature Engineering Module
===================================

Extracts deterministic, scale-invariant, and wrist-relative geometric features
from raw 21 3D hand landmarks for landmark-based classification and multimodal fusion.
"""

from typing import Any, Dict, List, Tuple
import numpy as np

# Total feature vector length: 78
# 63 scale-invariant wrist-relative coordinates (21 * 3)
# 5 joint flexion angles (degrees, [0, 180])
# 5 fingertip-to-wrist normalized Euclidean distances
# 5 finger extension boolean indicators (0.0 or 1.0)
FEATURE_DIM = 78

FEATURE_NAMES = [
    f"lm_{i}_{axis}_rel" for i in range(21) for axis in ["x", "y", "z"]
] + [
    "angle_thumb", "angle_index", "angle_middle", "angle_ring", "angle_pinky"
] + [
    "dist_thumb_tip", "dist_index_tip", "dist_middle_tip", "dist_ring_tip", "dist_pinky_tip"
] + [
    "ext_thumb", "ext_index", "ext_middle", "ext_ring", "ext_pinky"
]


def extract_features_from_landmarks(landmarks_list: List[Dict[str, float]]) -> np.ndarray:
    """
    Computes a 78-dimensional feature vector from a list of 21 landmark dictionaries [{'x', 'y', 'z'}, ...].
    Guarantees deterministic shape (78,) of dtype float32.
    """
    if not landmarks_list or len(landmarks_list) < 21:
        return np.zeros(FEATURE_DIM, dtype=np.float32)

    coords = np.array([[p["x"], p["y"], p.get("z", 0.0)] for p in landmarks_list[:21]], dtype=np.float32)

    # 1. Wrist Translation
    wrist = coords[0]
    wrist_rel = coords - wrist

    # 2. Hand Scale Normalization (wrist to middle MCP index 9)
    scale = float(np.linalg.norm(coords[9] - wrist))
    if scale < 1e-6:
        scale = float(np.max(np.linalg.norm(wrist_rel, axis=1)))
    if scale < 1e-6:
        scale = 1.0

    scale_norm_coords = wrist_rel / scale
    flat_coords = scale_norm_coords.flatten()

    # 3. 5 Joint Flexion Angles
    triplets = [
        (1, 2, 4),    # Thumb (CMC, MCP, TIP)
        (5, 6, 8),    # Index (MCP, PIP, TIP)
        (9, 10, 12),  # Middle
        (13, 14, 16), # Ring
        (17, 18, 20), # Pinky
    ]
    angles = []
    for a, b, c in triplets:
        v1 = coords[a] - coords[b]
        v2 = coords[c] - coords[b]
        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)
        if n1 > 1e-6 and n2 > 1e-6:
            cos = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
            ang = float(np.degrees(np.arccos(cos)))
        else:
            ang = 0.0
        angles.append(ang / 180.0)  # normalized [0, 1]

    # 4. Fingertip-to-Wrist Distances
    tips = [4, 8, 12, 16, 20]
    tip_dists = [float(np.linalg.norm(scale_norm_coords[t])) for t in tips]

    # 5. Finger Extension Booleans (relative to scale)
    extensions = [float(d > 1.25) for d in tip_dists]

    features = np.concatenate([flat_coords, np.array(angles, dtype=np.float32), np.array(tip_dists, dtype=np.float32), np.array(extensions, dtype=np.float32)])
    return features.astype(np.float32)
