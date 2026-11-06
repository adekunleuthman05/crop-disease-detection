"""Application configuration. Set environment variables instead of editing secrets into code."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "replace-this-before-production")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB, enforced by Flask before saving.
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
    UPLOAD_FOLDER = BASE_DIR / "instance" / "uploads"
    # Leave blank until the training collaborator supplies a TensorFlow/Keras model.
    MODEL_PATH = os.getenv("MODEL_PATH", "")
    # Demonstration mode is intentionally OFF. Set true only for UI development, never deployment.
    ENABLE_MOCK_PREDICTION = os.getenv("ENABLE_MOCK_PREDICTION", "false").lower() == "true"
    CLASS_LABELS = [
        "Healthy_Wheat", "Wheat_Leaf_Rust", "Wheat_Septoria",
        "Healthy_Rice", "Rice_Blast", "Brown_Spot", "Bacterial_Leaf_Blight",
        "Healthy_Tomato", "Bacterial_Spot", "Early_Blight", "Late_Blight",
    ]
