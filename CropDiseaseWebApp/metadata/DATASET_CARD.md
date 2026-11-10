# Dataset card (to complete after preparation)

**Name:** CropDiseaseDetection 11-class derivative dataset.

**Task:** single-label crop-leaf disease/health classification. **Unit:** one original source image. **Not a diagnostic device:** predictions require agronomist/pathologist confirmation before treatment decisions.

**Composition:** source-level composition is documented in `dataset_manifest.csv`. Do not publish a final total until `metadata/preparation_report.json` is generated. The four selected PlantVillage tomato classes are reported as 6,627 images (1,591 healthy; 1,000 early blight; 1,909 late blight; 2,127 bacterial spot); the wheat subset is 407 images (102/208/97); selected rice class totals must be measured after source acquisition from the stated 1,701-original collection.

**Collection context and limitations:** wheat was collected at Holeta farm, Ethiopia; rice at locations in Sirajganj and Pabna, Bangladesh; PlantVillage images are predominantly controlled-background. These distributions are not representative of Nigerian farms, cultivars, devices, seasons, or disease severity. Labels originate with source providers; the derivative mapping does not independently diagnose images.

**Recommended use:** development and research benchmarking with the stated split. **Out-of-scope:** clinical/agronomic diagnosis, unqualified pesticide advice, or claims of Nigerian generalization without independent local evaluation.

**Versioning:** record source archive checksums, this package version/commit, `classes.yaml`, `image_index.csv`, report, model checksum, and training environment for every experiment.
