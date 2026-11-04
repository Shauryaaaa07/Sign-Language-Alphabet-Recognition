#!/usr/bin/env python3
"""
Configurable Subset Evaluation Script (Model V4)
================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase: Multi-Class Sub-Manifold & Full Model Evaluation

Evaluates the trained 26-class CNN V4 model on a configurable subset of 3–8
alphabet letters (default: A, B, C, D, H, L, R, E) drawn from the independent
test split (`dataset/processed/Testing/`).

Outputs both:
1. Unrestricted Metrics: The model outputs probabilities across all 26 classes.
   A prediction of a non-subset class counts as a misclassification.
2. Restricted (Sub-Manifold) Metrics: Softmax probabilities are restricted to
   the chosen subset candidates (argmax over subset probabilities), reflecting
   performance in a closed subset domain.

Generates:
- results/subset/subset_unrestricted_classification_report.csv
- results/subset/subset_restricted_classification_report.csv
- results/subset/subset_predictions.csv
- results/subset/subset_unrestricted_confusion_matrix.png
- results/subset/subset_restricted_confusion_matrix.png
- results/subset/subset_summary.json
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import tensorflow as tf

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_CHECKPOINT = os.path.join(REPO_ROOT, "saved_models", "experiments", "isl_alphabet_cnn_v4_best.keras")
DEFAULT_TEST_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Testing")
DEFAULT_MAPPING = os.path.join(REPO_ROOT, "training", "label_classes.json")
DEFAULT_OUTPUT_DIR = os.path.join(REPO_ROOT, "results", "subset")
DEFAULT_SUBSET = ["A", "B", "C", "D", "H", "L", "R", "E"]


def compute_file_sha256(file_path: str) -> str:
    """Computes SHA-256 hash to verify file integrity and immutability."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_verified_classes(mapping_path: str) -> List[str]:
    """Loads and validates the 26 full class mappings."""
    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(f"Class mapping JSON not found: {mapping_path}")
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    classes = data.get("classes", [])
    if len(classes) != 26:
        raise ValueError(f"Expected 26 classes, found {len(classes)}")
    return classes


