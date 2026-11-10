# Acquire the source archives

All three primary sources are CC BY 4.0 according to their Mendeley Data records. Download them yourself from the cited landing pages so the recorded version, licence, and any click-through terms are reviewed at the time of acquisition. This package deliberately does **not** redistribute source images.

1. Download Wheat Leaf Dataset V1 from https://data.mendeley.com/datasets/wgd66f8n6h/1 and extract it to `raw/wheat_leaf_dataset/`.
2. Download Rice Leaf Bacterial and Fungal Disease Dataset V2 from https://data.mendeley.com/datasets/hx6f852hw4/2 and extract it to `raw/rice_bacterial_fungal/`. Select only the stated original-image folders; do not use the 5,188 augmented images as observations.
3. Download PlantVillage Dataset V1 from https://data.mendeley.com/datasets/tywbtsjrjv/1 and extract the RGB/color originals to `raw/plantvillage/`. Do not mix color with grayscale or segmented variants.

The Mendeley downloads are manual by design: file URLs can change and the preparer must review the source licence/version. `prepare_dataset.py` discovers folders recursively, so archive nesting is acceptable. It refuses ambiguous matching folders and writes its evidence to the report.
