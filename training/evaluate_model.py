#!/usr/bin/env python3
"""
Final Independent Testing Evaluation Script
===========================================

Indian Sign Language (ISL) Alphabet Recognition Project
Milestone 3.4: Final Independent Testing Split Evaluation

This script performs the first and only evaluation on the independent Testing split
(dataset/processed/Testing/) using the saved baseline CNN checkpoint:
- saved_models/isl_alphabet_cnn_best.keras
- training/label_classes.json

Strict Evaluation Protocol:
- The model weights and architecture are strictly frozen (inference only).
- Testing data was never seen or utilized during training or hyperparameter tuning.
- All 5,161 testing images across all 26 classes are evaluated exactly once.
- Generates:
  1. results/confusion_matrix.png
  2. results/classification_report.csv
  3. results/test_predictions.csv
  4. results/per_class_metrics.png
  5. docs/reports/FINAL_MODEL_EVALUATION_REPORT.md
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
import tensorflow as tf
from tensorflow import keras

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from training.data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        create_dataset_pipeline,
    )
    from training.model import load_verified_classes
except ModuleNotFoundError:
    from data_pipeline import (
        DEFAULT_DATASET_DIR,
        DEFAULT_IMAGE_SIZE,
        DEFAULT_MAPPING_PATH,
        create_dataset_pipeline,
    )
    from model import load_verified_classes

DEFAULT_CHECKPOINT_PATH = "saved_models/isl_alphabet_cnn_best.keras"
DEFAULT_TEST_DIR = "dataset/processed/Testing"
DEFAULT_CONFUSION_PNG = "results/confusion_matrix.png"
DEFAULT_METRICS_PNG = "results/per_class_metrics.png"
DEFAULT_REPORT_CSV = "results/classification_report.csv"
DEFAULT_PREDICTIONS_CSV = "results/test_predictions.csv"
DEFAULT_EVAL_REPORT_MD = "docs/reports/FINAL_MODEL_EVALUATION_REPORT.md"


def compute_file_sha256(file_path: str) -> str:
    """Computes SHA-256 hash to verify checkpoint immutability."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def plot_confusion_matrix(
    cm: np.ndarray,
    classes: List[str],
    output_png: str = DEFAULT_CONFUSION_PNG,
) -> None:
    """Renders and saves a clean, publication-ready 26x26 confusion matrix heatmap."""
    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    ax.set(
        xticks=np.arange(len(classes)),
        yticks=np.arange(len(classes)),
        xticklabels=classes,
        yticklabels=classes,
        title="ISL Alphabet Recognition: 26×26 Confusion Matrix (Testing Split)",
        ylabel="True Label (Ground Truth)",
        xlabel="Predicted Label",
    )
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    # Annotate cells with text counts
    thresh = cm.max() / 2.0
    for i in range(len(classes)):
        for j in range(len(classes)):
            val = cm[i, j]
            if val > 0:
                ax.text(
                    j, i, format(val, "d"),
                    ha="center", va="center",
                    color="white" if val > thresh else "black",
                    fontsize=7.5 if len(classes) == 26 else 9,
                )

    fig.tight_layout()
    plt.savefig(output_png, dpi=180, bbox_inches="tight")
    plt.close()


