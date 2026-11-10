"""Thin, validated adapter between Flask and a future TensorFlow/Keras classifier."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

MODEL_CACHE: dict[str, object] = {}


class ModelNotReadyError(RuntimeError):
    pass


class PredictionError(RuntimeError):
    pass


def _details(label: str) -> tuple[str, str]:
    crop, category = label.split("_", 1)
    return crop, "Healthy" if category == "Healthy" else category.replace("_", " ")


def _prepare_image(image_path: Path) -> np.ndarray:
    """Match the model notebook: RGB, aspect-preserving thumbnail, black padding, 0–1 floats."""
    with Image.open(image_path) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail((224, 224), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (224, 224), (0, 0, 0))
        canvas.paste(rgb, ((224 - rgb.width) // 2, (224 - rgb.height) // 2))
        pixels = np.asarray(canvas, dtype=np.float32) / 255.0
    return np.expand_dims(pixels, axis=0)


def predict_image(image_path: Path, config: dict) -> dict:
    labels = config["CLASS_LABELS"]
    if len(labels) != 10:
        raise PredictionError("CLASS_LABELS must contain the model's 10 labels in exact output order.")

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
            cache_key = str(model_path.resolve())
            model = MODEL_CACHE.get(cache_key)
            if model is None:
                model = tf.keras.models.load_model(model_path, compile=False)
                MODEL_CACHE[cache_key] = model
            scores = np.asarray(model.predict(batch, verbose=0)).squeeze()
        except Exception as error:  # TensorFlow reports varied model-format errors.
            raise PredictionError("Unable to load or run the configured TensorFlow/Keras model.") from error
        if scores.ndim != 1 or scores.size != len(labels):
            raise PredictionError(f"Model output must be one vector of {len(labels)} class scores.")
        index = int(np.argmax(scores))
        label, confidence = labels[index], float(scores[index])

    crop, condition = _details(label)
    return {"label": label.replace("_", " "), "crop": crop, "condition": condition, "confidence": confidence * 100}
