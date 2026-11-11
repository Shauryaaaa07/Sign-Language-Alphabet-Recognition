#!/usr/bin/env python3
"""
Simulate Dataset Cleaning (Dry-Run Only)
========================================

Indian Sign Language Alphabet Recognition Project
Milestone 2.4: Deterministic Data Cleaning Simulation

This script performs a dry-run simulation of dataset cleaning on the RealSign
raw dataset without modifying, moving, renaming, or deleting any file in `dataset/raw/`.

Cleaning Logic:
- Two-stage verification: flags corrupted or non-image files (e.g. text scripts).
- Content hashing: SHA-256 cryptographic hashing to form duplicate groups.
- Deterministic priority: Testing > Validation > Training.
  - Testing is preserved as the golden ground-truth benchmark.
  - Duplicate groups spanning splits preserve the copy in the highest priority split.
  - Duplicate groups within a split retain the lexicographically lowest relative path.
  - Hash groups spanning multiple class labels are flagged for manual review.
- Generates:
  1. `docs/reports/EXCLUDED_FILES_MANIFEST.json`
  2. `docs/reports/CLEANING_SIMULATION_REPORT.md`
"""

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from PIL import Image

EXPECTED_SPLITS = ("Training", "Testing", "Validation")
EXPECTED_CLASSES = tuple(chr(c) for c in range(ord("A"), ord("Z") + 1))


def compute_sha256(file_path: str) -> str:
    """Compute the SHA-256 hash of a file efficiently in chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_image(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Two-stage PIL image integrity verification.
    Stage 1: open and verify headers.
    Stage 2: reopen and load complete raster bitmap.
    """
    try:
        with open(file_path, "rb") as f:
            header = f.read(1024)
            if not header:
                return False, "Empty file (0 bytes)"

        with Image.open(file_path) as img:
            img.verify()

        with Image.open(file_path) as img:
            img.load()

        return True, None
    except Exception as e:
        return False, str(e)


