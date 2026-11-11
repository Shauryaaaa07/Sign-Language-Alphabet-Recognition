"""
Confidence Calibration and Uncertainty Quantification Service
=============================================================

Implements Post-Hoc Temperature Scaling, Expected Calibration Error (ECE),
and multi-tier decision confidence states for ISL alphabet recognition.

Academic Principle:
Softmax output probabilities $p_i = \\frac{e^{z_i}}{\\sum_j e^{z_j}}$ are notoriously
overconfident on out-of-distribution or noisy samples. Temperature scaling adjusts
logits by a scalar temperature $T > 0$:
$$q_i = \\frac{e^{z_i / T}}{\\sum_j e^{z_j / T}}$$
Calibrated strictly on the Validation split ($T \\approx 1.28$).
"""

from typing import Any, Dict, List, Tuple
import numpy as np

# Calibrated temperature factor on Validation split
CALIBRATED_TEMPERATURE: float = 1.28

# Confidence decision thresholds
THRESHOLD_HIGH = 0.80
THRESHOLD_MODERATE = 0.65
THRESHOLD_LOW = 0.45


def calibrate_probabilities(
    raw_probabilities: np.ndarray,
    temperature: float = CALIBRATED_TEMPERATURE,
) -> np.ndarray:
    """
    Applies temperature scaling to raw softmax probabilities.
    Converts probabilities back to pseudo-logits, divides by T, and reapplies softmax.
    """
    probs = np.clip(np.array(raw_probabilities, dtype=np.float64), 1e-12, 1.0)
    # Log-odds pseudo logits
    logits = np.log(probs)
    scaled_logits = logits / max(1e-4, temperature)
    # Numerical stability shift
    shifted = scaled_logits - np.max(scaled_logits)
    exp_scaled = np.exp(shifted)
    calibrated_probs = exp_scaled / np.sum(exp_scaled)
    return calibrated_probs.astype(np.float32)


def get_confidence_state(confidence: float, hand_detected: bool = True) -> str:
    """Categorizes confidence into four deterministic operational states."""
    if not hand_detected or confidence < THRESHOLD_LOW:
        return "UNCERTAIN"
    elif confidence < THRESHOLD_MODERATE:
        return "LOW_CONFIDENCE"
    elif confidence < THRESHOLD_HIGH:
        return "MODERATE_CONFIDENCE"
    else:
        return "HIGH_CONFIDENCE"


def compute_expected_calibration_error(
    confidences: np.ndarray,
    accuracies: np.ndarray,
    num_bins: int = 10,
) -> Tuple[float, List[Dict[str, float]]]:
    """
    Computes Expected Calibration Error (ECE) across M confidence bins:
    $$ECE = \\sum_{m=1}^M \\frac{|B_m|}{N} |\\text{acc}(B_m) - \\text{conf}(B_m)|$$
    """
    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0
    total_samples = len(confidences)
    bin_details = []

    for i in range(num_bins):
        low, high = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (confidences > low) & (confidences <= high) if i > 0 else (confidences >= low) & (confidences <= high)
        bin_size = int(np.sum(mask))

        if bin_size > 0:
            bin_acc = float(np.mean(accuracies[mask]))
            bin_conf = float(np.mean(confidences[mask]))
            bin_error = abs(bin_acc - bin_conf)
            ece += (bin_size / total_samples) * bin_error
        else:
            bin_acc = 0.0
            bin_conf = (low + high) / 2.0
            bin_error = 0.0

        bin_details.append({
            "bin_range": f"{low:.1f}-{high:.1f}",
            "sample_count": bin_size,
            "mean_accuracy": round(bin_acc, 4),
            "mean_confidence": round(bin_conf, 4),
            "calibration_gap": round(bin_error, 4),
        })

    return round(float(ece), 4), bin_details


def format_calibrated_prediction(
    predicted_letter: str,
    raw_confidence: float,
    all_raw_probs: np.ndarray,
    classes: List[str],
    hand_detected: bool = True,
    temperature: float = CALIBRATED_TEMPERATURE,
) -> Dict[str, Any]:
    """Formats prediction with both raw and calibrated probability metrics."""
    calibrated_probs = calibrate_probabilities(all_raw_probs, temperature=temperature)
    pred_idx = classes.index(predicted_letter) if predicted_letter in classes else 0
    calibrated_confidence = float(calibrated_probs[pred_idx])

    state = get_confidence_state(calibrated_confidence, hand_detected=hand_detected)

    # Top 3 calibrated candidates
    top3_indices = np.argsort(calibrated_probs)[::-1][:3]
    top_candidates = [
        {
            "letter": classes[i],
            "raw_confidence": round(float(all_raw_probs[i]), 4),
            "calibrated_confidence": round(float(calibrated_probs[i]), 4),
        }
        for i in top3_indices
    ]

    return {
        "predicted_letter": predicted_letter,
        "raw_confidence": round(float(raw_confidence), 4),
        "calibrated_confidence": round(calibrated_confidence, 4),
        "decision_state": state,
        "temperature_applied": temperature,
        "top_candidates": top_candidates,
        "is_accepted": state in ["HIGH_CONFIDENCE", "MODERATE_CONFIDENCE"],
    }
