#!/usr/bin/env python3
"""
Dataset Perceptual Hash (pHash/dHash) Near-Duplicate Audit Tool
==============================================================

Project: AI-Based Indian Sign Language (ISL) Alphabet Recognition
Purpose: Detect visual leakage / near-duplicate frames between Training and Testing splits.

Methodology:
- Computes Difference Hash (dHash, 64-bit gradient hash) for every image using PIL and NumPy.
- Compares test images against train images within each class using bitwise XOR Hamming distance.
- Hamming distance threshold:
  - distance == 0: Exact or near-exact pixel duplicate
  - distance <= 2: Perceptually near-identical frames (e.g. consecutive video frames, identical hand pose & background)
  - distance <= 4: Highly similar variant (slight lighting or micro-jitter)

Generates:
- results/audit/near_duplicates_summary.json
- results/audit/near_duplicate_pairs.csv
"""

import argparse
import datetime
import json
import os
import sys
import time
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAIN_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Training")
TEST_DIR = os.path.join(REPO_ROOT, "dataset", "processed", "Testing")
DEFAULT_OUTPUT_DIR = os.path.join(REPO_ROOT, "results", "audit")


def compute_dhash(img_path: str, hash_size: int = 8) -> int:
    """
    Computes a 64-bit difference hash (dHash) for an image.
    Resizes to (hash_size + 1, hash_size) in grayscale, compares adjacent pixels.
    """
    with Image.open(img_path) as img:
        gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
        pixels = np.asarray(gray, dtype=np.int32)
        # Difference between adjacent horizontal pixels
        diff = pixels[:, 1:] > pixels[:, :-1]
        # Pack boolean array into an integer hash
        hash_val = 0
        for bit in diff.flatten():
            hash_val = (hash_val << 1) | int(bit)
        return hash_val


def hamming_distance(h1: int, h2: int) -> int:
    """Calculates number of differing bits between two 64-bit integer hashes."""
    x = h1 ^ h2
    return bin(x).count("1")


