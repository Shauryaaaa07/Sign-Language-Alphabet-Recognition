#!/usr/bin/env python3
"""
Landmark Feature Extraction Script
==================================

Extracts 78-dimensional geometric landmark feature vectors from the
quarantined Training and Validation splits using MediaPipe Hand Landmarker.
Saves extracted datasets to .npz files for fast ML training and reproducible experiments.

STRICT PROTOCOL:
- Never processes dataset/processed/Testing/
- Only extracts from Training and Validation
"""

import argparse
import os
import sys
import time
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.vision.hand_landmarker import HandLandmarkDetector
from backend.vision.landmark_features import FEATURE_DIM, extract_features_from_landmarks

TRAIN_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Training")
VAL_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Validation")
OUTPUT_DIR = os.path.join(REPO_ROOT, "training", "landmark_pipeline", "data")


def extract_split_features(
    split_dir: str,
    classes: List[str],
    max_per_class: int = 120,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Extracts landmark feature matrix X and label vector y for a split."""
    detector = HandLandmarkDetector.get_instance()
    x_list = []
    y_list = []
    skipped = 0

    print(f"\nProcessing {split_dir} (Max {max_per_class} samples/class)...")
    for class_idx, class_name in enumerate(classes):
        class_folder = os.path.join(split_dir, class_name)
        if not os.path.isdir(class_folder):
            continue

        files = sorted([f for f in os.listdir(class_folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))])
        selected_files = files[:max_per_class]

        detected_in_class = 0
        for f in selected_files:
            img_path = os.path.join(class_folder, f)
            try:
                with Image.open(img_path) as img:
                    res = detector.process_image(img)
                if res["status"] == "hand_detected" and res["primary_hand"]:
                    feat = res["primary_hand"]["feature_vector_78"]
                    x_list.append(feat)
                    y_list.append(class_idx)
                    detected_in_class += 1
                else:
                    skipped += 1
            except Exception as e:
                skipped += 1

        print(f"  Class {class_name:2s}: Extracted {detected_in_class}/{len(selected_files)} hand landmarks")

    X = np.array(x_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int32)
    print(f"Extraction summary: {len(X)} samples collected, {skipped} frames without detected hands.")
    return X, y, classes


def main():
    parser = argparse.ArgumentParser(description="Extract hand landmarks from training & validation splits.")
    parser.add_argument("--max-train", type=int, default=100, help="Max train samples per class")
    parser.add_argument("--max-val", type=int, default=40, help="Max val samples per class")
    args = parser.parse_args()

    classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    t0 = time.time()
    # 1. Extract Training split
    X_train, y_train, _ = extract_split_features(TRAIN_DIR, classes, max_per_class=args.max_train)
    train_npz = os.path.join(OUTPUT_DIR, "landmarks_train.npz")
    np.savez_compressed(train_npz, X=X_train, y=y_train, classes=classes)
    print(f"Saved training landmarks: {train_npz} ({X_train.shape})")

    # 2. Extract Validation split
    X_val, y_val, _ = extract_split_features(VAL_DIR, classes, max_per_class=args.max_val)
    val_npz = os.path.join(OUTPUT_DIR, "landmarks_val.npz")
    np.savez_compressed(val_npz, X=X_val, y=y_val, classes=classes)
    print(f"Saved validation landmarks: {val_npz} ({X_val.shape})")

    print(f"Extraction completed in {time.time() - t0:.2f} seconds.")


if __name__ == "__main__":
    main()
