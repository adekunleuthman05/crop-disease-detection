# CropDiseaseDetection dataset builder

This is a reproducible, image-free build package for the agreed 11-class CropDiseaseDetection dataset. It preserves source attribution and creates a deterministic **70/15/15** train/validation/test split from original images only.

## Classes

`Healthy_Wheat`, `Wheat_Leaf_Rust`, `Wheat_Septoria`, `Healthy_Rice`, `Rice_Blast`, `Brown_Spot`, `Bacterial_Leaf_Blight`, `Healthy_Tomato`, `Early_Blight`, `Late_Blight`, and `Bacterial_Spot`.

`Wheat_Septoria` replaces the earlier proposed `Wheat_Leaf_Blight`: the wheat source labels Septoria, not leaf blight. The mapping, source URLs, DOI versions, licences, reported counts, and honest count gaps are in [dataset_manifest.csv](dataset_manifest.csv).

## What is and is not included

No images are included, generated, or silently downloaded. The Mendeley records are CC BY 4.0, but the downloader must inspect their current terms/version and save the unmodified archives. The rice record gives an exact total of 1,701 originals, but does **not** publish counts for its four selected classes; the manifest intentionally says so rather than inventing values. The script records actual discovered counts after acquisition.

## Build it

Use Python 3.11 or newer in a virtual environment:

```powershell
python -m pip install -r requirements.txt
```

Follow [metadata/SOURCE_ACQUISITION.md](metadata/SOURCE_ACQUISITION.md), extracting sources into this shape (archive nesting is allowed):

```text
raw/
  wheat_leaf_dataset/.../Healthy Wheat Leaf, Stripe Rust, Septoria Disease
  rice_bacterial_fungal/.../Healthy Rice Leaf, Leaf Blast, Brown Spot, Bacterial Leaf Blight
  plantvillage/.../Tomato___healthy, Tomato___Early_blight, Tomato___Late_blight, Tomato___Bacterial_spot
```

Then build and validate:

```powershell
python scripts/prepare_dataset.py --raw raw --output dataset
python scripts/validate_dataset.py --dataset dataset
```

If your filesystem cannot create hard links, add `--copy` to the preparation command. A non-empty output is refused; this protects against accidentally mixing runs. The optional `scripts/fetch_plantvillage.py` only clones the official repository metadata. It does not replace the licensed manual image download.

Outputs include `dataset/image_index.csv` (each selected original’s SHA-256, source and split) and `metadata/preparation_report.json` (actual counts, excluded unreadable files, source folders, and duplicate evidence). Keep them with the dataset.

## Leakage prevention and duplicates

The builder excludes directory paths containing augmentation, grayscale, or segmentation identifiers; you must still visually inspect the selected source folders. It first removes byte-identical within-class images and stops if an exact image has conflicting target labels. It then reports all perceptual-hash pairs within Hamming distance 4 and removes only same-class pairs, retaining cross-class pairs for a human label review. The split occurs **after** deduplication and **before** any augmentation. Apply random flip/rotation/zoom only in the training data pipeline at runtime; never save augmented derivatives into validation or test.

Splits are class-stratified, deterministic (`seed: 20260906`) and use largest-remainder allocation: 70% train, 15% validation, 15% test. A three-image class therefore becomes 2/1/0 under exact allocation; do not claim all splits contain a class unless the report confirms it.

## Attribution and licence

Use the exact citations in [metadata/ATTRIBUTION.md](metadata/ATTRIBUTION.md) in the thesis, repository, model card, and any redistribution. Retain licence notices, source URLs, DOI versions, and state that this package renames folders, filters classes, deduplicates and splits originals. CC BY 4.0 requires attribution, a link to the licence, and indication of these changes.

## Nigerian external evaluation

The training sources are Ethiopian (wheat), Bangladeshi (rice), and controlled PlantVillage images (tomato); they are not Nigerian field evidence. Collect a separately consented/permissioned Nigerian field test set with image ID, crop, diagnosis/diagnostician, location at a non-identifying geographic level, date/season, device, and consent/permission record. Freeze it before model selection; do not use it for tuning, augmentation, or threshold selection. Report performance both on the internal held-out test partition and this external set, including class counts and “not available” where a class lacks enough verified images.

## Integrate with the existing CropDiseaseDetection project

1. Build this package in a separate location and preserve its report.
2. Copy or link the resulting `dataset/` directory into the existing project root as `CropDiseaseDetection/dataset/`.
3. Change the old label `Wheat_Leaf_Blight` to `Wheat_Septoria` everywhere: model label list, UI text, tests, and evaluation reports. Do not remap it semantically.
4. Make the training loader use `dataset/train`, `dataset/validation`, and `dataset/test`; derive class names from `config/classes.yaml` or persist the same ordered label list with the trained model.
5. Put augmentation layers inside the training pipeline only. Run `validate_dataset.py` before every new training run and save `image_index.csv`, `preparation_report.json`, the configuration, package commit/version, and model checksum with results.
