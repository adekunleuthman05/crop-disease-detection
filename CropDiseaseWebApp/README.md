# Crop Disease Detection Web App

This is a standalone Flask upload-and-prediction interface. It intentionally does **not** produce real predictions until a trained TensorFlow/Keras model is configured.

## Run locally

1. Open a terminal in this folder and create/activate a virtual environment.
2. Install the interface dependencies: `pip install -r requirements.txt`.
3. Once the model is ready, install TensorFlow: `pip install tensorflow`.
4. Set `MODEL_PATH` to the model file/folder and run `python app.py`.
5. Visit `http://127.0.0.1:5000`.

PowerShell example after receiving a model at `models/crop_disease.keras`:

```powershell
$env:MODEL_PATH = "models/crop_disease.keras"
python app.py
```

To choose a non-default Flask signing key, also set `FLASK_SECRET_KEY` to a long random value. Do not use Flask's development server for public deployment.

## Required handoff from the training collaborator

Provide both of these items:

1. The complete loadable TensorFlow/Keras model: preferably a single `.keras` file, or a SavedModel directory compatible with the TensorFlow version used in deployment. Tell the web-app owner its exact path.
2. The exact zero-based output-index mapping used during training. It **must** match the order below before the app is used. If it differs, replace `CLASS_LABELS` in `config.py` to match the collaborator's `class_indices` exactly.

| Index | Class label |
|---:|---|
| 0 | Healthy_Wheat |
| 1 | Wheat_Leaf_Rust |
| 2 | Wheat_Septoria |
| 3 | Healthy_Rice |
| 4 | Rice_Blast |
| 5 | Brown_Spot |
| 6 | Bacterial_Leaf_Blight |
| 7 | Healthy_Tomato |
| 8 | Bacterial_Spot |
| 9 | Early_Blight |
| 10 | Late_Blight |

The adapter sends one RGB image resized to **224 × 224**, converted to `float32`, scaled to **0–1**, with shape **`(1, 224, 224, 3)`**. The model must return one vector of 11 scores in the mapping order above (normally softmax probabilities). If the trainer used different preprocessing—for example MobileNetV2's `preprocess_input` scaling—ask them to state that explicitly and update `_prepare_image` in `predictor.py` before deployment.

## Safe UI-only demo mode

For layout testing only, set `ENABLE_MOCK_PREDICTION=true`. It visibly returns the first label with 0.00% confidence and is disabled by default. It is not an inference result and must never be used for demonstrations of model accuracy or deployment.

## Privacy and security notes

- Only PNG, JPG/JPEG, and WEBP extensions are accepted; Pillow verifies the actual image content.
- Flask caps request size at 8 MB, uses a safe generated filename, and deletes the temporary upload after preprocessing. Images are not stored permanently by default.
- Keep the service behind HTTPS and authentication if it is exposed outside a trusted network. Do not place uploaded images or model files in version control.
- The included validation test covers the interface and file-extension rejection, not model accuracy.

## Test

Run `python -m unittest discover -s tests` from this folder.
