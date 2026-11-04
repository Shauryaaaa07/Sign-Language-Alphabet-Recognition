"""
FastAPI Backend Configuration
=============================

Configuration settings and paths for the ISL Alphabet Recognition backend service.
"""

import os
from pathlib import Path
from typing import List

# Base repository root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Path configurations
# Milestone 7.1: Selected production model candidate is CNN V4
# (Double-Conv + BatchNorm + Photometric Augmentation + L2 Kernel Regularization)
# Evaluated on independent test set: 86.34% accuracy, 83.96% macro F1.
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(BASE_DIR / "saved_models" / "experiments" / "isl_alphabet_cnn_v4_best.keras"),
)

LABEL_CLASSES_PATH = os.getenv(
    "LABEL_CLASSES_PATH",
    str(BASE_DIR / "training" / "label_classes.json"),
)

# Image preprocessing specifications (must align strictly with training pipeline)
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
IMAGE_CHANNELS = 3
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
NUM_CLASSES = 26

# Allowed CORS origins (Vite React frontend dev server)
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

# API Metadata
API_TITLE = "Indian Sign Language (ISL) Alphabet Recognition API"
API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "Production-grade FastAPI inference backend for 26-class ISL fingerspelling recognition "
    "powered by a trained 2D Convolutional Neural Network."
)

# Maximum file upload size in bytes (10 MB limit)
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
