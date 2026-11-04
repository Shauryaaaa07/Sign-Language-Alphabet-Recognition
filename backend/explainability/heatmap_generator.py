"""
Heatmap Overlay and Visualization Generator
============================================

Transforms 2D Grad-CAM activation heatmaps into visual overlays using OpenCV
colormaps, alpha blending, and base64 image encoding.
"""

import base64
import io
from typing import Tuple, Union

import cv2
import numpy as np
from PIL import Image


def overlay_heatmap_on_image(
    heatmap: np.ndarray,
    original_image: Union[np.ndarray, Image.Image, bytes],
    alpha: float = 0.45,
    colormap: int = cv2.COLORMAP_JET,
) -> Tuple[np.ndarray, np.ndarray, str, str]:
    """
    Overlays a 2D float32 heatmap [0, 1] onto an RGB image.

    Returns:
        Tuple:
        - colored_heatmap_rgb: uint8 RGB colormapped heatmap
        - blended_overlay_rgb: uint8 RGB blended visualization
        - heatmap_base64: Data URI for colored heatmap
        - overlay_base64: Data URI for blended overlay
    """
    # 1. Parse original image to uint8 RGB
    if isinstance(original_image, bytes):
        pil_img = Image.open(io.BytesIO(original_image)).convert("RGB")
        img_rgb = np.array(pil_img, dtype=np.uint8)
    elif isinstance(original_image, Image.Image):
        img_rgb = np.array(original_image.convert("RGB"), dtype=np.uint8)
    elif isinstance(original_image, np.ndarray):
        if original_image.dtype != np.uint8:
            img_rgb = (original_image * 255.0).clip(0, 255).astype(np.uint8)
        else:
            img_rgb = original_image
        if len(img_rgb.shape) == 4:
            img_rgb = img_rgb[0]
    else:
        raise ValueError("Unsupported original image format for heatmap overlay.")

    height, width = img_rgb.shape[:2]

    # 2. Resize heatmap to match image dimensions
    heatmap_resized = cv2.resize(heatmap, (width, height), interpolation=cv2.INTER_CUBIC)
    heatmap_uint8 = np.uint8(255 * np.clip(heatmap_resized, 0.0, 1.0))

    # 3. Apply Colormap (BGR output from OpenCV)
    heatmap_colored_bgr = cv2.applyColorMap(heatmap_uint8, colormap)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored_bgr, cv2.COLOR_BGR2RGB)

    # 4. Alpha Blending
    # Blended = alpha * heatmap + (1 - alpha) * original
    blended_rgb = cv2.addWeighted(
        heatmap_colored_rgb, alpha, img_rgb, 1.0 - alpha, 0
    )

    # 5. Encode to Base64 PNGs
    def to_base64(arr_rgb: np.ndarray) -> str:
        pil = Image.fromarray(arr_rgb)
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    heatmap_b64 = to_base64(heatmap_colored_rgb)
    overlay_b64 = to_base64(blended_rgb)

    return heatmap_colored_rgb, blended_rgb, heatmap_b64, overlay_b64
