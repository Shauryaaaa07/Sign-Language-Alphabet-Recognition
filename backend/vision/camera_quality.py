"""
Camera Quality and Real-Time Framing Analysis Module
====================================================

Evaluates environmental and optical capture conditions:
1. Mean illumination / brightness
2. Standard deviation contrast
3. Laplacian variance blur estimation
4. MediaPipe hand bounding box scale & centration
5. Actionable user advisory messages
"""

import io
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from backend.vision.hand_landmarker import HandLandmarkDetector

# Quality thresholds
MIN_BRIGHTNESS = 45.0      # Below this: dim / underexposed
MAX_BRIGHTNESS = 215.0     # Above this: overexposed / window glare
MIN_CONTRAST = 24.0        # Below this: low dynamic range / washed out
MIN_LAPLACIAN_VAR = 65.0   # Below this: motion blur or out of focus
MIN_HAND_AREA_PCT = 0.07   # Hand takes up less than 7% of frame -> too small
MAX_HAND_AREA_PCT = 0.85   # Hand takes up more than 85% of frame -> too close


class CameraQualityAnalyzer:
    """Evaluates frame optical quality and hand spatial positioning."""

    def __init__(self):
        self.detector = HandLandmarkDetector.get_instance()

    def analyze_frame(
        self,
        image_input: Union[bytes, np.ndarray, Image.Image],
    ) -> Dict[str, Any]:
        """Performs full image quality and hand framing audit."""
        # 1. Parse Image to BGR / Grayscale
        if isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img_bgr is None:
                return self._error_response("Failed to decode image bytes")
        elif isinstance(image_input, np.ndarray):
            if len(image_input.shape) == 3:
                img_bgr = cv2.cvtColor(image_input, cv2.COLOR_RGB2BGR) if image_input.shape[2] == 3 else image_input
            else:
                img_bgr = cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
        elif isinstance(image_input, Image.Image):
            img_bgr = cv2.cvtColor(np.array(image_input), cv2.COLOR_RGB2BGR)
        else:
            return self._error_response("Unsupported image input type")

        height, width = img_bgr.shape[:2]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 2. Photometric Metrics
        mean_brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        # 3. Blur Metric: Variance of the Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = float(laplacian.var())
        is_blurry = blur_score < MIN_LAPLACIAN_VAR

        # 4. Hand Detection & Spatial Framing
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        det_res = self.detector.process_image(img_rgb)

        hand_detected = det_res["status"] == "hand_detected"
        primary_hand = det_res.get("primary_hand")

        hand_area_pct = 0.0
        is_hand_centered = False
        hand_too_small = False
        hand_too_large = False

        if hand_detected and primary_hand:
            bbox = primary_hand["bounding_box_normalized"]
            hand_area_pct = float(bbox["width"] * bbox["height"])
            cx = (bbox["min_x"] + bbox["max_x"]) / 2.0
            cy = (bbox["min_y"] + bbox["max_y"]) / 2.0
            # Centered if within middle 60% of viewport
            is_hand_centered = (0.20 <= cx <= 0.80) and (0.15 <= cy <= 0.85)
            hand_too_small = hand_area_pct < MIN_HAND_AREA_PCT
            hand_too_large = hand_area_pct > MAX_HAND_AREA_PCT

        # 5. Diagnostic Advisory Generation
        advisories: List[str] = []
        status = "good"

        if mean_brightness < MIN_BRIGHTNESS:
            advisories.append("Lighting is too low (room is dim)")
            status = "suboptimal"
        elif mean_brightness > MAX_BRIGHTNESS:
            advisories.append("Image is too bright (reduce glare or backlight)")
            status = "suboptimal"

        if contrast < MIN_CONTRAST:
            advisories.append("Low contrast (poor distinction between hand and background)")
            status = "suboptimal"

        if is_blurry:
            advisories.append("Camera image is blurry (hold hand still or clean lens)")
            status = "suboptimal"

        if not hand_detected:
            advisories.append("Move your hand into the frame")
            status = "attention_needed"
        else:
            if hand_too_small:
                advisories.append("Hand is too far — bring it closer to the camera")
                status = "suboptimal"
            elif hand_too_large:
                advisories.append("Hand is too close — move it slightly back")
                status = "suboptimal"
            elif not is_hand_centered:
                advisories.append("Center your hand inside the target box")
                status = "suboptimal"

        if len(advisories) == 0:
            advisories.append("Camera quality is good")

        # 6. Overall Quality Score [0.0, 1.0]
        # Weighted aggregate
        b_score = 1.0 - min(1.0, abs(mean_brightness - 128.0) / 128.0)
        c_score = min(1.0, contrast / 50.0)
        blur_s = min(1.0, blur_score / 200.0)
        h_score = 1.0 if (hand_detected and not hand_too_small and not hand_too_large) else (0.4 if hand_detected else 0.0)

        quality_score = round(0.20 * b_score + 0.20 * c_score + 0.20 * blur_s + 0.40 * h_score, 3)

        return {
            "status": status,
            "quality_score": quality_score,
            "metrics": {
                "mean_brightness": round(mean_brightness, 1),
                "contrast": round(contrast, 1),
                "laplacian_variance": round(blur_score, 1),
                "is_blurry": is_blurry,
                "hand_detected": hand_detected,
                "hand_area_percentage": round(hand_area_pct * 100.0, 1),
                "is_hand_centered": is_hand_centered,
            },
            "primary_advisory": advisories[0],
            "all_advisories": advisories,
        }

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "quality_score": 0.0,
            "metrics": {},
            "primary_advisory": error_msg,
            "all_advisories": [error_msg],
        }


_analyzer_instance: Optional[CameraQualityAnalyzer] = None


def get_camera_analyzer() -> CameraQualityAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = CameraQualityAnalyzer()
    return _analyzer_instance