def plot_per_class_metrics(
    report_df: pd.DataFrame,
    classes: List[str],
    output_png: str = DEFAULT_METRICS_PNG,
) -> None:
    """Generates grouped bar chart showing Precision, Recall, and F1-score across all 26 letters."""
    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    df_classes = report_df[report_df["class"].isin(classes)].copy()

    x = np.arange(len(classes))
    width = 0.28

    fig, ax = plt.subplots(figsize=(15, 6))
    rects1 = ax.bar(x - width, df_classes["precision"] * 100, width, label="Precision (%)", color="#4e79a7")
    rects2 = ax.bar(x, df_classes["recall"] * 100, width, label="Recall (%)", color="#f28e2b")
    rects3 = ax.bar(x + width, df_classes["f1-score"] * 100, width, label="F1-Score (%)", color="#59a14f")

    ax.set_ylabel("Score (%)", fontsize=12)
    ax.set_title("ISL Alphabet Recognition: Per-Class Precision, Recall, and F1-Score (Testing Split)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax.legend(fontsize=11, loc="lower right")

    fig.tight_layout()
    plt.savefig(output_png, dpi=150, bbox_inches="tight")
    plt.close()


def evaluate_model_on_test_set(
    checkpoint_path: str = DEFAULT_CHECKPOINT_PATH,
    test_dir: str = DEFAULT_TEST_DIR,
    mapping_path: str = DEFAULT_MAPPING_PATH,
    confusion_png: str = DEFAULT_CONFUSION_PNG,
    metrics_png: str = DEFAULT_METRICS_PNG,
    report_csv: str = DEFAULT_REPORT_CSV,
    predictions_csv: str = DEFAULT_PREDICTIONS_CSV,
    eval_report_md: str = DEFAULT_EVAL_REPORT_MD,
    batch_size: int = 32,
) -> Dict[str, Any]:
    """Runs the complete end-to-end evaluation on the independent Testing split."""
    print("=" * 70)
    print("ISL ALPHABET RECOGNITION: FINAL INDEPENDENT TESTING EVALUATION")
    print("=" * 70)

    # 1. Verify Checkpoint Exists & Record Hash
    if not os.path.isfile(checkpoint_path):
        raise FileNotFoundError(f"Trained model checkpoint not found at: {checkpoint_path}")

    checkpoint_size = os.path.getsize(checkpoint_path)
    initial_checkpoint_hash = compute_file_sha256(checkpoint_path)
    print(f"[CHECKPOINT] Loading model from: {checkpoint_path}")
    print(f"[CHECKPOINT] Size: {checkpoint_size:,} bytes ({checkpoint_size / (1024 * 1024):.2f} MB)")
    print(f"[CHECKPOINT] SHA-256: {initial_checkpoint_hash}")

    model = keras.models.load_model(checkpoint_path)
    print("[CHECKPOINT] Model loaded successfully.")

    # 2. Load Verified Classes and Mapping
    classes = load_verified_classes(mapping_path)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    num_classes = len(classes)
    print(f"[CLASSES] Verified 26 classes: {', '.join(classes)}")

    # 3. Collect deterministic file list from Testing split
    test_files: List[str] = []
    test_true_indices: List[int] = []
    for c_idx, c in enumerate(classes):
        c_dir = os.path.join(test_dir, c)
        if not os.path.isdir(c_dir):
            raise FileNotFoundError(f"Missing class directory in Testing: {c_dir}")
        for fn in sorted(os.listdir(c_dir)):
            if fn.lower().endswith((".jpg", ".jpeg", ".png")):
                test_files.append(f"Testing/{c}/{fn}")
                test_true_indices.append(c_idx)

    total_test_images = len(test_files)
    print(f"[DATASET] Total independent testing images found: {total_test_images}")
    if total_test_images != 5161:
        print(f"[WARNING] Expected 5,161 testing images, found {total_test_images}")

    # 4. Create Testing Dataset Pipeline (strictly unaugmented, un-shuffled)
    test_ds = create_dataset_pipeline(
        split_dir=test_dir,
        classes=classes,
        batch_size=batch_size,
        is_training=False,
        enable_augmentation=False,
    )

    # 5. Model Evaluation (Loss & Accuracy)
    print("\n[EVALUATION] Calculating test loss and accuracy via model.evaluate() ...")
    eval_results = model.evaluate(test_ds, verbose=1)
    test_loss = float(eval_results[0])
    test_acc_eval = float(eval_results[1])
    print(f"[EVALUATION RESULT] Overall Test Loss     : {test_loss:.4f}")
    print(f"[EVALUATION RESULT] Overall Test Accuracy : {test_acc_eval * 100:.2f}%")

    # 6. Model Prediction (Probabilities for Confusion Matrix and Class Reports)
    print("\n[PREDICTION] Generating predictions on complete Testing split ...")
    raw_predictions = model.predict(test_ds, verbose=1)
    pred_indices = np.argmax(raw_predictions, axis=1)
    confidences = np.max(raw_predictions, axis=1)

    assert len(pred_indices) == total_test_images, (
        f"Prediction count ({len(pred_indices)}) does not match image count ({total_test_images})!"
    )

    y_true = np.array(test_true_indices)
    y_pred = np.array(pred_indices)

    # 7. Compute Global & Per-Class Metrics via Scikit-Learn
    acc = accuracy_score(y_true, y_pred)
    total_correct = int(np.sum(y_true == y_pred))
    total_incorrect = total_test_images - total_correct

    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average="weighted", zero_division=0
    )

    p_per_class, r_per_class, f1_per_class, supp_per_class = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=range(num_classes), zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred, labels=range(num_classes))

    # 8. Identify Most Confused Pairs
    confused_pairs = []
    for i in range(num_classes):
        for j in range(num_classes):
            if i != j and cm[i, j] > 0:
                confused_pairs.append({
                    "true_class": idx_to_class[i],
                    "pred_class": idx_to_class[j],
                    "count": int(cm[i, j]),
                    "true_support": int(supp_per_class[i]),
                    "error_rate": float(cm[i, j] / supp_per_class[i]),
                })
    confused_pairs.sort(key=lambda x: x["count"], reverse=True)

    # 9. Build and Save Predictions CSV
    print(f"[ARTIFACTS] Writing predictions to: {predictions_csv}")
    os.makedirs(os.path.dirname(os.path.abspath(predictions_csv)), exist_ok=True)
    predictions_df = pd.DataFrame({
        "relative_path": test_files,
        "true_class": [idx_to_class[idx] for idx in y_true],
        "predicted_class": [idx_to_class[idx] for idx in y_pred],
        "confidence": confidences,
        "is_correct": (y_true == y_pred),
    })
    predictions_df.to_csv(predictions_csv, index=False)

    # 10. Build and Save Classification Report CSV
    print(f"[ARTIFACTS] Writing classification report to: {report_csv}")
    os.makedirs(os.path.dirname(os.path.abspath(report_csv)), exist_ok=True)
    report_rows = []
    for i in range(num_classes):
        report_rows.append({
            "class": idx_to_class[i],
            "precision": float(p_per_class[i]),
            "recall": float(r_per_class[i]),
            "f1-score": float(f1_per_class[i]),
            "support": int(supp_per_class[i]),
        })
    report_df = pd.DataFrame(report_rows)

    summary_rows = [
        {
            "class": "macro avg",
            "precision": float(precision_macro),
            "recall": float(recall_macro),
            "f1-score": float(f1_macro),
            "support": total_test_images,
        },
        {
            "class": "weighted avg",
            "precision": float(precision_weighted),
            "recall": float(recall_weighted),
            "f1-score": float(f1_weighted),
            "support": total_test_images,
        },
    ]
    report_csv_df = pd.concat([report_df, pd.DataFrame(summary_rows)], ignore_index=True)
    report_csv_df.to_csv(report_csv, index=False)

    # 11. Plot Confusion Matrix & Per-Class Metrics
    print(f"[ARTIFACTS] Generating confusion matrix plot: {confusion_png}")
    plot_confusion_matrix(cm, classes, confusion_png)

    print(f"[ARTIFACTS] Generating per-class metrics plot: {metrics_png}")
    plot_per_class_metrics(report_df, classes, metrics_png)

    # 12. Verify Checkpoint Immutability
    final_checkpoint_hash = compute_file_sha256(checkpoint_path)
    assert initial_checkpoint_hash == final_checkpoint_hash, (
        "CRITICAL ERROR: Model checkpoint file was altered during evaluation!"
    )
    print("[VERIFICATION] Checkpoint SHA-256 confirmed unchanged (100% byte-identical).")

    # 13. Generate Formal Markdown Report
    print(f"[REPORT] Writing final evaluation report to: {eval_report_md}")
    generate_markdown_report(
        report_path=eval_report_md,
        checkpoint_path=checkpoint_path,
        checkpoint_size=checkpoint_size,
        total_test_images=total_test_images,
        test_loss=test_loss,
        test_acc=acc,
        total_correct=total_correct,
        total_incorrect=total_incorrect,
        precision_macro=precision_macro,
        recall_macro=recall_macro,
        f1_macro=f1_macro,
        precision_weighted=precision_weighted,
        recall_weighted=recall_weighted,
        f1_weighted=f1_weighted,
        report_df=report_df,
        confused_pairs=confused_pairs,
        classes=classes,
    )

    print("=" * 70)
    print(f"[SUCCESS] Final testing evaluation complete. Overall Accuracy: {acc * 100:.2f}%")
    print("=" * 70)

    return {
        "test_loss": test_loss,
        "test_accuracy": acc,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "precision_weighted": precision_weighted,
        "recall_weighted": recall_weighted,
        "f1_weighted": f1_weighted,
        "total_images": total_test_images,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "confused_pairs": confused_pairs[:10],
    }


