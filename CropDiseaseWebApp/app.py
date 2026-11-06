"""Flask entry point for crop disease image predictions."""
from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from config import Config
from predictor import ModelNotReadyError, PredictionError, predict_image


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    upload_dir = Path(app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    @app.errorhandler(413)
    def file_too_large(_error):
        flash(f"That file is too large. The maximum upload size is {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)} MB.", "error")
        return redirect(url_for("index"))

    @app.get("/")
    def index():
        return render_template("index.html", max_size_mb=app.config["MAX_CONTENT_LENGTH"] // (1024 * 1024))

    @app.post("/predict")
    def predict():
        upload = request.files.get("image")
        if upload is None or not upload.filename:
            flash("Please choose an image file before submitting.", "error")
            return redirect(url_for("index"))
        if not allowed_file(upload.filename):
            flash("Use a PNG, JPG, JPEG, or WEBP image.", "error")
            return redirect(url_for("index"))

        # Never trust the supplied filename; keep only a safe suffix and remove the file after use.
        safe_name = secure_filename(upload.filename)
        suffix = Path(safe_name).suffix.lower()
        temporary_path = upload_dir / f"{uuid4().hex}{suffix}"
        try:
            upload.save(temporary_path)
            with Image.open(temporary_path) as image:
                image.verify()  # Reject files that only pretend to be images.
            with Image.open(temporary_path) as image:
                preview = image.convert("RGB")
                preview.thumbnail((500, 500))
                preview_bytes = io.BytesIO()
                preview.save(preview_bytes, format="JPEG", quality=88)
            preview_data = base64.b64encode(preview_bytes.getvalue()).decode("ascii")

            result = predict_image(temporary_path, app.config)
        except (UnidentifiedImageError, OSError):
            flash("We could not read that file as a valid image.", "error")
            return redirect(url_for("index"))
        except ModelNotReadyError as error:
            flash(str(error), "error")
            return redirect(url_for("index"))
        except PredictionError as error:
            app.logger.warning("Prediction failed: %s", error)
            flash("The image was accepted, but prediction could not be completed. Please check the model integration settings.", "error")
            return redirect(url_for("index"))
        finally:
            temporary_path.unlink(missing_ok=True)

        return render_template("result.html", result=result, preview_data=preview_data)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
