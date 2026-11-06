"""Thin, validated adapter between Flask and a future TensorFlow/Keras classifier."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


class ModelNotReadyError(RuntimeError):
    pass


class PredictionError(RuntimeError):
    pass


def _details(label: str) -> tuple[str, str]:
    if label.startswith("Healthy_"):
        return label.removeprefix("Healthy_"), "Healthy"
    crop = "Wheat" if label.startswith("Wheat_") else "Rice" if label in {"Rice_Blast", "Brown_Spot", "Bacterial_Leaf_Blight"} else "Tomato"
    return crop, label.replace("_", " ")


def _prepare_image(image_path: Path) -> np.ndarray:
    """Return a batch of RGB float32 pixels in the planned 224 x 224 x 3 input format."""
    with Image.open(image_path) as image:
        rgb = image.convert("RGB").resize((224, 224))
        pixels = np.asarray(rgb, dtype=np.float32) / 255.0
    return np.expand_dims(pixels, axis=0)


def predict_image(image_path: Path, config: dict) -> dict:
    labels = config["CLASS_LABELS"]
    if len(labels) != 11:
        raise PredictionError("CLASS_LABELS must contain exactly 11 labels in the model's output order.")

    batch = _prepare_image(image_path)
    if config["ENABLE_MOCK_PREDICTION"]:
        # Deliberately obvious development-only output; it is never a model result.
        label, confidence = labels[0], 0.0
    else:
        configured_path = config.get("MODEL_PATH", "")
        if not configured_path:
            raise ModelNotReadyError("Predictions are not available yet: add the trained model path to MODEL_PATH first.")
        model_path = Path(configured_path)
        if not model_path.exists():
            raise ModelNotReadyError("Predictions are not available yet: the configured model file cannot be found.")
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path)
            scores = np.asarray(model.predict(batch, verbose=0)).squeeze()
        except Exception as error:  # TensorFlow reports varied model-format errors.
            raise PredictionError("Unable to load or run the configured TensorFlow/Keras model.") from error
        if scores.ndim != 1 or scores.size != len(labels):
            raise PredictionError(f"Model output must be one vector of {len(labels)} class scores.")
        index = int(np.argmax(scores))
        label, confidence = labels[index], float(scores[index])

    crop, condition = _details(label)
    return {"label": label.replace("_", " "), "crop": crop, "condition": condition, "confidence": confidence * 100}