def plot_cm(cm: np.ndarray, display_labels: List[str], title: str, output_path: str):
    """Saves a styled confusion matrix plot."""
    plt.figure(figsize=(8, 7))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(title, fontsize=12, fontweight="bold", pad=12)
    plt.colorbar()
    tick_marks = np.arange(len(display_labels))
    plt.xticks(tick_marks, display_labels, fontsize=10, rotation=45)
    plt.yticks(tick_marks, display_labels, fontsize=10)
    plt.xlabel("Predicted Label", fontsize=11, fontweight="bold")
    plt.ylabel("True Label", fontsize=11, fontweight="bold")

    thresh = cm.max() / 2.0 if cm.max() > 0 else 1.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j,
                i,
                f"{cm[i, j]}",
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontweight="bold",
                fontsize=9,
            )
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def evaluate_subset(
    checkpoint_path: str,
    test_dir: str,
    mapping_path: str,
    subset_letters: List[str],
    output_dir: str,
) -> Dict[str, any]:
    print("=" * 72)
    print("SignAI — Configurable Subset Evaluation (Model V4)")
    print("=" * 72)

    # 1. Validate Subset Configuration
    subset = sorted(list(set(l.strip().upper() for l in subset_letters)))
    if len(subset) < 3 or len(subset) > 8:
        raise ValueError(f"Subset must contain between 3 and 8 classes. Provided {len(subset)}: {subset}")

    all_classes = load_verified_classes(mapping_path)
    for l in subset:
        if l not in all_classes:
            raise ValueError(f"Letter '{l}' is not in the recognized 26 classes.")

    subset_indices = [all_classes.index(l) for l in subset]
    print(f"Selected Subset ({len(subset)} classes): {', '.join(subset)}")
    print(f"Subset Class Indices in 26-Class Model: {subset_indices}")

    # 2. Immutability Verification (Before)
    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
    sha_before = compute_file_sha256(checkpoint_path)
    print(f"Model Checkpoint: {os.path.basename(checkpoint_path)}")
    print(f"SHA-256 (Before Inference): {sha_before}")

    # 3. Load Model
    print("Loading CNN V4 model weights...")
    model = tf.keras.models.load_model(checkpoint_path, compile=False)
    print("Model loaded successfully.")

    # 4. Gather Test Samples for the Subset
    samples = []
    for letter in subset:
        letter_dir = os.path.join(test_dir, letter)
        if not os.path.isdir(letter_dir):
            raise FileNotFoundError(f"Test directory for class '{letter}' not found at: {letter_dir}")
        files = [
            f for f in os.listdir(letter_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        files.sort()
        for f in files:
            samples.append((letter, os.path.join(letter_dir, f)))

    print(f"Loaded {len(samples)} independent test samples across {len(subset)} classes.")

    # 5. Batch Inference
    images_batch = []
    true_labels = []
    file_paths = []

    print("Preprocessing images (128x128 RGB, /255.0)...")
    for true_letter, file_path in samples:
        img = Image.open(file_path).convert("RGB").resize((128, 128), Image.Resampling.BILINEAR)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        images_batch.append(arr)
        true_labels.append(true_letter)
        file_paths.append(file_path)

    x_test = np.array(images_batch, dtype=np.float32)

    print("Running forward pass...")
    t0 = time.time()
    raw_probs = model.predict(x_test, batch_size=64, verbose=0)
    inference_duration = time.time() - t0
    avg_latency_ms = (inference_duration / len(samples)) * 1000
    print(f"Inference completed in {inference_duration:.2f}s ({avg_latency_ms:.2f} ms/sample).")

    # 6. Unrestricted vs Restricted Evaluation
    records = []
    unrestricted_preds = []
    restricted_preds = []

    for i in range(len(samples)):
        t_label = true_labels[i]
        f_path = file_paths[i]
        probs = raw_probs[i]

        # Unrestricted: Argmax over all 26 classes
        top_idx_26 = int(np.argmax(probs))
        unrestricted_pred = all_classes[top_idx_26]
        unrestricted_conf = float(probs[top_idx_26])
        unrestricted_preds.append(unrestricted_pred)

        # Restricted: Argmax over only the subset classes
        subset_probs = probs[subset_indices]
        top_subset_rel_idx = int(np.argmax(subset_probs))
        restricted_pred = subset[top_subset_rel_idx]
        restricted_conf = float(subset_probs[top_subset_rel_idx] / (np.sum(subset_probs) + 1e-9))
        restricted_preds.append(restricted_pred)

        records.append({
            "filename": os.path.basename(f_path),
            "true_class": t_label,
            "unrestricted_pred": unrestricted_pred,
            "unrestricted_conf": round(unrestricted_conf, 4),
            "unrestricted_correct": unrestricted_pred == t_label,
            "restricted_pred": restricted_pred,
            "restricted_conf": round(restricted_conf, 4),
            "restricted_correct": restricted_pred == t_label,
        })

    df_preds = pd.DataFrame(records)

    # 7. Compute Metrics
    # Unrestricted: classes include subset plus any predicted outside classes
    unrestricted_unique_preds = sorted(list(set(unrestricted_preds) | set(subset)))
    unrestricted_acc = accuracy_score(true_labels, unrestricted_preds)
    unrestricted_report_dict = classification_report(
        true_labels,
        unrestricted_preds,
        labels=subset,
        output_dict=True,
        zero_division=0,
    )
    df_unrestricted_report = pd.DataFrame(unrestricted_report_dict).transpose()

    # Restricted: strictly among subset
    restricted_acc = accuracy_score(true_labels, restricted_preds)
    restricted_report_dict = classification_report(
        true_labels,
        restricted_preds,
        labels=subset,
        output_dict=True,
        zero_division=0,
    )
    df_restricted_report = pd.DataFrame(restricted_report_dict).transpose()

    os.makedirs(output_dir, exist_ok=True)

    # 8. Save CSV Reports & Predictions
    pred_csv_path = os.path.join(output_dir, "subset_predictions.csv")
    unrestricted_csv_path = os.path.join(output_dir, "subset_unrestricted_classification_report.csv")
    restricted_csv_path = os.path.join(output_dir, "subset_restricted_classification_report.csv")

    df_preds.to_csv(pred_csv_path, index=False)
    df_unrestricted_report.to_csv(unrestricted_csv_path, index=True)
    df_restricted_report.to_csv(restricted_csv_path, index=True)

    # 9. Confusion Matrices
    # Unrestricted CM
    unrestricted_cm = confusion_matrix(true_labels, unrestricted_preds, labels=unrestricted_unique_preds)
    unrestricted_cm_path = os.path.join(output_dir, "subset_unrestricted_confusion_matrix.png")
    plot_cm(
        unrestricted_cm,
        unrestricted_unique_preds,
        f"Subset Unrestricted Confusion Matrix ({len(subset)} True Classes)",
        unrestricted_cm_path,
    )

    # Restricted CM
    restricted_cm = confusion_matrix(true_labels, restricted_preds, labels=subset)
    restricted_cm_path = os.path.join(output_dir, "subset_restricted_confusion_matrix.png")
    plot_cm(
        restricted_cm,
        subset,
        f"Subset Restricted Confusion Matrix (Closed {len(subset)}-Class Domain)",
        restricted_cm_path,
    )

    # 10. Immutability Verification (After)
    sha_after = compute_file_sha256(checkpoint_path)
    if sha_before != sha_after:
        raise RuntimeError("FATAL: Checkpoint hash mismatch! Model file was modified during evaluation!")
    print(f"SHA-256 (After Inference):  {sha_after} [VERIFIED UNCHANGED]")

    # 11. Summary JSON
    summary = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_checkpoint": os.path.basename(checkpoint_path),
        "sha256": sha_after,
        "subset_classes": subset,
        "num_classes": len(subset),
        "total_test_samples": len(samples),
        "unrestricted": {
            "accuracy": round(float(unrestricted_acc), 4),
            "macro_f1": round(float(unrestricted_report_dict["macro avg"]["f1-score"]), 4),
            "weighted_f1": round(float(unrestricted_report_dict["weighted avg"]["f1-score"]), 4),
            "correct": int(df_preds["unrestricted_correct"].sum()),
        },
        "restricted": {
            "accuracy": round(float(restricted_acc), 4),
            "macro_f1": round(float(restricted_report_dict["macro avg"]["f1-score"]), 4),
            "weighted_f1": round(float(restricted_report_dict["weighted avg"]["f1-score"]), 4),
            "correct": int(df_preds["restricted_correct"].sum()),
        },
        "average_latency_ms": round(avg_latency_ms, 2),
    }

    summary_path = os.path.join(output_dir, "subset_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 72)
    print("SUBSET EVALUATION RESULTS SUMMARY:")
    print(f"  Subset Classes: {subset}")
    print(f"  Total Samples:  {len(samples)}")
    print(f"  Unrestricted Accuracy: {unrestricted_acc * 100:.2f}% (Macro F1: {unrestricted_report_dict['macro avg']['f1-score'] * 100:.2f}%)")
    print(f"  Restricted Accuracy:   {restricted_acc * 100:.2f}% (Macro F1: {restricted_report_dict['macro avg']['f1-score'] * 100:.2f}%)")
    print(f"  Saved artifacts to: {output_dir}")
    print("=" * 72 + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate CNN V4 on a 3-8 class subset of ISL alphabet.")
    parser.add_argument(
        "--classes",
        type=str,
        default=",".join(DEFAULT_SUBSET),
        help="Comma-separated list of 3-8 letters (e.g. 'A,B,C,D,H,L,R,E')",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=DEFAULT_CHECKPOINT,
        help="Path to trained CNN V4 model checkpoint",
    )
    parser.add_argument(
        "--test-dir",
        type=str,
        default=DEFAULT_TEST_DIR,
        help="Path to test dataset directory",
    )
    parser.add_argument(
        "--mapping",
        type=str,
        default=DEFAULT_MAPPING,
        help="Path to label_classes.json",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to save evaluation reports and plots",
    )

    args = parser.parse_args()
    letters = [x.strip() for x in args.classes.split(",") if x.strip()]
    evaluate_subset(
        checkpoint_path=args.checkpoint,
        test_dir=args.test_dir,
        mapping_path=args.mapping,
        subset_letters=letters,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