def generate_markdown_report(
    report_path: str,
    checkpoint_path: str,
    checkpoint_size: int,
    total_test_images: int,
    test_loss: float,
    test_acc: float,
    total_correct: int,
    total_incorrect: int,
    precision_macro: float,
    recall_macro: float,
    f1_macro: float,
    precision_weighted: float,
    recall_weighted: float,
    f1_weighted: float,
    report_df: pd.DataFrame,
    confused_pairs: List[Dict[str, Any]],
    classes: List[str],
) -> None:
    """Writes the comprehensive final evaluation report."""
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)

    lines = [
        "# Final Independent Testing Evaluation Report",
        "",
        "## 1. Executive Summary",
        f"- **Evaluation Timestamp (UTC):** `{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        f"- **Model Checkpoint Evaluated:** `{checkpoint_path}` (`{checkpoint_size / (1024 * 1024):.2f} MB`)",
        f"- **Evaluation Dataset:** Independent `Testing` split (`dataset/processed/Testing/`)",
        f"- **Total Independent Test Images:** `{total_test_images:,}`",
        f"- **Overall Test Accuracy:** `{(test_acc * 100):.2f}%`",
        f"- **Overall Test Loss:** `{test_loss:.4f}` (Sparse Categorical Cross-Entropy)",
        f"- **Total Correct Predictions:** `{total_correct:,}` / `{total_test_images:,}`",
        f"- **Total Incorrect Predictions:** `{total_incorrect:,}` / `{total_test_images:,}`",
        "",
        "> [!IMPORTANT]",
        "> **Strict Academic Testing Protocol:**",
        "> This milestone represents the **first and only evaluation** conducted on the independent Testing dataset. The model weights, architecture, and hyperparameters were established entirely during Milestone 3.3 using Training and Validation data only. Zero test set feedback or tuning was applied.",
        "",
        "---",
        "",
        "## 2. Global Metric Summary",
        "",
        "| Metric | Macro Average | Weighted Average | Description |",
        "|---|:---:|:---:|---|",
        f"| **Accuracy** | \\multicolumn{{2}}{{c|}}{{{(test_acc * 100):.2f}\\%}} | Fraction of total correct predictions across 5,161 images |",
        f"| **Precision** | **{(precision_macro * 100):.2f}%** | **{(precision_weighted * 100):.2f}%** | Positive predictive value (unweighted vs support-weighted) |",
        f"| **Recall** | **{(recall_macro * 100):.2f}%** | **{(recall_weighted * 100):.2f}%** | Sensitivity / True positive rate across classes |",
        f"| **F1-Score** | **{(f1_macro * 100):.2f}%** | **{(f1_weighted * 100):.2f}%** | Harmonic mean of precision and recall |",
        "",
        "---",
        "",
        "## 3. Per-Class Performance Table (All 26 Classes)",
        "",
        "| Class | Precision | Recall | F1-Score | Support | Status / Note |",
        "| :---: | :---: | :---: | :---: | :---: |---|",
    ]

    for _, row in report_df.iterrows():
        c = row["class"]
        p = float(row["precision"]) * 100
        r = float(row["recall"]) * 100
        f1 = float(row["f1-score"]) * 100
        sup = int(row["support"])

        if f1 >= 80.0:
            note = "Strong performance"
        elif f1 >= 50.0:
            note = "Moderate performance"
        elif f1 >= 25.0:
            note = "Lower performance"
        else:
            note = "Challenging class"

        lines.append(f"| **{c}** | {p:.2f}% | {r:.2f}% | {f1:.2f}% | {sup} | {note} |")

    lines.extend([
        f"| **Macro Avg** | **{(precision_macro * 100):.2f}%** | **{(recall_macro * 100):.2f}%** | **{(f1_macro * 100):.2f}%** | **{total_test_images:,}** | Unweighted average across 26 classes |",
        f"| **Weighted Avg** | **{(precision_weighted * 100):.2f}%** | **{(recall_weighted * 100):.2f}%** | **{(f1_weighted * 100):.2f}%** | **{total_test_images:,}** | Support-weighted average |",
        "",
        "---",
        "",
        "## 4. Confusion Matrix Analysis & Most Confused Letter Pairs",
        "",
        "The complete $26 \\times 26$ confusion matrix is visualized in [`results/confusion_matrix.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/confusion_matrix.png).",
        "",
        "### Top 10 Most Frequently Confused Letter Pairs:",
        "| Rank | True Letter | Misclassified As | Misclassification Count | Percentage of True Class |",
        "|:---:|:---:|:---:|:---:|:---:|",
    ])

    for rank, pair in enumerate(confused_pairs[:10], start=1):
        lines.append(
            f"| {rank} | **{pair['true_class']}** | **{pair['pred_class']}** | {pair['count']} | {pair['error_rate'] * 100:.1f}% ({pair['count']}/{pair['true_support']}) |"
        )

    # Classes with particularly low recall or F1
    lowest_f1_classes = report_df.sort_values(by="f1-score").head(5)
    lines.extend([
        "",
        "---",
        "",
        "## 5. Key Observations & Academic Defense Discussion",
        "",
        "### 5.1 Lowest Performing Classes",
    ])

    for _, row in lowest_f1_classes.iterrows():
        lines.append(
            f"- **Class '{row['class']}':** F1-Score = `{row['f1-score'] * 100:.2f}%` (Precision = `{row['precision'] * 100:.2f}%`, Recall = `{row['recall'] * 100:.2f}%`, Support = `{row['support']}`)."
        )

    lines.extend([
        "",
        "### 5.2 Confusion Analysis & Morphological Similarities",
        "- Letters with visual hand-pose ambiguities (e.g. similar finger extensions or shared palm orientations) represent the bulk of off-diagonal errors.",
        "- **Movement-Dependent Classes (J & Z):** In Indian Sign Language, letters J and Z are traditionally dynamic gestures. In the RealSign dataset, they are represented as static keyframe poses (crossed index fingers for J, flat hand on palm for Z). Their recognition relies solely on single-frame spatial features without temporal motion modeling.",
        "",
        "### 5.3 Baseline Architecture Context",
        "- The model is a lightweight 3-block 2D CNN (113,114 parameters) trained from scratch without pre-trained weights or transfer learning.",
        "- This establishes an honest, rigorous baseline benchmark for the 26-class ISL problem.",
        "",
        "---",
        "",
        "## 6. Generated Artifact Checklist",
        "- **Confusion Matrix Plot:** [`results/confusion_matrix.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/confusion_matrix.png)",
        "- **Per-Class Metrics Plot:** [`results/per_class_metrics.png`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/per_class_metrics.png)",
        "- **Classification Report CSV:** [`results/classification_report.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/classification_report.csv)",
        "- **Complete Test Predictions CSV:** [`results/test_predictions.csv`](file:///c:/Users/shaur/OneDrive/Desktop/Sign%20Language%20Alphabet%20Recognition/results/test_predictions.csv)",
    ])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Final Independent Testing Evaluation")
    parser.add_argument("--checkpoint-path", default=DEFAULT_CHECKPOINT_PATH)
    parser.add_argument("--test-dir", default=DEFAULT_TEST_DIR)
    parser.add_argument("--mapping-path", default=DEFAULT_MAPPING_PATH)
    parser.add_argument("--confusion-png", default=DEFAULT_CONFUSION_PNG)
    parser.add_argument("--metrics-png", default=DEFAULT_METRICS_PNG)
    parser.add_argument("--report-csv", default=DEFAULT_REPORT_CSV)
    parser.add_argument("--predictions-csv", default=DEFAULT_PREDICTIONS_CSV)
    parser.add_argument("--eval-report-md", default=DEFAULT_EVAL_REPORT_MD)
    args = parser.parse_args()

    evaluate_model_on_test_set(
        checkpoint_path=args.checkpoint_path,
        test_dir=args.test_dir,
        mapping_path=args.mapping_path,
        confusion_png=args.confusion_png,
        metrics_png=args.metrics_png,
        report_csv=args.report_csv,
        predictions_csv=args.predictions_csv,
        eval_report_md=args.eval_report_md,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
