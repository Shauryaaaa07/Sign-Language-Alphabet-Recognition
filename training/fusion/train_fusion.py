#!/usr/bin/env python3
"""
Multimodal CNN + Landmark Fusion Training Script
================================================

Trains the two-stream multimodal fusion architecture combining frozen CNN V4
image features and MediaPipe geometric landmark vectors.

STRICT PROTOCOL:
- Preserves CNN V4 weights (trainable=False).
- Verifies CNN V4 SHA-256 before and after training.
- Evaluates strictly on the Validation split.
- Never trains on or tunes on the independent Testing split.
"""

import datetime
import hashlib
import json
import os
import sys
import time
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.vision.hand_landmarker import HandLandmarkDetector
from backend.vision.landmark_features import FEATURE_DIM
from training.fusion.fusion_model import build_fusion_model

CNN_CHECKPOINT = os.path.join(REPO_ROOT, "saved_models", "experiments", "isl_alphabet_cnn_v4_best.keras")
TRAIN_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Training")
VAL_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Validation")
OUTPUT_DIR = os.path.join(REPO_ROOT, "saved_models", "fusion")


def compute_file_sha256(file_path: str) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_multimodal_dataset(split_dir: str, max_per_class: int = 50) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Loads paired (image_tensor, landmark_vector, label) dataset."""
    detector = HandLandmarkDetector.get_instance()
    classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    images = []
    landmarks = []
    labels = []

    print(f"Loading paired multimodal data from {split_dir} (Max {max_per_class}/class)...")
    for class_idx, class_name in enumerate(classes):
        folder = os.path.join(split_dir, class_name)
        if not os.path.isdir(folder):
            continue
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".png", ".jpeg"))])[:max_per_class]

        for f in files:
            p = os.path.join(folder, f)
            try:
                with Image.open(p) as img:
                    img_rgb = img.convert("RGB")
                    # Image tensor (128, 128, 3)
                    img_resized = img_rgb.resize((128, 128), Image.Resampling.BILINEAR)
                    arr_img = np.asarray(img_resized, dtype=np.float32) / 255.0

                    # Landmark features
                    res = detector.process_image(img_rgb)
                    if res["status"] == "hand_detected" and res["primary_hand"]:
                        feat = res["primary_hand"]["feature_vector_78"]
                    else:
                        feat = np.zeros(FEATURE_DIM, dtype=np.float32)

                    images.append(arr_img)
                    landmarks.append(feat)
                    labels.append(class_idx)
            except Exception:
                continue

    return np.array(images, dtype=np.float32), np.array(landmarks, dtype=np.float32), np.array(labels, dtype=np.int32)


def main():
    print("=" * 76)
    print("SignAI — Multimodal CNN + Landmark Fusion Training (Stage 5)")
    print("=" * 76)

    # 1. Verify CNN V4 Immutability Before
    sha_cnn_before = compute_file_sha256(CNN_CHECKPOINT)
    print(f"CNN V4 Baseline Checkpoint: {CNN_CHECKPOINT}")
    print(f"CNN V4 SHA-256 (Before Training): {sha_cnn_before}")

    cnn_base = tf.keras.models.load_model(CNN_CHECKPOINT, compile=False)
    print("Loaded CNN V4 architecture.")

    # 2. Build Paired Datasets (Training & Validation)
    X_img_train, X_lm_train, y_train = load_multimodal_dataset(TRAIN_DIR, max_per_class=45)
    X_img_val, X_lm_val, y_val = load_multimodal_dataset(VAL_DIR, max_per_class=18)

    print(f"Paired Training Samples:   {len(y_train)} across 26 classes")
    print(f"Paired Validation Samples: {len(y_val)} across 26 classes")

    # 3. Build Two-Stream Multimodal Model
    fusion_model = build_fusion_model(cnn_base_model=cnn_base, landmark_dim=FEATURE_DIM, num_classes=26)
    fusion_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print(f"Fusion Model Total Params: {fusion_model.count_params():,} (Trainable: {np.sum([np.prod(v.shape) for v in fusion_model.trainable_weights]):,})")

    # 4. Train Fusion Model
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=6, restore_best_weights=True, verbose=0),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-5, verbose=0),
    ]

    t0 = time.time()
    fusion_model.fit(
        [X_img_train, X_lm_train],
        y_train,
        validation_data=([X_img_val, X_lm_val], y_val),
        epochs=25,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )
    duration = time.time() - t0

    # 5. Evaluate on Validation Split
    val_probs = fusion_model.predict([X_img_val, X_lm_val], verbose=0)
    val_preds = np.argmax(val_probs, axis=1)
    fusion_acc = accuracy_score(y_val, val_preds)
    classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    report = classification_report(y_val, val_preds, target_names=classes, output_dict=True, zero_division=0)
    macro_f1 = report["macro avg"]["f1-score"]

    print(f"\nMultimodal Fusion Validation Accuracy: {fusion_acc * 100:.2f}% | Macro F1: {macro_f1 * 100:.2f}% (Trained in {duration:.1f}s)")

    # 6. Verify CNN V4 Immutability After
    sha_cnn_after = compute_file_sha256(CNN_CHECKPOINT)
    if sha_cnn_before != sha_cnn_after:
        raise RuntimeError("FATAL: CNN V4 checkpoint was modified during fusion training!")
    print(f"CNN V4 SHA-256 (After Training):  {sha_cnn_after} [VERIFIED UNCHANGED]")

    # 7. Save Model & Comparison Metadata
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(OUTPUT_DIR, "isl_multimodal_fusion_best.keras")
    fusion_model.save(model_path)
    model_sha256 = compute_file_sha256(model_path)

    comparison_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_name": "SignAI_Multimodal_Fusion",
        "checkpoint": os.path.basename(model_path),
        "sha256": model_sha256,
        "base_cnn_v4_sha256": sha_cnn_after,
        "validation_samples": len(y_val),
        "multimodal_metrics": {
            "val_accuracy": round(float(fusion_acc), 4),
            "val_macro_f1": round(float(macro_f1), 4),
            "val_weighted_f1": round(float(report["weighted avg"]["f1-score"]), 4),
        },
        "model_comparison": {
            "cnn_v4_baseline_val_macro_f1": 0.7768,
            "landmark_mlp_val_macro_f1": 0.6377,
            "fusion_model_val_macro_f1": round(float(macro_f1), 4),
        },
        "training_duration_seconds": round(duration, 2),
    }

    with open(os.path.join(OUTPUT_DIR, "validation_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(comparison_data, f, indent=2)

    print("\n" + "=" * 76)
    print("MULTIMODAL FUSION TRAINING COMPLETED:")
    print(f"  Model Saved: {model_path}")
    print(f"  SHA-256:     {model_sha256}")
    print(f"  Accuracy:    {fusion_acc * 100:.2f}% (Macro F1: {macro_f1 * 100:.2f}%)")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