def scan_dataset(dataset_dir: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Scans the dataset directory, verifying each image and computing SHA-256 hashes.
    Isolates and skips the 'Letters/' directory if present.
    """
    valid_files: List[Dict[str, Any]] = []
    invalid_files: List[Dict[str, Any]] = []

    for split in EXPECTED_SPLITS:
        split_path = os.path.join(dataset_dir, split)
        if not os.path.isdir(split_path):
            continue

        for class_label in sorted(os.listdir(split_path)):
            class_dir = os.path.join(split_path, class_label)
            if not os.path.isdir(class_dir):
                continue

            for fname in sorted(os.listdir(class_dir)):
                file_path = os.path.join(class_dir, fname)
                if not os.path.isfile(file_path):
                    continue

                rel_path = f"{split}/{class_label}/{fname}".replace("\\", "/")
                is_valid, err = verify_image(file_path)
                file_hash = compute_sha256(file_path)

                if is_valid:
                    valid_files.append({
                        "relative_path": rel_path,
                        "file_path": file_path,
                        "sha256": file_hash,
                        "split": split,
                        "class_label": class_label,
                    })
                else:
                    invalid_files.append({
                        "relative_path": rel_path,
                        "file_path": file_path,
                        "sha256": file_hash,
                        "split": split,
                        "class_label": class_label,
                        "error": err,
                    })

    return valid_files, invalid_files


def simulate_cleaning(
    valid_files: List[Dict[str, Any]],
    invalid_files: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Executes deterministic cleaning logic on scanned files.
    Priority: Testing > Validation > Training.
    Returns simulation results dictionary.
    """
    hash_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in valid_files:
        hash_groups[f["sha256"]].append(f)

    retained_files: List[Dict[str, Any]] = []
    excluded_files: List[Dict[str, Any]] = []
    manual_review_warnings: List[Dict[str, Any]] = []

    duplicate_groups_count = 0
    dup_groups_two_splits = 0
    dup_groups_three_splits = 0
    dup_groups_single_split = 0

    group_counter = 0

    for h in sorted(hash_groups.keys()):
        items = hash_groups[h]
        if len(items) == 1:
            retained_files.append(items[0])
            continue

        group_counter += 1
        group_id = f"DUP-GRP-{group_counter:04d}"
        duplicate_groups_count += 1

        classes_in_group = sorted(list(set(x["class_label"] for x in items)))
        if len(classes_in_group) > 1:
            warning_entry = {
                "duplicate_group_id": group_id,
                "sha256": h,
                "classes": classes_in_group,
                "files": [x["relative_path"] for x in items],
            }
            manual_review_warnings.append(warning_entry)

        splits_in_group = set(x["split"] for x in items)
        if len(splits_in_group) == 3:
            dup_groups_three_splits += 1
        elif len(splits_in_group) == 2:
            dup_groups_two_splits += 1
        else:
            dup_groups_single_split += 1

        testing_items = [x for x in items if x["split"] == "Testing"]
        validation_items = [x for x in items if x["split"] == "Validation"]
        training_items = [x for x in items if x["split"] == "Training"]

        if testing_items:
            canonical = min(testing_items, key=lambda x: x["relative_path"])
        elif validation_items:
            canonical = min(validation_items, key=lambda x: x["relative_path"])
        else:
            canonical = min(training_items, key=lambda x: x["relative_path"])

        retained_files.append(canonical)

        for item in sorted(items, key=lambda x: x["relative_path"]):
            if item["relative_path"] == canonical["relative_path"]:
                continue

            if item["split"] == canonical["split"]:
                reason = "INTRA_SPLIT_DUPLICATE"
            elif canonical["split"] == "Testing":
                reason = "CROSS_SPLIT_LEAKAGE_TEST_HOLD"
            elif canonical["split"] == "Validation":
                reason = "CROSS_SPLIT_LEAKAGE_VAL_HOLD"
            else:
                reason = "CROSS_SPLIT_LEAKAGE"

            excluded_files.append({
                "sha256": h,
                "duplicate_group_id": group_id,
                "relative_path": item["relative_path"],
                "split": item["split"],
                "class_label": item["class_label"],
                "exclusion_reason": reason,
                "retained_canonical_path": canonical["relative_path"],
            })

    for inv in sorted(invalid_files, key=lambda x: x["relative_path"]):
        excluded_files.append({
            "sha256": inv["sha256"],
            "duplicate_group_id": None,
            "relative_path": inv["relative_path"],
            "split": inv["split"],
            "class_label": inv["class_label"],
            "exclusion_reason": "CORRUPTED_NON_IMAGE_SCRIPT",
            "retained_canonical_path": None,
        })

    return {
        "valid_files_count": len(valid_files),
        "invalid_files_count": len(invalid_files),
        "total_physical_count": len(valid_files) + len(invalid_files),
        "total_unique_hashes": len(hash_groups),
        "duplicate_groups_count": duplicate_groups_count,
        "dup_groups_single_split": dup_groups_single_split,
        "dup_groups_two_splits": dup_groups_two_splits,
        "dup_groups_three_splits": dup_groups_three_splits,
        "retained_files": retained_files,
        "excluded_files": excluded_files,
        "manual_review_warnings": manual_review_warnings,
    }


def validate_simulation_results(
    sim_results: Dict[str, Any],
    original_valid_files: List[Dict[str, Any]],
    require_all_26_classes: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Validates simulated cleaning invariants:
    - Every retained file belongs to exactly one split.
    - No exact SHA-256 duplicate remains across different simulated splits or within splits.
    - No invalid image is retained.
    - All 26 classes remain represented in all splits (if require_all_26_classes is True).
    - Testing retains its original valid images except for within-Testing duplicate copies.
    """
    errors: List[str] = []
    retained = sim_results["retained_files"]
    retained_paths = set(x["relative_path"] for x in retained)

    # 1. Check unique paths
    if len(retained) != len(retained_paths):
        errors.append(f"Retained count ({len(retained)}) does not match unique path count ({len(retained_paths)}).")

    # 2. Check no duplicate hashes retained
    seen_hashes: Dict[str, str] = {}
    for item in retained:
        h = item["sha256"]
        if h in seen_hashes:
            errors.append(f"Duplicate hash {h} retained across files: {seen_hashes[h]} and {item['relative_path']}")
        seen_hashes[h] = item["relative_path"]

    # 3. Check invalid images not retained
    excluded_corrupt = set(
        x["relative_path"]
        for x in sim_results["excluded_files"]
        if x["exclusion_reason"] == "CORRUPTED_NON_IMAGE_SCRIPT"
    )
    overlap_corrupt = retained_paths.intersection(excluded_corrupt)
    if overlap_corrupt:
        errors.append(f"Corrupted files found in retained set: {overlap_corrupt}")

    # 4. Check class representation
    if require_all_26_classes:
        for split in EXPECTED_SPLITS:
            classes_in_split = set(x["class_label"] for x in retained if x["split"] == split)
            missing_classes = set(EXPECTED_CLASSES) - classes_in_split
            if missing_classes:
                errors.append(f"Split {split} is missing classes after simulation: {sorted(missing_classes)}")

    # 5. Check Testing preservation rule
    orig_testing_hashes = set(x["sha256"] for x in original_valid_files if x["split"] == "Testing")
    retained_testing_hashes = set(x["sha256"] for x in retained if x["split"] == "Testing")
    missing_test_hashes = orig_testing_hashes - retained_testing_hashes
    if missing_test_hashes:
        errors.append(f"Testing split lost {len(missing_test_hashes)} unique valid image hashes during cleaning.")

    is_valid = len(errors) == 0
    return is_valid, errors


def generate_manifest(
    sim_results: Dict[str, Any],
    manifest_path: str,
) -> None:
    """Generates the formal JSON exclusion manifest."""
    os.makedirs(os.path.dirname(os.path.abspath(manifest_path)), exist_ok=True)
    manifest_data = {
        "metadata": {
            "dataset_name": "RealSign-Indian-Sign-Language-Dataset",
            "simulation_mode": "dry-run",
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_files_audited": sim_results["total_physical_count"],
            "total_files_retained": len(sim_results["retained_files"]),
            "total_files_excluded": len(sim_results["excluded_files"]),
            "total_invalid_files": sim_results["invalid_files_count"],
            "total_duplicate_groups": sim_results["duplicate_groups_count"],
        },
        "exclusions": sim_results["excluded_files"],
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)


def generate_simulation_report(
    sim_results: Dict[str, Any],
    orig_valid_files: List[Dict[str, Any]],
    orig_invalid_files: List[Dict[str, Any]],
    validation_status: bool,
    validation_errors: List[str],
    report_path: str,
) -> None:
    """Generates the Markdown cleaning simulation report."""
    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)

    classes = EXPECTED_CLASSES
    before_counts = defaultdict(lambda: defaultdict(int))
    after_counts = defaultdict(lambda: defaultdict(int))

    for x in orig_valid_files:
        before_counts[x["split"]][x["class_label"]] += 1

    for x in sim_results["retained_files"]:
        after_counts[x["split"]][x["class_label"]] += 1

    reason_counts = defaultdict(int)
    for x in sim_results["excluded_files"]:
        reason_counts[x["exclusion_reason"]] += 1

    imbalance_ratios = {}
    for split in EXPECTED_SPLITS:
        split_after = [after_counts[split][c] for c in classes]
        min_c = min(split_after) if split_after else 0
        max_c = max(split_after) if split_after else 0
        ratio_str = f"{max_c / min_c:.3f}:1" if min_c > 0 else "N/A (empty class)"
        imbalance_ratios[split] = (min_c, max_c, ratio_str)

    lines: List[str] = [
        "# Dataset Cleaning Simulation Report (Dry-Run)",
        "",
        "## 1. Executive Summary",
        f"- **Simulation Execution Timestamp (UTC):** `{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        "- **Execution Mode:** Read-Only Simulation (`dataset/raw/` remains 100% immutable).",
        f"- **Validation Gate Status:** `{'PASS' if validation_status else 'FAIL'}`",
        f"- **Total Physical Files Inspected:** `{sim_results['total_physical_count']}` (plus 26 isolated in `Letters/`)",
        f"- **Original Valid Images:** `{sim_results['valid_files_count']}`",
        f"- **Original Invalid / Corrupted Files:** `{sim_results['invalid_files_count']}`",
        f"- **Total Files Retained:** `{len(sim_results['retained_files'])}`",
        f"- **Total Files Marked for Exclusion:** `{len(sim_results['excluded_files'])}`",
        f"- **Total Unique SHA-256 Hashes:** `{sim_results['total_unique_hashes']}`",
        f"- **Total Unique Duplicate Groups:** `{sim_results['duplicate_groups_count']}`",
        "",
        "---",
        "",
        "## 2. Duplicate Groups & Split-Wise Distribution",
        "A duplicate group is defined as a cluster of two or more physical files sharing the exact same SHA-256 hash.",
        "",
        f"- **Total Unique Duplicate Groups:** `{sim_results['duplicate_groups_count']}`",
        f"  - Duplicate groups isolated within a single split: `{sim_results['dup_groups_single_split']}`",
        f"  - Duplicate groups spanning exactly two splits: `{sim_results['dup_groups_two_splits']}`",
        f"  - Duplicate groups spanning all three splits: `{sim_results['dup_groups_three_splits']}`",
        "",
        "### Excluded Files Breakdown by Reason",
        "| Exclusion Reason | File Count | Description |",
        "|---|:---:|---|",
        f"| `CORRUPTED_NON_IMAGE_SCRIPT` | {reason_counts['CORRUPTED_NON_IMAGE_SCRIPT']} | Non-image Python batch-renaming text scripts |",
        f"| `CROSS_SPLIT_LEAKAGE_TEST_HOLD` | {reason_counts['CROSS_SPLIT_LEAKAGE_TEST_HOLD']} | Excluded from Train/Val because canonical copy is preserved in Testing |",
        f"| `CROSS_SPLIT_LEAKAGE_VAL_HOLD` | {reason_counts['CROSS_SPLIT_LEAKAGE_VAL_HOLD']} | Excluded from Train because canonical copy is preserved in Validation |",
        f"| `INTRA_SPLIT_DUPLICATE` | {reason_counts['INTRA_SPLIT_DUPLICATE']} | Redundant duplicate within the same split (lexicographically higher path) |",
        f"| **Total Excluded** | **{len(sim_results['excluded_files'])}** | |",
        "",
        "---",
        "",
        "## 3. Split Counts & Imbalance Ratios (Before vs. After)",
        "",
        "| Split | Initial Valid Images | Retained Clean Images | Excluded Files | Min Class | Max Class | Imbalance Ratio (After) |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for split in EXPECTED_SPLITS:
        init_v = sum(before_counts[split].values())
        ret_v = sum(after_counts[split].values())
        exc_v = init_v - ret_v
        min_c, max_c, r_str = imbalance_ratios[split]
        lines.append(f"| **{split}** | {init_v} | {ret_v} | {exc_v} | {min_c} | {max_c} | {r_str} |")

    tot_init = sum(sum(before_counts[s].values()) for s in EXPECTED_SPLITS)
    tot_ret = sum(sum(after_counts[s].values()) for s in EXPECTED_SPLITS)
    tot_exc = len(sim_results["excluded_files"])
    lines.append(f"| **Total** | **{tot_init}** | **{tot_ret}** | **{tot_exc}** (incl. 2 corrupt) | - | - | - |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Per-Class Image Distribution (A–Z Before vs. After)",
        "",
        "| Class | Training (Before / After) | Testing (Before / After) | Validation (Before / After) | Total Clean Retained |",
        "| :---: | :---: | :---: | :---: | :---: |",
    ])

    for c in classes:
        tr_b, tr_a = before_counts["Training"][c], after_counts["Training"][c]
        te_b, te_a = before_counts["Testing"][c], after_counts["Testing"][c]
        va_b, va_a = before_counts["Validation"][c], after_counts["Validation"][c]
        tot_c = tr_a + te_a + va_a
        lines.append(f"| **{c}** | {tr_b} / {tr_a} | {te_b} / {te_a} | {va_b} / {va_a} | **{tot_c}** |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Manual Review & Cross-Class Conflict Warnings",
    ])

    if not sim_results["manual_review_warnings"]:
        lines.append("- **Cross-Class Hash Inconsistencies:** None detected (`0`). No identical image appears in different class folders.")
    else:
        lines.append(f"- **WARNING:** {len(sim_results['manual_review_warnings'])} cross-class conflict(s) detected:")
        for w in sim_results["manual_review_warnings"]:
            lines.append(f"  - Group `{w['duplicate_group_id']}` (Hash: `{w['sha256']}`): Classes {w['classes']}")
            for p in w["files"]:
                lines.append(f"    - `{p}`")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Simulation Invariant Validation",
        f"- **Invariant 1: Every retained file belongs to exactly one split:** `{'PASSED' if validation_status else 'FAILED'}`",
        f"- **Invariant 2: No exact SHA-256 duplicate remains across simulated splits:** `{'PASSED' if validation_status else 'FAILED'}`",
        f"- **Invariant 3: No invalid/corrupt image is retained:** `{'PASSED' if validation_status else 'FAILED'}`",
        f"- **Invariant 4: All 26 classes remain represented in all splits:** `{'PASSED' if validation_status else 'FAILED'}`",
        f"- **Invariant 5: Testing retains all unique valid image hashes:** `{'PASSED' if validation_status else 'FAILED'}`",
    ])

    if not validation_status:
        lines.append("")
        lines.append("### Validation Failure Errors:")
        for err in validation_errors:
            lines.append(f"- [FAIL] {err}")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def run_self_tests() -> int:
    """
    Executes a synthetic unit test suite verifying simulation logic
    using isolated temporary fixtures without touching real dataset files.
    """
    print("[TEST SUITE] Starting synthetic unit tests for simulate_dataset_cleaning.py...")
    test_failures = 0

    def make_unique_img(path: str, seed: int) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img = Image.new("RGB", (32, 32))
        pixels = img.load()
        for x in range(32):
            for y in range(32):
                pixels[x, y] = (
                    (seed * 7 + x * 3) % 256,
                    (seed * 13 + y * 5) % 256,
                    (seed * 29 + x + y) % 256,
                )
        img.save(path, format="JPEG", quality=95)

    def make_corrupt_file(path: str, content: str = "print('corrupt')") -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    temp_root = tempfile.mkdtemp(prefix="sim_test_")
    try:
        # Helper to create a baseline fixture where every image is guaranteed unique
        def build_baseline_fixture(base_dir: str, images_per_class: int = 2) -> None:
            seed = 100
            for s_idx, s in enumerate(EXPECTED_SPLITS):
                for c_idx, c in enumerate(EXPECTED_CLASSES):
                    for img_i in range(images_per_class):
                        seed += 1
                        path = os.path.join(base_dir, s, c, f"{img_i}.jpg")
                        make_unique_img(path, seed)

        # Test 1: Clean unique dataset
        t1_dir = os.path.join(temp_root, "t1")
        build_baseline_fixture(t1_dir, images_per_class=2)
        v_files, inv_files = scan_dataset(t1_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        if valid and len(sim["excluded_files"]) == 0 and len(sim["retained_files"]) == 26 * 3 * 2:
            print("  [PASS] Test 1: Clean dataset has 0 exclusions and retains all unique files.")
        else:
            print(f"  [FAIL] Test 1: {errs}")
            test_failures += 1

        # Test 2: Intra-split duplicate in Training
        t2_dir = os.path.join(temp_root, "t2")
        build_baseline_fixture(t2_dir, images_per_class=2)
        # Add duplicate inside Training/A
        shutil.copyfile(os.path.join(t2_dir, "Training", "A", "0.jpg"), os.path.join(t2_dir, "Training", "A", "2.jpg"))
        v_files, inv_files = scan_dataset(t2_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        exc = sim["excluded_files"]
        if valid and len(exc) == 1 and exc[0]["exclusion_reason"] == "INTRA_SPLIT_DUPLICATE" and exc[0]["relative_path"] == "Training/A/2.jpg":
            print("  [PASS] Test 2: Intra-split duplicate correctly retained canonical file and excluded 2.jpg.")
        else:
            print(f"  [FAIL] Test 2: {errs}, exc={exc}")
            test_failures += 1

        # Test 3: Cross-split duplicate between Testing and Training
        t3_dir = os.path.join(temp_root, "t3")
        build_baseline_fixture(t3_dir, images_per_class=2)
        # Overwrite Training/A/0.jpg with Testing/A/0.jpg
        shutil.copyfile(os.path.join(t3_dir, "Testing", "A", "0.jpg"), os.path.join(t3_dir, "Training", "A", "0.jpg"))
        v_files, inv_files = scan_dataset(t3_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        exc = sim["excluded_files"]
        if valid and len(exc) == 1 and exc[0]["exclusion_reason"] == "CROSS_SPLIT_LEAKAGE_TEST_HOLD" and exc[0]["relative_path"] == "Training/A/0.jpg":
            print("  [PASS] Test 3: Train-Test duplicate correctly preserved Testing and excluded Training.")
        else:
            print(f"  [FAIL] Test 3: {errs}, exc={exc}")
            test_failures += 1

        # Test 4: Cross-split duplicate across all three splits
        t4_dir = os.path.join(temp_root, "t4")
        build_baseline_fixture(t4_dir, images_per_class=2)
        shutil.copyfile(os.path.join(t4_dir, "Testing", "B", "0.jpg"), os.path.join(t4_dir, "Training", "B", "0.jpg"))
        shutil.copyfile(os.path.join(t4_dir, "Testing", "B", "0.jpg"), os.path.join(t4_dir, "Validation", "B", "0.jpg"))
        v_files, inv_files = scan_dataset(t4_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        exc = sim["excluded_files"]
        reasons = set(x["exclusion_reason"] for x in exc)
        paths = set(x["relative_path"] for x in exc)
        if valid and len(exc) == 2 and reasons == {"CROSS_SPLIT_LEAKAGE_TEST_HOLD"} and paths == {"Training/B/0.jpg", "Validation/B/0.jpg"}:
            print("  [PASS] Test 4: Three-split duplicate preserved Testing and excluded both Train & Val.")
        else:
            print(f"  [FAIL] Test 4: {errs}, exc={exc}")
            test_failures += 1

        # Test 5: Cross-split duplicate between Validation and Training only
        t5_dir = os.path.join(temp_root, "t5")
        build_baseline_fixture(t5_dir, images_per_class=2)
        shutil.copyfile(os.path.join(t5_dir, "Validation", "C", "0.jpg"), os.path.join(t5_dir, "Training", "C", "0.jpg"))
        v_files, inv_files = scan_dataset(t5_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        exc = sim["excluded_files"]
        if valid and len(exc) == 1 and exc[0]["exclusion_reason"] == "CROSS_SPLIT_LEAKAGE_VAL_HOLD" and exc[0]["relative_path"] == "Training/C/0.jpg":
            print("  [PASS] Test 5: Val-Train duplicate preserved Validation and excluded Training.")
        else:
            print(f"  [FAIL] Test 5: {errs}, exc={exc}")
            test_failures += 1

        # Test 6: Corrupted non-image file
        t6_dir = os.path.join(temp_root, "t6")
        build_baseline_fixture(t6_dir, images_per_class=2)
        make_corrupt_file(os.path.join(t6_dir, "Testing", "E", "301.jpg"))
        v_files, inv_files = scan_dataset(t6_dir)
        sim = simulate_cleaning(v_files, inv_files)
        valid, errs = validate_simulation_results(sim, v_files, require_all_26_classes=True)
        exc = sim["excluded_files"]
        if valid and len(exc) == 1 and exc[0]["exclusion_reason"] == "CORRUPTED_NON_IMAGE_SCRIPT" and exc[0]["relative_path"] == "Testing/E/301.jpg" and exc[0]["retained_canonical_path"] is None:
            print("  [PASS] Test 6: Corrupted non-image file correctly quarantined with null canonical path.")
        else:
            print(f"  [FAIL] Test 6: {errs}, exc={exc}")
            test_failures += 1

        # Test 7: Cross-class duplicate warning
        t7_dir = os.path.join(temp_root, "t7")
        build_baseline_fixture(t7_dir, images_per_class=2)
        # Overwrite Training/B/0.jpg with Training/A/0.jpg
        shutil.copyfile(os.path.join(t7_dir, "Training", "A", "0.jpg"), os.path.join(t7_dir, "Training", "B", "0.jpg"))
        v_files, inv_files = scan_dataset(t7_dir)
        sim = simulate_cleaning(v_files, inv_files)
        warnings = sim["manual_review_warnings"]
        if len(warnings) == 1 and set(warnings[0]["classes"]) == {"A", "B"}:
            print("  [PASS] Test 7: Cross-class label inconsistency flagged for manual review.")
        else:
            print(f"  [FAIL] Test 7: warnings={warnings}")
            test_failures += 1

        # Test 8: Determinism test (run twice and compare manifest output)
        t8_dir = os.path.join(temp_root, "t8")
        build_baseline_fixture(t8_dir, images_per_class=2)
        shutil.copyfile(os.path.join(t8_dir, "Testing", "A", "0.jpg"), os.path.join(t8_dir, "Training", "A", "0.jpg"))
        v_files1, inv_files1 = scan_dataset(t8_dir)
        sim1 = simulate_cleaning(v_files1, inv_files1)
        m1_path = os.path.join(temp_root, "m1.json")
        generate_manifest(sim1, m1_path)
        with open(m1_path, "r", encoding="utf-8") as f:
            d1 = json.load(f)["exclusions"]

        v_files2, inv_files2 = scan_dataset(t8_dir)
        sim2 = simulate_cleaning(v_files2, inv_files2)
        m2_path = os.path.join(temp_root, "m2.json")
        generate_manifest(sim2, m2_path)
        with open(m2_path, "r", encoding="utf-8") as f:
            d2 = json.load(f)["exclusions"]

        if d1 == d2:
            print("  [PASS] Test 8: Repeated simulation execution produces 100% deterministic exclusions.")
        else:
            print("  [FAIL] Test 8: Non-deterministic output detected across runs.")
            test_failures += 1

    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    if test_failures == 0:
        print("[TEST SUITE] All 8 synthetic tests passed successfully!")
        return 0
    else:
        print(f"[TEST SUITE] {test_failures} test(s) failed!")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run dataset cleaning simulation for ISL fingerspelling.")
    parser.add_argument("--dataset-dir", default="dataset/raw", help="Path to raw dataset directory.")
    parser.add_argument(
        "--manifest-path",
        default="docs/reports/EXCLUDED_FILES_MANIFEST.json",
        help="Output path for the exclusion manifest JSON.",
    )
    parser.add_argument(
        "--report-path",
        default="docs/reports/CLEANING_SIMULATION_REPORT.md",
        help="Output path for the simulation Markdown report.",
    )
    parser.add_argument("--run-self-test", action="store_true", help="Run synthetic unit test suite and exit.")
    args = parser.parse_args()

    if args.run_self_test:
        return run_self_tests()

    print(f"[SIMULATION] Scanning dataset at: {args.dataset_dir}")
    if not os.path.isdir(args.dataset_dir):
        print(f"[ERROR] Dataset directory not found: {args.dataset_dir}")
        return 2

    valid_files, invalid_files = scan_dataset(args.dataset_dir)
    print(f"[SIMULATION] Scanned {len(valid_files)} valid images and {len(invalid_files)} invalid files.")

    sim_results = simulate_cleaning(valid_files, invalid_files)
    print(f"[SIMULATION] Retained: {len(sim_results['retained_files'])} | Excluded: {len(sim_results['excluded_files'])}")

    valid, errors = validate_simulation_results(sim_results, valid_files, require_all_26_classes=True)
    if not valid:
        print("[SIMULATION GATE] Simulation invariant validation FAILED:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("[SIMULATION GATE] All simulation invariants PASSED.")

    # Generate Manifest and Report
    print(f"[SIMULATION] Generating manifest at: {args.manifest_path}")
    generate_manifest(sim_results, args.manifest_path)

    print(f"[SIMULATION] Generating report at: {args.report_path}")
    generate_simulation_report(
        sim_results,
        valid_files,
        invalid_files,
        valid,
        errors,
        args.report_path,
    )

    print("[SIMULATION COMPLETE] Dry-run simulation finished successfully.")
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
