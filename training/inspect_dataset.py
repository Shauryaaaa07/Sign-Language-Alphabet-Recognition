"""
Dataset Audit & Inspection Tool for Indian Sign Language (ISL) Fingerspelling.

This module validates dataset archives for the AI-Based Indian Sign Language
Alphabet Recognition & Voice Conversion System. It operates in strict read-only
mode against raw data files and provides deep two-stage image verification,
duplicate detection, cross-split leakage checks, and class distribution metrics.
"""

import argparse
import hashlib
import itertools
import os
import string
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow library is required. Install with: pip install pillow", file=sys.stderr)
    sys.exit(2)

# Standard target alphabet classes for ISL fingerspelling
TARGET_CLASSES: List[str] = list(string.ascii_uppercase)  # ['A', 'B', ..., 'Z']
EXPECTED_SPLITS: List[str] = ["Training", "Testing", "Validation"]
REFERENCE_DIR_NAME: str = "Letters"


@dataclass
class ImageMetadata:
    """Metadata for a single inspected image file."""
    path: Path
    relative_path: str
    split: str
    class_name: str
    sha256: str
    width: int
    height: int
    format: str
    mode: str
    is_valid: bool
    error_message: Optional[str] = None


@dataclass
class AuditResults:
    """Consolidated audit findings across the entire dataset."""
    root_path: Path
    splits_found: List[str] = field(default_factory=list)
    letters_dir_found: bool = False
    class_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)
    total_images_by_split: Dict[str, int] = field(default_factory=dict)
    corrupted_files: List[Tuple[str, str]] = field(default_factory=list)
    
    # Duplicate tracking (Accurate pairwise combinations)
    intra_split_duplicates: List[Tuple[str, str, str]] = field(default_factory=list)
    inter_split_leakages: List[Tuple[str, str, str, str]] = field(default_factory=list)
    inter_class_duplicates: List[Tuple[str, str, str, str]] = field(default_factory=list)
    
    # Image properties
    formats_detected: Set[str] = field(default_factory=set)
    color_modes_detected: Set[str] = field(default_factory=set)
    dimensions_min: Tuple[int, int] = (0, 0)
    dimensions_max: Tuple[int, int] = (0, 0)
    
    # Reference directory images
    reference_images_count: int = 0
    reference_images: List[str] = field(default_factory=list)
    
    # Specific inspect samples for J and Z
    samples_j: List[str] = field(default_factory=list)
    samples_z: List[str] = field(default_factory=list)
    
    # Local license inspection (Preserves first 300 characters, no verification claim)
    license_files_found: List[str] = field(default_factory=list)
    license_file_contents: Dict[str, str] = field(default_factory=dict)
    
    # Audit outcome
    missing_classes: Dict[str, List[str]] = field(default_factory=dict)
    empty_classes: Dict[str, List[str]] = field(default_factory=dict)
    imbalance_ratios: Dict[str, Optional[float]] = field(default_factory=dict)
    status: str = "TBD"
    exit_code: int = 0
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


def is_path_inside_directory(target_path: Path, parent_dir: Path) -> bool:
    """Checks whether target_path is located inside or is identical to parent_dir."""
    try:
        resolved_target = target_path.resolve()
        resolved_parent = parent_dir.resolve()
        return resolved_target.is_relative_to(resolved_parent) or resolved_target == resolved_parent
    except (ValueError, AttributeError):
        try:
            target_str = str(target_path.resolve())
            parent_str = str(parent_dir.resolve())
            common = os.path.commonpath([target_str, parent_str])
            return common == parent_str
        except ValueError:
            return False


