#!/usr/bin/env python3
"""
Final Model Selection & Independent Test Evaluation Script (Model V4)
=====================================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Phase 6 — Milestone 6.6: Final Model Selection & Independent Test Evaluation

Candidate Model:
----------------
- Selected: CNN Model V4 (Experiment 3)
- Checkpoint: saved_models/experiments/isl_alphabet_cnn_v4_best.keras
- Architecture: 3 Double-Conv Blocks with BatchNormalization, GlobalAveragePooling2D,
  Dense(128, ReLU), Dropout(0.40), L2 Kernel Regularization (lambda = 0.0001), Dense(26, Softmax).
- Input: 128x128x3

Evaluation Protocols:
---------------------
- Split: dataset/processed/Testing/ (Strict independent holdout evaluation)
- Preprocessing: Deterministic rescaling (1/255.0), bilinear resize to 128x128.
- Strictly NO data augmentation during evaluation.
- Immutability check: Computes SHA-256 before and after inference to ensure the checkpoint is unmodified.

Artifacts Generated:
--------------------
- results/final/v4_test_classification_report.csv
- results/final/v4_test_predictions.csv
- results/final/v4_test_confusion_matrix.png
- results/final/v4_test_per_class_metrics.png
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
import tensorflow as tf
from tensorflow import keras

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_CHECKPOINT = os.path.join(REPO_ROOT, "saved_models", "experiments", "isl_alphabet_cnn_v4_best.keras")
DEFAULT_TEST_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Testing")
DEFAULT_MAPPING = os.path.join(REPO_ROOT, "training", "label_classes.json")
FINAL_RESULTS_DIR = os.path.join(REPO_ROOT, "results", "final")

REPORT_CSV_PATH = os.path.join(FINAL_RESULTS_DIR, "v4_test_classification_report.csv")
PREDICTIONS_CSV_PATH = os.path.join(FINAL_RESULTS_DIR, "v4_test_predictions.csv")
CONFUSION_PNG_PATH = os.path.join(FINAL_RESULTS_DIR, "v4_test_confusion_matrix.png")
METRICS_PNG_PATH = os.path.join(FINAL_RESULTS_DIR, "v4_test_per_class_metrics.png")


def compute_file_sha256(file_path: str) -> str:
    """Computes SHA-256 hash to verify file integrity and immutability."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_verified_classes(mapping_path: str) -> List[str]:
    """Loads and validates class mapping."""
    if not os.path.isfile(mapping_path):
        raise FileNotFoundError(f"Class mapping JSON not found: {mapping_path}")
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    classes = data.get("classes", [])
    if len(classes) != 26:
        raise ValueError(f"Expected 26 classes, found {len(classes)}")
    return classes


def plot_confusion_matrix(cm: np.ndarray, classes: List[str], output_path: str):
    """Renders high-resolution 26x26 confusion matrix."""
    plt.figure(figsize=(14, 12))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("ISL Alphabet Recognition: Final Independent Test Confusion Matrix (Model V4)", fontsize=13, fontweight="bold", pad=12)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=9)
    plt.yticks(tick_marks, classes, fontsize=9)
    plt.xlabel("Predicted Label", fontsize=11, fontweight="bold")
    plt.ylabel("True Label (Ground Truth)", fontsize=11, fontweight="bold")

    thresh = cm.max() / 2.0
    for i in range(len(classes)):
        for j in range(len(classes)):
            val = cm[i, j]
            if val > 0:
                plt.text(
                    j, i, str(val),
                    ha="center", va="center",
                    color="white" if val > thresh else "black",
                    fontsize=8,
                )

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"Confusion matrix saved to: {output_path}")