def audit_near_duplicates(
    train_dir: str,
    test_dir: str,
    classes: List[str],
    hamming_thresh: int,
    output_dir: str,
) -> Dict[str, any]:
    print("=" * 76)
    print("SignAI — Train-Test Near-Duplicate & Visual Leakage Audit (pHash / dHash)")
    print("=" * 76)
    print(f"Hamming Distance Threshold: <= {hamming_thresh} bits (out of 64 bits)")
    print(f"Classes Audited ({len(classes)}): {', '.join(classes)}")
    print("=" * 76)

    near_dup_pairs = []
    class_stats = {}
    total_test_images = 0
    total_test_flagged = 0

    t_start = time.time()

    for cls in classes:
        cls_train_dir = os.path.join(train_dir, cls)
        cls_test_dir = os.path.join(test_dir, cls)

        if not os.path.isdir(cls_train_dir) or not os.path.isdir(cls_test_dir):
            print(f"Skipping class '{cls}': directory missing.")
            continue

        train_files = [f for f in os.listdir(cls_train_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))]
        test_files = [f for f in os.listdir(cls_test_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))]

        # Compute train hashes
        train_hashes = []
        for tf in train_files:
            p = os.path.join(cls_train_dir, tf)
            train_hashes.append((tf, compute_dhash(p)))

        # Compute test hashes and compare against train hashes
        cls_flagged_test_files = set()
        cls_pairs = []

        for tef in test_files:
            p = os.path.join(cls_test_dir, tef)
            te_hash = compute_dhash(p)

            # Check min distance to any train sample in same class
            min_dist = 64
            closest_train_file = None
            for tr_file, tr_hash in train_hashes:
                dist = hamming_distance(te_hash, tr_hash)
                if dist < min_dist:
                    min_dist = dist
                    closest_train_file = tr_file
                if dist == 0:
                    break

            if min_dist <= hamming_thresh:
                cls_flagged_test_files.add(tef)
                pair_record = {
                    "class": cls,
                    "test_file": tef,
                    "closest_train_file": closest_train_file,
                    "hamming_distance": min_dist,
                    "similarity_level": (
                        "Exact/Identical (dist=0)" if min_dist == 0
                        else f"Near-Duplicate (dist={min_dist})"
                    ),
                }
                cls_pairs.append(pair_record)
                near_dup_pairs.append(pair_record)

        total_test_images += len(test_files)
        total_test_flagged += len(cls_flagged_test_files)

        flag_pct = (len(cls_flagged_test_files) / len(test_files) * 100) if test_files else 0.0
        class_stats[cls] = {
            "train_samples": len(train_files),
            "test_samples": len(test_files),
            "flagged_near_duplicates": len(cls_flagged_test_files),
            "leakage_rate_pct": round(flag_pct, 2),
        }
        print(f"Class {cls:2s}: {len(cls_flagged_test_files):3d} / {len(test_files):3d} test images flagged ({flag_pct:5.1f}% near-duplicate)")

    total_time = time.time() - t_start
    overall_leakage_pct = (total_test_flagged / total_test_images * 100) if total_test_images else 0.0

    os.makedirs(output_dir, exist_ok=True)

    # Save CSV of pairs
    import pandas as pd
    df_pairs = pd.DataFrame(near_dup_pairs)
    csv_path = os.path.join(output_dir, "near_duplicate_pairs.csv")
    df_pairs.to_csv(csv_path, index=False)

    summary = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "hamming_distance_threshold": hamming_thresh,
        "classes_audited": classes,
        "total_test_images_analyzed": total_test_images,
        "total_near_duplicates_found": total_test_flagged,
        "overall_leakage_rate_pct": round(overall_leakage_pct, 2),
        "audit_duration_seconds": round(total_time, 2),
        "per_class_statistics": class_stats,
        "academic_interpretation": (
            "High near-duplicate rates indicate that the test set contains frames captured in the "
            "same continuous video sessions or from the same signers as the training split. "
            "Consequently, test accuracy scores (e.g. 99.94% on subsets or 86.34% overall) must be reported "
            "strictly as in-distribution evaluation on held-out frames, NOT as proof of signer-independent "
            "or cross-environment generalization."
        ),
    }

    summary_path = os.path.join(output_dir, "near_duplicates_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 76)
    print("NEAR-DUPLICATE AUDIT COMPLETE:")
    print(f"  Analyzed {total_test_images} test samples against corresponding train classes.")
    print(f"  Flagged near-duplicates (Hamming dist <= {hamming_thresh}): {total_test_flagged} ({overall_leakage_pct:.2f}%)")
    print(f"  Audit time: {total_time:.2f}s")
    print(f"  Results saved to: {output_dir}")
    print("=" * 76 + "\n")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Audit train-test near-duplicates using dHash.")
    parser.add_argument(
        "--classes",
        type=str,
        default="A,B,C,D,E,H,L,R",
        help="Comma-separated class letters to audit (default: 'A,B,C,D,E,H,L,R', or 'ALL' for all 26)",
    )
    parser.add_argument(
        "--hamming",
        type=int,
        default=2,
        help="Hamming distance threshold for near-duplicates (default: 2)",
    )
    parser.add_argument(
        "--train-dir",
        type=str,
        default=TRAIN_DIR,
        help="Path to processed Training directory",
    )
    parser.add_argument(
        "--test-dir",
        type=str,
        default=TEST_DIR,
        help="Path to processed Testing directory",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help="Path to output directory for audit artifacts",
    )

    args = parser.parse_args()
    if args.classes.strip().upper() == "ALL":
        target_classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    else:
        target_classes = [c.strip().upper() for c in args.classes.split(",") if c.strip()]

    audit_near_duplicates(
        train_dir=args.train_dir,
        test_dir=args.test_dir,
        classes=target_classes,
        hamming_thresh=args.hamming,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