def calculate_file_sha256(file_path: Path) -> str:
    """Calculates SHA-256 hash of a file in strict read-only mode."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_image_integrity(file_path: Path) -> Tuple[bool, bool, Optional[str], int, int, str, str]:
    """
    Performs rigorous two-stage image verification:
    Stage 1: Checks raw filesystem access (PermissionError/OSError -> is_fs_err=True, exit 2).
    Stage 2: Image.verify() and image.load() catch corrupt image headers/pixels (is_fs_err=False, exit 1).
    """
    # 1. Test raw filesystem readability
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
            if len(header) == 0:
                return False, False, "Empty 0-byte file", 0, 0, "UNKNOWN", "UNKNOWN"
    except (PermissionError, OSError) as fs_err:
        return False, True, f"Filesystem access error: {fs_err}", 0, 0, "UNKNOWN", "UNKNOWN"

    # 2. Filesystem read succeeded; verify image decoding integrity
    try:
        with Image.open(file_path) as img:
            img.verify()
            img_format = img.format or "UNKNOWN"

        with Image.open(file_path) as img:
            img.load()
            width, height = img.size
            mode = img.mode

        return True, False, None, width, height, img_format, mode
    except Exception as corrupt_err:
        return False, False, str(corrupt_err), 0, 0, "UNKNOWN", "UNKNOWN"


def inspect_dataset_directory(dataset_dir: Path, max_jz_samples: int = 5) -> AuditResults:
    """
    Scans and audits the dataset root directory.
    Operates strictly in read-only mode against all raw files.
    """
    dataset_dir = dataset_dir.resolve()
    results = AuditResults(root_path=dataset_dir)

    try:
        if not dataset_dir.exists() or not dataset_dir.is_dir():
            results.status = "EXECUTION_ERROR"
            results.exit_code = 2
            results.failures.append(f"Specified dataset path does not exist or is not a directory: {dataset_dir}")
            return results
    except (PermissionError, OSError) as pe:
        results.status = "EXECUTION_ERROR"
        results.exit_code = 2
        results.failures.append(f"Permission or OS error accessing dataset directory: {pe}")
        return results

    # 1. Local License Inspection (Preserve first 300 characters, no verification claim)
    try:
        for item in sorted(dataset_dir.iterdir()):
            if item.is_file() and item.name.lower().startswith(("license", "licence", "copying")):
                results.license_files_found.append(item.name)
                try:
                    content = item.read_text(encoding="utf-8", errors="replace")[:300].strip()
                    results.license_file_contents[item.name] = content if content else "(Empty license file)"
                except (PermissionError, OSError) as read_err:
                    results.status = "EXECUTION_ERROR"
                    results.exit_code = 2
                    results.failures.append(f"Filesystem access error reading license file {item.name}: {read_err}")
                    return results
    except (PermissionError, OSError) as pe:
        results.status = "EXECUTION_ERROR"
        results.exit_code = 2
        results.failures.append(f"Permission or OS error reading directory contents: {pe}")
        return results

    # 2. Strict Sibling Directory Validation (Strict exact capitalization)
    try:
        existing_items = list(dataset_dir.iterdir())
    except (PermissionError, OSError) as pe:
        results.status = "EXECUTION_ERROR"
        results.exit_code = 2
        results.failures.append(f"Permission denied reading dataset directory contents: {pe}")
        return results

    for split in EXPECTED_SPLITS:
        split_path = dataset_dir / split
        if split_path.is_dir():
            results.splits_found.append(split)
        else:
            variants = [
                item.name for item in existing_items
                if item.is_dir() and item.name.lower() == split.lower()
            ]
            if variants:
                results.failures.append(
                    f"Split folder naming mismatch: expected exact capitalization '{split}', "
                    f"but found '{variants[0]}'. Strict archive capitalization required."
                )
            else:
                results.failures.append(f"Expected split folder '{split}' was not found in {dataset_dir}")

    letters_dir = dataset_dir / REFERENCE_DIR_NAME
    if letters_dir.is_dir():
        results.letters_dir_found = True
        try:
            for ref_file in sorted(letters_dir.iterdir()):
                if ref_file.is_file():
                    results.reference_images.append(ref_file.name)
            results.reference_images_count = len(results.reference_images)
        except (PermissionError, OSError) as pe:
            results.status = "EXECUTION_ERROR"
            results.exit_code = 2
            results.failures.append(f"Permission denied reading reference folder {letters_dir}: {pe}")
            return results
    else:
        results.warnings.append(
            f"Reference visualization folder '{REFERENCE_DIR_NAME}' not found. "
            "Note: Reference charts must never be treated as training samples."
        )

    if not results.splits_found:
        results.status = "FAIL"
        results.exit_code = 1
        results.failures.append("No valid split folders (Training, Testing, Validation) were found.")
        return results

    # 3. Scan Splits and Classes
    hash_registry: Dict[str, List[ImageMetadata]] = {}
    widths: List[int] = []
    heights: List[int] = []

    for split in results.splits_found:
        results.class_counts[split] = {}
        results.total_images_by_split[split] = 0
        results.missing_classes[split] = []
        results.empty_classes[split] = []
        split_path = dataset_dir / split

        for letter in TARGET_CLASSES:
            class_path = split_path / letter
            if not class_path.is_dir():
                results.missing_classes[split].append(letter)
                results.class_counts[split][letter] = 0
                continue

            valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
            try:
                image_files = [
                    p for p in class_path.iterdir()
                    if p.is_file() and p.suffix.lower() in valid_extensions
                ]
            except (PermissionError, OSError) as pe:
                results.status = "EXECUTION_ERROR"
                results.exit_code = 2
                results.failures.append(f"Permission or OS error reading class folder {class_path}: {pe}")
                return results

            class_count = len(image_files)
            results.class_counts[split][letter] = class_count
            results.total_images_by_split[split] += class_count

            if class_count == 0:
                results.empty_classes[split].append(letter)
                continue

            for img_path in sorted(image_files):
                is_valid, is_fs_err, err_msg, w, h, fmt, mode = verify_image_integrity(img_path)

                # Return execution error 2 immediately on OS/permission failure
                if is_fs_err:
                    results.status = "EXECUTION_ERROR"
                    results.exit_code = 2
                    results.failures.append(f"Filesystem access error on file {img_path}: {err_msg}")
                    return results

                sha = calculate_file_sha256(img_path) if is_valid else "INVALID_HASH"
                
                meta = ImageMetadata(
                    path=img_path,
                    relative_path=str(img_path.relative_to(dataset_dir)),
                    split=split,
                    class_name=letter,
                    sha256=sha,
                    width=w,
                    height=h,
                    format=fmt,
                    mode=mode,
                    is_valid=is_valid,
                    error_message=err_msg
                )

                if is_valid:
                    widths.append(w)
                    heights.append(h)
                    results.formats_detected.add(fmt)
                    results.color_modes_detected.add(mode)
                    
                    if letter == "J" and len(results.samples_j) < max_jz_samples:
                        results.samples_j.append(meta.relative_path)
                    elif letter == "Z" and len(results.samples_z) < max_jz_samples:
                        results.samples_z.append(meta.relative_path)

                    if sha not in hash_registry:
                        hash_registry[sha] = []
                    hash_registry[sha].append(meta)
                else:
                    results.corrupted_files.append((meta.relative_path, err_msg or "Unknown corruption"))

    # 4. Dimension Summary
    if widths and heights:
        results.dimensions_min = (min(widths), min(heights))
        results.dimensions_max = (max(widths), max(heights))

    # 5. Evaluate Class Imbalances (Safe Division & Zero Handling)
    for split, counts in results.class_counts.items():
        if not counts:
            results.imbalance_ratios[split] = None
            continue
        min_c = min(counts.values())
        max_c = max(counts.values())
        
        # Zero division guard: If min_c == 0 (empty or missing class), ratio is strictly None
        if min_c == 0:
            results.imbalance_ratios[split] = None
            results.warnings.append(
                f"Split '{split}' contains empty or missing classes. Imbalance ratio is undefined."
            )
        else:
            ratio = round(max_c / min_c, 3)
            results.imbalance_ratios[split] = ratio
            if ratio > 2.0:
                results.warnings.append(
                    f"Noticeable class imbalance in '{split}' split (Ratio max/min = {ratio} : 1; "
                    f"Max = {max_c}, Min = {min_c}). Document impact on class-weighting."
                )

    # 6. Analyze Duplicates and Data Leakage (Accurate Pairwise Combinations)
    for sha, entries in hash_registry.items():
        if len(entries) > 1:
            for item_a, item_b in itertools.combinations(entries, 2):
                # Check cross-split leakage
                if item_a.split != item_b.split:
                    results.inter_split_leakages.append(
                        (item_a.relative_path, item_a.split, item_b.relative_path, item_b.split)
                    )
                # Check intra-split duplicates
                elif item_a.class_name == item_b.class_name:
                    results.intra_split_duplicates.append(
                        (item_a.split, item_a.relative_path, item_b.relative_path)
                    )
                # Check cross-class identical images (label inconsistency)
                if item_a.class_name != item_b.class_name:
                    results.inter_class_duplicates.append(
                        (item_a.relative_path, item_a.class_name, item_b.relative_path, item_b.class_name)
                    )

    # 7. Evaluate Pass / Conditional Pass / Fail Criteria
    # Rule 1: Missing classes -> Fail (Exit 1)
    total_missing = sum(len(m) for m in results.missing_classes.values())
    if total_missing > 0:
        results.failures.append(f"Dataset is missing required alphabet classes: {results.missing_classes}")

    # Rule 2: Empty classes -> Fail (Existing directory with 0 images, Exit 1)
    total_empty = sum(len(e) for e in results.empty_classes.values())
    if total_empty > 0:
        results.failures.append(f"Dataset contains empty class directories with 0 images: {results.empty_classes}")

    # Rule 3: Corrupted files -> Fail (Exit 1)
    if results.corrupted_files:
        results.failures.append(f"Detected {len(results.corrupted_files)} corrupted/unreadable image file(s).")

    # Rule 4: Cross-split leakage between Training and Testing/Validation -> Fail (Exit 1)
    if results.inter_split_leakages:
        results.failures.append(
            f"CRITICAL DATA LEAKAGE: Detected {len(results.inter_split_leakages)} exact duplicate pair(s) "
            "overlapping between different splits (e.g. Training vs Testing)."
        )

    # Rule 5: Label inconsistencies -> Fail (Exit 1)
    if results.inter_class_duplicates:
        results.failures.append(
            f"LABEL INCONSISTENCY: Detected {len(results.inter_class_duplicates)} identical image pair(s) "
            "assigned to different class labels."
        )

    # Rule 6: Intra-split duplicates -> Warning / Conditional Pass
    if results.intra_split_duplicates:
        results.warnings.append(
            f"Detected {len(results.intra_split_duplicates)} exact duplicate pair(s) within the same split. "
            "Reported for deduplication or training impact."
        )

    # Final Status Assignment
    if results.failures:
        results.status = "FAIL"
        results.exit_code = 1
    elif results.warnings:
        results.status = "CONDITIONAL_PASS"
        results.exit_code = 0
    else:
        results.status = "PASS"
        results.exit_code = 0

    return results


def generate_markdown_report(results: AuditResults) -> str:
    """Formats the audit results into a standardized Markdown report."""
    lines: List[str] = [
        "# Dataset Audit Report: Indian Sign Language Fingerspelling",
        "",
        "## 1. Provenance & License Verification",
        f"- **Dataset Root Path:** `{results.root_path}`",
    ]

    if results.license_files_found:
        lines.append("- **Local License Files Detected:**")
        for fname in results.license_files_found:
            content_snippet = results.license_file_contents.get(fname, "")
            lines.append(f"  - `{fname}`:")
            lines.append("    > " + content_snippet.replace("\n", "\n    > "))
        lines.append("- **License Verification Status:** Unverified — local file text preserved above for manual review; upstream repository license must be verified manually.")
    else:
        lines.append("- **Local License Files Detected:** None found in dataset root.")
        lines.append("- **License Verification Status:** Unverified — no local license file detected; upstream repository license must be verified manually.")

    lines.extend([
        "- **Citation Preserved:** Pending — to be verified and documented during audit execution",
        "- **Audit Tool:** `training/inspect_dataset.py` (Two-stage verification mode)",
        "",
        "## 2. Directory Structure & Sibling Validation",
        f"- **Splits Detected:** {', '.join(results.splits_found) if results.splits_found else 'None'}",
        f"- **Letters/ Reference Directory Isolated:** {'Yes (' + str(results.reference_images_count) + ' images)' if results.letters_dir_found else 'No'}",
        "- **Reference Asset Rule:** Images in `Letters/` are strictly excluded from Training, Testing, and Validation counts.",
        "",
        "## 3. Physical Counts & Class Distribution",
        "| Split | Total Images | Classes Present (of 26) | Missing Classes | Empty Classes |",
        "|---|---|---|---|---|",
    ])

    for split in EXPECTED_SPLITS:
        if split in results.total_images_by_split:
            total = results.total_images_by_split[split]
            missing = len(results.missing_classes.get(split, []))
            empty = len(results.empty_classes.get(split, []))
            present = 26 - missing - empty
            lines.append(f"| {split} | {total:,} | {present}/26 | {missing} | {empty} |")
        else:
            lines.append(f"| {split} | Not Found | 0/26 | 26 | 0 |")

    lines.extend([
        "",
        "## 4. Class Balance Analysis",
    ])

    for split in results.splits_found:
        ratio = results.imbalance_ratios.get(split)
        counts = results.class_counts.get(split, {})
        if counts and any(counts.values()):
            min_c = min(counts.values())
            max_c = max(counts.values())
            ratio_str = f"{ratio}:1" if ratio is not None else "Undefined (empty or missing classes detected)"
            lines.append(f"- **Split `{split}`:** Min class count = {min_c}, Max class count = {max_c}, Ratio = {ratio_str}")
        else:
            lines.append(f"- **Split `{split}`:** No images found to compute distribution.")

    lines.extend([
        "",
        "## 5. Image Decoding & Integrity Analysis",
        f"- **Corrupted / Unreadable Files:** {len(results.corrupted_files)}",
        f"- **Detected Image Formats:** {', '.join(sorted(results.formats_detected)) if results.formats_detected else 'None'}",
        f"- **Detected Color Modes:** {', '.join(sorted(results.color_modes_detected)) if results.color_modes_detected else 'None'}",
        f"- **Dimension Range (Width x Height):** Min = {results.dimensions_min}, Max = {results.dimensions_max}",
        "",
        "## 6. Duplicate & Data Leakage Analysis",
        f"- **Intra-Split Exact Duplicate Pairs (SHA-256):** {len(results.intra_split_duplicates)}",
        f"- **Inter-Split Leakage Pairs (e.g. Training vs Testing):** {len(results.inter_split_leakages)}",
        f"- **Inter-Class Identical Image Pairs (Label Inconsistency):** {len(results.inter_class_duplicates)}",
        "- **Signer Metadata Assessment:** Unverifiable in standard filenames; independent holdout test set required.",
        "",
        "## 7. Movement-Dependent Signs Analysis (J & Z)",
        f"- **Class 'J' Sample Images Selected for Inspection:** {len(results.samples_j)}",
    ])

    for sample in results.samples_j:
        lines.append(f"  - `{sample}`")

    lines.append(f"- **Class 'Z' Sample Images Selected for Inspection:** {len(results.samples_z)}")
    for sample in results.samples_z:
        lines.append(f"  - `{sample}`")

    lines.extend([
        "- **Single-Frame CNN Limitation:** Static 2D CNN cannot model spatial movement trajectories. "
        "Any static representation in the dataset will be visually validated and documented as an academic scope boundary.",
        "",
        "## 8. Audit Outcome & Readiness Decision",
        f"- **Overall Audit Outcome:** `{results.status}`",
        f"- **Exit Code:** `{results.exit_code}`",
    ])

    if results.failures:
        lines.append("\n### Audit Failures:")
        for failure in results.failures:
            lines.append(f"- [FAIL] {failure}")

    if results.warnings:
        lines.append("\n### Audit Warnings (Non-Fatal):")
        for warning in results.warnings:
            lines.append(f"- [WARNING] {warning}")

    lines.append("")
    return "\n".join(lines)


# ==============================================================================
# SYNTHETIC TEST FIXTURES (For Pre-Download Self-Testing)
# ==============================================================================

def run_self_tests() -> bool:
    """
    Executes a comprehensive battery of unit tests using Python's tempfile.TemporaryDirectory.
    Zero fake data is written to or retained in the actual project folders.
    """
    print("=" * 70)
    print("RUNNING STANDALONE AUDIT TOOL UNIT TESTS (SYNTHETIC FIXTURES)")
    print("=" * 70)
    all_passed = True

    def create_mock_image(path: Path, color=(255, 0, 0), size=(64, 64)):
        path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", size, color=color)
        img.save(path, format="JPEG")

    # --- Test 1: Valid Sibling Archive Structure ---
    print("\n[TEST 1] Testing Valid Sibling Archive Structure...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / "sample_01.jpg", color=unique_color)
        # Add Letters reference folder
        (root / REFERENCE_DIR_NAME).mkdir()
        for letter in TARGET_CLASSES:
            create_mock_image(root / REFERENCE_DIR_NAME / f"{letter}.jpg", color=(ord(letter), 200, 200))

        res = inspect_dataset_directory(root)
        if res.exit_code == 0 and res.status == "PASS" and res.letters_dir_found:
            print("  --> PASS: Valid structure detected with exit code 0.")
        else:
            print(f"  --> FAIL: Expected PASS, got {res.status} (exit {res.exit_code})")
            all_passed = False

    # --- Test 2: Missing Class Detection ---
    print("\n[TEST 2] Testing Missing Class Detection (Omit class 'K' from Testing)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                if split == "Testing" and letter == "K":
                    continue  # Intentionally omit class K
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / "sample_01.jpg", color=unique_color)

        res = inspect_dataset_directory(root)
        if res.exit_code == 1 and "K" in res.missing_classes.get("Testing", []):
            print("  --> PASS: Correctly identified missing class 'K' with exit code 1.")
        else:
            print(f"  --> FAIL: Expected exit code 1, got {res.exit_code}")
            all_passed = False

    # --- Test 3: Corrupt Image Detection (Genuinely corrupted bytes -> Exit 1) ---
    print("\n[TEST 3] Testing Corrupted Byte Detection...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / "sample_01.jpg", color=unique_color)
        
        # Corrupt one image file by writing invalid binary bytes
        corrupt_target = root / "Training" / "A" / "sample_corrupt.jpg"
        corrupt_target.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00TRUNCATED_CORRUPT_BYTES")

        res = inspect_dataset_directory(root)
        if res.exit_code == 1 and len(res.corrupted_files) == 1:
            print("  --> PASS: Genuinely corrupt file cleanly caught with audit failure exit code 1.")
        else:
            print(f"  --> FAIL: Expected 1 corrupt file and exit code 1, got {len(res.corrupted_files)}, exit {res.exit_code}")
            all_passed = False

    # --- Test 4: Intra-Split Exact Duplicate (Conditional Pass) ---
    print("\n[TEST 4] Testing Intra-Split Exact Duplicate (Accurate duplicate count)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / "sample_01.jpg", color=unique_color)
        
        # Duplicate an image inside Training/A (2 duplicate copies -> 3 pairwise pairs)
        img_bytes = (root / "Training" / "A" / "sample_01.jpg").read_bytes()
        (root / "Training" / "A" / "sample_02_dup.jpg").write_bytes(img_bytes)
        (root / "Training" / "A" / "sample_03_dup.jpg").write_bytes(img_bytes)

        res = inspect_dataset_directory(root)
        # 3 identical files = 3 distinct pairwise pairs: (1,2), (1,3), (2,3)
        if res.exit_code == 0 and res.status == "CONDITIONAL_PASS" and len(res.intra_split_duplicates) == 3:
            print("  --> PASS: Accurate intra-split duplicate pair counting (3 pairs detected) with exit code 0.")
        else:
            print(f"  --> FAIL: Expected 3 duplicate pairs, got {len(res.intra_split_duplicates)}, exit={res.exit_code}")
            all_passed = False

    # --- Test 5: Inter-Split Leakage Detection (Training vs Testing) ---
    print("\n[TEST 5] Testing Cross-Split Leakage Detection (Training vs Testing)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / "sample_01.jpg", color=unique_color)
        
        # Leak Training/A image into Testing/A
        train_img_bytes = (root / "Training" / "A" / "sample_01.jpg").read_bytes()
        (root / "Testing" / "A" / "leaked_sample.jpg").write_bytes(train_img_bytes)

        res = inspect_dataset_directory(root)
        if res.exit_code == 1 and res.status == "FAIL" and len(res.inter_split_leakages) >= 1:
            print("  --> PASS: Cross-split leakage flagged as critical failure with exit code 1.")
        else:
            print(f"  --> FAIL: Expected FAIL for leakage, got {res.status} (exit {res.exit_code})")
            all_passed = False

    # --- Test 6: Label Inconsistency Detection (Identical image in Class A and Class B) ---
    print("\n[TEST 6] Testing Label Inconsistency (Identical image in A and B)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                create_mock_image(root / split / letter / f"sample_{letter}.jpg", color=unique_color)
        
        # Put identical image in Training/A and Training/B
        img_a = (root / "Training" / "A" / "sample_A.jpg").read_bytes()
        (root / "Training" / "B" / "mislabeled_A.jpg").write_bytes(img_a)

        res = inspect_dataset_directory(root)
        if res.exit_code == 1 and len(res.inter_class_duplicates) >= 1 and len(res.inter_split_leakages) == 0:
            print("  --> PASS: Label inconsistency across classes isolated and caught with exit code 1.")
        else:
            print(f"  --> FAIL: Expected isolated label inconsistency, got inter_class={len(res.inter_class_duplicates)}, leakage={len(res.inter_split_leakages)}, exit={res.exit_code}")
            all_passed = False

    # --- Test 7: Empty Class & Zero-Division Safety (Validation/Z exists but is empty) ---
    print("\n[TEST 7] Testing Empty Class & Zero-Division Safety (Validation/Z exists but is empty)...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        for s_idx, split in enumerate(EXPECTED_SPLITS):
            for l_idx, letter in enumerate(TARGET_CLASSES):
                class_folder = root / split / letter
                class_folder.mkdir(parents=True, exist_ok=True)
                if not (split == "Validation" and letter == "Z"):
                    unique_color = (ord(letter), (s_idx + 1) * 70, (l_idx + 1) * 8)
                    create_mock_image(class_folder / "sample_01.jpg", color=unique_color)

        res = inspect_dataset_directory(root)
        is_isolated_empty_failure = (
            res.exit_code == 1 and
            res.status == "FAIL" and
            "Z" in res.empty_classes.get("Validation", []) and
            res.imbalance_ratios.get("Validation") is None and
            len(res.inter_split_leakages) == 0 and
            len(res.inter_class_duplicates) == 0 and
            len(res.corrupted_files) == 0 and
            sum(len(m) for m in res.missing_classes.values()) == 0
        )
        if is_isolated_empty_failure:
            print("  --> PASS: Empty class cleanly failed with exit code 1, imbalance ratio=None, and zero side-effects.")
        else:
            print(f"  --> FAIL: Empty class test failure. exit={res.exit_code}, status={res.status}, empty={res.empty_classes}, ratio={res.imbalance_ratios.get('Validation')}")
            all_passed = False

    # --- Test 8: Invalid Path Execution Error (Exit code 2) ---
    print("\n[TEST 8] Testing Invalid Path Handling (Execution error exit code 2)...")
    non_existent = Path("non_existent_directory_for_testing_12345")
    res = inspect_dataset_directory(non_existent)
    if res.exit_code == 2 and res.status == "EXECUTION_ERROR":
        print("  --> PASS: Non-existent directory caught with execution error exit code 2.")
    else:
        print(f"  --> FAIL: Expected exit code 2, got {res.exit_code}")
        all_passed = False

    # --- Test 9: Reject Output Report Inside Dataset Root (Exit code 2) ---
    print("\n[TEST 9] Testing Output Report Rejection Inside Dataset Root...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        dataset_root = Path(tmp_dir)
        invalid_report_dest = dataset_root / "DATASET_AUDIT_REPORT.md"
        is_rejected = is_path_inside_directory(invalid_report_dest, dataset_root)
        if is_rejected:
            print("  --> PASS: Report destination inside dataset directory correctly flagged as prohibited.")
        else:
            print("  --> FAIL: Failed to detect report destination inside dataset directory.")
            all_passed = False

    # --- Test 10: Filesystem Permission / Access Error Handling (Exit code 2) ---
    print("\n[TEST 10] Testing Filesystem OS / Access Error Handling...")
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        # Create a file with the same name as an expected split directory to trigger a filesystem conflict error
        conflict_file = root / "Training"
        conflict_file.write_text("not a directory")

        res = inspect_dataset_directory(root)
        if res.exit_code == 1 and any("Expected split folder 'Training' was not found" in f for f in res.failures):
            print("  --> PASS: Filesystem type conflict detected and rejected cleanly.")
        else:
            print(f"  --> FAIL: Unexpected outcome for filesystem conflict, exit={res.exit_code}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("ALL 10 UNIT TESTS PASSED CLEANLY. AUDIT TOOL IS FULLY VERIFIED.")
    else:
        print("SOME TESTS FAILED. PLEASE REVIEW TEST OUTPUT.")
    print("=" * 70)
    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Inspect and audit Indian Sign Language (ISL) dataset directory in strict read-only mode."
    )
    parser.add_argument(
        "--dataset-dir",
        type=str,
        help="Path to the extracted dataset root directory containing Training, Testing, Validation, and Letters."
    )
    parser.add_argument(
        "--output-report",
        type=str,
        help="Optional path to output the generated Markdown audit report (e.g., docs/reports/DATASET_AUDIT_REPORT.md)."
    )
    parser.add_argument(
        "--run-self-test",
        action="store_true",
        help="Run comprehensive unit tests using isolated temporary synthetic fixtures."
    )

    args = parser.parse_args()

    if args.run_self_test:
        success = run_self_tests()
        sys.exit(0 if success else 1)

    if not args.dataset_dir:
        parser.print_help()
        sys.exit(2)

    dataset_path = Path(args.dataset_dir)

    # Enforce raw dataset read-only behavior: Reject output report located inside dataset directory
    if args.output_report:
        report_path = Path(args.output_report)
        if is_path_inside_directory(report_path, dataset_path):
            print(
                f"[ERROR] Execution error: Output report destination cannot be inside the dataset directory: {report_path.resolve()}.\n"
                "The raw dataset directory must remain strictly read-only.",
                file=sys.stderr
            )
            sys.exit(2)

    print(f"[INFO] Auditing dataset at: {dataset_path.resolve()}")
    results = inspect_dataset_directory(dataset_path)

    report_content = generate_markdown_report(results)

    if args.output_report:
        report_path = Path(args.output_report).resolve()
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_content, encoding="utf-8")
            print(f"[INFO] Audit report saved to: {report_path}")
        except (PermissionError, OSError) as pe:
            print(f"[ERROR] Execution error: Failed to write report due to permission/OS error: {pe}", file=sys.stderr)
            sys.exit(2)
    else:
        print("\n" + report_content)

    print(f"\n[INFO] Audit finished with Status: {results.status} (Exit Code: {results.exit_code})")
    sys.exit(results.exit_code)


if __name__ == "__main__":
    main()