def plot_per_class_metrics(report_df: pd.DataFrame, classes: List[str], output_path: str):
    """Renders grouped bar chart of per-class Precision, Recall, and F1."""
    df_classes = report_df[report_df["class"].isin(classes)].copy()
    x = np.arange(len(classes))
    width = 0.28

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(x - width, df_classes["precision"] * 100, width, label="Precision (%)", color="#2b5c8f")
    ax.bar(x, df_classes["recall"] * 100, width, label="Recall (%)", color="#e07a5f")
    ax.bar(x + width, df_classes["f1-score"] * 100, width, label="F1-Score (%)", color="#3d405b")

    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("ISL Alphabet Recognition: Per-Class Precision, Recall, and F1-Score (Independent Testing Split)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.legend(fontsize=10, loc="lower right")

    fig.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Per-class metrics plot saved to: {output_path}")


def run_test_evaluation(
    checkpoint_path: str = DEFAULT_CHECKPOINT,
    test_dir: str = DEFAULT_TEST_DIR,
    mapping_path: str = DEFAULT_MAPPING,
    batch_size: int = 32,
) -> Dict[str, Any]:
    """Runs the independent test evaluation and generates final evaluation artifacts."""
    os.makedirs(FINAL_RESULTS_DIR, exist_ok=True)

    print("=" * 75)
    print("PHASE 6 — MILESTONE 6.6: FINAL MODEL INDEPENDENT TEST EVALUATION")
    print("=" * 75)

    # 1. Model Integrity Check (Pre-Evaluation)
    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")

    pre_hash = compute_file_sha256(checkpoint_path)
    file_size_bytes = os.path.getsize(checkpoint_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    print(f"[CHECKPOINT] Path: {checkpoint_path}")
    print(f"[CHECKPOINT] File Size: {file_size_bytes:,} bytes ({file_size_mb:.2f} MB)")
    print(f"[CHECKPOINT] Pre-Eval SHA-256: {pre_hash}")

    model = keras.models.load_model(checkpoint_path)
    print(f"[CHECKPOINT] Model loaded successfully.")
    print(f"[CHECKPOINT] Input shape: {model.input_shape}")
    print(f"[CHECKPOINT] Output shape: {model.output_shape}")

    total_params = sum(int(tf.size(v)) for v in model.weights)
    trainable_params = sum(int(tf.size(v)) for v in model.trainable_weights)
    print(f"[CHECKPOINT] Total Parameters: {total_params:,}")
    print(f"[CHECKPOINT] Trainable Parameters: {trainable_params:,}")

    # 2. Class Mapping Verification
    classes = load_verified_classes(mapping_path)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    print(f"[CLASSES] Verified 26 classes: {classes[0]}..{classes[-1]}")

    # 3. Collect Test Images
    print(f"\n[DATASET] Scanning independent testing split: {test_dir}")
    test_records: List[Dict[str, Any]] = []
    for c_idx, c in enumerate(classes):
        c_folder = os.path.join(test_dir, c)
        if not os.path.isdir(c_folder):
            raise FileNotFoundError(f"Missing test directory for class '{c}': {c_folder}")
        files = sorted(os.listdir(c_folder))
        for fn in files:
            if fn.lower().endswith((".jpg", ".jpeg", ".png")):
                full_path = os.path.join(c_folder, fn)
                rel_path = os.path.relpath(full_path, REPO_ROOT)
                test_records.append({
                    "full_path": full_path,
                    "rel_path": rel_path,
                    "filename": fn,
                    "true_class": c,
                    "true_idx": c_idx,
                })

    num_test_samples = len(test_records)
    print(f"[DATASET] Total independent test images discovered: {num_test_samples:,}")

    # 4. Deterministic Batch Processing & Inference
    print("\n[INFERENCE] Commencing batched evaluation (batch_size = 32)...")
    start_eval_time = time.time()

    all_y_true = []
    all_y_pred = []
    all_confidences = []
    all_probabilities = []

    # Process in batches
    for i in range(0, num_test_samples, batch_size):
        batch_slice = test_records[i : i + batch_size]
        batch_images = []
        for record in batch_slice:
            # Deterministic preprocessing: PIL load RGB -> resize 128x128 -> / 255.0 float32
            img = Image.open(record["full_path"]).convert("RGB").resize((128, 128))
            arr = np.array(img, dtype=np.float32) / 255.0
            batch_images.append(arr)

        batch_tensor = np.stack(batch_images, axis=0)
        preds = model.predict(batch_tensor, verbose=0)

        for j, pred_vec in enumerate(preds):
            pred_idx = int(np.argmax(pred_vec))
            conf = float(pred_vec[pred_idx])
            true_idx = batch_slice[j]["true_idx"]

            all_y_true.append(true_idx)
            all_y_pred.append(pred_idx)
            all_confidences.append(conf)
            all_probabilities.append(pred_vec)

        if (i // batch_size) % 25 == 0 or (i + batch_size) >= num_test_samples:
            print(f"  Processed {min(i + batch_size, num_test_samples):,}/{num_test_samples:,} images...")

    eval_duration = time.time() - start_eval_time
    print(f"[INFERENCE] Evaluation completed in {eval_duration:.2f} seconds ({num_test_samples / eval_duration:.1f} img/sec).")

    all_y_true_np = np.array(all_y_true)
    all_y_pred_np = np.array(all_y_pred)
    all_prob_np = np.array(all_probabilities)

    # 5. Model Integrity Check (Post-Evaluation)
    post_hash = compute_file_sha256(checkpoint_path)
    if pre_hash != post_hash:
        raise RuntimeError(f"FATAL: Checkpoint was modified during evaluation! Pre: {pre_hash}, Post: {post_hash}")
    print(f"\n[INTEGRITY] SHA-256 match verified post-evaluation: {post_hash}")

    # 6. Quantitative Metrics Computation
    correct_count = int(np.sum(all_y_true_np == all_y_pred_np))
    incorrect_count = num_test_samples - correct_count
    test_accuracy = correct_count / num_test_samples

    # Compute Loss
    scce = keras.losses.SparseCategoricalCrossentropy(reduction="sum_over_batch_size")
    pure_ce_loss = float(scce(all_y_true_np, all_prob_np).numpy())
    l2_penalty = sum(float(tf.reduce_sum(l).numpy()) for l in model.losses)
    total_test_loss = pure_ce_loss + l2_penalty

    # Sklearn classification metrics
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        all_y_true_np, all_y_pred_np, average="macro", zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        all_y_true_np, all_y_pred_np, average="weighted", zero_division=0
    )

    report_dict = classification_report(
        all_y_true_np,
        all_y_pred_np,
        target_names=classes,
        output_dict=True,
        zero_division=0,
    )

    # Format classification report table
    report_rows = []
    for c in classes:
        report_rows.append({
            "class": c,
            "precision": report_dict[c]["precision"],
            "recall": report_dict[c]["recall"],
            "f1-score": report_dict[c]["f1-score"],
            "support": int(report_dict[c]["support"]),
        })
    report_df = pd.DataFrame(report_rows)
    report_df.to_csv(REPORT_CSV_PATH, index=False)
    print(f"\n[ARTIFACT] Classification report saved to: {REPORT_CSV_PATH}")

    # 7. Predictions CSV
    predictions_rows = []
    for idx, rec in enumerate(test_records):
        pred_idx = all_y_pred[idx]
        is_corr = bool(all_y_true[idx] == pred_idx)
        predictions_rows.append({
            "sample_index": idx,
            "filename": rec["filename"],
            "relative_path": rec["rel_path"],
            "true_class": rec["true_class"],
            "predicted_class": idx_to_class[pred_idx],
            "confidence": round(all_confidences[idx], 6),
            "correct": is_corr,
        })
    predictions_df = pd.DataFrame(predictions_rows)
    predictions_df.to_csv(PREDICTIONS_CSV_PATH, index=False)
    print(f"[ARTIFACT] Predictions table saved to: {PREDICTIONS_CSV_PATH}")

    # 8. Confusion Matrix & Per-Class Plots
    cm = confusion_matrix(all_y_true_np, all_y_pred_np)
    plot_confusion_matrix(cm, classes, CONFUSION_PNG_PATH)
    plot_per_class_metrics(report_df, classes, METRICS_PNG_PATH)

    # 9. Difficult Classes Breakdown
    difficult_classes = ["W", "Z", "S", "Y", "Q"]
    diff_analysis = {}
    for dc in difficult_classes:
        c_idx = class_to_idx[dc]
        row = cm[c_idx]
        tot = int(np.sum(row))
        corr = int(row[c_idx])
        top_confusions = []
        for p_idx in np.argsort(row)[::-1]:
            if p_idx != c_idx and row[p_idx] > 0:
                top_confusions.append((idx_to_class[p_idx], int(row[p_idx]), round(row[p_idx] / tot * 100, 1)))
        diff_analysis[dc] = {
            "total": tot,
            "correct": corr,
            "precision": report_dict[dc]["precision"],
            "recall": report_dict[dc]["recall"],
            "f1": report_dict[dc]["f1-score"],
            "top_confusions": top_confusions[:4],
        }

    summary = {
        "checkpoint_path": checkpoint_path,
        "checkpoint_hash": post_hash,
        "total_test_samples": num_test_samples,
        "correct_count": correct_count,
        "incorrect_count": incorrect_count,
        "test_accuracy": test_accuracy,
        "pure_ce_loss": pure_ce_loss,
        "l2_penalty": l2_penalty,
        "total_test_loss": total_test_loss,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_weighted": f1_weighted,
        "eval_duration_sec": eval_duration,
        "difficult_classes": diff_analysis,
        "report_dict": report_dict,
        "cm": cm,
        "classes": classes,
    }

    print("\n" + "=" * 75)
    print("                FINAL INDEPENDENT TEST METRICS SUMMARY")
    print("=" * 75)
    print(f"Total Test Samples:            {num_test_samples:,}")
    print(f"Correct Predictions:           {correct_count:,} ({test_accuracy * 100:.2f}%)")
    print(f"Incorrect Predictions:         {incorrect_count:,} ({(1 - test_accuracy) * 100:.2f}%)")
    print(f"Independent Test Accuracy:     {test_accuracy * 100:.2f}%")
    print(f"Pure Cross-Entropy Loss:       {pure_ce_loss:.4f}")
    print(f"L2 Penalty Term:               {l2_penalty:.4f}")
    print(f"Total Test Loss:               {total_test_loss:.4f}")
    print(f"Macro Precision:               {precision_macro * 100:.2f}%")
    print(f"Macro Recall:                  {recall_macro * 100:.2f}%")
    print(f"Macro F1-Score:                {f1_macro * 100:.2f}%")
    print(f"Weighted F1-Score:             {f1_weighted * 100:.2f}%")
    print("=" * 75)

    print("\n[DIFFICULT CLASSES BREAKDOWN (TESTING SPLIT)]")
    for dc in difficult_classes:
        d_info = diff_analysis[dc]
        print(f"  Class {dc} (Total: {d_info['total']}, Correct: {d_info['correct']}): "
              f"P={d_info['precision']*100:.1f}%, R={d_info['recall']*100:.1f}%, F1={d_info['f1']*100:.1f}%")
        conf_str = ", ".join([f"{c}: {n} ({pct}%)" for c, n, pct in d_info["top_confusions"]])
        print(f"    Top Confusions: {conf_str}")
    print("=" * 75 + "\n")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Model V4 on independent Testing split")
    parser.add_argument("--checkpoint", type=str, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--test-dir", type=str, default=DEFAULT_TEST_DIR)
    parser.add_argument("--mapping", type=str, default=DEFAULT_MAPPING)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    run_test_evaluation(
        checkpoint_path=args.checkpoint,
        test_dir=args.test_dir,
        mapping_path=args.mapping,
        batch_size=args.batch_size,
    )
