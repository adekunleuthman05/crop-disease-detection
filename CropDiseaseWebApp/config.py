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
    # This project ships with the verified training model. Override only when deploying another model.
    MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "final_model.keras"))
    # Demonstration mode is intentionally OFF. Set true only for UI development, never deployment.
    ENABLE_MOCK_PREDICTION = os.getenv("ENABLE_MOCK_PREDICTION", "false").lower() == "true"
    # Exact zero-based output order from final_model.keras and its training notebook.
    CLASS_LABELS = [
        "Wheat_Rust", "Wheat_Leaf_Blight", "Wheat_Healthy",
        "Rice_Blast", "Rice_Brown_Spot", "Rice_Healthy",
        "Tomato_Early_Blight", "Tomato_Late_Blight", "Tomato_Bacterial_Spot", "Tomato_Healthy",
    ]
