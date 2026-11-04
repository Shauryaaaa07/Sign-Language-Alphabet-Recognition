"""
Dynamic Gesture Architecture Training & Verification Script
===========================================================

Trains and benchmarks BiLSTM and BiGRU temporal gesture models on verified
kinematic motion trajectories (dynamic J hook, dynamic Z zig-zag, stationary hold).
Saves models and architectural metrics to saved_models/temporal/.
"""

import json
import os
import sys
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from training.temporal.sequence_dataset import TemporalSequenceDataset
from training.temporal.lstm_model import build_lstm_model
from training.temporal.gru_model import build_gru_model

OUTPUT_DIR = os.path.join(REPO_ROOT, "saved_models", "temporal")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def train_temporal():
    print("=" * 70)
    print("SignAI — Temporal Dynamic Gesture Model Verification (Stage 6)")
    print("=" * 70)

    dataset_gen = TemporalSequenceDataset(sequence_length=30, feature_dim=78)
    X, y, classes = dataset_gen.generate_synthetic_kinematic_sequences(
        samples_per_class=60,
        classes=["STATIC_HOLD", "DYNAMIC_J", "DYNAMIC_Z"],
        noise_std=0.03,
        seed=101,
    )
    print(f"Generated {len(X)} sequence samples across classes: {classes}")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # 1. BiLSTM Training
    print("\n--- Training Bidirectional LSTM ---")
    lstm = build_lstm_model(sequence_length=30, feature_dim=78, num_classes=len(classes))
    lstm.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    lstm.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=15,
        batch_size=16,
        verbose=1,
    )
    lstm_loss, lstm_acc = lstm.evaluate(X_val, y_val, verbose=0)
    print(f"BiLSTM Validation Accuracy: {lstm_acc * 100:.2f}%")

    lstm_path = os.path.join(OUTPUT_DIR, "isl_bilstm_dynamic.keras")
    lstm.save(lstm_path)
    print(f"Saved BiLSTM checkpoint to: {lstm_path}")

    # 2. BiGRU Training
    print("\n--- Training Bidirectional GRU ---")
    gru = build_gru_model(sequence_length=30, feature_dim=78, num_classes=len(classes))
    gru.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    gru.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=15,
        batch_size=16,
        verbose=1,
    )
    gru_loss, gru_acc = gru.evaluate(X_val, y_val, verbose=0)
    print(f"BiGRU Validation Accuracy: {gru_acc * 100:.2f}%")

    gru_path = os.path.join(OUTPUT_DIR, "isl_bigru_dynamic.keras")
    gru.save(gru_path)
    print(f"Saved BiGRU checkpoint to: {gru_path}")

    # 3. Save metadata
    meta = {
        "classes": classes,
        "sequence_length": 30,
        "feature_dim": 78,
        "bilstm_val_accuracy": float(lstm_acc),
        "bigru_val_accuracy": float(gru_acc),
        "status": "architectural_verification_complete",
        "notice": "RealSign dataset contains static images. Full dynamic training pending physical video collection for J and Z.",
    }
    with open(os.path.join(OUTPUT_DIR, "temporal_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("Saved temporal metadata.")


if __name__ == "__main__":
    train_temporal()
