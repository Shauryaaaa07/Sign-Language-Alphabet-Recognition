#!/usr/bin/env python3
"""
Real-World Dataset Evaluation Script (Model V4)
==============================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase: Out-of-Distribution & Unseen Signer Real-World Generalization Audit

Evaluates the trained 26-class CNN V4 model on real-world test images located in
`realworld_test/`. Images may be placed directly in `realworld_test/` or inside
class subdirectories (`realworld_test/A/`, `realworld_test/B/`, etc.).

Supported Naming Convention & Metadata Extraction:
---------------------------------------------------
Filenames with underscore separation are automatically parsed for environmental
and signer metadata tags:
  <Letter>_<Background>_<Signer>_<Index>.jpg
  Examples:
    A_plain_ravi.jpg        -> Letter: A, Background: plain, Signer: ravi
    B_cluttered_priya_1.jpg -> Letter: B, Background: cluttered, Signer: priya
    C_dark_alex.png         -> Letter: C, Background: dark, Signer: alex
    D.jpg                   -> Letter: D (no metadata tags)

Generates:
- results/realworld/realworld_classification_report.csv
- results/realworld/realworld_predictions.csv
- results/realworld/realworld_confusion_matrix.png
- results/realworld/realworld_summary.json
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

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
DEFAULT_REALWORLD_DIR = os.path.join(REPO_ROOT, "realworld_test")
DEFAULT_MAPPING = os.path.join(REPO_ROOT, "training", "label_classes.json")
DEFAULT_OUTPUT_DIR = os.path.join(REPO_ROOT, "results", "realworld")


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


def parse_sample_metadata(file_path: str, base_dir: str, valid_classes: List[str]) -> Optional[Dict[str, str]]:
    """
    Infers true label and metadata tags from path and filename.
    Returns None if the image cannot be mapped to a valid class.
    """
    rel = os.path.relpath(file_path, base_dir)
    filename = os.path.basename(file_path)
    stem, _ = os.path.splitext(filename)

    parts = stem.split("_")
    letter_candidate = parts[0].strip().upper()

    # Check parent folder name if filename doesn't immediately match a letter
    parent_dir = os.path.basename(os.path.dirname(file_path)).strip().upper()
    if parent_dir in valid_classes:
        true_letter = parent_dir
    elif letter_candidate in valid_classes:
        true_letter = letter_candidate
    else:
        # Check first character of filename
        first_char = stem[:1].upper()
        if first_char in valid_classes:
            true_letter = first_char
        else:
            return None

    background = parts[1].strip().lower() if len(parts) > 1 and not parts[1].isdigit() else "unspecified"
    signer = parts[2].strip().lower() if len(parts) > 2 and not parts[2].isdigit() else "unspecified"

    return {
        "file_path": file_path,
        "filename": filename,
        "relative_path": rel,
        "true_letter": true_letter,
        "background": background,
        "signer": signer,
    }


def plot_cm(cm: np.ndarray, display_labels: List[str], title: str, output_path: str):
    """Saves a styled confusion matrix plot."""
    plt.figure(figsize=(10, 9))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title(title, fontsize=12, fontweight="bold", pad=12)
    plt.colorbar()
    tick_marks = np.arange(len(display_labels))
    plt.xticks(tick_marks, display_labels, fontsize=9, rotation=45)
    plt.yticks(tick_marks, display_labels, fontsize=9)
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
                fontsize=8,
            )
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=200)
    plt.close()


def evaluate_realworld(
    checkpoint_path: str,
    data_dir: str,
    mapping_path: str,
    output_dir: str,
) -> Optional[Dict[str, any]]:
    print("=" * 76)
    print("SignAI — Real-World Evaluation Audit (Model V4)")
    print("=" * 76)
    print("IMPORTANT SCIENTIFIC NOTICE:")
    print("  This real-world evaluation dataset is strictly separate from the training,")
    print("  validation, and internal test sets. It tests real-world generalization under")
    print("  diverse backgrounds, lighting conditions, and signer variations.")
    print("=" * 76)

    # 1. Ensure directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        readme_path = os.path.join(data_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(
                "# Real-World Evaluation Test Folder\n\n"
                "Place test images here to evaluate the trained CNN V4 model on real-world conditions.\n\n"
                "### Naming Convention:\n"
                "`<Letter>_<Background>_<Signer>_<Index>.jpg`\n\n"
                "Examples:\n"
                "- `A_plain_ravi.jpg`\n"
                "- `B_cluttered_priya.jpg`\n"
                "- `C_office_alex.png`\n\n"
                "Alternatively, organize images into subfolders: `A/`, `B/`, etc.\n"
            )
        print(f"Created real-world test directory at: {data_dir}")
        print("Folder was empty. Added template README.md with naming instructions.")
        return None

    # 2. Gather image files
    all_classes = load_verified_classes(mapping_path)
    valid_exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

    collected_samples = []
    for root, _, files in os.walk(data_dir):
        for f in files:
            if f.lower().endswith(valid_exts):
                full_path = os.path.join(root, f)
                meta = parse_sample_metadata(full_path, data_dir, all_classes)
                if meta:
                    collected_samples.append(meta)

    if not collected_samples:
        print(f"No valid image files found in '{data_dir}'.")
        print("Please place images named like 'A_plain_ravi.jpg' or organized in 'A/', 'B/' subfolders.")
        readme_path = os.path.join(data_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(
                    "# Real-World Evaluation Test Folder\n\n"
                    "Place test images here to evaluate the trained CNN V4 model on real-world conditions.\n\n"
                    "Naming format: `<Letter>_<Background>_<Signer>.jpg` (e.g. `A_plain_ravi.jpg`)\n"
                )
        return None

    print(f"Found {len(collected_samples)} real-world evaluation images.")

    # 3. Model Integrity Check (Before)
    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
    sha_before = compute_file_sha256(checkpoint_path)
    print(f"Model Checkpoint: {os.path.basename(checkpoint_path)}")
    print(f"SHA-256 (Before Inference): {sha_before}")

    # 4. Load Model
    print("Loading CNN V4 model...")
    model = tf.keras.models.load_model(checkpoint_path, compile=False)
    print("Model loaded successfully.")

    # 5. Preprocess images
    images_batch = []
    print("Preprocessing images (128x128 RGB, /255.0)...")
    for s in collected_samples:
        img = Image.open(s["file_path"]).convert("RGB").resize((128, 128), Image.Resampling.BILINEAR)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        images_batch.append(arr)

    x_test = np.array(images_batch, dtype=np.float32)

    # 6. Predict
    t0 = time.time()
    raw_probs = model.predict(x_test, batch_size=32, verbose=0)
    duration = time.time() - t0
    avg_latency_ms = (duration / len(collected_samples)) * 1000
    print(f"Inference completed in {duration:.2f}s ({avg_latency_ms:.2f} ms/sample).")

    # 7. Build Records
    records = []
    true_labels = []
    pred_labels = []

    for i, s in enumerate(collected_samples):
        probs = raw_probs[i]
        top_idx = int(np.argmax(probs))
        pred_letter = all_classes[top_idx]
        conf = float(probs[top_idx])

        # Top 3
        top3_indices = np.argsort(probs)[-3:][::-1]
        top3_list = [{"letter": all_classes[idx], "confidence": round(float(probs[idx]), 4)} for idx in top3_indices]

        is_correct = (pred_letter == s["true_letter"])
        true_labels.append(s["true_letter"])
        pred_labels.append(pred_letter)

        records.append({
            "filename": s["filename"],
            "relative_path": s["relative_path"],
            "true_letter": s["true_letter"],
            "predicted_letter": pred_letter,
            "confidence": round(conf, 4),
            "correct": is_correct,
            "background": s["background"],
            "signer": s["signer"],
            "top3": json.dumps(top3_list),
        })

    df_preds = pd.DataFrame(records)

    # 8. Compute Metrics
    overall_acc = accuracy_score(true_labels, pred_labels)
    eval_classes = sorted(list(set(true_labels) | set(pred_labels)))
    report_dict = classification_report(
        true_labels,
        pred_labels,
        labels=eval_classes,
        output_dict=True,
        zero_division=0,
    )
    df_report = pd.DataFrame(report_dict).transpose()

    # Breakdown by Background
    bg_breakdown = {}
    for bg, group in df_preds.groupby("background"):
        bg_breakdown[bg] = {
            "total": len(group),
            "correct": int(group["correct"].sum()),
            "accuracy": round(float(group["correct"].mean()), 4),
            "avg_confidence": round(float(group["confidence"].mean()), 4),
        }

    # Breakdown by Signer
    signer_breakdown = {}
    for signer, group in df_preds.groupby("signer"):
        signer_breakdown[signer] = {
            "total": len(group),
            "correct": int(group["correct"].sum()),
            "accuracy": round(float(group["correct"].mean()), 4),
            "avg_confidence": round(float(group["confidence"].mean()), 4),
        }

    # 9. Save Artifacts
    os.makedirs(output_dir, exist_ok=True)
    preds_csv_path = os.path.join(output_dir, "realworld_predictions.csv")
    report_csv_path = os.path.join(output_dir, "realworld_classification_report.csv")
    cm_path = os.path.join(output_dir, "realworld_confusion_matrix.png")
    summary_path = os.path.join(output_dir, "realworld_summary.json")

    df_preds.to_csv(preds_csv_path, index=False)
    df_report.to_csv(report_csv_path, index=True)

    cm = confusion_matrix(true_labels, pred_labels, labels=eval_classes)
    plot_cm(cm, eval_classes, f"Real-World Test Confusion Matrix ({len(collected_samples)} samples)", cm_path)

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
        "total_samples": len(collected_samples),
        "overall_accuracy": round(float(overall_acc), 4),
        "macro_f1": round(float(report_dict["macro avg"]["f1-score"]), 4),
        "weighted_f1": round(float(report_dict["weighted avg"]["f1-score"]), 4),
        "average_latency_ms": round(avg_latency_ms, 2),
        "background_breakdown": bg_breakdown,
        "signer_breakdown": signer_breakdown,
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 76)
    print("REAL-WORLD EVALUATION RESULTS SUMMARY:")
    print(f"  Total Samples Evaluated: {len(collected_samples)}")
    print(f"  Overall Accuracy:        {overall_acc * 100:.2f}%")
    print(f"  Macro F1-Score:          {report_dict['macro avg']['f1-score'] * 100:.2f}%")
    if bg_breakdown:
        print("  Accuracy by Background:")
        for bg, stats in bg_breakdown.items():
            print(f"    - {bg}: {stats['accuracy']*100:.1f}% ({stats['correct']}/{stats['total']})")
    if signer_breakdown:
        print("  Accuracy by Signer:")
        for signer, stats in signer_breakdown.items():
            print(f"    - {signer}: {stats['accuracy']*100:.1f}% ({stats['correct']}/{stats['total']})")
    print(f"  Saved artifacts to: {output_dir}")
    print("=" * 76 + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate CNN V4 on real-world test images.")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=DEFAULT_REALWORLD_DIR,
        help="Path to realworld test dataset folder",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=DEFAULT_CHECKPOINT,
        help="Path to trained CNN V4 model checkpoint",
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
    evaluate_realworld(
        checkpoint_path=args.checkpoint,
        data_dir=args.data_dir,
        mapping_path=args.mapping,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
